"""Integration regression for the world disaster -> territory signal path.

These tests execute the real consumer pipeline against PostgreSQL and guard
against the two runtime defects found during deployment that aborted the whole
world tick transaction on the first max-severity disaster:

1. ``territory_modifiers`` was keyed off ``world_region_bindings.gameplay_region_id``
   (a gameplay UUID) while the column references ``world_regions(id)`` (the
   world-region text id) -> foreign-key violation.
2. ``travel_risk`` for a severity-5 disaster was 6000 bps while the schema CHECK
   bounds the modifier columns to [-5000, 5000] -> check violation.

The tests skip automatically when ``MADWORLD_DATABASE_URL`` is not configured,
matching the rest of the integration suite.
"""
from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import text

from app.application.master_b1_b2 import TERRITORY_CONSUMER, apply_territory_signal
from app.infrastructure.db import create_engine_from_env

pytestmark = pytest.mark.integration

# dust_basin is the world region that has a world_region_bindings row seeded by
# migration 025 (world -> gameplay region). It is the bound region in every
# freshly migrated database.
BOUND_WORLD_REGION = "dust_basin"
UNBOUND_WORLD_REGION = "iron_ruins"


@pytest.fixture(scope="module")
def engine():
    if not os.getenv("MADWORLD_DATABASE_URL"):
        pytest.skip("MADWORLD_DATABASE_URL is not configured")
    eng = create_engine_from_env()
    yield eng
    eng.dispose()


def _max_tick(conn) -> int:
    return int(conn.execute(text("SELECT COALESCE(MAX(tick), 0) FROM world_events")).scalar())


def _insert_disaster(conn, *, region_id: str, tick: int, severity: int = 5):
    event_id = uuid.uuid4()
    conn.execute(
        text(
            """
            INSERT INTO world_events (id, tick, region_id, event_type, severity, state, payload)
            VALUES (:id, :tick, :region, 'DISASTER', :severity, 'ACTIVE',
                    CAST(:payload AS JSONB))
            """
        ),
        {
            "id": event_id,
            "tick": tick,
            "region": region_id,
            "severity": severity,
            "payload": f'{{"severity": {severity}}}',
        },
    )
    return event_id


def test_max_severity_disaster_is_bounded_and_keyed_to_world_region(engine):
    """A severity-5 disaster must persist a territory modifier without raising.

    Covers both regressions: the modifier row must reference the world-region id
    (FK to world_regions), and every stored bps value must be within the
    [-5000, 5000] CHECK bounds (raw risk would be 6000).
    """
    with engine.begin() as conn:
        tick = _max_tick(conn) + 1
        event_id = _insert_disaster(conn, region_id=BOUND_WORLD_REGION, tick=tick, severity=5)
        payload = {"severity": 5}

        # Must not raise (FK or CHECK violation) -- this is exactly what used to
        # abort the whole world tick transaction.
        applied = apply_territory_signal(
            conn, event_id, BOUND_WORLD_REGION, "disaster", payload
        )
        assert applied is True

        row = conn.execute(
            text(
                """
                SELECT region_id, travel_time_bps, travel_risk_bps, extraction_bps
                FROM territory_modifiers
                WHERE source_type = 'world_event' AND source_id = CAST(:eid AS TEXT)
                """
            ),
            {"eid": str(event_id)},
        ).mappings().first()

        assert row is not None, "territory modifier was not persisted"
        # region_id must be the world-region id (FK to world_regions), never a
        # gameplay UUID.
        assert row["region_id"] == BOUND_WORLD_REGION
        assert row["region_id"] in {
            r[0] for r in conn.execute(text("SELECT id FROM world_regions")).all()
        }
        # All modifier columns must satisfy the schema CHECK bounds [-5000, 5000].
        for col in ("travel_time_bps", "travel_risk_bps", "extraction_bps"):
            v = int(row[col])
            assert -5000 <= v <= 5000, f"{col}={v} out of bounds"
        # A severity-5 disaster is a hazard: risk and travel time are positive,
        # extraction is negative, and the clamp caps risk at the 5000 ceiling
        # rather than the raw 6000.
        assert row["travel_risk_bps"] == 5000
        assert row["travel_time_bps"] == 4000      # 5*800 = 4000 (within bounds)
        assert row["extraction_bps"] == -5000      # 5*1000 = 5000, negated -> -5000


def test_territory_signal_is_consumed_at_most_once(engine):
    """Re-applying the same event is idempotent (consumer fence)."""
    with engine.begin() as conn:
        tick = _max_tick(conn) + 1
        event_id = _insert_disaster(conn, region_id=BOUND_WORLD_REGION, tick=tick, severity=3)
        payload = {"severity": 3}
        first = apply_territory_signal(conn, event_id, BOUND_WORLD_REGION, "disaster", payload)
        second = apply_territory_signal(conn, event_id, BOUND_WORLD_REGION, "disaster", payload)
        assert first is True
        assert second is False
        count = conn.execute(
            text(
                "SELECT COUNT(*) FROM territory_modifiers WHERE source_id = CAST(:eid AS TEXT)"
            ),
            {"eid": str(event_id)},
        ).scalar()
        assert count == 1


def test_unbound_region_disaster_does_not_corrupt_modifiers(engine):
    """A region without a world<->gameplay binding must not insert a modifier.

    The guarded insert only fires for a bound world region, so an unbound region
    (e.g. iron_ruins in a fresh database) must produce no territory_modifiers row
    and must not raise.
    """
    with engine.begin() as conn:
        bindings = conn.execute(
            text("SELECT COUNT(*) FROM world_region_bindings WHERE world_region_id = :r"),
            {"r": UNBOUND_WORLD_REGION},
        ).scalar()
        if bindings:
            pytest.skip("iron_ruins is bound in this database; unbound-path not applicable")
        tick = _max_tick(conn) + 1
        event_id = _insert_disaster(conn, region_id=UNBOUND_WORLD_REGION, tick=tick, severity=5)
        applied = apply_territory_signal(
            conn, event_id, UNBOUND_WORLD_REGION, "disaster", {"severity": 5}
        )
        # The effects row is still recorded (world_region_effects is keyed by the
        # world region directly) but no territory_modifiers row can exist without
        # a binding.
        count = conn.execute(
            text(
                "SELECT COUNT(*) FROM territory_modifiers WHERE source_id = CAST(:eid AS TEXT)"
            ),
            {"eid": str(event_id)},
        ).scalar()
        assert count == 0
        assert applied is True
        # consumption fence marker exists
        fence = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM world_event_consumptions
                WHERE consumer_name = :c AND world_event_id = :eid
                """
            ),
            {"c": TERRITORY_CONSUMER, "eid": event_id},
        ).scalar()
        assert fence == 1

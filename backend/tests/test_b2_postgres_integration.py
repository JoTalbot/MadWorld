import os
from uuid import uuid4

import pytest
from sqlalchemy import text

from app.application.travel_service import claim_recovery, depart_travel, plan_travel, resolve_encounter
from app.infrastructure.db import create_engine_from_env

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def engine():
    if not os.getenv("MADWORLD_DATABASE_URL"):
        pytest.skip("MADWORLD_DATABASE_URL is not configured")
    engine = create_engine_from_env()
    yield engine
    engine.dispose()


def seed_travel_fixture(engine, *, cargo_capacity: int = 1000) -> dict:
    player_id, wallet_id, vehicle_id = uuid4(), uuid4(), uuid4()
    handle = f"b2-{player_id.hex[:12]}"
    with engine.begin() as conn:
        region = conn.execute(text("SELECT id FROM regions ORDER BY id LIMIT 1")).scalar_one()
        conn.execute(
            text("INSERT INTO players (id, handle) VALUES (:id, :handle)"),
            {"id": player_id, "handle": handle},
        )
        conn.execute(
            text("INSERT INTO wallets (id, owner_id) VALUES (:id, :owner_id)"),
            {"id": wallet_id, "owner_id": player_id},
        )
        conn.execute(
            text("""
                INSERT INTO vehicles
                  (id, owner_id, code, chassis_code, durability, fuel, state, cargo_capacity)
                VALUES (:id, :owner, :code, 'b2-test', 100, 100, 'stored', :capacity)
            """),
            {"id": vehicle_id, "owner": player_id, "code": f"b2-{vehicle_id.hex}", "capacity": cargo_capacity},
        )
        for component in ("engine", "hull", "wheels", "fuel_system"):
            conn.execute(
                text("""
                    INSERT INTO vehicle_components(vehicle_id, component_code, condition, max_condition, armor)
                    VALUES (:vehicle, :component, 100, 100, 0)
                """),
                {"vehicle": vehicle_id, "component": component},
            )
        conn.execute(
            text("""
                INSERT INTO ledger_entries(idempotency_key, wallet_id, amount, reason, actor_id)
                VALUES (:key, :wallet, 100, 'b2-test-funds', :player)
            """),
            {"key": f"b2-funds:{player_id}", "wallet": wallet_id, "player": player_id},
        )
    return {
        "player_id": player_id,
        "wallet_id": wallet_id,
        "vehicle_id": vehicle_id,
        "region_id": region,
    }


def create_travelling_session(conn, fixture: dict, *, cargo_weight: int = 10) -> dict:
    session = plan_travel(
        conn,
        player_id=fixture["player_id"],
        vehicle_id=fixture["vehicle_id"],
        origin_region_id=fixture["region_id"],
        destination_region_id=fixture["region_id"],
        world_region_id="dust_basin",
        duration_seconds=60,
        fuel_reserved=10,
        cargo_weight=cargo_weight,
        base_risk_bps=100,
        idempotency_key=f"b2-plan:{uuid4()}",
    )
    departed = depart_travel(conn, session_id=session["id"])
    assert departed["state"] == "TRAVELLING"
    return session


def test_postgres_encounter_loss_persists_destruction_recovery_and_retry_idempotency(engine):
    fixture = seed_travel_fixture(engine)
    with engine.begin() as conn:
        session = create_travelling_session(conn, fixture)
        encounter_id = uuid4()
        conn.execute(
            text("""
                INSERT INTO travel_encounters(id, travel_session_id, encounter_type, severity)
                VALUES (:id, :session, 'AMBUSH', 5)
            """),
            {"id": encounter_id, "session": session["id"]},
        )

        resolved = resolve_encounter(conn, encounter_id=encounter_id, outcome="LOST")
        retry = resolve_encounter(conn, encounter_id=encounter_id, outcome="LOST")

        assert resolved["state"] == "LOST"
        assert retry["state"] == "LOST"

        travel = conn.execute(
            text("SELECT state FROM player_travel_sessions WHERE id=:id"), {"id": session["id"]}
        ).scalar_one()
        vehicle = conn.execute(
            text("SELECT state, durability FROM vehicles WHERE id=:id"), {"id": fixture["vehicle_id"]}
        ).mappings().one()
        components = conn.execute(
            text("SELECT count(*) AS count, min(condition) AS min_condition FROM vehicle_components WHERE vehicle_id=:id"),
            {"id": fixture["vehicle_id"]},
        ).mappings().one()
        cases = conn.execute(
            text("SELECT count(*) AS count FROM salvage_recovery_cases WHERE travel_session_id=:id"),
            {"id": session["id"]},
        ).scalar_one()

    assert travel == "LOST"
    assert vehicle["state"] == "destroyed"
    assert vehicle["durability"] == 0
    assert components["count"] == 4
    assert components["min_condition"] == 0
    assert cases == 1


def test_postgres_recovery_claim_debits_once_and_retry_is_idempotent(engine):
    fixture = seed_travel_fixture(engine)
    with engine.begin() as conn:
        session = create_travelling_session(conn, fixture)
        encounter_id = uuid4()
        conn.execute(
            text("""
                INSERT INTO travel_encounters(id, travel_session_id, encounter_type, severity)
                VALUES (:id, :session, 'AMBUSH', 5)
            """),
            {"id": encounter_id, "session": session["id"]},
        )
        resolve_encounter(conn, encounter_id=encounter_id, outcome="LOST")
        case = conn.execute(
            text("SELECT id FROM salvage_recovery_cases WHERE travel_session_id=:session"),
            {"session": session["id"]},
        ).scalar_one()

        recovered = claim_recovery(conn, player_id=fixture["player_id"], case_id=case)
        retry = claim_recovery(conn, player_id=fixture["player_id"], case_id=case)

        assert recovered["state"] == "RECOVERED"
        assert retry["state"] == "RECOVERED"

        debit_count = conn.execute(
            text("""
                SELECT count(*)
                FROM ledger_entries
                WHERE wallet_id=:wallet AND idempotency_key=:key
            """),
            {"wallet": fixture["wallet_id"], "key": f"recovery:{case}"},
        ).scalar_one()
        balance = conn.execute(
            text("SELECT COALESCE(SUM(amount), 0) FROM ledger_entries WHERE wallet_id=:wallet"),
            {"wallet": fixture["wallet_id"]},
        ).scalar_one()
        vehicle = conn.execute(
            text("SELECT state, durability FROM vehicles WHERE id=:id"), {"id": fixture["vehicle_id"]}
        ).mappings().one()
        component_min = conn.execute(
            text("SELECT min(condition) FROM vehicle_components WHERE vehicle_id=:id"),
            {"id": fixture["vehicle_id"]},
        ).scalar_one()

    assert debit_count == 1
    assert balance == 0
    assert vehicle["state"] == "stored"
    assert vehicle["durability"] >= 1
    assert component_min >= 1


def test_postgres_cargo_capacity_rejects_overload_and_accepts_boundary(engine):
    fixture = seed_travel_fixture(engine, cargo_capacity=50)
    with engine.begin() as conn:
        with pytest.raises(ValueError, match="cargo weight exceeds vehicle capacity"):
            plan_travel(
                conn,
                player_id=fixture["player_id"],
                vehicle_id=fixture["vehicle_id"],
                origin_region_id=fixture["region_id"],
                destination_region_id=fixture["region_id"],
                world_region_id="dust_basin",
                duration_seconds=60,
                fuel_reserved=10,
                cargo_weight=51,
                base_risk_bps=100,
                idempotency_key=f"b2-over:{uuid4()}",
            )

        accepted = plan_travel(
            conn,
            player_id=fixture["player_id"],
            vehicle_id=fixture["vehicle_id"],
            origin_region_id=fixture["region_id"],
            destination_region_id=fixture["region_id"],
            world_region_id="dust_basin",
            duration_seconds=60,
            fuel_reserved=10,
            cargo_weight=50,
            base_risk_bps=100,
            idempotency_key=f"b2-boundary:{uuid4()}",
        )

    assert accepted["state"] == "PLANNED"

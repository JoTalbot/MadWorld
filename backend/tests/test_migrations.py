from pathlib import Path

import pytest

from app.infrastructure.migrations import apply_migrations, discover_migrations


def test_migrations_are_deterministic_and_unique() -> None:
    migrations = discover_migrations(Path(__file__).parents[1] / "migrations")
    assert [m.name for m in migrations] == sorted(m.name for m in migrations)
    assert len({m.name for m in migrations}) == len(migrations)
    assert all(len(m.checksum) == 64 for m in migrations)


def test_migration_checksum_mismatch_is_rejected() -> None:
    pytest.importorskip("sqlalchemy")
    from sqlalchemy import create_engine, text

    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, checksum TEXT NOT NULL, applied_at TEXT NOT NULL)"))
        conn.execute(text("INSERT INTO schema_migrations (version, name, checksum, applied_at) VALUES (1, '001_foundation.sql', 'bad', 'now')"))
        with pytest.raises(RuntimeError, match="checksum mismatch"):
            apply_migrations(conn, Path(__file__).parents[1] / "migrations")


def test_phase6_world_outbox_bridge_is_transactional_and_idempotent() -> None:
    migration = (Path(__file__).parents[1] / "migrations" / "023_phase6_world_outbox_bridge.sql").read_text()
    assert "CREATE OR REPLACE FUNCTION bridge_world_event_to_outbox()" in migration
    assert "AFTER INSERT ON world_events" in migration
    assert "'world.' || NEW.event_type" in migration
    assert "world_event_id" in migration
    assert "CREATE TABLE IF NOT EXISTS world_event_consumptions" in migration
    assert "PRIMARY KEY (consumer_name, world_event_id)" in migration


def test_phase6_resource_seed_covers_all_supported_resources() -> None:
    migration = (Path(__file__).parents[1] / "migrations" / "024_phase6_resource_seed.sql").read_text()
    assert "('scrap'), ('fuel'), ('water')" in migration
    assert "CROSS JOIN" in migration
    assert "ON CONFLICT (region_id, resource_type) DO NOTHING" in migration


def test_master_b1_b2_migration_has_replay_travel_and_recovery_invariants() -> None:
    migration = (Path(__file__).parents[1] / "migrations" / "025_master_b1_b2_integration.sql").read_text()
    assert "world_region_bindings" in migration
    assert "world_region_effects" in migration
    assert "world_replay_checkpoints" in migration
    assert "player_travel_sessions" in migration
    assert "travel_encounters" in migration
    assert "salvage_recovery_cases" in migration
    assert "idempotency_key TEXT NOT NULL UNIQUE" in migration


def test_master_b1_b2_economy_signal_is_idempotent() -> None:
    migration = (Path(__file__).parents[1] / "migrations" / "026_master_b1_b2_economy_signals.sql").read_text()
    assert "world_economy_signals" in migration
    assert "world_event_id UUID PRIMARY KEY" in migration
    assert "CREATE UNIQUE INDEX IF NOT EXISTS idx_dynamic_missions_source_unique" in migration

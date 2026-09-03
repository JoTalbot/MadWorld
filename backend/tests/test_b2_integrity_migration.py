from pathlib import Path

MIGRATION = Path(__file__).parents[1] / "migrations" / "027_b2_travel_integrity.sql"
CARGO_MIGRATION = Path(__file__).parents[1] / "migrations" / "028_b2_cargo_capacity.sql"


def test_b2_travel_integrity_requires_active_travel():
    sql = MIGRATION.read_text()
    assert "OLD.state NOT IN ('TRAVELLING')" in sql
    assert "trg_validate_travel_session_outcome" in sql


def test_b2_encounters_require_active_travel():
    sql = MIGRATION.read_text()
    assert "session_state IS DISTINCT FROM 'TRAVELLING'" in sql
    assert "trg_validate_travel_encounter_session" in sql


def test_b2_cargo_capacity_is_authoritative_and_non_negative():
    sql = CARGO_MIGRATION.read_text()
    assert "ADD COLUMN IF NOT EXISTS cargo_capacity INTEGER NOT NULL DEFAULT 1000" in sql
    assert "CHECK (cargo_capacity >= 0)" in sql

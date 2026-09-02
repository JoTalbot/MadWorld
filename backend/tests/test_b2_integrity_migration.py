from pathlib import Path

MIGRATION = Path(__file__).parents[1] / "migrations" / "027_b2_travel_integrity.sql"


def test_b2_travel_integrity_requires_active_travel():
    sql = MIGRATION.read_text()
    assert "OLD.state NOT IN ('TRAVELLING')" in sql
    assert "trg_validate_travel_session_outcome" in sql


def test_b2_encounters_require_active_travel():
    sql = MIGRATION.read_text()
    assert "session_state IS DISTINCT FROM 'TRAVELLING'" in sql
    assert "trg_validate_travel_encounter_session" in sql

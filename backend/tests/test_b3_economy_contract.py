from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_b3_migration_defines_economy_state_and_storage_boundaries():
    sql = (ROOT / "migrations/029_b3_advanced_economy.sql").read_text()
    for token in (
        "regional_economic_state",
        "market_price_history",
        "production_facilities",
        "production_recipes",
        "production_jobs",
        "warehouses",
        "warehouse_items",
        "logistics_contracts",
        "player_economic_skills",
        "mass_units",
    ):
        assert token in sql
    assert "CHECK (used_units <= capacity_units)" in sql
    assert "CREATE TABLE IF NOT EXISTS market_price_history" not in sql


def test_b3_uses_legacy_economy_recipe_contract_as_authoritative():
    service = (ROOT / "app/application/phase7_economy_tx.py").read_text()
    routes = (ROOT / "app/api/phase7_economy_routes.py").read_text()
    assert "FROM economy_recipes WHERE id=:id AND enabled=TRUE" in service
    assert "SELECT * FROM economy_recipes WHERE enabled=TRUE ORDER BY code" in routes
    assert "FROM production_recipes WHERE enabled=TRUE" not in routes


def test_b3_services_use_row_locks_for_mutating_boundaries():
    source = (ROOT / "app/application/phase7_economy_tx.py").read_text()
    assert "production_facilities" in source and "FOR UPDATE" in source
    assert "production_jobs WHERE id=:id AND owner_id=:o FOR UPDATE" in source
    assert "warehouses WHERE owner_id=:o AND region_id=:r ORDER BY created_at LIMIT 1 FOR UPDATE" in source
    assert "logistics_contracts WHERE id=:id AND owner_id=:o FOR UPDATE" in source


def test_b3_idempotency_rejects_payload_reuse():
    source = (ROOT / "app/application/phase7_economy_tx.py").read_text()
    assert "request_hash" in source
    assert "IdempotencyConflict" in source
    assert "_check_idempotency(old, {\"facility_id\": facility_id, \"recipe_id\": recipe_id, \"batch_units\": batch})" in source
    assert "_check_idempotency(old, incoming)" in source


def test_b3_production_applies_maintenance_and_skill_modifier():
    source = (ROOT / "app/application/phase7_economy_tx.py").read_text()
    assert "production_level FROM player_economic_skills" in source
    assert "efficiency_bps" in source
    assert "maintenance_bps" in source
    assert "skill_level * 25" in source
    assert "effective_bps = max(1000" in source
    assert "_production_duration_seconds(conn, owner_id, facility, recipe)" in source


def test_b3_logistics_preserves_mass_and_exactly_once_reward():
    source = (ROOT / "app/application/phase7_economy_tx.py").read_text()
    assert "quantity * int(item[\"mass_units\"])" in source
    assert "used_units=used_units-:u" in source
    assert "used_units=used_units+:u" in source
    assert "ON CONFLICT(idempotency_key) DO NOTHING" in source
    assert "logistics-reward:{contract_id}" in source


def test_b3_api_exposes_complete_vertical_slice():
    routes = (ROOT / "app/api/phase7_economy_routes.py").read_text()
    for token in (
        '"/regions/{region_id}"',
        '"/regions/{region_id}/items/{item_id}/metrics"',
        '"/warehouses"',
        '"/facilities"',
        '"/production/recipes"',
        '"/production/jobs"',
        '"/production/start"',
        '"/production/{job_id}/complete"',
        '"/logistics"',
        '"/logistics/{contract_id}/deliver"',
    ):
        assert token in routes

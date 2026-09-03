from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def test_b3_migration_defines_authoritative_economy_state():
    sql=(ROOT/"migrations/029_b3_advanced_economy.sql").read_text()
    for token in ("regional_economic_state","market_price_history","production_facilities","production_recipes","production_jobs","warehouses","warehouse_items","logistics_contracts","player_economic_skills","mass_units"):
        assert token in sql
    assert "CHECK (used_units <= capacity_units)" in sql


def test_b3_services_are_transaction_boundary_agnostic():
    source=(ROOT/"app/application/phase7_economy.py").read_text()
    assert "FOR UPDATE" not in source or "market_metrics" in source
    assert "regional_state" in source
    assert "market_metrics" in source

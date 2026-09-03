from pathlib import Path


TRAVEL_SERVICE = Path(__file__).parents[1] / "app" / "application" / "travel_service.py"
MASTER_SERVICE = Path(__file__).parents[1] / "app" / "application" / "master_b1_b2.py"


def test_b2_travel_service_has_authoritative_transition_boundaries():
    sql = TRAVEL_SERVICE.read_text()
    assert "UPDATE vehicles v" in sql
    assert "v.fuel >= s.fuel_reserved" in sql
    assert "state='TRAVELLING'" in sql
    assert "state IN ('TRAVELLING','PLANNED')" in sql


def test_b2_recovery_is_explicitly_idempotent():
    sql = TRAVEL_SERVICE.read_text()
    assert "loss:{row['id']}" in sql
    assert "recovery:{case_id}" in sql
    assert "ON CONFLICT (idempotency_key) DO NOTHING" in sql
    assert "FOR UPDATE" in sql
    assert "state='destroyed'" in sql
    assert "state='stored'" in sql
    assert "state='RECOVERED'" in sql
    assert '"amount": -cost' in sql


def test_b2_region_bridge_is_used_for_territory_risk():
    sql = MASTER_SERVICE.read_text()
    assert "world_region_bindings" in sql
    assert "b.gameplay_region_id" in sql
    assert "region_id=b.gameplay_region_id" in sql

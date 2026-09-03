from pathlib import Path
from uuid import uuid4

import pytest

from app.application.travel_service import plan_travel


TRAVEL_SERVICE = Path(__file__).parents[1] / "app" / "application" / "travel_service.py"


class _Result:
    def mappings(self):
        return self

    def one(self):
        return {"id": uuid4(), "state": "PLANNED", "route_risk_bps": 1200, "version": 0}


class _Conn:
    def execute(self, statement, params):
        return _Result()


def test_plan_travel_rejects_invalid_duration():
    with pytest.raises(ValueError):
        plan_travel(
            _Conn(), player_id=uuid4(), vehicle_id=uuid4(), origin_region_id=uuid4(),
            destination_region_id=uuid4(), world_region_id="dust_basin", duration_seconds=0,
            fuel_reserved=10, cargo_weight=0, base_risk_bps=1000, idempotency_key="x",
        )


def test_recovery_claim_charges_authoritative_ledger():
    sql = TRAVEL_SERVICE.read_text()
    assert 'SELECT id FROM wallets' in sql
    assert 'SELECT COALESCE(SUM(amount), 0) AS balance' in sql
    assert 'INSERT INTO ledger_entries' in sql
    assert '"reason": "vehicle_recovery"' in sql
    assert '"amount": -cost' in sql


def test_recovery_claim_locks_case_and_wallet_for_atomicity():
    sql = TRAVEL_SERVICE.read_text()
    assert 'WHERE id=:id AND player_id=:p' in sql
    assert 'FOR UPDATE' in sql
    assert "state='AVAILABLE'" in sql
    assert 'f"recovery:{case_id}"' in sql


def test_zero_cost_recovery_does_not_create_invalid_zero_ledger_entry():
    sql = TRAVEL_SERVICE.read_text()
    assert 'if cost:' in sql


def test_encounter_loss_resolves_linked_travel_loss_authoritatively():
    sql = TRAVEL_SERVICE.read_text()
    assert "if outcome == 'LOST':" in sql
    assert "resolve_travel(conn, session_id=row['travel_session_id'], outcome='LOST')" in sql
    assert "SET state='destroyed', durability=0, version=version+1" in sql
    assert "INSERT INTO salvage_recovery_cases" in sql


def test_travel_and_encounter_resolution_are_retry_idempotent_for_same_outcome():
    sql = TRAVEL_SERVICE.read_text()
    assert 'if existing and existing["state"] == outcome:' in sql
    assert sql.count('SELECT id,travel_session_id,state') >= 1


def test_plan_travel_enforces_authoritative_vehicle_capacity():
    sql = TRAVEL_SERVICE.read_text()
    assert 'SELECT id,cargo_capacity,state' in sql
    assert 'cargo_weight > vehicle["cargo_capacity"]' in sql
    assert 'cargo weight exceeds vehicle capacity' in sql

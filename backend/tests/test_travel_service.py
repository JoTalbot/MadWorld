from uuid import uuid4

import pytest

from app.application.travel_service import plan_travel


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

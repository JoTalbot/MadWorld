"""GET /api/v1/economy/overview against PostgreSQL (integration).

Regression: the query selected economy_jobs.kind, which does not exist (kind lives
on economy_recipes), so the endpoint returned 500 for every player on the real schema.
"""
import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    if not os.getenv("MADWORLD_DATABASE_URL"): pytest.skip("MADWORLD_DATABASE_URL is not configured")
    return TestClient(app)


def test_economy_overview_renders_for_bootstrapped_player(client) -> None:
    s = client.post("/api/v1/sessions", json={"handle": f"eco_{uuid4().hex[:8]}"}).json()
    auth = {"Authorization": f"Bearer {s['token']}"}
    assert client.post("/api/v1/players/bootstrap", json={"player_id": s["player_id"], "character_name": "Eco"}, headers={**auth, "Idempotency-Key": f"eco-{s['player_id']}"}).status_code == 201
    settlement = client.get("/api/v1/settlement", headers=auth); assert settlement.status_code == 200, settlement.text
    overview = client.get("/api/v1/economy/overview", headers=auth)
    assert overview.status_code == 200, overview.text
    body = overview.json()
    # NOTE: settlement_id here comes from player_settlement_state (economy model) and differs from
    # the phase-4 settlement aggregate id returned by /settlement; tracked as a follow-up.
    assert body["region"] and body["warehouse_capacity"] >= 1000 and isinstance(body["active_jobs"], list)

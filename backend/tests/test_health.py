from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_world() -> None:
    response = client.get("/api/v1/world")
    assert response.status_code == 200
    import os
    body = response.json()
    assert len(body["regions"]) == 3 and {r["id"] for r in body["regions"]} == {"dust_basin", "iron_ruins", "salt_coast"}
    # Static seed without a database; authoritative season/tick when PostgreSQL is configured.
    assert body["authoritative"] is bool(os.getenv("MADWORLD_DATABASE_URL"))

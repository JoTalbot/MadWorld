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
    assert len(response.json()["regions"]) == 3

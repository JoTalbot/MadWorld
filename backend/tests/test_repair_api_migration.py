from fastapi.testclient import TestClient

from app.main import app


def test_legacy_vehicle_repair_is_explicitly_retired() -> None:
    client = TestClient(app)
    response = client.post("/api/v1/vehicles/00000000-0000-0000-0000-000000000001/repair", json={"amount": 25})

    assert response.status_code == 410
    assert response.headers["Deprecation"] == "true"
    assert response.headers["Sunset"] == "Wed, 30 Sep 2026 00:00:00 GMT"
    assert response.headers["X-MadWorld-Migration"] == "vehicle-repair-v2"
    body = response.json()
    assert body["code"] == "LEGACY_API_GONE"
    assert body["details"]["replacement"].endswith("/repair-job")

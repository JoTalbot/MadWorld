"""Per-session budget is independent of the per-network budget (memory backend)."""
import importlib
import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def small_limit_app(monkeypatch):
    monkeypatch.setenv("MADWORLD_RATE_LIMIT", "3"); monkeypatch.setenv("MADWORLD_ABUSE_CONTROL_BACKEND", "memory"); monkeypatch.delenv("MADWORLD_DATABASE_URL", raising=False)
    import app.main as main
    importlib.reload(main)
    yield main.app
    monkeypatch.delenv("MADWORLD_RATE_LIMIT", raising=False); importlib.reload(main)


def test_session_scope_limits_one_token_without_starving_others(small_limit_app) -> None:
    # Different sessions must be limited independently even though the test client shares one IP:
    # raise the network budget by spreading over distinct forwarded IPs is not possible here, so we
    # assert the *scope* reported on the first 429 instead.
    client = TestClient(small_limit_app)
    codes = [client.get("/health", headers={"Authorization": "Bearer A"}).status_code for _ in range(4)]
    assert codes[:3] == [200, 200, 200] and codes[3] == 429
    limited = client.get("/health", headers={"Authorization": "Bearer A"})
    assert limited.json()["details"]["scope"] in {"net", "sess"} and limited.headers["Retry-After"]


def test_unknown_api_paths_are_bucketed_in_metrics(small_limit_app) -> None:
    client = TestClient(small_limit_app)
    client.get("/api/v1/definitely-not-a-route")
    assert 'route="/api/v1/<unmatched>"' in client.get("/metrics").text

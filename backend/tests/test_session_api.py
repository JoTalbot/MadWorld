"""Session lifecycle tests against the in-memory session store (no PostgreSQL required)."""
from datetime import timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import get_uow
from app.api.session_routes import get_session_store
from app.domain.primitives import utc_now
from app.infrastructure.memory import InMemoryUnitOfWork
from app.infrastructure.sessions import InMemorySessionStore, hash_token
from app.main import app


def _client(store: InMemorySessionStore) -> TestClient:
    uow = InMemoryUnitOfWork()
    def override_uow(): yield uow
    app.dependency_overrides[get_session_store] = lambda: store
    app.dependency_overrides[get_uow] = override_uow
    return TestClient(app)


def test_session_create_returns_token_and_authenticates_owner() -> None:
    store = InMemorySessionStore()
    try:
        client = _client(store)
        created = client.post("/api/v1/sessions", json={"handle": "rook_01"})
        assert created.status_code == 201
        body = created.json(); token = body["token"]; player_id = body["player_id"]
        assert hash_token(token) in store.sessions and token not in store.sessions
        again = client.post("/api/v1/sessions", json={"handle": "rook_01"}).json()
        assert again["player_id"] == player_id and again["token"] != token
        bootstrap = client.post("/api/v1/players/bootstrap", json={"player_id": player_id, "character_name": "Rook"}, headers={"Authorization": f"Bearer {token}", "Idempotency-Key": "s-1"})
        assert bootstrap.status_code == 201
        foreign = client.post("/api/v1/players/bootstrap", json={"player_id": str(uuid4()), "character_name": "X"}, headers={"Authorization": f"Bearer {token}", "Idempotency-Key": "s-2"})
        assert foreign.status_code == 403
    finally: app.dependency_overrides.clear()


def test_session_rejects_missing_invalid_revoked_and_expired_tokens() -> None:
    store = InMemorySessionStore()
    try:
        client = _client(store)
        player_id = str(uuid4())
        assert client.get(f"/api/v1/players/{player_id}/state").status_code == 401
        assert client.get(f"/api/v1/players/{player_id}/state", headers={"Authorization": "Bearer nope"}).status_code == 401
        assert client.get(f"/api/v1/players/{player_id}/state", headers={"Authorization": "Basic abc"}).status_code == 401
        token = client.post("/api/v1/sessions", json={"handle": "dust_02"}).json()["token"]
        store.revoke(token, utc_now())
        assert client.get(f"/api/v1/players/{player_id}/state", headers={"Authorization": f"Bearer {token}"}).status_code == 401
        expired = "expired-token"; store.create("late_03", expired, utc_now() - timedelta(days=40), utc_now() - timedelta(days=10))
        assert client.get(f"/api/v1/players/{player_id}/state", headers={"Authorization": f"Bearer {expired}"}).status_code == 401
    finally: app.dependency_overrides.clear()


def test_session_handle_validation() -> None:
    try:
        client = _client(InMemorySessionStore())
        assert client.post("/api/v1/sessions", json={"handle": "ab"}).status_code == 422
        assert client.post("/api/v1/sessions", json={"handle": "bad handle!"}).status_code == 422
    finally: app.dependency_overrides.clear()

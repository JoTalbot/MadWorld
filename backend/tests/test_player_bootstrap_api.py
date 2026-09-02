from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import get_uow
from app.infrastructure.memory import InMemoryUnitOfWork
from app.main import app


def test_player_bootstrap_is_atomic_and_idempotent() -> None:
    player_id = uuid4(); uow = InMemoryUnitOfWork()
    def override_uow(): yield uow
    app.dependency_overrides[get_uow] = override_uow
    try:
        client = TestClient(app); payload = {"player_id": str(player_id), "character_name": "Rook"}; headers = {"Idempotency-Key": "bootstrap-1"}
        first = client.post("/api/v1/players/bootstrap", json=payload, headers=headers); second = client.post("/api/v1/players/bootstrap", json=payload, headers=headers)
        assert first.status_code == 201 and second.status_code == 201 and first.json() == second.json()
        assert len(uow.characters.characters) == 1 and len(uow.vehicles.vehicles) == 1
    finally: app.dependency_overrides.clear()


def test_player_state_snapshot_reads_coherent_bootstrap_state() -> None:
    player_id = uuid4(); uow = InMemoryUnitOfWork()
    def override_uow(): yield uow
    app.dependency_overrides[get_uow] = override_uow
    try:
        client = TestClient(app)
        response = client.post("/api/v1/players/bootstrap", json={"player_id": str(player_id), "character_name": "Dust"}, headers={"Idempotency-Key": "bootstrap-state-1"})
        assert response.status_code == 201
        snapshot = client.get(f"/api/v1/players/{player_id}/state"); assert snapshot.status_code == 200
        body = snapshot.json(); assert body["character"]["name"] == "Dust"; assert len(body["vehicles"]) == 1
        assert body["vehicles"][0]["fuel"] == 25 and body["vehicles"][0]["state"] == "active"
    finally: app.dependency_overrides.clear()


def test_player_bootstrap_rolls_back_when_vehicle_creation_fails() -> None:
    player_id = uuid4(); uow = InMemoryUnitOfWork(); original_save = uow.vehicles.save
    def fail_save(vehicle): raise RuntimeError("simulated vehicle persistence failure")
    uow.vehicles.save = fail_save
    try:
        from app.application.services import PlayerBootstrapService
        try:
            with uow: PlayerBootstrapService(uow).bootstrap(player_id, "Rollback")
        except RuntimeError: pass
    finally: uow.vehicles.save = original_save
    assert uow.characters.characters == {} and uow.vehicles.vehicles == {}

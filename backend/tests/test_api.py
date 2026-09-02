from datetime import timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import get_authenticated_player, get_uow
from app.domain.primitives import InventoryStack, Wallet, utc_now
from app.infrastructure.memory import InMemoryUnitOfWork
from app.main import app


def _auth(player_id):
    def override_auth(): return player_id
    app.dependency_overrides[get_authenticated_player] = override_auth


def test_health_exposes_request_id() -> None:
    response = TestClient(app).get("/health", headers={"X-Request-ID": "req-test"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test"
    assert response.json()["status"] == "ok"


def test_wallet_command_is_idempotent_and_returns_contract() -> None:
    player_id = uuid4(); wallet_id = uuid4(); uow = InMemoryUnitOfWork(wallets=None)
    from app.infrastructure.memory import InMemoryWalletRepository
    uow.wallets = InMemoryWalletRepository({wallet_id: Wallet(wallet_id, 100)}); uow.wallets.owners = {wallet_id: player_id}; _auth(player_id)
    def override_uow(): yield uow
    app.dependency_overrides[get_uow] = override_uow
    try:
        client = TestClient(app); payload = {"wallet_id": str(wallet_id), "amount": 25, "reason": "test reward"}; headers = {"Idempotency-Key": "wallet-test-1"}
        first = client.post("/api/v1/wallet/entries", json=payload, headers=headers); second = client.post("/api/v1/wallet/entries", json=payload, headers=headers)
        assert first.status_code == 201 and second.status_code == 201 and first.json() == second.json(); assert uow.wallets.wallets[wallet_id].balance == 125
        conflict = client.post("/api/v1/wallet/entries", json={"wallet_id": str(wallet_id), "amount": 50, "reason": "different"}, headers=headers)
        assert conflict.status_code == 409 and conflict.json()["code"] == "IDEMPOTENCY_CONFLICT"
    finally: app.dependency_overrides.clear()


def test_inventory_and_job_commands() -> None:
    inventory_id = uuid4(); item_id = uuid4(); owner_id = uuid4(); uow = InMemoryUnitOfWork()
    uow.inventories.stacks[(inventory_id, item_id)] = InventoryStack(item_id, 5, 100); uow.inventories.owners = {inventory_id: owner_id}; _auth(owner_id)
    def override_uow(): yield uow
    app.dependency_overrides[get_uow] = override_uow
    try:
        client = TestClient(app)
        response = client.post("/api/v1/inventory/remove", json={"inventory_id": str(inventory_id), "item_definition_id": str(item_id), "quantity": 2}, headers={"Idempotency-Key": "inventory-remove-1"})
        assert response.status_code == 200 and response.json()["quantity"] == 3
        start = utc_now(); job = client.post("/api/v1/jobs", json={"owner_id": str(owner_id), "job_type": "craft", "started_at": start.isoformat(), "completes_at": (start + timedelta(seconds=1)).isoformat()}, headers={"Idempotency-Key": "job-test-1"})
        assert job.status_code == 201; job_id = job.json()["id"]
        started = client.post(f"/api/v1/jobs/{job_id}/start", headers={"Idempotency-Key": "job-start-1"}); repeated = client.post(f"/api/v1/jobs/{job_id}/start", headers={"Idempotency-Key": "job-start-1"})
        assert started.status_code == 200 and repeated.status_code == 200 and started.json() == repeated.json() and started.json()["state"] == "running"
    finally: app.dependency_overrides.clear()


def test_state_changing_job_commands_require_idempotency_key() -> None:
    player_id = uuid4(); uow = InMemoryUnitOfWork(); _auth(player_id)
    def override_uow(): yield uow
    app.dependency_overrides[get_uow] = override_uow
    try:
        response = TestClient(app).post(f"/api/v1/jobs/{uuid4()}/start"); assert response.status_code == 400
    finally: app.dependency_overrides.clear()


def test_api_error_envelope_for_missing_wallet() -> None:
    player_id = uuid4(); uow = InMemoryUnitOfWork(); _auth(player_id)
    def override_uow(): yield uow
    app.dependency_overrides[get_uow] = override_uow
    try:
        response = TestClient(app).post("/api/v1/wallet/entries", json={"wallet_id": str(uuid4()), "amount": 10, "reason": "missing"}, headers={"Idempotency-Key": "missing-wallet-1", "X-Request-ID": "req-404"})
        assert response.status_code == 404 and response.json()["code"] == "NOT_FOUND" and response.json()["request_id"] == "req-404"
    finally: app.dependency_overrides.clear()


def test_character_and_vehicle_api_commands_are_idempotent() -> None:
    player_id = uuid4(); uow = InMemoryUnitOfWork(); _auth(player_id)
    def override_uow(): yield uow
    app.dependency_overrides[get_uow] = override_uow
    try:
        client = TestClient(app); character_payload = {"player_id": str(player_id), "name": "Rook"}
        first = client.post("/api/v1/characters", json=character_payload, headers={"Idempotency-Key": "character-1"}); repeated = client.post("/api/v1/characters", json=character_payload, headers={"Idempotency-Key": "character-1"})
        assert first.status_code == 201 and repeated.status_code == 201 and first.json() == repeated.json() and first.json()["name"] == "Rook"
        fetched = client.get(f"/api/v1/characters/by-player/{player_id}"); assert fetched.status_code == 200 and fetched.json() == first.json()
        vehicle_payload = {"owner_id": str(player_id)}; vehicle = client.post("/api/v1/vehicles/starter", json=vehicle_payload, headers={"Idempotency-Key": "vehicle-1"}); vehicle_repeat = client.post("/api/v1/vehicles/starter", json=vehicle_payload, headers={"Idempotency-Key": "vehicle-1"})
        assert vehicle.status_code == 201 and vehicle_repeat.status_code == 201 and vehicle.json() == vehicle_repeat.json(); assert vehicle.json()["chassis_code"] == "light_runner" and vehicle.json()["durability"] == 100 and vehicle.json()["fuel"] == 25
        listed = client.get(f"/api/v1/vehicles/by-owner/{player_id}"); assert listed.status_code == 200 and listed.json() == [vehicle.json()]
        vehicle_id = vehicle.json()["id"]; repaired = client.post(f"/api/v1/vehicles/{vehicle_id}/repair", json={"amount": 10}, headers={"Idempotency-Key": "repair-1"}); assert repaired.status_code == 200 and repaired.json()["durability"] == 100
        refueled = client.post(f"/api/v1/vehicles/{vehicle_id}/refuel", json={"amount": 15}, headers={"Idempotency-Key": "refuel-1"}); refueled_repeat = client.post(f"/api/v1/vehicles/{vehicle_id}/refuel", json={"amount": 15}, headers={"Idempotency-Key": "refuel-1"})
        assert refueled.status_code == 200 and refueled_repeat.status_code == 200 and refueled.json() == refueled_repeat.json() and refueled.json()["fuel"] == 40
    finally: app.dependency_overrides.clear()


def test_player_owned_endpoints_reject_wrong_session() -> None:
    owner_id = uuid4(); attacker_id = uuid4(); uow = InMemoryUnitOfWork(); _auth(attacker_id)
    from app.application.services import CharacterService, JobService, VehicleService
    from app.domain.primitives import Character
    with uow:
        character = Character.create(owner_id, "Owner"); uow.characters.save(character)
        vehicle = VehicleService(uow).create_starter(owner_id)
        start = utc_now(); job = JobService(uow).create(owner_id, "craft", start, start + timedelta(seconds=1), "seed-job")
    def override_uow(): yield uow
    app.dependency_overrides[get_uow] = override_uow
    try:
        client = TestClient(app)
        assert client.post("/api/v1/characters", json={"player_id": str(owner_id), "name": "Attack"}, headers={"Idempotency-Key": "attack-char"}).status_code == 403
        assert client.get(f"/api/v1/characters/by-player/{owner_id}").status_code == 403
        assert client.get(f"/api/v1/vehicles/{vehicle.id}").status_code == 403
        assert client.get(f"/api/v1/vehicles/by-owner/{owner_id}").status_code == 403
        assert client.post(f"/api/v1/jobs/{job.id}/start", headers={"Idempotency-Key": "attack-job"}).status_code == 403
        assert client.post("/api/v1/jobs", json={"owner_id": str(owner_id), "job_type": "craft", "started_at": start.isoformat(), "completes_at": (start + timedelta(seconds=1)).isoformat()}, headers={"Idempotency-Key": "attack-job-create"}).status_code == 403
    finally: app.dependency_overrides.clear()


def test_owned_endpoints_require_bearer_session() -> None:
    app.dependency_overrides.clear(); uow = InMemoryUnitOfWork()
    def override_uow(): yield uow
    app.dependency_overrides[get_uow] = override_uow
    try:
        client = TestClient(app); player_id = uuid4()
        assert client.get(f"/api/v1/characters/by-player/{player_id}").status_code == 401
        assert client.get(f"/api/v1/vehicles/by-owner/{player_id}").status_code == 401
        assert client.post("/api/v1/jobs", json={"owner_id": str(player_id), "job_type": "craft", "started_at": utc_now().isoformat(), "completes_at": (utc_now() + timedelta(seconds=1)).isoformat()}, headers={"Idempotency-Key": "no-auth"}).status_code == 401
    finally: app.dependency_overrides.clear()

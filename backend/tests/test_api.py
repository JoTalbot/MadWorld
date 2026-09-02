from datetime import timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import get_uow
from app.domain.primitives import InventoryStack, Wallet, utc_now
from app.infrastructure.memory import InMemoryUnitOfWork
from app.main import app


def test_health_exposes_request_id() -> None:
    response = TestClient(app).get("/health", headers={"X-Request-ID": "req-test"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test"
    assert response.json()["status"] == "ok"


def test_wallet_command_is_idempotent_and_returns_contract() -> None:
    wallet_id = uuid4()
    uow = InMemoryUnitOfWork(wallets=None)
    # Build the default repositories explicitly so this test remains readable.
    from app.infrastructure.memory import InMemoryWalletRepository
    uow.wallets = InMemoryWalletRepository({wallet_id: Wallet(wallet_id, 100)})

    def override_uow():
        yield uow

    app.dependency_overrides[get_uow] = override_uow
    try:
        client = TestClient(app)
        payload = {"wallet_id": str(wallet_id), "amount": 25, "reason": "test reward"}
        first = client.post("/api/v1/wallet/entries", json=payload, headers={"Idempotency-Key": "wallet-test-1"})
        second = client.post("/api/v1/wallet/entries", json=payload, headers={"Idempotency-Key": "wallet-test-1"})
        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json() == second.json()
        assert uow.wallets.wallets[wallet_id].balance == 125
    finally:
        app.dependency_overrides.clear()


def test_inventory_and_job_commands() -> None:
    inventory_id = uuid4()
    item_id = uuid4()
    owner_id = uuid4()
    uow = InMemoryUnitOfWork()
    uow.inventories.stacks[(inventory_id, item_id)] = InventoryStack(item_id, 5, 100)

    def override_uow():
        yield uow

    app.dependency_overrides[get_uow] = override_uow
    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/inventory/remove",
            json={"inventory_id": str(inventory_id), "item_definition_id": str(item_id), "quantity": 2},
        )
        assert response.status_code == 200
        assert response.json()["quantity"] == 3

        start = utc_now()
        job = client.post(
            "/api/v1/jobs",
            json={
                "owner_id": str(owner_id),
                "job_type": "craft",
                "started_at": start.isoformat(),
                "completes_at": (start + timedelta(seconds=1)).isoformat(),
            },
            headers={"Idempotency-Key": "job-test-1"},
        )
        assert job.status_code == 201
        job_id = job.json()["id"]
        started = client.post(f"/api/v1/jobs/{job_id}/start")
        assert started.status_code == 200
        assert started.json()["state"] == "running"
    finally:
        app.dependency_overrides.clear()


def test_api_error_envelope_for_missing_wallet() -> None:
    uow = InMemoryUnitOfWork()

    def override_uow():
        yield uow

    app.dependency_overrides[get_uow] = override_uow
    try:
        response = TestClient(app).post(
            "/api/v1/wallet/entries",
            json={"wallet_id": str(uuid4()), "amount": 10, "reason": "missing"},
            headers={"Idempotency-Key": "missing-wallet-1", "X-Request-ID": "req-404"},
        )
        assert response.status_code == 404
        assert response.json()["code"] == "NOT_FOUND"
        assert response.json()["request_id"] == "req-404"
    finally:
        app.dependency_overrides.clear()

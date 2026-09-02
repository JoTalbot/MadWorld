import os
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import text

from app.application.services import InventoryService, JobService, WalletService
from app.domain.primitives import utc_now
from app.infrastructure.db import create_engine_from_env
from app.infrastructure.postgres import PostgresUnitOfWork


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def engine():
    if not os.getenv("MADWORLD_DATABASE_URL"):
        pytest.skip("MADWORLD_DATABASE_URL is not configured")
    engine = create_engine_from_env()
    yield engine
    engine.dispose()


def seed_player(engine, prefix: str) -> tuple:
    player_id, wallet_id, inventory_id, item_id = uuid4(), uuid4(), uuid4(), uuid4()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO players (id, handle) VALUES (:id, :handle)"),
                     {"id": player_id, "handle": f"{prefix}-{player_id.hex[:12]}"})
        conn.execute(text("INSERT INTO wallets (id, owner_id) VALUES (:id, :owner_id)"),
                     {"id": wallet_id, "owner_id": player_id})
        conn.execute(text("INSERT INTO inventories (id, owner_id, name) VALUES (:id, :owner_id, 'test')"),
                     {"id": inventory_id, "owner_id": player_id})
        conn.execute(text("INSERT INTO item_definitions (id, code, name, category) VALUES (:id, :code, 'Test Item', 'test')"),
                     {"id": item_id, "code": f"test-{item_id.hex}"})
    return player_id, wallet_id, inventory_id, item_id


def test_postgres_wallet_inventory_and_outbox_are_transactional(engine) -> None:
    player_id, wallet_id, inventory_id, item_id = seed_player(engine, "pg")
    with PostgresUnitOfWork(engine) as uow:
        WalletService(uow).post_entry(wallet_id, 100, "starter", "pg-wallet-1")

    with PostgresUnitOfWork(engine) as uow:
        InventoryService(uow).add(inventory_id, item_id, 5)

    with engine.connect() as conn:
        balance = conn.execute(text("SELECT COALESCE(SUM(amount), 0) FROM ledger_entries WHERE wallet_id = :id"), {"id": wallet_id}).scalar_one()
        quantity = conn.execute(text("SELECT quantity FROM inventory_items WHERE inventory_id = :inventory_id AND item_definition_id = :item_id"),
                                {"inventory_id": inventory_id, "item_id": item_id}).scalar_one()
        events = conn.execute(text("SELECT count(*) FROM outbox_events WHERE aggregate_id IN (:wallet, :inventory)"),
                              {"wallet": wallet_id, "inventory": inventory_id}).scalar_one()
    assert balance == 100
    assert quantity == 5
    assert events == 2


def test_postgres_job_idempotency_and_state_persistence(engine) -> None:
    player_id, _, _, _ = seed_player(engine, "job")
    now = utc_now()
    with PostgresUnitOfWork(engine) as uow:
        service = JobService(uow)
        job = service.create(player_id, "craft", now, now + timedelta(seconds=1), "pg-job-1")

    with PostgresUnitOfWork(engine) as uow:
        service = JobService(uow)
        same = service.create(player_id, "craft", now, now + timedelta(seconds=1), "pg-job-1")
        assert same.id == job.id
        service.start(job.id)
        completed = service.complete(job.id, now + timedelta(seconds=1))
        assert completed.state.value == "completed"

    with engine.connect() as conn:
        state = conn.execute(text("SELECT state FROM jobs WHERE id = :id"), {"id": job.id}).scalar_one()
    assert state == "completed"

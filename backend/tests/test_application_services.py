"""Application service tests using the in-memory transactional adapter."""

from datetime import timedelta
from uuid import uuid4

import pytest

from app.application.errors import ConcurrencyConflict, IdempotencyConflict
from app.application.services import InventoryService, JobService, WalletService
from app.domain.primitives import Wallet, utc_now
from app.infrastructure.memory import InMemoryUnitOfWork


def test_wallet_entry_is_idempotent_and_emits_audit_and_outbox() -> None:
    uow = InMemoryUnitOfWork()
    wallet_id = uuid4()
    uow.wallets.save(Wallet(wallet_id, 100))
    service = WalletService(uow)

    first = service.post_entry(wallet_id, -30, "fuel", "fuel-1")
    second = service.post_entry(wallet_id, -30, "fuel", "fuel-1")

    assert first == second
    assert uow.wallets.get(wallet_id).balance == 70
    assert len(uow.wallets.ledger) == 1
    assert len(uow.audit.events) == 1
    assert len(uow.outbox.events) == 1


def test_reusing_idempotency_key_for_different_operation_is_rejected() -> None:
    uow = InMemoryUnitOfWork()
    wallet_id = uuid4()
    uow.wallets.save(Wallet(wallet_id, 100))
    service = WalletService(uow)
    service.post_entry(wallet_id, -10, "fuel", "same-key")
    with pytest.raises(IdempotencyConflict):
        service.post_entry(wallet_id, -20, "fuel", "same-key")


def test_inventory_add_and_remove_emit_events() -> None:
    uow = InMemoryUnitOfWork()
    inventory_id, item_id = uuid4(), uuid4()
    service = InventoryService(uow)
    service.add(inventory_id, item_id, 5)
    service.remove(inventory_id, item_id, 2)
    stack = uow.inventories.get_stack(inventory_id, item_id)
    assert stack is not None and stack.quantity == 3
    assert len(uow.outbox.events) == 2


def test_job_service_records_completion() -> None:
    uow = InMemoryUnitOfWork()
    now = utc_now()
    job = JobService(uow).create(uuid4(), "craft", now, now + timedelta(seconds=1), "job-1")
    JobService(uow).start(job.id)
    completed = JobService(uow).complete(job.id, now + timedelta(seconds=1))
    assert completed.state.value == "completed"
    assert [e["event_type"] for e in uow.outbox.events] == ["job.created", "job.started", "job.completed"]
    assert all("event_id" in e["payload"] and e["payload"]["schema_version"] == 1 for e in uow.outbox.events)


def test_stale_job_write_is_rejected() -> None:
    uow = InMemoryUnitOfWork()
    now = utc_now()
    job = JobService(uow).create(uuid4(), "craft", now, now + timedelta(seconds=1), "job-concurrency")
    first_read = uow.jobs.get(job.id)
    second_read = uow.jobs.get(job.id)
    assert first_read is not None and second_read is not None

    first_read.start()
    uow.jobs.save(first_read)

    second_read.start()
    with pytest.raises(ConcurrencyConflict):
        uow.jobs.save(second_read)


def test_stale_inventory_write_is_rejected() -> None:
    uow = InMemoryUnitOfWork()
    inventory_id, item_id = uuid4(), uuid4()
    service = InventoryService(uow)
    service.add(inventory_id, item_id, 5)
    first_read = uow.inventories.get_stack(inventory_id, item_id)
    second_read = uow.inventories.get_stack(inventory_id, item_id)
    assert first_read is not None and second_read is not None

    first_read.quantity += 1
    uow.inventories.save_stack(inventory_id, first_read)

    second_read.quantity += 1
    with pytest.raises(ConcurrencyConflict):
        uow.inventories.save_stack(inventory_id, second_read)


def test_in_memory_uow_rollback_restores_domain_audit_outbox_and_idempotency() -> None:
    wallet_id = uuid4()
    uow = InMemoryUnitOfWork()
    uow.wallets.save(Wallet(wallet_id, 100))

    with pytest.raises(RuntimeError, match="fault injection"):
        with uow:
            WalletService(uow).post_entry(wallet_id, -40, "rollback", "rollback-1")
            raise RuntimeError("fault injection")

    wallet = uow.wallets.get(wallet_id)
    assert wallet is not None and wallet.balance == 100
    assert uow.wallets.get_ledger_entry_by_idempotency_key("rollback-1") is None
    assert uow.audit.events == []
    assert uow.outbox.events == []
    assert uow.idempotency.records == {}
    assert uow.rolled_back is True
    assert uow.committed is False

from uuid import uuid4

from app.domain.primitives import LedgerEntry, Wallet
from app.infrastructure.memory import InMemoryUnitOfWork


def test_memory_uow_exposes_all_authoritative_boundaries() -> None:
    with InMemoryUnitOfWork() as uow:
        wallet = Wallet(uuid4(), balance=100)
        uow.wallets.save(wallet)
        uow.audit.append("wallet.created", "wallet", wallet.id, {})
        uow.outbox.enqueue("wallet.created", "wallet", wallet.id, {})

    assert uow.committed is True
    assert uow.rolled_back is False
    assert uow.wallets.get(wallet.id) is wallet
    assert len(uow.audit.events) == 1
    assert len(uow.outbox.events) == 1


def test_ledger_idempotency_key_is_unique_in_memory() -> None:
    wallet_id = uuid4()
    entry = LedgerEntry(uuid4(), wallet_id, 50, "reward", "same-command", __import__("app.domain.primitives", fromlist=["utc_now"]).utc_now())
    uow = InMemoryUnitOfWork()
    uow.wallets.add_ledger_entry(entry)
    uow.wallets.add_ledger_entry(entry)

    assert len(uow.wallets.ledger) == 1
    assert uow.wallets.get_ledger_entry_by_idempotency_key("same-command") is entry

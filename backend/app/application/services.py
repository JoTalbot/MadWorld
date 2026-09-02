"""Small use cases that enforce authoritative transaction boundaries."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from app.application.errors import IdempotencyConflict, NotFound
from app.application.ports import UnitOfWork
from app.domain.primitives import InventoryStack, Job, LedgerEntry, utc_now


class WalletService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def post_entry(self, wallet_id: UUID, amount: int, reason: str, idempotency_key: str, actor_id: UUID | None = None) -> LedgerEntry:
        existing = self.uow.wallets.get_ledger_entry_by_idempotency_key(idempotency_key)
        if existing is not None:
            if (existing.wallet_id, existing.amount, existing.reason) != (wallet_id, amount, reason):
                raise IdempotencyConflict("idempotency key already belongs to another operation")
            return existing
        wallet = self.uow.wallets.get(wallet_id)
        if wallet is None:
            raise NotFound("wallet not found")
        if amount >= 0:
            wallet.credit(amount)
        else:
            wallet.debit(-amount)
        entry = LedgerEntry(uuid4(), wallet_id, amount, reason, idempotency_key, utc_now())
        self.uow.wallets.save(wallet)
        self.uow.wallets.add_ledger_entry(entry)
        self._record("wallet.entry_posted", "wallet", wallet_id, {"entry_id": str(entry.id), "amount": amount, "reason": reason, "actor_id": str(actor_id) if actor_id else None})
        self.uow.commit()
        return entry

    def _record(self, event_type: str, aggregate_type: str, aggregate_id: UUID, payload: dict) -> None:
        self.uow.audit.append(event_type, aggregate_type, aggregate_id, payload)
        self.uow.outbox.enqueue(event_type, aggregate_type, aggregate_id, payload)


class InventoryService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def add(self, inventory_id: UUID, item_definition_id: UUID, quantity: int, condition: int = 100) -> InventoryStack:
        if quantity <= 0:
            raise ValueError("inventory quantity must be positive")
        stack = self.uow.inventories.get_stack(inventory_id, item_definition_id)
        if stack is None:
            stack = InventoryStack(item_definition_id, quantity, condition)
        else:
            if stack.condition != condition and stack.quantity > 0:
                raise ValueError("cannot merge inventory stacks with different condition")
            stack.quantity += quantity
        self.uow.inventories.save_stack(inventory_id, stack)
        self._record("inventory.item_added", inventory_id, {"item_definition_id": str(item_definition_id), "quantity": quantity, "condition": condition})
        self.uow.commit()
        return stack

    def remove(self, inventory_id: UUID, item_definition_id: UUID, quantity: int) -> InventoryStack | None:
        if quantity <= 0:
            raise ValueError("inventory quantity must be positive")
        stack = self.uow.inventories.get_stack(inventory_id, item_definition_id)
        if stack is None or stack.quantity < quantity:
            raise ValueError("inventory quantity is insufficient")
        remaining = stack.quantity - quantity
        if remaining == 0:
            self.uow.inventories.delete_stack(inventory_id, item_definition_id, stack.version)
            result = None
        else:
            stack.quantity = remaining
            self.uow.inventories.save_stack(inventory_id, stack)
            result = stack
        self._record("inventory.item_removed", inventory_id, {"item_definition_id": str(item_definition_id), "quantity": quantity})
        self.uow.commit()
        return result

    def _record(self, event_type: str, inventory_id: UUID, payload: dict) -> None:
        self.uow.audit.append(event_type, "inventory", inventory_id, payload)
        self.uow.outbox.enqueue(event_type, "inventory", inventory_id, payload)


class JobService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def create(self, owner_id: UUID, job_type: str, started_at: datetime, completes_at: datetime, idempotency_key: str) -> Job:
        existing = self.uow.jobs.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            if (existing.owner_id, existing.job_type, existing.started_at, existing.completes_at) != (owner_id, job_type, started_at, completes_at):
                raise IdempotencyConflict("idempotency key already belongs to another job")
            return existing
        job = Job.create(owner_id, job_type, started_at, completes_at)
        self.uow.jobs.save(job)
        self.uow.jobs.bind_idempotency_key(idempotency_key, job.id)
        self.uow.audit.append("job.created", "job", job.id, {"job_type": job_type})
        self.uow.outbox.enqueue("job.created", "job", job.id, {"job_type": job_type})
        self.uow.commit()
        return job

    def start(self, job_id: UUID) -> Job:
        job = self._get(job_id)
        job.start()
        return self._save(job, "job.started")

    def complete(self, job_id: UUID, now: datetime | None = None) -> Job:
        job = self._get(job_id)
        job.complete(now or utc_now())
        return self._save(job, "job.completed")

    def cancel(self, job_id: UUID) -> Job:
        job = self._get(job_id)
        job.cancel()
        return self._save(job, "job.cancelled")

    def _get(self, job_id: UUID) -> Job:
        job = self.uow.jobs.get(job_id)
        if job is None:
            raise NotFound("job not found")
        return job

    def _save(self, job: Job, event_type: str) -> Job:
        self.uow.jobs.save(job)
        self.uow.audit.append(event_type, "job", job.id, {"state": job.state.value})
        self.uow.outbox.enqueue(event_type, "job", job.id, {"state": job.state.value})
        self.uow.commit()
        return job

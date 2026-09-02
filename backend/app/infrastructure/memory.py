"""In-memory repositories used by application tests and local development."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from uuid import UUID

from app.application.errors import ConcurrencyConflict
from app.domain.primitives import InventoryStack, Job, LedgerEntry, Wallet


@dataclass
class InMemoryWalletRepository:
    wallets: dict[UUID, Wallet] = field(default_factory=dict)
    ledger: dict[str, LedgerEntry] = field(default_factory=dict)

    def get(self, wallet_id: UUID) -> Wallet | None:
        wallet = self.wallets.get(wallet_id)
        return deepcopy(wallet) if wallet else None

    def save(self, wallet: Wallet) -> None:
        current = self.wallets.get(wallet.id)
        if current is not None and current.version != wallet.version:
            raise ConcurrencyConflict("wallet changed since it was read")
        wallet.version += 1
        self.wallets[wallet.id] = deepcopy(wallet)

    def add_ledger_entry(self, entry: LedgerEntry) -> None:
        if entry.idempotency_key in self.ledger:
            return
        self.ledger[entry.idempotency_key] = entry

    def get_ledger_entry_by_idempotency_key(self, key: str) -> LedgerEntry | None:
        return self.ledger.get(key)


@dataclass
class InMemoryInventoryRepository:
    stacks: dict[tuple[UUID, UUID], InventoryStack] = field(default_factory=dict)

    def get_stack(self, inventory_id: UUID, item_definition_id: UUID) -> InventoryStack | None:
        stack = self.stacks.get((inventory_id, item_definition_id))
        return deepcopy(stack) if stack else None

    def save_stack(self, inventory_id: UUID, stack: InventoryStack) -> None:
        key = (inventory_id, stack.item_definition_id)
        current = self.stacks.get(key)
        if current is not None and current.version != stack.version:
            raise ConcurrencyConflict("inventory stack changed since it was read")
        stack.version += 1
        self.stacks[key] = deepcopy(stack)

    def delete_stack(self, inventory_id: UUID, item_definition_id: UUID) -> None:
        self.stacks.pop((inventory_id, item_definition_id), None)


@dataclass
class InMemoryJobRepository:
    jobs: dict[UUID, Job] = field(default_factory=dict)
    idempotency: dict[str, UUID] = field(default_factory=dict)

    def get(self, job_id: UUID) -> Job | None:
        job = self.jobs.get(job_id)
        return deepcopy(job) if job else None

    def get_by_idempotency_key(self, key: str) -> Job | None:
        job_id = self.idempotency.get(key)
        job = self.jobs.get(job_id) if job_id else None
        return deepcopy(job) if job else None

    def save(self, job: Job) -> None:
        current = self.jobs.get(job.id)
        if current is not None and current.version != job.version:
            raise ConcurrencyConflict("job changed since it was read")
        job.version += 1
        self.jobs[job.id] = deepcopy(job)

    def bind_idempotency_key(self, key: str, job_id: UUID) -> None:
        existing = self.idempotency.get(key)
        if existing is not None and existing != job_id:
            raise ConcurrencyConflict("idempotency key is already bound")
        self.idempotency[key] = job_id


@dataclass
class InMemoryAuditRepository:
    events: list[dict] = field(default_factory=list)

    def append(self, event_type: str, aggregate_type: str, aggregate_id: UUID, payload: dict) -> None:
        self.events.append({"event_type": event_type, "aggregate_type": aggregate_type, "aggregate_id": aggregate_id, "payload": payload})


@dataclass
class InMemoryOutboxRepository:
    events: list[dict] = field(default_factory=list)

    def enqueue(self, event_type: str, aggregate_type: str, aggregate_id: UUID, payload: dict) -> None:
        self.events.append({"event_type": event_type, "aggregate_type": aggregate_type, "aggregate_id": aggregate_id, "payload": payload})


@dataclass
class InMemoryUnitOfWork:
    wallets: InMemoryWalletRepository = field(default_factory=InMemoryWalletRepository)
    inventories: InMemoryInventoryRepository = field(default_factory=InMemoryInventoryRepository)
    jobs: InMemoryJobRepository = field(default_factory=InMemoryJobRepository)
    audit: InMemoryAuditRepository = field(default_factory=InMemoryAuditRepository)
    outbox: InMemoryOutboxRepository = field(default_factory=InMemoryOutboxRepository)
    committed: bool = False
    rolled_back: bool = False

    def __enter__(self) -> "InMemoryUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

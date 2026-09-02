"""In-memory repositories used by application tests and local development."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.application.errors import ConcurrencyConflict, IdempotencyConflict
from app.application.ports import IdempotencyRecord, OutboxEvent
from app.domain.primitives import Character, InventoryStack, Job, LedgerEntry, Vehicle, Wallet


@dataclass
class InMemoryWalletRepository:
    wallets: dict[UUID, Wallet] = field(default_factory=dict)
    ledger: dict[str, LedgerEntry] = field(default_factory=dict)
    def get(self, wallet_id: UUID) -> Wallet | None:
        wallet = self.wallets.get(wallet_id); return deepcopy(wallet) if wallet else None
    def save(self, wallet: Wallet) -> None:
        current = self.wallets.get(wallet.id)
        if current is not None and current.version != wallet.version: raise ConcurrencyConflict("wallet changed since it was read")
        wallet.version += 1; self.wallets[wallet.id] = deepcopy(wallet)
    def add_ledger_entry(self, entry: LedgerEntry) -> None:
        existing = self.ledger.get(entry.idempotency_key)
        if existing is not None and existing != entry: raise IdempotencyConflict("ledger idempotency key already exists")
        self.ledger[entry.idempotency_key] = entry
    def get_ledger_entry_by_idempotency_key(self, key: str) -> LedgerEntry | None: return self.ledger.get(key)


@dataclass
class InMemoryInventoryRepository:
    stacks: dict[tuple[UUID, UUID], InventoryStack] = field(default_factory=dict)
    def get_stack(self, inventory_id: UUID, item_definition_id: UUID) -> InventoryStack | None:
        stack = self.stacks.get((inventory_id, item_definition_id)); return deepcopy(stack) if stack else None
    def save_stack(self, inventory_id: UUID, stack: InventoryStack) -> None:
        key = (inventory_id, stack.item_definition_id); current = self.stacks.get(key)
        if current is not None and current.version != stack.version: raise ConcurrencyConflict("inventory stack changed since it was read")
        stack.version += 1; self.stacks[key] = deepcopy(stack)
    def delete_stack(self, inventory_id: UUID, item_definition_id: UUID, expected_version: int) -> None:
        key = (inventory_id, item_definition_id); current = self.stacks.get(key)
        if current is None or current.version != expected_version: raise ConcurrencyConflict("inventory stack changed since it was read")
        del self.stacks[key]


@dataclass
class InMemoryJobRepository:
    jobs: dict[UUID, Job] = field(default_factory=dict)
    idempotency: dict[str, UUID] = field(default_factory=dict)
    def get(self, job_id: UUID) -> Job | None:
        job = self.jobs.get(job_id); return deepcopy(job) if job else None
    def get_by_idempotency_key(self, key: str) -> Job | None:
        job_id = self.idempotency.get(key); job = self.jobs.get(job_id) if job_id else None; return deepcopy(job) if job else None
    def save(self, job: Job) -> None:
        current = self.jobs.get(job.id)
        if current is not None and current.version != job.version: raise ConcurrencyConflict("job changed since it was read")
        job.version += 1; self.jobs[job.id] = deepcopy(job)
    def bind_idempotency_key(self, key: str, job_id: UUID) -> None:
        existing = self.idempotency.get(key)
        if existing is not None and existing != job_id: raise IdempotencyConflict("idempotency key is already bound")
        self.idempotency[key] = job_id


@dataclass
class InMemoryCharacterRepository:
    characters: dict[UUID, Character] = field(default_factory=dict)
    def get(self, character_id: UUID) -> Character | None:
        character = self.characters.get(character_id); return deepcopy(character) if character else None
    def get_by_player_id(self, player_id: UUID) -> Character | None:
        character = next((c for c in self.characters.values() if c.player_id == player_id), None)
        return deepcopy(character) if character else None
    def save(self, character: Character) -> None:
        current = self.characters.get(character.id)
        if current is not None and current.version != character.version: raise ConcurrencyConflict("character changed since it was read")
        character.version += 1; self.characters[character.id] = deepcopy(character)


@dataclass
class InMemoryVehicleRepository:
    vehicles: dict[UUID, Vehicle] = field(default_factory=dict)
    def get(self, vehicle_id: UUID) -> Vehicle | None:
        vehicle = self.vehicles.get(vehicle_id); return deepcopy(vehicle) if vehicle else None
    def list_by_owner(self, owner_id: UUID) -> list[Vehicle]:
        return [deepcopy(v) for v in self.vehicles.values() if v.owner_id == owner_id]
    def lock_owner_for_starter(self, owner_id: UUID) -> None:
        return None
    def save(self, vehicle: Vehicle) -> None:
        current = self.vehicles.get(vehicle.id)
        if current is not None and current.version != vehicle.version: raise ConcurrencyConflict("vehicle changed since it was read")
        vehicle.version += 1; self.vehicles[vehicle.id] = deepcopy(vehicle)


@dataclass
class InMemoryIdempotencyRepository:
    records: dict[tuple[str, str], IdempotencyRecord] = field(default_factory=dict)
    def get(self, command_name: str, idempotency_key: str) -> IdempotencyRecord | None: return self.records.get((command_name, idempotency_key))
    def put(self, record: IdempotencyRecord) -> None:
        key = (record.command_name, record.idempotency_key); existing = self.records.get(key)
        if existing is not None and existing.request_hash != record.request_hash: raise IdempotencyConflict("idempotency key belongs to a different request")
        self.records[key] = record


@dataclass
class InMemoryAuditRepository:
    events: list[dict] = field(default_factory=list)
    def append(self, event_type: str, aggregate_type: str, aggregate_id: UUID, payload: dict) -> None:
        self.events.append({"event_type": event_type, "aggregate_type": aggregate_type, "aggregate_id": aggregate_id, "payload": payload})


@dataclass
class InMemoryOutboxRepository:
    events: list[dict] = field(default_factory=list)
    def enqueue(self, event_type: str, aggregate_type: str, aggregate_id: UUID, payload: dict) -> None:
        self.events.append({"id": uuid4(), "event_type": event_type, "aggregate_type": aggregate_type, "aggregate_id": aggregate_id, "payload": deepcopy(payload), "attempts": 0, "lease_owner": None, "lease_until": None, "published": False})
    def claim(self, owner: str, limit: int = 50, lease_seconds: int = 60, max_attempts: int = 10) -> list[OutboxEvent]:
        now = datetime.now(timezone.utc); result = []
        for event in self.events:
            if len(result) >= limit: break
            if event["published"] or event["attempts"] >= max_attempts: continue
            if event["lease_until"] and event["lease_until"] > now: continue
            event["attempts"] += 1; event["lease_owner"] = owner; event["lease_until"] = now + timedelta(seconds=lease_seconds)
            result.append(OutboxEvent(event["id"], event["event_type"], event["aggregate_type"], event["aggregate_id"], deepcopy(event["payload"]), event["attempts"], owner, event["lease_until"]))
        return result
    def mark_published(self, event_id: UUID, owner: str) -> None:
        for event in self.events:
            if event["id"] == event_id and event["lease_owner"] == owner: event["published"] = True; event["lease_until"] = None; return
        raise ConcurrencyConflict("outbox event is not leased by this owner")
    def mark_failed(self, event_id: UUID, owner: str, error: str, retry_after_seconds: int) -> None:
        for event in self.events:
            if event["id"] == event_id and event["lease_owner"] == owner: event["lease_until"] = datetime.now(timezone.utc) + timedelta(seconds=retry_after_seconds); event["last_error"] = error; return
        raise ConcurrencyConflict("outbox event is not leased by this owner")


@dataclass
class InMemoryUnitOfWork:
    wallets: InMemoryWalletRepository = field(default_factory=InMemoryWalletRepository)
    inventories: InMemoryInventoryRepository = field(default_factory=InMemoryInventoryRepository)
    jobs: InMemoryJobRepository = field(default_factory=InMemoryJobRepository)
    characters: InMemoryCharacterRepository = field(default_factory=InMemoryCharacterRepository)
    vehicles: InMemoryVehicleRepository = field(default_factory=InMemoryVehicleRepository)
    idempotency: InMemoryIdempotencyRepository = field(default_factory=InMemoryIdempotencyRepository)
    audit: InMemoryAuditRepository = field(default_factory=InMemoryAuditRepository)
    outbox: InMemoryOutboxRepository = field(default_factory=InMemoryOutboxRepository)
    committed: bool = False
    rolled_back: bool = False
    _snapshot: dict | None = field(default=None, init=False, repr=False)
    def __enter__(self) -> "InMemoryUnitOfWork":
        self._snapshot = {"wallets": deepcopy(self.wallets), "inventories": deepcopy(self.inventories), "jobs": deepcopy(self.jobs), "characters": deepcopy(self.characters), "vehicles": deepcopy(self.vehicles), "idempotency": deepcopy(self.idempotency), "audit": deepcopy(self.audit), "outbox": deepcopy(self.outbox)}
        return self
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is None: self.commit()
        else: self.rollback()
    def commit(self) -> None:
        self.committed = True; self._snapshot = None
    def rollback(self) -> None:
        if self._snapshot is not None:
            for name in self._snapshot: setattr(self, name, self._snapshot[name])
        self.rolled_back = True; self._snapshot = None

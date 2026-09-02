"""Small use cases; transaction ownership belongs to the command boundary."""

from __future__ import annotations

from datetime import datetime, timedelta
from math import ceil
from uuid import UUID, uuid4

from app.application.errors import IdempotencyConflict, NotFound
from app.application.ports import UnitOfWork
from app.domain.events import DEFAULT_EVENT_REGISTRY
from app.domain.primitives import Character, InventoryStack, Job, LedgerEntry, Vehicle, utc_now

REPAIR_KIT_ID = UUID("30000000-0000-0000-0000-00000000000a")
REPAIR_JOB_TYPE = "vehicle_repair"
REPAIR_DURATION = timedelta(seconds=60)
REPAIR_DURABILITY_PER_KIT = 25


class WalletService:
    def __init__(self, uow: UnitOfWork) -> None: self.uow = uow
    def post_entry(self, wallet_id: UUID, amount: int, reason: str, idempotency_key: str, actor_id: UUID | None = None) -> LedgerEntry:
        existing = self.uow.wallets.get_ledger_entry_by_idempotency_key(idempotency_key)
        if existing is not None:
            if (existing.wallet_id, existing.amount, existing.reason) != (wallet_id, amount, reason): raise IdempotencyConflict("idempotency key already belongs to another operation")
            return existing
        wallet = self.uow.wallets.get(wallet_id)
        if wallet is None: raise NotFound("wallet not found")
        if amount >= 0: wallet.credit(amount)
        else: wallet.debit(-amount)
        entry = LedgerEntry(uuid4(), wallet_id, amount, reason, idempotency_key, utc_now()); self.uow.wallets.save(wallet); self.uow.wallets.add_ledger_entry(entry)
        self._record("wallet.entry_posted", "wallet", wallet_id, {"entry_id": str(entry.id), "amount": amount, "reason": reason, "actor_id": str(actor_id) if actor_id else None}); return entry
    def _record(self, event_type: str, aggregate_type: str, aggregate_id: UUID, payload: dict) -> None:
        event = DEFAULT_EVENT_REGISTRY.create(event_type, aggregate_type, aggregate_id, payload); self.uow.audit.append(event.event_type, event.aggregate_type, aggregate_id, event.to_dict()); self.uow.outbox.enqueue(event.event_type, event.aggregate_type, aggregate_id, event.to_dict())


class InventoryService:
    def __init__(self, uow: UnitOfWork) -> None: self.uow = uow
    def add(self, inventory_id: UUID, item_definition_id: UUID, quantity: int, condition: int = 100) -> InventoryStack:
        if quantity <= 0: raise ValueError("inventory quantity must be positive")
        stack = self.uow.inventories.get_stack(inventory_id, item_definition_id)
        if stack is None: stack = InventoryStack(item_definition_id, quantity, condition)
        else:
            if stack.condition != condition and stack.quantity > 0: raise ValueError("cannot merge inventory stacks with different condition")
            stack.quantity += quantity
        self.uow.inventories.save_stack(inventory_id, stack); self._record("inventory.item_added", inventory_id, {"item_definition_id": str(item_definition_id), "quantity": quantity, "condition": condition}); return stack
    def remove(self, inventory_id: UUID, item_definition_id: UUID, quantity: int) -> InventoryStack | None:
        if quantity <= 0: raise ValueError("inventory quantity must be positive")
        stack = self.uow.inventories.get_stack(inventory_id, item_definition_id)
        if stack is None or stack.quantity < quantity: raise ValueError("inventory quantity is insufficient")
        remaining = stack.quantity - quantity
        if remaining == 0: self.uow.inventories.delete_stack(inventory_id, item_definition_id, stack.version); result = None
        else: stack.quantity = remaining; self.uow.inventories.save_stack(inventory_id, stack); result = stack
        self._record("inventory.item_removed", inventory_id, {"item_definition_id": str(item_definition_id), "quantity": quantity}); return result
    def _record(self, event_type: str, inventory_id: UUID, payload: dict) -> None:
        event = DEFAULT_EVENT_REGISTRY.create(event_type, "inventory", inventory_id, payload); self.uow.audit.append(event.event_type, event.aggregate_type, inventory_id, event.to_dict()); self.uow.outbox.enqueue(event.event_type, event.aggregate_type, inventory_id, event.to_dict())


class JobService:
    def __init__(self, uow: UnitOfWork) -> None: self.uow = uow
    def create(self, owner_id: UUID, job_type: str, started_at: datetime, completes_at: datetime, idempotency_key: str, metadata: dict | None = None) -> Job:
        existing = self.uow.jobs.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            if (existing.owner_id, existing.job_type, existing.started_at, existing.completes_at, existing.metadata) != (owner_id, job_type, started_at, completes_at, metadata or {}): raise IdempotencyConflict("idempotency key already belongs to another job")
            return existing
        job = Job.create(owner_id, job_type, started_at, completes_at, metadata); self.uow.jobs.save(job); self.uow.jobs.bind_idempotency_key(idempotency_key, job.id); self._record("job.created", job.id, {"job_type": job_type, "metadata": job.metadata}); return job
    def start(self, job_id: UUID) -> Job: job = self._get(job_id); job.start(); return self._save(job, "job.started")
    def complete(self, job_id: UUID, now: datetime | None = None) -> Job: job = self._get(job_id); job.complete(now or utc_now()); return self._save(job, "job.completed")
    def cancel(self, job_id: UUID) -> Job: job = self._get(job_id); job.cancel(); return self._save(job, "job.cancelled")
    def _get(self, job_id: UUID) -> Job:
        job = self.uow.jobs.get(job_id)
        if job is None: raise NotFound("job not found")
        return job
    def _save(self, job: Job, event_type: str) -> Job: self.uow.jobs.save(job); self._record(event_type, job.id, {"state": job.state.value}); return job
    def _record(self, event_type: str, aggregate_id: UUID, payload: dict) -> None:
        event = DEFAULT_EVENT_REGISTRY.create(event_type, "job", aggregate_id, payload); self.uow.audit.append(event.event_type, event.aggregate_type, aggregate_id, event.to_dict()); self.uow.outbox.enqueue(event.event_type, event.aggregate_type, aggregate_id, event.to_dict())


class CharacterService:
    def __init__(self, uow: UnitOfWork) -> None: self.uow = uow
    def create(self, player_id: UUID, name: str) -> Character:
        if self.uow.characters.get_by_player_id(player_id) is not None: raise ValueError("player already has a character")
        character = Character.create(player_id, name); self.uow.characters.save(character); self._record("character.created", character.id, {"player_id": str(player_id), "name": character.name}); return character
    def get_for_player(self, player_id: UUID) -> Character:
        character = self.uow.characters.get_by_player_id(player_id)
        if character is None: raise NotFound("character not found")
        return character
    def _record(self, event_type: str, aggregate_id: UUID, payload: dict) -> None:
        event = DEFAULT_EVENT_REGISTRY.create(event_type, "character", aggregate_id, payload); self.uow.audit.append(event.event_type, event.aggregate_type, aggregate_id, event.to_dict()); self.uow.outbox.enqueue(event.event_type, event.aggregate_type, aggregate_id, event.to_dict())


class VehicleService:
    def __init__(self, uow: UnitOfWork) -> None: self.uow = uow
    def create_starter(self, owner_id: UUID, code: str | None = None, chassis_code: str = "light_runner") -> Vehicle:
        if self.uow.vehicles.list_by_owner(owner_id): raise ValueError("starter vehicle can only be created for an owner without vehicles")
        code = code or f"starter-{owner_id.hex[:12]}"
        vehicle = Vehicle.create(owner_id, code, chassis_code, fuel=25); self.uow.vehicles.save(vehicle); self._record("vehicle.created", vehicle.id, {"owner_id": str(owner_id), "code": vehicle.code, "chassis_code": vehicle.chassis_code, "starter": True}); return vehicle
    def get(self, vehicle_id: UUID) -> Vehicle:
        vehicle = self.uow.vehicles.get(vehicle_id)
        if vehicle is None: raise NotFound("vehicle not found")
        return vehicle
    def list_for_owner(self, owner_id: UUID) -> list[Vehicle]: return self.uow.vehicles.list_by_owner(owner_id)
    def repair(self, vehicle_id: UUID, amount: int) -> Vehicle:
        vehicle = self.get(vehicle_id); vehicle.repair(amount); self.uow.vehicles.save(vehicle); return vehicle
    def start_repair(self, vehicle_id: UUID, inventory_id: UUID, amount: int, idempotency_key: str) -> Job:
        existing = self.uow.jobs.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            if existing.job_type != REPAIR_JOB_TYPE or existing.metadata.get("vehicle_id") != str(vehicle_id) or existing.metadata.get("inventory_id") != str(inventory_id): raise IdempotencyConflict("idempotency key already belongs to another repair")
            return existing
        vehicle = self.get(vehicle_id)
        if vehicle.durability >= 100: raise ValueError("vehicle does not need repair")
        amount = min(amount, 100 - vehicle.durability); kits = ceil(amount / REPAIR_DURABILITY_PER_KIT)
        stack = self.uow.inventories.get_stack(inventory_id, REPAIR_KIT_ID)
        if stack is None or stack.quantity < kits: raise ValueError("repair kits are insufficient")
        remaining = stack.quantity - kits
        if remaining == 0: self.uow.inventories.delete_stack(inventory_id, REPAIR_KIT_ID, stack.version)
        else: stack.quantity = remaining; self.uow.inventories.save_stack(inventory_id, stack)
        now = utc_now(); job = JobService(self.uow).create(vehicle.owner_id, REPAIR_JOB_TYPE, now, now + REPAIR_DURATION, idempotency_key, {"vehicle_id": str(vehicle_id), "inventory_id": str(inventory_id), "amount": amount, "kits": kits})
        self._record("vehicle.repair_started", vehicle.id, {"job_id": str(job.id), "amount": amount, "kits": kits}); return job
    def complete_repair(self, job_id: UUID, now: datetime | None = None) -> Job:
        job = self.uow.jobs.get(job_id)
        if job is None: raise NotFound("repair job not found")
        if job.job_type != REPAIR_JOB_TYPE: raise ValueError("job is not a vehicle repair")
        if job.state.value == "completed": return job
        vehicle = self.get(UUID(job.metadata["vehicle_id"])); amount = int(job.metadata["amount"])
        vehicle.repair(amount); self.uow.vehicles.save(vehicle); completed = JobService(self.uow).complete(job_id, now)
        self._record("vehicle.repaired", vehicle.id, {"job_id": str(job_id), "amount": amount, "durability": vehicle.durability}); return completed
    def refuel(self, vehicle_id: UUID, amount: int) -> Vehicle:
        vehicle = self.get(vehicle_id); vehicle.refuel(amount); self.uow.vehicles.save(vehicle); return vehicle
    def _record(self, event_type: str, aggregate_id: UUID, payload: dict) -> None:
        event = DEFAULT_EVENT_REGISTRY.create(event_type, "vehicle", aggregate_id, payload); self.uow.audit.append(event.event_type, event.aggregate_type, aggregate_id, event.to_dict()); self.uow.outbox.enqueue(event.event_type, event.aggregate_type, aggregate_id, event.to_dict())


class PlayerBootstrapService:
    """Atomically provisions the minimum playable identity for an existing player."""
    def __init__(self, uow: UnitOfWork) -> None: self.uow = uow
    def bootstrap(self, player_id: UUID, character_name: str) -> tuple[Character, Vehicle]:
        character = self.uow.characters.get_by_player_id(player_id); vehicles = self.uow.vehicles.list_by_owner(player_id)
        if character is not None or vehicles: raise ValueError("player is already bootstrapped")
        character = CharacterService(self.uow).create(player_id, character_name); vehicle = VehicleService(self.uow).create_starter(player_id); return character, vehicle

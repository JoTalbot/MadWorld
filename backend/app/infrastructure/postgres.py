"""PostgreSQL repositories and transactional Unit of Work."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import Connection, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from app.application.errors import ConcurrencyConflict, IdempotencyConflict
from app.application.ports import IdempotencyRecord, InventoryStackSnapshot, OutboxEvent, PlayerStateSnapshot, UnitOfWork
from app.domain.primitives import Character, InventoryStack, Job, JobState, LedgerEntry, Vehicle, VehicleState, Wallet
from app.infrastructure.errors import map_integrity_error


class PostgresWalletRepository:
    def __init__(self, conn: Connection) -> None: self.conn = conn
    def get(self, wallet_id: UUID) -> Wallet | None:
        row = self.conn.execute(text("SELECT id, version FROM wallets WHERE id = :id FOR UPDATE"), {"id": wallet_id}).mappings().first()
        if row is None: return None
        balance = self.conn.execute(text("SELECT COALESCE(SUM(amount), 0) FROM ledger_entries WHERE wallet_id = :id"), {"id": wallet_id}).scalar_one()
        return Wallet(UUID(str(row["id"])), int(balance), int(row["version"]))
    def save(self, wallet: Wallet) -> None:
        result = self.conn.execute(text("UPDATE wallets SET version = version + 1 WHERE id = :id AND version = :version"), {"id": wallet.id, "version": wallet.version})
        if result.rowcount != 1: raise ConcurrencyConflict("wallet changed since it was read")
        wallet.version += 1
    def add_ledger_entry(self, entry: LedgerEntry) -> None:
        try: self.conn.execute(text("INSERT INTO ledger_entries (id, idempotency_key, wallet_id, amount, reason, created_at) VALUES (:id, :key, :wallet_id, :amount, :reason, :created_at)"), {"id": entry.id, "key": entry.idempotency_key, "wallet_id": entry.wallet_id, "amount": entry.amount, "reason": entry.reason, "created_at": entry.created_at})
        except IntegrityError as exc: raise map_integrity_error(exc) from exc
    def get_ledger_entry_by_idempotency_key(self, key: str) -> LedgerEntry | None:
        row = self.conn.execute(text("SELECT id, wallet_id, amount, reason, idempotency_key, created_at FROM ledger_entries WHERE idempotency_key = :key"), {"key": key}).mappings().first()
        return LedgerEntry(UUID(str(row["id"])), UUID(str(row["wallet_id"])), int(row["amount"]), str(row["reason"]), str(row["idempotency_key"]), row["created_at"]) if row else None


class PostgresInventoryRepository:
    def __init__(self, conn: Connection) -> None: self.conn = conn
    def get_stack(self, inventory_id: UUID, item_definition_id: UUID) -> InventoryStack | None:
        row = self.conn.execute(text("SELECT item_definition_id, quantity, condition, version FROM inventory_items WHERE inventory_id = :inventory_id AND item_definition_id = :item_definition_id FOR UPDATE"), {"inventory_id": inventory_id, "item_definition_id": item_definition_id}).mappings().first()
        return InventoryStack(UUID(str(row["item_definition_id"])), int(row["quantity"]), int(row["condition"]), int(row["version"])) if row else None
    def save_stack(self, inventory_id: UUID, stack: InventoryStack) -> None:
        result = self.conn.execute(text("UPDATE inventory_items SET quantity = :quantity, condition = :condition, version = version + 1 WHERE inventory_id = :inventory_id AND item_definition_id = :item_definition_id AND version = :version"), {"inventory_id": inventory_id, "item_definition_id": stack.item_definition_id, "quantity": stack.quantity, "condition": stack.condition, "version": stack.version})
        if result.rowcount == 1: stack.version += 1; return
        if stack.version != 0: raise ConcurrencyConflict("inventory stack changed since it was read")
        try:
            self.conn.execute(text("INSERT INTO inventory_items (inventory_id, item_definition_id, quantity, condition, version) VALUES (:inventory_id, :item_definition_id, :quantity, :condition, 1)"), {"inventory_id": inventory_id, "item_definition_id": stack.item_definition_id, "quantity": stack.quantity, "condition": stack.condition}); stack.version = 1
        except IntegrityError as exc: raise map_integrity_error(exc) from exc
    def delete_stack(self, inventory_id: UUID, item_definition_id: UUID, expected_version: int) -> None:
        result = self.conn.execute(text("DELETE FROM inventory_items WHERE inventory_id = :inventory_id AND item_definition_id = :item_definition_id AND version = :version"), {"inventory_id": inventory_id, "item_definition_id": item_definition_id, "version": expected_version})
        if result.rowcount != 1: raise ConcurrencyConflict("inventory stack changed since it was read")


class PostgresJobRepository:
    def __init__(self, conn: Connection) -> None: self.conn = conn
    @staticmethod
    def _map(row: Any) -> Job:
        return Job(UUID(str(row["id"])), UUID(str(row["owner_id"])), str(row["job_type"]), row["started_at"], row["completes_at"], JobState(str(row["state"])), int(row["version"]), dict(row["metadata"] or {}))
    def get(self, job_id: UUID) -> Job | None:
        row = self.conn.execute(text("SELECT id, owner_id, job_type, state, started_at, completes_at, version, metadata FROM jobs WHERE id = :id FOR UPDATE"), {"id": job_id}).mappings().first(); return self._map(row) if row else None
    def get_by_idempotency_key(self, key: str) -> Job | None:
        row = self.conn.execute(text("SELECT id, owner_id, job_type, state, started_at, completes_at, version, metadata FROM jobs WHERE idempotency_key = :key"), {"key": key}).mappings().first(); return self._map(row) if row else None
    def save(self, job: Job) -> None:
        if job.version == 0:
            try: self.conn.execute(text("INSERT INTO jobs (id, owner_id, job_type, state, started_at, completes_at, idempotency_key, version, metadata) VALUES (:id, :owner_id, :job_type, :state, :started_at, :completes_at, :key, 1, CAST(:metadata AS JSONB))"), {"id": job.id, "owner_id": job.owner_id, "job_type": job.job_type, "state": job.state.value, "started_at": job.started_at, "completes_at": job.completes_at, "key": f"pending:{job.id}", "metadata": json.dumps(job.metadata)}); job.version = 1; return
            except IntegrityError as exc: raise map_integrity_error(exc) from exc
        result = self.conn.execute(text("UPDATE jobs SET state = :state, metadata = CAST(:metadata AS JSONB), version = version + 1 WHERE id = :id AND version = :version"), {"id": job.id, "state": job.state.value, "metadata": json.dumps(job.metadata), "version": job.version})
        if result.rowcount != 1: raise ConcurrencyConflict("job changed since it was read")
        job.version += 1
    def bind_idempotency_key(self, key: str, job_id: UUID) -> None:
        try:
            result = self.conn.execute(text("UPDATE jobs SET idempotency_key = :key WHERE id = :id AND idempotency_key = :placeholder"), {"key": key, "id": job_id, "placeholder": f"pending:{job_id}"})
            if result.rowcount != 1: raise IdempotencyConflict("job idempotency key cannot be rebound")
        except IntegrityError as exc: raise map_integrity_error(exc) from exc


class PostgresCharacterRepository:
    def __init__(self, conn: Connection) -> None: self.conn = conn
    @staticmethod
    def _map(row: Any) -> Character: return Character(UUID(str(row["id"])), UUID(str(row["player_id"])), str(row["name"]), int(row["level"]), int(row["version"]))
    def get(self, character_id: UUID) -> Character | None:
        row = self.conn.execute(text("SELECT id, player_id, name, level, version FROM characters WHERE id = :id FOR UPDATE"), {"id": character_id}).mappings().first(); return self._map(row) if row else None
    def get_by_player_id(self, player_id: UUID) -> Character | None:
        row = self.conn.execute(text("SELECT id, player_id, name, level, version FROM characters WHERE player_id = :player_id FOR UPDATE"), {"player_id": player_id}).mappings().first(); return self._map(row) if row else None
    def save(self, character: Character) -> None:
        if character.version == 0:
            try: self.conn.execute(text("INSERT INTO characters (id, player_id, name, level, version) VALUES (:id, :player_id, :name, :level, 1)"), {"id": character.id, "player_id": character.player_id, "name": character.name, "level": character.level}); character.version = 1; return
            except IntegrityError as exc: raise map_integrity_error(exc) from exc
        result = self.conn.execute(text("UPDATE characters SET name = :name, level = :level, version = version + 1 WHERE id = :id AND version = :version"), {"id": character.id, "name": character.name, "level": character.level, "version": character.version})
        if result.rowcount != 1: raise ConcurrencyConflict("character changed since it was read")
        character.version += 1


class PostgresVehicleRepository:
    def __init__(self, conn: Connection) -> None: self.conn = conn
    @staticmethod
    def _map(row: Any) -> Vehicle: return Vehicle(UUID(str(row["id"])), UUID(str(row["owner_id"])), str(row["code"]), str(row["chassis_code"]), int(row["durability"]), int(row["fuel"]), VehicleState(str(row["state"])), int(row["version"]))
    def get(self, vehicle_id: UUID) -> Vehicle | None:
        row = self.conn.execute(text("SELECT id, owner_id, code, chassis_code, durability, fuel, state, version FROM vehicles WHERE id = :id FOR UPDATE"), {"id": vehicle_id}).mappings().first(); return self._map(row) if row else None
    def list_by_owner(self, owner_id: UUID) -> list[Vehicle]:
        rows = self.conn.execute(text("SELECT id, owner_id, code, chassis_code, durability, fuel, state, version FROM vehicles WHERE owner_id = :owner_id ORDER BY created_at, id"), {"owner_id": owner_id}).mappings().all(); return [self._map(row) for row in rows]
    def save(self, vehicle: Vehicle) -> None:
        if vehicle.version == 0:
            try: self.conn.execute(text("INSERT INTO vehicles (id, owner_id, code, chassis_code, durability, fuel, state, version) VALUES (:id, :owner_id, :code, :chassis_code, :durability, :fuel, :state, 1)"), {"id": vehicle.id, "owner_id": vehicle.owner_id, "code": vehicle.code, "chassis_code": vehicle.chassis_code, "durability": vehicle.durability, "fuel": vehicle.fuel, "state": vehicle.state.value}); vehicle.version = 1; return
            except IntegrityError as exc: raise map_integrity_error(exc) from exc
        result = self.conn.execute(text("UPDATE vehicles SET durability = :durability, fuel = :fuel, state = :state, version = version + 1 WHERE id = :id AND version = :version"), {"id": vehicle.id, "durability": vehicle.durability, "fuel": vehicle.fuel, "state": vehicle.state.value, "version": vehicle.version})
        if result.rowcount != 1: raise ConcurrencyConflict("vehicle changed since it was read")
        vehicle.version += 1


class PostgresIdempotencyRepository:
    def __init__(self, conn: Connection) -> None: self.conn = conn
    @staticmethod
    def _map(row: Any) -> IdempotencyRecord: return IdempotencyRecord(str(row["command_name"]), str(row["idempotency_key"]), str(row["request_hash"]), int(row["response_status"]), dict(row["response_payload"]), UUID(str(row["actor_id"])) if row["actor_id"] else None, row["created_at"])
    def get(self, command_name: str, idempotency_key: str) -> IdempotencyRecord | None:
        row = self.conn.execute(text("SELECT command_name, idempotency_key, request_hash, response_status, response_payload, actor_id, created_at FROM idempotency_records WHERE command_name = :command_name AND idempotency_key = :key"), {"command_name": command_name, "key": idempotency_key}).mappings().first(); return self._map(row) if row else None
    def put(self, record: IdempotencyRecord) -> None:
        try: self.conn.execute(text("INSERT INTO idempotency_records (actor_id, command_name, idempotency_key, request_hash, response_status, response_payload, created_at) VALUES (:actor_id, :command_name, :key, :request_hash, :status, CAST(:payload AS JSONB), :created_at)"), {"actor_id": record.actor_id, "command_name": record.command_name, "key": record.idempotency_key, "request_hash": record.request_hash, "status": record.response_status, "payload": json.dumps(record.response_payload), "created_at": record.created_at})
        except IntegrityError as exc: raise map_integrity_error(exc) from exc


class PostgresAuditRepository:
    def __init__(self, conn: Connection) -> None: self.conn = conn
    def append(self, event_type: str, aggregate_type: str, aggregate_id: UUID, payload: dict) -> None: self.conn.execute(text("INSERT INTO audit_events (event_type, aggregate_type, aggregate_id, payload) VALUES (:event_type, :aggregate_type, :aggregate_id, CAST(:payload AS JSONB))"), {"event_type": event_type, "aggregate_type": aggregate_type, "aggregate_id": aggregate_id, "payload": json.dumps(payload)})


class PostgresOutboxRepository:
    def __init__(self, conn: Connection) -> None: self.conn = conn
    def enqueue(self, event_type: str, aggregate_type: str, aggregate_id: UUID, payload: dict) -> None: self.conn.execute(text("INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload) VALUES (:aggregate_type, :aggregate_id, :event_type, CAST(:payload AS JSONB))"), {"event_type": event_type, "aggregate_type": aggregate_type, "aggregate_id": aggregate_id, "payload": json.dumps(payload)})
    def claim(self, owner: str, limit: int = 50, lease_seconds: int = 60, max_attempts: int = 10) -> list[OutboxEvent]:
        now = datetime.now(timezone.utc); until = now + timedelta(seconds=lease_seconds)
        rows = self.conn.execute(text("""WITH candidates AS (SELECT id FROM outbox_events WHERE published_at IS NULL AND dead_lettered = FALSE AND attempts < :max_attempts AND (lease_until IS NULL OR lease_until <= :now) ORDER BY created_at LIMIT :limit FOR UPDATE SKIP LOCKED) UPDATE outbox_events o SET attempts = o.attempts + 1, lease_owner = :owner, lease_until = :until FROM candidates c WHERE o.id = c.id RETURNING o.id, o.event_type, o.aggregate_type, o.aggregate_id, o.payload, o.attempts, o.lease_owner, o.lease_until"""), {"max_attempts": max_attempts, "now": now, "limit": limit, "owner": owner, "until": until}).mappings().all()
        return [OutboxEvent(UUID(str(r["id"])), str(r["event_type"]), str(r["aggregate_type"]), UUID(str(r["aggregate_id"])), dict(r["payload"]), int(r["attempts"]), r["lease_owner"], r["lease_until"]) for r in rows]
    def mark_published(self, event_id: UUID, owner: str) -> None:
        result = self.conn.execute(text("UPDATE outbox_events SET published_at = NOW(), lease_owner = NULL, lease_until = NULL WHERE id = :id AND lease_owner = :owner AND published_at IS NULL"), {"id": event_id, "owner": owner})
        if result.rowcount != 1: raise ConcurrencyConflict("outbox event is not leased by this owner")
    def mark_failed(self, event_id: UUID, owner: str, error: str, retry_after_seconds: int) -> None:
        result = self.conn.execute(text("UPDATE outbox_events SET last_error = :error, lease_until = NOW() + (:delay * INTERVAL '1 second'), lease_owner = NULL, dead_lettered = CASE WHEN attempts >= 10 THEN TRUE ELSE FALSE END WHERE id = :id AND lease_owner = :owner"), {"id": event_id, "owner": owner, "error": error, "delay": retry_after_seconds})
        if result.rowcount != 1: raise ConcurrencyConflict("outbox event is not leased by this owner")


def _json(value: object) -> str: return json.dumps(value)


class PostgresPlayerStateRepository:
    """Deterministic read model of one account's wallet, inventory and active jobs."""
    def __init__(self, conn: Connection) -> None: self.conn = conn
    def snapshot(self, player_id: UUID) -> PlayerStateSnapshot:
        wallet_row = self.conn.execute(text("""
            SELECT id, version, COALESCE((SELECT SUM(amount) FROM ledger_entries le WHERE le.wallet_id = w.id), 0) AS balance
            FROM wallets w WHERE owner_id = :player_id"""), {"player_id": player_id}).mappings().first()
        wallet = Wallet(UUID(str(wallet_row["id"])), int(wallet_row["balance"]), int(wallet_row["version"])) if wallet_row else None
        inventory_rows = self.conn.execute(text("""
            SELECT i.id AS inventory_id, ii.item_definition_id, ii.quantity, ii.condition, ii.version
            FROM inventories i JOIN inventory_items ii ON ii.inventory_id = i.id
            WHERE i.owner_id = :player_id ORDER BY i.id, ii.item_definition_id"""), {"player_id": player_id}).mappings().all()
        inventory = [InventoryStackSnapshot(UUID(str(r["inventory_id"])), UUID(str(r["item_definition_id"])), int(r["quantity"]), int(r["condition"]), int(r["version"])) for r in inventory_rows]
        job_rows = self.conn.execute(text("""
            SELECT id, owner_id, job_type, started_at, completes_at, state, version, metadata
            FROM jobs WHERE owner_id = :player_id AND state IN ('queued', 'running') ORDER BY completes_at, id"""), {"player_id": player_id}).mappings().all()
        return PlayerStateSnapshot(wallet, inventory, [PostgresJobRepository._map(r) for r in job_rows])


class PostgresUnitOfWork:
    def __init__(self, engine: Engine) -> None: self.engine = engine
    def __enter__(self) -> "PostgresUnitOfWork":
        self.conn = self.engine.connect(); self.tx = self.conn.begin()
        self.wallets = PostgresWalletRepository(self.conn); self.inventories = PostgresInventoryRepository(self.conn); self.jobs = PostgresJobRepository(self.conn); self.characters = PostgresCharacterRepository(self.conn); self.vehicles = PostgresVehicleRepository(self.conn); self.player_state = PostgresPlayerStateRepository(self.conn); self.idempotency = PostgresIdempotencyRepository(self.conn); self.audit = PostgresAuditRepository(self.conn); self.outbox = PostgresOutboxRepository(self.conn); return self
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is None: self.commit()
        else: self.rollback()
        self.conn.close()
    def commit(self) -> None: self.tx.commit()
    def rollback(self) -> None: self.tx.rollback()

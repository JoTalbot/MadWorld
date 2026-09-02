"""PostgreSQL repositories and transactional Unit of Work."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy import Connection, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from app.application.errors import ConcurrencyConflict, IdempotencyConflict
from app.application.ports import UnitOfWork
from app.domain.primitives import InventoryStack, Job, JobState, LedgerEntry, Wallet
from app.infrastructure.errors import map_integrity_error


class PostgresWalletRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def get(self, wallet_id: UUID) -> Wallet | None:
        row = self.conn.execute(text("SELECT id, version FROM wallets WHERE id = :id FOR UPDATE"), {"id": wallet_id}).mappings().first()
        if row is None:
            return None
        balance = self.conn.execute(text("SELECT COALESCE(SUM(amount), 0) FROM ledger_entries WHERE wallet_id = :id"), {"id": wallet_id}).scalar_one()
        return Wallet(UUID(str(row["id"])), int(balance), int(row["version"]))

    def save(self, wallet: Wallet) -> None:
        result = self.conn.execute(text("UPDATE wallets SET version = version + 1 WHERE id = :id AND version = :version"), {"id": wallet.id, "version": wallet.version})
        if result.rowcount != 1:
            raise ConcurrencyConflict("wallet changed since it was read")
        wallet.version += 1

    def add_ledger_entry(self, entry: LedgerEntry) -> None:
        try:
            self.conn.execute(text("""
                INSERT INTO ledger_entries (id, idempotency_key, wallet_id, amount, reason, created_at)
                VALUES (:id, :key, :wallet_id, :amount, :reason, :created_at)
            """), {"id": entry.id, "key": entry.idempotency_key, "wallet_id": entry.wallet_id, "amount": entry.amount, "reason": entry.reason, "created_at": entry.created_at})
        except IntegrityError as exc:
            raise map_integrity_error(exc) from exc

    def get_ledger_entry_by_idempotency_key(self, key: str) -> LedgerEntry | None:
        row = self.conn.execute(text("SELECT id, wallet_id, amount, reason, idempotency_key, created_at FROM ledger_entries WHERE idempotency_key = :key"), {"key": key}).mappings().first()
        if row is None:
            return None
        return LedgerEntry(UUID(str(row["id"])), UUID(str(row["wallet_id"])), int(row["amount"]), str(row["reason"]), str(row["idempotency_key"]), row["created_at"])


class PostgresInventoryRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def get_stack(self, inventory_id: UUID, item_definition_id: UUID) -> InventoryStack | None:
        row = self.conn.execute(text("""
            SELECT item_definition_id, quantity, condition, version
            FROM inventory_items
            WHERE inventory_id = :inventory_id AND item_definition_id = :item_definition_id
            FOR UPDATE
        """), {"inventory_id": inventory_id, "item_definition_id": item_definition_id}).mappings().first()
        if row is None:
            return None
        return InventoryStack(UUID(str(row["item_definition_id"])), int(row["quantity"]), int(row["condition"]), int(row["version"]))

    def save_stack(self, inventory_id: UUID, stack: InventoryStack) -> None:
        result = self.conn.execute(text("""
            UPDATE inventory_items
               SET quantity = :quantity, condition = :condition, version = version + 1
             WHERE inventory_id = :inventory_id AND item_definition_id = :item_definition_id AND version = :version
        """), {"inventory_id": inventory_id, "item_definition_id": stack.item_definition_id, "quantity": stack.quantity, "condition": stack.condition, "version": stack.version})
        if result.rowcount == 1:
            stack.version += 1
            return
        if stack.version != 0:
            raise ConcurrencyConflict("inventory stack changed since it was read")
        try:
            self.conn.execute(text("""
                INSERT INTO inventory_items (inventory_id, item_definition_id, quantity, condition, version)
                VALUES (:inventory_id, :item_definition_id, :quantity, :condition, 1)
            """), {"inventory_id": inventory_id, "item_definition_id": stack.item_definition_id, "quantity": stack.quantity, "condition": stack.condition})
            stack.version = 1
        except IntegrityError as exc:
            raise map_integrity_error(exc) from exc

    def delete_stack(self, inventory_id: UUID, item_definition_id: UUID, expected_version: int) -> None:
        result = self.conn.execute(text("""
            DELETE FROM inventory_items
             WHERE inventory_id = :inventory_id AND item_definition_id = :item_definition_id AND version = :version
        """), {"inventory_id": inventory_id, "item_definition_id": item_definition_id, "version": expected_version})
        if result.rowcount != 1:
            raise ConcurrencyConflict("inventory stack changed since it was read")


class PostgresJobRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    @staticmethod
    def _map(row: Any) -> Job:
        return Job(UUID(str(row["id"])), UUID(str(row["owner_id"])), str(row["job_type"]), row["started_at"], row["completes_at"], JobState(str(row["state"])), int(row["version"]))

    def get(self, job_id: UUID) -> Job | None:
        row = self.conn.execute(text("SELECT id, owner_id, job_type, state, started_at, completes_at, version FROM jobs WHERE id = :id FOR UPDATE"), {"id": job_id}).mappings().first()
        return self._map(row) if row else None

    def get_by_idempotency_key(self, key: str) -> Job | None:
        row = self.conn.execute(text("SELECT id, owner_id, job_type, state, started_at, completes_at, version FROM jobs WHERE idempotency_key = :key"), {"key": key}).mappings().first()
        return self._map(row) if row else None

    def save(self, job: Job) -> None:
        if job.version == 0:
            try:
                self.conn.execute(text("""
                    INSERT INTO jobs (id, owner_id, job_type, state, started_at, completes_at, idempotency_key, version)
                    VALUES (:id, :owner_id, :job_type, :state, :started_at, :completes_at, :key, 1)
                """), {"id": job.id, "owner_id": job.owner_id, "job_type": job.job_type, "state": job.state.value, "started_at": job.started_at, "completes_at": job.completes_at, "key": f"pending:{job.id}"})
                job.version = 1
                return
            except IntegrityError as exc:
                raise map_integrity_error(exc) from exc
        result = self.conn.execute(text("UPDATE jobs SET state = :state, version = version + 1 WHERE id = :id AND version = :version"), {"id": job.id, "state": job.state.value, "version": job.version})
        if result.rowcount != 1:
            raise ConcurrencyConflict("job changed since it was read")
        job.version += 1

    def bind_idempotency_key(self, key: str, job_id: UUID) -> None:
        try:
            result = self.conn.execute(text("UPDATE jobs SET idempotency_key = :key WHERE id = :id AND idempotency_key = :placeholder"), {"key": key, "id": job_id, "placeholder": f"pending:{job_id}"})
            if result.rowcount != 1:
                raise IdempotencyConflict("job idempotency key cannot be rebound")
        except IntegrityError as exc:
            raise map_integrity_error(exc) from exc


class PostgresAuditRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def append(self, event_type: str, aggregate_type: str, aggregate_id: UUID, payload: dict) -> None:
        self.conn.execute(text("""
            INSERT INTO audit_events (event_type, aggregate_type, aggregate_id, payload)
            VALUES (:event_type, :aggregate_type, :aggregate_id, CAST(:payload AS JSONB))
        """), {"event_type": event_type, "aggregate_type": aggregate_type, "aggregate_id": aggregate_id, "payload": _json(payload)})


class PostgresOutboxRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def enqueue(self, event_type: str, aggregate_type: str, aggregate_id: UUID, payload: dict) -> None:
        self.conn.execute(text("""
            INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload)
            VALUES (:aggregate_type, :aggregate_id, :event_type, CAST(:payload AS JSONB))
        """), {"event_type": event_type, "aggregate_type": aggregate_type, "aggregate_id": aggregate_id, "payload": _json(payload)})


def _json(payload: dict) -> str:
    return json.dumps(payload, separators=(",", ":"), default=str)


class PostgresUnitOfWork(UnitOfWork):
    """One connection and one transaction owned by the command/request boundary."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.conn: Connection | None = None
        self.transaction = None

    def __enter__(self) -> "PostgresUnitOfWork":
        self.conn = self.engine.connect()
        self.transaction = self.conn.begin()
        self.wallets = PostgresWalletRepository(self.conn)
        self.inventories = PostgresInventoryRepository(self.conn)
        self.jobs = PostgresJobRepository(self.conn)
        self.audit = PostgresAuditRepository(self.conn)
        self.outbox = PostgresOutboxRepository(self.conn)
        return self

    def commit(self) -> None:
        if self.conn is None:
            raise RuntimeError("unit of work is not active")
        if self.transaction is not None and self.transaction.is_active:
            self.transaction.commit()
        self.transaction = self.conn.begin()

    def rollback(self) -> None:
        if self.conn is None:
            raise RuntimeError("unit of work is not active")
        if self.transaction is not None and self.transaction.is_active:
            self.transaction.rollback()
        self.transaction = self.conn.begin()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        try:
            if exc_type is not None:
                self.rollback()
            elif self.transaction is not None and self.transaction.is_active:
                self.commit()
        finally:
            if self.conn is not None:
                self.conn.close()
                self.conn = None
                self.transaction = None

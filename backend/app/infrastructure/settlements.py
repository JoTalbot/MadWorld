"""PostgreSQL settlement repository."""
from __future__ import annotations

import json
from uuid import UUID
from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError
from app.application.errors import ConcurrencyConflict, IdempotencyConflict
from app.domain.settlements import Settlement

class PostgresSettlementRepository:
    def __init__(self, conn: Connection) -> None: self.conn = conn
    @staticmethod
    def _map(row) -> Settlement:
        return Settlement(UUID(str(row["id"])), UUID(str(row["owner_id"])), str(row["region"]), int(row["level"]), dict(row["modules"] or {}), int(row["version"]))
    def get_by_owner(self, owner_id: UUID) -> Settlement | None:
        row = self.conn.execute(text("SELECT id, owner_id, region, level, modules, version FROM settlements WHERE owner_id = :owner_id FOR UPDATE"), {"owner_id": owner_id}).mappings().first()
        return self._map(row) if row else None
    def get(self, settlement_id: UUID) -> Settlement | None:
        row = self.conn.execute(text("SELECT id, owner_id, region, level, modules, version FROM settlements WHERE id = :id FOR UPDATE"), {"id": settlement_id}).mappings().first()
        return self._map(row) if row else None
    def save(self, settlement: Settlement) -> None:
        payload = json.dumps(settlement.modules)
        if settlement.version == 0:
            try:
                self.conn.execute(text("INSERT INTO settlements (id, owner_id, region, level, modules, version) VALUES (:id, :owner_id, :region, :level, CAST(:modules AS JSONB), 1)"), {"id": settlement.id, "owner_id": settlement.owner_id, "region": settlement.region, "level": settlement.level, "modules": payload})
                settlement.version = 1; return
            except IntegrityError as exc:
                raise IdempotencyConflict("settlement already exists for this owner") from exc
        result = self.conn.execute(text("UPDATE settlements SET region = :region, level = :level, modules = CAST(:modules AS JSONB), version = version + 1 WHERE id = :id AND version = :version"), {"id": settlement.id, "region": settlement.region, "level": settlement.level, "modules": payload, "version": settlement.version})
        if result.rowcount != 1: raise ConcurrencyConflict("settlement changed since it was read")
        settlement.version += 1

"""PostgreSQL settlement state repository."""
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
        # The player id is the stable aggregate id for a personal settlement.
        return Settlement(UUID(str(row["player_id"])), UUID(str(row["player_id"])), str(row["region"]), int(row["level"]), dict(row["modules"] or {}), int(row["version"]))

    def get_by_owner(self, owner_id: UUID) -> Settlement | None:
        row = self.conn.execute(text("SELECT player_id, region, level, modules, version FROM player_settlement_state WHERE player_id = :player_id FOR UPDATE"), {"player_id": owner_id}).mappings().first()
        return self._map(row) if row else None

    def get(self, settlement_id: UUID) -> Settlement | None:
        return self.get_by_owner(settlement_id)

    def save(self, settlement: Settlement) -> None:
        payload = json.dumps(settlement.modules)
        if settlement.version == 0:
            try:
                self.conn.execute(text("INSERT INTO player_settlement_state (player_id, settlement_id, region, level, modules, version) SELECT :player_id, id, :region, :level, CAST(:modules AS JSONB), 1 FROM settlements WHERE id = :settlement_id"), {"player_id": settlement.owner_id, "settlement_id": "20000000-0000-0000-0000-000000000001", "region": settlement.region, "level": settlement.level, "modules": payload})
                if self.conn.execute(text("SELECT 1 FROM player_settlement_state WHERE player_id = :player_id"), {"player_id": settlement.owner_id}).first() is None:
                    raise ValueError("default world settlement is not provisioned")
                settlement.version = 1
                return
            except IntegrityError as exc:
                raise IdempotencyConflict("settlement already exists for this player") from exc
        result = self.conn.execute(text("UPDATE player_settlement_state SET region = :region, level = :level, modules = CAST(:modules AS JSONB), version = version + 1, updated_at = NOW() WHERE player_id = :player_id AND version = :version"), {"player_id": settlement.owner_id, "region": settlement.region, "level": settlement.level, "modules": payload, "version": settlement.version})
        if result.rowcount != 1: raise ConcurrencyConflict("settlement changed since it was read")
        settlement.version += 1

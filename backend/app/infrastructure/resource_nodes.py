"""Persistence adapters for regional resource nodes."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Connection, text

from app.application.errors import ConcurrencyConflict
from app.application.gathering import ResourceNode


class PostgresResourceNodeRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def get_for_update(self, node_id: UUID) -> ResourceNode | None:
        row = self.conn.execute(text("""
            SELECT id, region_id, resource_item_definition_id, quantity,
                   gather_amount, cooldown_seconds, version, last_gathered_at
            FROM resource_nodes WHERE id = :id FOR UPDATE
        """), {"id": node_id}).mappings().first()
        if row is None:
            return None
        return ResourceNode(UUID(str(row["id"])), UUID(str(row["region_id"])),
                            UUID(str(row["resource_item_definition_id"])), int(row["quantity"]),
                            int(row["gather_amount"]), int(row["cooldown_seconds"]),
                            int(row["version"]), row["last_gathered_at"])

    def save(self, node: ResourceNode) -> None:
        result = self.conn.execute(text("""
            UPDATE resource_nodes
            SET quantity = :quantity, last_gathered_at = :last_gathered_at,
                version = version + 1
            WHERE id = :id AND version = :version
        """), {"id": node.id, "quantity": node.quantity,
               "last_gathered_at": node.last_gathered_at, "version": node.version})
        if result.rowcount != 1:
            raise ConcurrencyConflict("resource node changed since it was read")
        node = ResourceNode(node.id, node.region_id, node.resource_item_definition_id,
                            node.quantity, node.gather_amount, node.cooldown_seconds,
                            node.version + 1, node.last_gathered_at)

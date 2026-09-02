"""Authoritative aggregate read model for Android reconnect/bootstrap."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import text

from app.api.dependencies import get_engine
from app.api.schemas import (
    InventorySnapshot,
    JobResponse,
    PlayerStateResponse,
    WalletSnapshot,
)


def load_player_state(player_id: UUID, character, vehicles) -> PlayerStateResponse:
    """Build one deterministic account gameplay snapshot from PostgreSQL."""
    with get_engine().connect() as conn:
        wallet = conn.execute(
            text("""
                SELECT id, version,
                       COALESCE((SELECT SUM(amount) FROM ledger_entries le WHERE le.wallet_id = w.id), 0) AS balance
                FROM wallets w
                WHERE owner_id = :player_id
            """),
            {"player_id": player_id},
        ).mappings().first()
        inventories = conn.execute(
            text("""
                SELECT i.id AS inventory_id, ii.item_definition_id, ii.quantity, ii.condition, ii.version
                FROM inventories i
                JOIN inventory_items ii ON ii.inventory_id = i.id
                WHERE i.owner_id = :player_id
                ORDER BY i.id, ii.item_definition_id
            """),
            {"player_id": player_id},
        ).mappings().all()
        jobs = conn.execute(
            text("""
                SELECT id, owner_id, job_type, started_at, completes_at, state, version
                FROM jobs
                WHERE owner_id = :player_id AND state IN ('queued', 'running')
                ORDER BY completes_at, id
            """),
            {"player_id": player_id},
        ).mappings().all()

    return PlayerStateResponse(
        character=character,
        vehicles=vehicles,
        wallet=(WalletSnapshot(id=UUID(str(wallet["id"])), balance=int(wallet["balance"]), version=int(wallet["version"])) if wallet else None),
        inventory=[
            InventorySnapshot(
                inventory_id=UUID(str(row["inventory_id"])),
                item_definition_id=UUID(str(row["item_definition_id"])),
                quantity=int(row["quantity"]),
                condition=int(row["condition"]),
                version=int(row["version"]),
            )
            for row in inventories
        ],
        active_jobs=[
            JobResponse(
                id=UUID(str(row["id"])),
                owner_id=UUID(str(row["owner_id"])),
                job_type=str(row["job_type"]),
                started_at=row["started_at"],
                completes_at=row["completes_at"],
                state=str(row["state"]),
                version=int(row["version"]),
            )
            for row in jobs
        ],
    )

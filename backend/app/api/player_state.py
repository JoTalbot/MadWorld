"""Authoritative aggregate read model for Android reconnect/bootstrap.

The snapshot is assembled from the ``PlayerStateRepository`` port so the API
layer does not depend on a concrete storage engine. Postgres and in-memory
implementations live in ``app.infrastructure``.
"""

from __future__ import annotations

from uuid import UUID

from app.api.schemas import (
    InventorySnapshot,
    JobResponse,
    PlayerStateResponse,
    WalletSnapshot,
)
from app.application.ports import UnitOfWork


def load_player_state(uow: UnitOfWork, player_id: UUID, character, vehicles) -> PlayerStateResponse:
    """Build one deterministic account gameplay snapshot inside the current unit of work."""
    snapshot = uow.player_state.snapshot(player_id)
    return PlayerStateResponse(
        character=character,
        vehicles=vehicles,
        wallet=(WalletSnapshot(id=snapshot.wallet.id, balance=snapshot.wallet.balance, version=snapshot.wallet.version) if snapshot.wallet else None),
        inventory=[
            InventorySnapshot(
                inventory_id=row.inventory_id,
                item_definition_id=row.item_definition_id,
                quantity=row.quantity,
                condition=row.condition,
                version=row.version,
            )
            for row in snapshot.inventory
        ],
        active_jobs=[
            JobResponse(
                id=job.id,
                owner_id=job.owner_id,
                job_type=job.job_type,
                started_at=job.started_at,
                completes_at=job.completes_at,
                state=job.state.value,
                version=job.version,
            )
            for job in snapshot.active_jobs
        ],
    )

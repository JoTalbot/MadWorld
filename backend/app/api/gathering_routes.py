"""Regional resource gathering endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_uow
from app.api.idempotency import replay_or_none, require_key, store_response
from app.api.schemas import ResourceGatherRequest, ResourceGatherResponse
from app.application.gathering import GatheringService
from app.application.ports import UnitOfWork

router = APIRouter(prefix="/api/v1/resources", tags=["resources"])


def _inventory_owner(uow: UnitOfWork, inventory_id: UUID) -> UUID | None:
    owners = getattr(uow.inventories, "owners", None)
    if owners is not None:
        return owners.get(inventory_id)
    conn = getattr(uow.inventories, "conn", None)
    if conn is None:
        return None
    row = conn.execute(text("SELECT owner_id FROM inventories WHERE id = :id"), {"id": inventory_id}).mappings().first()
    return UUID(str(row["owner_id"])) if row else None


@router.post("/gather", response_model=ResourceGatherResponse, status_code=status.HTTP_200_OK)
def gather_resource(
    payload: ResourceGatherRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    uow: UnitOfWork = Depends(get_uow),
    authenticated_player: UUID = Depends(get_authenticated_player),
) -> ResourceGatherResponse:
    owner = _inventory_owner(uow, payload.inventory_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="inventory not found")
    if owner != authenticated_player:
        raise HTTPException(status_code=403, detail="session does not own inventory")

    key = require_key(idempotency_key)
    request_data = payload.model_dump(mode="json")
    replay = replay_or_none(uow, "resource.gather", key, request_data)
    if replay is not None:
        return ResourceGatherResponse.model_validate(replay)

    node, amount = GatheringService(uow).gather(authenticated_player, payload.inventory_id, payload.node_id)
    response = ResourceGatherResponse(
        node_id=node.id,
        region_id=node.region_id,
        item_definition_id=node.resource_item_definition_id,
        gathered_quantity=amount,
        remaining_quantity=node.quantity,
        next_available_at=node.last_gathered_at + __import__("datetime").timedelta(seconds=node.cooldown_seconds),
        version=node.version,
    )
    store_response(uow, "resource.gather", key, request_data, response.model_dump(mode="json"), status.HTTP_200_OK, authenticated_player)
    return response

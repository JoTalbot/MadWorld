"""Authoritative corporate hangar and asset custody operations for Phase 4."""
from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_uow
from app.api.phase4_routes import _require_permission
from app.application.ports import UnitOfWork

router = APIRouter(prefix="/api/v1/social", tags=["social-assets"])

class AssetRegister(BaseModel):
    corporation_id: UUID
    asset_type: str = Field(min_length=1, max_length=64)
    asset_id: UUID
    hangar_id: UUID | None = None
    assigned_to: UUID | None = None

class AssetMove(BaseModel):
    corporation_id: UUID
    asset_id: UUID
    target_hangar_id: UUID | None = None
    assigned_to: UUID | None = None


def _hangar_capacity(uow: UnitOfWork, hangar_id: UUID, corporation_id: UUID) -> tuple[int, int]:
    row = uow.conn.execute(text("SELECT capacity,(SELECT COUNT(*) FROM corporation_assets WHERE hangar_id=h.id) FROM corporation_hangars h WHERE h.id=:h AND h.corporation_id=:c FOR UPDATE"), {"h": hangar_id, "c": corporation_id}).first()
    if not row:
        raise HTTPException(404, "hangar not found")
    return int(row[0]), int(row[1])


def _check_member(uow: UnitOfWork, corporation_id: UUID, player_id: UUID) -> None:
    if uow.conn.execute(text("SELECT 1 FROM corporation_members WHERE corporation_id=:c AND player_id=:p"), {"c": corporation_id, "p": player_id}).first() is None:
        raise HTTPException(404, "assigned player is not a corporation member")


@router.post("/assets", status_code=201)
def register_asset(payload: AssetRegister, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _require_permission(uow, payload.corporation_id, player_id, "MANAGE_ASSETS")
    if payload.assigned_to:
        _check_member(uow, payload.corporation_id, payload.assigned_to)
    if payload.hangar_id:
        capacity, used = _hangar_capacity(uow, payload.hangar_id, payload.corporation_id)
        if used >= capacity:
            raise HTTPException(409, "hangar capacity reached")
    asset_id = uuid4()
    try:
        uow.conn.execute(text("INSERT INTO corporation_assets (id,corporation_id,asset_type,asset_id,hangar_id,assigned_to,version) VALUES (:id,:c,:t,:a,:h,:p,0)"), {"id": asset_id, "c": payload.corporation_id, "t": payload.asset_type, "a": payload.asset_id, "h": payload.hangar_id, "p": payload.assigned_to})
    except Exception as exc:
        raise HTTPException(409, "asset is already in corporate custody") from exc
    uow.audit.append("corporation.asset_registered", "corporation", payload.corporation_id, {"actor_id": str(player_id), "asset_id": str(payload.asset_id), "asset_type": payload.asset_type})
    return {"ok": True, "id": str(asset_id), "asset_id": str(payload.asset_id), "hangar_id": str(payload.hangar_id) if payload.hangar_id else None}


@router.post("/assets/move")
def move_asset(payload: AssetMove, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _require_permission(uow, payload.corporation_id, player_id, "MANAGE_ASSETS")
    row = uow.conn.execute(text("SELECT id,hangar_id,assigned_to,version FROM corporation_assets WHERE corporation_id=:c AND asset_id=:a FOR UPDATE"), {"c": payload.corporation_id, "a": payload.asset_id}).mappings().first()
    if not row:
        raise HTTPException(404, "corporate asset not found")
    if payload.assigned_to:
        _check_member(uow, payload.corporation_id, payload.assigned_to)
    if payload.target_hangar_id and payload.target_hangar_id != row["hangar_id"]:
        capacity, used = _hangar_capacity(uow, payload.target_hangar_id, payload.corporation_id)
        if used >= capacity:
            raise HTTPException(409, "hangar capacity reached")
    uow.conn.execute(text("UPDATE corporation_assets SET hangar_id=:h,assigned_to=:p,version=version+1 WHERE id=:id AND version=:v"), {"h": payload.target_hangar_id, "p": payload.assigned_to, "id": row["id"], "v": row["version"]})
    uow.audit.append("corporation.asset_moved", "corporation", payload.corporation_id, {"actor_id": str(player_id), "asset_id": str(payload.asset_id), "hangar_id": str(payload.target_hangar_id) if payload.target_hangar_id else None})
    return {"ok": True, "asset_id": str(payload.asset_id), "hangar_id": str(payload.target_hangar_id) if payload.target_hangar_id else None, "assigned_to": str(payload.assigned_to) if payload.assigned_to else None}

"""Authoritative manufacturer provenance binding for corporate assets."""
from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from app.api.dependencies import get_authenticated_player, get_uow
from app.api.phase4_routes import _require_permission
from app.application.ports import UnitOfWork

router = APIRouter(prefix="/api/v1/social", tags=["social-assets"])

class AssetProvenanceCreate(BaseModel):
    corporation_id: UUID
    asset_id: UUID
    manufacturer_id: UUID
    production_batch: str = Field(min_length=1, max_length=128)
    production_version: int = Field(default=1, gt=0)
    quality_rating: int | None = Field(default=None, ge=0, le=10000)

@router.post("/assets/provenance", status_code=201)
def bind_asset_provenance(payload: AssetProvenanceCreate, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _require_permission(uow, payload.corporation_id, player_id, "MANAGE_ASSETS")
    asset = uow.conn.execute(text("SELECT id FROM corporation_assets WHERE corporation_id=:c AND asset_id=:a FOR UPDATE"), {"c": payload.corporation_id, "a": payload.asset_id}).first()
    if not asset:
        raise HTTPException(404, "corporate asset not found")
    manufacturer = uow.conn.execute(text("SELECT quality_rating FROM manufacturers WHERE id=:m AND corporation_id=:c FOR UPDATE"), {"m": payload.manufacturer_id, "c": payload.corporation_id}).first()
    if not manufacturer:
        raise HTTPException(404, "manufacturer not found for corporation")
    quality = int(payload.quality_rating if payload.quality_rating is not None else manufacturer[0])
    try:
        uow.conn.execute(text("INSERT INTO asset_provenance (asset_id,manufacturer_id,quality_rating,production_batch,production_version) VALUES (:a,:m,:q,:b,:v)"), {"a": payload.asset_id, "m": payload.manufacturer_id, "q": quality, "b": payload.production_batch.strip(), "v": payload.production_version})
    except Exception as exc:
        raise HTTPException(409, "asset provenance already exists") from exc
    uow.audit.append("corporation.asset_provenance_bound", "corporation", payload.corporation_id, {"actor_id": str(player_id), "asset_id": str(payload.asset_id), "manufacturer_id": str(payload.manufacturer_id), "quality_rating": quality})
    return {"ok": True, "asset_id": str(payload.asset_id), "manufacturer_id": str(payload.manufacturer_id), "quality_rating": quality, "production_batch": payload.production_batch.strip(), "production_version": payload.production_version}

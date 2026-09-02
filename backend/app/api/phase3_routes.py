from __future__ import annotations
from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.api.dependencies import get_authenticated_player
from app.application.phase3_vehicle_combat import CombatService, RecoveryService, SalvageService, Weapon
from app.domain.primitives import DamageType, Vehicle, VehicleState

router = APIRouter(prefix="/api/v1/phase3", tags=["phase3"])

class CombatRequest(BaseModel):
    target_vehicle_id: UUID
    weapon_code: str = Field(min_length=1, max_length=80)
    component: str = Field(min_length=1, max_length=40)
    distance_m: int = Field(ge=0)
    idempotency_key: str = Field(min_length=1, max_length=200)

class RecoveryRequest(BaseModel):
    vehicle_id: UUID
    duration_seconds: int = Field(gt=0, le=86400 * 30)
    cost: int = Field(ge=0)
    idempotency_key: str = Field(min_length=1, max_length=200)

class Phase3ActionResponse(BaseModel):
    ok: bool
    action: str
    id: UUID | None = None
    message: str = ""

@router.get("/capabilities")
def capabilities(authenticated_player: UUID = Depends(get_authenticated_player)) -> dict:
    return {"player_id": authenticated_player, "systems": ["fitting", "weapons", "combat", "salvage", "recovery", "convoys"]}

@router.post("/combat/resolve", response_model=Phase3ActionResponse)
def resolve_combat(request: CombatRequest, authenticated_player: UUID = Depends(get_authenticated_player)) -> Phase3ActionResponse:
    # Transport-level endpoint contract. Production state mutation must be routed through the authoritative UoW/repository layer.
    if request.component not in {"engine", "hull", "wheels", "fuel_system"}:
        raise HTTPException(422, "unknown vehicle component")
    return Phase3ActionResponse(ok=True, action="combat_resolve", message="authoritative combat command accepted")

@router.post("/recovery/start", response_model=Phase3ActionResponse)
def start_recovery(request: RecoveryRequest, authenticated_player: UUID = Depends(get_authenticated_player)) -> Phase3ActionResponse:
    return Phase3ActionResponse(ok=True, action="recovery_start", id=request.vehicle_id, message="authoritative recovery command accepted")

@router.post("/salvage/preview", response_model=Phase3ActionResponse)
def salvage_preview(vehicle_id: UUID, authenticated_player: UUID = Depends(get_authenticated_player)) -> Phase3ActionResponse:
    return Phase3ActionResponse(ok=True, action="salvage_preview", id=vehicle_id, message="salvage result must be resolved by authoritative vehicle state")

"""Authoritative component damage endpoints."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status
from pydantic import BaseModel, Field

from app.api.dependencies import get_authenticated_player, get_uow
from app.api.idempotency import replay_or_none, require_key, store_response
from app.application.ports import UnitOfWork
from app.application.vehicle_damage import VehicleDamageService
from app.domain.primitives import DamageType

router = APIRouter(prefix="/api/v1", tags=["vehicle-damage"])


class DamageRequest(BaseModel):
    component: str = Field(min_length=1, max_length=40)
    amount: int = Field(gt=0, le=1000)
    damage_type: DamageType


class ComponentRepairRequest(BaseModel):
    component: str = Field(min_length=1, max_length=40)
    amount: int = Field(gt=0, le=100)


def _response(vehicle) -> dict:
    return {
        "id": vehicle.id,
        "owner_id": vehicle.owner_id,
        "code": vehicle.code,
        "chassis_code": vehicle.chassis_code,
        "durability": vehicle.durability,
        "fuel": vehicle.fuel,
        "state": vehicle.state.value,
        "version": vehicle.version,
        "components": {
            name: {
                "condition": component.condition,
                "max_condition": component.max_condition,
                "armor": component.armor,
                "destroyed": component.destroyed,
            }
            for name, component in sorted(vehicle.components.items())
        },
        "effects": vehicle.component_effects(),
    }


class VehicleDamageResponse(BaseModel):
    id: UUID
    owner_id: UUID
    code: str
    chassis_code: str
    durability: int
    fuel: int
    state: str
    version: int
    components: dict
    effects: dict[str, float]


@router.post("/vehicles/{vehicle_id}/damage", response_model=VehicleDamageResponse)
def damage_vehicle(vehicle_id: UUID, payload: DamageRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow), authenticated_player: UUID = Depends(get_authenticated_player)) -> VehicleDamageResponse:
    vehicle = VehicleDamageService(uow).get(vehicle_id)
    if vehicle.owner_id != authenticated_player:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="session does not own player")
    key = require_key(idempotency_key)
    request_data = {"vehicle_id": str(vehicle_id), **payload.model_dump(mode="json")}
    replay = replay_or_none(uow, "vehicle.damage", key, request_data)
    if replay is not None:
        return VehicleDamageResponse.model_validate(replay)
    vehicle = VehicleDamageService(uow).apply_damage(vehicle_id, payload.component, payload.amount, payload.damage_type)
    response = VehicleDamageResponse.model_validate(_response(vehicle))
    store_response(uow, "vehicle.damage", key, request_data, response.model_dump(mode="json"), status.HTTP_200_OK, authenticated_player)
    return response


@router.post("/vehicles/{vehicle_id}/repair-component", response_model=VehicleDamageResponse)
def repair_component(vehicle_id: UUID, payload: ComponentRepairRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow), authenticated_player: UUID = Depends(get_authenticated_player)) -> VehicleDamageResponse:
    vehicle = VehicleDamageService(uow).get(vehicle_id)
    if vehicle.owner_id != authenticated_player:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="session does not own player")
    key = require_key(idempotency_key)
    request_data = {"vehicle_id": str(vehicle_id), **payload.model_dump(mode="json")}
    replay = replay_or_none(uow, "vehicle.repair_component", key, request_data)
    if replay is not None:
        return VehicleDamageResponse.model_validate(replay)
    vehicle = VehicleDamageService(uow).repair_component(vehicle_id, payload.component, payload.amount)
    response = VehicleDamageResponse.model_validate(_response(vehicle))
    store_response(uow, "vehicle.repair_component", key, request_data, response.model_dump(mode="json"), status.HTTP_200_OK, authenticated_player)
    return response

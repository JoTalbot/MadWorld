from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field

from app.api.dependencies import get_authenticated_player, get_uow
from app.api.idempotency import replay_or_none, require_key, store_response
from app.application.expeditions import ExpeditionService
from app.application.ports import UnitOfWork
from app.domain.expeditions import ExpeditionRisk

router = APIRouter(prefix="/api/v1/expeditions", tags=["expeditions"])


class ExpeditionStartRequest(BaseModel):
    vehicle_id: UUID
    inventory_id: UUID
    region: str = Field(min_length=1, max_length=100)
    distance_km: int = Field(ge=1, le=1000)
    risk: ExpeditionRisk = ExpeditionRisk.LOW


class ExpeditionResponse(BaseModel):
    id: UUID
    owner_id: UUID
    job_type: str
    state: str
    started_at: datetime
    completes_at: datetime
    metadata: dict
    version: int


def response(job) -> ExpeditionResponse:
    return ExpeditionResponse.model_validate({
        "id": job.id,
        "owner_id": job.owner_id,
        "job_type": job.job_type,
        "state": job.state.value,
        "started_at": job.started_at,
        "completes_at": job.completes_at,
        "metadata": job.metadata,
        "version": job.version,
    })


@router.post("", response_model=ExpeditionResponse, status_code=201)
def start_expedition(
    payload: ExpeditionStartRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    uow: UnitOfWork = Depends(get_uow),
    player: UUID = Depends(get_authenticated_player),
):
    key = require_key(idempotency_key)
    data = payload.model_dump(mode="json")
    replay = replay_or_none(uow, "expedition.start", key, data)
    if replay is not None:
        return ExpeditionResponse.model_validate(replay)
    job = ExpeditionService(uow).start(player, **payload.model_dump(), idempotency_key=key)
    result = response(job)
    store_response(uow, "expedition.start", key, data, result.model_dump(mode="json"), 201, player)
    return result


@router.post("/{job_id}/complete", response_model=ExpeditionResponse)
def complete_expedition(
    job_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    player: UUID = Depends(get_authenticated_player),
):
    return response(ExpeditionService(uow).complete(player, job_id))

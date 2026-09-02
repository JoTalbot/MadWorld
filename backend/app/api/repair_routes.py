"""Authoritative vehicle repair job commands."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header

from app.api.dependencies import get_authenticated_player, get_uow
from app.api.idempotency import replay_or_none, require_key, store_response
from app.api.schemas import JobResponse, VehicleRepairRequest
from app.application.ports import UnitOfWork
from app.application.services import VehicleService

router = APIRouter(prefix="/api/v1", tags=["vehicle-repair"])


def _job_response(job) -> JobResponse:
    return JobResponse.model_validate({"id": job.id, "owner_id": job.owner_id, "job_type": job.job_type, "started_at": job.started_at, "completes_at": job.completes_at, "state": job.state.value, "version": job.version})


def _assert_owner(authenticated_player: UUID, owner_id: UUID) -> None:
    if authenticated_player != owner_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="session does not own player")


@router.post("/vehicles/{vehicle_id}/repair-job", response_model=JobResponse, status_code=201)
def start_vehicle_repair(vehicle_id: UUID, payload: VehicleRepairRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow), authenticated_player: UUID = Depends(get_authenticated_player)) -> JobResponse:
    vehicle = VehicleService(uow).get(vehicle_id)
    _assert_owner(authenticated_player, vehicle.owner_id)
    key = require_key(idempotency_key)
    request_data = {"vehicle_id": str(vehicle_id), **payload.model_dump(mode="json")}
    replay = replay_or_none(uow, "vehicle.repair_job", key, request_data)
    if replay is not None:
        return JobResponse.model_validate(replay)
    job = VehicleService(uow).start_repair(vehicle_id, payload.inventory_id, payload.amount, key)
    response = _job_response(job)
    store_response(uow, "vehicle.repair_job", key, request_data, response.model_dump(mode="json"), 201, authenticated_player)
    return response


@router.post("/repair-jobs/{job_id}/complete", response_model=JobResponse)
def complete_vehicle_repair(job_id: UUID, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow), authenticated_player: UUID = Depends(get_authenticated_player)) -> JobResponse:
    job = uow.jobs.get(job_id)
    if job is not None:
        _assert_owner(authenticated_player, job.owner_id)
    key = require_key(idempotency_key)
    request_data = {"job_id": str(job_id)}
    replay = replay_or_none(uow, "vehicle.repair_complete", key, request_data)
    if replay is not None:
        return JobResponse.model_validate(replay)
    completed = VehicleService(uow).complete_repair(job_id)
    response = _job_response(completed)
    store_response(uow, "vehicle.repair_complete", key, request_data, response.model_dump(mode="json"), 200, authenticated_player)
    return response

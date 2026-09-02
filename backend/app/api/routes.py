"""Versioned command endpoints backed by application services."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies import get_uow
from app.api.schemas import (
    InventoryAddRequest,
    InventoryRemoveRequest,
    InventoryResponse,
    JobCreateRequest,
    JobResponse,
    WalletEntryRequest,
    WalletEntryResponse,
)
from app.application.ports import UnitOfWork
from app.application.services import InventoryService, JobService, WalletService

router = APIRouter(prefix="/api/v1", tags=["commands"])


def _require_idempotency_key(value: str | None) -> str:
    if not value or not value.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Idempotency-Key header is required")
    return value.strip()


def _wallet_response(entry) -> WalletEntryResponse:
    return WalletEntryResponse(
        entry_id=entry.id,
        wallet_id=entry.wallet_id,
        amount=entry.amount,
        reason=entry.reason,
        idempotency_key=entry.idempotency_key,
        created_at=entry.created_at,
    )


def _job_response(job) -> JobResponse:
    return JobResponse(
        id=job.id,
        owner_id=job.owner_id,
        job_type=job.job_type,
        started_at=job.started_at,
        completes_at=job.completes_at,
        state=job.state.value,
        version=job.version,
    )


@router.post("/wallet/entries", response_model=WalletEntryResponse, status_code=status.HTTP_201_CREATED)
def post_wallet_entry(
    payload: WalletEntryRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    uow: UnitOfWork = Depends(get_uow),
) -> WalletEntryResponse:
    entry = WalletService(uow).post_entry(
        payload.wallet_id,
        payload.amount,
        payload.reason,
        _require_idempotency_key(idempotency_key),
        payload.actor_id,
    )
    return _wallet_response(entry)


@router.post("/inventory/add", response_model=InventoryResponse)
def add_inventory(payload: InventoryAddRequest, uow: UnitOfWork = Depends(get_uow)) -> InventoryResponse:
    stack = InventoryService(uow).add(
        payload.inventory_id,
        payload.item_definition_id,
        payload.quantity,
        payload.condition,
    )
    return InventoryResponse(
        item_definition_id=stack.item_definition_id,
        quantity=stack.quantity,
        condition=stack.condition,
        version=stack.version,
    )


@router.post("/inventory/remove", response_model=InventoryResponse | None)
def remove_inventory(payload: InventoryRemoveRequest, uow: UnitOfWork = Depends(get_uow)) -> InventoryResponse | None:
    stack = InventoryService(uow).remove(payload.inventory_id, payload.item_definition_id, payload.quantity)
    if stack is None:
        return None
    return InventoryResponse(
        item_definition_id=stack.item_definition_id,
        quantity=stack.quantity,
        condition=stack.condition,
        version=stack.version,
    )


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreateRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    uow: UnitOfWork = Depends(get_uow),
) -> JobResponse:
    job = JobService(uow).create(
        payload.owner_id,
        payload.job_type,
        payload.started_at,
        payload.completes_at,
        _require_idempotency_key(idempotency_key),
    )
    return _job_response(job)


@router.post("/jobs/{job_id}/start", response_model=JobResponse)
def start_job(job_id: UUID, uow: UnitOfWork = Depends(get_uow)) -> JobResponse:
    return _job_response(JobService(uow).start(job_id))


@router.post("/jobs/{job_id}/complete", response_model=JobResponse)
def complete_job(job_id: UUID, uow: UnitOfWork = Depends(get_uow)) -> JobResponse:
    return _job_response(JobService(uow).complete(job_id))


@router.post("/jobs/{job_id}/cancel", response_model=JobResponse)
def cancel_job(job_id: UUID, uow: UnitOfWork = Depends(get_uow)) -> JobResponse:
    return _job_response(JobService(uow).cancel(job_id))

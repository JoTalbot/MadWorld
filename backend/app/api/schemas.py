"""Stable request/response DTOs for the v1 API."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WalletEntryRequest(BaseModel):
    wallet_id: UUID
    amount: int = Field(ne=0)
    reason: str = Field(min_length=1, max_length=200)
    actor_id: UUID | None = None


class WalletEntryResponse(BaseModel):
    entry_id: UUID
    wallet_id: UUID
    amount: int
    reason: str
    idempotency_key: str
    created_at: datetime


class InventoryAddRequest(BaseModel):
    inventory_id: UUID
    item_definition_id: UUID
    quantity: int = Field(gt=0)
    condition: int = Field(default=100, ge=0, le=100)


class InventoryRemoveRequest(BaseModel):
    inventory_id: UUID
    item_definition_id: UUID
    quantity: int = Field(gt=0)


class InventoryResponse(BaseModel):
    item_definition_id: UUID
    quantity: int
    condition: int
    version: int


class JobCreateRequest(BaseModel):
    owner_id: UUID
    job_type: str = Field(min_length=1, max_length=100)
    started_at: datetime
    completes_at: datetime


class JobResponse(BaseModel):
    id: UUID
    owner_id: UUID
    job_type: str
    started_at: datetime
    completes_at: datetime
    state: str
    version: int


class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str
    details: dict | None = None

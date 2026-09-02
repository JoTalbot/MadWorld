"""Stable request/response DTOs for the v1 API."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class WalletEntryRequest(BaseModel):
    wallet_id: UUID
    amount: int
    reason: str = Field(min_length=1, max_length=200)
    actor_id: UUID | None = None
    @model_validator(mode="after")
    def validate_amount(self) -> "WalletEntryRequest":
        if self.amount == 0: raise ValueError("amount must not be zero")
        return self
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
class InventorySnapshot(InventoryResponse):
    inventory_id: UUID
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
class CharacterCreateRequest(BaseModel):
    player_id: UUID
    name: str = Field(min_length=1, max_length=80)
class CharacterResponse(BaseModel):
    id: UUID
    player_id: UUID
    name: str
    level: int
    version: int
class VehicleCreateRequest(BaseModel):
    owner_id: UUID
    code: str | None = Field(default=None, min_length=1, max_length=100)
    chassis_code: str = Field(default="light_runner", min_length=1, max_length=100)
class VehicleMutationRequest(BaseModel):
    amount: int = Field(gt=0)
class VehicleRepairRequest(BaseModel):
    inventory_id: UUID
    amount: int = Field(gt=0, le=100)
class VehicleResponse(BaseModel):
    id: UUID
    owner_id: UUID
    code: str
    chassis_code: str
    durability: int
    fuel: int
    state: str
    version: int
class WalletSnapshot(BaseModel):
    id: UUID
    balance: int
    version: int
class PlayerBootstrapRequest(BaseModel):
    player_id: UUID
    character_name: str = Field(min_length=1, max_length=80)
class PlayerBootstrapResponse(BaseModel):
    character: CharacterResponse
    vehicle: VehicleResponse
class PlayerStateResponse(BaseModel):
    character: CharacterResponse | None
    vehicles: list[VehicleResponse]
    wallet: WalletSnapshot | None = None
    inventory: list[InventorySnapshot] = Field(default_factory=list)
    active_jobs: list[JobResponse] = Field(default_factory=list)
class ResourceGatherRequest(BaseModel):
    inventory_id: UUID
    node_id: UUID
class ResourceGatherResponse(BaseModel):
    node_id: UUID
    region_id: UUID
    item_definition_id: UUID
    gathered_quantity: int
    remaining_quantity: int
    next_available_at: datetime
    version: int
class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str
    details: dict | None = None


class ContractTemplateResponse(BaseModel):
    code: str
    title: str
    description: str
    contract_type: str
    item_definition_id: UUID
    required_quantity: int
    reward: int
    duration_seconds: int
    penalty: int

class ContractAcceptRequest(BaseModel):
    template_code: str = Field(min_length=1, max_length=100)
    inventory_id: UUID
    wallet_id: UUID

class ContractResponse(BaseModel):
    id: UUID
    owner_id: UUID
    template_code: str
    title: str
    description: str
    contract_type: str
    item_definition_id: UUID
    required_quantity: int
    reward: int
    penalty: int
    inventory_id: UUID
    wallet_id: UUID
    accepted_at: datetime
    deadline: datetime
    state: str
    version: int

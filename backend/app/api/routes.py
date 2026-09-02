"""Versioned authoritative command endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from app.api.dependencies import get_uow
from app.api.idempotency import replay_or_none, require_key, store_response
from app.api.schemas import (
    CharacterCreateRequest,
    CharacterResponse,
    InventoryAddRequest,
    InventoryRemoveRequest,
    InventoryResponse,
    JobCreateRequest,
    JobResponse,
    VehicleCreateRequest,
    VehicleMutationRequest,
    VehicleResponse,
    WalletEntryRequest,
    WalletEntryResponse,
)
from app.application.ports import UnitOfWork
from app.application.services import CharacterService, InventoryService, JobService, VehicleService, WalletService

router = APIRouter(prefix="/api/v1", tags=["commands"])


def _wallet_response(entry) -> WalletEntryResponse:
    return WalletEntryResponse.model_validate({"entry_id": entry.id, "wallet_id": entry.wallet_id, "amount": entry.amount, "reason": entry.reason, "idempotency_key": entry.idempotency_key, "created_at": entry.created_at})


def _job_response(job: object) -> JobResponse:
    return JobResponse.model_validate({"id": job.id, "owner_id": job.owner_id, "job_type": job.job_type, "started_at": job.started_at, "completes_at": job.completes_at, "state": job.state.value, "version": job.version})


def _inventory_response(stack) -> InventoryResponse:
    return InventoryResponse.model_validate({"item_definition_id": stack.item_definition_id, "quantity": stack.quantity, "condition": stack.condition, "version": stack.version})


def _character_response(character) -> CharacterResponse:
    return CharacterResponse.model_validate({"id": character.id, "player_id": character.player_id, "name": character.name, "level": character.level, "version": character.version})


def _vehicle_response(vehicle) -> VehicleResponse:
    return VehicleResponse.model_validate({"id": vehicle.id, "owner_id": vehicle.owner_id, "code": vehicle.code, "chassis_code": vehicle.chassis_code, "durability": vehicle.durability, "fuel": vehicle.fuel, "state": vehicle.state.value})


@router.post("/wallet/entries", response_model=WalletEntryResponse, status_code=status.HTTP_201_CREATED)
def post_wallet_entry(payload: WalletEntryRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow)) -> WalletEntryResponse:
    key = require_key(idempotency_key); request_data = payload.model_dump(mode="json"); replay = replay_or_none(uow, "wallet.post_entry", key, request_data)
    if replay is not None: return WalletEntryResponse.model_validate(replay)
    entry = WalletService(uow).post_entry(payload.wallet_id, payload.amount, payload.reason, key, payload.actor_id); response = _wallet_response(entry)
    store_response(uow, "wallet.post_entry", key, request_data, response.model_dump(mode="json"), status.HTTP_201_CREATED, payload.actor_id); return response


@router.post("/inventory/add", response_model=InventoryResponse, status_code=status.HTTP_200_OK)
def add_inventory(payload: InventoryAddRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow)) -> InventoryResponse:
    key = require_key(idempotency_key); request_data = payload.model_dump(mode="json"); replay = replay_or_none(uow, "inventory.add", key, request_data)
    if replay is not None: return InventoryResponse.model_validate(replay)
    stack = InventoryService(uow).add(payload.inventory_id, payload.item_definition_id, payload.quantity, payload.condition); response = _inventory_response(stack)
    store_response(uow, "inventory.add", key, request_data, response.model_dump(mode="json"), status.HTTP_200_OK); return response


@router.post("/inventory/remove", response_model=InventoryResponse | None)
def remove_inventory(payload: InventoryRemoveRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow)) -> InventoryResponse | None:
    key = require_key(idempotency_key); request_data = payload.model_dump(mode="json"); replay = replay_or_none(uow, "inventory.remove", key, request_data)
    if replay is not None: return InventoryResponse.model_validate(replay) if replay else None
    stack = InventoryService(uow).remove(payload.inventory_id, payload.item_definition_id, payload.quantity); response = _inventory_response(stack) if stack is not None else None
    store_response(uow, "inventory.remove", key, request_data, response.model_dump(mode="json") if response else {}, status.HTTP_200_OK); return response


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreateRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow)) -> JobResponse:
    key = require_key(idempotency_key); request_data = payload.model_dump(mode="json"); replay = replay_or_none(uow, "job.create", key, request_data)
    if replay is not None: return JobResponse.model_validate(replay)
    job = JobService(uow).create(payload.owner_id, payload.job_type, payload.started_at, payload.completes_at, key); response = _job_response(job)
    store_response(uow, "job.create", key, request_data, response.model_dump(mode="json"), status.HTTP_201_CREATED, payload.owner_id); return response


@router.post("/jobs/{job_id}/start", response_model=JobResponse)
def start_job(job_id: UUID, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow)) -> JobResponse:
    return _job_transition(job_id, "job.start", idempotency_key, uow, lambda: JobService(uow).start(job_id))


@router.post("/jobs/{job_id}/complete", response_model=JobResponse)
def complete_job(job_id: UUID, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow)) -> JobResponse:
    return _job_transition(job_id, "job.complete", idempotency_key, uow, lambda: JobService(uow).complete(job_id))


@router.post("/jobs/{job_id}/cancel", response_model=JobResponse)
def cancel_job(job_id: UUID, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow)) -> JobResponse:
    return _job_transition(job_id, "job.cancel", idempotency_key, uow, lambda: JobService(uow).cancel(job_id))


def _job_transition(job_id: UUID, command_name: str, idempotency_key: str | None, uow: UnitOfWork, transition) -> JobResponse:
    key = require_key(idempotency_key); request_data = {"job_id": str(job_id)}; replay = replay_or_none(uow, command_name, key, request_data)
    if replay is not None: return JobResponse.model_validate(replay)
    response = _job_response(transition()); store_response(uow, command_name, key, request_data, response.model_dump(mode="json"), status.HTTP_200_OK); return response


@router.post("/characters", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
def create_character(payload: CharacterCreateRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow)) -> CharacterResponse:
    key = require_key(idempotency_key); request_data = payload.model_dump(mode="json"); replay = replay_or_none(uow, "character.create", key, request_data)
    if replay is not None: return CharacterResponse.model_validate(replay)
    character = CharacterService(uow).create(payload.player_id, payload.name); response = _character_response(character)
    store_response(uow, "character.create", key, request_data, response.model_dump(mode="json"), status.HTTP_201_CREATED, payload.player_id); return response


@router.get("/characters/by-player/{player_id}", response_model=CharacterResponse)
def get_character(player_id: UUID, uow: UnitOfWork = Depends(get_uow)) -> CharacterResponse:
    return _character_response(CharacterService(uow).get_for_player(player_id))


@router.post("/vehicles/starter", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_starter_vehicle(payload: VehicleCreateRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow)) -> VehicleResponse:
    key = require_key(idempotency_key); request_data = payload.model_dump(mode="json"); replay = replay_or_none(uow, "vehicle.create_starter", key, request_data)
    if replay is not None: return VehicleResponse.model_validate(replay)
    vehicle = VehicleService(uow).create_starter(payload.owner_id, payload.code, payload.chassis_code); response = _vehicle_response(vehicle)
    store_response(uow, "vehicle.create_starter", key, request_data, response.model_dump(mode="json"), status.HTTP_201_CREATED, payload.owner_id); return response


@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: UUID, uow: UnitOfWork = Depends(get_uow)) -> VehicleResponse:
    return _vehicle_response(VehicleService(uow).get(vehicle_id))


@router.get("/vehicles/by-owner/{owner_id}", response_model=list[VehicleResponse])
def list_vehicles(owner_id: UUID, uow: UnitOfWork = Depends(get_uow)) -> list[VehicleResponse]:
    return [_vehicle_response(vehicle) for vehicle in VehicleService(uow).list_for_owner(owner_id)]


def _vehicle_mutation(vehicle_id: UUID, payload: VehicleMutationRequest, command_name: str, idempotency_key: str | None, uow: UnitOfWork, mutate) -> VehicleResponse:
    key = require_key(idempotency_key); request_data = {"vehicle_id": str(vehicle_id), **payload.model_dump(mode="json")}; replay = replay_or_none(uow, command_name, key, request_data)
    if replay is not None: return VehicleResponse.model_validate(replay)
    response = _vehicle_response(mutate(payload.amount)); store_response(uow, command_name, key, request_data, response.model_dump(mode="json"), status.HTTP_200_OK); return response


@router.post("/vehicles/{vehicle_id}/repair", response_model=VehicleResponse)
def repair_vehicle(vehicle_id: UUID, payload: VehicleMutationRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow)) -> VehicleResponse:
    return _vehicle_mutation(vehicle_id, payload, "vehicle.repair", idempotency_key, uow, lambda amount: VehicleService(uow).repair(vehicle_id, amount))


@router.post("/vehicles/{vehicle_id}/refuel", response_model=VehicleResponse)
def refuel_vehicle(vehicle_id: UUID, payload: VehicleMutationRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), uow: UnitOfWork = Depends(get_uow)) -> VehicleResponse:
    return _vehicle_mutation(vehicle_id, payload, "vehicle.refuel", idempotency_key, uow, lambda amount: VehicleService(uow).refuel(vehicle_id, amount))

"""B2 authoritative travel/gameplay API."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import get_authenticated_player, get_uow
from app.application.travel_service import (
    claim_recovery,
    depart_travel,
    plan_travel,
    resolve_encounter,
    resolve_travel,
    spawn_encounter,
)

router = APIRouter(prefix="/api/v1/travel", tags=["travel"])


class TravelPlan(BaseModel):
    vehicle_id: UUID
    origin_region_id: UUID
    destination_region_id: UUID
    world_region_id: str = Field(min_length=1, max_length=64)
    duration_seconds: int = Field(gt=0, le=7 * 24 * 3600)
    fuel_reserved: int = Field(ge=0)
    cargo_weight: int = Field(ge=0)
    base_risk_bps: int = Field(ge=0, le=10000)
    idempotency_key: str = Field(min_length=1, max_length=128)


class TravelResolve(BaseModel):
    outcome: str


class EncounterResolve(BaseModel):
    outcome: str


@router.post("/plan")
def create_travel_plan(body: TravelPlan, player_id: UUID = Depends(get_authenticated_player), uow=Depends(get_uow)):
    owned = uow.conn.execute(
        __import__('sqlalchemy').text("SELECT 1 FROM vehicles WHERE id=:v AND owner_id=:p"),
        {"v": body.vehicle_id, "p": player_id},
    ).first()
    if not owned:
        raise PermissionError("vehicle does not belong to authenticated player")
    return plan_travel(uow.conn, player_id=player_id, **body.model_dump())


@router.post("/{session_id}/depart")
def depart(session_id: UUID, player_id: UUID = Depends(get_authenticated_player), uow=Depends(get_uow)):
    owned = uow.conn.execute(
        __import__('sqlalchemy').text("SELECT 1 FROM player_travel_sessions WHERE id=:s AND player_id=:p"),
        {"s": session_id, "p": player_id},
    ).first()
    if not owned:
        raise PermissionError("travel session does not belong to authenticated player")
    return depart_travel(uow.conn, session_id=session_id)


@router.post("/{session_id}/resolve")
def resolve(session_id: UUID, body: TravelResolve, player_id: UUID = Depends(get_authenticated_player), uow=Depends(get_uow)):
    owned = uow.conn.execute(
        __import__('sqlalchemy').text("SELECT 1 FROM player_travel_sessions WHERE id=:s AND player_id=:p"),
        {"s": session_id, "p": player_id},
    ).first()
    if not owned:
        raise PermissionError("travel session does not belong to authenticated player")
    return resolve_travel(uow.conn, session_id=session_id, outcome=body.outcome)


@router.post("/{session_id}/encounters/{world_event_id}")
def encounter(session_id: UUID, world_event_id: UUID, encounter_type: str, severity: int = 1,
              player_id: UUID = Depends(get_authenticated_player), uow=Depends(get_uow)):
    owned = uow.conn.execute(
        __import__('sqlalchemy').text("SELECT 1 FROM player_travel_sessions WHERE id=:s AND player_id=:p"),
        {"s": session_id, "p": player_id},
    ).first()
    if not owned:
        raise PermissionError("travel session does not belong to authenticated player")
    return {"encounter_id": str(spawn_encounter(uow.conn, session_id=session_id, world_event_id=world_event_id, encounter_type=encounter_type, severity=severity))}


@router.post("/encounters/{encounter_id}/resolve")
def resolve_encounter_route(encounter_id: UUID, body: EncounterResolve,
                            player_id: UUID = Depends(get_authenticated_player), uow=Depends(get_uow)):
    owned = uow.conn.execute(
        __import__('sqlalchemy').text("""
            SELECT 1 FROM travel_encounters e JOIN player_travel_sessions s ON s.id=e.travel_session_id
            WHERE e.id=:e AND s.player_id=:p
        """), {"e": encounter_id, "p": player_id}).first()
    if not owned:
        raise PermissionError("encounter does not belong to authenticated player")
    return resolve_encounter(uow.conn, encounter_id=encounter_id, outcome=body.outcome)


@router.post("/recovery/{case_id}/claim")
def claim(case_id: UUID, player_id: UUID = Depends(get_authenticated_player), uow=Depends(get_uow)):
    return claim_recovery(uow.conn, player_id=player_id, case_id=case_id)

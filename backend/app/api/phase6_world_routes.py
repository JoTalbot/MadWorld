"""Authoritative Phase 6 world-state queries and simulation control surface."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_uow
from app.application.phase6_world import simulate_tick
from app.application.ports import UnitOfWork

router = APIRouter(prefix="/api/v1/world-simulation", tags=["world-simulation"])

@router.get("")
def world_state(player: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    state = uow.conn.execute(text("SELECT season,tick,last_tick_at,version FROM world_simulation_state WHERE id=1")).mappings().one()
    factions = uow.conn.execute(text("SELECT id,name,doctrine,aggression_bps,logistics_bps,version FROM world_factions ORDER BY id")).mappings().all()
    pressures = uow.conn.execute(text("SELECT region_id,resource_type,target_quantity,available_quantity,pressure_bps,trend_bps,version FROM regional_resource_pressure ORDER BY region_id,resource_type")).mappings().all()
    events = uow.conn.execute(text("SELECT id,tick,region_id,faction_id,event_type,severity,state,payload,created_at FROM world_events WHERE state='ACTIVE' ORDER BY created_at DESC LIMIT 50")).mappings().all()
    missions = uow.conn.execute(text("SELECT id,region_id,mission_type,title,reward_credits,risk_bps,state,expires_at FROM dynamic_missions WHERE state='AVAILABLE' ORDER BY created_at DESC LIMIT 50")).mappings().all()
    discoveries = uow.conn.execute(text("SELECT id,region_id,resource_type,quantity,expires_at,state FROM resource_discoveries WHERE state='AVAILABLE' ORDER BY id DESC LIMIT 50")).mappings().all()
    disasters = uow.conn.execute(text("SELECT d.id,d.region_id,d.disaster_type,d.severity,d.starts_at,d.ends_at,z.hazard_bps,z.travel_risk_bps,z.extraction_modifier_bps FROM world_disasters d JOIN catastrophe_zones z ON z.disaster_id=d.id WHERE d.state='ACTIVE' ORDER BY d.starts_at DESC LIMIT 50")).mappings().all()
    return {"authoritative":True,"simulation":dict(state),"factions":[dict(x) for x in factions],"pressures":[dict(x) for x in pressures],"events":[dict(x) for x in events],"missions":[dict(x) for x in missions],"discoveries":[dict(x) for x in discoveries],"disasters":[dict(x) for x in disasters]}

@router.post("/tick")
def advance_tick(player: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow), expected_tick: int | None = None, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    # This endpoint is intentionally restricted to the authenticated operator path
    # in deployment. Until a dedicated service identity exists, reject player calls
    # rather than allowing any game client to advance global simulation time.
    raise HTTPException(403, "world simulation ticks are service-controlled")


def run_world_tick(uow: UnitOfWork, expected_tick: int | None = None) -> dict:
    """Service/scheduler entry point; API clients cannot invoke it directly."""
    return simulate_tick(uow.conn, expected_tick)

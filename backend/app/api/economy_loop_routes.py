"""Authoritative economy-to-gameplay read model.

Composes existing authoritative systems into one compact mobile-facing view.
It does not create a second source of truth.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_engine

router = APIRouter(prefix="/api/v1/economy", tags=["economy-loop"])


class EconomyJob(BaseModel):
    id: UUID
    kind: str
    recipe_id: UUID
    settlement_id: UUID
    state: str
    completes_at: str


class EconomyFacility(BaseModel):
    code: str
    level: int
    efficiency_bps: int


class EconomyOverview(BaseModel):
    settlement_id: UUID
    region: str
    warehouse_capacity: int
    warehouse_used: int
    facilities: list[EconomyFacility]
    active_jobs: list[EconomyJob]
    contract_count: int
    ready_vehicles: int
    market_price_points: int
    next_action: str


def _next_action(active_jobs: int, contract_count: int, ready_vehicles: int, market_points: int) -> str:
    if active_jobs:
        return "job_in_progress"
    if contract_count:
        return "review_contracts"
    if ready_vehicles:
        return "prepare_expedition"
    if market_points:
        return "review_market"
    return "gather_resources"


@router.get("/overview", response_model=EconomyOverview)
def economy_overview(authenticated_player: UUID = Depends(get_authenticated_player)) -> EconomyOverview:
    with get_engine().connect() as conn:
        settlement = conn.execute(
            text("SELECT s.id, s.region FROM player_settlements ps JOIN settlements s ON s.id=ps.settlement_id WHERE ps.player_id=:player ORDER BY s.id LIMIT 1"),
            {"player": authenticated_player},
        ).mappings().first()
        if settlement is None:
            raise ValueError("player settlement not found")
        settlement_id = UUID(str(settlement["id"]))
        inv = conn.execute(text("SELECT id FROM inventories WHERE owner_id=:owner ORDER BY id LIMIT 1"), {"owner": authenticated_player}).scalar()
        used = int(conn.execute(text("SELECT COALESCE(SUM(quantity),0) FROM inventory_items WHERE inventory_id=:inv"), {"inv": inv}).scalar() or 0) if inv else 0
        level = int(conn.execute(text("SELECT COALESCE(level,1) FROM player_settlement_state WHERE settlement_id=:settlement AND owner_id=:owner"), {"settlement": settlement_id, "owner": authenticated_player}).scalar() or 1)
        capacity = 1000 + (level - 1) * 500
        facilities = conn.execute(text("SELECT code,level,efficiency_bps FROM economy_facilities WHERE settlement_id=:settlement ORDER BY code"), {"settlement": settlement_id}).mappings().all()
        jobs = conn.execute(text("SELECT id,kind,recipe_id,settlement_id,state,completes_at FROM economy_jobs WHERE owner_id=:owner AND state='running' ORDER BY completes_at"), {"owner": authenticated_player}).mappings().all()
        contract_count = int(conn.execute(text("SELECT COUNT(*) FROM contracts WHERE player_id=:player AND state IN ('available','accepted','in_progress')"), {"player": authenticated_player}).scalar() or 0)
        ready_vehicles = int(conn.execute(text("SELECT COUNT(*) FROM vehicles WHERE owner_id=:owner AND state='active' AND durability >= 50 AND fuel > 0"), {"owner": authenticated_player}).scalar() or 0)
        market_points = int(conn.execute(text("SELECT COUNT(*) FROM market_price_history WHERE recorded_at >= NOW() - INTERVAL '7 days'")).scalar() or 0)
    return EconomyOverview(
        settlement_id=settlement_id,
        region=str(settlement["region"]),
        warehouse_capacity=capacity,
        warehouse_used=used,
        facilities=[EconomyFacility(code=str(r["code"]), level=int(r["level"]), efficiency_bps=int(r["efficiency_bps"])) for r in facilities],
        active_jobs=[EconomyJob(id=UUID(str(r["id"])), kind=str(r["kind"]), recipe_id=UUID(str(r["recipe_id"])), settlement_id=UUID(str(r["settlement_id"])), state=str(r["state"]), completes_at=r["completes_at"].isoformat()) for r in jobs],
        contract_count=contract_count,
        ready_vehicles=ready_vehicles,
        market_price_points=market_points,
        next_action=_next_action(len(jobs), contract_count, ready_vehicles, market_points),
    )

"""B3 Advanced Economy API surface."""
from uuid import UUID
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy import text
from app.api.dependencies import get_authenticated_player, get_engine
from app.application.phase7_economy import regional_state, market_metrics
from app.application.phase7_economy_tx import (
    complete_production,
    create_facility,
    create_logistics,
    create_warehouse,
    deliver_logistics,
    start_production,
)

router = APIRouter(prefix="/api/v1/economy", tags=["economy"])


class CapacityRequest(BaseModel):
    region_id: UUID
    name: str = Field(min_length=1, max_length=120)
    capacity_units: int = Field(gt=0)


class FacilityRequest(CapacityRequest):
    facility_type: str = Field(min_length=1, max_length=80)


class ProductionRequest(BaseModel):
    facility_id: UUID
    recipe_id: UUID
    batch_units: int = Field(gt=0)


class LogisticsRequest(BaseModel):
    source_warehouse_id: UUID
    destination_warehouse_id: UUID
    item_definition_id: UUID
    quantity: int = Field(gt=0)
    reward: int = Field(ge=0)
    route_risk_bps: int = Field(ge=0, le=10000)


@router.get("/regions/{region_id}")
def economy_region(
    region_id: UUID,
    authenticated_player: UUID = Depends(get_authenticated_player),
):
    with get_engine().connect() as conn:
        return regional_state(conn, region_id)


@router.get("/regions/{region_id}/items/{item_id}/metrics")
def economy_metrics(
    region_id: UUID,
    item_id: UUID,
    authenticated_player: UUID = Depends(get_authenticated_player),
):
    with get_engine().connect() as conn:
        return {
            "region_id": region_id,
            "item_definition_id": item_id,
            **market_metrics(conn, region_id, item_id),
        }


@router.get("/warehouses")
def warehouses(authenticated_player: UUID = Depends(get_authenticated_player)):
    with get_engine().connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM warehouses WHERE owner_id=:o ORDER BY created_at"),
            {"o": authenticated_player},
        ).mappings().all()
        return [dict(r) for r in rows]


@router.post("/warehouses", status_code=201)
def warehouse_create(
    payload: CapacityRequest,
    authenticated_player: UUID = Depends(get_authenticated_player),
):
    with get_engine().begin() as conn:
        return dict(
            create_warehouse(
                conn,
                authenticated_player,
                payload.region_id,
                payload.name,
                payload.capacity_units,
            )
        )


@router.get("/facilities")
def facilities(authenticated_player: UUID = Depends(get_authenticated_player)):
    with get_engine().connect() as conn:
        rows = conn.execute(
            text(
                "SELECT * FROM production_facilities "
                "WHERE owner_id=:o ORDER BY created_at"
            ),
            {"o": authenticated_player},
        ).mappings().all()
        return [dict(r) for r in rows]


@router.post("/facilities", status_code=201)
def facility_create(
    payload: FacilityRequest,
    authenticated_player: UUID = Depends(get_authenticated_player),
):
    with get_engine().begin() as conn:
        return dict(
            create_facility(
                conn,
                authenticated_player,
                payload.region_id,
                payload.name,
                payload.facility_type,
                payload.capacity_units,
            )
        )


@router.get("/production/recipes")
def production_recipes(authenticated_player: UUID = Depends(get_authenticated_player)):
    with get_engine().connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM production_recipes WHERE enabled=TRUE ORDER BY code")
        ).mappings().all()
        return [dict(r) for r in rows]


@router.get("/production/jobs")
def production_jobs(authenticated_player: UUID = Depends(get_authenticated_player)):
    with get_engine().connect() as conn:
        rows = conn.execute(
            text(
                "SELECT * FROM production_jobs "
                "WHERE owner_id=:o ORDER BY started_at DESC"
            ),
            {"o": authenticated_player},
        ).mappings().all()
        return [dict(r) for r in rows]


@router.post("/production/start", status_code=201)
def production_start(
    payload: ProductionRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    authenticated_player: UUID = Depends(get_authenticated_player),
):
    if not idempotency_key:
        raise ValueError("Idempotency-Key header is required")
    with get_engine().begin() as conn:
        return dict(
            start_production(
                conn,
                authenticated_player,
                payload.facility_id,
                payload.recipe_id,
                payload.batch_units,
                idempotency_key,
            )
        )


@router.post("/production/{job_id}/complete")
def production_complete(
    job_id: UUID,
    authenticated_player: UUID = Depends(get_authenticated_player),
):
    with get_engine().begin() as conn:
        return dict(complete_production(conn, authenticated_player, job_id))


@router.get("/logistics")
def logistics(authenticated_player: UUID = Depends(get_authenticated_player)):
    with get_engine().connect() as conn:
        rows = conn.execute(
            text(
                "SELECT * FROM logistics_contracts "
                "WHERE owner_id=:o ORDER BY created_at DESC"
            ),
            {"o": authenticated_player},
        ).mappings().all()
        return [dict(r) for r in rows]


@router.post("/logistics", status_code=201)
def logistics_create(
    payload: LogisticsRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    authenticated_player: UUID = Depends(get_authenticated_player),
):
    if not idempotency_key:
        raise ValueError("Idempotency-Key header is required")
    with get_engine().begin() as conn:
        return dict(
            create_logistics(
                conn,
                authenticated_player,
                payload.source_warehouse_id,
                payload.destination_warehouse_id,
                payload.item_definition_id,
                payload.quantity,
                payload.reward,
                payload.route_risk_bps,
                idempotency_key,
            )
        )


@router.post("/logistics/{contract_id}/deliver")
def logistics_deliver(
    contract_id: UUID,
    authenticated_player: UUID = Depends(get_authenticated_player),
):
    with get_engine().begin() as conn:
        return dict(deliver_logistics(conn, authenticated_player, contract_id))

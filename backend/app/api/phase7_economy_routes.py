"""B3 Advanced Economy API surface."""
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from app.api.dependencies import get_authenticated_player, get_engine
from app.application.phase7_economy import regional_state, market_metrics

router=APIRouter(prefix="/api/v1/economy",tags=["economy"])

class CapacityRequest(BaseModel):
    region_id: UUID
    name: str = Field(min_length=1,max_length=120)
    capacity_units: int = Field(gt=0)

@router.get("/regions/{region_id}")
def economy_region(region_id: UUID, authenticated_player: UUID=Depends(get_authenticated_player)):
    with get_engine().connect() as conn:
        return regional_state(conn,region_id)

@router.get("/regions/{region_id}/items/{item_id}/metrics")
def economy_metrics(region_id: UUID,item_id: UUID,authenticated_player: UUID=Depends(get_authenticated_player)):
    with get_engine().connect() as conn:
        return {"region_id":region_id,"item_definition_id":item_id,**market_metrics(conn,region_id,item_id)}

@router.get("/warehouses")
def warehouses(authenticated_player: UUID=Depends(get_authenticated_player)):
    with get_engine().connect() as conn:
        rows=conn.execute(text("SELECT * FROM warehouses WHERE owner_id=:o ORDER BY created_at"),{"o":authenticated_player}).mappings().all()
    return [dict(r) for r in rows]

@router.post("/warehouses",status_code=201)
def create_warehouse(payload:CapacityRequest,authenticated_player: UUID=Depends(get_authenticated_player)):
    with get_engine().begin() as conn:
        row=conn.execute(text("INSERT INTO warehouses(owner_id,region_id,name,capacity_units) VALUES(:o,:r,:n,:c) RETURNING *"),{"o":authenticated_player,"r":payload.region_id,"n":payload.name,"c":payload.capacity_units}).mappings().one()
    return dict(row)

@router.get("/facilities")
def facilities(authenticated_player: UUID=Depends(get_authenticated_player)):
    with get_engine().connect() as conn:
        rows=conn.execute(text("SELECT * FROM production_facilities WHERE owner_id=:o ORDER BY created_at"),{"o":authenticated_player}).mappings().all()
    return [dict(r) for r in rows]

@router.post("/facilities",status_code=201)
def create_facility(payload:CapacityRequest,facility_type: str="refinery",authenticated_player: UUID=Depends(get_authenticated_player)):
    with get_engine().begin() as conn:
        row=conn.execute(text("INSERT INTO production_facilities(owner_id,region_id,name,facility_type,capacity_units) VALUES(:o,:r,:n,:t,:c) RETURNING *"),{"o":authenticated_player,"r":payload.region_id,"n":payload.name,"t":facility_type,"c":payload.capacity_units}).mappings().one()
    return dict(row)

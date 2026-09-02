from __future__ import annotations
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, Header, Query
from pydantic import BaseModel
from sqlalchemy import text
from app.api.dependencies import get_authenticated_player, get_engine
from app.api.idempotency import request_hash
router = APIRouter(prefix="/api/v1/economy", tags=["economy"])
class StartJobRequest(BaseModel):
    recipe_id: UUID
    settlement_id: UUID
class RecipeResponse(BaseModel):
    id: UUID; code: str; name: str; kind: str; facility_code: str; duration_seconds: int; inputs: list[dict]; outputs: list[dict]
class JobResponse(BaseModel):
    id: UUID; recipe_id: UUID; settlement_id: UUID; state: str; started_at: str; completes_at: str
class WarehouseItem(BaseModel):
    item_definition_id: UUID; code: str; name: str; quantity: int; condition: int
class WarehouseResponse(BaseModel):
    settlement_id: UUID; capacity: int; used: int; items: list[WarehouseItem]
class PricePoint(BaseModel):
    recorded_at: str; quantity: int; unit_price: int; total_amount: int
def _inventory(conn, player_id: UUID):
    row = conn.execute(text("SELECT id FROM inventories WHERE owner_id=:owner ORDER BY id LIMIT 1 FOR UPDATE"), {"owner": player_id}).mappings().first()
    if row is None: raise ValueError("player inventory not found")
    return row["id"]
def _recipe(conn, recipe_id: UUID):
    row = conn.execute(text("SELECT * FROM economy_recipes WHERE id=:id AND enabled=true"), {"id": recipe_id}).mappings().first()
    if row is None: raise ValueError("economy recipe not found or disabled")
    return row
def _json(value): return value if isinstance(value, list) else json.loads(value)
def _owned_settlement(conn, player_id: UUID, settlement_id: UUID) -> None:
    if conn.execute(text("SELECT 1 FROM player_settlements WHERE player_id=:player AND settlement_id=:settlement"), {"player": player_id, "settlement": settlement_id}).scalar() is None: raise PermissionError("settlement does not belong to player")
def _job_response(row) -> JobResponse: return JobResponse(id=row["id"], recipe_id=row["recipe_id"], settlement_id=row["settlement_id"], state=row["state"], started_at=row["started_at"].isoformat(), completes_at=row["completes_at"].isoformat())
@router.get("/recipes", response_model=list[RecipeResponse])
def recipes(kind: str | None = None, authenticated_player: UUID = Depends(get_authenticated_player)):
    with get_engine().connect() as conn: rows = conn.execute(text("SELECT * FROM economy_recipes WHERE enabled=true AND (:kind IS NULL OR kind=:kind) ORDER BY kind,code"), {"kind": kind}).mappings().all()
    return [RecipeResponse(id=r["id"], code=r["code"], name=r["name"], kind=r["kind"], facility_code=r["facility_code"], duration_seconds=r["duration_seconds"], inputs=_json(r["inputs"]), outputs=_json(r["outputs"])) for r in rows]
@router.get("/warehouse", response_model=WarehouseResponse)
def warehouse(settlement_id: UUID, authenticated_player: UUID = Depends(get_authenticated_player)):
    with get_engine().connect() as conn:
        _owned_settlement(conn, authenticated_player, settlement_id); inv = _inventory(conn, authenticated_player)
        rows = conn.execute(text("SELECT i.item_definition_id,d.code,d.name,i.quantity,i.condition FROM inventory_items i JOIN item_definitions d ON d.id=i.item_definition_id WHERE i.inventory_id=:inv ORDER BY d.code"), {"inv": inv}).mappings().all()
        level = conn.execute(text("SELECT level FROM player_settlement_state WHERE settlement_id=:settlement AND owner_id=:player"), {"settlement": settlement_id, "player": authenticated_player}).scalar() or 1
    used = sum(int(r["quantity"]) for r in rows); capacity = 1000 + (int(level) - 1) * 500
    return WarehouseResponse(settlement_id=settlement_id, capacity=capacity, used=used, items=[WarehouseItem(item_definition_id=r["item_definition_id"], code=r["code"], name=r["name"], quantity=int(r["quantity"]), condition=int(r["condition"])) for r in rows])
@router.post("/jobs", response_model=JobResponse, status_code=201)
def start_job(payload: StartJobRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), authenticated_player: UUID = Depends(get_authenticated_player)):
    if not idempotency_key: raise ValueError("Idempotency-Key header is required")
    request_data = payload.model_dump(mode="json")
    with get_engine().begin() as conn:
        prior = conn.execute(text("SELECT * FROM economy_jobs WHERE owner_id=:owner AND idempotency_key=:key"), {"owner": authenticated_player, "key": idempotency_key}).mappings().first()
        if prior is not None:
            if request_hash({"recipe_id": str(prior["recipe_id"]), "settlement_id": str(prior["settlement_id"])}) != request_hash(request_data): raise ValueError("idempotency key belongs to a different economy job")
            return _job_response(prior)
        _owned_settlement(conn, authenticated_player, payload.settlement_id); recipe = _recipe(conn, payload.recipe_id); inv = _inventory(conn, authenticated_player)
        locked = []
        for entry in _json(recipe["inputs"]):
            item = conn.execute(text("SELECT i.id,i.item_definition_id,i.quantity FROM inventory_items i JOIN item_definitions d ON d.id=i.item_definition_id WHERE i.inventory_id=:inv AND d.code=:code FOR UPDATE"), {"inv": inv, "code": entry["item_code"]}).mappings().first(); qty = int(entry["quantity"])
            if item is None or int(item["quantity"]) < qty: raise ValueError(f"insufficient input: {entry['item_code']}")
            locked.append((item, qty))
        for item, qty in locked:
            remaining = int(item["quantity"]) - qty
            if remaining: conn.execute(text("UPDATE inventory_items SET quantity=:quantity,version=version+1 WHERE id=:id"), {"quantity": remaining, "id": item["id"]})
            else: conn.execute(text("DELETE FROM inventory_items WHERE id=:id"), {"id": item["id"]})
        now = datetime.now(timezone.utc)
        row = conn.execute(text("INSERT INTO economy_jobs(owner_id,settlement_id,recipe_id,state,started_at,completes_at,idempotency_key) VALUES(:owner,:settlement,:recipe,'running',:started,:complete,:key) RETURNING *"), {"owner": authenticated_player, "settlement": payload.settlement_id, "recipe": payload.recipe_id, "started": now, "complete": now + timedelta(seconds=int(recipe["duration_seconds"])), "key": idempotency_key}).mappings().one()
    return _job_response(row)
@router.post("/jobs/{job_id}/complete", response_model=JobResponse)
def complete_job(job_id: UUID, authenticated_player: UUID = Depends(get_authenticated_player)):
    with get_engine().begin() as conn:
        job = conn.execute(text("SELECT * FROM economy_jobs WHERE id=:id AND owner_id=:owner FOR UPDATE"), {"id": job_id, "owner": authenticated_player}).mappings().first()
        if job is None: raise ValueError("economy job not found")
        if job["state"] == "completed": return _job_response(job)
        if datetime.now(timezone.utc) < job["completes_at"]: raise ValueError("economy job is not due")
        recipe = _recipe(conn, job["recipe_id"]); inv = _inventory(conn, authenticated_player)
        for output in _json(recipe["outputs"]):
            item = conn.execute(text("SELECT id,stack_limit FROM item_definitions WHERE code=:code"), {"code": output["item_code"]}).mappings().one(); qty = int(output["quantity"])
            existing = conn.execute(text("SELECT quantity FROM inventory_items WHERE inventory_id=:inv AND item_definition_id=:item FOR UPDATE"), {"inv": inv, "item": item["id"]}).mappings().first()
            if existing is not None:
                if int(existing["quantity"]) + qty > int(item["stack_limit"]): raise ValueError("output would exceed inventory stack limit")
                conn.execute(text("UPDATE inventory_items SET quantity=quantity+:qty,version=version+1 WHERE inventory_id=:inv AND item_definition_id=:item"), {"qty": qty, "inv": inv, "item": item["id"]})
            else: conn.execute(text("INSERT INTO inventory_items(inventory_id,item_definition_id,quantity,condition) VALUES(:inv,:item,:qty,100)"), {"inv": inv, "item": item["id"], "qty": qty})
        row = conn.execute(text("UPDATE economy_jobs SET state='completed',completed_at=now() WHERE id=:id RETURNING *"), {"id": job_id}).mappings().one()
    return _job_response(row)
@router.get("/prices/{region_id}/{item_definition_id}", response_model=list[PricePoint])
def price_history(region_id: UUID, item_definition_id: UUID, limit: int = Query(default=50, ge=1, le=200), authenticated_player: UUID = Depends(get_authenticated_player)):
    with get_engine().connect() as conn: rows = conn.execute(text("SELECT recorded_at,quantity,unit_price,total_amount FROM market_price_history WHERE region_id=:region AND item_definition_id=:item ORDER BY recorded_at DESC LIMIT :limit"), {"region": region_id, "item": item_definition_id, "limit": limit}).mappings().all()
    return [PricePoint(recorded_at=r["recorded_at"].isoformat(), quantity=int(r["quantity"]), unit_price=int(r["unit_price"]), total_amount=int(r["total_amount"])) for r in rows]

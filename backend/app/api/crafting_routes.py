"""Authoritative crafting commands backed by persistent jobs."""
from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_engine
from app.api.idempotency import request_hash

router = APIRouter(prefix="/api/v1/crafting", tags=["crafting"])

class CraftRequest(BaseModel):
    recipe_id: UUID
    inventory_id: UUID

class CraftResponse(BaseModel):
    job_id: UUID
    recipe_id: UUID
    state: str
    started_at: str
    completes_at: str

class RecipeResponse(BaseModel):
    id: UUID
    code: str
    name: str
    duration_seconds: int
    ingredients: list[dict]
    outputs: list[dict]


def _inventory(conn, player_id: UUID, inventory_id: UUID):
    return conn.execute(text("SELECT id FROM inventories WHERE id=:id AND owner_id=:owner FOR UPDATE"), {"id": inventory_id, "owner": player_id}).mappings().first()


def _item(conn, code: str):
    return conn.execute(text("SELECT id, stack_limit FROM item_definitions WHERE code=:code"), {"code": code}).mappings().one()


def _recipe(conn, recipe_id: UUID):
    return conn.execute(text("SELECT id,code,name,duration_seconds,ingredients,outputs FROM crafting_recipes WHERE id=:id AND enabled=TRUE"), {"id": recipe_id}).mappings().one_or_none()


def _response(row):
    return CraftResponse(job_id=UUID(str(row["id"])), recipe_id=UUID(str(row["recipe_id"])), state=str(row["state"]), started_at=row["started_at"].isoformat(), completes_at=row["completes_at"].isoformat())

@router.get("/recipes", response_model=list[RecipeResponse])
def recipes(authenticated_player: UUID = Depends(get_authenticated_player)):
    with get_engine().connect() as conn:
        rows = conn.execute(text("SELECT id,code,name,duration_seconds,ingredients,outputs FROM crafting_recipes WHERE enabled=TRUE ORDER BY code")).mappings().all()
    return [RecipeResponse(id=UUID(str(r["id"])), code=r["code"], name=r["name"], duration_seconds=int(r["duration_seconds"]), ingredients=list(r["ingredients"]), outputs=list(r["outputs"])) for r in rows]

@router.post("/jobs", response_model=CraftResponse, status_code=201)
def craft(payload: CraftRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), authenticated_player: UUID = Depends(get_authenticated_player)):
    if not idempotency_key:
        raise ValueError("Idempotency-Key header is required")
    with get_engine().begin() as conn:
        existing = conn.execute(text("SELECT j.id,j.owner_id,j.job_type,j.state,j.started_at,j.completes_at, split_part(j.job_type, ':', 2)::uuid AS recipe_id FROM jobs j WHERE j.owner_id=:owner AND j.idempotency_key=:key"), {"owner": authenticated_player, "key": idempotency_key}).mappings().first()
        request_data = payload.model_dump(mode="json")
        if existing:
            stored = {"recipe_id": str(existing["recipe_id"]), "inventory_id": request_data["inventory_id"]}
            if request_hash(stored) != request_hash(request_data):
                raise ValueError("idempotency key belongs to a different crafting request")
            return _response(existing)
        recipe = _recipe(conn, payload.recipe_id)
        if recipe is None:
            raise ValueError("crafting recipe not found or disabled")
        inv = _inventory(conn, authenticated_player, payload.inventory_id)
        if inv is None:
            raise ValueError("inventory does not belong to session player")
        for ingredient in recipe["ingredients"]:
            item = _item(conn, ingredient["item_code"])
            stack = conn.execute(text("SELECT quantity FROM inventory_items WHERE inventory_id=:inv AND item_definition_id=:item FOR UPDATE"), {"inv": inv["id"], "item": item["id"]}).scalar()
            if stack is None or int(stack) < int(ingredient["quantity"]):
                raise ValueError(f"insufficient ingredient: {ingredient['item_code']}")
        for ingredient in recipe["ingredients"]:
            item = _item(conn, ingredient["item_code"])
            conn.execute(text("UPDATE inventory_items SET quantity=quantity-:qty, version=version+1 WHERE inventory_id=:inv AND item_definition_id=:item"), {"inv": inv["id"], "item": item["id"], "qty": ingredient["quantity"]})
            conn.execute(text("DELETE FROM inventory_items WHERE inventory_id=:inv AND item_definition_id=:item AND quantity=0"), {"inv": inv["id"], "item": item["id"]})
        from app.domain.primitives import utc_now
        started = utc_now()
        completed = started + timedelta(seconds=int(recipe["duration_seconds"]))
        row = conn.execute(text("INSERT INTO jobs (owner_id,job_type,state,started_at,completes_at,idempotency_key,version) VALUES (:owner,:type,'queued',:started,:completed,:key,1) RETURNING id,owner_id,job_type,state,started_at,completes_at"), {"owner": authenticated_player, "type": f"craft:{payload.recipe_id}", "started": started, "completed": completed, "key": idempotency_key}).mappings().one()
        conn.execute(text("INSERT INTO crafting_job_meta(job_id,recipe_id,inventory_id) VALUES (:job,:recipe,:inv)"), {"job": row["id"], "recipe": payload.recipe_id, "inv": payload.inventory_id})
        return _response({**dict(row), "recipe_id": payload.recipe_id})

@router.post("/jobs/{job_id}/complete", response_model=CraftResponse)
def complete(job_id: UUID, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), authenticated_player: UUID = Depends(get_authenticated_player)):
    if not idempotency_key:
        raise ValueError("Idempotency-Key header is required")
    with get_engine().begin() as conn:
        job = conn.execute(text("SELECT j.id,j.owner_id,j.state,j.started_at,j.completes_at,m.recipe_id,m.inventory_id FROM jobs j JOIN crafting_job_meta m ON m.job_id=j.id WHERE j.id=:id FOR UPDATE"), {"id": job_id}).mappings().one_or_none()
        if job is None or UUID(str(job["owner_id"])) != authenticated_player:
            raise ValueError("crafting job not found")
        if str(job["state"]) == "completed":
            return CraftResponse(job_id=job_id, recipe_id=UUID(str(job["recipe_id"])), state="completed", started_at=job["started_at"].isoformat(), completes_at=job["completes_at"].isoformat())
        if job["completes_at"] > __import__("datetime").datetime.now(__import__("datetime").timezone.utc):
            raise ValueError("crafting job completion time has not been reached")
        recipe = _recipe(conn, UUID(str(job["recipe_id"])))
        for output in recipe["outputs"]:
            item = _item(conn, output["item_code"])
            existing = conn.execute(text("SELECT quantity FROM inventory_items WHERE inventory_id=:inv AND item_definition_id=:item FOR UPDATE"), {"inv": job["inventory_id"], "item": item["id"]}).scalar()
            quantity = int(output["quantity"])
            if existing is not None and int(existing) + quantity > int(item["stack_limit"]):
                raise ValueError("crafting output exceeds inventory stack limit")
            conn.execute(text("INSERT INTO inventory_items(inventory_id,item_definition_id,quantity,condition) VALUES(:inv,:item,:qty,100) ON CONFLICT(inventory_id,item_definition_id) DO UPDATE SET quantity=inventory_items.quantity+:qty,version=inventory_items.version+1"), {"inv": job["inventory_id"], "item": item["id"], "qty": quantity})
        conn.execute(text("UPDATE jobs SET state='completed',version=version+1 WHERE id=:id"), {"id": job_id})
        return CraftResponse(job_id=job_id, recipe_id=UUID(str(job["recipe_id"])), state="completed", started_at=job["started_at"].isoformat(), completes_at=job["completes_at"].isoformat())

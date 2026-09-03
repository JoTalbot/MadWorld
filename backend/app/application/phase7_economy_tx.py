from __future__ import annotations
from datetime import timedelta
from uuid import UUID
from sqlalchemy import text
from app.api.idempotency import request_hash
from app.application.errors import IdempotencyConflict, NotFound
from app.domain.primitives import utc_now


def _owned(conn, table: str, entity_id: UUID, owner_id: UUID):
    row = conn.execute(text(f"SELECT * FROM {table} WHERE id=:id AND owner_id=:owner FOR UPDATE"), {"id": entity_id, "owner": owner_id}).mappings().first()
    if row is None:
        raise NotFound(f"{table} not found")
    return row


def _check_idempotency(existing, incoming: dict) -> None:
    if existing is None:
        return
    stored = {key: existing[key] for key in incoming}
    if request_hash(stored) != request_hash(incoming):
        raise IdempotencyConflict("idempotency key belongs to a different request")


def create_warehouse(conn, owner_id: UUID, region_id: UUID, name: str, capacity: int):
    if capacity <= 0:
        raise ValueError("warehouse capacity must be positive")
    return conn.execute(text("INSERT INTO warehouses(owner_id,region_id,name,capacity_units) VALUES(:o,:r,:n,:c) RETURNING *"), {"o":owner_id,"r":region_id,"n":name,"c":capacity}).mappings().one()


def create_facility(conn, owner_id: UUID, region_id: UUID, name: str, facility_type: str, capacity: int):
    if capacity <= 0:
        raise ValueError("facility capacity must be positive")
    return conn.execute(text("INSERT INTO production_facilities(owner_id,region_id,name,facility_type,capacity_units) VALUES(:o,:r,:n,:t,:c) RETURNING *"), {"o":owner_id,"r":region_id,"n":name,"t":facility_type,"c":capacity}).mappings().one()


def start_production(conn, owner_id: UUID, facility_id: UUID, recipe_id: UUID, batch: int, key: str):
    if batch <= 0:
        raise ValueError("batch_units must be positive")
    old = conn.execute(text("SELECT * FROM production_jobs WHERE owner_id=:o AND idempotency_key=:k"), {"o":owner_id,"k":key}).mappings().first()
    if old:
        _check_idempotency(old, {"facility_id": facility_id, "recipe_id": recipe_id, "batch_units": batch})
        return old
    facility = _owned(conn, "production_facilities", facility_id, owner_id)
    recipe = conn.execute(text("SELECT * FROM economy_recipes WHERE id=:id AND enabled=TRUE"), {"id":recipe_id}).mappings().first()
    if recipe is None:
        raise NotFound("economy recipe not found")
    if facility["facility_type"] != recipe["facility_code"]:
        raise ValueError("facility type cannot run this recipe")
    if batch > int(facility["capacity_units"]):
        raise ValueError("production batch exceeds facility capacity")
    warehouse = conn.execute(text("SELECT * FROM warehouses WHERE owner_id=:o AND region_id=:r ORDER BY created_at LIMIT 1 FOR UPDATE"), {"o":owner_id,"r":facility["region_id"]}).mappings().first()
    if warehouse is None:
        raise ValueError("an owned warehouse in the facility region is required")
    for x in recipe["inputs"]:
        item = conn.execute(text("SELECT id,mass_units FROM item_definitions WHERE code=:c"), {"c":x["item_code"]}).mappings().one()
        need = int(x["quantity"]) * batch
        stock = conn.execute(text("SELECT quantity FROM warehouse_items WHERE warehouse_id=:w AND item_definition_id=:i FOR UPDATE"), {"w":warehouse["id"],"i":item["id"]}).scalar()
        if stock is None or int(stock) < need:
            raise ValueError(f"insufficient production input: {x['item_code']}")
    for x in recipe["inputs"]:
        item = conn.execute(text("SELECT id,mass_units FROM item_definitions WHERE code=:c"), {"c":x["item_code"]}).mappings().one()
        need = int(x["quantity"]) * batch
        conn.execute(text("UPDATE warehouse_items SET quantity=quantity-:q WHERE warehouse_id=:w AND item_definition_id=:i"), {"q":need,"w":warehouse["id"],"i":item["id"]})
        conn.execute(text("DELETE FROM warehouse_items WHERE warehouse_id=:w AND item_definition_id=:i AND quantity=0"), {"w":warehouse["id"],"i":item["id"]})
        conn.execute(text("UPDATE warehouses SET used_units=used_units-:u,version=version+1 WHERE id=:w"), {"u":need*int(item["mass_units"]),"w":warehouse["id"]})
    started = utc_now()
    completed = started + timedelta(seconds=int(recipe["duration_seconds"]))
    return conn.execute(text("INSERT INTO production_jobs(owner_id,facility_id,recipe_id,batch_units,started_at,completes_at,idempotency_key) VALUES(:o,:f,:r,:b,:s,:d,:k) RETURNING *"), {"o":owner_id,"f":facility_id,"r":recipe_id,"b":batch,"s":started,"d":completed,"k":key}).mappings().one()


def complete_production(conn, owner_id: UUID, job_id: UUID):
    job = conn.execute(text("SELECT * FROM production_jobs WHERE id=:id AND owner_id=:o FOR UPDATE"), {"id":job_id,"o":owner_id}).mappings().first()
    if job is None:
        raise NotFound("production job not found")
    if job["state"] == "completed":
        return job
    if job["completes_at"] > utc_now():
        raise ValueError("production job completion time has not been reached")
    recipe = conn.execute(text("SELECT * FROM economy_recipes WHERE id=:id AND enabled=TRUE"), {"id":job["recipe_id"]}).mappings().one()
    facility = conn.execute(text("SELECT * FROM production_facilities WHERE id=:id AND owner_id=:o"), {"id":job["facility_id"],"o":owner_id}).mappings().one()
    warehouse = conn.execute(text("SELECT * FROM warehouses WHERE owner_id=:o AND region_id=:r ORDER BY created_at LIMIT 1 FOR UPDATE"), {"o":owner_id,"r":facility["region_id"]}).mappings().first()
    if warehouse is None:
        raise ValueError("destination warehouse is required")
    for x in recipe["outputs"]:
        item = conn.execute(text("SELECT mass_units FROM item_definitions WHERE code=:c"), {"c":x["item_code"]}).mappings().one()
        units = int(x["quantity"]) * int(job["batch_units"]) * int(item["mass_units"])
        if int(warehouse["used_units"]) + units > int(warehouse["capacity_units"]):
            raise ValueError("warehouse capacity exceeded by production output")
    for x in recipe["outputs"]:
        item = conn.execute(text("SELECT id,mass_units FROM item_definitions WHERE code=:c"), {"c":x["item_code"]}).mappings().one()
        quantity = int(x["quantity"]) * int(job["batch_units"])
        conn.execute(text("INSERT INTO warehouse_items(warehouse_id,item_definition_id,quantity) VALUES(:w,:i,:q) ON CONFLICT(warehouse_id,item_definition_id) DO UPDATE SET quantity=warehouse_items.quantity+:q"), {"w":warehouse["id"],"i":item["id"],"q":quantity})
        conn.execute(text("UPDATE warehouses SET used_units=used_units+:u,version=version+1 WHERE id=:w"), {"u":quantity*int(item["mass_units"]),"w":warehouse["id"]})
    return conn.execute(text("UPDATE production_jobs SET state='completed',completed_at=now(),version=version+1 WHERE id=:id RETURNING *"), {"id":job_id}).mappings().one()


def create_logistics(conn, owner_id: UUID, source_id: UUID, destination_id: UUID, item_id: UUID, quantity: int, reward: int, risk: int, key: str):
    if quantity <= 0 or reward < 0 or not 0 <= risk <= 10000:
        raise ValueError("invalid logistics contract values")
    old = conn.execute(text("SELECT * FROM logistics_contracts WHERE owner_id=:o AND idempotency_key=:k"), {"o":owner_id,"k":key}).mappings().first()
    incoming = {"source_warehouse_id": source_id, "destination_warehouse_id": destination_id, "item_definition_id": item_id, "quantity": quantity, "reward": reward, "route_risk_bps": risk}
    if old:
        _check_idempotency(old, incoming)
        return old
    if source_id == destination_id:
        raise ValueError("source and destination warehouses must differ")
    _owned(conn, "warehouses", source_id, owner_id)
    _owned(conn, "warehouses", destination_id, owner_id)
    item = conn.execute(text("SELECT mass_units FROM item_definitions WHERE id=:i"), {"i":item_id}).mappings().one()
    stock = conn.execute(text("SELECT quantity FROM warehouse_items WHERE warehouse_id=:w AND item_definition_id=:i FOR UPDATE"), {"w":source_id,"i":item_id}).scalar()
    if stock is None or int(stock) < quantity:
        raise ValueError("insufficient warehouse stock")
    units = quantity * int(item["mass_units"])
    conn.execute(text("UPDATE warehouse_items SET quantity=quantity-:q WHERE warehouse_id=:w AND item_definition_id=:i"), {"q":quantity,"w":source_id,"i":item_id})
    conn.execute(text("DELETE FROM warehouse_items WHERE warehouse_id=:w AND item_definition_id=:i AND quantity=0"), {"w":source_id,"i":item_id})
    conn.execute(text("UPDATE warehouses SET used_units=used_units-:u,version=version+1 WHERE id=:w"), {"u":units,"w":source_id})
    return conn.execute(text("INSERT INTO logistics_contracts(owner_id,source_warehouse_id,destination_warehouse_id,item_definition_id,quantity,reward,route_risk_bps,idempotency_key) VALUES(:o,:s,:d,:i,:q,:r,:risk,:k) RETURNING *"), {"o":owner_id,"s":source_id,"d":destination_id,"i":item_id,"q":quantity,"r":reward,"risk":risk,"k":key}).mappings().one()


def deliver_logistics(conn, owner_id: UUID, contract_id: UUID):
    contract = conn.execute(text("SELECT * FROM logistics_contracts WHERE id=:id AND owner_id=:o FOR UPDATE"), {"id":contract_id,"o":owner_id}).mappings().first()
    if contract is None:
        raise NotFound("logistics contract not found")
    if contract["state"] == "delivered":
        return contract
    if contract["state"] not in ("accepted","in_transit"):
        raise ValueError("logistics contract cannot be delivered")
    destination = _owned(conn, "warehouses", contract["destination_warehouse_id"], owner_id)
    item = conn.execute(text("SELECT mass_units FROM item_definitions WHERE id=:i"), {"i":contract["item_definition_id"]}).mappings().one()
    units = int(contract["quantity"]) * int(item["mass_units"])
    if int(destination["used_units"]) + units > int(destination["capacity_units"]):
        raise ValueError("destination warehouse capacity exceeded")
    conn.execute(text("INSERT INTO warehouse_items(warehouse_id,item_definition_id,quantity) VALUES(:w,:i,:q) ON CONFLICT(warehouse_id,item_definition_id) DO UPDATE SET quantity=warehouse_items.quantity+:q"), {"w":destination["id"],"i":contract["item_definition_id"],"q":contract["quantity"]})
    conn.execute(text("UPDATE warehouses SET used_units=used_units+:u,version=version+1 WHERE id=:w"), {"u":units,"w":destination["id"]})
    if int(contract["reward"]) > 0:
        wallet = conn.execute(text("SELECT id FROM wallets WHERE owner_id=:o FOR UPDATE"), {"o":owner_id}).mappings().one()
        conn.execute(text("INSERT INTO ledger_entries(wallet_id,amount,reason,actor_id,idempotency_key) VALUES(:w,:a,'logistics_reward',:o,:k) ON CONFLICT(idempotency_key) DO NOTHING"), {"w":wallet["id"],"a":contract["reward"],"o":owner_id,"k":f"logistics-reward:{contract_id}"})
    return conn.execute(text("UPDATE logistics_contracts SET state='delivered',delivered_at=now(),version=version+1 WHERE id=:id RETURNING *"), {"id":contract_id}).mappings().one()

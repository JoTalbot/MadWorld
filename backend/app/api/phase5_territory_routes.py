"""Authoritative Phase 5 territory commands and state queries."""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_uow
from app.api.idempotency import replay_or_none, require_key, store_response
from app.application.ports import UnitOfWork

router = APIRouter(prefix="/api/v1/territory", tags=["territory"])

class ClaimRequest(BaseModel):
    corporation_id: UUID
    region_id: str = Field(min_length=1,max_length=64)
    target_type: str = Field(min_length=1,max_length=64)
    target_id: str = Field(min_length=1,max_length=128)
    expected_version: int = Field(default=0,ge=0)

class InfrastructureRequest(BaseModel):
    corporation_id: UUID
    region_id: str = Field(min_length=1,max_length=64)
    infrastructure_type: str = Field(min_length=1,max_length=64)
    name: str = Field(min_length=1,max_length=128)
    settlement_id: UUID|None = None
    upkeep_bps: int = Field(default=0,ge=0,le=10000)

class RoadRequest(BaseModel):
    corporation_id: UUID
    region_id: str
    from_node: str = Field(min_length=1,max_length=128)
    to_node: str = Field(min_length=1,max_length=128)
    travel_modifier_bps: int = Field(default=0,ge=-5000,le=5000)
    risk_modifier_bps: int = Field(default=0,ge=-5000,le=5000)

class ResourceSiteRequest(BaseModel):
    corporation_id: UUID
    region_id: str
    resource_type: str = Field(min_length=1,max_length=64)
    name: str = Field(min_length=1,max_length=128)
    capacity: int = Field(gt=0,le=10_000_000)
    extraction_limit: int = Field(default=100,gt=0,le=1_000_000)
    renewal_rate: int = Field(default=0,ge=0,le=1_000_000)

class ObjectiveRequest(BaseModel):
    corporation_id: UUID
    region_id: str
    target_type: str
    target_id: str
    opens_at: datetime
    contest_ends_at: datetime

class ResolveObjectiveRequest(BaseModel):
    corporation_id: UUID
    winner_corporation_id: UUID|None = None


def _member(uow: UnitOfWork, corp: UUID, player: UUID) -> bool:
    return uow.conn.execute(text("SELECT 1 FROM corporation_members WHERE corporation_id=:c AND player_id=:p"),{"c":corp,"p":player}).first() is not None

def _event(uow: UnitOfWork, region: str, kind: str, aggregate: UUID, actor: UUID|None, payload: dict) -> None:
    uow.conn.execute(text("INSERT INTO territory_events(region_id,event_type,aggregate_type,aggregate_id,actor_corporation_id,payload) VALUES (:r,:e,'territory',:a,:c,CAST(:p AS JSONB))"),{"r":region,"e":kind,"a":aggregate,"c":actor,"p":__import__('json').dumps(payload)})
    uow.audit.append(kind,"territory",aggregate,payload)
    uow.outbox.enqueue(kind,"territory",aggregate,payload)

def _authorized(uow: UnitOfWork, corp: UUID, player: UUID) -> None:
    if not _member(uow,corp,player): raise HTTPException(403,"corporation membership required")

@router.get("")
def territory_state(player: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow)):
    regions=uow.conn.execute(text("SELECT id,name,security,version FROM world_regions ORDER BY id")).mappings().all()
    claims=uow.conn.execute(text("SELECT id,region_id,target_type,target_id,claimant_corporation_id,state,version FROM territory_claims ORDER BY region_id,target_type,target_id")).mappings().all()
    control=uow.conn.execute(text("SELECT region_id,target_type,target_id,controller_corporation_id,controlled_since,version FROM territory_control ORDER BY region_id,target_type,target_id")).mappings().all()
    roads=uow.conn.execute(text("SELECT id,region_id,from_node,to_node,controller_corporation_id,travel_modifier_bps,risk_modifier_bps,version FROM territory_roads ORDER BY region_id,from_node,to_node")).mappings().all()
    resources=uow.conn.execute(text("SELECT id,region_id,resource_type,name,controller_corporation_id,capacity,remaining,renewal_rate,extraction_limit,version FROM territory_resource_sites ORDER BY region_id,name")).mappings().all()
    return {"authoritative":True,"regions":[dict(x) for x in regions],"claims":[dict(x) for x in claims],"control":[dict(x) for x in control],"roads":[dict(x) for x in roads],"resource_sites":[dict(x) for x in resources]}

@router.post("/claims",status_code=201)
def claim(payload: ClaimRequest,player: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow),idempotency_key: str|None=Header(default=None,alias="Idempotency-Key")):
    key=require_key(idempotency_key); body=payload.model_dump(); replay=replay_or_none(uow,"territory.claim",key,body)
    if replay is not None:return replay
    _authorized(uow,payload.corporation_id,player)
    if uow.conn.execute(text("SELECT 1 FROM world_regions WHERE id=:r"),{"r":payload.region_id}).first() is None: raise HTTPException(404,"region not found")
    row=uow.conn.execute(text("SELECT id,version,claimant_corporation_id,state FROM territory_claims WHERE region_id=:r AND target_type=:t AND target_id=:id FOR UPDATE"),{"r":payload.region_id,"t":payload.target_type,"id":payload.target_id}).mappings().first()
    if row and row["claimant_corporation_id"] != payload.corporation_id and row["state"] != "RELEASED": raise HTTPException(409,"territorial target is already claimed")
    if row and int(row["version"]) != payload.expected_version: raise HTTPException(409,"stale territory claim version")
    claim_id=UUID(str(row["id"])) if row else uuid4()
    if row:
        uow.conn.execute(text("UPDATE territory_claims SET claimant_corporation_id=:c,state='ACTIVE',version=version+1 WHERE id=:id AND version=:v"),{"c":payload.corporation_id,"id":claim_id,"v":payload.expected_version})
    else:
        uow.conn.execute(text("INSERT INTO territory_claims(id,region_id,target_type,target_id,claimant_corporation_id,state,version) VALUES (:id,:r,:t,:tid,:c,'ACTIVE',0)"),{"id":claim_id,"r":payload.region_id,"t":payload.target_type,"tid":payload.target_id,"c":payload.corporation_id})
    control=uow.conn.execute(text("SELECT id,version FROM territory_control WHERE region_id=:r AND target_type=:t AND target_id=:id FOR UPDATE"),{"r":payload.region_id,"t":payload.target_type,"id":payload.target_id}).mappings().first()
    if control is None:
        uow.conn.execute(text("INSERT INTO territory_control(region_id,target_type,target_id,controller_corporation_id,controlled_since,version) VALUES (:r,:t,:id,:c,now(),0)"),{"r":payload.region_id,"t":payload.target_type,"id":payload.target_id,"c":payload.corporation_id})
        uow.conn.execute(text("INSERT INTO territory_control_history(region_id,target_type,target_id,new_controller,reason) VALUES (:r,:t,:id,:c,'claim')"),{"r":payload.region_id,"t":payload.target_type,"id":payload.target_id,"c":payload.corporation_id})
    else:
        uow.conn.execute(text("UPDATE territory_control SET controller_corporation_id=:c,controlled_since=now(),version=version+1 WHERE id=:id"),{"c":payload.corporation_id,"id":control["id"]})
        uow.conn.execute(text("INSERT INTO territory_control_history(region_id,target_type,target_id,new_controller,reason) VALUES (:r,:t,:id,:c,'claim')"),{"r":payload.region_id,"t":payload.target_type,"id":payload.target_id,"c":payload.corporation_id})
    result={"ok":True,"claim_id":str(claim_id),"controller_corporation_id":str(payload.corporation_id),"region_id":payload.region_id,"target_type":payload.target_type,"target_id":payload.target_id}
    _event(uow,payload.region_id,"territory.claimed",claim_id,payload.corporation_id,result);store_response(uow,"territory.claim",key,body,result,201,player);return result

@router.post("/infrastructure",status_code=201)
def create_infrastructure(payload: InfrastructureRequest,player: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow),idempotency_key: str|None=Header(default=None,alias="Idempotency-Key")):
    key=require_key(idempotency_key);body=payload.model_dump();replay=replay_or_none(uow,"territory.infrastructure",key,body)
    if replay is not None:return replay
    _authorized(uow,payload.corporation_id,player); iid=uuid4()
    try:uow.conn.execute(text("INSERT INTO territory_infrastructure(id,region_id,settlement_id,infrastructure_type,name,controller_corporation_id,upkeep_bps) VALUES (:id,:r,:s,:t,:n,:c,:u)"),{"id":iid,"r":payload.region_id,"s":payload.settlement_id,"t":payload.infrastructure_type,"n":payload.name.strip(),"c":payload.corporation_id,"u":payload.upkeep_bps})
    except Exception as exc:raise HTTPException(409,"infrastructure already exists") from exc
    result={"ok":True,"infrastructure_id":str(iid),"controller_corporation_id":str(payload.corporation_id)};_event(uow,payload.region_id,"territory.infrastructure_created",iid,payload.corporation_id,result);store_response(uow,"territory.infrastructure",key,body,result,201,player);return result

@router.post("/roads",status_code=201)
def create_road(payload: RoadRequest,player: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow),idempotency_key: str|None=Header(default=None,alias="Idempotency-Key")):
    key=require_key(idempotency_key);body=payload.model_dump();replay=replay_or_none(uow,"territory.road",key,body)
    if replay is not None:return replay
    _authorized(uow,payload.corporation_id,player);rid=uuid4()
    try:uow.conn.execute(text("INSERT INTO territory_roads(id,region_id,from_node,to_node,controller_corporation_id,travel_modifier_bps,risk_modifier_bps) VALUES (:id,:r,:f,:t,:c,:tm,:rm)"),{"id":rid,"r":payload.region_id,"f":payload.from_node,"t":payload.to_node,"c":payload.corporation_id,"tm":payload.travel_modifier_bps,"rm":payload.risk_modifier_bps})
    except Exception as exc:raise HTTPException(409,"road segment already exists") from exc
    result={"ok":True,"road_id":str(rid),"controller_corporation_id":str(payload.corporation_id)};_event(uow,payload.region_id,"territory.road_controlled",rid,payload.corporation_id,result);store_response(uow,"territory.road",key,body,result,201,player);return result

@router.post("/resource-sites",status_code=201)
def create_resource_site(payload: ResourceSiteRequest,player: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow),idempotency_key: str|None=Header(default=None,alias="Idempotency-Key")):
    key=require_key(idempotency_key);body=payload.model_dump();replay=replay_or_none(uow,"territory.resource_site",key,body)
    if replay is not None:return replay
    _authorized(uow,payload.corporation_id,player);rid=uuid4()
    try:uow.conn.execute(text("INSERT INTO territory_resource_sites(id,region_id,resource_type,name,controller_corporation_id,capacity,remaining,renewal_rate,extraction_limit) VALUES (:id,:r,:t,:n,:c,:cap,:cap,:rr,:el)"),{"id":rid,"r":payload.region_id,"t":payload.resource_type,"n":payload.name.strip(),"c":payload.corporation_id,"cap":payload.capacity,"rr":payload.renewal_rate,"el":payload.extraction_limit})
    except Exception as exc:raise HTTPException(409,"resource site already exists") from exc
    result={"ok":True,"resource_site_id":str(rid),"remaining":payload.capacity,"controller_corporation_id":str(payload.corporation_id)};_event(uow,payload.region_id,"territory.resource_site_created",rid,payload.corporation_id,result);store_response(uow,"territory.resource_site",key,body,result,201,player);return result

@router.post("/resource-sites/{site_id}/extract")
def extract(site_id: UUID,amount: int=1,player: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow),idempotency_key: str|None=Header(default=None,alias="Idempotency-Key")):
    key=require_key(idempotency_key);body={"site_id":str(site_id),"amount":amount};replay=replay_or_none(uow,"territory.extract",key,body)
    if replay is not None:return replay
    if amount<=0:raise HTTPException(400,"amount must be positive")
    row=uow.conn.execute(text("SELECT region_id,controller_corporation_id,remaining,extraction_limit,version FROM territory_resource_sites WHERE id=:id FOR UPDATE"),{"id":site_id}).mappings().first()
    if not row:raise HTTPException(404,"resource site not found")
    if row["controller_corporation_id"] is None or not _member(uow,UUID(str(row["controller_corporation_id"])),player):raise HTTPException(403,"resource site controller membership required")
    actual=min(amount,int(row["extraction_limit"]),int(row["remaining"]))
    if actual<=0:raise HTTPException(409,"resource site is depleted")
    uow.conn.execute(text("UPDATE territory_resource_sites SET remaining=remaining-:a,version=version+1 WHERE id=:id AND version=:v"),{"a":actual,"id":site_id,"v":row["version"]})
    result={"ok":True,"resource_site_id":str(site_id),"extracted":actual,"remaining":int(row["remaining"])-actual};_event(uow,str(row["region_id"]),"territory.resource_extracted",site_id,UUID(str(row["controller_corporation_id"])),result);store_response(uow,"territory.extract",key,body,result,200,player);return result

@router.post("/objectives",status_code=201)
def create_objective(payload: ObjectiveRequest,player: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow),idempotency_key: str|None=Header(default=None,alias="Idempotency-Key")):
    key=require_key(idempotency_key);body=payload.model_dump(mode="json");replay=replay_or_none(uow,"territory.objective",key,body)
    if replay is not None:return replay
    _authorized(uow,payload.corporation_id,player)
    if payload.contest_ends_at<=payload.opens_at:raise HTTPException(400,"contest_ends_at must be after opens_at")
    oid=uuid4();uow.conn.execute(text("INSERT INTO territory_objectives(id,region_id,target_type,target_id,state,opens_at,contest_ends_at) VALUES (:id,:r,:t,:tid,CASE WHEN :o<=now() THEN 'OPEN' ELSE 'SCHEDULED' END,:o,:e)"),{"id":oid,"r":payload.region_id,"t":payload.target_type,"tid":payload.target_id,"o":payload.opens_at,"e":payload.contest_ends_at})
    result={"ok":True,"objective_id":str(oid),"state":"OPEN" if payload.opens_at<=datetime.now(UTC) else "SCHEDULED"};_event(uow,payload.region_id,"territory.objective_created",oid,payload.corporation_id,result);store_response(uow,"territory.objective",key,body,result,201,player);return result

@router.post("/objectives/{objective_id}/resolve")
def resolve_objective(objective_id: UUID,payload: ResolveObjectiveRequest,player: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow),idempotency_key: str|None=Header(default=None,alias="Idempotency-Key")):
    key=require_key(idempotency_key);body={**payload.model_dump(mode="json"),"objective_id":str(objective_id)};replay=replay_or_none(uow,"territory.objective.resolve",key,body)
    if replay is not None:return replay
    _authorized(uow,payload.corporation_id,player);row=uow.conn.execute(text("SELECT region_id,state,contest_ends_at,target_type,target_id FROM territory_objectives WHERE id=:id FOR UPDATE"),{"id":objective_id}).mappings().first()
    if not row:raise HTTPException(404,"objective not found")
    if row["state"] not in ("OPEN","CONTESTED"):raise HTTPException(409,"objective is not resolvable in current state")
    now=datetime.now(UTC)
    if now<row["contest_ends_at"]:raise HTTPException(409,"objective contest window is still open")
    uow.conn.execute(text("UPDATE territory_objectives SET state='RESOLVED',resolved_at=now(),winner_corporation_id=:w,version=version+1 WHERE id=:id"),{"w":payload.winner_corporation_id,"id":objective_id})
    result={"ok":True,"objective_id":str(objective_id),"state":"RESOLVED","winner_corporation_id":str(payload.winner_corporation_id) if payload.winner_corporation_id else None};_event(uow,str(row["region_id"]),"territory.objective_resolved",objective_id,payload.corporation_id,result);store_response(uow,"territory.objective.resolve",key,body,result,200,player);return result

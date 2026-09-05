"""Authoritative Phase 4 social-sandbox commands."""
from __future__ import annotations

import json
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_uow
from app.application.phase4_operations import Phase4Operations
from app.application.phase4_social import PERMISSIONS, SocialPolicy
from app.application.ports import UnitOfWork

router = APIRouter(prefix="/api/v1/social", tags=["social"])
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "LEADER": set(PERMISSIONS),
    "DIRECTOR": {"MANAGE_MEMBERS","MANAGE_ROLES","MANAGE_WALLET","MANAGE_HANGAR","MANAGE_ASSETS","TRADE","COMMAND_FLEET","RECRUIT","CREATE_CONTRACTS"},
    "QUARTERMASTER": {"MANAGE_WALLET","MANAGE_HANGAR","MANAGE_ASSETS"}, "TRADER": {"TRADE","CREATE_CONTRACTS"},
    "FLEET_COMMANDER": {"COMMAND_FLEET","MANAGE_HANGAR"}, "RECRUITER": {"RECRUIT","MANAGE_MEMBERS"},
    "DIPLOMAT": {"DIPLOMACY","CREATE_CONTRACTS"}, "MECHANIC": {"MANAGE_HANGAR","MANAGE_ASSETS"}, "MEMBER": set(),
}
class CorporationCreate(BaseModel):
    code: str = Field(min_length=2,max_length=32); name: str = Field(min_length=2,max_length=80); tax_bps: int = Field(default=0,ge=0,le=10000)
class MemberChange(BaseModel): corporation_id: UUID; player_id: UUID; role: str = "MEMBER"
class RoleChange(BaseModel): corporation_id: UUID; player_id: UUID; role: str
class DiplomacyChange(BaseModel):
    source_corporation_id: UUID; target_corporation_id: UUID; relation: str; standing: int = Field(default=0,ge=-10000,le=10000); trade_allowed: bool=True; transit_allowed: bool=False
class ContractCreate(BaseModel):
    issuer_corporation_id: UUID; contract_type: str = Field(min_length=1,max_length=64); terms: dict[str,Any] = Field(default_factory=dict); counterparty_corporation_id: UUID|None=None; counterparty_player_id: UUID|None=None
class HangarCreate(BaseModel): corporation_id: UUID; name: str = Field(min_length=1,max_length=64); capacity: int = Field(gt=0,le=10000)
class ContractTransitionRequest(BaseModel): contract_id: UUID; new_state: str
class ReputationChange(BaseModel):
    target_type: str = Field(min_length=1,max_length=64); target_id: str = Field(min_length=1,max_length=128); delta: int = Field(ge=-10000,le=10000); reason: str = Field(min_length=1,max_length=256); subject_player_id: UUID|None=None; subject_corporation_id: UUID|None=None

def _member_role(uow: UnitOfWork,c: UUID,p: UUID)->str|None:
    row=uow.conn.execute(text("SELECT role FROM corporation_members WHERE corporation_id=:c AND player_id=:p"),{"c":c,"p":p}).first(); return str(row[0]) if row else None

def _require_permission(uow: UnitOfWork,c: UUID,p: UUID,perm: str)->str:
    role=_member_role(uow,c,p)
    if role is None or perm not in ROLE_PERMISSIONS.get(role,set()): raise HTTPException(403,f"corporation permission required: {perm}")
    return role

def _require_corp(uow: UnitOfWork,c: UUID)->None:
    if uow.conn.execute(text("SELECT 1 FROM corporations WHERE id=:id"),{"id":c}).first() is None: raise HTTPException(404,"corporation not found")

@router.get("/capabilities")
def capabilities(_: UUID=Depends(get_authenticated_player)):
    return {"systems":["corporations","roles","shared_wallets","shared_hangars","alliances","diplomacy","social_contracts","reputation","manufacturers"],"authoritative":True}

@router.post("/corporations",status_code=201)
def create_corporation(payload: CorporationCreate,player_id: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow),idempotency_key: str|None=Header(default=None,alias="Idempotency-Key")):
    if not idempotency_key: raise HTTPException(400,"Idempotency-Key is required")
    if uow.conn.execute(text("SELECT 1 FROM corporation_members WHERE player_id=:p"),{"p":player_id}).first(): raise HTTPException(409,"player already belongs to a corporation")
    corporation=SocialPolicy.create_corporation(player_id,payload.code,payload.name,payload.tax_bps); wallet_id=uuid4()
    try:
        uow.conn.execute(text("INSERT INTO wallets (id,version) VALUES (:id,0)"),{"id":wallet_id})
        uow.conn.execute(text("INSERT INTO corporations (id,owner_id,code,name,tax_bps,wallet_id,version) VALUES (:id,:owner,:code,:name,:tax,:wallet,0)"),{"id":corporation.id,"owner":player_id,"code":corporation.code,"name":corporation.name,"tax":corporation.tax_bps,"wallet":wallet_id})
        uow.conn.execute(text("INSERT INTO corporation_members (corporation_id,player_id,role,version) VALUES (:c,:p,'LEADER',0)"),{"c":corporation.id,"p":player_id})
        uow.audit.append("corporation.created","corporation",corporation.id,{"actor_id":str(player_id),"code":corporation.code}); uow.outbox.enqueue("corporation.created","corporation",corporation.id,{"owner_id":str(player_id),"wallet_id":str(wallet_id)})
    except Exception as exc: raise HTTPException(409,"corporation code is already in use") from exc
    return {"ok":True,"corporation_id":str(corporation.id),"wallet_id":str(wallet_id),"owner_id":str(player_id),"role":"LEADER"}

@router.post("/members")
def add_member(payload: MemberChange,player_id: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow)):
    _require_permission(uow,payload.corporation_id,player_id,"MANAGE_MEMBERS"); SocialPolicy.create_member(payload.corporation_id,payload.player_id,payload.role)
    try: uow.conn.execute(text("INSERT INTO corporation_members (corporation_id,player_id,role,version) VALUES (:c,:p,:r,0)"),{"c":payload.corporation_id,"p":payload.player_id,"r":payload.role})
    except Exception as exc: raise HTTPException(409,"player is already a corporation member") from exc
    uow.audit.append("corporation.member_added","corporation",payload.corporation_id,{"actor_id":str(player_id),"player_id":str(payload.player_id),"role":payload.role}); return {"ok":True}

@router.post("/members/role")
def change_role(payload: RoleChange,player_id: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow)):
    _require_permission(uow,payload.corporation_id,player_id,"MANAGE_ROLES"); SocialPolicy.validate_role(payload.role)
    old=_member_role(uow,payload.corporation_id,payload.player_id)
    if old is None: raise HTTPException(404,"corporation member not found")
    if payload.player_id==player_id and payload.role!="LEADER": raise HTTPException(409,"leader cannot demote itself")
    uow.conn.execute(text("UPDATE corporation_members SET role=:r,version=version+1 WHERE corporation_id=:c AND player_id=:p"),{"r":payload.role,"c":payload.corporation_id,"p":payload.player_id}); uow.audit.append("corporation.member_role_changed","corporation",payload.corporation_id,{"actor_id":str(player_id),"player_id":str(payload.player_id),"from":old,"to":payload.role}); return {"ok":True,"role":payload.role}

@router.post("/hangars",status_code=201)
def create_hangar(payload: HangarCreate,player_id: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow)):
    _require_permission(uow,payload.corporation_id,player_id,"MANAGE_HANGAR"); _require_corp(uow,payload.corporation_id); hid=uuid4()
    try: uow.conn.execute(text("INSERT INTO corporation_hangars (id,corporation_id,name,capacity,version) VALUES (:id,:c,:n,:cap,0)"),{"id":hid,"c":payload.corporation_id,"n":payload.name.strip(),"cap":payload.capacity})
    except Exception as exc: raise HTTPException(409,"hangar name is already in use") from exc
    uow.audit.append("corporation.hangar_created","corporation",payload.corporation_id,{"actor_id":str(player_id),"hangar_id":str(hid)}); return {"ok":True,"hangar_id":str(hid),"capacity":payload.capacity}

@router.post("/diplomacy")
def set_diplomacy(payload: DiplomacyChange,player_id: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow)):
    _require_permission(uow,payload.source_corporation_id,player_id,"DIPLOMACY"); _require_corp(uow,payload.target_corporation_id); r=SocialPolicy.set_diplomacy(payload.source_corporation_id,payload.target_corporation_id,payload.relation,payload.standing,payload.trade_allowed,payload.transit_allowed)
    uow.conn.execute(text("""INSERT INTO diplomatic_relations (id,source_corporation_id,target_corporation_id,relation,standing,trade_allowed,transit_allowed,version) VALUES (:id,:s,:t,:r,:st,:tr,:ti,0) ON CONFLICT (source_corporation_id,target_corporation_id) DO UPDATE SET relation=EXCLUDED.relation,standing=EXCLUDED.standing,trade_allowed=EXCLUDED.trade_allowed,transit_allowed=EXCLUDED.transit_allowed,version=diplomatic_relations.version+1"""),{"id":uuid4(),"s":r.source_corporation_id,"t":r.target_corporation_id,"r":r.relation,"st":r.standing,"tr":r.trade_allowed,"ti":r.transit_allowed}); uow.audit.append("diplomacy.changed","corporation",payload.source_corporation_id,{"actor_id":str(player_id),"target":str(payload.target_corporation_id),"relation":r.relation}); return {"ok":True,"relation":r.relation,"standing":r.standing,"trade_allowed":r.trade_allowed,"transit_allowed":r.transit_allowed}

@router.post("/contracts",status_code=201)
def create_contract(payload: ContractCreate,player_id: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow)):
    _require_permission(uow,payload.issuer_corporation_id,player_id,"CREATE_CONTRACTS"); c=SocialPolicy.create_contract(payload.issuer_corporation_id,payload.contract_type,payload.terms,payload.counterparty_corporation_id,payload.counterparty_player_id)
    uow.conn.execute(text("INSERT INTO social_contracts (id,issuer_corporation_id,counterparty_corporation_id,counterparty_player_id,contract_type,terms,state,version) VALUES (:id,:i,:cc,:cp,:t,CAST(:terms AS JSONB),'OFFERED',0)"),{"id":c.id,"i":c.issuer_corporation_id,"cc":c.counterparty_corporation_id,"cp":c.counterparty_player_id,"t":c.contract_type,"terms":json.dumps(c.terms)}); uow.audit.append("social_contract.created","social_contract",c.id,{"actor_id":str(player_id)}); return {"ok":True,"contract_id":str(c.id),"state":"OFFERED"}

@router.post("/contracts/transition")
def transition_contract(payload: ContractTransitionRequest,player_id: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow)):
    row=uow.conn.execute(text("SELECT issuer_corporation_id,counterparty_corporation_id,counterparty_player_id,state,version FROM social_contracts WHERE id=:id FOR UPDATE"),{"id":payload.contract_id}).mappings().first()
    if not row: raise HTTPException(404,"social contract not found")
    issuer=UUID(str(row["issuer_corporation_id"]))
    if _member_role(uow,issuer,player_id) is None and not (row["counterparty_player_id"] and UUID(str(row["counterparty_player_id"]))==player_id): raise HTTPException(403,"contract participant required")
    Phase4Operations.transition_contract(str(row["state"]),payload.new_state)
    uow.conn.execute(text("UPDATE social_contracts SET state=:state,version=version+1 WHERE id=:id AND version=:v"),{"state":payload.new_state,"id":payload.contract_id,"v":row["version"]}); uow.audit.append("social_contract.transitioned","social_contract",payload.contract_id,{"actor_id":str(player_id),"state":payload.new_state}); return {"ok":True,"state":payload.new_state}

@router.post("/reputation")
def change_reputation(payload: ReputationChange,player_id: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow)):
    subject_corp=payload.subject_corporation_id or None
    if subject_corp: _require_permission(uow,subject_corp,player_id,"MANAGE_MEMBERS")
    elif payload.subject_player_id!=player_id: raise HTTPException(403,"player reputation may only be changed by the player or a future trusted system actor")
    r=__import__('app.application.phase4_operations',fromlist=['Phase4Operations']).Phase4Operations.reputation_delta(payload.subject_player_id,subject_corp,payload.target_type,payload.target_id,payload.delta,payload.reason)
    if subject_corp:
        row=uow.conn.execute(text("SELECT id,standing,version FROM social_reputation WHERE subject_corporation_id=:c AND target_type=:t AND target_id=:id FOR UPDATE"),{"c":subject_corp,"t":r.target_type,"id":r.target_id}).mappings().first()
    else:
        row=uow.conn.execute(text("SELECT id,standing,version FROM social_reputation WHERE subject_player_id=:p AND target_type=:t AND target_id=:id FOR UPDATE"),{"p":r.subject_player_id,"t":r.target_type,"id":r.target_id}).mappings().first()
    new=max(-10000,min(10000,(int(row["standing"]) if row else 0)+r.delta)); rid=row["id"] if row else uuid4()
    if row: uow.conn.execute(text("UPDATE social_reputation SET standing=:s,version=version+1 WHERE id=:id AND version=:v"),{"s":new,"id":rid,"v":row["version"]})
    else: uow.conn.execute(text("INSERT INTO social_reputation (id,subject_player_id,subject_corporation_id,target_type,target_id,standing,version) VALUES (:id,:p,:c,:t,:tid,:s,0)"),{"id":rid,"p":r.subject_player_id,"c":subject_corp,"t":r.target_type,"tid":r.target_id,"s":new})
    uow.conn.execute(text("INSERT INTO social_reputation_history (id,subject_player_id,subject_corporation_id,target_type,target_id,delta,reason,actor_id) VALUES (:id,:p,:c,:t,:tid,:d,:reason,:actor)"),{"id":uuid4(),"p":r.subject_player_id,"c":subject_corp,"t":r.target_type,"tid":r.target_id,"d":r.delta,"reason":r.reason,"actor":player_id}); uow.audit.append("reputation.changed","reputation",rid,{"actor_id":str(player_id),"delta":r.delta,"standing":new}); return {"ok":True,"standing":new}

@router.get("/overview/{corporation_id}")
def corporation_overview(corporation_id: UUID,player_id: UUID=Depends(get_authenticated_player),uow: UnitOfWork=Depends(get_uow)):
    _require_corp(uow,corporation_id); role=_member_role(uow,corporation_id,player_id)
    if role is None: raise HTTPException(403,"corporation membership required")
    corp=uow.conn.execute(text("SELECT id,code,name,tax_bps,wallet_id,status,version FROM corporations WHERE id=:id"),{"id":corporation_id}).mappings().first(); members=uow.conn.execute(text("SELECT player_id,role,joined_at FROM corporation_members WHERE corporation_id=:id ORDER BY joined_at,player_id"),{"id":corporation_id}).mappings().all(); hangars=uow.conn.execute(text("SELECT id,name,capacity,version FROM corporation_hangars WHERE corporation_id=:id ORDER BY name"),{"id":corporation_id}).mappings().all()
    return {"corporation":dict(corp),"viewer_role":role,"members":[dict(x) for x in members],"hangars":[dict(x) for x in hangars]}

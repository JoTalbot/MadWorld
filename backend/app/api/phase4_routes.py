"""Authoritative Phase 4 social-sandbox commands.

All mutations run inside the existing request UnitOfWork transaction.  The API
therefore stops being a validation-only facade and becomes the server authority
for the first social gameplay loop.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_uow
from app.application.ports import UnitOfWork
from app.application.phase4_social import PERMISSIONS, SocialPolicy

router = APIRouter(prefix="/api/v1/social", tags=["social"])

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "LEADER": set(PERMISSIONS),
    "DIRECTOR": {"MANAGE_MEMBERS", "MANAGE_ROLES", "MANAGE_WALLET", "MANAGE_HANGAR", "MANAGE_ASSETS", "TRADE", "COMMAND_FLEET", "RECRUIT", "CREATE_CONTRACTS"},
    "QUARTERMASTER": {"MANAGE_WALLET", "MANAGE_HANGAR", "MANAGE_ASSETS"},
    "TRADER": {"TRADE", "CREATE_CONTRACTS"},
    "FLEET_COMMANDER": {"COMMAND_FLEET", "MANAGE_HANGAR"},
    "RECRUITER": {"RECRUIT", "MANAGE_MEMBERS"},
    "DIPLOMAT": {"DIPLOMACY", "CREATE_CONTRACTS"},
    "MECHANIC": {"MANAGE_HANGAR", "MANAGE_ASSETS"},
    "MEMBER": set(),
}

class CorporationCreate(BaseModel):
    code: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=2, max_length=80)
    tax_bps: int = Field(default=0, ge=0, le=10000)

class MemberChange(BaseModel):
    corporation_id: UUID
    player_id: UUID
    role: str = "MEMBER"

class RoleChange(BaseModel):
    corporation_id: UUID
    player_id: UUID
    role: str

class DiplomacyChange(BaseModel):
    source_corporation_id: UUID
    target_corporation_id: UUID
    relation: str
    standing: int = Field(default=0, ge=-10000, le=10000)
    trade_allowed: bool = True
    transit_allowed: bool = False

class ContractCreate(BaseModel):
    issuer_corporation_id: UUID
    contract_type: str = Field(min_length=1, max_length=64)
    terms: dict[str, Any] = Field(default_factory=dict)
    counterparty_corporation_id: UUID | None = None
    counterparty_player_id: UUID | None = None

class HangarCreate(BaseModel):
    corporation_id: UUID
    name: str = Field(min_length=1, max_length=64)
    capacity: int = Field(gt=0, le=10000)


def _member_role(uow: UnitOfWork, corporation_id: UUID, player_id: UUID) -> str | None:
    row = uow.conn.execute(text("SELECT role FROM corporation_members WHERE corporation_id=:corporation_id AND player_id=:player_id"), {"corporation_id": corporation_id, "player_id": player_id}).first()
    return str(row[0]) if row else None


def _require_permission(uow: UnitOfWork, corporation_id: UUID, player_id: UUID, permission: str) -> str:
    role = _member_role(uow, corporation_id, player_id)
    if role is None or permission not in ROLE_PERMISSIONS.get(role, set()):
        raise HTTPException(status_code=403, detail=f"corporation permission required: {permission}")
    return role


def _require_corporation_exists(uow: UnitOfWork, corporation_id: UUID) -> None:
    if uow.conn.execute(text("SELECT 1 FROM corporations WHERE id=:id"), {"id": corporation_id}).first() is None:
        raise HTTPException(status_code=404, detail="corporation not found")


@router.get("/capabilities")
def capabilities(_: UUID = Depends(get_authenticated_player)):
    return {"systems": ["corporations", "roles", "shared_wallets", "shared_hangars", "alliances", "diplomacy", "social_contracts", "reputation", "manufacturers"], "authoritative": True}


@router.post("/corporations", status_code=status.HTTP_201_CREATED)
def create_corporation(payload: CorporationCreate, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key is required")
    if uow.conn.execute(text("SELECT 1 FROM corporation_members WHERE player_id=:player_id"), {"player_id": player_id}).first():
        raise HTTPException(status_code=409, detail="player already belongs to a corporation")
    corporation = SocialPolicy.create_corporation(player_id, payload.code, payload.name, payload.tax_bps)
    wallet_id = uuid4()
    try:
        uow.conn.execute(text("INSERT INTO wallets (id, version) VALUES (:id, 0)"), {"id": wallet_id})
        uow.conn.execute(text("INSERT INTO corporations (id, owner_id, code, name, tax_bps, wallet_id, version) VALUES (:id,:owner_id,:code,:name,:tax_bps,:wallet_id,0)"), {"id": corporation.id, "owner_id": player_id, "code": corporation.code, "name": corporation.name, "tax_bps": corporation.tax_bps, "wallet_id": wallet_id})
        uow.conn.execute(text("INSERT INTO corporation_members (corporation_id, player_id, role, version) VALUES (:corporation_id,:player_id,'LEADER',0)"), {"corporation_id": corporation.id, "player_id": player_id})
        uow.audit.append("corporation.created", "corporation", corporation.id, {"actor_id": str(player_id), "code": corporation.code})
        uow.outbox.enqueue("corporation.created", "corporation", corporation.id, {"owner_id": str(player_id), "wallet_id": str(wallet_id)})
    except Exception as exc:
        raise HTTPException(status_code=409, detail="corporation code is already in use") from exc
    return {"ok": True, "corporation_id": str(corporation.id), "wallet_id": str(wallet_id), "owner_id": str(player_id), "role": "LEADER"}


@router.post("/members")
def add_member(payload: MemberChange, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _require_permission(uow, payload.corporation_id, player_id, "MANAGE_MEMBERS")
    SocialPolicy.create_member(payload.corporation_id, payload.player_id, payload.role)
    try:
        uow.conn.execute(text("INSERT INTO corporation_members (corporation_id, player_id, role, version) VALUES (:corporation_id,:player_id,:role,0)"), {"corporation_id": payload.corporation_id, "player_id": payload.player_id, "role": payload.role})
    except Exception as exc:
        raise HTTPException(status_code=409, detail="player is already a corporation member") from exc
    uow.audit.append("corporation.member_added", "corporation", payload.corporation_id, {"actor_id": str(player_id), "player_id": str(payload.player_id), "role": payload.role})
    return {"ok": True, "corporation_id": str(payload.corporation_id), "player_id": str(payload.player_id), "role": payload.role}


@router.post("/members/role")
def change_role(payload: RoleChange, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _require_permission(uow, payload.corporation_id, player_id, "MANAGE_ROLES")
    SocialPolicy.validate_role(payload.role)
    if _member_role(uow, payload.corporation_id, payload.player_id) is None:
        raise HTTPException(status_code=404, detail="corporation member not found")
    if payload.player_id == player_id and payload.role != "LEADER":
        raise HTTPException(status_code=409, detail="leader cannot demote itself")
    uow.conn.execute(text("UPDATE corporation_members SET role=:role, version=version+1 WHERE corporation_id=:corporation_id AND player_id=:player_id"), {"role": payload.role, "corporation_id": payload.corporation_id, "player_id": payload.player_id})
    uow.audit.append("corporation.member_role_changed", "corporation", payload.corporation_id, {"actor_id": str(player_id), "player_id": str(payload.player_id), "role": payload.role})
    return {"ok": True, "role": payload.role}


@router.post("/hangars", status_code=status.HTTP_201_CREATED)
def create_hangar(payload: HangarCreate, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _require_permission(uow, payload.corporation_id, player_id, "MANAGE_HANGAR")
    _require_corporation_exists(uow, payload.corporation_id)
    hangar_id = uuid4()
    try:
        uow.conn.execute(text("INSERT INTO corporation_hangars (id, corporation_id, name, capacity, version) VALUES (:id,:corporation_id,:name,:capacity,0)"), {"id": hangar_id, "corporation_id": payload.corporation_id, "name": payload.name.strip(), "capacity": payload.capacity})
    except Exception as exc:
        raise HTTPException(status_code=409, detail="hangar name is already in use") from exc
    uow.audit.append("corporation.hangar_created", "corporation", payload.corporation_id, {"actor_id": str(player_id), "hangar_id": str(hangar_id)})
    return {"ok": True, "hangar_id": str(hangar_id), "capacity": payload.capacity}


@router.post("/diplomacy")
def set_diplomacy(payload: DiplomacyChange, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _require_permission(uow, payload.source_corporation_id, player_id, "DIPLOMACY")
    relation = SocialPolicy.set_diplomacy(payload.source_corporation_id, payload.target_corporation_id, payload.relation, payload.standing, payload.trade_allowed, payload.transit_allowed)
    relation_id = uuid4()
    uow.conn.execute(text("""INSERT INTO diplomatic_relations (id, source_corporation_id, target_corporation_id, relation, standing, trade_allowed, transit_allowed, version)
        VALUES (:id,:source,:target,:relation,:standing,:trade,:transit,0)
        ON CONFLICT (source_corporation_id,target_corporation_id) DO UPDATE SET relation=EXCLUDED.relation, standing=EXCLUDED.standing, trade_allowed=EXCLUDED.trade_allowed, transit_allowed=EXCLUDED.transit_allowed, version=diplomatic_relations.version+1"""), {"id": relation_id, "source": relation.source_corporation_id, "target": relation.target_corporation_id, "relation": relation.relation, "standing": relation.standing, "trade": relation.trade_allowed, "transit": relation.transit_allowed})
    uow.audit.append("diplomacy.changed", "corporation", payload.source_corporation_id, {"actor_id": str(player_id), "target": str(payload.target_corporation_id), "relation": relation.relation})
    return {"ok": True, "relation": relation.relation, "standing": relation.standing, "trade_allowed": relation.trade_allowed, "transit_allowed": relation.transit_allowed}


@router.post("/contracts", status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreate, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _require_permission(uow, payload.issuer_corporation_id, player_id, "CREATE_CONTRACTS")
    contract = SocialPolicy.create_contract(payload.issuer_corporation_id, payload.contract_type, payload.terms, payload.counterparty_corporation_id, payload.counterparty_player_id)
    uow.conn.execute(text("INSERT INTO social_contracts (id, issuer_corporation_id, counterparty_corporation_id, counterparty_player_id, contract_type, terms, state, version) VALUES (:id,:issuer,:counterparty_corp,:counterparty_player,:contract_type,CAST(:terms AS JSONB),'OFFERED',0)"), {"id": contract.id, "issuer": contract.issuer_corporation_id, "counterparty_corp": contract.counterparty_corporation_id, "counterparty_player": contract.counterparty_player_id, "contract_type": contract.contract_type, "terms": __import__('json').dumps(contract.terms)})
    uow.audit.append("social_contract.created", "social_contract", contract.id, {"actor_id": str(player_id), "issuer": str(payload.issuer_corporation_id)})
    uow.outbox.enqueue("social_contract.created", "social_contract", contract.id, {"issuer": str(payload.issuer_corporation_id)})
    return {"ok": True, "contract_id": str(contract.id), "state": "OFFERED"}


@router.get("/overview/{corporation_id}")
def corporation_overview(corporation_id: UUID, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _member_role(uow, corporation_id, player_id) or (_require_corporation_exists(uow, corporation_id), None)[1]
    role = _member_role(uow, corporation_id, player_id)
    if role is None:
        raise HTTPException(status_code=403, detail="corporation membership required")
    corp = uow.conn.execute(text("SELECT id, code, name, tax_bps, wallet_id, status, version FROM corporations WHERE id=:id"), {"id": corporation_id}).mappings().first()
    members = uow.conn.execute(text("SELECT player_id, role, joined_at FROM corporation_members WHERE corporation_id=:id ORDER BY joined_at, player_id"), {"id": corporation_id}).mappings().all()
    hangars = uow.conn.execute(text("SELECT id, name, capacity, version FROM corporation_hangars WHERE corporation_id=:id ORDER BY name"), {"id": corporation_id}).mappings().all()
    return {"corporation": dict(corp), "viewer_role": role, "members": [dict(x) for x in members], "hangars": [dict(x) for x in hangars]}

from __future__ import annotations
from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.api.dependencies import get_authenticated_player
from app.application.phase4_social import SocialPolicy

router = APIRouter(prefix="/api/v1/social", tags=["social"])

class CorporationCreate(BaseModel):
    code: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=2, max_length=80)
    tax_bps: int = Field(default=0, ge=0, le=10000)

class MemberChange(BaseModel):
    corporation_id: UUID
    player_id: UUID
    role: str = "MEMBER"

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

@router.get("/capabilities")
def capabilities(_: UUID = Depends(get_authenticated_player)):
    return {"systems": ["corporations", "roles", "shared_wallets", "shared_hangars", "alliances", "diplomacy", "social_contracts", "reputation", "manufacturers"], "authoritative": True}

@router.post("/corporations/validate")
def validate_corporation(payload: CorporationCreate, player_id: UUID = Depends(get_authenticated_player)):
    corporation = SocialPolicy.create_corporation(player_id, payload.code, payload.name, payload.tax_bps)
    return {"ok": True, "action": "corporation_create", "corporation_id": str(corporation.id), "owner_id": str(player_id), "code": corporation.code}

@router.post("/members/validate")
def validate_member(payload: MemberChange, _: UUID = Depends(get_authenticated_player)):
    member = SocialPolicy.create_member(payload.corporation_id, payload.player_id, payload.role)
    return {"ok": True, "action": "member_change", "corporation_id": str(member.corporation_id), "player_id": str(member.player_id), "role": member.role}

@router.post("/diplomacy/validate")
def validate_diplomacy(payload: DiplomacyChange, _: UUID = Depends(get_authenticated_player)):
    relation = SocialPolicy.set_diplomacy(payload.source_corporation_id, payload.target_corporation_id, payload.relation, payload.standing, payload.trade_allowed, payload.transit_allowed)
    return {"ok": True, "action": "diplomacy_change", "relation": relation.relation, "standing": relation.standing}

@router.post("/contracts/validate")
def validate_contract(payload: ContractCreate, _: UUID = Depends(get_authenticated_player)):
    contract = SocialPolicy.create_contract(payload.issuer_corporation_id, payload.contract_type, payload.terms, payload.counterparty_corporation_id, payload.counterparty_player_id)
    return {"ok": True, "action": "social_contract_create", "contract_id": str(contract.id), "state": contract.state}

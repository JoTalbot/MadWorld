"""Phase 4 social-sandbox domain rules and immutable command results."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

ROLES = {"LEADER", "DIRECTOR", "QUARTERMASTER", "TRADER", "FLEET_COMMANDER", "RECRUITER", "DIPLOMAT", "MECHANIC", "MEMBER"}
RELATIONS = {"ALLIED", "FRIENDLY", "NEUTRAL", "HOSTILE", "WAR"}
PERMISSIONS = {
    "MANAGE_MEMBERS", "MANAGE_ROLES", "MANAGE_WALLET", "MANAGE_HANGAR",
    "MANAGE_ASSETS", "TRADE", "COMMAND_FLEET", "RECRUIT", "DIPLOMACY", "CREATE_CONTRACTS",
}

@dataclass(frozen=True, slots=True)
class Corporation:
    id: UUID
    owner_id: UUID
    code: str
    name: str
    tax_bps: int = 0

@dataclass(frozen=True, slots=True)
class CorporationMember:
    corporation_id: UUID
    player_id: UUID
    role: str

@dataclass(frozen=True, slots=True)
class Diplomacy:
    source_corporation_id: UUID
    target_corporation_id: UUID
    relation: str
    standing: int
    trade_allowed: bool
    transit_allowed: bool

@dataclass(frozen=True, slots=True)
class SocialContract:
    id: UUID
    issuer_corporation_id: UUID
    contract_type: str
    terms: dict
    state: str = "OFFERED"
    counterparty_corporation_id: UUID | None = None
    counterparty_player_id: UUID | None = None

@dataclass(frozen=True, slots=True)
class Manufacturer:
    id: UUID
    corporation_id: UUID
    brand_name: str
    quality_rating: int
    reputation: int

@dataclass(frozen=True, slots=True)
class SocialCommandResult:
    id: UUID
    action: str
    ok: bool
    message: str

class SocialPolicy:
    @staticmethod
    def validate_role(role: str) -> None:
        if role not in ROLES:
            raise ValueError(f"unknown corporation role: {role}")
    @staticmethod
    def validate_permission(permission: str) -> None:
        if permission not in PERMISSIONS:
            raise ValueError(f"unknown corporation permission: {permission}")
    @staticmethod
    def validate_relation(relation: str) -> None:
        if relation not in RELATIONS:
            raise ValueError(f"unknown diplomatic relation: {relation}")
    @staticmethod
    def validate_tax(tax_bps: int) -> None:
        if not 0 <= tax_bps <= 10_000:
            raise ValueError("corporation tax must be between 0 and 10000 bps")
    @staticmethod
    def create_corporation(owner_id: UUID, code: str, name: str, tax_bps: int = 0) -> Corporation:
        if not code.strip() or not name.strip(): raise ValueError("corporation code and name are required")
        SocialPolicy.validate_tax(tax_bps)
        return Corporation(uuid4(), owner_id, code.strip().upper(), name.strip(), tax_bps)
    @staticmethod
    def create_member(corporation_id: UUID, player_id: UUID, role: str = "MEMBER") -> CorporationMember:
        SocialPolicy.validate_role(role)
        return CorporationMember(corporation_id, player_id, role)
    @staticmethod
    def set_diplomacy(source: UUID, target: UUID, relation: str, standing: int, trade_allowed: bool, transit_allowed: bool) -> Diplomacy:
        if source == target: raise ValueError("a corporation cannot establish diplomacy with itself")
        SocialPolicy.validate_relation(relation)
        if not -10_000 <= standing <= 10_000: raise ValueError("standing out of range")
        if relation in {"HOSTILE", "WAR"} and trade_allowed: raise ValueError("hostile/war relations cannot enable trade")
        return Diplomacy(source, target, relation, standing, trade_allowed, transit_allowed)
    @staticmethod
    def create_contract(issuer: UUID, contract_type: str, terms: dict, counterparty_corporation_id: UUID | None = None, counterparty_player_id: UUID | None = None) -> SocialContract:
        if (counterparty_corporation_id is None) == (counterparty_player_id is None): raise ValueError("exactly one counterparty is required")
        if not contract_type.strip(): raise ValueError("contract type is required")
        return SocialContract(uuid4(), issuer, contract_type.strip(), dict(terms), counterparty_corporation_id=counterparty_corporation_id, counterparty_player_id=counterparty_player_id)

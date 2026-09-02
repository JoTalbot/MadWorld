"""Final authoritative Phase 4 operations: escrow settlement, reputation propagation and brands."""
from __future__ import annotations
import json
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from app.api.dependencies import get_authenticated_player, get_uow
from app.api.idempotency import replay_or_none, require_key, store_response
from app.api.phase4_routes import _member_role, _require_permission
from app.application.phase4_operations import Phase4Operations
from app.application.ports import UnitOfWork
router = APIRouter(prefix="/api/v1/social", tags=["social-completion"])
class EscrowContractCreate(BaseModel):
    issuer_corporation_id: UUID
    contract_type: str = Field(min_length=1, max_length=64)
    amount: int = Field(gt=0)
    counterparty_corporation_id: UUID | None = None
    counterparty_player_id: UUID | None = None
    terms: dict = Field(default_factory=dict)
class ContractSettle(BaseModel): contract_id: UUID; new_state: str
class ManufacturerCreate(BaseModel):
    corporation_id: UUID
    brand_name: str = Field(min_length=2, max_length=80)
    quality_rating: int = Field(default=5000, ge=0, le=10000)
def _wallet(uow: UnitOfWork, corporation_id: UUID | None = None, player_id: UUID | None = None) -> UUID:
    row = uow.conn.execute(text("SELECT wallet_id FROM corporations WHERE id=:id"), {"id": corporation_id}).first() if corporation_id else uow.conn.execute(text("SELECT id FROM wallets WHERE owner_id=:id"), {"id": player_id}).first()
    if not row or not row[0]: raise HTTPException(404, "wallet not found")
    return UUID(str(row[0]))
def _balance(uow: UnitOfWork, wallet_id: UUID) -> int:
    return int(uow.conn.execute(text("SELECT COALESCE(SUM(amount),0) FROM ledger_entries WHERE wallet_id=:w"), {"w": wallet_id}).scalar_one())
def _lock_wallets(uow: UnitOfWork, ids: list[UUID]) -> None:
    for wid in sorted(set(ids), key=str):
        if not uow.conn.execute(text("SELECT id FROM wallets WHERE id=:id FOR UPDATE"), {"id": wid}).first(): raise HTTPException(404, "wallet not found")
def _apply_reputation(uow: UnitOfWork, contract: dict, actor: UUID) -> None:
    terms = dict(contract["terms"] or {}); delta = terms.get("reputation_delta")
    if delta is None: return
    target_type, target_id = terms.get("reputation_target_type"), terms.get("reputation_target_id")
    if target_type is None or target_id is None: raise HTTPException(400, "reputation_delta requires reputation_target_type and reputation_target_id")
    sp = UUID(str(contract["counterparty_player_id"])) if contract["counterparty_player_id"] else None
    sc = UUID(str(contract["counterparty_corporation_id"])) if contract["counterparty_corporation_id"] else None
    r = Phase4Operations.reputation_delta(sp, sc, str(target_type), str(target_id), int(delta), f"social contract {contract['id']} completed")
    q = "SELECT id,standing,version FROM social_reputation WHERE subject_corporation_id=:s AND target_type=:t AND target_id=:id FOR UPDATE" if sc else "SELECT id,standing,version FROM social_reputation WHERE subject_player_id=:s AND target_type=:t AND target_id=:id FOR UPDATE"
    row = uow.conn.execute(text(q), {"s": sc or sp, "t": r.target_type, "id": r.target_id}).mappings().first(); current = int(row["standing"]) if row else 0; new = max(-10000, min(10000, current + r.delta)); rid = row["id"] if row else uuid4()
    if row: uow.conn.execute(text("UPDATE social_reputation SET standing=:v,version=version+1 WHERE id=:id AND version=:ver"), {"v": new, "id": rid, "ver": row["version"]})
    else: uow.conn.execute(text("INSERT INTO social_reputation (id,subject_player_id,subject_corporation_id,target_type,target_id,standing,version) VALUES (:id,:p,:c,:t,:tid,:v,0)"), {"id": rid, "p": sp, "c": sc, "t": r.target_type, "tid": r.target_id, "v": new})
    uow.conn.execute(text("INSERT INTO social_reputation_history (id,subject_player_id,subject_corporation_id,target_type,target_id,delta,reason,actor_id) VALUES (:id,:p,:c,:t,:tid,:d,:reason,:actor)"), {"id": uuid4(), "p": sp, "c": sc, "t": r.target_type, "tid": r.target_id, "d": r.delta, "reason": r.reason, "actor": actor})
@router.post("/contracts/escrow", status_code=201)
def create_escrow_contract(payload: EscrowContractCreate, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    key = require_key(idempotency_key); body = payload.model_dump(mode="json"); replay = replay_or_none(uow, "social.contract.escrow.create", key, body)
    if replay is not None: return replay
    _require_permission(uow, payload.issuer_corporation_id, player_id, "CREATE_CONTRACTS")
    if (payload.counterparty_corporation_id is None) == (payload.counterparty_player_id is None): raise HTTPException(400, "exactly one counterparty is required")
    source = _wallet(uow, corporation_id=payload.issuer_corporation_id); target_corp = payload.counterparty_corporation_id
    if target_corp and not uow.conn.execute(text("SELECT 1 FROM corporations WHERE id=:id"), {"id": target_corp}).first(): raise HTTPException(404, "counterparty corporation not found")
    if payload.counterparty_player_id and not uow.conn.execute(text("SELECT 1 FROM players WHERE id=:id"), {"id": payload.counterparty_player_id}).first(): raise HTTPException(404, "counterparty player not found")
    _lock_wallets(uow, [source])
    if _balance(uow, source) < payload.amount: raise HTTPException(409, "insufficient corporate funds for escrow")
    cid, ew = uuid4(), uuid4(); terms = dict(payload.terms); terms["escrow_amount"] = payload.amount
    uow.conn.execute(text("INSERT INTO wallets (id,owner_id,version) VALUES (:id,NULL,0)"), {"id": ew})
    uow.conn.execute(text("INSERT INTO social_contracts (id,issuer_corporation_id,counterparty_corporation_id,counterparty_player_id,contract_type,terms,state,version) VALUES (:id,:issuer,:cc,:cp,:type,CAST(:terms AS JSONB),'OFFERED',0)"), {"id": cid, "issuer": payload.issuer_corporation_id, "cc": target_corp, "cp": payload.counterparty_player_id, "type": payload.contract_type.strip(), "terms": json.dumps(terms)})
    uow.conn.execute(text("INSERT INTO social_contract_escrow (contract_id,wallet_id,amount,state) VALUES (:c,:w,:amount,'LOCKED')"), {"c": cid, "w": ew, "amount": payload.amount})
    for sign, suffix in [(-1, "debit"), (1, "escrow-credit")]:
        uow.conn.execute(text("INSERT INTO ledger_entries (id,idempotency_key,wallet_id,amount,reason,actor_id) VALUES (:id,:key,:w,:amount,:reason,:actor)"), {"id": uuid4(), "key": f"{key}:{suffix}", "w": source if sign < 0 else ew, "amount": sign * payload.amount, "reason": f"escrow:{cid}", "actor": player_id})
    result = {"ok": True, "contract_id": str(cid), "escrow_wallet_id": str(ew), "amount": payload.amount, "state": "OFFERED"}; store_response(uow, "social.contract.escrow.create", key, body, result, 201, player_id)
    uow.audit.append("social_contract.escrow_locked", "social_contract", cid, {"actor_id": str(player_id), "amount": payload.amount}); uow.outbox.enqueue("social_contract.escrow_locked", "social_contract", cid, {"amount": payload.amount}); return result
@router.post("/contracts/settle")
def settle_contract(payload: ContractSettle, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    key = require_key(idempotency_key); body = payload.model_dump(mode="json"); replay = replay_or_none(uow, "social.contract.settle", key, body)
    if replay is not None: return replay
    row = uow.conn.execute(text("SELECT * FROM social_contracts WHERE id=:id FOR UPDATE"), {"id": payload.contract_id}).mappings().first()
    if not row: raise HTTPException(404, "social contract not found")
    issuer = UUID(str(row["issuer_corporation_id"])); counter = UUID(str(row["counterparty_corporation_id"])) if row["counterparty_corporation_id"] else None
    authorized = _member_role(uow, issuer, player_id) is not None or (counter is not None and _member_role(uow, counter, player_id) is not None) or (row["counterparty_player_id"] and UUID(str(row["counterparty_player_id"])) == player_id)
    if not authorized: raise HTTPException(403, "contract participant required")
    Phase4Operations.transition_contract(str(row["state"]), payload.new_state); escrow = uow.conn.execute(text("SELECT * FROM social_contract_escrow WHERE contract_id=:id FOR UPDATE"), {"id": payload.contract_id}).mappings().first()
    if escrow:
        ew, amount = UUID(str(escrow["wallet_id"])), int(escrow["amount"])
        if str(escrow["state"]) != "LOCKED": raise HTTPException(409, "escrow is already settled")
        if payload.new_state == "COMPLETED":
            target = _wallet(uow, corporation_id=counter) if counter else _wallet(uow, player_id=UUID(str(row["counterparty_player_id"]))); _lock_wallets(uow, [ew, target])
            for wid, amount_signed, suffix in [(ew, -amount, "escrow-debit"), (target, amount, "release")]: uow.conn.execute(text("INSERT INTO ledger_entries (id,idempotency_key,wallet_id,amount,reason,actor_id) VALUES (:id,:key,:w,:amount,:reason,:actor)"), {"id": uuid4(), "key": f"{key}:{suffix}", "w": wid, "amount": amount_signed, "reason": f"contract:{payload.contract_id}:release", "actor": player_id})
            uow.conn.execute(text("UPDATE social_contract_escrow SET state='RELEASED',released_at=NOW() WHERE contract_id=:id AND state='LOCKED'"), {"id": payload.contract_id}); _apply_reputation(uow, dict(row), player_id)
        elif payload.new_state in {"CANCELLED", "EXPIRED"}:
            source = _wallet(uow, corporation_id=issuer); _lock_wallets(uow, [ew, source])
            for wid, amount_signed, suffix in [(ew, -amount, "escrow-refund-debit"), (source, amount, "refund")]: uow.conn.execute(text("INSERT INTO ledger_entries (id,idempotency_key,wallet_id,amount,reason,actor_id) VALUES (:id,:key,:w,:amount,:reason,:actor)"), {"id": uuid4(), "key": f"{key}:{suffix}", "w": wid, "amount": amount_signed, "reason": f"contract:{payload.contract_id}:refund", "actor": player_id})
            uow.conn.execute(text("UPDATE social_contract_escrow SET state='REFUNDED',released_at=NOW() WHERE contract_id=:id AND state='LOCKED'"), {"id": payload.contract_id})
    uow.conn.execute(text("UPDATE social_contracts SET state=:state,version=version+1 WHERE id=:id AND version=:v"), {"state": payload.new_state, "id": payload.contract_id, "v": row["version"]})
    result = {"ok": True, "contract_id": str(payload.contract_id), "state": payload.new_state, "escrow_state": ({"COMPLETED":"RELEASED","CANCELLED":"REFUNDED","EXPIRED":"REFUNDED"}.get(payload.new_state) if escrow else None)}; store_response(uow, "social.contract.settle", key, body, result, 200, player_id); uow.audit.append("social_contract.settled", "social_contract", payload.contract_id, {"actor_id": str(player_id), "state": payload.new_state}); uow.outbox.enqueue("social_contract.settled", "social_contract", payload.contract_id, {"state": payload.new_state}); return result
@router.post("/manufacturers", status_code=201)
def create_manufacturer(payload: ManufacturerCreate, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _require_permission(uow, payload.corporation_id, player_id, "TRADE")
    if not uow.conn.execute(text("SELECT 1 FROM corporations WHERE id=:id"), {"id": payload.corporation_id}).first(): raise HTTPException(404, "corporation not found")
    mid = uuid4()
    try: uow.conn.execute(text("INSERT INTO manufacturers (id,corporation_id,brand_name,quality_rating,reputation,version) VALUES (:id,:c,:b,:q,0,0)"), {"id": mid, "c": payload.corporation_id, "b": payload.brand_name.strip(), "q": payload.quality_rating})
    except Exception as exc: raise HTTPException(409, "manufacturer or brand already exists") from exc
    uow.audit.append("manufacturer.created", "corporation", payload.corporation_id, {"actor_id": str(player_id), "manufacturer_id": str(mid), "brand_name": payload.brand_name.strip()}); return {"ok": True, "manufacturer_id": str(mid), "brand_name": payload.brand_name.strip(), "quality_rating": payload.quality_rating}

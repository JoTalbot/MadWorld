"""B6 authoritative finance and asset provenance commands."""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_uow
from app.api.idempotency import replay_or_none, require_key, store_response
from app.application.ports import UnitOfWork

router = APIRouter(prefix="/api/v1/finance", tags=["finance"])

class CreditCreate(BaseModel):
    principal: int = Field(gt=0, le=10_000_000_000)
    interest_bps: int = Field(default=500, ge=0, le=10000)
    due_at: datetime
    lender_player_id: UUID | None = None

class Repayment(BaseModel):
    amount: int = Field(gt=0)

class CollateralCreate(BaseModel):
    asset_id: UUID
    collateral_value: int = Field(gt=0)

class InsuranceCreate(BaseModel):
    asset_id: UUID
    coverage_value: int = Field(gt=0)
    premium: int = Field(ge=0)
    deductible: int = Field(default=0, ge=0)
    expires_at: datetime

class InvestmentCreate(BaseModel):
    principal: int = Field(gt=0)
    target_type: str = Field(min_length=1, max_length=32)
    target_id: UUID
    return_bps: int = Field(ge=-10000, le=100000)
    maturity_at: datetime

class ProvenanceRecord(BaseModel):
    asset_id: UUID
    event_type: str = Field(min_length=1, max_length=40)
    quality_rating: int | None = Field(default=None, ge=0, le=10000)
    manufacturer_id: UUID | None = None
    production_batch: str | None = Field(default=None, max_length=128)
    metadata: dict = Field(default_factory=dict)


def _wallet(uow: UnitOfWork, player_id: UUID) -> UUID:
    row = uow.conn.execute(text("SELECT id FROM wallets WHERE owner_id=:p FOR UPDATE"), {"p": player_id}).first()
    if not row: raise HTTPException(404, "wallet not found")
    return UUID(str(row[0]))


def _balance(uow: UnitOfWork, wallet_id: UUID) -> int:
    return int(uow.conn.execute(text("SELECT COALESCE(SUM(amount),0) FROM ledger_entries WHERE wallet_id=:w"), {"w": wallet_id}).scalar_one())


def _debit(uow: UnitOfWork, player_id: UUID, amount: int, key: str, reason: str) -> UUID:
    wallet_id = _wallet(uow, player_id)
    if _balance(uow, wallet_id) < amount: raise HTTPException(409, "insufficient funds")
    uow.conn.execute(text("INSERT INTO ledger_entries(id,idempotency_key,wallet_id,amount,reason,actor_id) VALUES (:id,:key,:w,:amount,:reason,:actor)"), {"id":uuid4(),"key":key,"w":wallet_id,"amount":-amount,"reason":reason,"actor":player_id})
    return wallet_id


def _asset_owned(uow: UnitOfWork, player_id: UUID, asset_id: UUID) -> None:
    if not uow.conn.execute(text("SELECT id FROM vehicles WHERE id=:a AND owner_id=:p FOR UPDATE"), {"a":asset_id,"p":player_id}).first():
        raise HTTPException(403, "asset is not owned by the authenticated player")


@router.post("/credit", status_code=201)
def create_credit(payload: CreditCreate, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    key = require_key(idempotency_key); body = payload.model_dump(mode="json")
    replay = replay_or_none(uow,"finance.credit.create",key,body)
    if replay is not None: return replay
    if payload.due_at <= datetime.now(UTC): raise HTTPException(400,"due_at must be in the future")
    lender = payload.lender_player_id
    if lender == player_id: raise HTTPException(400,"borrower and lender must differ")
    agreement = uuid4()
    uow.conn.execute(text("INSERT INTO finance_credit_agreements(id,borrower_player_id,lender_player_id,principal,outstanding,interest_bps,due_at) VALUES (:id,:b,:l,:p,:p,:i,:d)"), {"id":agreement,"b":player_id,"l":lender,"p":payload.principal,"i":payload.interest_bps,"d":payload.due_at})
    result={"ok":True,"credit_agreement_id":str(agreement),"principal":payload.principal,"outstanding":payload.principal,"status":"ACTIVE"}
    store_response(uow,"finance.credit.create",key,body,result,201,player_id)
    uow.audit.append("finance.credit.created","finance",agreement,{"actor_id":str(player_id),"principal":payload.principal})
    uow.outbox.enqueue("finance.credit.created","finance",agreement,result)
    return result


@router.post("/credit/{agreement_id}/repay")
def repay_credit(agreement_id: UUID, payload: Repayment, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    key=require_key(idempotency_key); body=payload.model_dump(mode="json")|{"agreement_id":str(agreement_id)}
    replay=replay_or_none(uow,"finance.credit.repay",key,body)
    if replay is not None:return replay
    row=uow.conn.execute(text("SELECT borrower_player_id,outstanding,status FROM finance_credit_agreements WHERE id=:id FOR UPDATE"),{"id":agreement_id}).mappings().first()
    if not row:raise HTTPException(404,"credit agreement not found")
    if UUID(str(row["borrower_player_id"]))!=player_id:raise HTTPException(403,"borrower authorization required")
    if row["status"] not in ("ACTIVE","DEFAULTED"):raise HTTPException(409,"credit is not repayable")
    amount=min(payload.amount,int(row["outstanding"]))
    _debit(uow,player_id,amount,key+":debit","credit repayment")
    new_outstanding=int(row["outstanding"])-amount
    status="REPAID" if new_outstanding==0 else "ACTIVE"
    uow.conn.execute(text("UPDATE finance_credit_agreements SET outstanding=:o,status=:s,version=version+1,updated_at=now() WHERE id=:id"),{"o":new_outstanding,"s":status,"id":agreement_id})
    result={"ok":True,"credit_agreement_id":str(agreement_id),"repaid":amount,"outstanding":new_outstanding,"status":status}
    store_response(uow,"finance.credit.repay",key,body,result,200,player_id); uow.audit.append("finance.credit.repaid","finance",agreement_id,{"actor_id":str(player_id),"amount":amount}); uow.outbox.enqueue("finance.credit.repaid","finance",agreement_id,result)
    return result


@router.post("/credit/{agreement_id}/default")
def default_credit(agreement_id: UUID, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    key=require_key(idempotency_key); body={"agreement_id":str(agreement_id)}; replay=replay_or_none(uow,"finance.credit.default",key,body)
    if replay is not None:return replay
    row=uow.conn.execute(text("SELECT borrower_player_id,status,due_at FROM finance_credit_agreements WHERE id=:id FOR UPDATE"),{"id":agreement_id}).mappings().first()
    if not row:raise HTTPException(404,"credit agreement not found")
    if UUID(str(row["borrower_player_id"]))!=player_id:raise HTTPException(403,"borrower authorization required")
    if row["status"]!="ACTIVE":raise HTTPException(409,"credit is not active")
    if row["due_at"]>datetime.now(UTC):raise HTTPException(409,"credit is not due")
    uow.conn.execute(text("UPDATE finance_credit_agreements SET status='DEFAULTED',version=version+1,updated_at=now() WHERE id=:id"),{"id":agreement_id})
    result={"ok":True,"credit_agreement_id":str(agreement_id),"status":"DEFAULTED"}; store_response(uow,"finance.credit.default",key,body,result,200,player_id); uow.audit.append("finance.credit.defaulted","finance",agreement_id,{"actor_id":str(player_id)}); uow.outbox.enqueue("finance.credit.defaulted","finance",agreement_id,result); return result


@router.post("/credit/{agreement_id}/collateral", status_code=201)
def pledge_collateral(agreement_id: UUID, payload: CollateralCreate, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    key=require_key(idempotency_key); body=payload.model_dump(mode="json")|{"agreement_id":str(agreement_id)}; replay=replay_or_none(uow,"finance.collateral.pledge",key,body)
    if replay is not None:return replay
    row=uow.conn.execute(text("SELECT borrower_player_id,status,outstanding FROM finance_credit_agreements WHERE id=:id FOR UPDATE"),{"id":agreement_id}).mappings().first()
    if not row:raise HTTPException(404,"credit agreement not found")
    if UUID(str(row["borrower_player_id"]))!=player_id:raise HTTPException(403,"borrower authorization required")
    if row["status"]!="ACTIVE":raise HTTPException(409,"credit is not active")
    _asset_owned(uow,player_id,payload.asset_id)
    if payload.collateral_value < int(row["outstanding"]): raise HTTPException(409,"collateral value must cover outstanding principal")
    cid=uuid4(); uow.conn.execute(text("INSERT INTO finance_collateral(id,credit_agreement_id,asset_id,collateral_value) VALUES (:id,:c,:a,:v)"),{"id":cid,"c":agreement_id,"a":payload.asset_id,"v":payload.collateral_value})
    result={"ok":True,"collateral_id":str(cid),"asset_id":str(payload.asset_id),"status":"PLEDGED"}; store_response(uow,"finance.collateral.pledge",key,body,result,201,player_id); uow.audit.append("finance.collateral.pledged","finance",agreement_id,{"actor_id":str(player_id),"asset_id":str(payload.asset_id)}); return result


@router.post("/insurance", status_code=201)
def create_insurance(payload: InsuranceCreate, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    key=require_key(idempotency_key); body=payload.model_dump(mode="json"); replay=replay_or_none(uow,"finance.insurance.create",key,body)
    if replay is not None:return replay
    if payload.expires_at<=datetime.now(UTC):raise HTTPException(400,"expires_at must be in the future")
    if payload.deductible>payload.coverage_value:raise HTTPException(400,"deductible exceeds coverage")
    _asset_owned(uow,player_id,payload.asset_id); _debit(uow,player_id,payload.premium,key+":premium","insurance premium")
    pid=uuid4(); uow.conn.execute(text("INSERT INTO finance_insurance_policies(id,holder_player_id,asset_id,coverage_value,premium,deductible,expires_at) VALUES (:id,:p,:a,:c,:pr,:d,:e)"),{"id":pid,"p":player_id,"a":payload.asset_id,"c":payload.coverage_value,"pr":payload.premium,"d":payload.deductible,"e":payload.expires_at})
    result={"ok":True,"policy_id":str(pid),"status":"ACTIVE"}; store_response(uow,"finance.insurance.create",key,body,result,201,player_id); uow.audit.append("finance.insurance.created","finance",pid,{"actor_id":str(player_id),"asset_id":str(payload.asset_id)}); return result


@router.post("/investment", status_code=201)
def create_investment(payload: InvestmentCreate, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    key=require_key(idempotency_key); body=payload.model_dump(mode="json"); replay=replay_or_none(uow,"finance.investment.create",key,body)
    if replay is not None:return replay
    if payload.maturity_at<=datetime.now(UTC):raise HTTPException(400,"maturity_at must be in the future")
    _debit(uow,player_id,payload.principal,key+":principal","investment principal")
    iid=uuid4(); uow.conn.execute(text("INSERT INTO finance_investments(id,investor_player_id,principal,target_type,target_id,return_bps,maturity_at) VALUES (:id,:p,:v,:t,:tid,:r,:m)"),{"id":iid,"p":player_id,"v":payload.principal,"t":payload.target_type,"tid":payload.target_id,"r":payload.return_bps,"m":payload.maturity_at})
    result={"ok":True,"investment_id":str(iid),"status":"ACTIVE","principal":payload.principal}; store_response(uow,"finance.investment.create",key,body,result,201,player_id); uow.audit.append("finance.investment.created","finance",iid,{"actor_id":str(player_id),"principal":payload.principal}); return result


@router.post("/provenance", status_code=201)
def record_provenance(payload: ProvenanceRecord, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    key=require_key(idempotency_key); body=payload.model_dump(mode="json"); replay=replay_or_none(uow,"finance.provenance.record",key,body)
    if replay is not None:return replay
    _asset_owned(uow,player_id,payload.asset_id)
    event_id=uuid4(); uow.conn.execute(text("INSERT INTO asset_provenance_history(id,asset_id,event_type,owner_player_id,quality_rating,manufacturer_id,production_batch,metadata) VALUES (:id,:a,:e,:p,:q,:m,:b,CAST(:md AS JSONB))"),{"id":event_id,"a":payload.asset_id,"e":payload.event_type,"p":player_id,"q":payload.quality_rating,"m":payload.manufacturer_id,"b":payload.production_batch,"md":__import__('json').dumps(payload.metadata)})
    result={"ok":True,"provenance_event_id":str(event_id),"asset_id":str(payload.asset_id)}; store_response(uow,"finance.provenance.record",key,body,result,201,player_id); uow.audit.append("finance.provenance.recorded","asset",payload.asset_id,{"actor_id":str(player_id),"event_type":payload.event_type}); return result


@router.get("/provenance/{asset_id}")
def provenance(asset_id: UUID, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _asset_owned(uow,player_id,asset_id)
    rows=uow.conn.execute(text("SELECT id,event_type,owner_player_id,quality_rating,manufacturer_id,production_batch,metadata,recorded_at FROM asset_provenance_history WHERE asset_id=:a ORDER BY recorded_at,id"),{"a":asset_id}).mappings().all()
    return {"ok":True,"asset_id":str(asset_id),"history":[{**dict(r),"id":str(r["id"]),"owner_player_id":str(r["owner_player_id"]) if r["owner_player_id"] else None,"manufacturer_id":str(r["manufacturer_id"]) if r["manufacturer_id"] else None,"recorded_at":r["recorded_at"].isoformat()} for r in rows]}


@router.get("/credit/{agreement_id}")
def credit(agreement_id: UUID, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    row=uow.conn.execute(text("SELECT id,borrower_player_id,lender_player_id,principal,outstanding,interest_bps,status,due_at,version,created_at,updated_at FROM finance_credit_agreements WHERE id=:id FOR SHARE"),{"id":agreement_id}).mappings().first()
    if not row:raise HTTPException(404,"credit agreement not found")
    if UUID(str(row["borrower_player_id"]))!=player_id and (row["lender_player_id"] is None or UUID(str(row["lender_player_id"]))!=player_id):raise HTTPException(403,"credit participant authorization required")
    return {"ok":True,**{k:(str(v) if isinstance(v,UUID) else v.isoformat() if hasattr(v,'isoformat') else v) for k,v in dict(row).items()}}

"""Authoritative corporate wallet operations for Phase 4."""
from __future__ import annotations
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from app.api.dependencies import get_authenticated_player, get_uow
from app.api.idempotency import replay_or_none, require_key, store_response
from app.application.ports import UnitOfWork
from app.api.phase4_routes import _require_permission

router = APIRouter(prefix="/api/v1/social", tags=["social-wallet"])

class WalletTransfer(BaseModel):
    corporation_id: UUID
    recipient_player_id: UUID | None = None
    recipient_corporation_id: UUID | None = None
    amount: int = Field(gt=0)
    reason: str = Field(min_length=1, max_length=256)


def _validate_recipient(payload: WalletTransfer) -> None:
    if (payload.recipient_player_id is None) == (payload.recipient_corporation_id is None):
        raise HTTPException(400, "exactly one recipient is required")


def _wallet_for_player(uow: UnitOfWork, player_id: UUID) -> UUID:
    row = uow.conn.execute(text("SELECT id FROM wallets WHERE owner_id=:p"), {"p": player_id}).first()
    if not row:
        raise HTTPException(404, "recipient wallet not found")
    return UUID(str(row[0]))


def _wallet_for_corporation(uow: UnitOfWork, corporation_id: UUID) -> UUID:
    row = uow.conn.execute(text("SELECT wallet_id FROM corporations WHERE id=:c"), {"c": corporation_id}).first()
    if not row or not row[0]:
        raise HTTPException(409, "corporation wallet is not configured")
    return UUID(str(row[0]))


def _balance(uow: UnitOfWork, wallet_id: UUID) -> int:
    value = uow.conn.execute(text("SELECT COALESCE(SUM(amount),0) FROM ledger_entries WHERE wallet_id=:w"), {"w": wallet_id}).scalar_one()
    return int(value)


def _lock_wallets(uow: UnitOfWork, wallet_ids: list[UUID]) -> None:
    for wallet_id in sorted(set(wallet_ids), key=str):
        row = uow.conn.execute(text("SELECT id FROM wallets WHERE id=:w FOR UPDATE"), {"w": wallet_id}).first()
        if not row:
            raise HTTPException(404, "wallet not found")


@router.get("/wallet/{corporation_id}")
def wallet_overview(corporation_id: UUID, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    _require_permission(uow, corporation_id, player_id, "MANAGE_WALLET")
    wallet_id = _wallet_for_corporation(uow, corporation_id)
    return {"ok": True, "corporation_id": str(corporation_id), "wallet_id": str(wallet_id), "balance": _balance(uow, wallet_id)}


@router.post("/wallet/transfer")
def transfer_wallet(
    payload: WalletTransfer,
    player_id: UUID = Depends(get_authenticated_player),
    uow: UnitOfWork = Depends(get_uow),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    key = require_key(idempotency_key)
    replay = replay_or_none(uow, "social.wallet.transfer", key, payload.model_dump(mode="json"))
    if replay is not None:
        return replay
    _validate_recipient(payload)
    _require_permission(uow, payload.corporation_id, player_id, "MANAGE_WALLET")
    source = _wallet_for_corporation(uow, payload.corporation_id)
    target = _wallet_for_player(uow, payload.recipient_player_id) if payload.recipient_player_id else _wallet_for_corporation(uow, payload.recipient_corporation_id)
    if source == target:
        raise HTTPException(409, "source and destination wallet must differ")
    _lock_wallets(uow, [source, target])
    if _balance(uow, source) < payload.amount:
        raise HTTPException(409, "insufficient corporate funds")
    debit_key = f"{key}:debit"
    credit_key = f"{key}:credit"
    uow.conn.execute(text("INSERT INTO ledger_entries (id,idempotency_key,wallet_id,amount,reason,actor_id) VALUES (:id,:key,:w,:amount,:reason,:actor)"), {"id": uuid4(), "key": debit_key, "w": source, "amount": -payload.amount, "reason": payload.reason, "actor": player_id})
    uow.conn.execute(text("INSERT INTO ledger_entries (id,idempotency_key,wallet_id,amount,reason,actor_id) VALUES (:id,:key,:w,:amount,:reason,:actor)"), {"id": uuid4(), "key": credit_key, "w": target, "amount": payload.amount, "reason": payload.reason, "actor": player_id})
    result = {"ok": True, "source_wallet_id": str(source), "destination_wallet_id": str(target), "amount": payload.amount, "balance": _balance(uow, source)}
    store_response(uow, "social.wallet.transfer", key, payload.model_dump(mode="json"), result, 200, player_id)
    uow.audit.append("social.wallet.transferred", "corporation", payload.corporation_id, {"actor_id": str(player_id), "amount": payload.amount, "source_wallet_id": str(source), "destination_wallet_id": str(target)})
    uow.outbox.enqueue("social.wallet.transferred", "corporation", payload.corporation_id, {"amount": payload.amount, "source_wallet_id": str(source), "destination_wallet_id": str(target)})
    return result

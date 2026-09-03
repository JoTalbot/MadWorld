from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_engine
from app.application.errors import NotFound

router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.post("/{order_id}/cancel")
def cancel_order(order_id: UUID, authenticated_player: UUID = Depends(get_authenticated_player)):
    with get_engine().begin() as conn:
        order = conn.execute(
            text("SELECT * FROM market_orders WHERE id=:id AND owner_id=:owner FOR UPDATE"),
            {"id": order_id, "owner": authenticated_player},
        ).mappings().first()
        if order is None:
            raise NotFound("market order not found")
        if order["status"] != "open" or int(order["remaining_quantity"]) == 0:
            return {"id": order_id, "status": str(order["status"]), "remaining_quantity": int(order["remaining_quantity"])}

        remaining = int(order["remaining_quantity"])
        if order["side"] == "buy":
            wallet = conn.execute(
                text("SELECT id FROM wallets WHERE owner_id=:owner FOR UPDATE"),
                {"owner": authenticated_player},
            ).mappings().one()
            refund = remaining * int(order["unit_price"])
            if refund > 0:
                conn.execute(
                    text("INSERT INTO ledger_entries(wallet_id,amount,reason,actor_id,idempotency_key) VALUES(:w,:a,'market_buy_cancel_refund',:o,:k) ON CONFLICT(idempotency_key) DO NOTHING"),
                    {"w": wallet["id"], "a": refund, "o": authenticated_player, "k": f"market-cancel-refund:{order_id}"},
                )
        else:
            escrow = conn.execute(
                text("SELECT quantity,condition FROM market_sell_escrow WHERE order_id=:id FOR UPDATE"),
                {"id": order_id},
            ).mappings().first()
            if escrow is None or int(escrow["quantity"]) != remaining:
                raise ValueError("sell escrow does not match remaining order quantity")
            inv = conn.execute(
                text("SELECT id FROM inventories WHERE owner_id=:owner ORDER BY id LIMIT 1 FOR UPDATE"),
                {"owner": authenticated_player},
            ).mappings().one()
            conn.execute(
                text("INSERT INTO inventory_items(inventory_id,item_definition_id,quantity,condition) VALUES(:inv,:item,:qty,:condition) ON CONFLICT(inventory_id,item_definition_id) DO UPDATE SET quantity=inventory_items.quantity+:qty"),
                {"inv": inv["id"], "item": order["item_definition_id"], "qty": remaining, "condition": escrow["condition"]},
            )
            conn.execute(text("DELETE FROM market_sell_escrow WHERE order_id=:id"), {"id": order_id})

        return conn.execute(
            text("UPDATE market_orders SET status='cancelled',remaining_quantity=0,updated_at=now(),version=version+1 WHERE id=:id RETURNING id,status,remaining_quantity"),
            {"id": order_id},
        ).mappings().one()

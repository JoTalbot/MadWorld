"""Transactional regional player market endpoints for the vertical slice."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_engine

router = APIRouter(prefix="/api/v1/market", tags=["market"])


class OrderRequest(BaseModel):
    region_id: UUID
    item_definition_id: UUID
    quantity: int = Field(gt=0)
    unit_price: int = Field(gt=0)


class OrderResponse(BaseModel):
    id: UUID
    region_id: UUID
    item_definition_id: UUID
    side: str
    quantity: int
    remaining_quantity: int
    unit_price: int
    status: str
    created_at: str


class BookOrder(BaseModel):
    id: UUID
    owner_id: UUID
    side: str
    quantity: int
    remaining_quantity: int
    unit_price: int
    created_at: str


class BookResponse(BaseModel):
    region_id: UUID
    item_definition_id: UUID
    bids: list[BookOrder]
    asks: list[BookOrder]


def _order_response(row) -> OrderResponse:
    return OrderResponse(
        id=UUID(str(row["id"])), region_id=UUID(str(row["region_id"])),
        item_definition_id=UUID(str(row["item_definition_id"])), side=str(row["side"]),
        quantity=int(row["quantity"]), remaining_quantity=int(row["remaining_quantity"]),
        unit_price=int(row["unit_price"]), status=str(row["status"]), created_at=row["created_at"].isoformat(),
    )


def _wallet(conn, player_id: UUID):
    return conn.execute(text("SELECT id FROM wallets WHERE owner_id = :player_id FOR UPDATE"), {"player_id": player_id}).mappings().one()


def _balance(conn, wallet_id: UUID) -> int:
    row = conn.execute(text("SELECT COALESCE(SUM(amount), 0) AS balance FROM ledger_entries WHERE wallet_id = :wallet_id"), {"wallet_id": wallet_id}).mappings().one()
    return int(row["balance"])


def _inventory(conn, player_id: UUID):
    return conn.execute(text("SELECT id FROM inventories WHERE owner_id = :player_id ORDER BY id LIMIT 1 FOR UPDATE"), {"player_id": player_id}).mappings().one()


def _ledger(conn, wallet_id: UUID, amount: int, reason: str, actor_id: UUID, key: str) -> None:
    conn.execute(text("INSERT INTO ledger_entries (wallet_id, amount, reason, actor_id, idempotency_key) VALUES (:wallet_id, :amount, :reason, :actor_id, :key)"), {"wallet_id": wallet_id, "amount": amount, "reason": reason, "actor_id": actor_id, "key": key})


def _match(conn, order_id: UUID) -> None:
    order = conn.execute(text("SELECT * FROM market_orders WHERE id = :id FOR UPDATE"), {"id": order_id}).mappings().one()
    opposite = "sell" if order["side"] == "buy" else "buy"
    if order["side"] == "buy":
        rows = conn.execute(text("SELECT * FROM market_orders WHERE region_id=:region AND item_definition_id=:item AND side=:side AND status='open' AND remaining_quantity>0 AND unit_price<=:price AND owner_id<>:owner ORDER BY unit_price ASC, created_at ASC, id ASC FOR UPDATE"), {"region": order["region_id"], "item": order["item_definition_id"], "side": opposite, "price": order["unit_price"], "owner": order["owner_id"]}).mappings().all()
    else:
        rows = conn.execute(text("SELECT * FROM market_orders WHERE region_id=:region AND item_definition_id=:item AND side=:side AND status='open' AND remaining_quantity>0 AND unit_price>=:price AND owner_id<>:owner ORDER BY unit_price DESC, created_at ASC, id ASC FOR UPDATE"), {"region": order["region_id"], "item": order["item_definition_id"], "side": opposite, "price": order["unit_price"], "owner": order["owner_id"]}).mappings().all()
    for other in rows:
        other_remaining = int(other["remaining_quantity"])
        while int(order["remaining_quantity"]) > 0 and other_remaining > 0:
            qty = min(int(order["remaining_quantity"]), other_remaining)
            trade_price = int(other["unit_price"])
            buy = order if order["side"] == "buy" else other
            sell = other if order["side"] == "buy" else order
            seller_wallet = _wallet(conn, UUID(str(sell["owner_id"])))
            amount = qty * trade_price
            trade_key = f"market-trade:{order_id}:{other['id']}:{int(order['remaining_quantity'])}:{other_remaining}"
            sell_escrow = conn.execute(text("SELECT quantity, condition FROM market_sell_escrow WHERE order_id=:id FOR UPDATE"), {"id": sell["id"]}).mappings().first()
            if sell_escrow is None or int(sell_escrow["quantity"]) < qty:
                raise ValueError("sell order escrow is insufficient")
            item_def = conn.execute(text("SELECT stack_limit FROM item_definitions WHERE id=:item"), {"item": order["item_definition_id"]}).mappings().one()
            buyer_inv = _inventory(conn, UUID(str(buy["owner_id"])))
            buyer_stack = conn.execute(text("SELECT quantity FROM inventory_items WHERE inventory_id=:inv AND item_definition_id=:item FOR UPDATE"), {"inv": buyer_inv["id"], "item": order["item_definition_id"]}).mappings().first()
            if buyer_stack is not None and int(buyer_stack["quantity"]) + qty > int(item_def["stack_limit"]):
                raise ValueError("buyer inventory stack limit exceeded")
            conn.execute(text("INSERT INTO inventory_items (inventory_id, item_definition_id, quantity, condition) VALUES (:inv,:item,:qty,:condition) ON CONFLICT (inventory_id,item_definition_id) DO UPDATE SET quantity=inventory_items.quantity+:qty"), {"inv": buyer_inv["id"], "item": order["item_definition_id"], "qty": qty, "condition": sell_escrow["condition"]})
            conn.execute(text("UPDATE market_sell_escrow SET quantity=quantity-:qty WHERE order_id=:id"), {"id": sell["id"], "qty": qty})
            _ledger(conn, UUID(str(seller_wallet["id"])), amount, "market_sale", UUID(str(sell["owner_id"])), trade_key)
            for current in (order, other):
                new_remaining = int(current["remaining_quantity"]) - qty
                status = "filled" if new_remaining == 0 else "open"
                conn.execute(text("UPDATE market_orders SET remaining_quantity=:remaining,status=:status,updated_at=now(),version=version+1 WHERE id=:id"), {"id": current["id"], "remaining": new_remaining, "status": status})
            conn.execute(text("INSERT INTO market_trade_history (buy_order_id,sell_order_id,region_id,item_definition_id,buyer_id,seller_id,quantity,unit_price,total_amount) VALUES (:buy,:sell,:region,:item,:buyer,:seller,:qty,:price,:amount)"), {"buy": buy["id"], "sell": sell["id"], "region": order["region_id"], "item": order["item_definition_id"], "buyer": buy["owner_id"], "seller": sell["owner_id"], "qty": qty, "price": trade_price, "amount": amount})
            other_remaining -= qty
            order = conn.execute(text("SELECT * FROM market_orders WHERE id=:id FOR UPDATE"), {"id": order_id}).mappings().one()
    if order["side"] == "buy" and order["status"] == "filled":
        reserved = int(order["quantity"]) * int(order["unit_price"])
        spent = conn.execute(text("SELECT COALESCE(SUM(total_amount),0) AS total FROM market_trade_history WHERE buy_order_id=:id"), {"id": order_id}).scalar_one()
        refund = reserved - int(spent)
        if refund > 0:
            wallet = _wallet(conn, UUID(str(order["owner_id"])))
            _ledger(conn, UUID(str(wallet["id"])), refund, "market_buy_reserve_refund", UUID(str(order["owner_id"])), f"market-refund:{order_id}")


@router.get("/{region_id}/{item_definition_id}", response_model=BookResponse)
def book(region_id: UUID, item_definition_id: UUID, authenticated_player: UUID = Depends(get_authenticated_player)) -> BookResponse:
    with get_engine().connect() as conn:
        bids = conn.execute(text("SELECT id,owner_id,side,quantity,remaining_quantity,unit_price,created_at FROM market_orders WHERE region_id=:region AND item_definition_id=:item AND side='buy' AND status='open' AND remaining_quantity>0 ORDER BY unit_price DESC,created_at ASC,id ASC"), {"region": region_id, "item": item_definition_id}).mappings().all()
        asks = conn.execute(text("SELECT id,owner_id,side,quantity,remaining_quantity,unit_price,created_at FROM market_orders WHERE region_id=:region AND item_definition_id=:item AND side='sell' AND status='open' AND remaining_quantity>0 ORDER BY unit_price ASC,created_at ASC,id ASC"), {"region": region_id, "item": item_definition_id}).mappings().all()
    return BookResponse(region_id=region_id, item_definition_id=item_definition_id, bids=[BookOrder(**{**dict(r), "created_at": r["created_at"].isoformat()}) for r in bids], asks=[BookOrder(**{**dict(r), "created_at": r["created_at"].isoformat()}) for r in asks])


def _existing(conn, owner_id: UUID, key: str):
    return conn.execute(text("SELECT * FROM market_orders WHERE owner_id=:owner AND idempotency_key=:key"), {"owner": owner_id, "key": key}).mappings().first()


@router.post("/buy", response_model=OrderResponse)
def buy(payload: OrderRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), authenticated_player: UUID = Depends(get_authenticated_player)) -> OrderResponse:
    if not idempotency_key:
        raise ValueError("Idempotency-Key header is required")
    with get_engine().begin() as conn:
        existing = _existing(conn, authenticated_player, idempotency_key)
        if existing is not None:
            return _order_response(existing)
        wallet = _wallet(conn, authenticated_player)
        reserve = payload.quantity * payload.unit_price
        if _balance(conn, UUID(str(wallet["id"]))) < reserve:
            raise ValueError("insufficient funds for market order")
        _ledger(conn, UUID(str(wallet["id"])), -reserve, "market_buy_reserve", authenticated_player, f"market-reserve:{authenticated_player}:{idempotency_key}")
        row = conn.execute(text("INSERT INTO market_orders (region_id,owner_id,item_definition_id,side,quantity,remaining_quantity,unit_price,idempotency_key) VALUES (:region,:owner,:item,'buy',:qty,:qty,:price,:key) RETURNING *"), {"region": payload.region_id, "owner": authenticated_player, "item": payload.item_definition_id, "qty": payload.quantity, "price": payload.unit_price, "key": idempotency_key}).mappings().one()
        _match(conn, UUID(str(row["id"])))
        return _order_response(conn.execute(text("SELECT * FROM market_orders WHERE id=:id"), {"id": row["id"]}).mappings().one())


@router.post("/sell", response_model=OrderResponse)
def sell(payload: OrderRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), authenticated_player: UUID = Depends(get_authenticated_player)) -> OrderResponse:
    if not idempotency_key:
        raise ValueError("Idempotency-Key header is required")
    with get_engine().begin() as conn:
        existing = _existing(conn, authenticated_player, idempotency_key)
        if existing is not None:
            return _order_response(existing)
        inv = _inventory(conn, authenticated_player)
        item = conn.execute(text("SELECT quantity,condition FROM inventory_items WHERE inventory_id=:inv AND item_definition_id=:item FOR UPDATE"), {"inv": inv["id"], "item": payload.item_definition_id}).mappings().first()
        if item is None or int(item["quantity"]) < payload.quantity:
            raise ValueError("insufficient inventory for market order")
        remaining_inventory = int(item["quantity"]) - payload.quantity
        if remaining_inventory == 0:
            conn.execute(text("DELETE FROM inventory_items WHERE inventory_id=:inv AND item_definition_id=:item"), {"inv": inv["id"], "item": payload.item_definition_id})
        else:
            conn.execute(text("UPDATE inventory_items SET quantity=:remaining WHERE inventory_id=:inv AND item_definition_id=:item"), {"inv": inv["id"], "item": payload.item_definition_id, "remaining": remaining_inventory})
        row = conn.execute(text("INSERT INTO market_orders (region_id,owner_id,item_definition_id,side,quantity,remaining_quantity,unit_price,idempotency_key) VALUES (:region,:owner,:item,'sell',:qty,:qty,:price,:key) RETURNING *"), {"region": payload.region_id, "owner": authenticated_player, "item": payload.item_definition_id, "qty": payload.quantity, "price": payload.unit_price, "key": idempotency_key}).mappings().one()
        conn.execute(text("INSERT INTO market_sell_escrow(order_id,quantity,condition) VALUES (:id,:qty,:condition)"), {"id": row["id"], "qty": payload.quantity, "condition": item["condition"]})
        _match(conn, UUID(str(row["id"])))
        return _order_response(conn.execute(text("SELECT * FROM market_orders WHERE id=:id"), {"id": row["id"]}).mappings().one())

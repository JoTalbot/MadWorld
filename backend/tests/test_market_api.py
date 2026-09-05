import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api import market_routes
from app.api.dependencies import get_authenticated_player
from app.infrastructure.db import create_engine_from_env
from app.main import app

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def engine():
    if not os.getenv("MADWORLD_DATABASE_URL"):
        pytest.skip("MADWORLD_DATABASE_URL is not configured")
    engine = create_engine_from_env()
    yield engine
    engine.dispose()


def seed_market_players(engine):
    region_id = uuid4()
    item_id = uuid4()
    seller_id, buyer_id = uuid4(), uuid4()
    seller_wallet, buyer_wallet = uuid4(), uuid4()
    seller_inventory, buyer_inventory = uuid4(), uuid4()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO regions (id, code, name) VALUES (:id, :code, 'Test Region')"),
                     {"id": region_id, "code": f"test-region-{region_id.hex}"})
        conn.execute(text("INSERT INTO item_definitions (id, code, name, category, stack_limit) VALUES (:id, :code, 'Market Item', 'test', 100)"),
                     {"id": item_id, "code": f"market-item-{item_id.hex}"})
        for player_id, wallet_id, inventory_id, handle in (
            (seller_id, seller_wallet, seller_inventory, "market-seller"),
            (buyer_id, buyer_wallet, buyer_inventory, "market-buyer"),
        ):
            conn.execute(text("INSERT INTO players (id, handle) VALUES (:id, :handle)"), {"id": player_id, "handle": f"{handle}-{player_id.hex[:8]}"})
            conn.execute(text("INSERT INTO wallets (id, owner_id) VALUES (:id, :owner_id)"), {"id": wallet_id, "owner_id": player_id})
            conn.execute(text("INSERT INTO inventories (id, owner_id, name) VALUES (:id, :owner_id, 'market-test')"), {"id": inventory_id, "owner_id": player_id})
        conn.execute(text("INSERT INTO inventory_items (inventory_id, item_definition_id, quantity, condition) VALUES (:inventory, :item, 10, 90)"),
                     {"inventory": seller_inventory, "item": item_id})
        conn.execute(text("INSERT INTO ledger_entries (wallet_id, amount, reason, actor_id, idempotency_key) VALUES (:wallet, 1000, 'test_funding', :actor, :key)"),
                     {"wallet": buyer_wallet, "actor": buyer_id, "key": f"market-funding-{buyer_id}"})
        conn.execute(text("INSERT INTO ledger_entries (wallet_id, amount, reason, actor_id, idempotency_key) VALUES (:wallet, 1000, 'test_funding', :actor, :key)"),
                     {"wallet": seller_wallet, "actor": seller_id, "key": f"market-funding-{seller_id}"})
    return region_id, item_id, seller_id, buyer_id, seller_wallet, buyer_wallet, seller_inventory, buyer_inventory


def auth(player_id):
    def override_auth():
        return player_id
    app.dependency_overrides[get_authenticated_player] = override_auth


def test_market_crosses_orders_and_settles_inventory_and_funds(engine, monkeypatch):
    region_id, item_id, seller_id, buyer_id, seller_wallet, buyer_wallet, seller_inventory, buyer_inventory = seed_market_players(engine)
    monkeypatch.setattr(market_routes, "get_engine", lambda: engine)
    client = TestClient(app)
    try:
        auth(seller_id)
        sell = client.post("/api/v1/market/sell", json={"region_id": str(region_id), "item_definition_id": str(item_id), "quantity": 4, "unit_price": 20}, headers={"Idempotency-Key": "sell-1"})
        assert sell.status_code == 200
        assert sell.json()["remaining_quantity"] == 4

        auth(buyer_id)
        buy = client.post("/api/v1/market/buy", json={"region_id": str(region_id), "item_definition_id": str(item_id), "quantity": 4, "unit_price": 25}, headers={"Idempotency-Key": "buy-1"})
        assert buy.status_code == 200
        assert buy.json()["status"] == "filled"
        assert buy.json()["remaining_quantity"] == 0

        with engine.connect() as conn:
            seller_qty = conn.execute(text("SELECT quantity FROM inventory_items WHERE inventory_id=:inventory AND item_definition_id=:item"), {"inventory": seller_inventory, "item": item_id}).scalar_one()
            buyer_qty = conn.execute(text("SELECT quantity FROM inventory_items WHERE inventory_id=:inventory AND item_definition_id=:item"), {"inventory": buyer_inventory, "item": item_id}).scalar_one()
            escrow = conn.execute(text("SELECT quantity FROM market_sell_escrow WHERE order_id=:order"), {"order": sell.json()["id"]}).scalar_one()
            seller_balance = conn.execute(text("SELECT COALESCE(SUM(amount),0) FROM ledger_entries WHERE wallet_id=:wallet"), {"wallet": seller_wallet}).scalar_one()
            buyer_balance = conn.execute(text("SELECT COALESCE(SUM(amount),0) FROM ledger_entries WHERE wallet_id=:wallet"), {"wallet": buyer_wallet}).scalar_one()
            trades = conn.execute(text("SELECT count(*) FROM market_trade_history WHERE buy_order_id=:order"), {"order": buy.json()["id"]}).scalar_one()
        assert seller_qty == 6
        assert buyer_qty == 4
        assert escrow == 0
        assert seller_balance == 1080
        assert buyer_balance == 920
        assert trades == 1
    finally:
        app.dependency_overrides.clear()


def test_market_buy_is_idempotent_for_same_owner_and_key(engine, monkeypatch):
    region_id, item_id, seller_id, buyer_id, *_ = seed_market_players(engine)
    monkeypatch.setattr(market_routes, "get_engine", lambda: engine)
    client = TestClient(app)
    try:
        auth(buyer_id)
        payload = {"region_id": str(region_id), "item_definition_id": str(item_id), "quantity": 2, "unit_price": 10}
        first = client.post("/api/v1/market/buy", json=payload, headers={"Idempotency-Key": "same-key"})
        second = client.post("/api/v1/market/buy", json=payload, headers={"Idempotency-Key": "same-key"})
        assert first.status_code == second.status_code == 200
        assert first.json() == second.json()
        with engine.connect() as conn:
            orders = conn.execute(text("SELECT count(*) FROM market_orders WHERE owner_id=:owner AND idempotency_key=:key"), {"owner": buyer_id, "key": "same-key"}).scalar_one()
            reserves = conn.execute(text("SELECT count(*) FROM ledger_entries WHERE wallet_id=(SELECT id FROM wallets WHERE owner_id=:owner) AND reason='market_buy_reserve'"), {"owner": buyer_id}).scalar_one()
        assert orders == 1
        assert reserves == 1
    finally:
        app.dependency_overrides.clear()


def test_market_idempotency_key_reuse_with_different_payload_is_rejected(engine, monkeypatch):
    region_id, item_id, seller_id, buyer_id, *_ = seed_market_players(engine)
    monkeypatch.setattr(market_routes, "get_engine", lambda: engine)
    client = TestClient(app)
    try:
        auth(buyer_id)
        first_payload = {"region_id": str(region_id), "item_definition_id": str(item_id), "quantity": 2, "unit_price": 10}
        changed_payload = {"region_id": str(region_id), "item_definition_id": str(item_id), "quantity": 3, "unit_price": 10}
        first = client.post("/api/v1/market/buy", json=first_payload, headers={"Idempotency-Key": "conflict-key"})
        second = client.post("/api/v1/market/buy", json=changed_payload, headers={"Idempotency-Key": "conflict-key"})
        assert first.status_code == 200
        assert second.status_code == 409
        assert second.json()["code"] == "IDEMPOTENCY_CONFLICT"
        with engine.connect() as conn:
            orders = conn.execute(text("SELECT count(*) FROM market_orders WHERE owner_id=:owner AND idempotency_key=:key"), {"owner": buyer_id, "key": "conflict-key"}).scalar_one()
            reserves = conn.execute(text("SELECT count(*) FROM ledger_entries WHERE wallet_id=(SELECT id FROM wallets WHERE owner_id=:owner) AND reason='market_buy_reserve'"), {"owner": buyer_id}).scalar_one()
        assert orders == 1
        assert reserves == 1
    finally:
        app.dependency_overrides.clear()


def test_market_isolates_region_and_item_order_books(engine, monkeypatch):
    region_id, item_id, seller_id, buyer_id, *_ = seed_market_players(engine)
    other_region, other_item = uuid4(), uuid4()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO regions (id, code, name) VALUES (:id, :code, 'Other Region')"), {"id": other_region, "code": f"other-region-{other_region.hex}"})
        conn.execute(text("INSERT INTO item_definitions (id, code, name, category, stack_limit) VALUES (:id, :code, 'Other Item', 'test', 100)"), {"id": other_item, "code": f"other-item-{other_item.hex}"})
    monkeypatch.setattr(market_routes, "get_engine", lambda: engine)
    client = TestClient(app)
    try:
        auth(seller_id)
        response = client.post("/api/v1/market/sell", json={"region_id": str(region_id), "item_definition_id": str(item_id), "quantity": 1, "unit_price": 30}, headers={"Idempotency-Key": "isolated-sell"})
        assert response.status_code == 200
        auth(buyer_id)
        other_book = client.get(f"/api/v1/market/{other_region}/{other_item}")
        assert other_book.status_code == 200
        assert other_book.json()["bids"] == []
        assert other_book.json()["asks"] == []
    finally:
        app.dependency_overrides.clear()

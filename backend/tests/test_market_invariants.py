from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player
from app.api import market_routes
from app.main import app
from test_market_api import auth, seed_market_players

pytestmark = pytest.mark.integration


def test_market_price_time_priority_and_partial_fill(engine, monkeypatch):
    region_id, item_id, seller_id, buyer_id, *_ = seed_market_players(engine)
    seller2 = uuid4()
    wallet2 = uuid4()
    inventory2 = uuid4()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO players (id, handle) VALUES (:id, :handle)"), {"id": seller2, "handle": f"seller2-{seller2.hex[:8]}"})
        conn.execute(text("INSERT INTO wallets (id, owner_id) VALUES (:id, :owner_id)"), {"id": wallet2, "owner_id": seller2})
        conn.execute(text("INSERT INTO inventories (id, owner_id, name) VALUES (:id, :owner_id, 'market-test-2')"), {"id": inventory2, "owner_id": seller2})
        conn.execute(text("INSERT INTO inventory_items (inventory_id, item_definition_id, quantity, condition) VALUES (:inventory, :item, 3, 80)"), {"inventory": inventory2, "item": item_id})
    monkeypatch.setattr(market_routes, "get_engine", lambda: engine)
    client = TestClient(app)
    try:
        auth(seller_id)
        first = client.post('/api/v1/market/sell', json={'region_id': str(region_id), 'item_definition_id': str(item_id), 'quantity': 2, 'unit_price': 20}, headers={'Idempotency-Key': 'priority-1'})
        assert first.status_code == 200
        auth(seller2)
        second = client.post('/api/v1/market/sell', json={'region_id': str(region_id), 'item_definition_id': str(item_id), 'quantity': 3, 'unit_price': 20}, headers={'Idempotency-Key': 'priority-2'})
        assert second.status_code == 200
        auth(buyer_id)
        buy = client.post('/api/v1/market/buy', json={'region_id': str(region_id), 'item_definition_id': str(item_id), 'quantity': 4, 'unit_price': 25}, headers={'Idempotency-Key': 'priority-buy'})
        assert buy.status_code == 200
        assert buy.json()['status'] == 'filled'
        with engine.connect() as conn:
            remaining_first = conn.execute(text('SELECT remaining_quantity FROM market_orders WHERE id=:id'), {'id': first.json()['id']}).scalar_one()
            remaining_second = conn.execute(text('SELECT remaining_quantity FROM market_orders WHERE id=:id'), {'id': second.json()['id']}).scalar_one()
            rows = conn.execute(text('SELECT quantity, unit_price FROM market_trade_history WHERE buy_order_id=:id ORDER BY created_at, id'), {'id': buy.json()['id']}).fetchall()
        assert remaining_first == 0
        assert remaining_second == 1
        assert [(int(r[0]), int(r[1])) for r in rows] == [(2, 20), (2, 20)]
    finally:
        app.dependency_overrides.clear()


def test_market_stack_limit_failure_rolls_back_entire_buy(engine, monkeypatch):
    region_id, item_id, seller_id, buyer_id, seller_wallet, buyer_wallet, seller_inventory, buyer_inventory = seed_market_players(engine)
    with engine.begin() as conn:
        conn.execute(text('UPDATE item_definitions SET stack_limit=10 WHERE id=:id'), {'id': item_id})
        conn.execute(text('INSERT INTO inventory_items (inventory_id, item_definition_id, quantity, condition) VALUES (:inventory, :item, 9, 100)'), {'inventory': buyer_inventory, 'item': item_id})
    monkeypatch.setattr(market_routes, 'get_engine', lambda: engine)
    client = TestClient(app)
    try:
        auth(seller_id)
        sell = client.post('/api/v1/market/sell', json={'region_id': str(region_id), 'item_definition_id': str(item_id), 'quantity': 2, 'unit_price': 20}, headers={'Idempotency-Key': 'rollback-sell'})
        assert sell.status_code == 200
        auth(buyer_id)
        buy = client.post('/api/v1/market/buy', json={'region_id': str(region_id), 'item_definition_id': str(item_id), 'quantity': 2, 'unit_price': 20}, headers={'Idempotency-Key': 'rollback-buy'})
        assert buy.status_code >= 400
        with engine.connect() as conn:
            seller_qty = conn.execute(text('SELECT quantity FROM inventory_items WHERE inventory_id=:inventory AND item_definition_id=:item'), {'inventory': seller_inventory, 'item': item_id}).scalar_one()
            buyer_qty = conn.execute(text('SELECT quantity FROM inventory_items WHERE inventory_id=:inventory AND item_definition_id=:item'), {'inventory': buyer_inventory, 'item': item_id}).scalar_one()
            order_count = conn.execute(text("SELECT count(*) FROM market_orders WHERE owner_id=:owner AND idempotency_key='rollback-buy'"), {'owner': buyer_id}).scalar_one()
            reserve_count = conn.execute(text("SELECT count(*) FROM ledger_entries WHERE wallet_id=:wallet AND reason='market_buy_reserve'"), {'wallet': buyer_wallet}).scalar_one()
        assert seller_qty == 8
        assert buyer_qty == 9
        assert order_count == 0
        assert reserve_count == 0
    finally:
        app.dependency_overrides.clear()


def test_market_missing_idempotency_key_is_rejected_without_mutation(engine, monkeypatch):
    region_id, item_id, seller_id, buyer_id, seller_wallet, buyer_wallet, seller_inventory, buyer_inventory = seed_market_players(engine)
    monkeypatch.setattr(market_routes, 'get_engine', lambda: engine)
    client = TestClient(app)
    try:
        auth(buyer_id)
        response = client.post('/api/v1/market/buy', json={'region_id': str(region_id), 'item_definition_id': str(item_id), 'quantity': 1, 'unit_price': 10})
        assert response.status_code >= 400
        with engine.connect() as conn:
            orders = conn.execute(text('SELECT count(*) FROM market_orders WHERE owner_id=:owner'), {'owner': buyer_id}).scalar_one()
            reserves = conn.execute(text("SELECT count(*) FROM ledger_entries WHERE wallet_id=:wallet AND reason='market_buy_reserve'"), {'wallet': buyer_wallet}).scalar_one()
        assert orders == 0
        assert reserves == 0
    finally:
        app.dependency_overrides.clear()

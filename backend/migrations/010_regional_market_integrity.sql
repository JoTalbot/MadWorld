ALTER TABLE market_orders DROP CONSTRAINT IF EXISTS market_orders_idempotency_key_key;

CREATE UNIQUE INDEX IF NOT EXISTS uq_market_orders_owner_idempotency
    ON market_orders(owner_id, idempotency_key);

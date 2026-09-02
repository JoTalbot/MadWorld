CREATE TABLE market_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id UUID NOT NULL REFERENCES regions(id),
    owner_id UUID NOT NULL REFERENCES players(id),
    item_definition_id UUID NOT NULL REFERENCES item_definitions(id),
    side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    remaining_quantity BIGINT NOT NULL CHECK (remaining_quantity >= 0 AND remaining_quantity <= quantity),
    unit_price BIGINT NOT NULL CHECK (unit_price > 0),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'filled', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    version INTEGER NOT NULL DEFAULT 0 CHECK (version >= 0),
    idempotency_key TEXT NOT NULL UNIQUE
);

CREATE TABLE market_sell_escrow (
    order_id UUID PRIMARY KEY REFERENCES market_orders(id) ON DELETE CASCADE,
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    condition INTEGER NOT NULL DEFAULT 100 CHECK (condition BETWEEN 0 AND 100)
);

CREATE INDEX idx_market_book ON market_orders(region_id, item_definition_id, side, status, unit_price, created_at, id);
CREATE INDEX idx_market_owner ON market_orders(owner_id, status, created_at);

CREATE TABLE market_trade_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buy_order_id UUID NOT NULL REFERENCES market_orders(id),
    sell_order_id UUID NOT NULL REFERENCES market_orders(id),
    region_id UUID NOT NULL REFERENCES regions(id),
    item_definition_id UUID NOT NULL REFERENCES item_definitions(id),
    buyer_id UUID NOT NULL REFERENCES players(id),
    seller_id UUID NOT NULL REFERENCES players(id),
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    unit_price BIGINT NOT NULL CHECK (unit_price > 0),
    total_amount BIGINT NOT NULL CHECK (total_amount > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_market_history_item_region ON market_trade_history(region_id, item_definition_id, created_at);

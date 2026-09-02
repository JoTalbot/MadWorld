ALTER TABLE market_sell_escrow
    DROP CONSTRAINT IF EXISTS market_sell_escrow_quantity_check;

ALTER TABLE market_sell_escrow
    ADD CONSTRAINT market_sell_escrow_quantity_check CHECK (quantity >= 0);

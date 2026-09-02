CREATE OR REPLACE FUNCTION record_market_price_history() RETURNS trigger AS $$
BEGIN
    INSERT INTO market_price_history(region_id,item_definition_id,trade_id,quantity,unit_price,total_amount)
    VALUES(NEW.region_id,NEW.item_definition_id,NEW.id,NEW.quantity,NEW.unit_price,NEW.total_amount)
    ON CONFLICT DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_market_price_history ON market_trade_history;
CREATE TRIGGER trg_market_price_history
AFTER INSERT ON market_trade_history
FOR EACH ROW EXECUTE FUNCTION record_market_price_history();

CREATE TABLE IF NOT EXISTS economy_facilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    settlement_id UUID NOT NULL REFERENCES settlements(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1 CHECK(level >= 1),
    efficiency_bps INTEGER NOT NULL DEFAULT 10000 CHECK(efficiency_bps BETWEEN 1000 AND 20000),
    UNIQUE(settlement_id, code)
);

CREATE INDEX IF NOT EXISTS idx_economy_facilities_settlement ON economy_facilities(settlement_id);

INSERT INTO economy_facilities(settlement_id,code,level,efficiency_bps)
SELECT s.id, f.code, 1, 10000
FROM settlements s
CROSS JOIN (VALUES ('refinery'), ('workshop')) AS f(code)
ON CONFLICT (settlement_id,code) DO NOTHING;

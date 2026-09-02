CREATE TABLE IF NOT EXISTS economy_recipes (
    id UUID PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('refining','production')),
    facility_code TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds > 0),
    inputs JSONB NOT NULL,
    outputs JSONB NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS economy_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    settlement_id UUID NOT NULL REFERENCES settlements(id),
    recipe_id UUID NOT NULL REFERENCES economy_recipes(id),
    state TEXT NOT NULL DEFAULT 'running' CHECK (state IN ('running','completed','cancelled')),
    started_at TIMESTAMPTZ NOT NULL,
    completes_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_economy_jobs_due ON economy_jobs(state, completes_at);
CREATE INDEX IF NOT EXISTS idx_economy_jobs_owner ON economy_jobs(owner_id, created_at DESC);

CREATE TABLE IF NOT EXISTS market_price_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id UUID NOT NULL REFERENCES regions(id),
    item_definition_id UUID NOT NULL REFERENCES item_definitions(id),
    trade_id UUID NOT NULL REFERENCES market_trade_history(id),
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    unit_price BIGINT NOT NULL CHECK (unit_price > 0),
    total_amount BIGINT NOT NULL CHECK (total_amount > 0),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_market_price_history_lookup ON market_price_history(region_id, item_definition_id, recorded_at DESC);

INSERT INTO economy_recipes (id,code,name,kind,facility_code,duration_seconds,inputs,outputs) VALUES
('60000000-0000-0000-0000-000000000001','refine_metal','Refine Scrap Metal','refining','refinery',30,'[{"item_code":"scrap_metal","quantity":5}]','[{"item_code":"metal_plate","quantity":1}]'),
('60000000-0000-0000-0000-000000000002','refine_wire','Bundle Salvaged Wire','refining','workshop',20,'[{"item_code":"salvaged_wire","quantity":4}]','[{"item_code":"wire_bundle","quantity":1}]'),
('60000000-0000-0000-0000-000000000003','refine_fuel','Refine Fuel Cell','refining','refinery',45,'[{"item_code":"raw_fuel","quantity":3},{"item_code":"chemicals","quantity":1}]','[{"item_code":"fuel_cell","quantity":1}]'),
('60000000-0000-0000-0000-000000000004','produce_repair_kit','Produce Field Repair Kit','production','workshop',60,'[{"item_code":"metal_plate","quantity":1},{"item_code":"wire_bundle","quantity":1},{"item_code":"chemicals","quantity":1}]','[{"item_code":"repair_kit","quantity":1}]'),
('60000000-0000-0000-0000-000000000005','produce_armor_panel','Produce Armor Panel','production','workshop',90,'[{"item_code":"metal_plate","quantity":2},{"item_code":"fiber","quantity":2},{"item_code":"chemicals","quantity":1}]','[{"item_code":"armor_panel","quantity":1}]')
ON CONFLICT (id) DO NOTHING;

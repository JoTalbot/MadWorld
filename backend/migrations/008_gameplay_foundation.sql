CREATE TABLE regions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    risk_tier INTEGER NOT NULL DEFAULT 1 CHECK (risk_tier BETWEEN 1 AND 5)
);

CREATE TABLE settlements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id UUID NOT NULL REFERENCES regions(id),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    market_fee_bps INTEGER NOT NULL DEFAULT 250 CHECK (market_fee_bps BETWEEN 0 AND 10000)
);

CREATE TABLE player_settlements (
    player_id UUID PRIMARY KEY REFERENCES players(id) ON DELETE CASCADE,
    settlement_id UUID NOT NULL REFERENCES settlements(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE resource_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id UUID NOT NULL REFERENCES regions(id),
    resource_item_definition_id UUID NOT NULL REFERENCES item_definitions(id),
    quantity BIGINT NOT NULL CHECK (quantity >= 0),
    gather_amount INTEGER NOT NULL CHECK (gather_amount > 0),
    cooldown_seconds INTEGER NOT NULL CHECK (cooldown_seconds > 0),
    version INTEGER NOT NULL DEFAULT 0 CHECK (version >= 0)
);

CREATE INDEX idx_settlements_region ON settlements(region_id);
CREATE INDEX idx_resource_nodes_region ON resource_nodes(region_id);
CREATE INDEX idx_player_settlements_settlement ON player_settlements(settlement_id);

INSERT INTO regions (id, code, name, risk_tier)
VALUES ('10000000-0000-0000-0000-000000000001', 'ash-basin', 'Ash Basin', 1)
ON CONFLICT (id) DO NOTHING;

INSERT INTO settlements (id, region_id, code, name, market_fee_bps)
VALUES ('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'dusthaven', 'Dusthaven', 250)
ON CONFLICT (id) DO NOTHING;

INSERT INTO item_definitions (id, code, name, category, stack_limit)
VALUES
('30000000-0000-0000-0000-000000000001', 'scrap_metal', 'Scrap Metal', 'resource', 1000),
('30000000-0000-0000-0000-000000000002', 'salvaged_wire', 'Salvaged Wire', 'resource', 1000),
('30000000-0000-0000-0000-000000000003', 'raw_fuel', 'Raw Fuel', 'resource', 500),
('30000000-0000-0000-0000-000000000004', 'fiber', 'Industrial Fiber', 'resource', 1000),
('30000000-0000-0000-0000-000000000005', 'chemicals', 'Recovered Chemicals', 'resource', 500),
('30000000-0000-0000-0000-000000000006', 'metal_plate', 'Reinforced Plate', 'component', 500),
('30000000-0000-0000-0000-000000000007', 'wire_bundle', 'Wire Bundle', 'component', 500),
('30000000-0000-0000-0000-000000000008', 'fuel_cell', 'Fuel Cell', 'component', 100),
('30000000-0000-0000-0000-000000000009', 'reinforced_tire', 'Reinforced Tire', 'component', 50),
('30000000-0000-0000-0000-00000000000a', 'repair_kit', 'Field Repair Kit', 'component', 50),
('30000000-0000-0000-0000-00000000000b', 'water', 'Water', 'resource', 1000),
('30000000-0000-0000-0000-00000000000c', 'food_ration', 'Food Ration', 'consumable', 500),
('30000000-0000-0000-0000-00000000000d', 'ammo_basic', 'Basic Ammunition', 'consumable', 500),
('30000000-0000-0000-0000-00000000000e', 'engine_parts', 'Engine Parts', 'component', 100),
('30000000-0000-0000-0000-00000000000f', 'armor_panel', 'Armor Panel', 'component', 100)
ON CONFLICT (id) DO NOTHING;

INSERT INTO resource_nodes (id, region_id, resource_item_definition_id, quantity, gather_amount, cooldown_seconds)
VALUES
('40000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 10000, 10, 30),
('40000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000002', 5000, 8, 45),
('40000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000003', 2500, 5, 60),
('40000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000004', 7000, 12, 30),
('40000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000005', 3000, 4, 75)
ON CONFLICT (id) DO NOTHING;

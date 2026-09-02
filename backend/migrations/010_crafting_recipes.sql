CREATE TABLE crafting_recipes (
    id UUID PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds > 0),
    ingredients JSONB NOT NULL,
    outputs JSONB NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_crafting_recipes_enabled ON crafting_recipes(enabled);

INSERT INTO crafting_recipes (id, code, name, duration_seconds, ingredients, outputs)
VALUES
('50000000-0000-0000-0000-000000000001', 'reinforced_plate', 'Reinforced Plate', 30,
 '[{"item_code":"scrap_metal","quantity":5},{"item_code":"salvaged_wire","quantity":1}]',
 '[{"item_code":"metal_plate","quantity":1}]'),
('50000000-0000-0000-0000-000000000002', 'wire_bundle', 'Wire Bundle', 20,
 '[{"item_code":"salvaged_wire","quantity":4}]',
 '[{"item_code":"wire_bundle","quantity":1}]'),
('50000000-0000-0000-0000-000000000003', 'fuel_cell', 'Fuel Cell', 45,
 '[{"item_code":"raw_fuel","quantity":3},{"item_code":"chemicals","quantity":1},{"item_code":"salvaged_wire","quantity":2}]',
 '[{"item_code":"fuel_cell","quantity":1}]'),
('50000000-0000-0000-0000-000000000004', 'repair_kit', 'Field Repair Kit', 60,
 '[{"item_code":"metal_plate","quantity":1},{"item_code":"wire_bundle","quantity":1},{"item_code":"chemicals","quantity":1}]',
 '[{"item_code":"repair_kit","quantity":1}]'),
('50000000-0000-0000-0000-000000000005', 'armor_panel', 'Armor Panel', 90,
 '[{"item_code":"metal_plate","quantity":2},{"item_code":"fiber","quantity":2},{"item_code":"chemicals","quantity":1}]',
 '[{"item_code":"armor_panel","quantity":1}]')
ON CONFLICT (id) DO NOTHING;

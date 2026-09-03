-- B2 Hybrid cargo-capacity foundation.
-- Capacity is expressed in abstract cargo units until item mass/loadout data is
-- promoted into the authoritative inventory contract. The deterministic default
-- preserves existing travel payloads while preventing over-capacity plans.
ALTER TABLE vehicles
    ADD COLUMN IF NOT EXISTS cargo_capacity INTEGER NOT NULL DEFAULT 1000
    CHECK (cargo_capacity >= 0);

CREATE INDEX IF NOT EXISTS idx_vehicles_owner_capacity
    ON vehicles(owner_id, cargo_capacity);

CREATE TABLE IF NOT EXISTS vehicle_components (
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    component_code TEXT NOT NULL,
    condition INTEGER NOT NULL DEFAULT 100 CHECK (condition BETWEEN 0 AND 100),
    max_condition INTEGER NOT NULL DEFAULT 100 CHECK (max_condition BETWEEN 1 AND 100),
    armor INTEGER NOT NULL DEFAULT 0 CHECK (armor BETWEEN 0 AND 100),
    PRIMARY KEY (vehicle_id, component_code),
    CHECK (condition <= max_condition)
);

CREATE INDEX IF NOT EXISTS idx_vehicle_components_vehicle
    ON vehicle_components(vehicle_id);

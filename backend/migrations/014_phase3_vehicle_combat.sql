-- IMP-083..IMP-090 Phase 3 vehicle/combat foundation.
-- Additive schema: existing authoritative vehicle/component state remains compatible.
CREATE TABLE IF NOT EXISTS vehicle_chassis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    mass INTEGER NOT NULL DEFAULT 1000 CHECK (mass > 0),
    base_armor INTEGER NOT NULL DEFAULT 0 CHECK (base_armor BETWEEN 0 AND 100),
    fuel_capacity INTEGER NOT NULL DEFAULT 100 CHECK (fuel_capacity > 0),
    module_slots INTEGER NOT NULL DEFAULT 4 CHECK (module_slots >= 0),
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS vehicle_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    slot_type TEXT NOT NULL,
    mass INTEGER NOT NULL DEFAULT 1 CHECK (mass > 0),
    armor INTEGER NOT NULL DEFAULT 0 CHECK (armor BETWEEN 0 AND 100),
    power INTEGER NOT NULL DEFAULT 0,
    fuel_modifier_bps INTEGER NOT NULL DEFAULT 0,
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS vehicle_fittings (
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    slot INTEGER NOT NULL CHECK (slot >= 0),
    module_id UUID NOT NULL REFERENCES vehicle_modules(id),
    version BIGINT NOT NULL DEFAULT 0,
    PRIMARY KEY(vehicle_id, slot),
    UNIQUE(vehicle_id, module_id)
);
CREATE TABLE IF NOT EXISTS weapons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    damage INTEGER NOT NULL CHECK (damage > 0),
    damage_type TEXT NOT NULL,
    range_m INTEGER NOT NULL DEFAULT 100 CHECK (range_m > 0),
    cooldown_seconds INTEGER NOT NULL DEFAULT 5 CHECK (cooldown_seconds > 0),
    ammo_item_definition_id UUID REFERENCES item_definitions(id),
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS vehicle_weapons (
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    slot INTEGER NOT NULL CHECK (slot >= 0),
    weapon_id UUID NOT NULL REFERENCES weapons(id),
    version BIGINT NOT NULL DEFAULT 0,
    PRIMARY KEY(vehicle_id, slot)
);
CREATE TABLE IF NOT EXISTS combat_engagements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attacker_vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    defender_vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    state TEXT NOT NULL DEFAULT 'active',
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,
    version BIGINT NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS combat_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES combat_engagements(id) ON DELETE CASCADE,
    actor_vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    target_vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    weapon_id UUID REFERENCES weapons(id),
    component_code TEXT NOT NULL,
    damage INTEGER NOT NULL CHECK (damage >= 0),
    damage_type TEXT,
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS vehicle_salvage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    owner_id UUID NOT NULL REFERENCES players(id),
    state TEXT NOT NULL DEFAULT 'available',
    recovery_percent INTEGER NOT NULL DEFAULT 50 CHECK (recovery_percent BETWEEN 0 AND 100),
    resolved_at TIMESTAMPTZ,
    version BIGINT NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS vehicle_recovery_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    owner_id UUID NOT NULL REFERENCES players(id),
    settlement_id UUID REFERENCES settlements(id),
    started_at TIMESTAMPTZ NOT NULL,
    completes_at TIMESTAMPTZ NOT NULL,
    state TEXT NOT NULL DEFAULT 'running',
    cost BIGINT NOT NULL DEFAULT 0 CHECK (cost >= 0),
    idempotency_key TEXT NOT NULL UNIQUE,
    version BIGINT NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS convoys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES players(id),
    name TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'active',
    version BIGINT NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS convoy_members (
    convoy_id UUID NOT NULL REFERENCES convoys(id) ON DELETE CASCADE,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    role TEXT NOT NULL DEFAULT 'escort',
    PRIMARY KEY(convoy_id, vehicle_id)
);
CREATE INDEX IF NOT EXISTS idx_combat_engagements_vehicle ON combat_engagements(attacker_vehicle_id, defender_vehicle_id, state);
CREATE INDEX IF NOT EXISTS idx_recovery_due ON vehicle_recovery_jobs(state, completes_at);

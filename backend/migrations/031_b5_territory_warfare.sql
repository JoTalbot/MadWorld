-- B5 Territory Warfare: contests, defenses, supply, siege and strategic objectives.
ALTER TABLE territory_claims ADD COLUMN IF NOT EXISTS claim_cost BIGINT NOT NULL DEFAULT 0;
ALTER TABLE territory_claims ADD COLUMN IF NOT EXISTS upkeep_per_tick BIGINT NOT NULL DEFAULT 0;
ALTER TABLE territory_claims ADD COLUMN IF NOT EXISTS contested_until TIMESTAMPTZ;
CREATE TABLE IF NOT EXISTS territory_checkpoints (
 id UUID PRIMARY KEY,
 region_id TEXT NOT NULL REFERENCES world_regions(id),
 name TEXT NOT NULL,
 controller_corporation_id UUID REFERENCES corporations(id),
 defense_bps INTEGER NOT NULL DEFAULT 5000 CHECK(defense_bps BETWEEN 0 AND 10000),
 condition_bps INTEGER NOT NULL DEFAULT 10000 CHECK(condition_bps BETWEEN 0 AND 10000),
 version BIGINT NOT NULL DEFAULT 0,
 UNIQUE(region_id,name)
);
CREATE TABLE IF NOT EXISTS territory_supply_lines (
 id UUID PRIMARY KEY,
 region_id TEXT NOT NULL REFERENCES world_regions(id),
 source_target_id TEXT NOT NULL,
 destination_target_id TEXT NOT NULL,
 owner_corporation_id UUID NOT NULL REFERENCES corporations(id),
 capacity BIGINT NOT NULL CHECK(capacity>0),
 current_supply BIGINT NOT NULL DEFAULT 0 CHECK(current_supply>=0),
 disruption_bps INTEGER NOT NULL DEFAULT 0 CHECK(disruption_bps BETWEEN 0 AND 10000),
 state VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
 version BIGINT NOT NULL DEFAULT 0,
 UNIQUE(region_id,source_target_id,destination_target_id)
);
CREATE TABLE IF NOT EXISTS territory_warfare_operations (
 id UUID PRIMARY KEY,
 region_id TEXT NOT NULL REFERENCES world_regions(id),
 objective_id UUID REFERENCES territory_objectives(id),
 attacker_corporation_id UUID NOT NULL REFERENCES corporations(id),
 defender_corporation_id UUID REFERENCES corporations(id),
 operation_type VARCHAR(24) NOT NULL,
 state VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
 attack_bps INTEGER NOT NULL DEFAULT 0 CHECK(attack_bps BETWEEN 0 AND 10000),
 defense_bps INTEGER NOT NULL DEFAULT 0 CHECK(defense_bps BETWEEN 0 AND 10000),
 opens_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 resolves_at TIMESTAMPTZ,
 version BIGINT NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS territory_warfare_events (
 id UUID PRIMARY KEY,
 operation_id UUID NOT NULL REFERENCES territory_warfare_operations(id),
 event_type VARCHAR(32) NOT NULL,
 actor_corporation_id UUID REFERENCES corporations(id),
 payload JSONB NOT NULL DEFAULT '{}'::jsonb,
 occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 UNIQUE(operation_id,event_type,occurred_at)
);
CREATE INDEX IF NOT EXISTS idx_warfare_ops_region_state ON territory_warfare_operations(region_id,state);
CREATE INDEX IF NOT EXISTS idx_supply_lines_owner ON territory_supply_lines(owner_corporation_id,state);

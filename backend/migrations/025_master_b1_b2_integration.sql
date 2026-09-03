-- Master Batch B1/B2: bind the deterministic world to gameplay-facing domains.
-- The world simulator remains authoritative for world state; this migration adds
-- durable integration state without granting it direct ownership of player wallets.

CREATE TABLE IF NOT EXISTS world_region_bindings (
  world_region_id TEXT PRIMARY KEY REFERENCES world_regions(id),
  gameplay_region_id UUID NOT NULL UNIQUE REFERENCES regions(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO world_region_bindings(world_region_id, gameplay_region_id)
SELECT 'dust_basin', id FROM regions WHERE code = 'ash-basin'
ON CONFLICT (world_region_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS world_region_effects (
  world_region_id TEXT PRIMARY KEY REFERENCES world_regions(id),
  market_fee_modifier_bps INTEGER NOT NULL DEFAULT 0 CHECK (market_fee_modifier_bps BETWEEN -2500 AND 2500),
  travel_time_modifier_bps INTEGER NOT NULL DEFAULT 0 CHECK (travel_time_modifier_bps BETWEEN -5000 AND 5000),
  travel_risk_modifier_bps INTEGER NOT NULL DEFAULT 0 CHECK (travel_risk_modifier_bps BETWEEN -5000 AND 5000),
  extraction_modifier_bps INTEGER NOT NULL DEFAULT 0 CHECK (extraction_modifier_bps BETWEEN -5000 AND 5000),
  supply_modifier_bps INTEGER NOT NULL DEFAULT 0 CHECK (supply_modifier_bps BETWEEN -10000 AND 10000),
  source_world_event_id UUID REFERENCES world_events(id),
  updated_tick BIGINT NOT NULL DEFAULT 0,
  version BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS world_replay_checkpoints (
  tick BIGINT PRIMARY KEY REFERENCES world_simulation_ticks(tick),
  state_hash TEXT NOT NULL CHECK (length(state_hash) = 64),
  event_hash TEXT NOT NULL CHECK (length(event_hash) = 64),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE world_simulation_ticks ADD COLUMN IF NOT EXISTS state_hash TEXT;
ALTER TABLE world_simulation_ticks ADD COLUMN IF NOT EXISTS event_hash TEXT;
ALTER TABLE world_simulation_ticks ADD COLUMN IF NOT EXISTS duration_ms INTEGER;
ALTER TABLE world_simulation_ticks ADD COLUMN IF NOT EXISTS lag_ms INTEGER;

ALTER TABLE world_convoy_events ADD COLUMN IF NOT EXISTS spawn_tick BIGINT;
ALTER TABLE world_convoy_events ADD COLUMN IF NOT EXISTS travel_ends_tick BIGINT;
ALTER TABLE world_convoy_events ADD COLUMN IF NOT EXISTS resolved_tick BIGINT;
ALTER TABLE world_convoy_events ADD COLUMN IF NOT EXISTS loss_reason TEXT;

ALTER TABLE resource_discoveries ADD COLUMN IF NOT EXISTS discovered_tick BIGINT;
ALTER TABLE resource_discoveries ADD COLUMN IF NOT EXISTS expires_tick BIGINT;

ALTER TABLE dynamic_missions ADD COLUMN IF NOT EXISTS source_event_id UUID REFERENCES world_events(id);
ALTER TABLE dynamic_missions ADD COLUMN IF NOT EXISTS invalidated_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_world_convoys_progress ON world_convoy_events(state, travel_ends_tick);
CREATE INDEX IF NOT EXISTS idx_resource_discoveries_expiry ON resource_discoveries(state, expires_tick);
CREATE INDEX IF NOT EXISTS idx_dynamic_missions_source ON dynamic_missions(source_event_id,state);

-- B2 authoritative travel command state. Resource/fuel/cargo mutation is performed
-- by the gameplay service, never by the world tick simulator itself.
CREATE TABLE IF NOT EXISTS player_travel_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  vehicle_id UUID NOT NULL REFERENCES vehicles(id),
  origin_region_id UUID NOT NULL REFERENCES regions(id),
  destination_region_id UUID NOT NULL REFERENCES regions(id),
  state TEXT NOT NULL DEFAULT 'PLANNED' CHECK (state IN ('PLANNED','TRAVELLING','ARRIVED','INTERRUPTED','LOST','CANCELLED')),
  departure_at TIMESTAMPTZ,
  arrival_at TIMESTAMPTZ,
  planned_duration_seconds INTEGER NOT NULL CHECK (planned_duration_seconds > 0),
  fuel_reserved BIGINT NOT NULL DEFAULT 0 CHECK (fuel_reserved >= 0),
  cargo_weight BIGINT NOT NULL DEFAULT 0 CHECK (cargo_weight >= 0),
  route_risk_bps INTEGER NOT NULL DEFAULT 0 CHECK (route_risk_bps BETWEEN 0 AND 10000),
  world_region_id TEXT REFERENCES world_regions(id),
  idempotency_key TEXT NOT NULL UNIQUE,
  version BIGINT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_player_travel_player_state ON player_travel_sessions(player_id,state,created_at);
CREATE INDEX IF NOT EXISTS idx_player_travel_vehicle_state ON player_travel_sessions(vehicle_id,state);
CREATE UNIQUE INDEX IF NOT EXISTS idx_player_travel_active_vehicle
  ON player_travel_sessions(vehicle_id)
  WHERE state IN ('PLANNED','TRAVELLING');

CREATE TABLE IF NOT EXISTS travel_encounters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  travel_session_id UUID NOT NULL REFERENCES player_travel_sessions(id) ON DELETE CASCADE,
  world_event_id UUID REFERENCES world_events(id),
  encounter_type TEXT NOT NULL CHECK (encounter_type IN ('FACTION','CONVOY','DISASTER','AMBUSH','DISCOVERY')),
  severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
  state TEXT NOT NULL DEFAULT 'PENDING' CHECK (state IN ('PENDING','RESOLVED','ESCAPED','DEFEATED','LOST')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  resolved_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_travel_encounter_event ON travel_encounters(travel_session_id,world_event_id) WHERE world_event_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS salvage_recovery_cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  vehicle_id UUID NOT NULL REFERENCES vehicles(id),
  travel_session_id UUID REFERENCES player_travel_sessions(id),
  state TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK (state IN ('AVAILABLE','CLAIMED','RECOVERED','ABANDONED')),
  recovery_cost BIGINT NOT NULL DEFAULT 0 CHECK (recovery_cost >= 0),
  salvage_value BIGINT NOT NULL DEFAULT 0 CHECK (salvage_value >= 0),
  expires_at TIMESTAMPTZ,
  idempotency_key TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  version BIGINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_salvage_recovery_player ON salvage_recovery_cases(player_id,state,created_at);

CREATE TABLE IF NOT EXISTS world_integration_telemetry (
  id BIGSERIAL PRIMARY KEY,
  tick BIGINT NOT NULL,
  metric_name TEXT NOT NULL,
  metric_value BIGINT NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_world_integration_telemetry_tick ON world_integration_telemetry(tick,metric_name);

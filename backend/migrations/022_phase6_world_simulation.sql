-- Phase 6 Hybrid: deterministic world simulation, factions, pressures, events, discoveries, disasters and missions.
CREATE TABLE IF NOT EXISTS world_simulation_state (
  id SMALLINT PRIMARY KEY CHECK (id = 1),
  season INTEGER NOT NULL DEFAULT 1 CHECK (season > 0),
  tick BIGINT NOT NULL DEFAULT 0 CHECK (tick >= 0),
  last_tick_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  version BIGINT NOT NULL DEFAULT 0
);
INSERT INTO world_simulation_state(id) VALUES (1) ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS world_factions (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  doctrine TEXT NOT NULL,
  aggression_bps INTEGER NOT NULL DEFAULT 5000 CHECK (aggression_bps BETWEEN 0 AND 10000),
  logistics_bps INTEGER NOT NULL DEFAULT 5000 CHECK (logistics_bps BETWEEN 0 AND 10000),
  version BIGINT NOT NULL DEFAULT 0
);
INSERT INTO world_factions(id,name,doctrine,aggression_bps,logistics_bps) VALUES
 ('rust_legion','Rust Legion','raider',8000,3500),
 ('dust_collective','Dust Collective','merchant',3500,8000),
 ('free_scavengers','Free Scavengers','survivalist',5500,5500)
ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS world_faction_regions (
  faction_id TEXT NOT NULL REFERENCES world_factions(id),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  influence_bps INTEGER NOT NULL DEFAULT 0 CHECK (influence_bps BETWEEN 0 AND 10000),
  hostility_bps INTEGER NOT NULL DEFAULT 0 CHECK (hostility_bps BETWEEN -10000 AND 10000),
  supply_bps INTEGER NOT NULL DEFAULT 5000 CHECK (supply_bps BETWEEN 0 AND 10000),
  version BIGINT NOT NULL DEFAULT 0,
  PRIMARY KEY(faction_id,region_id)
);
INSERT INTO world_faction_regions(faction_id,region_id,influence_bps,hostility_bps,supply_bps)
SELECT f.id,r.id,CASE r.id WHEN 'dust_basin' THEN 6500 WHEN 'iron_ruins' THEN 4500 ELSE 3000 END,0,5000
FROM world_factions f CROSS JOIN world_regions r
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS regional_resource_pressure (
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  resource_type TEXT NOT NULL,
  target_quantity BIGINT NOT NULL DEFAULT 1000 CHECK (target_quantity > 0),
  available_quantity BIGINT NOT NULL DEFAULT 1000 CHECK (available_quantity >= 0),
  pressure_bps INTEGER NOT NULL DEFAULT 0 CHECK (pressure_bps BETWEEN -10000 AND 10000),
  trend_bps INTEGER NOT NULL DEFAULT 0 CHECK (trend_bps BETWEEN -5000 AND 5000),
  version BIGINT NOT NULL DEFAULT 0,
  PRIMARY KEY(region_id,resource_type)
);
INSERT INTO regional_resource_pressure(region_id,resource_type,target_quantity,available_quantity)
SELECT id,'scrap',1000,1000 FROM world_regions ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS world_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tick BIGINT NOT NULL,
  region_id TEXT REFERENCES world_regions(id),
  faction_id TEXT REFERENCES world_factions(id),
  event_type TEXT NOT NULL,
  severity INTEGER NOT NULL DEFAULT 1 CHECK (severity BETWEEN 1 AND 5),
  state TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (state IN ('ACTIVE','RESOLVED','EXPIRED')),
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  resolved_at TIMESTAMPTZ,
  UNIQUE(tick,event_type,region_id,faction_id)
);
CREATE INDEX IF NOT EXISTS idx_world_events_region_time ON world_events(region_id,created_at);
CREATE INDEX IF NOT EXISTS idx_world_events_state ON world_events(state,created_at);

CREATE TABLE IF NOT EXISTS world_convoy_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  world_event_id UUID NOT NULL UNIQUE REFERENCES world_events(id),
  origin_region_id TEXT NOT NULL REFERENCES world_regions(id),
  destination_region_id TEXT NOT NULL REFERENCES world_regions(id),
  faction_id TEXT REFERENCES world_factions(id),
  cargo_type TEXT NOT NULL,
  cargo_quantity BIGINT NOT NULL CHECK (cargo_quantity > 0),
  danger_bps INTEGER NOT NULL CHECK (danger_bps BETWEEN 0 AND 10000),
  state TEXT NOT NULL DEFAULT 'SPAWNED' CHECK (state IN ('SPAWNED','TRAVELLING','ARRIVED','LOST')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS resource_discoveries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  world_event_id UUID NOT NULL UNIQUE REFERENCES world_events(id),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  resource_type TEXT NOT NULL,
  quantity BIGINT NOT NULL CHECK (quantity > 0),
  expires_at TIMESTAMPTZ,
  discovered_by TEXT NOT NULL DEFAULT 'world_simulation',
  state TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK (state IN ('AVAILABLE','EXHAUSTED','EXPIRED'))
);

CREATE TABLE IF NOT EXISTS world_disasters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  world_event_id UUID NOT NULL UNIQUE REFERENCES world_events(id),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  disaster_type TEXT NOT NULL,
  severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
  starts_at TIMESTAMPTZ NOT NULL,
  ends_at TIMESTAMPTZ,
  state TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (state IN ('ACTIVE','RESOLVED','EXPIRED'))
);

CREATE TABLE IF NOT EXISTS catastrophe_zones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  disaster_id UUID NOT NULL UNIQUE REFERENCES world_disasters(id),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  hazard_bps INTEGER NOT NULL CHECK (hazard_bps BETWEEN 0 AND 10000),
  travel_risk_bps INTEGER NOT NULL CHECK (travel_risk_bps BETWEEN 0 AND 10000),
  extraction_modifier_bps INTEGER NOT NULL CHECK (extraction_modifier_bps BETWEEN -10000 AND 0),
  state TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (state IN ('ACTIVE','RESOLVED'))
);

CREATE TABLE IF NOT EXISTS dynamic_missions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  world_event_id UUID NOT NULL REFERENCES world_events(id),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  mission_type TEXT NOT NULL,
  title TEXT NOT NULL,
  reward_credits BIGINT NOT NULL CHECK (reward_credits >= 0),
  risk_bps INTEGER NOT NULL CHECK (risk_bps BETWEEN 0 AND 10000),
  state TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK (state IN ('AVAILABLE','ACCEPTED','COMPLETED','EXPIRED')),
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_dynamic_missions_region_state ON dynamic_missions(region_id,state,expires_at);

CREATE TABLE IF NOT EXISTS world_simulation_ticks (
  tick BIGINT PRIMARY KEY,
  season INTEGER NOT NULL,
  seed TEXT NOT NULL,
  generated_events INTEGER NOT NULL DEFAULT 0,
  generated_missions INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS world_simulation_event_log (
  sequence BIGSERIAL PRIMARY KEY,
  tick BIGINT NOT NULL,
  event_id UUID NOT NULL REFERENCES world_events(id),
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(tick,event_id)
);

-- Phase 5 Hybrid: persistent territory, infrastructure, routes, resources and strategic objectives.
CREATE TABLE IF NOT EXISTS world_regions (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  security TEXT NOT NULL DEFAULT 'frontier',
  version BIGINT NOT NULL DEFAULT 0
);
INSERT INTO world_regions(id,name,security) VALUES
 ('dust_basin','Dust Basin','lawless'),
 ('iron_ruins','Iron Ruins','contested'),
 ('salt_coast','Salt Coast','frontier')
ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS territory_claims (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  claimant_corporation_id UUID NOT NULL REFERENCES corporations(id),
  state TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (state IN ('ACTIVE','CONTESTED','RELEASED')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  version BIGINT NOT NULL DEFAULT 0,
  UNIQUE(region_id,target_type,target_id)
);
CREATE TABLE IF NOT EXISTS territory_control (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  controller_corporation_id UUID REFERENCES corporations(id),
  controlled_since TIMESTAMPTZ,
  version BIGINT NOT NULL DEFAULT 0,
  UNIQUE(region_id,target_type,target_id)
);
CREATE TABLE IF NOT EXISTS territory_control_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  previous_controller UUID REFERENCES corporations(id),
  new_controller UUID REFERENCES corporations(id),
  reason TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS territory_infrastructure (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  settlement_id UUID,
  infrastructure_type TEXT NOT NULL,
  name TEXT NOT NULL,
  controller_corporation_id UUID REFERENCES corporations(id),
  condition_bps INTEGER NOT NULL DEFAULT 10000 CHECK (condition_bps BETWEEN 0 AND 10000),
  upkeep_bps INTEGER NOT NULL DEFAULT 0 CHECK (upkeep_bps BETWEEN 0 AND 10000),
  version BIGINT NOT NULL DEFAULT 0,
  UNIQUE(region_id,infrastructure_type,name)
);
CREATE TABLE IF NOT EXISTS territory_roads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  from_node TEXT NOT NULL,
  to_node TEXT NOT NULL,
  controller_corporation_id UUID REFERENCES corporations(id),
  travel_modifier_bps INTEGER NOT NULL DEFAULT 0 CHECK (travel_modifier_bps BETWEEN -5000 AND 5000),
  risk_modifier_bps INTEGER NOT NULL DEFAULT 0 CHECK (risk_modifier_bps BETWEEN -5000 AND 5000),
  version BIGINT NOT NULL DEFAULT 0,
  UNIQUE(region_id,from_node,to_node)
);
CREATE TABLE IF NOT EXISTS territory_resource_sites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  resource_type TEXT NOT NULL,
  name TEXT NOT NULL,
  controller_corporation_id UUID REFERENCES corporations(id),
  capacity BIGINT NOT NULL CHECK (capacity > 0),
  remaining BIGINT NOT NULL CHECK (remaining >= 0),
  renewal_rate BIGINT NOT NULL DEFAULT 0 CHECK (renewal_rate >= 0),
  extraction_limit BIGINT NOT NULL DEFAULT 100 CHECK (extraction_limit > 0),
  version BIGINT NOT NULL DEFAULT 0,
  UNIQUE(region_id,resource_type,name),
  CHECK (remaining <= capacity)
);
CREATE TABLE IF NOT EXISTS territory_modifiers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  source_type TEXT NOT NULL,
  source_id TEXT NOT NULL,
  market_fee_bps INTEGER NOT NULL DEFAULT 0 CHECK (market_fee_bps BETWEEN -2500 AND 2500),
  travel_time_bps INTEGER NOT NULL DEFAULT 0 CHECK (travel_time_bps BETWEEN -5000 AND 5000),
  travel_risk_bps INTEGER NOT NULL DEFAULT 0 CHECK (travel_risk_bps BETWEEN -5000 AND 5000),
  extraction_bps INTEGER NOT NULL DEFAULT 0 CHECK (extraction_bps BETWEEN -5000 AND 5000),
  version BIGINT NOT NULL DEFAULT 0,
  UNIQUE(region_id,source_type,source_id)
);
CREATE TABLE IF NOT EXISTS territory_objectives (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'SCHEDULED' CHECK (state IN ('SCHEDULED','OPEN','CONTESTED','RESOLVED','CLOSED')),
  opens_at TIMESTAMPTZ NOT NULL,
  contest_ends_at TIMESTAMPTZ NOT NULL,
  resolved_at TIMESTAMPTZ,
  winner_corporation_id UUID REFERENCES corporations(id),
  version BIGINT NOT NULL DEFAULT 0,
  CHECK (contest_ends_at > opens_at)
);
CREATE TABLE IF NOT EXISTS territory_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  event_type TEXT NOT NULL,
  aggregate_type TEXT NOT NULL,
  aggregate_id UUID NOT NULL,
  actor_corporation_id UUID REFERENCES corporations(id),
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_territory_claims_corp ON territory_claims(claimant_corporation_id,state);
CREATE INDEX IF NOT EXISTS idx_territory_control_region ON territory_control(region_id,target_type);
CREATE INDEX IF NOT EXISTS idx_territory_objectives_due ON territory_objectives(state,opens_at,contest_ends_at);
CREATE INDEX IF NOT EXISTS idx_territory_resources_region ON territory_resource_sites(region_id,resource_type);
CREATE INDEX IF NOT EXISTS idx_territory_events_region ON territory_events(region_id,occurred_at);

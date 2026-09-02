-- B1 concrete world→economy bridge. Market matching remains owned by the market domain;
-- this table is the durable normalized signal it consumes.
CREATE TABLE IF NOT EXISTS world_economy_signals (
  world_event_id UUID PRIMARY KEY REFERENCES world_events(id) ON DELETE CASCADE,
  region_id TEXT NOT NULL REFERENCES world_regions(id),
  event_type TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  pressure_bps INTEGER NOT NULL CHECK (pressure_bps BETWEEN -10000 AND 10000),
  scarcity_bps INTEGER NOT NULL CHECK (scarcity_bps BETWEEN 0 AND 10000),
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_world_economy_signals_region ON world_economy_signals(region_id,created_at);

-- World-generated missions are uniquely tied to their source event so retries
-- cannot create duplicate player-facing jobs.
CREATE UNIQUE INDEX IF NOT EXISTS idx_dynamic_missions_source_unique
  ON dynamic_missions(source_event_id)
  WHERE source_event_id IS NOT NULL;

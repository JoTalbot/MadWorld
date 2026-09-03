-- B4 NPC faction simulation: bounded, deterministic, authoritative actions.
-- world_factions uses stable text identifiers (migration 022); preserve that authority boundary here.
CREATE TABLE IF NOT EXISTS npc_faction_actions (
 id UUID PRIMARY KEY,
 faction_id TEXT NOT NULL REFERENCES world_factions(id),
 region_id VARCHAR(64) NOT NULL,
 action_type VARCHAR(32) NOT NULL,
 target_region_id VARCHAR(64),
 priority INTEGER NOT NULL,
 rationale JSONB NOT NULL DEFAULT '{}'::jsonb,
 state VARCHAR(16) NOT NULL DEFAULT 'PLANNED',
 scheduled_tick BIGINT NOT NULL,
 executed_tick BIGINT,
 version BIGINT NOT NULL DEFAULT 0,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 UNIQUE(faction_id, scheduled_tick, action_type, region_id)
);
CREATE INDEX IF NOT EXISTS idx_npc_faction_actions_tick ON npc_faction_actions(scheduled_tick,state);
CREATE TABLE IF NOT EXISTS faction_diplomacy (
 faction_id TEXT NOT NULL REFERENCES world_factions(id),
 other_faction_id TEXT NOT NULL REFERENCES world_factions(id),
 relation_bps INTEGER NOT NULL DEFAULT 0 CHECK(relation_bps BETWEEN -10000 AND 10000),
 state VARCHAR(24) NOT NULL DEFAULT 'NEUTRAL',
 version BIGINT NOT NULL DEFAULT 0,
 updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 PRIMARY KEY(faction_id,other_faction_id),
 CHECK(faction_id<>other_faction_id)
);
CREATE TABLE IF NOT EXISTS faction_action_events (
 id UUID PRIMARY KEY,
 action_id UUID NOT NULL REFERENCES npc_faction_actions(id),
 faction_id TEXT NOT NULL REFERENCES world_factions(id),
 region_id VARCHAR(64) NOT NULL,
 action_type VARCHAR(32) NOT NULL,
 tick BIGINT NOT NULL,
 payload JSONB NOT NULL DEFAULT '{}'::jsonb,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 UNIQUE(action_id)
);

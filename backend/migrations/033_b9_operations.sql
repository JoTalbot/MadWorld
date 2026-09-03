CREATE TABLE IF NOT EXISTS device_push_tokens (
    player_id TEXT NOT NULL,
    token TEXT NOT NULL,
    platform TEXT NOT NULL CHECK (platform IN ('android')),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (player_id, token)
);

CREATE INDEX IF NOT EXISTS idx_device_push_tokens_enabled
    ON device_push_tokens (player_id) WHERE enabled = TRUE;

CREATE TABLE IF NOT EXISTS analytics_events (
    event_id UUID PRIMARY KEY,
    player_id TEXT,
    event_name TEXT NOT NULL,
    event_version INTEGER NOT NULL DEFAULT 1,
    properties JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analytics_events_name_time
    ON analytics_events (event_name, occurred_at DESC);

CREATE TABLE IF NOT EXISTS liveops_flags (
    flag_key TEXT PRIMARY KEY,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

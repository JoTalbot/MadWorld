-- B10: shared (PostgreSQL-backed) abuse controls so several API processes/replicas
-- enforce one rate limit, one replay window and one abuse score per client.
-- Rows are short-lived; every write path also prunes expired rows for its key,
-- and the world tick worker/operators may run the bulk prune periodically.

CREATE TABLE IF NOT EXISTS abuse_control_hits (
    id BIGSERIAL PRIMARY KEY,
    control_key TEXT NOT NULL,
    hit_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_abuse_control_hits_key_time ON abuse_control_hits(control_key, hit_at);

CREATE TABLE IF NOT EXISTS abuse_control_replays (
    replay_key TEXT PRIMARY KEY,
    seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_abuse_control_replays_expiry ON abuse_control_replays(expires_at);

CREATE TABLE IF NOT EXISTS abuse_control_scores (
    actor TEXT PRIMARY KEY,
    score INTEGER NOT NULL CHECK (score >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

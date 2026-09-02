CREATE TABLE player_settlement_state (
    player_id UUID PRIMARY KEY REFERENCES players(id) ON DELETE CASCADE,
    settlement_id UUID NOT NULL REFERENCES settlements(id),
    region TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1 CHECK (level >= 1),
    modules JSONB NOT NULL DEFAULT '{"garage":1,"warehouse":1,"workshop":1,"contracts":1,"market":1}'::jsonb,
    version INTEGER NOT NULL DEFAULT 0 CHECK (version >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_player_settlement_state_settlement ON player_settlement_state(settlement_id);

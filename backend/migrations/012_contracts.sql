CREATE TABLE contract_templates (
 id UUID PRIMARY KEY,
 code TEXT NOT NULL UNIQUE,
 title TEXT NOT NULL,
 description TEXT NOT NULL DEFAULT '',
 objectives JSONB NOT NULL,
 reward JSONB NOT NULL DEFAULT '{}'::jsonb,
 deadline_seconds INTEGER,
 risk TEXT NOT NULL DEFAULT 'low',
 faction_id TEXT,
 reputation_required INTEGER NOT NULL DEFAULT 0,
 prerequisites JSONB NOT NULL DEFAULT '[]'::jsonb,
 chain_next JSONB NOT NULL DEFAULT '[]'::jsonb,
 enabled BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE contracts (
 id UUID PRIMARY KEY,
 template_id UUID NOT NULL REFERENCES contract_templates(id),
 player_id UUID NOT NULL REFERENCES players(id),
 state TEXT NOT NULL,
 offered_at TIMESTAMPTZ NOT NULL,
 accepted_at TIMESTAMPTZ,
 deadline_at TIMESTAMPTZ,
 progress JSONB NOT NULL DEFAULT '{}'::jsonb,
 reward_granted BOOLEAN NOT NULL DEFAULT FALSE,
 version BIGINT NOT NULL DEFAULT 0
);
CREATE INDEX idx_contracts_player ON contracts(player_id, state, offered_at);
CREATE TABLE faction_reputation (
 player_id UUID NOT NULL REFERENCES players(id),
 faction_id TEXT NOT NULL,
 reputation INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(player_id, faction_id)
);

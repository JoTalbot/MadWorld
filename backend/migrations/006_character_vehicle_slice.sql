ALTER TABLE vehicles
    ADD COLUMN state TEXT NOT NULL DEFAULT 'active' CHECK (state IN ('active', 'destroyed', 'stored')),
    ADD COLUMN version INTEGER NOT NULL DEFAULT 0 CHECK (version >= 0);

CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL UNIQUE REFERENCES players(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1 CHECK (level > 0),
    version INTEGER NOT NULL DEFAULT 0 CHECK (version >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_vehicles_owner ON vehicles(owner_id);

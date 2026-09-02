ALTER TABLE resource_nodes
    ADD COLUMN last_gathered_at TIMESTAMPTZ;

CREATE INDEX idx_resource_nodes_available
    ON resource_nodes(region_id, resource_item_definition_id, quantity);

CREATE TABLE IF NOT EXISTS player_settlement_storage (
    player_id UUID PRIMARY KEY REFERENCES players(id) ON DELETE CASCADE,
    settlement_id UUID NOT NULL REFERENCES settlements(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

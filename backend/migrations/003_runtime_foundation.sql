-- Runtime persistence foundation for accepted IMP-012 optimistic concurrency.
-- inventory_items is a mutable aggregate row and therefore needs its own version.

ALTER TABLE inventory_items
    ADD COLUMN IF NOT EXISTS version BIGINT NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_inventory_items_version
    ON inventory_items(inventory_id, item_definition_id, version);

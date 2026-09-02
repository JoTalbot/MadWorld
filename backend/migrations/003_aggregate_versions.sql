-- Extend optimistic concurrency to wallet and inventory-item aggregates.

ALTER TABLE wallets
    ADD COLUMN IF NOT EXISTS version BIGINT NOT NULL DEFAULT 0;

ALTER TABLE inventory_items
    ADD COLUMN IF NOT EXISTS version BIGINT NOT NULL DEFAULT 0;

ALTER TABLE wallets
    ADD CONSTRAINT wallets_version_nonnegative_check
    CHECK (version >= 0);

ALTER TABLE inventory_items
    ADD CONSTRAINT inventory_items_version_nonnegative_check
    CHECK (version >= 0);

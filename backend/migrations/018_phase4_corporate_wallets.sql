-- Phase 4: allow corporation-owned wallets while preserving one wallet per player.
-- This is infrastructure hardening for the accepted shared-wallet model.
ALTER TABLE wallets ALTER COLUMN owner_id DROP NOT NULL;
ALTER TABLE wallets DROP CONSTRAINT IF EXISTS wallets_owner_id_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_wallet_player_owner
  ON wallets(owner_id)
  WHERE owner_id IS NOT NULL;

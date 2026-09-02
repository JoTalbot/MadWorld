-- Phase 4 integrity hardening: enforce uniqueness that PostgreSQL NULL semantics
-- cannot guarantee with the original composite UNIQUE constraints.
--
-- Wallets now support both player-owned and shared corporate wallets. Existing
-- player wallets keep their owner_id; corporate wallets intentionally use NULL.
ALTER TABLE wallets ALTER COLUMN owner_id DROP NOT NULL;
ALTER TABLE wallets DROP CONSTRAINT IF EXISTS wallets_owner_id_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_wallets_player_owner
  ON wallets(owner_id)
  WHERE owner_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_social_reputation_player_target
  ON social_reputation(subject_player_id, target_type, target_id)
  WHERE subject_player_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_social_reputation_corporation_target
  ON social_reputation(subject_corporation_id, target_type, target_id)
  WHERE subject_corporation_id IS NOT NULL;

-- MadWorld currently models one primary corporation membership per player.
-- This makes the application invariant database-enforced under concurrent requests.
CREATE UNIQUE INDEX IF NOT EXISTS uq_corporation_members_one_corporation
  ON corporation_members(player_id);

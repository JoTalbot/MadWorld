-- Phase 4 integrity hardening: enforce uniqueness that PostgreSQL NULL semantics
-- cannot guarantee with the original composite UNIQUE constraints.
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

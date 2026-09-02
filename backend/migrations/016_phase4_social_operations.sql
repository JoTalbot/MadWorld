-- Phase 4 authoritative operations: alliance membership, social contract lifecycle,
-- corporate wallet movements and explicit reputation history.
CREATE TABLE IF NOT EXISTS alliance_invitations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alliance_id UUID NOT NULL REFERENCES alliances(id) ON DELETE CASCADE,
  corporation_id UUID NOT NULL REFERENCES corporations(id) ON DELETE CASCADE,
  invited_by UUID NOT NULL REFERENCES players(id),
  state TEXT NOT NULL DEFAULT 'OFFERED',
  expires_at TIMESTAMPTZ,
  version INTEGER NOT NULL DEFAULT 0,
  UNIQUE(alliance_id, corporation_id)
);
CREATE TABLE IF NOT EXISTS social_contract_escrow (
  contract_id UUID PRIMARY KEY REFERENCES social_contracts(id) ON DELETE CASCADE,
  wallet_id UUID NOT NULL REFERENCES wallets(id),
  amount BIGINT NOT NULL CHECK (amount >= 0),
  state TEXT NOT NULL DEFAULT 'LOCKED',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  released_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS social_reputation_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject_player_id UUID REFERENCES players(id),
  subject_corporation_id UUID REFERENCES corporations(id),
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  delta INTEGER NOT NULL,
  reason TEXT NOT NULL,
  actor_id UUID REFERENCES players(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK ((subject_player_id IS NOT NULL) <> (subject_corporation_id IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS idx_rep_history_subject_player ON social_reputation_history(subject_player_id, created_at);
CREATE INDEX IF NOT EXISTS idx_rep_history_subject_corp ON social_reputation_history(subject_corporation_id, created_at);

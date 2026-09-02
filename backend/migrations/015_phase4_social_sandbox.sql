-- Phase 4: social sandbox foundation.
CREATE TABLE IF NOT EXISTS corporations (
  id UUID PRIMARY KEY,
  owner_id UUID NOT NULL REFERENCES players(id),
  code TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  tax_bps INTEGER NOT NULL DEFAULT 0 CHECK (tax_bps BETWEEN 0 AND 10000),
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  wallet_id UUID REFERENCES wallets(id),
  version INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS corporation_members (
  corporation_id UUID NOT NULL REFERENCES corporations(id) ON DELETE CASCADE,
  player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'MEMBER',
  joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  version INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (corporation_id, player_id)
);
CREATE TABLE IF NOT EXISTS corporation_permissions (
  corporation_id UUID NOT NULL REFERENCES corporations(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  permission TEXT NOT NULL,
  PRIMARY KEY (corporation_id, role, permission)
);
CREATE TABLE IF NOT EXISTS corporation_hangars (
  id UUID PRIMARY KEY,
  corporation_id UUID NOT NULL REFERENCES corporations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  capacity INTEGER NOT NULL CHECK (capacity > 0),
  version INTEGER NOT NULL DEFAULT 0,
  UNIQUE(corporation_id, name)
);
CREATE TABLE IF NOT EXISTS corporation_assets (
  id UUID PRIMARY KEY,
  corporation_id UUID NOT NULL REFERENCES corporations(id) ON DELETE CASCADE,
  asset_type TEXT NOT NULL,
  asset_id UUID NOT NULL,
  hangar_id UUID REFERENCES corporation_hangars(id),
  assigned_to UUID REFERENCES players(id),
  version INTEGER NOT NULL DEFAULT 0,
  UNIQUE(corporation_id, asset_type, asset_id)
);
CREATE TABLE IF NOT EXISTS alliances (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  code TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  version INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS alliance_members (
  alliance_id UUID NOT NULL REFERENCES alliances(id) ON DELETE CASCADE,
  corporation_id UUID NOT NULL REFERENCES corporations(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'MEMBER',
  joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  version INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (alliance_id, corporation_id)
);
CREATE TABLE IF NOT EXISTS diplomatic_relations (
  id UUID PRIMARY KEY,
  source_corporation_id UUID NOT NULL REFERENCES corporations(id) ON DELETE CASCADE,
  target_corporation_id UUID NOT NULL REFERENCES corporations(id) ON DELETE CASCADE,
  relation TEXT NOT NULL DEFAULT 'NEUTRAL',
  standing INTEGER NOT NULL DEFAULT 0 CHECK (standing BETWEEN -10000 AND 10000),
  trade_allowed BOOLEAN NOT NULL DEFAULT TRUE,
  transit_allowed BOOLEAN NOT NULL DEFAULT FALSE,
  version INTEGER NOT NULL DEFAULT 0,
  UNIQUE(source_corporation_id, target_corporation_id),
  CHECK(source_corporation_id <> target_corporation_id)
);
CREATE TABLE IF NOT EXISTS social_contracts (
  id UUID PRIMARY KEY,
  issuer_corporation_id UUID NOT NULL REFERENCES corporations(id),
  counterparty_corporation_id UUID REFERENCES corporations(id),
  counterparty_player_id UUID REFERENCES players(id),
  contract_type TEXT NOT NULL,
  terms JSONB NOT NULL DEFAULT '{}'::jsonb,
  state TEXT NOT NULL DEFAULT 'OFFERED',
  expires_at TIMESTAMPTZ,
  version INTEGER NOT NULL DEFAULT 0,
  CHECK ((counterparty_corporation_id IS NOT NULL) <> (counterparty_player_id IS NOT NULL))
);
CREATE TABLE IF NOT EXISTS social_reputation (
  id UUID PRIMARY KEY,
  subject_player_id UUID REFERENCES players(id),
  subject_corporation_id UUID REFERENCES corporations(id),
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  standing INTEGER NOT NULL DEFAULT 0 CHECK (standing BETWEEN -10000 AND 10000),
  version INTEGER NOT NULL DEFAULT 0,
  CHECK ((subject_player_id IS NOT NULL) <> (subject_corporation_id IS NOT NULL)),
  UNIQUE(subject_player_id, target_type, target_id),
  UNIQUE(subject_corporation_id, target_type, target_id)
);
CREATE TABLE IF NOT EXISTS manufacturers (
  id UUID PRIMARY KEY,
  corporation_id UUID NOT NULL UNIQUE REFERENCES corporations(id),
  brand_name TEXT NOT NULL UNIQUE,
  quality_rating INTEGER NOT NULL DEFAULT 5000 CHECK (quality_rating BETWEEN 0 AND 10000),
  reputation INTEGER NOT NULL DEFAULT 0 CHECK (reputation BETWEEN -10000 AND 10000),
  version INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_corp_members_player ON corporation_members(player_id);
CREATE INDEX IF NOT EXISTS idx_alliance_members_corp ON alliance_members(corporation_id);
CREATE INDEX IF NOT EXISTS idx_social_contracts_state ON social_contracts(state, expires_at);
CREATE INDEX IF NOT EXISTS idx_social_rep_target ON social_reputation(target_type, target_id);

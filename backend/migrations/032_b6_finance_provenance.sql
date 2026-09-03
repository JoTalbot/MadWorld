-- B6 Finance & Provenance: secured credit, collateral, insurance, financing and immutable asset history.
-- Money remains authoritative in ledger_entries; these tables only record financial contracts and claims.
CREATE TABLE IF NOT EXISTS finance_credit_agreements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  borrower_player_id UUID NOT NULL REFERENCES players(id),
  lender_player_id UUID REFERENCES players(id),
  principal BIGINT NOT NULL CHECK (principal > 0),
  outstanding BIGINT NOT NULL CHECK (outstanding >= 0 AND outstanding <= principal),
  interest_bps INTEGER NOT NULL DEFAULT 0 CHECK (interest_bps BETWEEN 0 AND 10000),
  status VARCHAR(24) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DEFAULTED','REPAID','RECOVERED','CANCELLED')),
  due_at TIMESTAMPTZ NOT NULL,
  version BIGINT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_finance_credit_borrower ON finance_credit_agreements(borrower_player_id,status);
CREATE INDEX IF NOT EXISTS idx_finance_credit_due ON finance_credit_agreements(status,due_at);

CREATE TABLE IF NOT EXISTS finance_collateral (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  credit_agreement_id UUID NOT NULL REFERENCES finance_credit_agreements(id) ON DELETE CASCADE,
  asset_id UUID NOT NULL,
  collateral_value BIGINT NOT NULL CHECK (collateral_value > 0),
  status VARCHAR(20) NOT NULL DEFAULT 'PLEDGED' CHECK (status IN ('PLEDGED','RELEASED','SEIZED')),
  version BIGINT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(credit_agreement_id,asset_id)
);
CREATE INDEX IF NOT EXISTS idx_finance_collateral_asset ON finance_collateral(asset_id,status);

CREATE TABLE IF NOT EXISTS finance_insurance_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  holder_player_id UUID NOT NULL REFERENCES players(id),
  asset_id UUID NOT NULL,
  coverage_value BIGINT NOT NULL CHECK (coverage_value > 0),
  premium BIGINT NOT NULL CHECK (premium >= 0),
  deductible BIGINT NOT NULL DEFAULT 0 CHECK (deductible >= 0 AND deductible <= coverage_value),
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','EXPIRED','CLAIMED','CANCELLED')),
  expires_at TIMESTAMPTZ NOT NULL,
  version BIGINT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_finance_insurance_asset ON finance_insurance_policies(asset_id,status);

CREATE TABLE IF NOT EXISTS finance_investments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  investor_player_id UUID NOT NULL REFERENCES players(id),
  principal BIGINT NOT NULL CHECK (principal > 0),
  target_type VARCHAR(32) NOT NULL,
  target_id UUID NOT NULL,
  return_bps INTEGER NOT NULL CHECK (return_bps BETWEEN -10000 AND 100000),
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','SETTLED','DEFAULTED','CANCELLED')),
  maturity_at TIMESTAMPTZ NOT NULL,
  version BIGINT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_finance_investor_status ON finance_investments(investor_player_id,status);

CREATE TABLE IF NOT EXISTS asset_provenance_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id UUID NOT NULL,
  event_type VARCHAR(40) NOT NULL,
  owner_player_id UUID REFERENCES players(id),
  quality_rating INTEGER CHECK (quality_rating BETWEEN 0 AND 10000),
  manufacturer_id UUID,
  production_batch VARCHAR(128),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(asset_id,recorded_at,event_type)
);
CREATE INDEX IF NOT EXISTS idx_asset_provenance_history_asset ON asset_provenance_history(asset_id,recorded_at);

CREATE TABLE IF NOT EXISTS finance_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_key TEXT NOT NULL UNIQUE,
  aggregate_type VARCHAR(40) NOT NULL,
  aggregate_id UUID NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  actor_id UUID REFERENCES players(id),
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_finance_events_aggregate ON finance_events(aggregate_type,aggregate_id,created_at);

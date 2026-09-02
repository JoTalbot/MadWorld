-- Phase 4 completion hardening: escrow lifecycle and manufacturer provenance.
ALTER TABLE social_contract_escrow
  ADD CONSTRAINT social_contract_escrow_state_check
  CHECK (state IN ('LOCKED','RELEASED','REFUNDED'));
ALTER TABLE alliance_invitations
  ADD CONSTRAINT alliance_invitation_state_check
  CHECK (state IN ('OFFERED','ACCEPTED','DECLINED','EXPIRED'));

CREATE TABLE IF NOT EXISTS asset_provenance (
  asset_id UUID PRIMARY KEY,
  manufacturer_id UUID NOT NULL REFERENCES manufacturers(id),
  quality_rating INTEGER NOT NULL CHECK (quality_rating BETWEEN 0 AND 10000),
  production_batch TEXT NOT NULL,
  production_version INTEGER NOT NULL DEFAULT 1 CHECK (production_version > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_asset_provenance_manufacturer ON asset_provenance(manufacturer_id);

CREATE OR REPLACE FUNCTION validate_social_escrow_transition()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.state = 'RELEASED' AND OLD.state <> 'LOCKED' THEN
    RAISE EXCEPTION 'escrow can only be released from LOCKED';
  END IF;
  IF NEW.state = 'REFUNDED' AND OLD.state <> 'LOCKED' THEN
    RAISE EXCEPTION 'escrow can only be refunded from LOCKED';
  END IF;
  IF NEW.state = 'LOCKED' AND OLD.state <> 'LOCKED' THEN
    RAISE EXCEPTION 'escrow cannot return to LOCKED';
  END IF;
  RETURN NEW;
END;
$$;
DROP TRIGGER IF EXISTS trg_social_escrow_transition ON social_contract_escrow;
CREATE TRIGGER trg_social_escrow_transition
BEFORE UPDATE OF state ON social_contract_escrow
FOR EACH ROW EXECUTE FUNCTION validate_social_escrow_transition();

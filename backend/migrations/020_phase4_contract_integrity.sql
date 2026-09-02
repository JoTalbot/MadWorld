-- Phase 4: database-enforced consistency between escrow and social-contract lifecycle.
-- Escrow-backed contracts cannot bypass financial settlement through the legacy transition endpoint.
CREATE OR REPLACE FUNCTION validate_social_contract_escrow_state()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
  escrow_state TEXT;
BEGIN
  SELECT state INTO escrow_state
  FROM social_contract_escrow
  WHERE contract_id = NEW.id;

  IF escrow_state IS NOT NULL THEN
    IF NEW.state = 'ACCEPTED' AND escrow_state <> 'LOCKED' THEN
      RAISE EXCEPTION 'escrow-backed contract must remain LOCKED while ACCEPTED';
    END IF;
    IF NEW.state = 'COMPLETED' AND escrow_state <> 'RELEASED' THEN
      RAISE EXCEPTION 'escrow-backed contract cannot complete before escrow release';
    END IF;
    IF NEW.state IN ('CANCELLED','EXPIRED') AND escrow_state <> 'REFUNDED' THEN
      RAISE EXCEPTION 'escrow-backed contract cannot close before escrow refund';
    END IF;
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_social_contract_escrow_state ON social_contracts;
CREATE TRIGGER trg_social_contract_escrow_state
BEFORE UPDATE OF state ON social_contracts
FOR EACH ROW EXECUTE FUNCTION validate_social_contract_escrow_state();

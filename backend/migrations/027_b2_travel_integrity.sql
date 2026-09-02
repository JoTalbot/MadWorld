-- B2 travel integrity: terminal outcomes require an active trip; encounters only
-- belong to active trips. These invariants keep the command layer from creating
-- impossible gameplay states under retries or client reconnects.

CREATE OR REPLACE FUNCTION validate_travel_session_outcome()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.state IN ('LOST','INTERRUPTED','ARRIVED')
     AND OLD.state NOT IN ('TRAVELLING') THEN
    RAISE EXCEPTION 'travel session terminal outcome requires TRAVELLING state';
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_travel_session_outcome ON player_travel_sessions;
CREATE TRIGGER trg_validate_travel_session_outcome
BEFORE UPDATE OF state ON player_travel_sessions
FOR EACH ROW
WHEN (NEW.state IS DISTINCT FROM OLD.state)
EXECUTE FUNCTION validate_travel_session_outcome();

CREATE OR REPLACE FUNCTION validate_travel_encounter_session()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  session_state TEXT;
BEGIN
  SELECT state INTO session_state
  FROM player_travel_sessions
  WHERE id = NEW.travel_session_id;

  IF session_state IS DISTINCT FROM 'TRAVELLING' THEN
    RAISE EXCEPTION 'travel encounter requires TRAVELLING session';
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_travel_encounter_session ON travel_encounters;
CREATE TRIGGER trg_validate_travel_encounter_session
BEFORE INSERT ON travel_encounters
FOR EACH ROW
EXECUTE FUNCTION validate_travel_encounter_session();

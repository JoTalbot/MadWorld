-- B1 foundation: bridge every authoritative world event into the existing
-- transactional outbox without letting the simulator mutate player domains.
--
-- The trigger is intentionally database-local. World event creation and its
-- outbox delivery record therefore commit or roll back together with the
-- simulation tick transaction.

CREATE INDEX IF NOT EXISTS idx_world_events_tick_id
    ON world_events (tick, id);

CREATE INDEX IF NOT EXISTS idx_outbox_world_events
    ON outbox_events (aggregate_type, aggregate_id, created_at)
    WHERE aggregate_type = 'world_event';

CREATE OR REPLACE FUNCTION bridge_world_event_to_outbox()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO outbox_events (
        aggregate_type,
        aggregate_id,
        event_type,
        payload
    )
    VALUES (
        'world_event',
        NEW.id,
        'world.' || NEW.event_type,
        jsonb_build_object(
            'world_event_id', NEW.id,
            'tick', NEW.tick,
            'region_id', NEW.region_id,
            'faction_id', NEW.faction_id,
            'event_type', NEW.event_type,
            'severity', NEW.severity,
            'payload', NEW.payload
        )
    );

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_world_event_outbox ON world_events;

CREATE TRIGGER trg_world_event_outbox
AFTER INSERT ON world_events
FOR EACH ROW
EXECUTE FUNCTION bridge_world_event_to_outbox();

-- Consumers use this table as an idempotency fence. The unique key means a
-- redelivery can never apply the same world event twice for the same consumer.
CREATE TABLE IF NOT EXISTS world_event_consumptions (
    consumer_name TEXT NOT NULL,
    world_event_id UUID NOT NULL REFERENCES world_events(id) ON DELETE CASCADE,
    consumed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload_hash TEXT,
    PRIMARY KEY (consumer_name, world_event_id)
);

CREATE INDEX IF NOT EXISTS idx_world_event_consumptions_event
    ON world_event_consumptions (world_event_id, consumed_at);

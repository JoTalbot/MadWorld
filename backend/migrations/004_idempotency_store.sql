-- Shared durable idempotency foundation for authoritative API commands.
CREATE TABLE IF NOT EXISTS idempotency_records (
    actor_id UUID NULL,
    command_name TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    response_status INTEGER NOT NULL,
    response_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (command_name, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_idempotency_records_actor_created
    ON idempotency_records(actor_id, created_at);

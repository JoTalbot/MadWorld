CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    handle TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL UNIQUE REFERENCES players(id),
    currency TEXT NOT NULL DEFAULT 'SC',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ledger_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key TEXT NOT NULL UNIQUE,
    wallet_id UUID NOT NULL REFERENCES wallets(id),
    amount BIGINT NOT NULL,
    reason TEXT NOT NULL,
    actor_id UUID REFERENCES players(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (amount <> 0)
);

CREATE TABLE item_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    stack_limit INTEGER NOT NULL DEFAULT 1 CHECK (stack_limit > 0)
);

CREATE TABLE inventories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES players(id),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventory_id UUID NOT NULL REFERENCES inventories(id) ON DELETE CASCADE,
    item_definition_id UUID NOT NULL REFERENCES item_definitions(id),
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    condition INTEGER NOT NULL DEFAULT 100 CHECK (condition BETWEEN 0 AND 100),
    UNIQUE (inventory_id, item_definition_id)
);

CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES players(id),
    code TEXT NOT NULL UNIQUE,
    chassis_code TEXT NOT NULL,
    durability INTEGER NOT NULL DEFAULT 100 CHECK (durability BETWEEN 0 AND 100),
    fuel INTEGER NOT NULL DEFAULT 0 CHECK (fuel >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES players(id),
    job_type TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'queued',
    started_at TIMESTAMPTZ NOT NULL,
    completes_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    idempotency_key TEXT NOT NULL UNIQUE
);

CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    aggregate_type TEXT NOT NULL,
    aggregate_id UUID NOT NULL,
    actor_id UUID REFERENCES players(id),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ledger_wallet_time ON ledger_entries(wallet_id, created_at);
CREATE INDEX idx_inventory_owner ON inventories(owner_id);
CREATE INDEX idx_jobs_completion ON jobs(state, completes_at);
CREATE INDEX idx_audit_aggregate ON audit_events(aggregate_type, aggregate_id, created_at);

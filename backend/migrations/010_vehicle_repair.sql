ALTER TABLE jobs
    ADD COLUMN IF NOT EXISTS metadata JSONB NOT NULL DEFAULT '{}'::jsonb;

CREATE INDEX IF NOT EXISTS idx_jobs_type_state_completion
    ON jobs(job_type, state, completes_at);

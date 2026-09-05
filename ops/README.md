# MadWorld B9 Operations

## Production topology

- `api`: stateless FastAPI instance behind the deployment's reverse proxy. **Run exactly one API process** until the in-process rate limiter / replay guard / abuse scorer are moved to shared storage (see `backend/README.md`, "Scaling constraint"). Horizontal API scaling is a tracked capacity-gate dependency, not a supported configuration today.
- `world-tick-worker`: authoritative world clock worker. Multiple replicas are safe because PostgreSQL advisory locking permits one tick owner per transaction.
- `migrator`: one-shot schema migration job, run before API/worker rollout.
- PostgreSQL remains the authoritative persistent store.

## Deployment order

1. Provision PostgreSQL and credentials.
2. Run `migrator` successfully.
3. Start API instances and wait for `/health`.
4. Start one or more world-tick workers.
5. Verify tick progression and logs.

## Catch-up policy

The world tick worker is intentionally bounded and does not attempt unbounded catch-up in a single request. A delayed tick should be processed transactionally, and repeated worker execution remains serialized by the PostgreSQL advisory lock. Operators should investigate sustained lag rather than silently fast-forwarding economy/combat state.

## Backup / restore

- Take regular PostgreSQL logical or provider-native backups according to the production retention policy.
- Before restore, stop mutation traffic and world workers.
- Restore into an isolated database first and verify migration/schema history.
- Validate authoritative invariants and application health before reopening traffic.
- Preserve the incident timeline and backup identifier used for recovery.

## Disaster recovery

Recovery priority: PostgreSQL -> migrations/schema -> API -> world worker -> Android clients.

RPO/RTO values are deployment-specific and must be configured by the operator. This repository does not invent availability guarantees that infrastructure has not actually been tested to provide.

## Observability

Minimum operational signals:

- API request rate, 4xx/5xx rate and latency.
- Rate-limit/replay rejection counts.
- World tick duration, lag and skipped-lock attempts.
- Database connection saturation and migration failures.
- Backup success/failure and restore verification results.

## Rollback

Application rollback must not run an older binary against a schema that requires newer migrations. Prefer forward-compatible migrations and roll back application images only after schema compatibility is verified.

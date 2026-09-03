# B9 Load / Stress Test Plan

## Targets

- API sustained request rate.
- Mutation latency and error rate under concurrency.
- Database pool saturation.
- World tick duration and lag under concurrent API traffic.
- Rate-limit and replay containment behavior.

## Safety

Load tests must target an isolated environment with synthetic accounts and data. Never run stress traffic against production without an explicit maintenance window and tested rollback.

## Exit criteria

- No invariant, authorization or idempotency failure.
- No unbounded queue growth.
- Rate limiter contains configured abusive traffic.
- p95/p99 latency and error thresholds are recorded for the deployment environment.
- World tick remains serialized and authoritative.

Thresholds are environment-specific and must be measured, not invented in repository documentation.

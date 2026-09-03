# MadWorld — Release Owner Runbook

## Purpose

This runbook closes the environment-dependent portion of B10 without pretending that repository CI can verify external infrastructure.

## 1. Deploy a production-like candidate

- Use the exact candidate commit intended for release.
- Provision PostgreSQL with the documented connection settings.
- Apply migrations before starting API/world workers.
- Verify `/health` and worker health/lag.
- Record deployment commit, schema version and configuration revision.

## 2. Backup and restore

- Run `ops/backup_restore.sh` against the production-like database.
- Restore into an isolated database.
- Verify `schema_migrations` and representative authoritative tables.
- Record backup size, duration, restore duration and verification result.
- Do not overwrite the source database during the exercise.

## 3. Load and capacity

- Run `ops/LOAD_TEST_PLAN.md` only against an isolated environment.
- Measure API latency, error rate, database pool utilization, world-tick lag and rate-limit containment.
- Record tested request rate, concurrency, database size and observed bottleneck.
- Set an explicit approved capacity before launch.

## 4. Android release matrix

- Execute API 26 low-memory profile.
- Execute API 29–32 mid-range profile.
- Execute API 33–35 modern profile.
- Execute at least one physical device when available.
- Verify login, authoritative refresh, offline queue, reconnect, stale-state rejection, notifications and core gameplay navigation.
- Record OS/device/build identifiers and pass/fail evidence.

## 5. External providers

- Configure crash reporting.
- Configure analytics.
- Configure push notifications/device tokens.
- Verify production endpoints and credentials without committing secrets.
- Trigger controlled test events and confirm delivery/ingestion.

## 6. Rollback and disaster recovery

- Rehearse application rollback to the previous known-good candidate.
- Rehearse database restore into an isolated environment.
- Verify that failed migrations do not leave the deployment falsely marked healthy.
- Record recovery time and recovery point achieved.

## 7. Incident response

- Confirm operational owner and escalation path.
- Confirm API, worker and database alerts.
- Confirm logs and critical metrics are accessible.
- Exercise one simulated incident and record response timing.

## 8. Privacy/legal and release approval

- Complete privacy/legal review outside the repository.
- Confirm analytics/push/crash data handling is approved.
- Confirm store metadata and required disclosures.
- Approve final server capacity and rollback plan.

## 9. Release decision

B10 may move from `ACTIVE / Release Candidate` to `COMPLETE` only after all mandatory checks have explicit evidence. Unknown is not pass.

The repository-side release gate is necessary but insufficient for production approval.

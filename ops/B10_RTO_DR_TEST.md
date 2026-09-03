# B10 RTO / Disaster Recovery Test

Target: verify recovery from a fresh isolated environment without touching existing unrelated infrastructure.

## Procedure

1. Record current release commit/image and latest successful backup timestamp.
2. Provision an isolated PostgreSQL target and application namespace.
3. Restore the latest backup using `ops/backup_restore.sh`.
4. Apply/verify all migrations and row/table counts.
5. Start API and worker using the candidate image.
6. Measure time from recovery start to `/health/ready`, then to the first successful world tick.
7. Execute representative read/write contracts and verify idempotency.
8. Tear down only the isolated recovery resources.

## Evidence

Record `T_restore`, `T_ready`, `T_first_tick`, migration count, table count, test result and cleanup result. The current repository evidence demonstrates isolated restore and worker recovery, but not a full fresh-host cutover. Therefore the final gate remains PARTIALLY VERIFIED until this exercise is executed by the release owner.

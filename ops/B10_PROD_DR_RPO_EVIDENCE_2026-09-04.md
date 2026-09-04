# B10 Production Backup / DR Evidence

Date: 2026-09-04

This record captures target-environment evidence supplied from the MadWorld production server during the B10 release gate. It is intentionally conservative: an isolated Docker recovery on the same host is not represented as a fresh-host disaster-recovery proof.

## Backup / RPO evidence

- Daily `madworld-backup.timer` is installed and enabled for MadWorld.
- The timer is configured for `03:15 UTC` with `Persistent=true` and a small randomized delay.
- A successful scheduled backup was observed at `2026-09-04T03:16:00Z`.
- The observed backup completed successfully and was subsequently checksum-verified.
- Backup retention is configured for 14 days.
- Backup script validates the custom-format dump with `pg_restore --list` and writes SHA-256 metadata.
- Target-server free disk was approximately 103 GB of 145 GB total, so the 1 GiB fail-closed threshold was not approached.
- The daily schedule supports an RPO target of <=24 hours. A measured data-loss RPO is not claimed because no production incident/data-change timestamp was used to measure actual loss.

## Isolated recovery rehearsal

- Latest verified backup used: `madworld-20260904T103808Z.dump`.
- SHA-256 verification returned `OK`.
- The dump was restored into a newly created, isolated PostgreSQL 16 container/database named `madworld_restore`.
- Isolated restore used dedicated MadWorld-only Docker resources: `madworld-dr-postgres`, `madworld_dr_pgdata`, and `madworld_dr_net`.
- `pg_restore` completed without error.
- `restore_verified = 1`.
- Restored `schema_migrations` count: `41`.
- Restored database size: `24 MB`.
- Observed restore duration from the supplied timestamps: approximately 2 seconds (`10:50:23Z` to `10:50:25Z`).
- After the rehearsal, the temporary DR container, volume and network were removed.
- Production MadWorld API and PostgreSQL remained healthy after cleanup; public `/health/ready` returned status `ok`, database `ok`, and `migrations_applied: 41`.

## Gate interpretation

- Scheduled backup installation/execution: VERIFIED.
- Backup checksum/integrity/disk guard: VERIFIED.
- RPO target: <=24h from daily schedule, VERIFIED as a target; measured production data-loss RPO remains UNVERIFIED.
- Isolated recovery procedure: VERIFIED.
- Measured same-host isolated restore time: approximately 2 seconds.
- Fresh-host DR: UNVERIFIED.
- Target recovery-environment DR rehearsal: UNVERIFIED.
- Fresh-host production RTO: UNVERIFIED.

No final production release/tag is authorized by this evidence alone.

# B10 Fresh-Host Disaster Recovery + Measured RTO — Evidence Record

Date: 2026-09-04
Scope: MadWorld-only isolated recovery rehearsal. Production resources untouched.
Repo HEAD during this batch: `ec213ceaff60a4c5ee7f7afe992c303c22374049`

## Result

**FAIL — NOT EXECUTED (environment blocked).** No fresh-host DR rehearsal was
performed and **no RTO is claimed**. The Fresh-host DR/RTO gate remains **OPEN**.

Blocking prerequisites that were absent in the executing environment:

- No production backup source. A DR restore must use the freshly verified
  production dump as its source; no dump exists in this environment and the
  production host is unreachable (see `ops/B10_BACKUP_RPO_EVIDENCE_2026-09-04.md`
  for the connectivity trace: SSH reset at kex, TLS reset before handshake,
  egress filter signature on all probed ports).
- No PostgreSQL tooling (`psql`, `pg_dump`, `pg_restore`) and no Docker in the
  sandbox to host an isolated recovery environment.
- No SSH key material or other access path to the production host.

Per the repository rule, a synthetic/local restore that does not use the real
production backup would not be a disaster-recovery rehearsal and would not
close this gate. No such rehearsal was run, so nothing here can be misread as
RTO evidence.

## Attempted actions (UTC)

Attempt window `2026-09-04T10:07Z`–`2026-09-04T10:09:46Z`:

- SSH (publickey, BatchMode) as `root`, `ubuntu`, `madworld`, `admin`, `deploy`
  to `129.213.177.56` — all reset at `kex_exchange_identification`
  (`Connection closed/reset by ... port 22`).
- TCP connect probe of ports 22/80/443/5433/8000/8090 — all "handshake OK"
  instantly, i.e. egress interception; no application protocol completes.
- `https://api.autosklo.org.ua/health/ready` — HTTP 000, `SSL_ERROR_SYSCALL`
  (unreachable from this sandbox; unrelated Cloudflare IPs also unreachable, so
  no conclusion about production API health is drawn).
- Confirmed the sandbox has no `psql`/`pg_dump`/`pg_restore`/`docker` and no
  copy of any MadWorld production dump.
- Repository-side static validation that PASSED (this environment only):
  `bash -n ops/backup_restore.sh` -> OK; unit/script presence on HEAD confirmed.

## Required Part-B record fields

| Item | Value recorded |
|---|---|
| Recovery start UTC | NONE — rehearsal not started |
| Restore completion UTC | NONE |
| Total restore duration | NONE |
| Backup identifier/file | NONE (no production backup available to this environment) |
| Restored DB identity/environment | NONE |
| Migration/schema verification | NONE (target schema: 41 migrations per last recorded production `/health/ready` — NOT re-observed this batch) |
| Row/invariant verification | NONE |
| Application startup result | NONE |
| `/health/ready` result | NOT OBSERVED this batch (see trace) |
| Database connectivity | NOT TESTED |
| No-connection-to-production-DB check | NOT TESTED — trivially satisfied only in the sense that this environment cannot reach production at all; this is NOT evidence of recovery isolation |
| Measured RTO | **NOT MEASURED** — no rehearsal executed |

## Rehearsal procedure available (repository side, NOT executed)

`ops/backup_restore.sh` on HEAD implements: `pg_dump` of source URL ->
`pg_restore --clean --if-exists --no-owner` to an isolated target URL ->
`SELECT 1` connectivity probe -> `schema_migrations` count ->
`backup_restore_verified=true`. Static review only; it was NOT run because no
production backup and no PostgreSQL tooling are available here.

## PASS/FAIL summary

| Check | Result |
|---|---|
| Isolated MadWorld-only recovery environment created | FAIL — NOT EXECUTED |
| Freshly verified production backup used as source | FAIL — no backup available |
| Restore via `ops/backup_restore.sh` | FAIL — NOT EXECUTED |
| Recovery/restore timestamps and duration | FAIL — no data |
| Migration/schema + row/invariant verification | FAIL — no data |
| Application startup + `/health/ready` | FAIL — not observed this batch |
| No-connection-to-production verification | FAIL — NOT TESTED (unreachability of production from the sandbox is not a recovery-isolation check) |
| Measured RTO | FAIL — NOT MEASURED |

## What was NOT tested

- Nothing was restored anywhere; no isolated database was created.
- No migrations were applied, no schema/row invariants verified.
- No API container was started against a restored database; `/health/ready`
  was not exercised against a recovery environment.
- Cleanup of temporary recovery resources: N/A (none were created).
- Production volumes/databases were never touched, per the safety boundary.

## Safety statement

- Zero MadWorld production resources were created, modified or deleted.
- Production DB remained online and untouched.
- Octopus/liza services, unrelated networks/volumes/PostgreSQL, public ports
  8000/8090 and the host were not touched.
- No Docker resources were created or removed.

## What is required to close this gate

1. Access to a verified production dump (produced by the Part-A backup) and
   PostgreSQL tooling, OR SSH access to `129.213.177.56` to run the rehearsal
   in an isolated environment there.
2. Execute the full Part-B procedure and attach outputs (timestamps, restore
   duration, migration count, invariants, application startup, `/health/ready`,
   isolation check) to this record.

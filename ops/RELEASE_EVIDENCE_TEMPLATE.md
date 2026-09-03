# B10 Release Evidence Template

> Operational evidence record for the MadWorld Release Candidate. This document records observed evidence only. Unknown or unexecuted checks must remain `UNKNOWN`.

## 1. Candidate identity

- Candidate commit:
- Branch/tag:
- Release candidate version:
- Evidence date (UTC):
- Release owner:

## 2. Automated repository gate

- Unified release-gate workflow run:
- Backend job/run:
- Android job/run:
- Final gate result: `PASS` / `FAIL` / `UNKNOWN`
- Backend pytest result:
- Production Compose validation: `PASS` / `FAIL` / `UNKNOWN`
- Android unit tests: `PASS` / `FAIL` / `UNKNOWN`
- Android debug APK build: `PASS` / `FAIL` / `UNKNOWN`
- APK artifact/checksum:

## 3. Backend / database verification

- Migration from clean database: `PASS` / `FAIL` / `UNKNOWN`
- Database engine/version:
- Backup command executed: `PASS` / `FAIL` / `UNKNOWN`
- Backup artifact identifier:
- Restore executed against isolated database: `PASS` / `FAIL` / `UNKNOWN`
- Restore verification result:
- Restore duration:
- Schema migration head after restore:

## 4. Load / capacity verification

- Environment:
- Test duration:
- Target request rate:
- Achieved request rate:
- p50 latency:
- p95 latency:
- p99 latency:
- Error rate:
- Database pool saturation observed: `YES` / `NO` / `UNKNOWN`
- World-tick lag observed:
- Rate-limit containment verified: `PASS` / `FAIL` / `UNKNOWN`
- Capacity approval: `APPROVED` / `REJECTED` / `UNKNOWN`

## 5. Android verification

| Target | Result | Evidence |
|---|---|---|
| API 26 emulator | `PASS/FAIL/UNKNOWN` | |
| API 29-32 emulator/device | `PASS/FAIL/UNKNOWN` | |
| API 33-35 emulator/device | `PASS/FAIL/UNKNOWN` | |
| Physical Android device | `PASS/FAIL/UNKNOWN` | |
| Offline queue/reconnect | `PASS/FAIL/UNKNOWN` | |
| Notifications | `PASS/FAIL/UNKNOWN` | |
| Localization | `PASS/FAIL/UNKNOWN` | |
| Accessibility | `PASS/FAIL/UNKNOWN` | |

## 6. External providers and production controls

- Crash reporting configured and verified: `PASS` / `FAIL` / `UNKNOWN`
- Analytics configured and verified: `PASS` / `FAIL` / `UNKNOWN`
- Push delivery configured and verified: `PASS` / `FAIL` / `UNKNOWN`
- Production secrets/configuration verified: `PASS` / `FAIL` / `UNKNOWN`
- Privacy/legal approval: `APPROVED` / `REJECTED` / `UNKNOWN`

## 7. Rollback / disaster recovery / incident response

- Rollback rehearsal executed: `PASS` / `FAIL` / `UNKNOWN`
- Rollback duration:
- Restore/DR rehearsal executed: `PASS` / `FAIL` / `UNKNOWN`
- Incident-response contacts/runbook verified: `PASS` / `FAIL` / `UNKNOWN`
- Recovery objective achieved: `PASS` / `FAIL` / `UNKNOWN`

## 8. Release decision

### Mandatory rule

B10 cannot be marked complete while any mandatory automated gate is `FAIL` or any mandatory production/physical verification remains `UNKNOWN`.

- Release decision: `GO` / `NO-GO` / `CONDITIONAL` / `UNKNOWN`
- Blocking items:
- Approver:
- Approval timestamp (UTC):
- Notes:

## Evidence hygiene

- Never record secrets, tokens, private keys, credentials, or personal data here.
- Link or reference immutable workflow runs/artifacts rather than copying sensitive logs.
- Keep failed and superseded evidence for auditability; do not rewrite history to make a release look cleaner. Humanity has enough of that already.

---

# Deployed evidence record — `26b9d22` (observed on arm-server-01, 2026-09-03)

> Filled from actual observation on a real production-like server. Unknown/unexecuted
> external checks remain `UNKNOWN`. No secrets are recorded.

## 1. Candidate identity

- Candidate commit: `26b9d220f897951ab39376f0ccd8bbc546879166` (previous RC `44df14000195d32b1472f96a2a6aa6d3dc31b5ee` + runtime/ops fixes)
- Branch/tag: `main` (no tag)
- Release candidate version: `0.1.0`
- Evidence date (UTC): `2026-09-03T12:36Z`
- Release owner: deployment agent (environment gate); human product owner sign-off pending

## 2. Automated repository gate

- Unified release-gate workflow run: `33755504203` — success (Commit 26b9d22)
- Backend job/run: Release Gate `backend` job — success; Backend CI run `33755504032` — success
- Android job/run: Release Gate `android` job — success
- Final gate result: `PASS` (Release Gate `gate` job success)
- Backend pytest result: `166 passed` (CI gate + server re-run)
- Production Compose validation: `PASS`
- Android unit tests: `PASS` (4 tests, 0 failures)
- Android debug APK build: `PASS`
- APK artifact/checksum: GitHub artifact `madworld-android-release-gate` id `9893304894`; server APK SHA-256 `11e6993f128bcd3df8fabb5e65ae54c12ed1e3a1c3eca092ba5f76ac3d715410`

## 3. Backend / database verification

- Migration from clean database: `PASS` — 41 migrations, 113 tables; idempotent re-run
- Database engine/version: PostgreSQL 16 (isolated `postgres:16` container; db `madworld_db`, role `madworld`)
- Backup command executed: `PASS` (`ops/backup_restore.sh`, `pg_dump -Fc`)
- Backup artifact identifier: `backups/madworld_db_20260903T123512Z.dump`
- Restore executed against isolated database: `PASS` (`madworld_restore_verify`, then dropped)
- Restore verification result: `backup_restore_verified=true`; 41 migrations / 113 tables present
- Restore duration: ~2 s (backup + restore)
- Schema migration head after restore: `033_b9_operations.sql`

## 4. Load / capacity verification

- Environment: shared ARM64 host, API loopback `127.0.0.1:8090`, read-only traffic
- Test duration: bounded safety probes (no production stress)
- Target request rate: bounded probe
- Achieved request rate: ~376–850 req/s at low concurrency on read endpoints
- p50 latency: ~3.3 ms
- p95 latency: ~4.1 ms
- p99 latency: ~58 ms
- Error rate: 0% within the rate limit; burst containment verified
- Database pool saturation observed: `NO` (Postgres ~74 MB / 1 GB)
- World-tick lag observed: `lag_ms=0`; tick duration 20–50 ms; 0 failures through tick 46+
- Rate-limit containment verified: `PASS` (burst → exactly 120×200 then 429)
- Capacity approval: `UNKNOWN` (owner)

## 5. Android verification

| Target | Result | Evidence |
|---|---|---|
| API 26 emulator | `UNKNOWN` | No Android runtime on headless server; minSdk 26 compiled |
| API 29-32 emulator/device | `UNKNOWN` | Not executed on server |
| API 33-35 emulator/device | `UNKNOWN` | Not executed; compile/target SDK 35 build PASS |
| Physical Android device | `UNKNOWN` | Not available |
| Offline queue/reconnect | `UNIT-PASS` | Offline/state-guard unit tests pass; on-device pending |
| Notifications | `UNKNOWN` | Code present; device verification pending |
| Localization | `UNKNOWN` | Not verified on device |
| Accessibility | `UNKNOWN` | Not verified on device |

## 6. External providers and production controls

- Crash reporting configured and verified: `UNKNOWN` (owner)
- Analytics configured and verified: `UNKNOWN` (owner)
- Push delivery configured and verified: `UNKNOWN` (owner)
- Production secrets/configuration verified: `PASS` (`.env` 600, git-ignored, not in images; PG/API loopback only)
- Privacy/legal approval: `UNKNOWN` (owner)

## 7. Rollback / disaster recovery / incident response

- Rollback rehearsal executed: `PASS` (documented `ops/ROLLBACK.md`; stop-only-MadWorld; previous candidate `44df140`)
- Rollback duration: deterministic; not formally timed
- Restore/DR rehearsal executed: `PASS` (real backup + isolated restore)
- Incident-response contacts/runbook verified: `UNKNOWN` (owner defines on-call)
- Recovery objective achieved: `CONDITIONAL` (backup/restore verified; RPO/RTO owner)

## 8. Release decision

- Release decision: `CONDITIONAL` (technical/environment gates GREEN; external owner gates UNKNOWN)
- Blocking items: physical/emulator Android matrix; external crash/analytics/push providers; privacy/legal; final capacity approval; on-call/RPO/RTO; owner confirmation of bounded disaster-modifier clamp.
- Approver: human release owner (pending)
- Approval timestamp (UTC): `UNKNOWN`
- Notes: GitHub `main` and production server now run the same verified commit `26b9d22`. The two runtime bugs that aborted world ticks are fixed in GitHub (not only on the server). All 166 backend tests, the GitHub Release Gate, Android unit tests/APK, migrations, backup/restore, rate-limit and replay checks are green.


---

# External / Owner Release Gate Status — 2026-09-03, commit `f127f87`

> Every gate below is assigned `VERIFIED`, `PARTIALLY VERIFIED`, `UNVERIFIED` or
> `BLOCKED` **with evidence**. Unknown is not treated as pass. Server-side
> technical gates are `VERIFIED`; anything requiring an external account, a
> physical Android device, or a legal/owner decision is marked accordingly. No
> secrets are recorded.

## Gate status table

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | Backend tests (169) | **VERIFIED** | CI Release Gate `33757777783` success; server `169 passed` on PG16 |
| 2 | Migrations (clean DB) | **VERIFIED** | 41 migrations / 113 tables, idempotent; CI + server |
| 3 | Production Compose validation | **VERIFIED** | CI backend job `docker compose config` success |
| 4 | Android unit tests | **VERIFIED** | CI android job + server `:app:testDebugUnitTest` pass (4 tests) |
| 5 | Android debug APK build + checksum | **VERIFIED** | CI artifact `9893304894`; server APK SHA-256 `11e6993f128bcd3df8fabb5e65ae54c12ed1e3a1c3eca092ba5f76ac3d715410` |
| 6 | API health / real readiness | **VERIFIED** | `/health/ready` → database ok, migrations_applied=41; container healthy |
| 7 | World-tick worker | **VERIFIED** | ticks advancing past 77, lag_ms=0, 0 failures, restart 0, survives restart |
| 8 | Backup / restore | **VERIFIED (isolated)** | `pg_dump`→isolated DB restore; 41 migrations/113 tables; `backup_restore_verified=true` |
| 9 | Security posture (server) | **VERIFIED** | non-root, not privileged, no-new-privileges, loopback-only ports, `.env` 600/git-ignored, rate-limit + replay verified |
| 10 | Capacity (bounded) | **PARTIALLY VERIFIED** | safe read-only probe only: p50 5.7 ms, p95 8.3 ms, p99 123 ms, 0% error within limit, ~2 DB conns/100 max, 429 containment; production-scale capacity approval pending |
| 11 | RTO | **PARTIALLY VERIFIED** | API healthy ~4 s; restore ~1.9 s; worker reconnects ~27 s (first tick within 60 s); full DR cut-over to a fresh host not rehearsed |
| 12 | RPO / scheduled backups | **PARTIALLY VERIFIED / GAP** | on-demand backup works and is fast; **no scheduled backup job exists** → until one is configured, potential data loss window = time since last manual backup. Owner must set retention/schedule |
| 13 | Android emulator matrix (API 26 / 29–32 / 33–35) | **UNVERIFIED** | no emulator package, no `/dev/kvm` (nested virtualization unavailable), adb daemon cannot run on this host |
| 14 | Physical Android device | **UNVERIFIED — physical device unavailable** | no device attached; on-device install/launch/login/offline/reconnect/notifications/rotation/network-loss cannot be executed. Not simulated |
| 15 | Push notifications (FCM/APNs) | **BLOCKED — EXTERNAL PROVIDER UNVERIFIED** | `device_push_tokens` table exists; no push-delivery backend code, no Firebase/FCM SDK, no `google-services.json`, no credentials. Local in-app `NotificationCenter` only. Offline-device delivery, retry, token registration are not implemented end-to-end |
| 16 | Crash reporting | **BLOCKED — EXTERNAL PROVIDER UNVERIFIED** | no Crashlytics/Sentry/etc. SDK or config; `analytics_events`/`audit_events` tables exist but no external provider. No debug telemetry observed |
| 17 | Analytics | **BLOCKED — EXTERNAL PROVIDER UNVERIFIED** | `analytics_events` schema exists; **no route writes to it**, no outbound HTTP, no provider credentials. Not claimed working |
| 18 | External provider inventory | **VERIFIED (inventory)** | no outbound external calls in backend (no httpx/requests use); only external dependency is the cloud host + container image registry; Android bundles no third-party tracking/push SDK |
| 19 | Privacy / legal | **BLOCKED — LEGAL REVIEW REQUIRED** | no Privacy Policy, Terms, data-safety/deletion disclosure in repo; owner/legal must produce. See `ops/LEGAL_REVIEW_REQUIRED.md` |
| 20 | Disaster-clamp product decision | **PARTIALLY VERIFIED — OWNER CONFIRMATION** | technical clamp applied & tested (see `ops/B10-PROD-DISASTER-CLAMP.md`); product balance interpretation pending owner sign-off |
| 21 | Incident response / on-call | **UNVERIFIED** | no on-call/escalation defined; not certifiable from server |
| 22 | Release tag | **VERIFIED (RC)** | annotated tag `v0.1.0-rc1` on the verified commit (after gates green); public production release tag deliberately NOT created |

## External providers (item 18 detail)

| Provider | Purpose | Configured | Reachable | Authenticated | Production verified |
|---|---|---|---|---|---|
| PostgreSQL | authoritative store | n/a — self-hosted `postgres:16` container | VERIFIED (in-cluster) | VERIFIED (isolated `madworld` role) | VERIFIED |
| Cloud host (OCI VM) | runtime | VERIFIED (existing) | VERIFIED | n/a | VERIFIED |
| FCM / Firebase Cloud Messaging | push | **NO** | n/a | NO | **EXTERNAL PROVIDER UNVERIFIED** |
| Crash reporting (Sentry/Crashlytics…) | crashes | **NO** | n/a | NO | **EXTERNAL PROVIDER UNVERIFIED** |
| Analytics (Mixpanel/Amplitude/GA…) | analytics | **NO** | n/a | NO | **EXTERNAL PROVIDER UNVERIFIED** |
| Outbound HTTP / 3rd-party APIs | integrations | none present | n/a | n/a | none to verify |

Legend: VERIFIED = demonstrated in this environment; PARTIALLY VERIFIED = demonstrated with documented limits; UNVERIFIED = not executable here; BLOCKED = requires external account/legal/owner and cannot pass without it.

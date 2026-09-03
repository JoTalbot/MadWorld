# MadWorld — B10 Release Candidate Audit

Date: 2026-09-03

## Purpose

Record the final repository-side B10 audit without treating environment-dependent checks as passed merely because code exists.

## Verified in repository / CI

- B1–B6 are recorded COMPLETE in the production backlog.
- B7 is recorded COMPLETE with explicit deferred external/extended work.
- B8 is recorded COMPLETE with production-infrastructure controls explicitly separated from repository code.
- B9 is recorded COMPLETE with its automated exit gate passed.
- B10 release-gate artifacts exist:
  - `ops/RELEASE_CHECKLIST.md`
  - `ops/RELEASE_NOTES_B10.md`
  - `backend/tests/test_b10_release_gate.py`
- Release Gate run `33748075997` completed successfully on candidate commit `83e639af9317a4f17f8d4eb3e59ea6c8727c6c4b`.
- Release Gate backend job `100625077855` passed migrations, production Compose validation and the complete backend release-gate test suite.
- Release Gate Android job `100625077651` passed unit tests, debug APK assembly, checksum generation and artifact upload.
- Release Gate final job `100625565742` passed.
- Android release-gate artifact `madworld-android-release-gate` was produced successfully; SHA-256 digest: `99676b9b274a45104954919815abf2f9b7a7fb9f9ff023d03ec6f4c84f8950f3`.
- Production Compose validation is part of the automated gate.
- B10 release-gate contract tests are part of the backend test suite.
- PostgreSQL URL normalization to the installed psycopg 3 driver is now protected by `backend/tests/test_database_url_contract.py`.

## Not honestly verifiable from repository-only access

These checks remain RELEASE-OWNER / ENVIRONMENT gates:

- Full end-to-end gameplay regression on a deployed environment.
- Real PostgreSQL backup and restore exercise against the intended production-like environment.
- Sustained load/stress execution against an isolated production-like environment with capacity measurements.
- Android API 26 / 29–32 / 33–35 execution on the actual release matrix.
- Physical Android device verification.
- External crash-reporting provider configuration and validation.
- External analytics/push provider configuration and validation.
- Production secrets/configuration verification.
- Privacy/legal approval.
- Final capacity approval.
- Rollback and disaster-recovery rehearsal.
- Incident-response rehearsal and operational ownership sign-off.
- Final release version/tag selection.

## Release decision

**B10 remains ACTIVE / Release Candidate.**

The repository-side implementation and automated Release Gate are green, but the project must not be labeled production-ready until the mandatory environment and owner checks above are explicitly verified.

This distinction is intentional: a green CI run is evidence that the code passed its automated contract, not evidence that a real production environment, device fleet, external providers or legal approvals exist. Humanity has suffered enough from checkboxes pretending to be reality.

## Next release-owner actions

1. Execute the production-like migration and backup/restore exercise.
2. Execute isolated load/stress verification and record capacity numbers.
3. Run the Android release matrix, including a physical device where available.
4. Configure and validate crash, analytics and push providers.
5. Verify production secrets/configuration and deployment health.
6. Rehearse rollback, disaster recovery and incident response.
7. Complete privacy/legal review.
8. Select release version/tag and complete the release checklist.
9. Only then change B10 from ACTIVE to COMPLETE.

---

## Deployment gate update — commit `26b9d22` (2026-09-03)

The environment-dependent portion of B10 was executed on a real production-like
server (Ubuntu 24.04 LTS, aarch64). Two runtime defects in the release candidate
were found during real deployment, fixed and committed as `26b9d22`:

1. `apply_territory_signal` keyed `territory_modifiers` off
   `world_region_bindings.gameplay_region_id` (a gameplay UUID), but
   `territory_modifiers.region_id` references `world_regions(id)`. This raised a
   foreign-key violation and rolled the entire world tick back. Fixed to key/join
   through the authoritative world-region side (`b.world_region_id`).
2. Disaster territory modifiers (raw `severity*1200` up to 6000 bps) exceeded the
   schema CHECK bounds of `[-5000,5000]`, raising a check violation and aborting
   the tick. The modifiers are now clamped to the schema-authoritative bounds
   (the docstring already promised a "bounded" modifier). No gameplay/economy
   coefficient was changed.

Supporting ops changes in the same commit:

- Real readiness probe `GET /health/ready` (verifies PostgreSQL connectivity and
  counts applied migrations); Docker healthcheck wired to it via the deployment
  overlay.
- `ops/docker-compose.deploy.yml` deployment overlay (isolated PostgreSQL
  container, loopback-only port mapping, non-root/resource limits/no-new-privileges).
- `.gitignore` added to keep `.env`, backups and build artifacts out of Git.
- `test_b2_region_bridge_is_used_for_territory_risk` updated to lock the correct
  world-region keying and guard against the gameplay-UUID regression.

### Automated Release Gate on `26b9d22`

- Release Gate run **`33755504203`** — `success`
  - `backend` job: migrations, production Compose validation, full backend
    release-gate test suite — `success`.
  - `android` job: Android unit tests, `assembleDebug`, artifact checksum,
    artifact upload (`madworld-android-release-gate`, artifact id `9893304894`) — `success`.
  - `gate` job: `success`.
- Backend CI run **`33755504032`** — `success` (migrations, module resolution,
  production Compose validation, full pytest).

### Server-side verification on `26b9d22`

- Backend: `166 passed` on PostgreSQL 16 (integration tests included); migrations
  41 / 113 tables, idempotent.
- Production Docker: API healthy (`/health/ready` → database ok, migrations_applied=41),
  world-tick worker ticking with 0 failures (observed past tick 44, lag_ms=0,
  restart count 0), migrator one-shot `Exited (0)`.
- Backup/restore: real `pg_dump` + isolated restore verified (41 migrations,
  113 tables), temporary restore DB dropped.
- Security: `.env` chmod 600 and git-ignored; containers non-root and not
  privileged; PostgreSQL/API loopback-only; rate-limit (120/min → 429) and
  replay guard (duplicate mutation → 409 `REPLAY_DETECTED`) verified.
- Android unit tests and debug APK built and checksummed (see artifact manifest).

### Remaining owner/external gates (unchanged)

Physical Android device / emulator matrix, external crash/analytics/push
providers, privacy/legal review, final capacity approval, incident-ownership,
and RPO/RTO sign-off remain release-owner gates that cannot be certified from
this server. Product owner should also confirm the bounded disaster-modifier
clamp matches intended balance (no coefficient changed).


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

---

# Final repository production batch — commit `bdf6657` (2026-09-03)

The repository-side portion of the requested B10 production batch is now committed to `main`.

### Implemented

- `android/app/build.gradle.kts`: production API URL is injected through Gradle property/environment `MADWORLD_API_URL`; `10.0.2.2:8000` remains only as a development fallback.
- `docs/ANDROID_API_CONFIGURATION.md`: build/release configuration rules.
- `ops/backup_daily.sh`: daily custom-format PostgreSQL backup, integrity validation, SHA-256 metadata, retention and low-disk guard.
- `ops/madworld-backup.service` and `ops/madworld-backup.timer`: intended systemd schedule, daily at 03:15 UTC with persistence/randomized delay.
- `ops/B10_BACKUP_RPO.md`: installation, verification and RPO policy.
- `ops/B10_RTO_DR_TEST.md`: fresh-environment recovery procedure and evidence requirements.
- `ops/B10_INCIDENT_RESPONSE.md`: incident severity, first-response, recovery and closure runbook.
- `ops/B10_HTTPS_GATE.md`: production TLS/reverse-proxy owner gate without inventing a domain.
- `ops/ANDROID_DEVICE_MATRIX_B10.md`: API 26 / 29–32 / 33–35 evidence matrix.
- `ops/B10_EXTERNAL_PROVIDERS.md`: push/crash/analytics provider gates.
- `ops/B10_CAPACITY_VERIFICATION.md`: isolated capacity test procedure.
- `ops/B10_OBSERVABILITY_BASELINE.md`: MadWorld-only operational signals, explicitly isolated from Octopus.
- `ops/B10_GOOGLE_PLAY_READINESS.md`: store readiness checklist.
- `ops/FINAL_RELEASE_DECISION.md`: current decision **GO AFTER OWNER ACTIONS**.
- `ops/B10_FINAL_BATCH_STATUS.md`: batch scope and non-certified external gates.

### Remaining gates

The batch deliberately does not fabricate evidence for real production HTTPS, scheduled backup execution, fresh-host DR, production-scale capacity, Android device/emulator execution, external providers, legal approval, incident ownership, or product-owner confirmation. These remain explicit release-owner actions.

### Safety boundary

No Octopus infrastructure, secrets, host-wide cleanup, gameplay/economy coefficient or RC tag was changed by this repository batch.

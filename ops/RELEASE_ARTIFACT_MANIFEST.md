# B10 Release Artifact Manifest

This manifest defines the immutable evidence expected for a MadWorld Release Candidate. It does not claim that an artifact exists until a workflow or release owner records concrete evidence.

## Candidate

- Commit SHA:
- Release candidate tag:
- Version:
- Build timestamp (UTC):

## Backend

- Migration head:
- Backend CI run:
- Unified release-gate run:
- Production Compose validation: `PASS` / `FAIL` / `UNKNOWN`
- Test result:

## Android

- APK artifact name:
- APK path within artifact:
- SHA-256:
- Build job/run:
- Minimum SDK:
- Target SDK:
- Release artifact verification: `PASS` / `FAIL` / `UNKNOWN`

## Configuration

- Required production environment variables verified without exposing values: `PASS` / `FAIL` / `UNKNOWN`
- Database connectivity verified: `PASS` / `FAIL` / `UNKNOWN`
- Worker health verified: `PASS` / `FAIL` / `UNKNOWN`
- Rollback target identified: `PASS` / `FAIL` / `UNKNOWN`

## Release provenance

- Source repository: `JoTalbot/MadWorld`
- Candidate commit must match the source used to produce every release artifact.
- Artifact checksums must be recorded from the actual generated artifact.
- No credentials, tokens, private keys, or secret configuration values belong in this file.

## Status

`UNVERIFIED` until the release owner populates the fields from immutable CI/artifact evidence.

---

# Deployed build record — `26b9d22` (filled from immutable CI/artifact evidence, 2026-09-03)

> Environment: production-like server `arm-server-01`, Ubuntu 24.04.4 LTS, aarch64.
> No credentials or secret values are recorded here.

## Candidate

- Repository: `JoTalbot/MadWorld`
- Previous RC commit: `44df14000195d32b1472f96a2a6aa6d3dc31b5ee`
- Deployed / GitHub `main` commit: `26b9d220f897951ab39376f0ccd8bbc546879166`
- Release candidate tag: none (branch `main`)
- Version: `0.1.0`
- Build timestamp (UTC): `2026-09-03T12:33Z`

## Backend

- Migration head: `033_b9_operations.sql` (41 migrations, 113 tables; idempotent)
- Backend CI run: `33755504032` — `success`
- Unified release-gate run: `33755504203` — `success`
- Production Compose validation: `PASS` (`ops/docker-compose.production.yml` validated in CI; deployment overlay `ops/docker-compose.deploy.yml` used on server)
- Test result: `166 passed` (both CI gate and server, PostgreSQL 16 integration included)
- Docker images built on the server from commit `26b9d22` (tagged `latest` and `26b9d22`):
  - `madworld-api:26b9d22` — image id `a0c602e5999c`
  - `madworld-world-tick-worker:26b9d22` — image id `94e1179ff3f1`
  - `madworld-migrator:26b9d22` — image id `3da4a8352eec`
  - Base `python:3.12-slim` (linux/arm64); runs as non-root uid 10001
- Database: `postgres:16` image id `f1c3376c26f2`, isolated container, volume `madworld_pgdata`, network `madworld_net`

## Android

- APK artifact name (CI): `madworld-android-release-gate` (GitHub Actions artifact id `9893304894`, run `33755504203`, `android` job — success)
- APK path within artifact: `android/app/build/outputs/apk/debug/app-debug.apk`
- APK artifact name (server build): `artifacts/android/madworld-app-debug.apk`
- SHA-256 (server-built debug APK): `11e6993f128bcd3df8fabb5e65ae54c12ed1e3a1c3eca092ba5f76ac3d715410`
  (Note: CI- and server-built APK digests differ because they are produced on different runners/build hosts; both are verified against their own generated artifact.)
- Build job/run: Release Gate `android` job, run `33755504203` — success; server build via Gradle 8.10.2 / JDK 17 / AGP 8.7.3
- Minimum SDK: 26
- Target SDK: 35 (compileSdk 35)
- Unit tests: `:app:testDebugUnitTest` PASS (4 tests, 0 failures); `:app:assembleDebug` PASS
- Release artifact verification: `PASS` (aapt badging confirms package `com.jotalbot.madworld`, versionName 0.1.0)

## Database backup artifact

- Backup file: `backups/madworld_db_20260903T123512Z.dump` (custom format)
- Restore verification: `PASS` (isolated DB; 41 migrations / 113 tables; temp restore DB dropped)

## Configuration

- Required production environment variables verified without exposing values: `PASS` (`.env` chmod 600, git-ignored, not present in images; values never logged)
- Database connectivity verified: `PASS` (`/health/ready` → database ok, migrations_applied=41)
- Worker health verified: `PASS` (ticks advancing past 44, lag_ms=0, 0 failures, restart count 0)
- Rollback target identified: `PASS` (`ops/ROLLBACK.md`; previous candidate `44df140`; backup retained)

## Network / port provenance (loopback only; no UFW change)

- API: container 8000 → host `127.0.0.1:8090`
- PostgreSQL: container 5432 → host `127.0.0.1:5433` (isolated `madworld_db`; not public)
- Host `127.0.0.1:8000` remains owned by the unrelated existing project and was never touched.

## Status

`VERIFIED (environment)` for all server-side automated/technical gates and the
GitHub Release Gate on `26b9d22`. External/provider/device/legal gates remain
`UNKNOWN` and require the release owner.

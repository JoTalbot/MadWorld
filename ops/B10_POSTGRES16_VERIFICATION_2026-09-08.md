# B10 Local PostgreSQL 16 Verification — 2026-09-08

## Status and boundary

**VERIFIED: full local backend test suite with real PostgreSQL.**
**NOT VERIFIED: exact-head GitHub CI, Android emulator matrix, production release.**

- Repository / branch: `JoTalbot/MadWorld` / `arena/01a080ed-madworld` (PR #24).
- Tested commit: `879faa4d39c70a50746d288b1b4bfe3fe5d98ee9`.
- Tested backend tree: `8e9e2d5030ae6f4463ab59e24bc64000fac96170`.
- Environment: isolated Linux x86_64 sandbox, Python 3.11.2, PostgreSQL 16.2,
  genuine `pgcrypto` 1.3. GitHub CI's Python 3.12 / container environment was
  **not** substituted or certified by this run.
- Production database, host services, Remote Operator queue and release tags:
  **NOT TOUCHED**.

This continues the CI recovery in `ops/B10_ANDROID_MATRIX_RECOVERY_2026-09-08.md`.
It closes the local PostgreSQL test gap (previously 25 skipped tests), not the
permissions/runner blocker or any Android/owner/environment release gate.

## Verified results

| Check | Result |
|---|---|
| Native PostgreSQL server identity | 16.2 (`server_version_num=160002`) |
| Isolation | private Unix socket, `listen_addresses=''`, no TCP listener; fixture-only `madworld_test` database |
| Initial failed bootstrap recovery | missing `pgcrypto` classified as an environment dependency; transaction left no public tables |
| Genuine `pgcrypto` verification | SHA-256 known answer, PGP encrypt/decrypt roundtrip, random-byte length and bcrypt smoke PASS |
| Fresh authoritative migrations | all **43** applied, including real extension registration; no migration SQL changed |
| Immediate migration rerun | no pending migrations |
| Full backend suite | **281 passed, zero skipped**, one upstream Starlette/AnyIO deprecation warning |
| Ruff / mypy / OpenAPI | PASS / PASS (38 source files) / current |
| Post-suite migration verification | all 43 stored names/checksums exactly match source; rerun applies nothing |
| Post-suite connections | only the verifier's own client connection remained |
| Cleanup | fast shutdown completed; process exited **0**; PID file and socket removed, no listener remains |

Postconditions were verified at **13:43 UTC**; shutdown completed at
**2026-09-08 13:43:20 UTC**. No temporary database process was left running.

## Test-only dependency provenance

The sandbox could install Python packages and fetch GitHub source, but could
not connect to Debian/PGDG package repositories. A native test-only fallback
was used; it is **not** a new application dependency or a production distribution:

- `pgserver==0.1.4` Linux CPython 3.11 wheel supplies PostgreSQL **16.2**, but
  does **not** include `pgcrypto`. Wheel SHA-256:
  `d595789b47624a3d963aa9aa6359da9be31beb7e61f1a45541953242068b8813`.
- Genuine `contrib/pgcrypto` source: `postgres/postgres` tag `REL_16_2`, commit
  `b78fa8547d02fc72ace679fb4d5289dccdbfc781`.
- OpenSSL source: `openssl/openssl` tag `openssl-3.0.20`, commit
  `5aada9c299a3b28fc82348f4e2b93805fa0a0e9c`.
- zlib headers: `madler/zlib` tag `v1.2.13`; Git blob IDs
  `953cb5012dc203171c99d623b1e9aa310c278b12` (`zlib.h`) and
  `bf977d3e70adef441e6d9ee286c30d65de90654e` (`zconf.h`), verified against the
  downloaded contents; linked system zlib 1.2.13.
- Built `pgcrypto.so` SHA-256:
  `7968a968bc3716f37cae85d1a41b03a0f462cab43636946d2da463e51b9b6fc6`.

Dependencies, source archives, compiler output and fixture cluster data stay
under ignored `.venv/` and `.cache/`; none is committed. Do not add this fallback
package to `backend/requirements.txt` or use this old minor version in production.
Prefer a current PostgreSQL 16 distribution with contrib/pgcrypto or the normal
CI container when those channels are available.

### Reproduction outline for the isolated fallback

1. Install the existing backend test dependencies in a venv, then the pinned
   `pgserver==0.1.4` test-only package. Discover its binaries with
   `Path(pgserver.__file__).parent / 'pginstall' / 'bin'`; the README's
   `pgserver.POSTGRES_BIN_PATH` attribute is not exported by this version.
2. Build OpenSSL with `linux-x86_64 no-shared no-tests no-module no-asm -fPIC`,
   then `make -j2 build_libs`. Build matching `contrib/pgcrypto` with PGXS from
   the bundled `pg_config`, `-DUSE_OPENSSL`, the OpenSSL/zlib include directories,
   and link `libcrypto.a`, system `libz.so.1`, `-ldl -pthread`. Install only into
   that venv's PostgreSQL distribution. Do not create a stub extension or edit
   authoritative migration `001_foundation.sql` to bypass the requirement.
3. Initialize a **new** cluster as the unprivileged sandbox user with UTF-8,
   locale `C`, local trust and host reject. Keep the parent/socket directories
   mode 0700. Run PostgreSQL in the foreground through the process manager,
   with no TCP listener and `unix_socket_permissions=0700`.
4. Before mutation, query and assert the exact local data directory, database,
   major version and empty `listen_addresses`. Verify native crypto functions,
   then remove only that fresh fixture extension registration so the first
   migration exercises `CREATE EXTENSION` itself.
5. Set `MADWORLD_DATABASE_URL` to that private socket explicitly; run the
   unmodified migration runner twice, then ruff, mypy, OpenAPI check and the
   entire backend pytest suite. Compare all migration names/checksums afterward.
6. Dispose clients, shut down the owned cluster, wait for terminal exit and
   verify the PID file/socket are absent. Never point this procedure at a
   deployment or at an existing database.

Generated logs/manifests are in ignored `artifacts/b10-ci-continuation/`.
Important results and immutable source identifiers are retained above.

## Remaining CI/Android blocker (rechecked 13:45 UTC)

- PR #24 is still DRAFT at `879faa4`; its Backend CI `34226608687` and Agent
  Governance `34226608688` remain QUEUED, with no terminal conclusion.
- `main` remains `df787dc`; the workflow patch is NOT APPLIED.
- The Remote Operator broker also remained queued on `main`; routing another
  request to the same blocked control plane does not provide execution evidence.
- This sandbox has no `/dev/kvm`; the Android SDK download endpoint was also
  unreachable. No real emulator or APK build was executed here.
- GitHub's Android job-log endpoint returned a storage download redirect, but
  fetching the log failed with EOF. No emulator startup cause is established;
  temporary signed download URLs are not retained in the evidence.

The owner handoff in `docs/patches/README.md` remains required: apply/remove the
workflow patch together on this working branch, reconcile stale Release Gate
runs with an Actions-authorized account, then collect terminal exact-head
workflow results and real emulator artifacts. Do not infer CI or release PASS
from this isolated backend verification.

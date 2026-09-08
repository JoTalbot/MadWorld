# B10 Repository CI Repair Evidence — 2026-09-08

Date: 2026-09-08

## Problem

`main` Backend CI had been red for the entire recent ops window (30+ consecutive
runs, including docs/ops-only commits, failing in under a minute). The exact-head
Release Gate rerun on `main` (queued runs 284/285/287/289 and earlier) therefore
cannot pass until the repository-side failures are fixed and merged.

Five independent repository-side defects caused the red state:

1. **Ruff `I001` import order** in `backend/scripts/migrate.py`
   (`import sys` after `from pathlib import Path`). Regression introduced by
   `fb7b0f3`; only surfaced once `406caa1` restored the ruff gate in Backend CI.
2. **Committed OpenAPI contract drift** — `contracts/openapi.json` still
   contained the removed Firebase push-token API
   (`/api/v1/sessions/push-token`, `PushTokenRequest`, `PushTokenResponse`)
   after `fd4582c`/`59df966` removed it from the application; the contract was
   never regenerated.
3. **Stale release-gate workflow contract guard** — `819af55` added the
   `android-matrix` emulator smoke job to `release-gate.yml` and changed the
   final gate dependency to `needs: [backend, android, android-matrix]`, but
   `test_b10_release_workflow_contract.py` still asserted the old
   `needs: [backend, android]` topology.
4. **Remote Operator request-queue guard violations** — three legacy queue
   records that predate the strict guard in
   `test_remote_operator_requests.py`:
   - `cmd-20260908-050500-capacity-discovery`: `INPUTS_JSON` with invalid
     `\(`/`\)` escapes; executed with terminal SUCCESS evidence on the
     `remote-operator-results` branch (2026-09-08T04:50:24Z, exit 0).
   - `cmd-20260908-060000-prod-firebase-removal` and
     `cmd-20260908-061000-prod-firebase-removal-v2`: no `INPUTS_JSON` in the
     stored record, marked `STATUS: INVALID`, superseded by
     `cmd-20260908-062000-prod-firebase-removal-final`.
   - `cmd-20260908-092000-prod-credential-rotation-diagnostic-v2`:
     `STATUS: HOLD` (operator-paused via `ce34ac8`).
5. **Unpinned lint tooling** in Backend CI (`pip install ... ruff mypy`) is a
   latent drift risk only; no fix applied beyond the deterministic source fixes
   above.

## Fix

Commit `0589ac1` on branch `arena/01a0806c-madworld`, PR #23
(https://github.com/JoTalbot/MadWorld/pull/23):

- `backend/scripts/migrate.py` — import order (ruff `I001`).
- `backend/contracts/openapi.json` — regenerated with
  `python scripts/export_openapi.py` (125 paths; Firebase push-token residue
  removed, consistent with the recorded owner decision that Firebase/FCM is out
  of release scope).
- `backend/tests/test_b10_release_workflow_contract.py` — guard now matches the
  intended gate topology including `android-matrix`.
- `backend/tests/test_remote_operator_requests.py` — classified legacy records
  are on named self-cleaning allowlists (`LEGACY_NON_STRICT_JSON`,
  `LEGACY_MISSING_INPUTS_JSON`, `LEGACY_HOLD_STATUS`); records are never
  rewritten, deleted, or re-executed.
- `ops/remote-operator/RECONCILIATION.md` — evidence-backed classification
  rows added.
- `ops/B10_CI_REPAIR_EVIDENCE_2026-09-08.md` — this record.

## Verification (local, commit 0589ac1)

- `ruff check .` — all checks passed.
- `mypy` — no issues (38 source files).
- `pytest -q` — 224 passed, 25 skipped (PostgreSQL-gated tests skip without
  `MADWORLD_DATABASE_URL`; they run in CI with PostgreSQL 16).
- `python scripts/export_openapi.py --check` — contract up to date.
- `import app.main` — 125 routes, `/api/v1/travel/plan` present.

## Verification (CI, PR #23 commit 0589ac1)

- Backend CI pull_request run `34213184023` — **SUCCESS** (full job: ruff,
  mypy, OpenAPI check, migrations on PostgreSQL 16, module resolution,
  production compose validation, `pytest` — green).
- Agent Governance pull_request run `34213183981` — **SUCCESS**.

## Main state at time of writing

- `main` HEAD `6ec1c4b` still runs the pre-fix code: its Backend CI is red and
  the in-flight Release Gate runs (284/285) fail the `backend` job while their
  `android` job passes and the Android API 26/29/32/35 emulator smoke matrix
  continues (independent evidence capture).
- After PR #23 is merged to `main`, the push event re-triggers Backend CI and
  the Release Gate on the fixed exact head (paths `backend/**` match); the
  scheduled Remote Operator broker continues consuming pending request records.

## Remaining mandatory gates (unchanged, external/owner)

Full 5-minute controlled isolated capacity run with queue-depth evidence;
Android API 26/29–32 device-or-emulator evidence completion (matrix runs in the
release gate) plus physical-device validation; Privacy/Terms/Data
Safety/deletion legal review and publication; account-deletion implementation
verification or owner-approved manual process; rollback rehearsal; exact-head
Release Gate rerun on the final release commit; artifact digest freeze; final
version/tag and production publication after the owner GO decision.

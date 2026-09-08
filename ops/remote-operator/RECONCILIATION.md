# Remote Operator pending-queue reconciliation

`COMMANDS.txt` is append-only and remains the immutable audit trail. Reconciliation never rewrites, deletes, or fabricates queue execution results.

## Execution safety policy

A `PENDING` command is executable only when all conditions hold:

1. `COMMAND_ID` has the documented format.
2. No terminal or busy state record exists for that ID.
3. A valid `CREATED_AT` timestamp exists.
4. Pending age is no greater than `REMOTE_OPERATOR_PENDING_MAX_AGE_SECONDS`, default 24 hours.

Legacy/orphan `PENDING` records without `CREATED_AT` are reported as `ORPHAN_PENDING_WITHOUT_CREATED_AT` and are **never executed automatically**. Timestamped records older than the configured threshold are reported as stale and are **never executed automatically**.

Terminal and busy states remain non-replayable:

- `CLAIMED` / `RUNNING`: active, do not re-execute.
- `DONE` / `FAILED` / `TIMEOUT` / `CANCELLED` / `INTERRUPTED` / `INVALID`: terminal, do not re-execute.

This policy closes the historical-queue hazard where an old `PENDING` entry could become executable solely because its state file was missing.

## Reconciliation

`ops/remote-operator/reconcile-stale-pending.sh` is read-only. It reports orphan and stale candidates and explicitly records that the queue was not modified. Any future automated retirement/quarantine must be executor/state-manager owned, create a verifiable terminal record, and preserve the original command as immutable audit history.

## Workflow-dispatch REQUESTS queue: silent-skip hazard

`.github/remote-operator/REQUESTS/` is a second, independent queue consumed by the
`remote-operator-workflow-dispatch.yml` broker. Its failure mode is different from `COMMANDS.txt`:

The broker only accepts a record whose `COMMAND_ID` matches `cmd-[0-9]{8}-[0-9]{6}-[A-Za-z0-9._-]+`.
A record that fails that regex is **skipped with `continue` — silently, with no state record, no
result, no warning, and no reconciliation report**. Such a record stays `PENDING` forever and looks
like a queued command that is merely waiting. The same applies to a record whose `INPUTS_JSON` is
not a single-line JSON object, or, for `remote-operator-dispatch.yml`, whose `command` input is empty.

`backend/tests/test_remote_operator_requests.py` now enforces the broker's own acceptance rules on
every request record, so a new unexecutable request fails CI instead of silently rotting in the queue.

### Classified legacy orphan records (2026-09-08)

Both are immutable history and are **not** rewritten, deleted, or marked DONE. Neither requires
re-execution:

| Record | Defect | Classification |
|---|---|---|
| `cmd-20260907-governance-recheck` (`20260907-governance-recheck.txt`) | `COMMAND_ID` has no `HHMMSS` segment, so the broker never accepted it | `ORPHAN_NEVER_EXECUTABLE` / superseded — its intent was a re-run of `agent-governance.yml`, which runs on every push to `main` and has since completed `success` many times. No action required. |
| `cmd-20260907-remote-governance-dispatch` (`20260907-governance-remote-dispatch.txt`) | same malformed `COMMAND_ID` | `ORPHAN_NEVER_EXECUTABLE` / superseded by `cmd-20260907-134800-remote-governance-dispatch`, which has terminal evidence on the `remote-operator-results` branch. No action required. |

Four further records (`20260907-144100-economy-overview-500-env-discovery`,
`20260907-172600-cloudflare-access-diagnose`, `20260907-dr-isolated-rehearsal-direct-v2`,
`20260907-dr-isolated-rehearsal-workflow-dispatch`) contain `INPUTS_JSON` with invalid JSON escapes.
These were executed only because the broker applies a documented escape-repair fallback before
parsing. They are accepted as-is, but new records must be strict JSON; the guard test enforces that
for anything not on the classified legacy list.

### Classified legacy records (2026-09-08, late batch)

The following records predate the current strict form of the guard test
(`backend/tests/test_remote_operator_requests.py`). All are immutable history;
none is rewritten, deleted, or re-executed:

| Record | Defect | Classification |
|---|---|---|
| `cmd-20260908-050500-capacity-discovery` (`20260908-050500-capacity-discovery.txt`) | `INPUTS_JSON` uses invalid `\(`/`\)` escapes (strict JSON would reject it) | `EXECUTED_VIA_REPAIR` — terminal SUCCESS evidence on the `remote-operator-results` branch (`cmd-20260908-050500-capacity-discovery.json`, exit 0, 2026-09-08T04:50:24Z). No re-execution. |
| `cmd-20260908-060000-prod-firebase-removal` (`20260908-060000-production-firebase-removal.txt`) | No `INPUTS_JSON` in the stored record; `WORKFLOW: remote-operator-dispatch.yml` | Terminal. Executed FAILED (exit 1, `POSTGRES_USER: unbound variable`, 2026-09-08T03:11:19Z; result on `remote-operator-results`), record marked `STATUS: INVALID`. Superseded by `cmd-20260908-062000-prod-firebase-removal-final`. No re-execution. |
| `cmd-20260908-061000-prod-firebase-removal-v2` (`20260908-061000-production-firebase-removal-v2.txt`) | No `INPUTS_JSON` in the stored record; `WORKFLOW: remote-operator-dispatch.yml` | Terminal. Never executed (no terminal result record exists), marked `STATUS: INVALID` with reason. Superseded by `cmd-20260908-062000-prod-firebase-removal-final`. No re-execution. |
| `cmd-20260908-092000-prod-credential-rotation-diagnostic-v2` (`20260908-092000-prod-credential-rotation-diagnostic-v2.txt`) | `STATUS: HOLD` is not an execution state | Paused by operator commit `ce34ac8`; never executed from `HOLD`; superseded by later credential-rotation diagnostic attempts. No action required. |

The guard test keeps each classified ID on a named allowlist
(`LEGACY_NON_STRICT_JSON`, `LEGACY_MISSING_INPUTS_JSON`, `LEGACY_HOLD_STATUS`)
and fails CI if any allowlisted ID disappears or a new record repeats the same
defect.

## Verification

`ops/remote-operator/test-reconcile-stale-pending.sh` exercises the legacy/orphan and fresh timestamp cases. `.github/workflows/reconcile-stale-pending.yml` runs the test and publishes the reconciliation audit as an artifact.

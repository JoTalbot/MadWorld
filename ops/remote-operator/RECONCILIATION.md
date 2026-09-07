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

## Verification

`ops/remote-operator/test-reconcile-stale-pending.sh` exercises the legacy/orphan and fresh timestamp cases. `.github/workflows/reconcile-stale-pending.yml` runs the test and publishes the reconciliation audit as an artifact.

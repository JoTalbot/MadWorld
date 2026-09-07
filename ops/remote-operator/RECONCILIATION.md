# Remote Operator stale-PENDING reconciliation

The canonical command queue is append-only and remains an audit trail. Historical `PENDING` entries must not be silently rewritten to `DONE` or `CANCELLED` because that would fabricate executor state.

`reconcile-stale-pending.sh` performs a read-only audit. It identifies PENDING commands older than the configured age that have no terminal/busy state record. It does **not** execute, mutate, or delete queue entries.

## Policy

- PENDING + no state: candidate for manual/owner disposition, not execution evidence.
- CLAIMED/RUNNING: active and must not be re-executed.
- DONE/FAILED/TIMEOUT/CANCELLED/INTERRUPTED/INVALID: terminal and must not be re-executed.
- Queue history is immutable.
- Any future automated retirement mechanism must create a verifiable executor-owned terminal record before excluding a command from execution.

Default stale threshold: 24 hours.

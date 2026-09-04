# Remote Operator Engine Specification

## Goal

When the deployed server copy of `.github/remote-operator/COMMANDS.txt` changes, the server-side operator detects the change and executes only new `PENDING` commands. Execution is observable, bounded, cancellable, resumable through explicit recovery, and recorded back into the repository.

## Canonical data model

`COMMANDS.txt` is the human/agent-facing command input. Each command has an immutable `COMMAND_ID`.

Execution state is kept separately in `.github/remote-operator/state/<COMMAND_ID>.json` so the original command remains an audit record and result commits do not need to rewrite the input queue.

Results are stored in `.github/remote-operator/results/<COMMAND_ID>/`:

- `result.json` — machine-readable metadata and lifecycle timestamps.
- `result.md` — concise human-readable report.
- `stdout.log` — captured standard output.
- `stderr.log` — captured standard error.

## Lifecycle

```text
PENDING
  -> CLAIMED
  -> RUNNING
  -> DONE
  -> FAILED
  -> TIMEOUT
  -> CANCELLED
  -> INTERRUPTED
```

Only valid transitions are accepted. `COMMAND_ID` is the idempotency key. `ATTEMPT_ID` identifies one execution attempt.

## Detection

A persistent systemd watcher uses Linux `inotify` where available. It debounces bursts of filesystem events and rescans the queue after every change. It also performs a periodic safety rescan so an event loss cannot permanently strand a command.

A change is not itself permission to execute every line. The parser selects only syntactically valid commands whose current state is `PENDING` and whose `COMMAND_ID` has not already completed.

## Claiming and concurrency

Claiming must be atomic. A per-command lock prevents two workers from executing the same `COMMAND_ID` concurrently.

Default concurrency is 4. Independent commands can execute concurrently. Optional resource locks prevent conflicting commands from running together.

The original command is never changed during execution. State files contain `CLAIMED_AT`, `STARTED_AT`, `ATTEMPT_ID`, executor identity, PID/process-group information, and the latest state.

## Execution and timing

Every attempt records:

- `CREATED_AT`
- `CLAIMED_AT`
- `STARTED_AT`
- `FINISHED_AT`
- `QUEUE_WAIT_SECONDS`
- `EXECUTION_SECONDS`
- `DURATION_SECONDS`
- `EXIT_CODE`

Commands run in a dedicated process group. The configured timeout is enforced by the executor, not by the shell command itself.

## Timeout and cancellation

On timeout or cancellation, send `SIGTERM` to the process group and wait 15 seconds. If descendants remain, send `SIGKILL` to the group. Capture the final stdout/stderr and mark the attempt `TIMEOUT` or `CANCELLED`.

A timeout does not automatically retry a command. This avoids duplicate side effects for non-idempotent commands.

## Recovery

If the server restarts while a command is `RUNNING`, the executor marks the attempt `INTERRUPTED` after validating that its recorded process group no longer exists. It does not silently rerun the command. Recovery requires an explicit new attempt/retry policy.

## Result synchronization

Results and state are committed to the repository by the server using a dedicated bot identity/credential configured outside the repository. The credential must be least-privilege and must never appear in queue files, logs, artifacts, or result content.

Result commits must not trigger the normal application deployment loop. The deployment workflow is for GitHub-to-server synchronization; operator result synchronization is server-to-GitHub only.

## Failure behavior

If GitHub result synchronization fails, the local result remains durable under the project directory and is retried by the result-sync worker. The command is not re-executed merely because result publication failed.

If command parsing fails, the invalid entry is reported as `INVALID` with a diagnostic result. It is never executed as a fallback.

## Recommended status vocabulary

`PENDING`, `CLAIMED`, `RUNNING`, `DONE`, `FAILED`, `TIMEOUT`, `CANCELLED`, `INTERRUPTED`, `INVALID`.

## Security requirements

- Never store secrets in `COMMANDS.txt`.
- Never echo private keys or tokens.
- Use strict SSH host-key verification where SSH is used.
- Do not delete server-only files during normal repository deployment.
- Do not automatically retry non-idempotent commands.
- Do not execute an already terminal command under the same `COMMAND_ID`.
- Preserve command text and result metadata as an audit trail.

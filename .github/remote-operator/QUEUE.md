# Remote Operator Queue

The repository uses one canonical append-only queue file: `.github/remote-operator/COMMANDS.txt`.

## Lifecycle

`PENDING -> CLAIMED -> RUNNING -> DONE`

Failure:

`RUNNING -> FAILED | TIMEOUT`

A command must have a unique immutable `COMMAND_ID`. Agents must never reuse an ID.

## Command format

Append one command block to the end of `.github/remote-operator/COMMANDS.txt`:

```text
---
COMMAND_ID: cmd-YYYYMMDD-HHMMSS-unique
STATUS: PENDING
AGENT: <agent-id>
CREATED_AT: <UTC timestamp>
TIMEOUT_MINUTES: 30
MODE: sync

COMMAND:
<shell command or bash script>
---
```

## Concurrency rules

1. Only `PENDING` commands are eligible for execution.
2. An executor must atomically claim a command before execution by changing its state to `CLAIMED` and recording the attempt/claim metadata.
3. A claimed command must become `RUNNING` before the remote command starts.
4. A command already marked `CLAIMED`, `RUNNING`, `DONE`, `FAILED`, or `TIMEOUT` must never be executed again automatically under the same `COMMAND_ID`.
5. The `COMMAND_ID` is the idempotency key.
6. Results belong to the command ID and should be stored separately from the queue definition when output is large.
7. A crashed executor must not silently cause duplicate execution. Recovery requires an explicit stale-claim policy and a new `ATTEMPT_ID`.
8. Parallel agents may process different command IDs concurrently, provided the claim mechanism is concurrency-safe.
9. An agent must not modify another agent's active command.
10. Secrets and credentials must never be stored in queue files.
11. Completed commands remain in the queue as an audit trail.

## Result format

For every completed attempt, store:

```text
COMMAND_ID: <id>
ATTEMPT_ID: <id>-attempt-N
STATUS: DONE | FAILED | TIMEOUT
EXIT_CODE: <integer>
STARTED_AT: <UTC timestamp>
FINISHED_AT: <UTC timestamp>
EXECUTOR: <executor-id>

COMMAND:
<exact command executed>

STDOUT:
<captured stdout>

STDERR:
<captured stderr>
```

The full stdout/stderr may be stored in the corresponding Actions artifact and/or a separate repository result file. Never store secrets in either location.

## Current implementation boundary

The queue protocol is committed to the repository. The current GitHub connector does not expose workflow dispatch and cannot safely create the arbitrary SSH execution workflow required to consume this queue. Consequently, queue entries must remain `PENDING` until an actual executor performs and verifies the command.

Do not mark commands `DONE` merely because they were committed.

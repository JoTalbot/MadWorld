# Remote Operator Queue

The queue is designed for multiple parallel agents.

## Lifecycle

`PENDING -> CLAIMED -> RUNNING -> DONE`

Failure:

`RUNNING -> FAILED`

A command must have a unique immutable ID. Agents must never reuse an ID.

## Command format

Create one command file per request under `.github/remote-operator/queue/` using:

```text
ID: cmd-YYYYMMDD-HHMMSS-unique
STATUS: PENDING
AGENT: <agent-id>
CREATED_AT: <UTC timestamp>
TIMEOUT_MINUTES: 30
MODE: sync

COMMAND:
<shell command or bash script>
```

## Concurrency rules

1. Only `PENDING` commands are eligible for execution.
2. An agent must atomically claim a command before execution by changing its state to `CLAIMED` and recording its agent ID and claim timestamp.
3. A claimed command must then become `RUNNING` before the remote command starts.
4. A command already marked `CLAIMED`, `RUNNING`, `DONE`, or `FAILED` must never be executed again automatically.
5. The command ID is the idempotency key.
6. Results belong to the command ID and are stored separately from the queue definition.
7. A crashed agent must not silently cause duplicate execution. Recovery requires an explicit stale-claim policy and a new attempt ID.
8. Parallel agents may process different command IDs concurrently.
9. An agent must not modify another agent's active command.
10. Secrets and credentials must never be stored in queue files.

## Result format

For every completed attempt, store:

```text
COMMAND_ID: <id>
ATTEMPT_ID: <id>-attempt-N
STATUS: DONE | FAILED | TIMEOUT
EXIT_CODE: <integer>
STARTED_AT: <UTC timestamp>
FINISHED_AT: <UTC timestamp>
AGENT: <agent-id>

COMMAND:
<exact command executed>

STDOUT:
<captured stdout>

STDERR:
<captured stderr>
```

The queue file should remain as an audit record. Do not delete completed commands.

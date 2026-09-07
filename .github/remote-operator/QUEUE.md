# Remote Operator Queue

The repository uses append-only request records under `.github/remote-operator/REQUESTS/`. Each request is immutable and identified by a unique `COMMAND_ID`.

For workflow-dispatch operations, the request record is consumed by the Remote Operator workflow-dispatch broker. Terminal evidence is written to the `remote-operator-results` branch under `.github/remote-operator/workflow-dispatch/<COMMAND_ID>.json`.

## Lifecycle

Request record:

`PENDING -> broker claim/execution -> terminal result`

Remote command execution itself follows:

`PENDING -> CLAIMED -> RUNNING -> DONE`

Failure:

`RUNNING -> FAILED | TIMEOUT`

A command must have a unique immutable `COMMAND_ID`. Agents must never reuse an ID.

## Workflow-dispatch request format

Create a new file under `.github/remote-operator/REQUESTS/`:

```text
---
COMMAND_ID: cmd-YYYYMMDD-HHMMSS-unique
STATUS: PENDING
AGENT: <agent-id>
CREATED_AT: <UTC timestamp>
TIMEOUT_MINUTES: 30
MODE: workflow_dispatch
TYPE: WORKFLOW_DISPATCH
WORKFLOW: <workflow-file.yml>
REF: main
INPUTS_JSON: {"input_name":"value"}
---
```

For direct server execution, use the documented Remote Operator request format for the server-execution workflow rather than inventing a second queue location.

## Concurrency and idempotency

1. Only `PENDING` requests are eligible for execution.
2. The executor/broker must claim work safely before execution and must not execute the same `COMMAND_ID` twice automatically.
3. A command already represented by terminal evidence must not be re-executed under the same `COMMAND_ID`.
4. `COMMAND_ID` is the immutable idempotency key; retries require a new command ID/attempt according to the executor policy.
5. Results belong to the command ID and should be stored separately from the request definition when output is large.
6. A crashed executor must not silently cause duplicate execution. Recovery requires an explicit stale-claim policy and a new attempt identity.
7. Parallel agents may process different command IDs concurrently, provided claim/execution is concurrency-safe.
8. An agent must not modify another agent's active command.
9. Secrets and credentials must never be stored in request files or result records.
10. Completed requests remain as immutable audit history.

## Mandatory terminal-result rule

Appending a request is submission evidence only. Dispatching a workflow is not execution evidence. Every queued operation must wait/poll until the target reaches a terminal result or the configured timeout, then verify workflow status, job status/conclusion, exit code where applicable, stdout/stderr, `result.json` and artifacts where applicable.

A timeout is a terminal outcome, not permission to assume success.

## Current verified implementation

The workflow-dispatch broker is an active Remote Operator control-plane component. It uses the repository-scoped ephemeral `GITHUB_TOKEN` with `actions: write` to dispatch target workflows and waits for their terminal state. The verified standard path is documented in `docs/REMOTE_OPERATOR_WORKFLOW_DISPATCH.md`.

The broker's GitHub dispatch path avoids requiring GitHub CLI authentication on the server. Server-side commands must not assume that `gh` is authenticated unless the execution workflow explicitly provisions and scopes credentials for that operation.

Do not mark commands `DONE` merely because a request was committed or a workflow was dispatched. Only terminal execution evidence may establish completion.

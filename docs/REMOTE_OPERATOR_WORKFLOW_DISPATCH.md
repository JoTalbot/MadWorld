# Remote Operator: GitHub Actions workflow dispatch

## Purpose

Remote Operator can launch GitHub Actions workflows that are normally started through the GitHub Actions **Run workflow** UI. The request is queued as a `TYPE: WORKFLOW_DISPATCH` record and is executed by the Remote Operator workflow-dispatch broker.

The broker is part of the Remote Operator control plane. It runs on queue changes, on a five-minute safety schedule, or manually. It uses the repository-scoped `GITHUB_TOKEN` with `actions: write` to call GitHub's workflow-dispatch API, then waits for the target workflow to reach a terminal state.

GitHub explicitly supports `workflow_dispatch` from a workflow using `GITHUB_TOKEN`. citehttps://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow

## Request format

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

Rules:

- `COMMAND_ID` is immutable and unique.
- `STATUS` remains `PENDING` in the request. It is an append-only request/audit record.
- Terminal execution evidence is written to `remote-operator-results` under `.github/remote-operator/workflow-dispatch/<COMMAND_ID>.json`.
- Secrets must never be placed in the request.
- Only workflows that already expose `workflow_dispatch` may be targeted.
- Inputs are limited by GitHub's workflow-dispatch API to the inputs declared by the target workflow.

## Execution lifecycle

```text
Remote Operator request
        ↓
workflow-dispatch broker
        ↓
GitHub workflow_dispatch API
        ↓
target Actions workflow
        ↓
poll workflow run
        ↓
inspect jobs + artifacts
        ↓
terminal result
        ↓
remote-operator-results
```

A successful API dispatch is **not** a successful operation. The broker waits for the target workflow and records `DONE`, `FAILED`, or `TIMEOUT` according to the terminal workflow result.

## Evidence

The result record contains:

- command ID;
- target workflow and ref;
- supplied inputs;
- workflow run ID and URL;
- workflow status and conclusion;
- job status/conclusion;
- artifact metadata;
- executor identity;
- start/end timestamps;
- duration;
- error information when applicable.

The target workflow remains responsible for producing its own `result.json`, stdout, stderr and artifacts. Those artifacts are the authoritative execution evidence for the target operation.

## Example

For the universal Remote Operator workflow:

```text
---
COMMAND_ID: cmd-YYYYMMDD-HHMMSS-diagnostics
STATUS: PENDING
AGENT: chatgpt
CREATED_AT: 2026-09-07T00:00:00Z
TIMEOUT_MINUTES: 10
MODE: workflow_dispatch
TYPE: WORKFLOW_DISPATCH
WORKFLOW: remote-operator.yml
REF: main
INPUTS_JSON: {"operation":"diagnostics","command":"","mode":"sync","timeout_minutes":"2","workdir":"","cleanup":"true"}
---
```

This replaces the need for a human to open Actions and press **Run workflow**.

## Safety

The broker does not modify `COMMANDS.txt` terminal states and does not put GitHub credentials into server-side queue files. It uses the ephemeral `GITHUB_TOKEN` supplied to the broker workflow. GitHub documents `Actions: write` as the required repository permission for creating a workflow-dispatch event. citehttps://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event

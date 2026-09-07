# Remote Operator: GitHub Actions workflow dispatch

## Purpose

Remote Operator can launch GitHub Actions workflows that are normally started through the GitHub Actions **Run workflow** UI. The request is queued as a `TYPE: WORKFLOW_DISPATCH` record and is executed by the Remote Operator workflow-dispatch broker.

The broker is part of the Remote Operator control plane. It runs on queue changes, on a five-minute safety schedule, or manually. It uses the repository-scoped `GITHUB_TOKEN` with `actions: write` to call GitHub's workflow-dispatch API, then waits for the target workflow to reach a terminal state.

GitHub explicitly supports `workflow_dispatch` from a workflow using `GITHUB_TOKEN`.

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
- The broker must wait for the target workflow to reach a terminal state or its configured timeout. Dispatching the API request alone is never sufficient evidence.

## Verified standard path

For MadWorld's universal Remote Operator, use the **wrapper workflow** `remote-operator-dispatch.yml`. It calls the existing reusable Remote Operator workflow and has been end-to-end verified through this broker, including root execution and result artifact publication.

The legacy `remote-operator.yml` declares `workflow_dispatch` in the repository source, but direct API dispatch has returned GitHub HTTP 422 saying that the workflow does not have a `workflow_dispatch` trigger. Until GitHub's workflow metadata/API state is independently reconciled, it is treated as **legacy / NOT VERIFIED for direct dispatch**, not as the standard path.

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

## Verified wrapper example

For the standard wrapper workflow:

```text
---
COMMAND_ID: cmd-YYYYMMDD-HHMMSS-diagnostics
STATUS: PENDING
AGENT: chatgpt
CREATED_AT: 2026-09-07T00:00:00Z
TIMEOUT_MINUTES: 10
MODE: workflow_dispatch
TYPE: WORKFLOW_DISPATCH
WORKFLOW: remote-operator-dispatch.yml
REF: main
INPUTS_JSON: {"command":"id -un; id -u; hostname -s","timeout_minutes":"2","workdir":"","cleanup":"true"}
---
```

The verified end-to-end run used this path and produced a successful terminal workflow result, a successful root-level remote command, and the `remote-operator-result` artifact. This replaces the need for a human to open Actions and press **Run workflow**.

## Safety

The broker does not modify `COMMANDS.txt` terminal states and does not put GitHub credentials into server-side queue files. It uses the ephemeral `GITHUB_TOKEN` supplied to the broker workflow. GitHub documents `Actions: write` as the required repository permission for creating a workflow-dispatch event.

All technical actions that would otherwise require a human operator should be routed through Remote Operator. A manual human step is allowed only when Remote Operator is technically incapable of performing it or when explicit legal/owner approval is inherently required.

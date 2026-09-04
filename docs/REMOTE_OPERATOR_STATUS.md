# Remote Operator: Current Status

## Repository state

The remote-operator architecture and operating rules are stored in GitHub.

Implemented repository components:

- `.github/workflows/remote-operator.yml` — SSH operator workflow with sync/async execution and result artifacts.
- `.github/remote-operator/COMMANDS.txt` — canonical append-only Bash command queue.
- `.github/remote-operator/QUEUE.md` — queue lifecycle, idempotency and concurrency protocol.
- `.github/remote-operator/COMMAND.txt` — legacy single-command file; do not use for new requests.
- `docs/REMOTE_OPERATOR.md` — operator documentation.
- `AGENTS.md` — agent rules for GitHub, Remote Operator and the command queue.

## Required secrets

The workflow expects these GitHub repository secrets:

- `REMOTE_SSH_HOST`
- `REMOTE_SSH_PORT`
- `REMOTE_SSH_USER`
- `REMOTE_SSH_PRIVATE_KEY`
- `REMOTE_SSH_HOST_KEY`
- `REMOTE_WORKDIR` (optional)

No secret values belong in the repository.

## Execution protocol

1. An agent appends a unique command to `COMMANDS.txt` with `STATUS: PENDING`.
2. An executor claims the command before starting it.
3. The executor changes the lifecycle to `RUNNING`.
4. The executor runs the exact command over SSH.
5. The executor records `DONE`, `FAILED`, or `TIMEOUT`, together with exit code and attempt metadata.
6. stdout/stderr are preserved in the execution result and/or Actions artifact.
7. The original command remains in the queue as an audit record.

## Important limitation

At the time this document was committed, the connected GitHub tooling available to ChatGPT could read and write repository files and inspect Actions, but it did not expose a `workflow_dispatch` operation. It also rejected creation of the arbitrary SSH-execution workflow through its security boundary.

Therefore this repository must not pretend that a queued command was executed when there is no verified Actions run. The correct status is `NOT EXECUTED` until an executor actually runs the command and the result is verified.

## Security invariants

- No command allowlist is required by the intended operator design.
- SSH host-key verification must remain enabled.
- Secrets and private keys must never appear in queue files, source files, logs, artifacts, issues or reports.
- No force push is required.
- Failed or timed-out commands are not silently retried under the same `COMMAND_ID`.
- Parallel execution is permitted only when command claiming is concurrency-safe.

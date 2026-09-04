# Universal Remote Operator

This repository uses GitHub Actions and a server-side queue executor as an SSH bridge to the configured Linux server.

## Canonical documentation

For reusable installation and migration instructions, see:

- `docs/REMOTE_OPERATOR_UNIVERSAL.md` — setup for **new projects and existing/legacy projects**;
- `docs/REMOTE_OPERATOR_INSTALL.md` — server installation;
- `.github/remote-operator/QUEUE.md` — queue protocol and lifecycle;
- `AGENTS.md` — mandatory agent behavior, including waiting for results.

## Agent access

**All MadWorld AI agents may use the Remote Operator SSH module for server-side work.**

Use it whenever a task requires access to the Linux server, including:

- diagnostics and health checks;
- testing against the deployed environment;
- service/systemd inspection and maintenance;
- deployment and post-deployment verification;
- database checks and migrations when explicitly required by the task;
- logs, filesystem, Docker and networking checks;
- recovery and operational procedures.

The agent-facing interface is the canonical command queue:

`.github/remote-operator/COMMANDS.txt`

The installed server-side executor watches this queue and executes pending commands over the configured server account. Agents must treat the queue and recorded execution result as the audit trail.

## Required GitHub repository secrets

- `REMOTE_SSH_HOST`
- `REMOTE_SSH_PORT`
- `REMOTE_SSH_USER`
- `REMOTE_SSH_PRIVATE_KEY`
- `REMOTE_SSH_HOST_KEY`
- `REMOTE_WORKDIR` (optional)

`REMOTE_SSH_HOST_KEY` must be a complete `known_hosts` entry, not only a bare public-key blob. Keep strict host-key verification enabled.

Secret values must never be committed or printed.

## Workflow

`.github/workflows/remote-operator.yml` supports SSH command execution through GitHub Actions.

Inputs:

- `operation`: `command` or `diagnostics`
- `command`: arbitrary shell command or multiline Bash script
- `mode`: `sync` or `async`
- `timeout_minutes`: timeout for async polling
- `workdir`: optional remote working directory
- `cleanup`: cleanup for completed async jobs

## Server-side queue executor

The production server also runs the Remote Operator queue executor as a systemd service.

Relevant components:

- `ops/remote-operator/executor.sh`
- `ops/remote-operator/watcher.sh`
- `ops/remote-operator/state-manager.sh`
- `ops/remote-operator/result-manager.sh`
- `ops/remote-operator/cancel.sh`
- `ops/remote-operator/madworld-remote-operator.service`
- `ops/remote-operator/result-sync.sh`

The executor supports parallel independent commands, bounded concurrency, command timeouts, cancellation, process-group cleanup and idempotent command IDs.

Agents should not bypass this mechanism for tasks intended to run through Remote Operator.

## Mandatory wait-for-result rule

Putting a command into the queue is only **submission**, not execution completion.

After submitting a command, the agent must wait until a terminal state is recorded:

`DONE | FAILED | TIMEOUT | CANCELLED | INTERRUPTED | INVALID`

The agent must inspect the actual result, including exit code and available stdout/stderr, before reporting success or starting a dependent operation.

`async` means polling is required. It does **not** mean fire-and-forget.

If the timeout expires without a trustworthy terminal result, report `TIMEOUT` or `UNKNOWN`; never invent success.

## Sync

`sync` keeps SSH attached until the remote command exits and returns stdout, stderr and exit code.

## Async

`async` starts a detached remote process, records its PID and logs, then polls until completion or timeout.

## Results

Each workflow run publishes an artifact named `remote-operator-result` containing:

- `result.json`
- `result.md`
- `stdout.log`
- `stderr.log`

The server-side executor additionally stores state and results under `.github/remote-operator/state/` and `.github/remote-operator/results/`.

Runtime state/results are published to the dedicated `remote-operator-results` branch and are intentionally excluded from normal deployment triggers. They must not be pushed into `main` as runtime-result commits.

## Command queue

The canonical agent-facing queue is `.github/remote-operator/COMMANDS.txt`.

- New remote Bash requests are appended only to the end of `COMMANDS.txt`.
- Every request has a unique immutable `COMMAND_ID` and starts as `STATUS: PENDING`.
- Commands must not contain secrets.
- The intended lifecycle is `PENDING -> CLAIMED -> RUNNING -> DONE`, with `FAILED`, `TIMEOUT`, `CANCELLED`, `INTERRUPTED` and `INVALID` terminal states where applicable.
- Completed commands remain available as an audit trail.
- Parallel agents may append independent commands but must not rewrite active commands belonging to other agents.
- Detailed queue and concurrency rules are documented in `.github/remote-operator/QUEUE.md`.
- `.github/remote-operator/COMMAND.txt` is legacy and must not be used for new requests.

## Automatic queue execution status

The repository documents both the GitHub Actions SSH bridge and the installed server-side queue executor.

A queue entry is **not** considered executed merely because it was appended to `COMMANDS.txt`. The agent must verify the actual state/result and, where applicable, stdout, stderr and exit code.

Do not replace an unverified execution with a fake success state or an unverified claim.

## Security

The operator intentionally does not use a command allowlist. Access is constrained by the SSH account, GitHub Secrets, host-key verification and Linux permissions on the server.

Secrets, private keys, passwords, tokens, cookies and other credentials must never appear in queue entries, logs, artifacts, repository files, issues or reports.

Do not use force push or destructive production operations unless explicitly required and authorized by the task.

## ChatGPT / agent operation

When server access is required, agents should use the Remote Operator SSH module rather than inventing a local-only result. Prefer the canonical queue for server-side execution when working through the installed production executor. Always report the actual execution status and evidence.

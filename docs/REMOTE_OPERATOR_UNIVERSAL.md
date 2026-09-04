# Remote Operator: universal setup for new and existing projects

## 1. Purpose

Remote Operator is the standard SSH execution layer for AI-agent work that requires access to a Linux server.

The canonical model is:

`AI agent -> GitHub queue -> deployed project checkout -> server watcher -> executor -> result/state -> result-sync -> GitHub`

The design deliberately supports arbitrary shell commands. There is no command allowlist. Access is controlled by the SSH account, GitHub credentials, host-key verification and Linux permissions.

## 2. Non-negotiable execution rule

A task is **not complete** when it is merely appended to the queue.

After creating a remote task, the agent must:

1. record a unique `COMMAND_ID`;
2. wait for the executor to claim and run it;
3. poll or fetch the recorded state/result;
4. wait until a terminal status is reached: `DONE`, `FAILED`, `TIMEOUT`, `CANCELLED`, `INTERRUPTED` or `INVALID`;
5. inspect the exit code and, where available, stdout/stderr;
6. only then report the result or start a dependent next step.

For a timeout, the agent must report `TIMEOUT` or `UNKNOWN`; it must never convert an unverified task into success.

## 3. New project: recommended bootstrap

### 3.1 Repository files

Add these components to the new project:

```text
.github/
  workflows/
    deploy-on-push.yml
  remote-operator/
    COMMANDS.txt
    QUEUE.md
    state/
    results/
ops/
  remote-operator/
    executor.sh
    watcher.sh
    state-manager.sh
    result-manager.sh
    cancel.sh
    result-sync.sh
    install.sh
    <project>-remote-operator.service
    <project>-remote-operator-sync.service
    <project>-remote-operator-sync.timer
```

Copy the implementation from this repository and change only project-specific paths, service names and configuration. Keep the queue protocol and terminal-state semantics intact.

### 3.2 GitHub secrets

Configure, outside the repository:

- `REMOTE_SSH_HOST`
- `REMOTE_SSH_PORT`
- `REMOTE_SSH_USER`
- `REMOTE_SSH_PRIVATE_KEY`
- `REMOTE_SSH_HOST_KEY`
- `REMOTE_WORKDIR`

`REMOTE_SSH_HOST_KEY` must contain a valid `known_hosts` entry, for example:

```text
<host-or-ip> ssh-ed25519 <public-host-key>
```

Do not disable `StrictHostKeyChecking` and do not commit private keys or tokens.

### 3.3 Server bootstrap

On the target server, create the project checkout at the configured workdir and make sure the SSH user owns the checkout and can run the required project commands.

Then install the server-side operator from the checkout:

```bash
cd <REMOTE_WORKDIR>
git pull --ff-only origin main
sudo ./ops/remote-operator/install.sh <REMOTE_WORKDIR>
```

Enable and start the operator and result-sync services/timer installed by the project.

Verify all of the following before using production commands:

```bash
systemctl is-enabled <project>-remote-operator.service
systemctl is-active <project>-remote-operator.service
systemctl is-enabled <project>-remote-operator-sync.timer
systemctl is-active <project>-remote-operator-sync.timer
```

### 3.4 First test

Append a harmless one-minute smoke command to `COMMANDS.txt`. Never use a production migration, restart or destructive command as the first test.

Wait for the actual result and verify:

- state exists;
- status is terminal;
- exit code is correct;
- stdout/stderr are captured;
- result-sync publishes the result without changing the command into a second execution.

## 4. Existing/legacy project: migration

Do not rebuild the application merely to add Remote Operator. Treat Remote Operator as an operational layer around the existing project.

### Phase A: inventory

Identify:

- repository default branch;
- production checkout path;
- Linux user running the project;
- current deployment mechanism;
- current systemd/Docker/process supervisor;
- current Git authentication on the server;
- current GitHub Actions workflows;
- existing SSH host key;
- backup/recovery procedure;
- services that must not be interrupted during installation.

### Phase B: add operator files

Add the Remote Operator implementation and documentation under `.github/remote-operator/`, `ops/remote-operator/` and `docs/`.

Do not overwrite application configuration or runtime data. Keep existing project services intact.

### Phase C: install alongside the application

Install the operator as a separate systemd service. It should watch only the project's canonical queue.

Install result-sync separately so runtime state/results do not pollute the application's normal deployment branch.

The recommended result branch is:

`remote-operator-results`

Runtime result commits must not be deployed back into the application checkout as ordinary code changes.

### Phase D: validate without production impact

Use a read-only diagnostic/smoke command first. Then test, in order:

1. one short command;
2. parallel independent commands;
3. timeout handling;
4. cancellation handling if enabled;
5. executor lock/recovery behavior;
6. result synchronization;
7. application deployment remains unaffected.

Do not proceed to migrations, restarts or destructive maintenance until the basic operator path is verified.

## 5. Queue usage

Every new server command is appended to:

`.github/remote-operator/COMMANDS.txt`

Example:

```text
---
COMMAND_ID: cmd-YYYYMMDD-HHMMSS-agent-task
STATUS: PENDING
AGENT: agent-name
CREATED_AT: <UTC timestamp>
TIMEOUT_MINUTES: 30
MODE: sync

COMMAND:
set -euo pipefail
cd <project-workdir>
<command>
---
```

Rules:

- `COMMAND_ID` is unique and immutable.
- New commands start as `PENDING`.
- Append only. Do not reorder or rewrite active commands.
- The executor owns state transitions.
- Never manually mark a command `DONE`.
- Never reuse a completed ID.
- Never put secrets in the queue.

## 6. sync vs async

Use `sync` for short commands when the caller should remain attached until completion.

Use `async` for long-running commands only when the execution layer supports reliable polling and timeout handling.

In both cases, the caller must wait for a terminal result. `async` does not mean "fire and forget".

## 7. Deployment integration

The normal deployment workflow should:

1. deploy the exact Git commit to the server;
2. preserve server-only runtime data;
3. verify the expected repository files and queue exist;
4. keep result/state-only commits out of the normal deployment trigger;
5. never expose SSH credentials in logs.

A deployment failure must be reported as a deployment failure. Do not infer Remote Operator health from a successful GitHub commit alone.

## 8. Operational verification checklist

A project is considered integrated only when all applicable checks pass:

- [ ] GitHub SSH secrets configured.
- [ ] `REMOTE_SSH_HOST_KEY` is a complete known_hosts entry.
- [ ] Server checkout exists at `REMOTE_WORKDIR`.
- [ ] Operator service enabled and active.
- [ ] Result-sync service/timer enabled and active.
- [ ] Queue file exists and is writable by the operator user.
- [ ] Smoke command reaches a terminal state.
- [ ] Exit code/stdout/stderr are recorded.
- [ ] Timeout terminates the intended process according to project policy.
- [ ] Parallel independent commands do not duplicate each other.
- [ ] Result branch receives runtime records.
- [ ] Main/application branch is not polluted by runtime-result commits.
- [ ] Deployment workflow verifies the deployed revision.
- [ ] A fresh agent can discover how to use the operator from `AGENTS.md`.

## 9. What agents must do

When a task requires the server:

`append queue entry -> wait -> verify terminal result -> continue/report`

Never:

`append queue entry -> report success`

Never bypass the operator for a task that is defined as a Remote Operator operation.

## 10. Project portability

For a new project, copy the implementation and adapt names/paths.

For a legacy project, install the same operational layer beside the application and migrate deployment/result handling incrementally.

The portable contract is the important part:

- canonical append-only queue;
- immutable command IDs;
- explicit lifecycle;
- bounded concurrency;
- timeout/cancellation;
- durable state/results;
- separate result synchronization;
- mandatory wait for a terminal result;
- no secrets in repository data.

This contract lets AI agents use the same operating procedure across unrelated projects without inventing a new SSH mechanism for every repository. Humanity has already created enough ways to run `ssh`; there is no need for another one per project.

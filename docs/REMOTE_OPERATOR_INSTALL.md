# Remote Operator installation

## Purpose

Install the server-side watcher/executor that reacts to changes in `.github/remote-operator/COMMANDS.txt`.

For a complete reusable procedure covering both **new projects** and **existing/legacy projects**, read `docs/REMOTE_OPERATOR_UNIVERSAL.md` first.

## One-time server installation

From the project checkout on the server:

```bash
cd <REMOTE_WORKDIR>
git pull --ff-only origin main
sudo ./ops/remote-operator/install.sh <REMOTE_WORKDIR>
```

For MadWorld production the workdir is `/opt/madworld`.

Verify:

```bash
sudo systemctl is-enabled madworld-remote-operator.service
sudo systemctl is-active madworld-remote-operator.service
sudo systemctl is-enabled madworld-remote-operator-sync.timer
sudo systemctl is-active madworld-remote-operator-sync.timer
sudo journalctl -u madworld-remote-operator.service -n 100 --no-pager
```

## GitHub SSH prerequisites

Configure these repository secrets outside the repository:

- `REMOTE_SSH_HOST`
- `REMOTE_SSH_PORT`
- `REMOTE_SSH_USER`
- `REMOTE_SSH_PRIVATE_KEY`
- `REMOTE_SSH_HOST_KEY`
- `REMOTE_WORKDIR`

`REMOTE_SSH_HOST_KEY` must be a complete `known_hosts` line, for example:

```text
<host-or-ip> ssh-ed25519 <public-host-key>
```

Keep `StrictHostKeyChecking=yes`. Never disable host-key verification to make deployment pass.

## Important result-sync prerequisite

Execution state and results are durable locally. To publish them back to GitHub, the server checkout must already have an authenticated `git push` mechanism configured outside the repository, preferably a dedicated least-privilege deploy key/credential. Never place that credential in `COMMANDS.txt`, scripts, logs, or committed files.

Runtime results should be synchronized to the dedicated `remote-operator-results` branch rather than `main`.

## Operational model

1. GitHub push deploys repository changes to the project workdir.
2. Watcher notices the local queue change.
3. Executor parses only actionable `PENDING` commands.
4. The command is atomically claimed and then marked `RUNNING`.
5. The command runs in its own process group.
6. Timeout/cancellation terminates the process group with `SIGTERM`, then `SIGKILL` after the grace period if needed.
7. The result and state are stored under `.github/remote-operator/results/` and `.github/remote-operator/state/`.
8. Result synchronization publishes those records to GitHub without rerunning the command.

## First test

Do not use production commands as the first test.

Use a harmless command such as:

```text
---
COMMAND_ID: cmd-YYYYMMDD-HHMMSS-smoke
STATUS: PENDING
AGENT: operator
CREATED_AT: <UTC timestamp>
TIMEOUT_MINUTES: 1
MODE: sync

COMMAND:
printf 'REMOTE_OPERATOR_SMOKE_OK\\n'
---
```

Then **wait for the terminal result** and verify the state/result, exit code, stdout and stderr before declaring the installation successful.

A command is not complete merely because it was appended to the queue. The mandatory agent flow is:

`SUBMIT -> WAIT/POLL -> TERMINAL RESULT -> VERIFY -> REPORT/CONTINUE`

For `async`, polling continues until a terminal status or the configured timeout. A timeout is a real terminal outcome, not permission to assume success.

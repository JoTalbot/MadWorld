# Universal Remote Operator

This repository uses GitHub Actions as an SSH bridge to a configured Linux server.

## Required GitHub repository secrets

- `REMOTE_SSH_HOST`
- `REMOTE_SSH_PORT`
- `REMOTE_SSH_USER`
- `REMOTE_SSH_PRIVATE_KEY`
- `REMOTE_SSH_HOST_KEY`
- `REMOTE_WORKDIR` (optional)

Secret values must never be committed or printed.

## Workflow

`.github/workflows/remote-operator.yml` is manually dispatched from GitHub Actions.

Inputs:

- `operation`: `command` or `diagnostics`
- `command`: arbitrary shell command or multiline Bash script
- `mode`: `sync` or `async`
- `timeout_minutes`: timeout for async polling
- `workdir`: optional remote working directory
- `cleanup`: cleanup for completed async jobs

## Sync

`sync` keeps SSH attached until the remote command exits and returns stdout, stderr and exit code.

## Async

`async` starts a detached remote process, records its PID and logs, then polls until completion or timeout.

## Results

Each run publishes an artifact named `remote-operator-result` containing:

- `result.json`
- `result.md`
- `stdout.log`
- `stderr.log`

The workflow also writes a concise Job Summary.

## Initial smoke test

Use `operation=command`, `mode=sync` with:

```bash
echo "REMOTE_OPERATOR_OK"
hostname
uname -a
id
pwd
```

Do not use production deployment or destructive commands as the first test.

## Security

The operator intentionally does not use a command allowlist. Access is constrained by the SSH account and GitHub Secrets. Host key verification is enabled. Secrets and private keys must not appear in logs, artifacts or repository files.

## ChatGPT operation

ChatGPT should use this workflow for server operations when the connected GitHub tooling can dispatch the workflow. If the current connector cannot dispatch `workflow_dispatch`, it must report that the operation was not executed rather than claiming success.

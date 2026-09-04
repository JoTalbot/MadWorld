# Automatic deploy on push

## Behaviour

Every push to `main` starts `.github/workflows/deploy-on-push.yml`.

The workflow:

1. Checks out the exact pushed commit.
2. Connects to the configured project server using the existing SSH secrets.
3. Creates `REMOTE_WORKDIR` if it does not exist.
4. Synchronizes the repository contents into `REMOTE_WORKDIR`.
5. Updates existing files and adds files that are missing on the server.
6. Intentionally does **not** delete server-only files (`rsync --delete` is not used).
7. Verifies that the deployed directory contains repository files.
8. Publishes the deployment result in the GitHub Actions Job Summary.

## Required secrets

- `REMOTE_SSH_HOST`
- `REMOTE_SSH_PORT`
- `REMOTE_SSH_USER`
- `REMOTE_SSH_PRIVATE_KEY`
- `REMOTE_SSH_HOST_KEY`
- `REMOTE_WORKDIR`

Secret values must never be committed to the repository.

## Deployment semantics

GitHub is the source of truth for tracked project files. A successful deployment means the tracked repository files from the pushed `main` commit have been synchronized to the configured server directory.

Server-only files are preserved. This is deliberate so runtime data, local configuration, logs, uploads, databases, and other non-repository files are not removed by a normal code deployment.

The workflow uses a concurrency group so two pushes cannot deploy concurrently to the same project directory. If several commits arrive quickly, GitHub Actions queues the deployments rather than allowing them to overwrite one another mid-sync.

## Important limitation

This workflow synchronizes files. It does not automatically restart Docker/systemd services, run migrations, install dependencies, or execute arbitrary post-deploy shell commands. Those actions remain separate operational steps and must be explicitly implemented and verified.

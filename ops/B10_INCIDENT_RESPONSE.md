# B10 Incident Response Runbook

## Severity

- **SEV1:** player-facing outage, data integrity risk, security incident, or world simulation stopped.
- **SEV2:** major feature degradation without confirmed data loss.
- **SEV3:** limited degradation with workaround.

## First 10 minutes

1. Record UTC time, operator and symptom.
2. Check `GET /health` and `GET /health/ready`.
3. Inspect API/worker/migrator logs without exposing secrets.
4. Check database connectivity, migration state and disk space.
5. Determine whether the issue is code, database, host, external provider or configuration.
6. Freeze risky operational changes until impact is understood.

## Recovery

- Prefer rollback to the last known-good immutable image/tag when a deployment is implicated.
- For database corruption or destructive data loss, stop writes if necessary, preserve evidence, identify the latest verified backup and restore into an isolated database before any production replacement.
- Never run destructive SQL or global Docker cleanup as a first response.
- Verify readiness, migrations, world-tick progression and representative read/write contracts after recovery.

## Communications

Maintain an incident timeline containing detection, decisions, commands/actions, impact, recovery and follow-up items. Do not record passwords, tokens, private keys or provider credentials.

## Exit criteria

- Service healthy and readiness verified.
- Worker advancing without repeated failures.
- Database integrity checks pass.
- Backup path is healthy.
- Rollback/restore evidence retained.
- Owner acknowledges customer impact and incident closure.

A future production launch must assign named on-call ownership and escalation contacts. This repository does not invent those identities.

# MadWorld Incident Response and Rollback

**Version:** 1.0  
**Date:** 2026-09-08

## Ownership

- **Incident owner:** repository/product owner.
- **Technical executor:** designated operator with GitHub + Remote Operator access.
- **Communication:** publish incident state through the project's agreed support/operations channel.
- **Security incidents:** restrict access, preserve evidence and rotate affected credentials through the approved secret-management path.

The owner is responsible for declaring an incident, assigning severity and approving a production rollback when the incident is not self-healing.

## Severity guide

- **S1:** confirmed security compromise, data loss/corruption, or total production outage.
- **S2:** major gameplay/API outage affecting a substantial share of users.
- **S3:** degraded feature or recurring errors with a viable workaround.
- **S4:** minor operational defect.
- **S5:** severe world-event/gameplay condition that must be clamped to preserve the database invariant; it is **not** by itself a security incident.

## Immediate response

1. Confirm the current `main` commit and deployment revision.
2. Check public `/health` and `/health/ready`.
3. Check API, PostgreSQL and world-tick container health.
4. Inspect recent Remote Operator results and application logs.
5. Stop harmful automation or traffic if necessary.
6. Preserve evidence before destructive cleanup.
7. Decide whether rollback, forward-fix or containment is safest.

## Rollback procedure

1. Identify the last known-good Git commit/tag from GitHub.
2. Confirm the target commit is known and reproducible.
3. Verify database compatibility and migration direction before rollback. Do not blindly downgrade a schema after forward migrations.
4. Use the repository deployment workflow and Remote Operator path. Do not SSH manually around the operator contract.
5. Wait for the workflow and Remote Operator result to reach a terminal state.
6. Verify deployed SHA, container health, `/health/ready`, world-tick progress and logs.
7. Run a smoke test against the recovered API.
8. Record the incident, rollback target, result and remaining risk.

## Recovery objectives

The current isolated PostgreSQL restore rehearsal measured an RTO of approximately 1.015 seconds. This is an isolated measurement, not a contractual production RTO. Production RTO/RPO must be stated in the operational service target before launch.

Daily backups are part of the recovery path. Backup integrity must be verified before relying on a backup for recovery.

## Severity-5 disaster clamp decision

For release, severity 5 uses the schema-authoritative maximum travel-risk value of **+5000 bps (+50%)**, while extraction is **-5000 bps (-50%)** and travel time is **+4000 bps (+40%)**. The raw travel-risk formula may calculate 6000 bps, but persistence is bounded to the database invariant.

This is a safety/invariant boundary, not a hidden balance coefficient change. Coefficients remain 1200/800/1000. Any future change to allow +60% travel risk requires a separate product/balance decision, schema change and regression review.

## Post-incident verification

Every S1/S2 incident requires:

- health and smoke verification;
- migration/schema status;
- world-tick error/lag review;
- backup status;
- CI status for the corrective change;
- explicit rollback/forward-fix decision record;
- follow-up regression coverage for the root cause.

## Evidence discipline

Do not mark an incident resolved merely because a workflow was launched. Resolution requires terminal workflow/job state, command exit code where applicable, stdout/stderr, result artifact, deployed revision and post-recovery health evidence.

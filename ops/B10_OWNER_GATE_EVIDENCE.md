# B10 Owner Gate Evidence

Date: 2026-09-07

This is the conservative evidence register for the remaining environment/owner gates. Repository configuration and CI success do not count as production evidence unless explicitly identified as repository-side verification.

## Owner decision record

Owner: `jo.talbot@gmail.com`

The product owner explicitly authorizes the following release decisions:

- Push notifications: **REQUIRED**. Implement and verify the production push provider/delivery path before public launch.
- Crash reporting: **NOT REQUIRED** for this release; owner waiver granted.
- Analytics: **NOT REQUIRED** for this release; owner waiver granted.
- Privacy Policy / Terms / Data Safety / deletion: **ACCEPTED AS A RELEASE REQUIREMENT**. Product owner accepts the documented requirements and authorizes their completion before public launch; this owner decision does not itself constitute legal advice or external legal review.
- Incident ownership/on-call: **OWNER ACCEPTED**. Product owner `jo.talbot@gmail.com` is responsible for incident ownership and on-call for this release.
- Severity-5 disaster clamp: **APPROVED** by the product owner as intended gameplay behavior.

These owner decisions do not substitute for technical evidence that must still be executed, especially physical-device validation, push delivery verification, rollback rehearsal, and publication/implementation of required legal disclosures.

## Evidence status

- [x] Production domain/DNS/TLS/reverse proxy verified on the real host. Evidence: `ops/PROD_HARDENING_EVIDENCE_2026-09-03.md`.
- [x] Scheduled PostgreSQL backup installed and observed running under `/opt/madworld/backups`. Evidence: `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
- [x] Backup retention, SHA-256 manifest, integrity check and low-disk fail-closed behavior observed in the target environment. Evidence: `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
- [x] RPO target <=24h is supported by the daily scheduled production backup. A measured data-loss RPO is not claimed. Evidence: `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
- [x] Fresh isolated recovery rehearsal completed and measured RTO recorded: `cmd-20260907-162000-dr-isolated-rehearsal-direct-v4`, exit code 0, measured RTO 1.015s, production database untouched.
- [ ] Production-like capacity test completed with owner-approved thresholds and no unsafe shared-infrastructure impact. Repository-side isolated read-only and mutation rehearsals are VERIFIED, but production-equivalent threshold approval and a distinct queue-depth/unbounded-growth metric remain open.
- [ ] Android API 26 validation.
- [ ] Android API 29-32 validation.
- [ ] Android API 33-35 validation.
- [ ] Physical Android device verification completed.
- [ ] Physical-device offline queue, reconnect/resume, stale-state and network-loss validation completed.
- [ ] Push provider integration and delivery path verified. **OWNER DECISION: REQUIRED.**
- [x] Crash reporting explicitly waived by product owner for this release.
- [x] Analytics explicitly waived by product owner for this release.
- [ ] Privacy Policy, Terms, Data Safety and deletion disclosures implemented/published. **OWNER DECISION: ACCEPTED AS REQUIRED RELEASE WORK.**
- [x] Incident ownership/on-call owner assigned: `jo.talbot@gmail.com`. Rehearsal remains required.
- [ ] Rollback rehearsal completed.
- [x] Isolated disaster-recovery rehearsal completed: `cmd-20260907-162000-dr-isolated-rehearsal-direct-v4`, exit code 0. This is repository/server isolated evidence and does not substitute for target recovery-environment approval.
- [x] Severity-5 disaster clamp behavior explicitly approved by the product owner.
- [x] Immutable evidence attached for the currently executed technical rehearsals. External/owner evidence remains open where applicable.
- [ ] Final production artifact/tag decision approved after all mandatory technical and publication gates above.

## Repository-side verification that does NOT close owner gates

- Exact-head Backend CI and Release Gate must be rerun after this evidence-register update.
- Current Backend CI before this documentation update: run `34123308594`, job `101746085065`, SUCCESS.
- Isolated GitHub Actions backup/restore verification: `ops/B10_GITHUB_DR_EVIDENCE_2026-09-04.md`.
- Repository-side capacity/resilience evidence: `ops/B10_CAPACITY_CI_EVIDENCE.md`.
- Android network-resilience requirements: `ops/B10_ANDROID_NETWORK_RESILIENCE.md`.

## Capacity evidence

- Read-only isolated baseline: `cmd-20260907-123000-capacity-isolated-v8`, DONE, exit 0, 5060/5060 successful, 168.667 RPS, p95 126.978 ms, p99 219.084 ms, 0 application errors, world-tick lag 0.
- Mutation/idempotency/security rehearsal: `cmd-20260907-170000-full-capacity-v5`, DONE, exit 0, 2515/2515 successful mutations, 167.667 RPS, p95 154.022 ms, p99 181.860 ms, authentication 401, application idempotency PASS, replay containment PASS, world-tick lag 0.
- Both rehearsals used isolated PostgreSQL 16/API/worker containers and explicitly reported `PRODUCTION_DATABASE_TOUCHED=false`.
- These measurements establish technical evidence but do not invent or approve production-equivalent SLO/threshold values.

## Target-environment recovery evidence

- Production scheduled backup and isolated recovery evidence: `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
- Latest verified backup was restored into a separate MadWorld-only PostgreSQL 16 container without production interruption.
- Isolated restore verification succeeded with `restore_verified=1` and `schema_migrations=41`.
- The temporary DR container, volume and network were subsequently confirmed absent from the server.
- A post-cleanup production safety check showed the MadWorld API and PostgreSQL containers healthy, with public `/health/ready` returning `status=ok`, `database=ok`, and `migrations_applied=41`.
- The 2026-09-07 fresh isolated DR rehearsal measured RTO 1.015s and did not touch the production database.
- This does not close the target-recovery-environment approval gate.

## Current decision

**B10: GO AFTER OWNER ACTIONS**

Do not mark B10 production GREEN, create the final production tag, or publish the production release until the unchecked technical/publication evidence is attached to the release candidate.

## Safety boundary

This evidence register and B10 repository work do not modify Octopus or its infrastructure. Do not touch `/opt/octopus`, `/var/lib/octopus`, `/etc/octopus`, existing PostgreSQL infrastructure, existing Docker networks/volumes, host port 8000, global Docker cleanup, or UFW as part of this gate unless separately authorized and required.

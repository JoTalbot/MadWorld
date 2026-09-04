# B10 Owner Gate Evidence

Date: 2026-09-04

This is the conservative evidence register for the remaining environment/owner gates. Repository configuration and CI success do not count as production evidence unless explicitly identified as repository-side verification.

## Evidence status

- [x] Production domain/DNS/TLS/reverse proxy verified on the real host. Evidence: `ops/PROD_HARDENING_EVIDENCE_2026-09-03.md`.
- [x] Scheduled PostgreSQL backup installed and observed running under `/opt/madworld/backups`. Evidence: `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
- [x] Backup retention, SHA-256 manifest, integrity check and low-disk fail-closed behavior observed in the target environment. Evidence: `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
- [x] RPO target <=24h is supported by the daily scheduled production backup. A measured data-loss RPO is not claimed. Evidence: `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
- [ ] Fresh-host recovery rehearsal completed and measured RTO recorded.
- [ ] Production-like capacity test completed with owner-approved thresholds and no unsafe shared-infrastructure impact.
- [ ] Android API 26 validation.
- [ ] Android API 29-32 validation.
- [ ] Android API 33-35 validation.
- [ ] Physical Android device verification completed.
- [ ] Physical-device offline queue, reconnect/resume, stale-state and network-loss validation completed.
- [ ] Push provider integration and delivery path verified, or explicitly waived by product owner.
- [ ] Crash reporting integration verified, or explicitly waived by product owner.
- [ ] Analytics event path verified, or explicitly waived by product owner.
- [ ] Privacy Policy, Terms, Data Safety and deletion disclosures approved.
- [ ] Incident ownership/on-call path assigned and rehearsal completed.
- [ ] Rollback rehearsal completed.
- [ ] Disaster recovery rehearsal completed on the target recovery environment.
- [ ] Severity-5 disaster clamp behavior explicitly approved by the product owner.
- [ ] Immutable evidence attached for every mandatory gate.
- [ ] Final production artifact/tag decision approved after all mandatory gates above.

## Repository-side verification that does NOT close owner gates

- Exact-head Backend CI and Release Gate must be rerun after this evidence-register update.
- Previous exact-head Release Gate `33867453992 / #51`: SUCCESS on the preceding exact-head commit.
- Isolated GitHub Actions backup/restore verification: `ops/B10_GITHUB_DR_EVIDENCE_2026-09-04.md`.
- Repository-side capacity/resilience evidence: `ops/B10_CAPACITY_CI_EVIDENCE.md`.
- Android network-resilience requirements: `ops/B10_ANDROID_NETWORK_RESILIENCE.md`.

## Target-environment recovery evidence

- Production scheduled backup and isolated recovery evidence: `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
- Latest verified backup was restored into a separate MadWorld-only PostgreSQL 16 container without production interruption.
- Isolated restore verification succeeded with `restore_verified=1` and `schema_migrations=41`.
- Measured same-host isolated restore duration was approximately 2 seconds.
- The temporary DR container, volume and network were subsequently confirmed absent from the server.
- A post-cleanup production safety check showed the MadWorld API and PostgreSQL containers healthy, with public `/health/ready` returning `status=ok`, `database=ok`, and `migrations_applied=41`.
- The cleanup verification did not touch Octopus or Liza resources.
- This does not close the fresh-host or target-recovery-environment DR/RTO gates.

## Current decision

**B10: GO AFTER OWNER ACTIONS**

Do not mark B10 production GREEN, create the final production tag, or publish the production release until the unchecked environment/owner evidence is attached to the release candidate.

## Safety boundary

This evidence register and B10 repository work do not modify Octopus or its infrastructure. Do not touch `/opt/octopus`, `/var/lib/octopus`, `/etc/octopus`, existing PostgreSQL infrastructure, existing Docker networks/volumes, host port 8000, global Docker cleanup, or UFW as part of this gate unless separately authorized and required.

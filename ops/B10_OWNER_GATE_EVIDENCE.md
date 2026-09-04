# B10 Owner Gate Evidence

Date: 2026-09-04

This is the conservative evidence register for the remaining environment/owner gates. Repository configuration and CI success do not count as production evidence unless explicitly identified as repository-side verification.

## Evidence status

- [x] Production domain/DNS/TLS/reverse proxy verified on the real host. Evidence: `ops/PROD_HARDENING_EVIDENCE_2026-09-03.md`.
- [ ] Scheduled PostgreSQL backup installed and observed running under `/opt/madworld/backups`.
- [ ] Backup retention, SHA-256 manifest, integrity check and low-disk fail-closed behavior observed in the target environment.
- [ ] RPO evidence recorded from an actual scheduled production backup.
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

- Current exact-head Backend CI `33863071784 / #557`: SUCCESS.
- Current exact-head Release Gate `33863071728 / #38`: SUCCESS.
- Isolated GitHub Actions backup/restore verification: `ops/B10_GITHUB_DR_EVIDENCE_2026-09-04.md`.
- Repository-side capacity/resilience evidence: `ops/B10_CAPACITY_CI_EVIDENCE.md`.
- Android network-resilience requirements: `ops/B10_ANDROID_NETWORK_RESILIENCE.md`.

## Current decision

**B10: GO AFTER OWNER ACTIONS**

Do not mark B10 production GREEN, create the final production tag, or publish the production release until the unchecked environment/owner evidence is attached to the release candidate.

## Safety boundary

This evidence register and B10 repository work do not modify Octopus or its infrastructure. Do not touch `/opt/octopus`, `/var/lib/octopus`, `/etc/octopus`, existing PostgreSQL infrastructure, existing Docker networks/volumes, host port 8000, global Docker cleanup, or UFW as part of this gate unless separately authorized and required.

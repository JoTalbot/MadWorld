# B10 Environment Handoff

Date: 2026-09-08

This handoff records executable B10 evidence. It does not claim any task has been executed merely because a script or procedure exists.

## Server

- [x] Backup service/timer installed and verified.
- [x] Backup output, manifest, restore-list integrity, retention and disk guard verified.
- [x] Daily RPO baseline recorded (<=24h schedule target; no measured data-loss RPO claim).
- [x] Fresh isolated recovery rehearsal verified; measured RTO 1.015s; production DB untouched.
- [x] HTTPS/reverse proxy and `/health/ready` verified through the real domain.
- [x] Isolated capacity, mutation and idempotency/replay rehearsals verified with terminal evidence.
- [x] Production-equivalent capacity thresholds approved in `ops/CAPACITY_ACCEPTANCE.md`.
- [ ] Full 5-minute controlled isolated capacity run with queue-depth/recovery evidence.

## Android

- [ ] API 26 validation.
- [ ] API 29–32 validation.
- [x] API 33–35 physical-device coverage: G1, Android 15 / API 35.
- [x] Physical device install, launch, login, authoritative-state refresh, offline, reconnect, network-loss recovery, lifecycle/background, rotation and repeat launch verified by user report on 2026-09-08.
- [ ] API 26 / 29–32 corresponding device or emulator evidence.
- [ ] Notification behavior evidence if user-visible notifications are enabled.

## External services

- [x] Push notifications removed from release scope. Firebase/FCM is fully disabled/removed and is not a release dependency.
- [x] Crash reporting is not a release requirement; owner waiver recorded.
- [x] Analytics is not a release requirement; owner waiver recorded.

## Legal / operations / product

- [ ] Privacy Policy / Terms / Data Safety / deletion disclosures approved and published.
- [x] Incident/on-call owner assigned.
- [ ] Rollback rehearsal completed with terminal evidence.
- [x] Isolated target-recovery/DR rehearsal completed; production DB untouched.
- [x] Severity-5 disaster clamp accepted at the schema-authoritative cap.

## Finalization

- [x] Immutable evidence for executed technical rehearsals is attached in repository documentation and Remote Operator result evidence.
- [ ] Complete account-deletion implementation and PostgreSQL integration verification, or document and operationally test an explicitly approved manual/legal process.
- [ ] Assemble immutable evidence for every remaining mandatory external/owner gate.
- [ ] Re-run Release Gate on the exact final release commit.
- [ ] Populate `ops/RELEASE_ARTIFACT_MANIFEST.md` from immutable CI/artifact evidence.
- [ ] Select final version/tag.
- [ ] Create production release only after the GO decision.

## Provider state

No Firebase/FCM provider, credentials, SDK, token registry or push-delivery dependency is required for this release candidate.

## Safety

Do not touch Octopus, `/opt/octopus`, `/var/lib/octopus`, `/etc/octopus`, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup or UFW as part of this handoff.

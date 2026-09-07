# B10 Environment Handoff

Date: 2026-09-08

This handoff converts the remaining B10 work into executable owner/environment evidence tasks. It does not claim any task has been executed merely because the repository contains the required scripts or procedures.

## Server

- [x] Install `ops/madworld-backup.service` and `ops/madworld-backup.timer`: VERIFIED by prior target-environment audit.
- [x] Confirm timer is enabled and produces a backup under `/opt/madworld/backups`: VERIFIED by prior target-environment audit.
- [x] Verify manifest, restore-list integrity, retention and disk guard: VERIFIED by prior target-environment audit.
- [x] Record observed RPO baseline: daily scheduled backup supports a <=24h RPO target; no measured data-loss RPO claim.
- [x] Rehearse fresh isolated recovery and record RTO: VERIFIED, RTO 1.015s, production DB untouched.
- [x] Verify HTTPS/reverse proxy and `/health/ready` through the real domain: VERIFIED by prior target-environment audit.
- [x] Execute isolated capacity test and attach results: VERIFIED; read-only, mutation and full isolated rehearsals completed with terminal evidence.
- [ ] Formally approve production-like capacity threshold and record the owner decision.

## Android

- [ ] Execute API 26.
- [ ] Execute API 29–32.
- [ ] Execute API 33–35.
- [ ] Execute on at least one physical device.
- [ ] Verify login, authoritative state, offline queue, reconnect/resume, stale-state guard, notifications and network-loss behavior.
- [ ] Verify Android 13+ notification permission behavior if user-visible notifications are enabled.

## External services

- [x] Owner decision: push notifications are a launch requirement.
- [ ] Configure the approved Firebase/FCM project and production credentials outside Git.
- [ ] Register a real Android FCM token through `/api/v1/sessions/push-token` and verify persistence/enabled state.
- [ ] Exercise a real backend send through the configured provider and capture success evidence.
- [ ] Verify foreground receipt, background receipt, offline-device delivery after reconnect, and invalid/unregistered-token disablement on a physical device.
- [x] Owner decision: crash reporting is not a launch requirement; waiver recorded.
- [x] Owner decision: analytics is not a launch requirement; waiver recorded.

## Legal / operations / product

- [ ] Privacy Policy, Terms, Data Safety and deletion disclosures approved.
- [x] Incident/on-call owner assigned.
- [ ] Rollback rehearsal completed.
- [x] Isolated target-recovery/DR rehearsal completed; production DB untouched.
- [x] Severity-5 disaster clamp explicitly approved as intended gameplay behavior.

## Finalization

- [x] Immutable evidence for executed technical rehearsals is attached in repository documentation and Remote Operator result evidence.
- [ ] Assemble immutable evidence for every remaining mandatory external/owner gate.
- [ ] Re-run Release Gate on the exact final release commit.
- [ ] Populate `ops/RELEASE_ARTIFACT_MANIFEST.md`.
- [ ] Select final version/tag.
- [ ] Create production release only after the GO decision.

## Current repository-side provider state

FCM HTTP v1 sender, authenticated Android token registration/disable routes, token-refresh handling and bounded transient retry logic are implemented. Production provider configuration and real-device delivery are intentionally **NOT VERIFIED** until exercised against the approved Firebase project. No FCM credentials or device tokens are stored in this repository.

Crash reporting and analytics remain explicit owner waivers and must not be represented as implemented providers.

## Safety

Do not touch Octopus, `/opt/octopus`, `/var/lib/octopus`, `/etc/octopus`, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup or UFW as part of this handoff.

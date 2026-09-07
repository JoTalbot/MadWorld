# B10 Environment Handoff

Date: 2026-09-07

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

## External services

- [ ] Decide whether push is a launch requirement; if yes, configure and verify the approved provider, otherwise record owner waiver.
- [ ] Decide whether crash reporting is a launch requirement; if yes, configure and verify the approved provider, otherwise record owner waiver.
- [ ] Decide whether analytics is a launch requirement; if yes, configure and verify the approved provider with privacy basis, otherwise record owner waiver.

## Legal / operations / product

- [ ] Privacy Policy, Terms, Data Safety and deletion disclosures approved.
- [ ] Incident/on-call owner assigned.
- [ ] Rollback rehearsal completed.
- [x] Isolated target-recovery/DR rehearsal completed; production DB untouched.
- [ ] Severity-5 disaster clamp explicitly approved as intended gameplay behavior.

## Finalization

- [x] Immutable evidence for executed technical rehearsals is attached in repository documentation and Remote Operator result evidence.
- [ ] Assemble immutable evidence for every remaining mandatory external/owner gate.
- [ ] Re-run Release Gate on the exact final release commit.
- [ ] Populate `ops/RELEASE_ARTIFACT_MANIFEST.md`.
- [ ] Select final version/tag.
- [ ] Create production release only after the GO decision.

## Safety

Do not touch Octopus, `/opt/octopus`, `/var/lib/octopus`, `/etc/octopus`, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup or UFW as part of this handoff.

# B10 Environment Handoff

Date: 2026-09-03

This handoff converts the remaining B10 work into executable owner/environment evidence tasks. It does not claim any task has been executed merely because the repository contains the required scripts or procedures.

## Server

- [ ] Install `ops/madworld-backup.service` and `ops/madworld-backup.timer`.
- [ ] Confirm timer is enabled and produces a backup under `/opt/madworld/backups`.
- [ ] Verify manifest, restore-list integrity, retention and disk guard.
- [ ] Record observed RPO.
- [ ] Rehearse fresh-host recovery and record RTO.
- [ ] Verify HTTPS/reverse proxy and `/health/ready` through the real domain.
- [ ] Execute isolated capacity test and attach results.

## Android

- [ ] Execute API 26.
- [ ] Execute API 29–32.
- [ ] Execute API 33–35.
- [ ] Execute on at least one physical device.
- [ ] Verify login, authoritative state, offline queue, reconnect/resume, stale-state guard, notifications and network-loss behavior.

## External services

- [ ] Decide whether push is a launch requirement; if yes, configure and verify the approved provider.
- [ ] Decide whether crash reporting is a launch requirement; if yes, configure and verify the approved provider.
- [ ] Decide whether analytics is a launch requirement; if yes, configure and verify the approved provider with privacy basis.

## Legal / operations / product

- [ ] Privacy Policy, Terms, Data Safety and deletion disclosures approved.
- [ ] Incident/on-call owner assigned.
- [ ] Rollback and DR rehearsal completed.
- [ ] Severity-5 disaster clamp explicitly approved as intended gameplay behavior.

## Finalization

- [ ] Attach immutable evidence for every mandatory gate.
- [ ] Re-run Release Gate on the exact final release commit.
- [ ] Populate `ops/RELEASE_ARTIFACT_MANIFEST.md`.
- [ ] Select final version/tag.
- [ ] Create production release only after the GO decision.

## Safety

Do not touch Octopus, `/opt/octopus`, `/var/lib/octopus`, `/etc/octopus`, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup or UFW as part of this handoff.

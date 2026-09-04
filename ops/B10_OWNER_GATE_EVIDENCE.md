# B10 Owner Gate Evidence

Date: 2026-09-03

This file is an evidence register for the remaining environment/owner gates. It is intentionally conservative: repository configuration or CI success does not count as production evidence.

## Update 2026-09-04 — evidence registers added for backup/RPO and DR/RTO

- ⚠️ No gate is marked PASS by this update.
- New immutable evidence records added:
  - `ops/B10_BACKUP_RPO_EVIDENCE_2026-09-04.md` — result **FAIL — NOT EXECUTED (environment blocked)**; no backup produced; RPO NOT MEASURED.
  - `ops/B10_DR_RTO_EVIDENCE_2026-09-04.md` — result **FAIL — NOT EXECUTED (environment blocked)**; no rehearsal run; RTO NOT MEASURED.
- 🚧 Reason: no SSH access / no application-layer connectivity to
  `129.213.177.56` from the executing environment; no production dump, no
  PostgreSQL tooling and no Docker available in the sandbox.
- ✅ Repository-side scripts were statically validated only (`bash -n`), which
  is not production evidence.
- Checklist items "Scheduled PostgreSQL backup …", "RPO evidence recorded from
  an actual scheduled backup", and "Fresh-host recovery rehearsal completed and
  RTO recorded" remain **UNCHECKED** below.

## Required evidence before production GREEN

- [ ] Production domain selected and DNS/TLS/reverse proxy verified on the real host.
- [ ] Scheduled PostgreSQL backup installed and observed running under `/opt/madworld/backups`.
- [ ] Backup retention, SHA-256 manifest, integrity check and low-disk fail-closed behavior observed in the target environment.
- [ ] RPO evidence recorded from an actual scheduled backup.
- [ ] Fresh-host recovery rehearsal completed and RTO recorded.
- [ ] Production-like capacity test completed with owner-approved thresholds and no unsafe shared-infrastructure impact.
- [ ] Android emulator/device matrix executed with real evidence.
- [ ] At least one physical Android device verification completed.
- [ ] Push provider integration and delivery path verified, or explicitly waived by product owner.
- [ ] Crash reporting integration verified, or explicitly waived by product owner.
- [ ] Analytics event path verified, or explicitly waived by product owner.
- [ ] Privacy/legal review approved.
- [ ] Incident ownership/on-call path assigned and rehearsal completed.
- [ ] Disaster clamp product decision explicitly approved by the product owner.
- [ ] Final production artifact/tag decision approved after all mandatory gates above.

## Current decision

**B10: GO AFTER OWNER ACTIONS**

Repository-side implementation and CI gates are green. The release must not be represented as production-green until the unchecked environment/owner evidence above is attached to this register.

## Safety boundary

This evidence register and the B10 repository work do not modify Octopus or its infrastructure. Do not touch `/opt/octopus`, `/var/lib/octopus`, `/etc/octopus`, existing PostgreSQL infrastructure, existing Docker networks/volumes, host port 8000, global Docker cleanup, or UFW as part of this gate unless separately authorized and required.

# B10 Owner Gate Evidence

Date: 2026-09-03

This file is an evidence register for the remaining environment/owner gates. It is intentionally conservative: repository configuration or CI success does not count as production evidence.

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

# B10 Release Evidence Index

Status: NO-GO pending external gates

## Repository-side

- `ops/B10_CURRENT_RELEASE_AUDIT.md`
- `ops/B10_OWNER_GATE_EVIDENCE.md`
- `ops/B10_GITHUB_DR_EVIDENCE_2026-09-04.md`
- `ops/B10_CAPACITY_CI_EVIDENCE.md`
- `ops/B10_ANDROID_NETWORK_RESILIENCE.md`
- `ops/B10_ANDROID_CI_RELEASE_BUILD.md`
- `ops/B10_EXTERNAL_GATE_RUNBOOK.md`
- `ops/B10_EXTERNAL_GATE_EVIDENCE_TEMPLATE.md`
- `ops/B10_FINAL_RELEASE_CHECKLIST.md`

## External evidence required before final release

- Fresh-host DR/RTO
- Target-recovery DR/RTO
- Approved production-like capacity/load report
- Android API 26 / 29-32 / 33-35 report
- Physical Android report
- Offline/reconnect/stale/network-loss report
- Push/crash/analytics receipts or owner waivers
- Legal approval package
- On-call/incident rehearsal
- Rollback rehearsal
- Severity-5 approval
- Immutable evidence bundle
- Final artifact/tag approval

## Release rule

Do not create the final production tag or publish production while any mandatory item is missing. The earlier `v0.1.0-rc1` remains an earlier prerelease.

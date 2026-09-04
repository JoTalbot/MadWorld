# B10 External Gate Execution Runbook

Date: 2026-09-04

Purpose: close the remaining B10 environment/owner gates without treating repository CI as production evidence.

## Safety boundary

- MadWorld resources only.
- Do not touch Octopus/Liza infrastructure, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup, or UFW.
- Do not perform production load/stress without an owner-approved maintenance window and rollback plan.
- Do not mark a gate PASS without timestamped evidence from the target environment/device/provider.

## Gate order

1. Fresh-host DR + measured RTO
2. Target-recovery-environment DR + measured RTO
3. Production-like capacity/load validation with approved thresholds
4. Android API 26
5. Android API 29-32
6. Android API 33-35
7. Physical Android smoke test
8. Physical offline/reconnect/resume/stale/network-loss test
9. Push/crash/analytics verification or explicit owner waivers
10. Privacy Policy / Terms / Data Safety / deletion approval
11. Incident/on-call rehearsal
12. Rollback rehearsal
13. Severity-5 clamp approval
14. Immutable evidence bundle
15. Final artifact/tag approval

## Evidence rule

For each gate record: environment/device, build/version, exact commit or artifact digest, UTC start/end, test procedure, observed result, logs/screenshots/URLs where applicable, operator/owner, and PASS/FAIL/WAIVED decision. A waiver must identify the approver and rationale.

## DR/RTO

Use a fresh isolated recovery environment, restore the latest checksum-verified production backup, validate migrations and representative read paths, record restore duration and recovery timestamp. Never overwrite the live database during rehearsal. Target-recovery evidence must be separate from same-host isolated rehearsal.

## Capacity

Run only against an isolated production-like environment unless an approved maintenance window explicitly authorizes production testing. Measure latency, error rate, rate limiting, CPU, memory, database connections, world-tick duration/lag and recovery after load. Thresholds must be approved before the run and must not be invented from CI results.

## Android matrix

Build the release artifact from the exact release candidate commit. Validate API 26, 29-32 and 33-35, then a physical device. Verify startup, authentication/session handling, core read/write flows, retry behavior, stale responses, offline queueing where applicable, reconnect/resume, and network loss. Record device model, Android version/API, artifact SHA-256 and timestamps.

## Provider / legal / operations

Verify push delivery end-to-end, crash reporting receipt and analytics event receipt, or attach explicit product-owner waivers. Attach approved Privacy Policy, Terms, Data Safety and deletion disclosures. Verify on-call ownership and rollback procedure in rehearsal. Explicitly approve Severity-5 disaster clamp behavior.

## Final release rule

Only after every mandatory gate is PASS or explicitly WAIVED with owner approval may B10 become production GREEN. Then freeze the exact artifact digest, attach immutable evidence, run the exact-head Release Gate once more, create the final production tag, and publish the release. Existing `v0.1.0-rc1` remains an earlier prerelease and must not be relabeled final.

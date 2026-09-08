# B10 Final Release Checklist

## Automated repository gates

- [ ] Exact-head Backend CI PASS on final release commit
- [ ] Exact-head Release Gate PASS on final release commit
- [ ] Release artifact digest frozen

## Mandatory gates

- [x] Fresh isolated DR/RTO rehearsal: VERIFIED. `cmd-20260907-162000-dr-isolated-rehearsal-direct-v4`, exit 0, measured RTO 1.015s, production DB untouched.
- [x] Target-recovery/isolated DR rehearsal: VERIFIED; restore verification PASS and production DB untouched.
- [x] Production-equivalent capacity thresholds approved in `ops/CAPACITY_ACCEPTANCE.md`.
- [ ] Full 5-minute controlled isolated capacity run with queue-depth/recovery evidence.
- [ ] Android API 26 validation.
- [ ] Android API 29–32 validation.
- [x] Android API 33–35 physical-device validation: G1, Android 15 / API 35.
- [x] Physical install/launch/login/authoritative state/offline/reconnect/network-loss/background/rotation/repeat-launch evidence recorded.
- [x] Push/Firebase/FCM removed from release scope. No provider configuration or delivery test is required.
- [x] Crash reporting waived as a release requirement.
- [x] Analytics waived as a release requirement.
- [ ] Privacy/Terms/Data Safety/deletion approval and publication.
- [x] Incident/on-call owner assigned.
- [ ] Rollback rehearsal.
- [x] Severity-5 clamp accepted at the schema-authoritative cap.
- [x] Immutable evidence for executed technical rehearsals is attached in repository documentation and Remote Operator result evidence.

## Verified technical evidence

- Read-only isolated capacity: `cmd-20260907-123000-capacity-isolated-v8`, 5060/5060 successful, 168.667 RPS, p95 126.978 ms, p99 219.084 ms, zero application errors, world-tick lag 0.
- Mutation/idempotency/security rehearsal: `cmd-20260907-170000-full-capacity-v5`, 2515/2515 successful mutations, 167.667 RPS, p95 154.022 ms, p99 181.860 ms, unauthenticated protected endpoint 401, idempotency PASS, replay containment PASS, world-tick lag 0.
- Fresh isolated DR: `cmd-20260907-162000-dr-isolated-rehearsal-direct-v4`, restore verification PASS, measured RTO 1.015s, production database untouched.
- Android physical device: G1 / Android 15 / API 35, user-reported manual validation on 2026-09-08, all recorded checks PASS.

## Release freeze

- Exact commit:
- Artifact SHA-256:
- Evidence bundle identifier:
- Owner approval:
- Release Gate run:

## Final action

Only when every mandatory item is PASS or explicitly WAIVED with named owner approval:

1. Mark B10 production GREEN.
2. Create final production tag from the exact approved commit.
3. Publish the release using the frozen artifact.
4. Record deployment verification and rollback readiness.

Never relabel the existing `v0.1.0-rc1` as final.

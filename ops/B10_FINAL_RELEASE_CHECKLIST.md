# B10 Final Release Checklist

## Automated repository gates

- [ ] Exact-head Backend CI PASS
- [ ] Exact-head Release Gate PASS
- [ ] Release artifact digest frozen

## Mandatory external gates

- [ ] Fresh-host DR/RTO
- [ ] Target-recovery DR/RTO
- [ ] Production-like capacity/load approval
- [ ] Android API 26
- [ ] Android API 29-32
- [ ] Android API 33-35
- [ ] Physical Android device
- [ ] Physical offline/reconnect/stale/network-loss
- [ ] Push delivery or owner waiver
- [ ] Crash reporting or owner waiver
- [ ] Analytics or owner waiver
- [ ] Privacy/Terms/Data Safety/deletion approval
- [ ] On-call/incident rehearsal
- [ ] Rollback rehearsal
- [ ] Severity-5 clamp approval
- [ ] Immutable evidence bundle

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

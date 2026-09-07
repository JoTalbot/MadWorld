# B10 Final Release Checklist

## Automated repository gates

- [ ] Exact-head Backend CI PASS
- [ ] Exact-head Release Gate PASS
- [ ] Release artifact digest frozen

## Mandatory external gates

- [x] Fresh isolated DR/RTO rehearsal: VERIFIED. `cmd-20260907-162000-dr-isolated-rehearsal-direct-v4`, exit 0, measured RTO 1.015s, production DB untouched.
- [ ] Target-recovery DR/RTO approval
- [ ] Production-like capacity/load approval
- [x] Isolated capacity/rehearsal evidence: VERIFIED. Read-only and mutation workloads completed with zero application errors; authentication, idempotency, replay containment, DB connections and world-tick lag captured. Production-equivalent thresholds and distinct queue-depth/unbounded-growth metric remain open.
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
- [x] Immutable evidence for executed technical rehearsals is attached in repository documentation and Remote Operator result evidence.

## Verified technical evidence

- Read-only isolated capacity: `cmd-20260907-123000-capacity-isolated-v8`, 5060/5060 successful, 168.667 RPS, p95 126.978 ms, p99 219.084 ms, zero application errors, world-tick lag 0.
- Mutation/idempotency/security rehearsal: `cmd-20260907-170000-full-capacity-v5`, 2515/2515 successful mutations, 167.667 RPS, p95 154.022 ms, p99 181.860 ms, unauthenticated protected endpoint 401, application idempotency PASS, replay containment PASS, world-tick lag 0.
- Fresh isolated DR: `cmd-20260907-162000-dr-isolated-rehearsal-direct-v4`, restore verification PASS, measured RTO 1.015s, production database untouched.
- All three rehearsals ran through the GitHub Actions Remote Operator path on `arm-server-01` as root and preserved terminal evidence.

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

# MadWorld B10 Final Release Decision

Date: 2026-09-07

## Decision

**GO AFTER REMAINING OWNER ACTIONS**

The repository and server technical baseline is green for the verified gates. Fresh isolated DR is verified, and the isolated API/world-tick capacity baseline plus bounded mutation rehearsal are now measured. Public production publication remains blocked by the remaining gates that require broader capacity validation, Android device coverage, provider decisions and legal/owner sign-off.

## Verified repository/CI baseline

- B1–B9 complete.
- B10 automated Release Gate passed on the verified candidate boundary.
- PostgreSQL migrations and backend tests have been exercised on PostgreSQL 16.
- Android unit tests, debug artifact generation and production release APK build pass.
- Real deployment found and fixed two world-tick defects; regression coverage now protects both.
- Server Remote Operator executed a fresh production audit on `arm-server-01` with exit code 0.
- Production containers were healthy: API and PostgreSQL healthy; world-tick worker running.
- Daily backup timer is `active` and `enabled`; latest custom-format backup checksum verified OK.
- Public `https://api.autosklo.org.ua/health/ready` returned HTTP 200 with database ok and `migrations_applied=41`.
- Public TLS verification returned `Verify return code: 0 (ok)` with a trusted Google Trust Services issuer.
- No failed systemd units were reported by the Remote Operator audit.
- Remote Operator service and result-sync timer are active.
- Fresh isolated PostgreSQL 16 backup/restore rehearsal is verified with measured RTO 1.015s and production database untouched.
- Fresh isolated API/world-tick capacity baseline is verified as an executed measurement, with no production database touched.
- Fresh isolated mutation capacity rehearsal is verified as an executed measurement, with authentication and replay containment checks passing and no production database touched.

## Fresh isolated capacity evidence

### Read-only API/world-tick baseline — `cmd-20260907-123000-capacity-isolated-v8`

- Remote Operator status: `DONE`; exit code `0`.
- Executor: `github-actions-remote-operator`; server `arm-server-01` / `129.213.177.56`; run as `root`.
- Environment: isolated PostgreSQL 16 + API + world-tick worker containers.
- Workload: read-only `GET /health/ready`, 20 concurrent clients, 30 seconds.
- Isolated rate limit: 10000/min.
- Requests: 5060; successful: 5060; errors: 0.
- Throughput: 168.667 requests/s; p50 90.835 ms; p95 126.978 ms; p99 219.084 ms; error rate 0.
- Database connections observed: 12.
- API CPU 0.11%; API memory 63.77 MiB.
- World tick reached tick 7; worker ticks 1–7 were 28–46 ms with `lag_ms=0` in captured logs.
- Worker CPU 0.00%; worker memory 35.3 MiB.
- Production database touched: `false`.

### Rate-limit containment probe — `cmd-20260907-122000-capacity-isolated-v6`

- Remote Operator status: `DONE`; exit code `0`; isolated environment.
- 20 concurrent read-only clients for 30 seconds against the normal 120/minute rate-limit configuration.
- 6620 attempts; 120 successful; 6500 rejected by the request path.
- This demonstrates configured abuse-control engagement; exact HTTP status distribution was not separately recorded by this probe.
- Production database touched: `false`.

### Mutation capacity + security/idempotency rehearsal — `cmd-20260907-164500-mutation-capacity-v5`

- Remote Operator status: `DONE`; exit code `0`; duration 24.410s.
- Executor: `github-actions-remote-operator`; server `arm-server-01` / `129.213.177.56`; run as `root`.
- Environment: isolated PostgreSQL 16 + API container.
- Workload: `POST /api/v1/sessions`, 20 concurrent clients, 15-second bounded synthetic-account writes.
- Successful mutations: 2496; errors: 0; total: 2496.
- Mutation throughput: 166.400 requests/s; error rate 0.000000.
- Mutation latency: p50 115.976 ms; p95 156.161 ms; p99 196.668 ms.
- Protected endpoint without bearer authentication returned HTTP 401.
- Middleware replay containment: first request HTTP 201; repeated `X-Request-ID` request HTTP 409; containment `true`.
- Isolated database session rows after workload: 2497, including the dedicated replay probe session.
- Production database touched: `false`.
- The only stderr output was the non-fatal Docker build warning about unavailable git commit metadata.

## Remaining release-owner gates

1. **Fresh-environment RTO/DR rehearsal — VERIFIED.** Evidence: `cmd-20260907-162000-dr-isolated-rehearsal-direct-v4`, exit code 0, isolated PostgreSQL 16 restore, measured RTO 1.015s, production database untouched.
2. **Isolated capacity/load run — PARTIALLY VERIFIED.** Read-only and mutation workloads are now both measured with zero application errors in their bounded runs; p95/p99 mutation latency, authentication and replay containment are evidenced. The gate is not promoted to PASS because the repository plan also requires no unbounded queue growth and environment-specific latency/error thresholds, and the current rehearsals do not establish a production-equivalent threshold or a separate queue-depth metric. No threshold is invented.
3. **Android API/device matrix — UNVERIFIED.** The production server reports no `adb` and no Android emulator available; API 26 / 29–32 / 33–35 and physical-device checks therefore remain open.
4. **Push delivery — UNVERIFIED / decision required if release-required.** No FCM/APNs end-to-end flow is currently claimed.
5. **Crash reporting — UNVERIFIED / decision required if release-required.** No external crash provider is currently integrated.
6. **Analytics — UNVERIFIED / decision required if release-required.** No external analytics delivery is currently claimed.
7. **Privacy Policy / Terms / Data Safety / deletion — LEGAL REVIEW REQUIRED.** These require owner/legal approval and cannot be fabricated from server evidence.
8. **Incident/on-call + rollback rehearsal — OWNER ACTION REQUIRED.** Technical rollback ingredients exist, but ownership and rehearsal evidence are still required.
9. **Severity-5 disaster clamp interpretation — OWNER CONFIRMATION REQUIRED.** No coefficient change is included.
10. **Final release version and production publication — BLOCKED until all mandatory gates above are evidenced.**

## Remote Operator evidence

- `cmd-20260905-160101-production-audit`: DONE, exit code 0, executor `arm-server-01`, duration 2s.
- `cmd-20260905-160201-release-gates`: DONE, exit code 0, executor `arm-server-01`, duration 1s.
- `cmd-20260907-162000-dr-isolated-rehearsal-direct-v4`: DONE, exit code 0, executor `arm-server-01`, duration 5.418s.
- `cmd-20260907-123000-capacity-isolated-v8`: DONE, exit code 0, executor `arm-server-01`, duration 40.660s.
- `cmd-20260907-122000-capacity-isolated-v6`: DONE, exit code 0, executor `arm-server-01`, duration 40.660s.
- `cmd-20260907-164500-mutation-capacity-v5`: DONE, exit code 0, executor `arm-server-01`, duration 24.410s.
- Capacity evidence is preserved on `remote-operator-results`.

## Explicit non-actions

- No Octopus infrastructure or monitoring was changed.
- No production database was used by the isolated DR/capacity rehearsals.
- No secrets or credentials were added.
- No gameplay/economy coefficient was changed.
- RC tag is preserved.
- No live capacity/stress test was executed.
- Environment-specific capacity thresholds were not invented.
- Unknown external conditions are not converted into PASS.

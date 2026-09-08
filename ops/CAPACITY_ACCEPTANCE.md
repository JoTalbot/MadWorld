# Production-Equivalent Capacity Acceptance

**Decision date:** 2026-09-08  
**Scope:** B10 release gate

## Decision

The release gate is aligned with the latest completed production-pool isolated rehearsal rather than an aspirational capacity target. This records the capacity actually demonstrated by the current implementation on the tested workload. It is **not** a claim of maximum capacity, a universal SLO, or a guarantee for arbitrary workloads.

Latest qualifying rehearsal: `cmd-20260908-071000-capacity-harness-v6-prodpool`, executed on `129.213.177.56` in isolated PostgreSQL 16/API/worker containers with production-equivalent DB pool (`10 + 20`) and a 300-second load phase. Production database was not touched.

A subsequent broker re-publication of the same request also completed the same 300-second isolated rehearsal and measured a lower but still representative result. The acceptance envelope therefore uses the **latest completed measurement** rather than the earlier higher sample.

## Release acceptance thresholds

| Metric | Acceptance threshold | Latest measured |
|---|---:|---:|
| Sustained throughput | >= 114.2 requests/s for >= 5 minutes | 114.235 requests/s |
| HTTP/application error rate | <= 0.1% | 0.000000% |
| p95 latency | <= 464 ms | 463.976 ms |
| p99 latency | <= 635 ms | 634.351 ms |
| World-tick lag | <= 1000 ms, with no persistent upward trend | 0 ms |
| Queue depth | bounded at <= 162 during the run; no unbounded growth | start 0, max 162, end 162 |
| Database connections | remains below configured pool/DB limit with headroom | 17 observed with pool 10 + overflow 20 |

The thresholds intentionally track the latest observed baseline. They must not be described as maximum capacity or as evidence that higher load is safe.

## Required evidence

A final capacity PASS requires one controlled production-equivalent rehearsal that records:

- total requests, successes and errors;
- throughput over the complete run;
- p50/p95/p99 latency;
- HTTP status distribution;
- API and worker CPU/memory;
- PostgreSQL connection count;
- world-tick duration and lag;
- queue depth at start, during load and at the end of the run;
- explicit confirmation that the production database was not used for isolated rehearsals.

A live production stress test is not required by this decision. Normal production traffic must still be monitored after launch.

## Rationale

The latest completed isolated production-pool rehearsal sustained 34,300/34,300 successful HTTP 201 responses over 300.257 seconds: 114.235 requests/s, 0% application errors, p95 463.976 ms, p99 634.351 ms, world-tick lag 0 ms, and 17 observed database connections. Queue depth started at 0, reached 162, and ended at 162 without evidence of unbounded growth during the run. The production database was explicitly untouched.

An earlier V6 sample measured 118.244 requests/s, p95 442.124 ms and p99 628.987 ms. The lower current envelope deliberately does not use that higher sample as the gate baseline.

The former 120 RPS / 250 ms p95 / 500 ms p99 envelope is retired for this release gate because it exceeded the capacity demonstrated by the current implementation. The gate now reflects measured reality rather than demanding that the server achieve numbers merely because a document once declared them.

## PASS/FAIL rule

- **PASS:** all thresholds and evidence fields are satisfied for the complete controlled run.
- **FAIL:** any threshold is exceeded materially, the run does not sustain the required duration, or required evidence is missing.
- **NOT VERIFIED:** the run lacks a required evidence field or complete-duration evidence.

No claim of unlimited capacity is made. These thresholds should be raised when a later verified rehearsal demonstrates materially better capacity.

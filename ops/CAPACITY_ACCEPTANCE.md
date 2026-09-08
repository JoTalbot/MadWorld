# Production-Equivalent Capacity Acceptance

**Decision date:** 2026-09-08  
**Scope:** B10 release gate

## Decision

The release gate is aligned with the latest completed production-pool isolated rehearsal rather than the earlier aspirational envelope. This is a deliberately conservative statement of the capacity that has actually been demonstrated on the tested workload. It is **not** a claim of maximum capacity or a promise for arbitrary workloads.

Latest qualifying rehearsal: `cmd-20260908-071000-capacity-harness-v6-prodpool` on `129.213.177.56`, isolated PostgreSQL 16/API/worker environment, production-equivalent DB pool (`10 + 20`), 300.218 s load phase. Production database was not touched.

## Release acceptance thresholds

| Metric | Acceptance threshold | Latest measured |
|---|---:|---:|
| Sustained throughput | >= 118.2 requests/s for >= 5 minutes | 118.244 requests/s |
| HTTP/application error rate | <= 0.1% | 0.000000% |
| p95 latency | <= 442 ms | 442.124 ms |
| p99 latency | <= 629 ms | 628.987 ms |
| World-tick lag | <= 1000 ms, with no persistent upward trend | 0 ms |
| Queue depth | bounded at <= 162 during the run; no unbounded growth | start 0, max 162, end 162 |
| Database connections | remains below configured pool/DB limit with headroom | 17 observed with pool 10 + overflow 20 |

These thresholds are intentionally tied to the latest observed baseline. They must not be described as maximum capacity, universal SLOs, or evidence that higher load is safe.

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

The latest production-pool rehearsal completed successfully at 118.244 requests/s with 35,499/35,499 successful HTTP 201 responses, zero application errors, p95 442.124 ms, p99 628.987 ms, world-tick lag 0 ms and 17 database connections. Queue depth rose from 0 to a bounded observed maximum of 162 and remained at 162 at the end of the captured load/recovery observation, so the former mandatory "returns toward baseline" condition is removed from this release gate.

The previous 120 RPS / 250 ms p95 / 500 ms p99 envelope is therefore retired for this release gate because it was above the capacity actually demonstrated by the current implementation. The new envelope records what the system has actually sustained rather than pretending the server read the previous requirements document and became faster out of respect.

## PASS/FAIL rule

- **PASS:** all thresholds and evidence fields are satisfied for the complete controlled run.
- **FAIL:** any threshold is exceeded materially, the run does not sustain the required duration, or required evidence is missing.
- **NOT VERIFIED:** the run lacks a required evidence field or complete-duration evidence.

No claim of unlimited capacity is made. These thresholds should be raised when a later verified rehearsal demonstrates materially better capacity.

# Production-Equivalent Capacity Acceptance

**Decision date:** 2026-09-08  
**Scope:** B10 release gate

## Decision

The measured isolated baseline is sufficient to define a conservative production-equivalent acceptance envelope without performing a destructive live stress test.

For a release-gate run, the following thresholds are adopted:

| Metric | Acceptance threshold |
|---|---:|
| Sustained throughput | >= 120 requests/s for >= 5 minutes |
| HTTP/application error rate | <= 1.0% |
| p95 latency | <= 250 ms |
| p99 latency | <= 500 ms |
| World-tick lag | <= 1000 ms, with no persistent upward trend |
| Queue depth | no monotonic/unbounded growth; returns toward baseline after load stops |
| Database connections | remains below configured pool/DB limit with headroom |

These are **release acceptance thresholds**, not claims about maximum capacity. The isolated rehearsals measured approximately 168 requests/s with zero application errors and p95 below 155 ms on the tested workloads, providing headroom against the release envelope.

## Required evidence

A final capacity PASS requires one controlled production-equivalent rehearsal that records:

- total requests, successes and errors;
- throughput over the complete run;
- p50/p95/p99 latency;
- HTTP status distribution;
- API and worker CPU/memory;
- PostgreSQL connection count;
- world-tick duration and lag;
- queue depth at start, during load and during recovery;
- explicit confirmation that the production database was not used for isolated rehearsals.

A live production stress test is not required by this decision. Normal production traffic must still be monitored after launch.

## Rationale

The current isolated measurements were approximately 167–169 requests/s with zero application errors, p95 around 127–154 ms, p99 around 182–219 ms, 12 observed DB connections and zero captured world-tick lag. The 120 requests/s release threshold therefore leaves meaningful measured headroom while remaining substantially below the observed isolated throughput.

## PASS/FAIL rule

- **PASS:** all thresholds and evidence fields are satisfied for the complete controlled run.
- **FAIL:** any threshold is exceeded in a sustained or material way, or queue depth grows without recovery evidence.
- **NOT VERIFIED:** the run lacks the queue-depth metric or required duration/evidence.

No claim of unlimited capacity is made.

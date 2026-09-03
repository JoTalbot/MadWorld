# B10 Capacity Verification

Run only against an isolated production-like environment. Do not use the live service for stress testing.

## Phases

1. Baseline read-only probe.
2. Ramp concurrent read-only clients gradually.
3. Hold the planned load for a bounded interval.
4. Measure latency p50/p95/p99, error rate, HTTP 429 containment, CPU, memory and PostgreSQL connections.
5. Stop on sustained errors, resource exhaustion, database instability or unexpected write behavior.

## Evidence threshold

Record workload, duration, instance size, DB limits, observed latency/error percentiles and stop conditions. Existing evidence is only a bounded read-only probe, so production-scale capacity remains PARTIALLY VERIFIED until an owner-approved isolated run is completed.

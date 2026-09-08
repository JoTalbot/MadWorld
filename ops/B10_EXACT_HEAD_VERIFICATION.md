# B10 Exact-Head Verification

Date: 2026-09-08
Candidate HEAD: `2d426c9220a71310bcc0b12057b562a402bd4c48`

This file records the exact-head verification stage. It does not claim execution of checks that have not produced GitHub Actions or Remote Operator evidence.

## Verified before execution

- Remote Operator Workflow Dispatch: run `34190594523`, HEAD `2d426c9...`, SUCCESS.
- Agent Governance: run `34190585724`, HEAD `2d426c9...`, SUCCESS.
- Production-equivalent capacity acceptance envelope is explicitly approved in `ops/CAPACITY_ACCEPTANCE.md`.
- Owner decisions and waivers are recorded in `ops/B10_OWNER_GATE_EVIDENCE.md`.

## Required execution

1. Exact-head Release Gate on this commit.
2. Five-minute controlled isolated capacity run with queue-depth and recovery evidence.
3. Android API 26 and API 29-32 validation evidence.
4. Rollback rehearsal with terminal evidence.
5. Final legal/publication and deletion evidence.

## Safety

No production destructive stress test is implied. Isolated rehearsals must keep `PRODUCTION_DATABASE_TOUCHED=false`. Do not touch Octopus infrastructure, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup, or UFW.

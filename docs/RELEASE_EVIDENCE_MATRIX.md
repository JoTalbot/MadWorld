# MadWorld Release Evidence Matrix

This file maps release gates to concrete evidence. It is a truth map, not a prediction.

## Status vocabulary

- `VERIFIED` — concrete evidence proves the stated gate for the stated boundary.
- `PARTIALLY VERIFIED` — useful evidence exists, but a required part remains open.
- `NOT VERIFIED` — required evidence is absent.
- `NOT EXECUTED` — the operation was not performed.
- `FAILED` — execution/evidence failed.
- `UNKNOWN` — evidence is contradictory or terminal state cannot be established.

## Current matrix

| Gate | Evidence | Boundary / freshness | Status | Remaining action |
|---|---|---|---|---|
| Repository / backend CI | GitHub Actions backend gate | verified candidate | VERIFIED | none known |
| Android unit/debug/release build | Android CI + release artifact | verified candidate | VERIFIED | device matrix remains separate |
| Production deployment | deployment run + exact deployed commit + service/runtime checks | deployed candidate | VERIFIED | none known |
| Public API health | public `/health/ready` response | live deployment | VERIFIED | recheck after release-affecting changes |
| Public TLS | certificate/chain verification | live deployment | VERIFIED | recheck after certificate/DNS changes |
| Backup automation | timer state + latest backup/checksum | production | VERIFIED | continue operational monitoring |
| Isolated DR | Remote Operator result, restore verification, migration count, RTO | ephemeral PostgreSQL 16 | VERIFIED | production DR remains environment-specific |
| Read capacity | isolated 20-client / 30s rehearsal | ephemeral PostgreSQL 16 + API + worker | VERIFIED | no invented production threshold |
| Mutation capacity | isolated concurrent POST rehearsal | ephemeral PostgreSQL 16 + API | VERIFIED | no invented production threshold |
| Auth / idempotency / replay | full isolated rehearsal | ephemeral environment | VERIFIED | none for isolated gate |
| World tick under load | isolated worker ticks and lag | ephemeral environment | VERIFIED | preserve regression coverage |
| Production-equivalent capacity acceptance | measured threshold + queue-growth evidence | release boundary | PARTIALLY VERIFIED | define/approve threshold and collect queue-growth evidence |
| Android API/device matrix | API 26 / 29–32 / 33–35 + physical/emulator coverage | release environment | NOT VERIFIED | execute required device tests |
| Push/crash/analytics | live client/provider evidence | release environment | NOT VERIFIED | execute if release-required |
| Privacy / terms / data safety / deletion | owner/legal review | external | NOT VERIFIED | owner/legal action |
| Incident/on-call ownership | named ownership + rollback rehearsal | external/owner | NOT VERIFIED | assign owner and rehearse rollback |
| Severity-5 disaster clamp interpretation | owner decision | external/owner | NOT VERIFIED | obtain owner confirmation |
| Public publication | all required gates closed | release | NOT VERIFIED | blocked by remaining gates |

## Rules

1. Every `VERIFIED` row must have concrete evidence.
2. Evidence is tied to a candidate/commit or environment boundary.
3. A successful workflow or command does not automatically make a release gate PASS.
4. Unknown external conditions never become PASS by assumption.
5. When code/config changes after verification, reassess every affected row.
6. Keep large logs in GitHub artifacts; keep this matrix concise.

## Maintenance

Update this matrix in the same logical batch as consequential release-gate work. Never invent measurements, approvals, thresholds or external state.

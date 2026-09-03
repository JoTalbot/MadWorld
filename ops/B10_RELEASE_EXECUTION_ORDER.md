# B10 Release Execution Order

Date: 2026-09-03

## Purpose

Single ordered execution sheet for the remaining MadWorld production-release gates. Repository/CI evidence is separated from environment and owner evidence.

## Current baseline

- `main`: `fec22ba22ad5596929325679bb2da9c4133ef5c3`
- Backend CI #538: SUCCESS.
- Release Candidate: `v0.1.0-rc1` preserved.
- Production release tag: not created.
- Current decision: `GO AFTER OWNER ACTIONS`.

## Execution order

1. Deploy/verify production HTTPS and `/health/ready` through the real hostname.
2. Install the daily backup service/timer under `/opt/madworld/backups`; execute and retain evidence.
3. Verify backup integrity, retention and low-disk fail-closed behavior; record actual RPO.
4. Execute a fresh-host restore/recovery rehearsal and record RTO.
5. Execute isolated production-like capacity testing and record owner-approved thresholds.
6. Execute Android API 26 / 29–32 / 33–35 matrix and at least one physical device test.
7. Decide release requirements for push, crash reporting and analytics; configure only the approved providers and verify end-to-end paths.
8. Complete Privacy Policy, Terms, Data Safety and deletion review.
9. Assign incident/on-call ownership and rehearse rollback/incident response.
10. Confirm the existing severity-5 disaster clamp as the intended product behavior. No coefficient change is implied.
11. Re-run the final automated Release Gate against the exact release commit.
12. Populate immutable artifact/provenance evidence.
13. Select final version/tag only after mandatory gates are green.
14. Create the production release.

## Hard rules

- Never convert unavailable evidence into PASS.
- Never create the production tag while a mandatory gate is unresolved.
- Never add secrets or provider credentials to Git.
- Never alter Octopus infrastructure as part of this sequence.
- Never change gameplay/economy balance silently.
- Preserve `v0.1.0-rc1` until the production release is independently verified.

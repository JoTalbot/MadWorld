# MadWorld B10 Final Release Decision

Date: 2026-09-08

## Decision

**GO AFTER REMAINING EXTERNAL VERIFICATION**

The delegated owner decisions are now recorded in-repository. The technical baseline remains green. Public production publication is still blocked only by external/device evidence and final legal publication/verification that cannot be truthfully manufactured inside GitHub.

## Closed delegated decisions

- **Capacity acceptance:** production-equivalent release thresholds are defined in `ops/CAPACITY_ACCEPTANCE.md`.
- **Push:** Firebase/FCM push notifications are explicitly removed from release scope. No Firebase project, credentials, SDK, token registration or push delivery is required.
- **Privacy/Terms:** drafts prepared in `docs/legal/`; final jurisdiction-specific legal review and publication remain required.
- **Deletion:** documented in `docs/legal/DATA_DELETION.md`; complete automated deletion is not claimed until its implementation is verified.
- **Incident/on-call/rollback:** runbook prepared in `ops/INCIDENT_RESPONSE_AND_ROLLBACK.md`; technical ownership model and rollback procedure are documented. A live rollback rehearsal is not claimed without execution evidence.
- **Severity-5 disaster clamp:** accepted for release at the schema-authoritative cap; no gameplay coefficient changed.

## Verified repository/CI baseline

- B1–B9 complete.
- B10 automated Release Gate passed on the verified candidate boundary.
- PostgreSQL migrations and backend tests exercised on PostgreSQL 16.
- Android unit tests and debug artifact generation pass; release build is being revalidated after Firebase removal.
- Production world-tick defects were fixed with regression coverage.
- Production audit on `arm-server-01` completed with exit code 0.
- Production API and PostgreSQL healthy; world-tick worker running.
- Daily backup timer active/enabled and latest backup checksum verified.
- Public `/health/ready` returned HTTP 200 with database ok and `migrations_applied=41`.
- Public TLS verification returned code 0 with a trusted Google Trust Services issuer.
- No failed systemd units reported by the production audit.
- Remote Operator service and result-sync timer active.
- Isolated PostgreSQL backup/restore rehearsal verified with measured RTO 1.015s and production database untouched.
- Isolated API/world-tick and mutation/idempotency rehearsals verified with zero application errors in the captured runs.

## Capacity decision

The release acceptance envelope is now explicitly defined:

- sustained throughput >= 120 requests/s for >= 5 minutes;
- application error rate <= 1.0%;
- p95 <= 250 ms;
- p99 <= 500 ms;
- world-tick lag <= 1000 ms without persistent upward trend;
- queue depth must not grow monotonically/unboundedly and must recover toward baseline;
- PostgreSQL connections must remain below configured limits with headroom.

Existing isolated runs measured approximately 167–169 requests/s with zero application errors and p95 around 127–154 ms. They do not by themselves prove the full 5-minute gate because queue-depth evidence was not captured.

## Remaining mandatory gates

1. **Android API/device matrix — UNVERIFIED.** API 26 / 29–32 / 33–35 plus at least one physical Android device still require execution evidence.
2. **Push delivery — REMOVED FROM RELEASE SCOPE.** No FCM production configuration or physical-device push test is required.
3. **Privacy Policy / Terms — LEGAL REVIEW REQUIRED.** Drafts are prepared, but legal publication and a valid operator/support contact remain required.
4. **Data deletion — PARTIALLY VERIFIED.** The policy/process is documented, but complete deletion implementation and PostgreSQL integration behavior remain unverified.
5. **Capacity full gate — PARTIALLY VERIFIED.** Thresholds are decided, but the required 5-minute controlled run with queue-depth/recovery evidence remains unexecuted.
6. **Rollback rehearsal — NOT VERIFIED.** Runbook and ownership are documented; a real rehearsal requires execution through the production operator path and terminal evidence.

Crash reporting and external analytics are explicitly **not release requirements** for this candidate and remain disabled/unclaimed.

## Severity-5 decision

Severity 5 is accepted at +5000 bps travel risk, -5000 bps extraction and +4000 bps travel time. The raw +6000 bps travel-risk calculation is clamped to the schema-authoritative maximum. Coefficients remain unchanged.

## Release status

**NOT READY FOR PUBLIC PRODUCTION PUBLICATION.**

The remaining blockers are external/device execution and final legal publication, not Firebase configuration.

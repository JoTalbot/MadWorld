# MadWorld — B10 Release Candidate Audit

Date: 2026-09-03

## Purpose

Record the final repository-side B10 audit without treating environment-dependent checks as passed merely because code exists.

## Verified in repository / CI

- B1–B6 are recorded COMPLETE in the production backlog.
- B7 is recorded COMPLETE with explicit deferred external/extended work.
- B8 is recorded COMPLETE with production-infrastructure controls explicitly separated from repository code.
- B9 is recorded COMPLETE with its automated exit gate passed.
- B10 release-gate artifacts exist:
  - `ops/RELEASE_CHECKLIST.md`
  - `ops/RELEASE_NOTES_B10.md`
  - `backend/tests/test_b10_release_gate.py`
- Release Gate run `33748075997` completed successfully on candidate commit `83e639af9317a4f17f8d4eb3e59ea6c8727c6c4b`.
- Release Gate backend job `100625077855` passed migrations, production Compose validation and the complete backend release-gate test suite.
- Release Gate Android job `100625077651` passed unit tests, debug APK assembly, checksum generation and artifact upload.
- Release Gate final job `100625565742` passed.
- Android release-gate artifact `madworld-android-release-gate` was produced successfully; SHA-256 digest: `99676b9b274a45104954919815abf2f9b7a7fb9f9ff023d03ec6f4c84f8950f3`.
- Production Compose validation is part of the automated gate.
- B10 release-gate contract tests are part of the backend test suite.
- PostgreSQL URL normalization to the installed psycopg 3 driver is now protected by `backend/tests/test_database_url_contract.py`.

## Not honestly verifiable from repository-only access

These checks remain RELEASE-OWNER / ENVIRONMENT gates:

- Full end-to-end gameplay regression on a deployed environment.
- Real PostgreSQL backup and restore exercise against the intended production-like environment.
- Sustained load/stress execution against an isolated production-like environment with capacity measurements.
- Android API 26 / 29–32 / 33–35 execution on the actual release matrix.
- Physical Android device verification.
- External crash-reporting provider configuration and validation.
- External analytics/push provider configuration and validation.
- Production secrets/configuration verification.
- Privacy/legal approval.
- Final capacity approval.
- Rollback and disaster-recovery rehearsal.
- Incident-response rehearsal and operational ownership sign-off.
- Final release version/tag selection.

## Release decision

**B10 remains ACTIVE / Release Candidate.**

The repository-side implementation and automated Release Gate are green, but the project must not be labeled production-ready until the mandatory environment and owner checks above are explicitly verified.

This distinction is intentional: a green CI run is evidence that the code passed its automated contract, not evidence that a real production environment, device fleet, external providers or legal approvals exist. Humanity has suffered enough from checkboxes pretending to be reality.

## Next release-owner actions

1. Execute the production-like migration and backup/restore exercise.
2. Execute isolated load/stress verification and record capacity numbers.
3. Run the Android release matrix, including a physical device where available.
4. Configure and validate crash, analytics and push providers.
5. Verify production secrets/configuration and deployment health.
6. Rehearse rollback, disaster recovery and incident response.
7. Complete privacy/legal review.
8. Select release version/tag and complete the release checklist.
9. Only then change B10 from ACTIVE to COMPLETE.

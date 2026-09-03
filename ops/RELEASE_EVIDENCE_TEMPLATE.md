# B10 Release Evidence Template

> Operational evidence record for the MadWorld Release Candidate. This document records observed evidence only. Unknown or unexecuted checks must remain `UNKNOWN`.

## 1. Candidate identity

- Candidate commit:
- Branch/tag:
- Release candidate version:
- Evidence date (UTC):
- Release owner:

## 2. Automated repository gate

- Unified release-gate workflow run:
- Backend job/run:
- Android job/run:
- Final gate result: `PASS` / `FAIL` / `UNKNOWN`
- Backend pytest result:
- Production Compose validation: `PASS` / `FAIL` / `UNKNOWN`
- Android unit tests: `PASS` / `FAIL` / `UNKNOWN`
- Android debug APK build: `PASS` / `FAIL` / `UNKNOWN`
- APK artifact/checksum:

## 3. Backend / database verification

- Migration from clean database: `PASS` / `FAIL` / `UNKNOWN`
- Database engine/version:
- Backup command executed: `PASS` / `FAIL` / `UNKNOWN`
- Backup artifact identifier:
- Restore executed against isolated database: `PASS` / `FAIL` / `UNKNOWN`
- Restore verification result:
- Restore duration:
- Schema migration head after restore:

## 4. Load / capacity verification

- Environment:
- Test duration:
- Target request rate:
- Achieved request rate:
- p50 latency:
- p95 latency:
- p99 latency:
- Error rate:
- Database pool saturation observed: `YES` / `NO` / `UNKNOWN`
- World-tick lag observed:
- Rate-limit containment verified: `PASS` / `FAIL` / `UNKNOWN`
- Capacity approval: `APPROVED` / `REJECTED` / `UNKNOWN`

## 5. Android verification

| Target | Result | Evidence |
|---|---|---|
| API 26 emulator | `PASS/FAIL/UNKNOWN` | |
| API 29-32 emulator/device | `PASS/FAIL/UNKNOWN` | |
| API 33-35 emulator/device | `PASS/FAIL/UNKNOWN` | |
| Physical Android device | `PASS/FAIL/UNKNOWN` | |
| Offline queue/reconnect | `PASS/FAIL/UNKNOWN` | |
| Notifications | `PASS/FAIL/UNKNOWN` | |
| Localization | `PASS/FAIL/UNKNOWN` | |
| Accessibility | `PASS/FAIL/UNKNOWN` | |

## 6. External providers and production controls

- Crash reporting configured and verified: `PASS` / `FAIL` / `UNKNOWN`
- Analytics configured and verified: `PASS` / `FAIL` / `UNKNOWN`
- Push delivery configured and verified: `PASS` / `FAIL` / `UNKNOWN`
- Production secrets/configuration verified: `PASS` / `FAIL` / `UNKNOWN`
- Privacy/legal approval: `APPROVED` / `REJECTED` / `UNKNOWN`

## 7. Rollback / disaster recovery / incident response

- Rollback rehearsal executed: `PASS` / `FAIL` / `UNKNOWN`
- Rollback duration:
- Restore/DR rehearsal executed: `PASS` / `FAIL` / `UNKNOWN`
- Incident-response contacts/runbook verified: `PASS` / `FAIL` / `UNKNOWN`
- Recovery objective achieved: `PASS` / `FAIL` / `UNKNOWN`

## 8. Release decision

### Mandatory rule

B10 cannot be marked complete while any mandatory automated gate is `FAIL` or any mandatory production/physical verification remains `UNKNOWN`.

- Release decision: `GO` / `NO-GO` / `CONDITIONAL` / `UNKNOWN`
- Blocking items:
- Approver:
- Approval timestamp (UTC):
- Notes:

## Evidence hygiene

- Never record secrets, tokens, private keys, credentials, or personal data here.
- Link or reference immutable workflow runs/artifacts rather than copying sensitive logs.
- Keep failed and superseded evidence for auditability; do not rewrite history to make a release look cleaner. Humanity has enough of that already.

# B10 Current Release Audit

Date: 2026-09-03
Current HEAD: `8545a3d649963dad90afe2821b05ecf8b986e4aa`

## Repository state

- B1-B9 production program: COMPLETE.
- B10 repository-side implementation: COMPLETE.
- Current Android local-device hardening is present on HEAD.
- Release Gate evidence previously passed on the preceding exact verified boundary.
- HEAD is 6 commits ahead of that boundary; the delta is limited to README/status/backlog documentation plus Android debug cleartext/API configuration.
- Therefore previous green Release Gate evidence must not be treated as evidence for the current HEAD.

## Current release decision

**NO-GO pending external/owner gates and a final exact-HEAD Release Gate run.**

## Mandatory gates

- [ ] Real `api.autosklo.org.ua`/production API HTTPS and reverse-proxy verification.
- [ ] Scheduled backup installed and executed; measured RPO recorded.
- [ ] Fresh-host disaster recovery rehearsal; measured RTO recorded.
- [ ] Isolated production capacity/load validation and approval.
- [ ] Android API 26 validation.
- [ ] Android API 29-32 validation.
- [ ] Android API 33-35 validation.
- [ ] Physical Android device validation.
- [ ] Physical-device offline queue, reconnect/resume, stale-state and network-loss validation.
- [ ] Production push/crash/analytics provider decisions and verification where required.
- [ ] Privacy Policy, Terms, Data Safety and deletion disclosures approved.
- [ ] Incident/on-call ownership assigned.
- [ ] Rollback rehearsal completed.
- [ ] DR rehearsal completed.
- [ ] Product-owner approval of severity-5 disaster clamp behavior.
- [ ] Immutable evidence attached for every mandatory gate.
- [ ] Final Release Gate run on the exact release commit.
- [ ] Final version/tag created.
- [ ] Production release published.

## Android local development note

- Emulator debug fallback remains `http://10.0.2.2:8000`.
- Physical phones must use a reachable LAN API URL through `MADWORLD_API_URL`.
- Debug builds may use cleartext HTTP for local development only.
- Release builds keep cleartext HTTP disabled and require HTTPS.

## Batch safety boundary

MadWorld release work must remain isolated to this repository/application. Do not touch Octopus infrastructure, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup or UFW.

## Rule

Do not convert UNKNOWN/UNVERIFIED external evidence into VERIFIED because a script, checklist or repository configuration exists. Production GO is allowed only after the evidence is real, immutable and attached to the exact release candidate.

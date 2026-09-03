# B10 Current Release Audit

Date: 2026-09-03
Current HEAD: `c07677a479499a855b1acb40f89ea523d43e764a`

## Repository state

- B1-B9 production program: COMPLETE.
- B10 repository-side implementation: COMPLETE.
- Android local-device hardening is present on HEAD.
- Final exact-HEAD Release Gate run **33799077507 / #31: SUCCESS**.
- Final exact-HEAD Backend CI **33799077517 / #550: SUCCESS**.
- Android Release Gate job: SUCCESS, including unit tests, debug APK assembly, checksum generation and artifact upload.
- Backend Release Gate job: SUCCESS, including migrations, production Compose validation and B10 release-gate tests.
- Final gate job: SUCCESS.
- Release-gate artifact `madworld-android-release-gate` exists and is not expired; recorded digest: `sha256:3556aecd50f1c41c140de5683f52491b59093fb8f79bd1ea9279d63c189ef9c5`.

## Current release decision

**NO-GO for public production launch until the remaining owner/environment gates below have real evidence.**

The repository and CI side is green. This audit deliberately does not convert external prerequisites into VERIFIED merely because documentation or automated tests exist.

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
- [ ] Final version/tag created from the verified release commit.
- [ ] Production release published.

## External verification note

A direct network probe from the available execution environment could not resolve `api.autosklo.org.ua`; therefore production HTTPS is **UNVERIFIED**, not failed and not passed. No infrastructure outside MadWorld was modified.

## Android local development note

- Emulator debug fallback remains `http://10.0.2.2:8000`.
- Physical phones must use a reachable LAN API URL through `MADWORLD_API_URL`.
- Debug builds may use cleartext HTTP for local development only.
- Release builds keep cleartext HTTP disabled and require HTTPS.

## Existing release state

- GitHub currently has `v0.1.0-rc1` as a prerelease candidate from an earlier commit.
- It must not be relabeled as a final production release or treated as the final exact-HEAD artifact.

## Batch safety boundary

MadWorld release work must remain isolated to this repository/application. Do not touch Octopus infrastructure, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup or UFW.

## Rule

Do not convert UNKNOWN/UNVERIFIED external evidence into VERIFIED because a script, checklist or repository configuration exists. Production GO is allowed only after the evidence is real, immutable and attached to the exact release candidate.

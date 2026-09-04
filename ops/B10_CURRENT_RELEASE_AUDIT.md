# B10 Current Release Audit

Date: 2026-09-04
Current HEAD: `11864d58cf3d81d7aac1749a7498611904efecb4`

## Repository state

- B1-B9 production program: COMPLETE.
- B10 repository-side implementation: COMPLETE.
- Android local-device hardening and network-resilience requirements are present.
- Exact-head Backend CI: **33866800270 / #569: SUCCESS**.
- Exact-head Release Gate: **33866800289 / #50: SUCCESS**.
- Exact-head Release Gate completed backend validation, Android tests/build/checksum/artifact path and final gate successfully.
- Release artifact: `madworld-android-release-gate`, digest `sha256:134fe4ae7c09f9ed6a66f5c40280cdcb567f240506366468b50d17abf2ca0bcf`.
- Production HTTPS/reverse-proxy evidence is attached at `ops/PROD_HARDENING_EVIDENCE_2026-09-03.md`.
- Production scheduled backup/RPO evidence is attached at `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
- Repository-side isolated backup/restore verification is attached at `ops/B10_GITHUB_DR_EVIDENCE_2026-09-04.md`.
- Repository-side capacity/resilience evidence is attached at `ops/B10_CAPACITY_CI_EVIDENCE.md`.
- Android network-resilience requirements are attached at `ops/B10_ANDROID_NETWORK_RESILIENCE.md`.

## Current release decision

**NO-GO for public production launch until the remaining owner/environment gates have real evidence.**

CI is green on the exact current HEAD. This is necessary, but it does not substitute for fresh-host DR/RTO, production-scale capacity, real Android devices, provider/legal/ownership decisions, rollback rehearsal, severity-5 approval and final release approval.

## Mandatory gates

- [x] Real `api.autosklo.org.ua`/production API HTTPS and reverse-proxy verification. Evidence: `ops/PROD_HARDENING_EVIDENCE_2026-09-03.md`.
- [x] Scheduled backup installed and executed in target environment. Evidence: `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
- [x] Backup retention, SHA-256 manifest, integrity check and low-disk fail-closed behavior observed. Evidence: `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
- [x] RPO target <=24h supported by daily scheduled backup. No measured data-loss RPO claim. Evidence: `ops/B10_PROD_DR_RPO_EVIDENCE_2026-09-04.md`.
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
- [ ] DR rehearsal completed on the target recovery environment.
- [ ] Product-owner approval of severity-5 disaster clamp behavior.
- [ ] Immutable evidence attached for every mandatory gate.
- [x] Exact-head Release Gate rerun: `33866800289 / #50: SUCCESS`.
- [ ] Final version/tag created from the verified release commit.
- [ ] Production release published.

## Evidence interpretation

Repository automation may prove that a procedure is executable and repeatable in an isolated environment. It does not prove that the corresponding production operation has been installed, scheduled, observed, measured or approved. Unknown remains Unknown until target-environment evidence is attached.

## External verification note

Production HTTPS/reverse-proxy is VERIFIED by the Arena Agent server audit. Verified chain: Cloudflare-proxied DNS -> TLS on `api.autosklo.org.ua` -> nginx -> `127.0.0.1:8090` -> MadWorld API container port 8000. Public `/health/ready` returned HTTP 200 with database and migration status healthy. The HTTP port-80 access-control ordering issue was identified and fixed; post-fix non-allow-listed direct HTTP access returns 403.

## Android local development note

- Emulator debug fallback remains `http://10.0.2.2:8000`.
- Physical phones must use a reachable API URL through `MADWORLD_API_URL`.
- Debug builds may use cleartext HTTP for local development only.
- Release builds keep cleartext HTTP disabled and require HTTPS.
- Production physical-device builds should use `https://api.autosklo.org.ua`.

## Existing release state

- GitHub has `v0.1.0-rc1` as a prerelease candidate from an earlier commit.
- It must not be relabeled as a final production release or treated as the final exact-HEAD artifact.

## Batch safety boundary

MadWorld release work must remain isolated to this repository/application. Do not touch Octopus infrastructure, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup or UFW.

# B10 Current Release Audit

Date: 2026-09-03
Updated: 2026-09-04
Current HEAD: `ec213ceaff60a4c5ee7f7afe992c303c22374049`

## Update 2026-09-04 — backup/RPO and DR/RTO batch

- ⚠️ This update records a **BLOCKED execution batch**, not a pass.
- ❌ Scheduled-backup + measured-RPO gate: **still OPEN — NOT PASSED**. Evidence record: `ops/B10_BACKUP_RPO_EVIDENCE_2026-09-04.md`.
- ❌ Fresh-host DR + measured-RTO gate: **still OPEN — NOT PASSED**. Evidence record: `ops/B10_DR_RTO_EVIDENCE_2026-09-04.md`.
- 🚧 Blocker: the executing environment has no SSH key material and no
  application-layer connectivity to `129.213.177.56` (SSH reset at
  `kex_exchange_identification`; TLS reset before handshake; every probed port
  answers the TCP handshake instantly — egress-interception signature). The
  sandbox also has no `psql`/`pg_dump`/`pg_restore`/`docker` and no copy of a
  production dump. No production backup was executed and no RPO/RTO is claimed.
- ✅ Only repository-side static validation passed (`bash -n` on
  `ops/backup_daily.sh`, `ops/backup_restore.sh`; unit-file presence on HEAD).
  This does not count as production evidence.
- ℹ️ Production HTTPS row below reflects the previously committed
  `ops/PROD_HARDENING_EVIDENCE_2026-09-03.md`. It was NOT re-verified in this
  batch (sandbox egress cannot reach Cloudflare-fronted endpoints); this batch
  neither confirms nor contradicts that record.
- 🚫 Decision unchanged: **NO-GO** for production release while any mandatory
  gate below is OPEN.

## Repository state

- B1-B9 production program: COMPLETE.
- B10 repository-side implementation: COMPLETE.
- Android local-device hardening is present on HEAD.
- Previous exact-HEAD Release Gate run **33799077507 / #31: SUCCESS**.
- Previous exact-HEAD Backend CI **33799077517 / #550: SUCCESS**.
- Previous Android Release Gate job: SUCCESS, including unit tests, debug APK assembly, checksum generation and artifact upload.
- Previous Backend Release Gate job: SUCCESS, including migrations, production Compose validation and B10 release-gate tests.
- Previous final gate job: SUCCESS.
- Previous release-gate artifact `madworld-android-release-gate` recorded digest: `sha256:3556aecd50f1c41c140de5683f52491b59093fb8f79bd1ea9279d63c189ef9c5`.
- A production hardening evidence record is now attached at `ops/PROD_HARDENING_EVIDENCE_2026-09-03.md`.

## Current release decision

**NO-GO for public production launch until the remaining owner/environment gates below have real evidence.**

The repository and prior CI side are green, but the evidence commit changed HEAD. Therefore the Release Gate must be rerun on the current exact release commit before final release.

## Mandatory gates

- [x] Real `api.autosklo.org.ua`/production API HTTPS and reverse-proxy verification. Evidence: `ops/PROD_HARDENING_EVIDENCE_2026-09-03.md`.
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
- [ ] Final exact-head Release Gate rerun on the current release commit.
- [ ] Final version/tag created from the verified release commit.
- [ ] Production release published.

## External verification note

Production HTTPS/reverse-proxy is now **VERIFIED** by the Arena Agent server audit. Verified chain: Cloudflare-proxied DNS -> TLS on `api.autosklo.org.ua` -> nginx -> `127.0.0.1:8090` -> MadWorld API container port 8000. Public `/health/ready` returned HTTP 200 with database and migration status healthy. The HTTP port-80 access-control ordering issue was identified and fixed; post-fix non-allow-listed direct HTTP access returns 403.

Full evidence, commands, configuration details, timestamps and the restart verification are recorded in `ops/PROD_HARDENING_EVIDENCE_2026-09-03.md`.

## Android local development note

- Emulator debug fallback remains `http://10.0.2.2:8000`.
- Physical phones must use a reachable API URL through `MADWORLD_API_URL`.
- Debug builds may use cleartext HTTP for local development only.
- Release builds keep cleartext HTTP disabled and require HTTPS.
- Production physical-device builds should use `https://api.autosklo.org.ua`.

## Existing release state

- GitHub currently has `v0.1.0-rc1` as a prerelease candidate from an earlier commit.
- It must not be relabeled as a final production release or treated as the final exact-HEAD artifact.

## Batch safety boundary

MadWorld release work must remain isolated to this repository/application. Do not touch Octopus infrastructure, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup or UFW.

## Rule

Do not convert UNKNOWN/UNVERIFIED external evidence into VERIFIED because a script, checklist or repository configuration exists. Production GO is allowed only after the evidence is real, immutable and attached to the exact release candidate.

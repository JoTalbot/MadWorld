# B10 Final Batch Status

Date: 2026-09-03
Current HEAD: `c583be18a39d562e7364d53914367593af0a9f2b`

## Repository-side batch status

The repository-side B1-B10 production program is complete. The repository-side Release Gate previously passed on the preceding exact verified boundary (`650bd816a078b26dfe49b2ef23a8545e35a1f60a`), including:

- Release Gate run `33773666109`: success
- Backend CI run `33773666081`: success
- Release Gate backend job: migrations, production Compose validation and release-gate tests passed
- Release Gate Android job: Android unit tests, debug APK assembly and artifact checksum passed
- Release Gate final gate job: passed

Since that verification boundary, Android physical-device/debug API configuration was hardened and the current exact-head audit was added. The previous green result therefore does **not** certify the current HEAD.

## Remaining mandatory external/owner gates

These cannot be truthfully certified from GitHub repository state alone and remain blocking until real evidence is attached:

- real-domain HTTPS/reverse-proxy verification;
- scheduled backup installation/execution and measured RPO;
- fresh-host disaster-recovery rehearsal and measured RTO;
- isolated production-capacity/load validation and approval;
- Android API 26, API 29–32 and API 33–35 execution;
- at least one physical Android device validation;
- end-to-end offline queue, reconnect/resume, stale-state and network-loss validation on real Android environments;
- push/crash/analytics provider decisions and, where required, production verification;
- Privacy Policy, Terms, Data Safety and deletion disclosures approved;
- incident/on-call ownership assigned;
- rollback and DR rehearsal completed;
- product-owner approval of the severity-5 disaster clamp behavior;
- immutable evidence attached for every mandatory gate;
- final Release Gate rerun on the exact current release commit after those gates are closed;
- final version/tag and production release publication.

## Release decision

**NO-GO until the mandatory external/owner gates above are actually verified.**

The repository must not convert UNVERIFIED or UNKNOWN evidence into VERIFIED merely because the corresponding scripts, checklists or procedures exist.

## Product scope

No gameplay/economy balance change was introduced by the B10 release hardening work. Any change to disaster clamp coefficients or schema bounds must go through the persistent improvement backlog approval policy.

## Android local-device hardening

- Debug builds explicitly allow cleartext HTTP for local development only.
- Physical devices must use a reachable LAN API URL through `MADWORLD_API_URL`.
- Release builds keep cleartext HTTP disabled and require HTTPS.
- The emulator-only `10.0.2.2` fallback must not be used on a physical phone.

## Safety boundary

Production verification must remain scoped to MadWorld. Do not touch Octopus infrastructure, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup or UFW as part of MadWorld release work.

See `ops/B10_CURRENT_RELEASE_AUDIT.md` for the exact-head gate matrix.
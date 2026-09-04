# B10 Final Batch Status

Date: 2026-09-04
Current HEAD: updated by this commit

## Repository-side batch status

The repository-side B1-B10 production program is complete. The current exact-head CI/release automation is green, while production launch remains blocked by external environment and owner gates.

## Verified repository-side gates

- Current exact-head Backend CI: `33863387147` / #558 — SUCCESS.
- Current exact-head Release Gate before this documentation commit: `33863387180` / #39 — SUCCESS.
- Production HTTPS/reverse-proxy evidence: `ops/PROD_HARDENING_EVIDENCE_2026-09-03.md`.
- Isolated backup/restore verification: `ops/B10_GITHUB_DR_EVIDENCE_2026-09-04.md`.
- Repository-side capacity/resilience evidence: `ops/B10_CAPACITY_CI_EVIDENCE.md`.
- Android network-resilience requirements: `ops/B10_ANDROID_NETWORK_RESILIENCE.md`.

## Remaining mandatory external/owner gates

These cannot be truthfully certified from GitHub repository state alone and remain blocking until real evidence is attached:

- scheduled backup installation/execution and measured production RPO;
- fresh-host disaster-recovery rehearsal and measured production RTO;
- isolated production-capacity/load validation and owner approval;
- Android API 26, API 29–32 and API 33–35 execution;
- at least one physical Android device validation;
- physical-device offline queue, reconnect/resume, stale-state and network-loss validation;
- push/crash/analytics provider decisions and, where required, production verification;
- Privacy Policy, Terms, Data Safety and deletion disclosures approved;
- incident/on-call ownership assigned;
- rollback and target-environment DR rehearsal;
- product-owner approval of severity-5 disaster-clamp behavior;
- immutable evidence attached for every mandatory gate;
- final Release Gate rerun on the exact final release commit after all required evidence is closed;
- final version/tag and production release publication.

## Release decision

**NO-GO until the mandatory external/owner gates above are actually verified.**

Repository scripts, CI runs and checklists are evidence of implementation or repeatability only. They do not become production evidence by optimism.

## Product scope

No gameplay/economy balance change was introduced by B10 release hardening. Any change to disaster-clamp coefficients or schema bounds must go through the persistent improvement backlog approval policy.

## Android local-device hardening

- Debug builds explicitly allow cleartext HTTP for local development only.
- Physical devices must use a reachable API URL through `MADWORLD_API_URL`.
- Release builds keep cleartext HTTP disabled and require HTTPS.
- The emulator-only `10.0.2.2` fallback must not be used on a physical phone.

## Safety boundary

Production verification must remain scoped to MadWorld. Do not touch Octopus infrastructure, unrelated PostgreSQL, existing Docker networks/volumes, host port 8000, global Docker cleanup or UFW as part of MadWorld release work.

See `ops/B10_CURRENT_RELEASE_AUDIT.md` and `ops/B10_OWNER_GATE_EVIDENCE.md` for the current exact-head and owner-gate matrices.

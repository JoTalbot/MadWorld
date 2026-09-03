# MadWorld — B10 Final Release Checklist

## Release gate

B10 is complete only when implementation, automated verification, applicable Android/backend CI, operational checks, and final repository audit all pass.

## Product regression

- [ ] Onboarding/authentication
- [ ] Gathering/resource extraction
- [ ] Refining/production/crafting
- [ ] Market/order lifecycle
- [ ] Logistics/warehouse
- [ ] Regional travel
- [ ] Vehicle combat
- [ ] Salvage/recovery
- [ ] Missions/contracts/expeditions
- [ ] Territory/warfare
- [ ] Corporations/alliances
- [ ] Convoys
- [ ] Dynamic world/NPC factions
- [ ] Finance/provenance
- [ ] Notifications/offline/reconnect

## Technical gate

- [ ] Clean migration chain on PostgreSQL
- [ ] Backend unit/API/persistence/invariant tests green
- [ ] Android unit tests and debug artifact green
- [ ] Integration/concurrency/retry/idempotency tests green
- [ ] Security/exploit regression green
- [ ] Deterministic replay checks green
- [ ] Load/stress contracts green
- [ ] Production Compose validation green
- [ ] Backup creation and restore verification green
- [ ] Release artifact/build metadata verified

## Operations

- [ ] Health endpoint verified
- [ ] Worker health/lag observed
- [ ] Structured logs available
- [ ] Critical metrics and alert thresholds configured
- [ ] Database capacity/pool limits reviewed
- [ ] Rollback procedure rehearsed
- [ ] Disaster-recovery procedure rehearsed
- [ ] Incident response ownership documented

## Android release matrix

- [ ] API 26 low-memory emulator
- [ ] API 29–32 mid-range profile
- [ ] API 33–35 modern profile
- [ ] At least one physical device when available
- [ ] Offline → reconnect → authoritative refresh
- [ ] Notification/localization/accessibility smoke checks

## Product/release readiness

- [ ] Privacy/legal review completed by owner
- [ ] Analytics events validated
- [ ] Crash reporting configured
- [ ] Localization coverage reviewed
- [ ] Accessibility audit completed
- [ ] Onboarding reviewed
- [ ] Server capacity approved
- [ ] Database migration/rollback plan approved
- [ ] Release notes prepared
- [ ] Version/tag selected

## Final sign-off

B10 must not be marked COMPLETE while any required automated gate is red or any mandatory production/physical verification is unknown. Environment-dependent checks must be explicitly recorded as verified, blocked, or deferred rather than inferred.

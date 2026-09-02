# MadWorld Improvement Backlog

## Working policy — persistent across chats

This file is the persistent source of truth for improvement proposals and implementation decisions. A new chat must read and follow this policy instead of requiring the user to restate it.

1. When a materially useful improvement is discovered during analysis or implementation, record it in this backlog immediately.
2. For every product-changing improvement, record materially different implementation variants before selecting one. At minimum consider Minimal, Systemic, Advanced and Hybrid where applicable.
3. New product-changing improvements start as `PLANNED`; they are not considered approved merely because they appear in the backlog.
4. In the chat, present newly discovered improvements and ask the user whether to apply them. Do not silently implement product-changing improvements.
5. After the user selects a variant, change the item to `ACCEPTED`, record the selected variant and implement it.
6. Bug fixes, security fixes and non-product-changing refactors may be applied directly when they improve correctness or safety without changing the intended game design.
7. When implementation is complete, record the implementation status, important deferred parts and tests/verification in the backlog.
8. Never delete an accepted or planned improvement merely because it is deferred. Preserve the decision history.

## IMP-020 — Authoritative time + due-job scheduling
- Status: ACCEPTED — Hybrid
## IMP-023 — Versioned domain events
- Status: ACCEPTED — Hybrid
## IMP-026 — Observability foundation
- Status: ACCEPTED — Hybrid
## IMP-027 — Reconnect/resume
- Status: ACCEPTED — Hybrid
## IMP-028 — Offline command delivery
- Status: ACCEPTED — Hybrid
## IMP-029 — Regional player markets
- Status: COMPLETE — Hybrid selected slice.
## IMP-061 — Inventory authority
- Status: ACCEPTED
## IMP-062 — Item definitions
- Status: ACCEPTED
## IMP-063 — Wallet/ledger authority
- Status: ACCEPTED
## IMP-064 — Crafting jobs
- Status: ACCEPTED
## IMP-065 — Outbox delivery
- Status: ACCEPTED
## IMP-066 — API idempotency
- Status: COMPLETE for selected slice.
## IMP-067 — In-memory transactional semantics
- Status: ACCEPTED — Hybrid
## IMP-068 — Player bootstrap vertical slice
- Status: ACCEPTED — Hybrid
## IMP-069 — Player state snapshot API
- Status: ACCEPTED — Hybrid
## IMP-070 — Android authoritative-state client
- Status: ACCEPTED — Hybrid
## IMP-071 — Persistent player sessions
- Status: ACCEPTED — Hybrid
## IMP-072 — Player-boundary session enforcement
- Status: COMPLETE for selected slice.
## IMP-073 — Regional market matching concurrency hardening
- Status: COMPLETE — Technical hardening.
## IMP-074 — Vehicle repair vertical slice
- Status: COMPLETE — Hybrid.
## IMP-075 — Legacy vehicle repair API migration
- Status: COMPLETE — Hybrid.
## IMP-076 — Component-aware vehicle damage
- Status: COMPLETE — Advanced + Systemic.
## IMP-077 — Contract system
- Status: COMPLETE — Advanced + Systemic.
## IMP-078 — Expedition system
- Status: COMPLETE — Advanced + Systemic.
## IMP-079 — Settlement / base-point gameplay loop
- Status: COMPLETE — Hybrid.
## IMP-080 — Android settlement gameplay client
- Status: COMPLETE — Hybrid.
## IMP-081 — Phase 2 Economy Foundation
- Status: COMPLETE — Hybrid.
## IMP-082 — Economy-to-Gameplay Integration
- Status: COMPLETE — Hybrid.

## PHASE 3 — Vehicles & Combat
### IMP-083 — Modular vehicle fitting
- Status: COMPLETE — Hybrid foundation.
### IMP-084 — Vehicle stats and systems
- Status: COMPLETE — Hybrid foundation.
### IMP-085 — Weapon system
- Status: COMPLETE — Hybrid foundation.
### IMP-086 — Authoritative vehicle combat
- Status: COMPLETE — Advanced + Systemic foundation.
### IMP-087 — Salvage
- Status: COMPLETE — Hybrid foundation.
### IMP-088 — Vehicle recovery
- Status: COMPLETE — Hybrid foundation.
### IMP-089 — Convoys
- Status: COMPLETE — Hybrid foundation.
### IMP-090 — Phase 3 Android integration
- Status: COMPLETE — Hybrid foundation.
### Phase 3 verification note
- Status: IMPLEMENTED as one batch on `main`; production hardening remains tracked by follow-up work.

## PHASE 4 — Social Sandbox

### IMP-091 — Corporations / gangs
- Status: COMPLETE — Hybrid foundation selected by user command to execute Phase 4 as one batch.
- Implemented: corporation identity, owner boundary, code/name/tax invariants, membership persistence.

### IMP-092 — Roles and permissions
- Status: COMPLETE — Hybrid foundation.
- Implemented: canonical role set and permission vocabulary with domain validation.

### IMP-093 — Shared wallets
- Status: COMPLETE — Hybrid.
- Implemented: corporation-owned wallet support, authoritative balance/transfer commands, deterministic locking, immutable ledger, idempotency, audit/outbox integration.
- Deferred product work: funding policies and richer treasury/reporting UI.

### IMP-094 — Shared hangars and corporate assets
- Status: COMPLETE — Hybrid.
- Implemented: hangar capacity, custody registration/move/assignment, row locking, optimistic version checks and manufacturer provenance binding.
- Deferred product work: full physical vehicle/item ownership transfer semantics.

### IMP-095 — Alliances
- Status: COMPLETE — Hybrid social-core lifecycle.
- Implemented: alliance creation, invitations, accept/decline/leave lifecycle, membership overview and authoritative persistence.
- Deferred product work: alliance-level territorial/economic effects and richer governance.

### IMP-096 — Diplomacy
- Status: COMPLETE — Advanced foundation.
- Implemented: directed relations, standings, trade/transit flags and hostile-trade invariant.
- Deferred product work: world/NPC/market effects.

### IMP-097 — Social contracts
- Status: COMPLETE — Hybrid.
- Implemented: participant validation, authoritative lifecycle, escrow creation, wallet locking, balanced ledger settlement, release/refund, idempotency, audit/outbox and state-integrity enforcement.
- Deferred product work: physical delivery verification beyond the accepted social-core financial settlement.

### IMP-098 — Social reputation
- Status: COMPLETE — Hybrid social-core slice.
- Implemented: bounded authoritative mutation, immutable history and contract-driven reputation propagation on successful settlement.
- Deferred product work: world/NPC/economy-wide propagation.

### IMP-099 — Manufacturers / brands
- Status: COMPLETE — Hybrid.
- Implemented: corporation brand identity, bounded quality rating and asset manufacturer provenance binding.

### IMP-100 — Phase 4 Android integration
- Status: COMPLETE — Hybrid social management surface.
- Implemented: typed social state, capability discovery, corporation creation/overview, corporate wallet balance/refresh and manufacturer/brand creation UI.
- Deferred product work: full alliance, asset and contract mutation screens.

### IMP-101 — Phase 4 social lifecycle hardening
- Status: COMPLETE — Hybrid.
- Implemented: contract transition invariants, reputation mutation invariants, escrow/invitation state validation and persistence for escrow/history/invitations.

### IMP-102 — Phase 4 social database integrity hardening
- Status: COMPLETE — Technical hardening.
- Implemented: partial unique indexes for reputation targets, one-primary-corporation membership constraint, escrow transition trigger and escrow-backed contract state consistency trigger.

### IMP-103 — Phase 4 authoritative financial/social operations
- Status: COMPLETE — Hybrid social-core scope.
- Implemented: corporate wallet operations, alliance lifecycle, hangar/asset accounting, escrow settlement, contract-driven reputation propagation, manufacturer provenance and Android social-management surface.
- Product-changing expansions remain deferred and preserved as future work.

### Phase 4 verification note
- Main branch head: `88fc84147b42c87fcb7387a5dcd908960abd86bf`.
- Backend CI #329: SUCCESS. Migration chain applied and test suite completed successfully.
- Android CI #37: SUCCESS. Debug APK assembled successfully.
- Backend CI #323: FAILED on the superseded test-only commit; failure was caused by an incorrect test assumption and was corrected before CI #329.
- Migrations `016_phase4_social_operations.sql`, `017_phase4_social_integrity.sql`, `018_phase4_corporate_wallets.sql`, `019_phase4_social_completion.sql` and `020_phase4_contract_integrity.sql` are present.
- Phase 4 social core is COMPLETE. Remaining items listed above are product expansions that intentionally cross into broader world/economic gameplay rather than unfinished Phase 4 correctness.

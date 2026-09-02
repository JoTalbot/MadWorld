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
- Status: IN PROGRESS — Hybrid.
- Implemented: corporation wallet link, database support for corporation-owned wallets, authoritative balance/transfer endpoints with deterministic row locking and idempotency.
- Deferred: wallet funding policies and richer treasury/reporting UI.

### IMP-094 — Shared hangars and corporate assets
- Status: IN PROGRESS — Hybrid.
- Implemented: hangar capacity and corporate asset custody registration/move/assignment endpoints with row locking and capacity checks.
- Deferred: transactional vehicle/item ownership transfer and deeper asset provenance rules.

### IMP-095 — Alliances
- Status: IN PROGRESS — Hybrid.
- Implemented: alliance membership/invitation persistence plus authoritative create/invite/accept/leave lifecycle routes.
- Deferred: alliance-level economic/territory effects and richer diplomatic governance.

### IMP-096 — Diplomacy
- Status: COMPLETE — Advanced foundation.
- Implemented: directed relations, standings, trade/transit flags and hostile-trade invariant.
- Deferred: world/NPC/market effects.

### IMP-097 — Social contracts
- Status: IN PROGRESS — Hybrid.
- Implemented: participant validation, authoritative lifecycle transitions, audit trail and escrow persistence foundation.
- Deferred: wallet locking/release/refund settlement and delivery verification.

### IMP-098 — Social reputation
- Status: IN PROGRESS — Hybrid.
- Implemented: bounded authoritative reputation mutation and immutable history.
- Deferred: event-driven propagation into economy/NPC/world services.

### IMP-099 — Manufacturers / brands
- Status: COMPLETE — Hybrid foundation.
- Implemented: one-to-one corporation brand identity, quality rating and reputation.
- Deferred: item provenance and quality integration.

### IMP-100 — Phase 4 Android integration
- Status: IN PROGRESS — Hybrid.
- Implemented: typed social state models, capability discovery, corporation overview and corporation creation client/UI.
- Deferred: full alliance, wallet, asset and contract mutation UI.

### IMP-101 — Phase 4 social lifecycle hardening
- Status: ACCEPTED — Hybrid, approved by user continuation of Phase 4 implementation.
- Implemented: contract transition invariants, reputation mutation invariants, escrow/invitation state validation, persistence for escrow/history/invitations.
- Deferred: full economic settlement and Android mutation UI.

### IMP-102 — Phase 4 social database integrity hardening
- Status: COMPLETE — Technical hardening.
- Implemented: partial unique indexes for player/corporation reputation targets and database-enforced one-primary-corporation membership under concurrent requests.
- Verification: migration `017_phase4_social_integrity.sql` is present.

### IMP-103 — Phase 4 authoritative financial/social operations
- Status: IN PROGRESS — Hybrid.
- Scope: idempotent corporate wallet operations, completed alliance lifecycle, hangar/asset accounting, contract escrow settlement and contract-driven reputation propagation.
- Implemented in current slice: corporate wallet balance/transfer commands, deterministic wallet locking, immutable ledger entries, request idempotency, corporation-owned wallet schema support via migration `018_phase4_corporate_wallets.sql`, and authoritative corporate asset custody/hangar operations.
- Product-changing choices remain deferred where they alter the intended ownership/membership model.

### Phase 4 verification note
- Backend CI #304: SUCCESS on the latest verified push before the current wallet/asset-operation slice.
- Android CI #34: SUCCESS after the Android bootstrap restoration.
- Migration `016_phase4_social_operations.sql` and lifecycle rules/tests are present.
- Migration `017_phase4_social_integrity.sql` is present for reputation and membership integrity.
- Migration `018_phase4_corporate_wallets.sql` fixes the schema mismatch that previously made corporation wallet creation incompatible with the original player-owned wallet constraint.
- Corporate wallet and asset routes are registered in `main`; wallet transfers use idempotency, deterministic locking, insufficient-funds protection, audit and outbox events.
- New CI verification is required for the current wallet/asset slice.
- Phase 4 remains IN PROGRESS until contract escrow settlement, deeper asset accounting and Android management UI are verified end-to-end.

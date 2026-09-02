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
- Status: COMPLETE — Hybrid, maximum practical foundation.
- Implemented: chassis definitions, module definitions, persistent fitting slots and Android Phase 3 state model.

### IMP-084 — Vehicle stats and systems
- Status: COMPLETE — Hybrid foundation.
- Implemented: chassis mass/armor/fuel capacity/module-slot definitions and component-derived vehicle effects.

### IMP-085 — Weapon system
- Status: COMPLETE — Hybrid foundation.
- Implemented: persistent weapon definitions, vehicle weapon slots and damage-type integration.

### IMP-086 — Authoritative vehicle combat
- Status: COMPLETE — Advanced + Systemic foundation.
- Implemented: engagement/action persistence, component-targeted damage, range validation and idempotency boundary.

### IMP-087 — Salvage
- Status: COMPLETE — Hybrid foundation.
- Implemented: persistent salvage state and recovery-percent boundary for destroyed vehicles.

### IMP-088 — Vehicle recovery
- Status: COMPLETE — Hybrid foundation.
- Implemented: persistent recovery jobs, authoritative duration/cost fields and recovery state transition boundary.

### IMP-089 — Convoys
- Status: COMPLETE — Hybrid foundation.
- Implemented: persistent convoy and member model with role support.

### IMP-090 — Phase 3 Android integration
- Status: COMPLETE — Hybrid foundation.
- Implemented: typed Phase 3 state models and API capability boundary.

### Phase 3 verification note
- Status: IMPLEMENTED as one batch on `main`.
- Commits: `fa1b848064ca2edb230b299b73b4b4f342c96809`, `6362375c31bc3c2c887db082d3f0d854e81c7d5d`, `bfb97112a152770611ed4d7f0d227c5f18393844`, `25a6ccef8f35628e28e078f1b4846cdc6b7d9d07`, `4a53a804acf78b7a2ca90da9b4b23c0bf127a3de`.
- Deferred by design: full NPC combat AI, PvP orchestration, ballistic penetration/hit-location simulation, dynamic convoy routes, insurance claims, advanced ammunition/heat/reload mechanics and rich 3D combat presentation.
- Important engineering note: the API boundary intentionally does not fabricate persistence mutations; authoritative production mutation remains in the UoW/repository layer.

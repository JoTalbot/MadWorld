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

## IMP-078 — Expedition system
- Status: COMPLETE — Advanced + Systemic; maximum-option scope
- Selected by user: `3 + 2`.
- Implementation: persistent server-side expedition jobs; region/distance/risk planning; authoritative duration and fuel consumption; deterministic stored outcomes; deterministic loot and component-aware vehicle damage; guarded time-based completion with exactly-once resolution; completion audit/outbox event; contract progression hook; authenticated/idempotent API; ownership validation for vehicle and inventory; focused domain/application tests; expedition design documentation.
- Verification: PR #8 merged to `main` as merge commit `63c6b60bddd48912801e5edb493721fb83fd06bd`. PR CI #233 passed with 68 tests passed and 0 failures before merge.
- Deferred by design: dynamic world-generated routes, NPC encounters/combat, convoy/group expeditions, weather/disaster modifiers, insurance/recovery and live-economy-driven loot generation.

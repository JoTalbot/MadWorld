# IMP-077 Contract System

Accepted scope: Advanced + Systemic.

The contract system is persistent and authoritative. Contract templates define reusable objectives, prerequisites, deadlines, risk tiers, faction/reputation requirements and deterministic rewards. Contract instances track player progress and lifecycle state.

Objective progress is driven by canonical domain events. Event matching is intentionally data-driven so gathering, crafting, market and expedition outcomes can contribute without coupling contracts to those services.

Reward application is idempotent and performed once when all objectives are complete. Deadlines use the authoritative server clock. Chains are represented by prerequisite contract-template identifiers, allowing future branching without embedding narrative logic in the persistence layer.

Deferred: fully procedural world-generated contracts, complex branching narrative content and live economy-driven contract generation.

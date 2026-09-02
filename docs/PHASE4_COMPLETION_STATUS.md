# Phase 4 completion status

## Current implementation

Phase 4 Social Sandbox has been expanded to the authoritative core needed for a playable social/economic foundation:

- Corporations, roles and permission-gated management.
- Corporation-owned wallets with immutable ledger movements, deterministic locking and idempotent transfers.
- Corporate hangars and asset custody with capacity and optimistic version checks.
- Alliance invitation and membership lifecycle, including decline and membership overview.
- Directed diplomacy with standing and trade/transit controls.
- Social contracts with lifecycle rules and escrow-backed financial settlement.
- Contract completion/refund reputation propagation with immutable history.
- Manufacturers/brands with bounded quality ratings.
- Asset manufacturer provenance binding.
- Android corporation, corporate-wallet and manufacturer management surface.
- Database integrity enforcement for escrow lifecycle and escrow-backed contract state transitions.

## Verification

- Migration chain reached `019_phase4_social_completion.sql` successfully in the last Backend CI run.
- Backend CI run `#323` failed only because the newly added test incorrectly expected Pydantic to enforce a cross-field counterparty invariant that is intentionally enforced at the API boundary. The test has been corrected.
- New Backend CI run `#328` is running against commit `f1c54fd99b038e57324b84bada538d0fc5aa3b8e`.
- New Android CI run `#37` is running against the same commit.
- Migration `020_phase4_contract_integrity.sql` and asset provenance registration are now included in the current branch history.

## Explicit boundary

The following remain outside the Phase 4 social-core completion gate because they change broader game design rather than merely harden the accepted social model:

- Alliance territorial/economic effects.
- World/NPC reputation propagation beyond contract-driven social reputation.
- Rich treasury/reporting screens.
- Full physical vehicle/item ownership transfer semantics.

These are preserved as future product work rather than treated as unfinished correctness work for the Phase 4 social core.

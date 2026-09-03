# MadWorld — B6 Finance & Provenance Status

## Scope

B6 implements the accepted production-batch foundation for secured finance and asset history:

- secured credit agreements with bounded principal, interest, outstanding balance and lifecycle;
- collateral pledges bound to player-owned vehicles;
- repayment with authoritative wallet ledger debit and idempotency;
- deterministic overdue default transition;
- insurance policies with premium debit and bounded coverage/deductible;
- investment/financing records with authoritative principal debit;
- append-only asset provenance history;
- finance event boundary for future recovery/settlement consumers;
- authenticated read surfaces and mutation authorization.

## Authority boundary

- Money is never stored as a mutable balance in B6. Wallet balances remain the sum of authoritative `ledger_entries`.
- Finance contracts record obligations and claims, but do not mint currency.
- Asset collateral and provenance commands require authenticated player ownership of the referenced vehicle asset.
- Mutating commands require `Idempotency-Key` and use the existing transactional idempotency store.
- Important mutations emit audit events and use the existing outbox where downstream processing is required.

## Deferred / explicit follow-up

- automated collateral seizure and liquidation policy;
- insurer underwriting/risk pricing engine;
- secondary-market financing instruments;
- corporate and alliance credit facilities;
- richer asset-quality degradation and manufacturer lifecycle propagation;
- statistical financial abuse scoring and circuit breakers, covered by B8.

These are not silently treated as complete.

## Verification

- Contract coverage is in `backend/tests/test_b6_finance_contract.py`.
- Backend CI must pass on the final B6 head before B6 is declared release-gated complete.

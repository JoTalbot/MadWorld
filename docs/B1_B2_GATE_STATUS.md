# B1/B2 Gate Status

- B1 integration work is implemented on `feat/master-batch-b1-b10`.
- B2 travel state invariants and world/gameplay region binding are implemented.
- B2 LOST travel now authoritatively destroys the linked vehicle, zeroes persisted component condition, and creates an idempotent recovery case in the same transaction.
- B2 recovery claim now locks the recovery case and player wallet, validates the ledger balance, performs an idempotent ledger debit, restores the vehicle to `stored`, repairs persisted component condition to a valid recovered minimum, and marks the case `RECOVERED` in the same transaction.
- Remaining gate items: authoritative encounter→combat damage integration, authoritative cargo-capacity validation, and DB-backed reconnect/retry integration coverage.
- CI must pass on the exact final HEAD before the gate is closed.
- Do not merge PR #14 before exact-HEAD CI verification.

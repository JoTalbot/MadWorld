# B1/B2 Gate Status

- B1 integration work is implemented on `feat/master-batch-b1-b10`.
- B2 travel state invariants and world/gameplay region binding are implemented.
- B2 LOST travel now authoritatively destroys the linked vehicle, zeroes persisted component condition, and creates an idempotent recovery case in the same transaction.
- B2 encounter `LOST` is now an authoritative terminal travel outcome: encounter resolution delegates to the linked travel-loss path on the same DB transaction, so vehicle destruction and recovery creation cannot be detached from the encounter result.
- B2 travel and encounter resolution retries are idempotent for the same terminal outcome and reject conflicting terminal outcomes.
- B2 recovery claim locks the recovery case and player wallet, validates the ledger balance, performs an idempotent ledger debit, restores the vehicle to `stored`, repairs persisted component condition to a valid recovered minimum, and treats an already `RECOVERED` case as an idempotent retry.
- B2 cargo capacity is now authoritative at travel planning time through `vehicles.cargo_capacity`. Migration `028_b2_cargo_capacity.sql` introduces a deterministic 1000-unit baseline without changing existing travel payloads that fit within it.
- Remaining gate item: DB-backed reconnect/retry integration coverage against PostgreSQL, including duplicate terminal requests and the encounter-loss→vehicle-loss→recovery chain.
- CI must pass on the exact final HEAD before the gate is closed.
- Do not merge PR #14 before exact-HEAD CI verification.

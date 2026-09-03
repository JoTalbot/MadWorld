# B1/B2 Gate Status

- B1 integration work is implemented on `feat/master-batch-b1-b10`.
- B2 travel state invariants and world/gameplay region binding are implemented.
- B2 LOST travel now authoritatively destroys the linked vehicle, zeroes persisted component condition, and creates an idempotent recovery case in the same transaction.
- B2 encounter `LOST` is now an authoritative terminal travel outcome: encounter resolution delegates to the linked travel-loss path on the same DB transaction, so vehicle destruction and recovery creation cannot be detached from the encounter result.
- B2 travel and encounter resolution retries are idempotent for the same terminal outcome and reject conflicting terminal outcomes.
- B2 recovery claim locks the recovery case and player wallet, validates the ledger balance, performs an idempotent ledger debit, restores the vehicle to `stored`, repairs persisted component condition to a valid recovered minimum, and treats an already `RECOVERED` case as an idempotent retry.
- B2 cargo capacity is authoritative at travel planning time through `vehicles.cargo_capacity`. Migration `028_b2_cargo_capacity.sql` introduces a deterministic 1000-unit baseline without changing existing travel payloads that fit within it.
- PostgreSQL integration coverage exercises the persisted encounter-loss → travel-loss → vehicle-destruction → recovery chain, duplicate terminal requests, exactly-once recovery debit, and cargo-capacity boundary enforcement.
- Final exact-HEAD CI verification passed on commit `13de09468115b5a24df39bc4a3d992bc7322a57c`: Backend CI run `33704312163` (#424), job `100490053887`, with all migration steps through `028_b2_cargo_capacity.sql` applied and `130 passed, 1 warning in 1.99s`.
- The CI job also verified application module resolution with 87 routes and the required `/api/v1/travel/plan` route.
- Gate status: **GREEN / READY TO MERGE**.
- PR #14 remains open and must not be merged unless explicitly requested.

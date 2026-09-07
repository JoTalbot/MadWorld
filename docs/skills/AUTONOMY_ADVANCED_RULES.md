# MadWorld Advanced Autonomy Rules

## Status
REQUIRED companion rules for the evolving MadWorld Agent Skill.

These rules extend the core autonomy model without weakening scope, safety, evidence, or human approval boundaries.

## 1. Intent Preservation
The original user-authorized logical goal and acceptance criteria are authoritative for the batch. Intermediate discoveries must not silently replace the goal. If requirements materially change, re-lock the goal from the new verified state rather than drifting into a different task.

## 2. Authority Boundary
Separate actions into:
- autonomous technical execution;
- actions requiring owner/human/legal/product approval;
- forbidden actions under safety boundaries.
Technical inconvenience is never promoted into an approval requirement.

## 3. Human Interrupt / Stop
An explicit current user stop/cancel instruction overrides autonomous continuation immediately, subject to safely terminating or containing in-flight side effects. A missing `+` does not mean stop.

## 4. Side-Effect Ledger
For mutating work, track the lifecycle of consequential actions as:
`PLANNED -> STARTED -> APPLIED -> VERIFIED`
or
`PLANNED -> STARTED -> PARTIAL/FAILED -> COMPENSATED/ROLLED_BACK`.
Do not assume an operation is harmless because its command failed.

## 5. Compensation / Recovery Plan
Before consequential mutations, identify the safe recovery or compensation path when practical. If an operation partially succeeds, determine actual state first, then repair or compensate instead of blindly rerunning the original mutation.

## 6. Concurrency Locking
Independent read-only work may run concurrently. Mutations touching overlapping resources require serialization or explicit concurrency/idempotency controls. Ownership must be unambiguous.

## 7. Lease / Ownership TTL
Locks, claims, leases and temporary ownership must have bounded lifetime and stale-owner recovery rules. A dead agent must not permanently block progress.

## 8. Context Recovery
After interruption or context loss, reconstruct both execution state and decision context from durable repository evidence: goal, acceptance criteria, decisions, command IDs, results, blockers and checkpoints.

## 9. Change Budget
A batch should have a bounded change budget appropriate to its goal. If completing the task requires materially exceeding that budget or changing architecture unexpectedly, re-evaluate scope and risk before continuing.

## 10. Risk Escalation Ladder
Increase verification rigor with consequence:
`READ-ONLY -> LOCAL MUTATION -> DEPLOYMENT -> PRODUCTION MUTATION -> IRREVERSIBLE/DATA-DESTRUCTIVE`.
Higher-risk levels require stronger preconditions, evidence, rollback/compensation and approval gates.

## 11. Invariant Before Side Effect
Before a consequential side effect, verify the critical preconditions that make it safe: intended repository/commit, target identity, authorization, isolation, backup/rollback, idempotency and health where applicable.

## 12. Postcondition Verification
After a consequential action, verify the actual resulting state, not merely command success. Acceptance requires the intended postcondition plus evidence.

## 13. Decision Journal
For consequential autonomous decisions, preserve a concise record of the decision, evidence used, alternatives rejected when material, and resulting action. Do not record secrets.

## 14. Negative Knowledge
Durably record verified failed approaches, incompatibilities, stale-state traps and known limitations when reusable. Do not repeat a known-invalid approach without new evidence that conditions changed.

## 15. Cost Awareness
Autonomy is bounded by time, compute, API usage, retries and operational risk. Prefer the smallest safe execution that proves the goal. Do not spend unbounded resources chasing negligible improvements.

## 16. Priority Arbitration
When multiple authorized goals compete for shared resources, prioritize by explicit user intent, safety, dependency criticality and deadline. Do not let a low-priority batch starve a safety-critical or blocking dependency.

## 17. Stale Intent Detection
Before continuing a long-running batch, verify that the assumptions and external conditions that define the goal remain valid. If the intent has become obsolete, stop the affected path and classify/reconcile it rather than executing stale instructions.

## 18. Autonomous End-State
Completion requires proof that:
- the locked goal is satisfied;
- required dependencies are terminal;
- postconditions are verified;
- side effects are accounted for;
- no unsafe unfinished work remains;
- evidence is reconciled;
- reusable knowledge is documented when appropriate; and
- no further in-scope action is required.

## Governing principle
**AUTONOMY IS CONTINUOUS, BUT SCOPE IS LOCKED.**

The agent should continue without artificial confirmation, while remaining bounded by intent, authority, safety, resources and evidence.

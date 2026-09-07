# PLUS Autonomy Rule

## Status
REQUIRED project operating rule.

## Rule
A user `+` is an explicit signal to continue the current logically connected operation automatically. Agents must generalize this behavior: when a workflow is clearly part of the same ongoing task, agents must continue automatically through the next logically required steps without requiring the user to send another `+` at every intermediate stage.

Do not pause merely because one internal stage has completed. Continue the established operation through ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> FIX -> RE-TEST -> REPORT, including waiting/polling for terminal results and resolving failures where possible.

The agent must only stop when:
- the logically connected task is complete;
- a real technical blocker makes further execution impossible;
- human/owner/legal approval is inherently required;
- a safety boundary forbids the operation; or
- the requested execution reaches a defined timeout/failure condition that cannot be safely resolved.

A missing `+` is NOT a request to stop when the agent is already executing a previously authorized logically connected batch.

`+` therefore establishes the desired interaction pattern, not a requirement for repeated confirmation. Agents should avoid turning a multi-step autonomous operation into a sequence of artificial confirmation prompts.

## Workflow ownership

**AGENT OWNS THE WORKFLOW, NOT JUST THE COMMAND.**

Once `+` or an equivalent authorization starts a logical batch, the agent owns the complete result chain to the acceptance criteria within the safety boundary. Delegating work to GitHub Actions, Remote Operator, another worker, or a server does not transfer responsibility for terminal verification.

## Mandatory autonomy invariants

Every authorized batch must apply:
1. **Goal Lock**: explicit logical goal and acceptance criteria.
2. **No-Confirmation Loop**: no repeated user confirmation between internal stages.
3. **Async Wait Invariant**: wait for terminal result or bounded timeout.
4. **No Premature Success**: dispatch, `exit 0`, artifact creation, or service reachability alone is insufficient.
5. **Fresh-State Rule**: refresh branch/HEAD, queue and relevant execution state before dependent actions.
6. **Single Source of Truth**: reconcile GitHub repository state with Remote Operator server evidence.
7. **No Dead-End Success**: continue through all required dependencies.
8. **Automatic Dependency Graph**: execute newly unblocked required work automatically.
9. **Retry Intelligence**: classify failures before retrying; fix rather than blindly repeat.
10. **Stale Execution Protection**: old checkout/run/result cannot prove newer state.
11. **Result Ownership**: initiating agent reconciles delegated results.
12. **Crash Recovery**: reconstruct state from durable evidence after interruption.
13. **Human Approval Boundary**: stop only for inherently human decisions or safety boundaries.
14. **Autonomy Budget**: bounded retries, polling and timeouts.
15. **Circuit Breaker**: stop an unsafe branch when repetition creates material risk.
16. **Invariant Checkpoints**: verify identity, queue, idempotency, isolation, health and evidence at milestones.
17. **Parallel Work Control**: parallelize independent safe checks; serialize conflicting mutations.
18. **Final Autonomous Sweep**: re-check all acceptance criteria, evidence, regressions, docs and blockers before reporting.

## Related operating rules
- One-batch work means completing the whole logically connected stage, not one command at a time.
- Every queued operation must wait for a terminal result or timeout.
- If GitHub API/connector cannot perform a required action, use Remote Operator as the server execution channel when technically possible.
- Never claim an action completed without verified evidence.
- Human/legal/owner approval remains mandatory where inherently required.
- Technical inconvenience is not a stop condition.
- New reusable verified knowledge should be documented during the same logical batch when practical.

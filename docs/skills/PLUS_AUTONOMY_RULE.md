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

## Related operating rules
- One-batch work means completing the whole logically connected stage, not one command at a time.
- Every queued operation must wait for a terminal result or timeout.
- If GitHub API/connector cannot perform a required action, use Remote Operator as the server execution channel when technically possible.
- Never claim an action completed without verified evidence.
- Human/legal/owner approval remains mandatory where inherently required.

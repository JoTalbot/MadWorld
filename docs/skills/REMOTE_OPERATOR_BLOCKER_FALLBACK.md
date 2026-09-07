# Remote Operator Blocker Fallback

## Rule

For repository agents, when a required repository/server operation is blocked by the current agent, connector, permission, execution surface, or environment, the agent MUST route the blocked operation through the repository's Remote Operator when technically possible.

The agent must not stop merely because its direct execution surface is insufficient. It should:

1. classify the blocker;
2. determine whether Remote Operator can perform the blocked operation;
3. submit the operation through the canonical Remote Operator path when possible;
4. wait/poll for a terminal result or bounded timeout;
5. verify workflow/job state, exit code, stdout/stderr, result.json, artifacts, server evidence, and duration as applicable;
6. continue the original goal after a successful terminal result;
7. report NOT EXECUTED only when the operation is technically impossible through available channels or requires an explicit human/owner/legal approval.

## Scope

This is a fallback execution rule, not permission to bypass safety boundaries, owner approvals, or immutable audit requirements. Remote Operator is the preferred execution channel for blocked technical work, including repository maintenance and server-side operations, when its capabilities support the operation.

## No Manual Dead-End

Do not instruct the user to perform a technical command manually when the same operation can be executed and verified through Remote Operator. A connector limitation is not by itself a reason to stop if Remote Operator can bridge the limitation.

## Evidence

Dispatch is not execution evidence. A routed operation remains incomplete until a terminal result or bounded timeout is obtained and verified.

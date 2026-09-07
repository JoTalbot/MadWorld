# MadWorld Agent Skill

**Status:** REQUIRED / EVOLVING  
**Scope:** all AI agents, coding agents, reviewers, operators, and automated workers working on `JoTalbot/MadWorld`.

## 1. Mandatory use

Every new worker/agent MUST read and apply, before making changes:

1. `AGENTS.md`
2. `docs/CHATGPT_AGENT_RULES.md`
3. `docs/REMOTE_OPERATOR.md`
4. `.github/remote-operator/QUEUE.md`
5. this skill: `docs/skills/MADWORLD_AGENT_SKILL.md`

A worker that has not loaded this skill is **NOT READY TO MODIFY THE REPOSITORY**.

The skill is part of the repository's operating contract, not optional onboarding material.

## 2. Evolving project knowledge

This file is a living operational skill. It must become better as the project is worked on.

Whenever an agent discovers experience that is useful beyond the immediate task, the agent MUST capture it in this skill during the same logical work batch whenever practical.

Examples of knowledge worth preserving:

- a failure mode and its verified cause;
- a reliable diagnostic or verification procedure;
- an important repository/server dependency;
- a CI/CD or deployment trap;
- a Remote Operator behavior or limitation;
- a recovery or rollback procedure that was actually verified;
- a test pattern that prevents a previously observed regression;
- a release-gate lesson;
- a security or operational invariant;
- a non-obvious constraint that future agents must know;
- a failed approach that should not be repeated.

Do not record guesses as experience. Record verified facts, evidence, and explicitly marked hypotheses separately.

## 3. Learning loop

For every non-trivial task:

`ANALYZE -> IMPLEMENT -> TEST -> VERIFY -> LEARN -> DOCUMENT -> RE-TEST -> REPORT`

The `LEARN` and `DOCUMENT` stages are mandatory when new reusable knowledge appears.

The agent must ask itself:

- What did we learn?
- Would another agent benefit from knowing this before touching the project?
- Did an unexpected failure reveal a reusable rule?
- Did we discover a better verification method?
- Did an existing rule become obsolete or incomplete?

If yes, update this skill immediately rather than leaving the knowledge only in chat, an issue, or an ephemeral log.

## 4. Safe skill maintenance

- Preserve existing useful knowledge.
- Prefer additive, precise changes over wholesale rewrites.
- Remove or correct obsolete knowledge only when the new fact is verified.
- Never store secrets, credentials, tokens, private keys, cookies, personal data, or sensitive server values.
- Never claim a procedure is verified unless evidence exists.
- Include concise evidence references where useful, such as workflow/run IDs, commit SHAs, filenames, or test names.
- Keep operationally important lessons close to the relevant section.

## 5. Required structure for new lessons

Add reusable lessons under `## 7. Verified Project Lessons` using this format:

### YYYY-MM-DD — Short lesson title

- **Situation:** what happened.
- **Finding:** verified cause or behavior.
- **Rule:** what future agents must do.
- **Verification:** test/run/commit/evidence.
- **Status:** `VERIFIED`, `PARTIALLY VERIFIED`, `NOT VERIFIED`, `FAILED`, or `UNKNOWN`.

If a lesson is only a temporary hypothesis, label it explicitly as such and do not turn it into a mandatory rule until verified.

## 6. New-agent completion requirement

Before declaring a task complete, every agent must:

- confirm that this skill was loaded;
- apply its relevant rules;
- add newly discovered reusable knowledge;
- check whether any existing lesson needs correction;
- leave the repository in a state where the next agent can continue without relying on private chat history.

The repository is the durable memory of the project. Chat is not.

## 7. Verified Project Lessons

### 2026-09-07 — Remote Operator queue must not execute historical orphan PENDING entries

- **Situation:** historical entries in `.github/remote-operator/COMMANDS.txt` remained `PENDING` without corresponding executor state records.
- **Finding:** the executor previously treated an unclaimed `PENDING` record without state as executable, creating a risk of unexpectedly running old commands.
- **Rule:** reconciliation must distinguish fresh pending work from historical/orphaned pending records. Historical queue entries must not be silently rewritten. Queue history remains append-only.
- **Verification:** repository audit, executor review, and reconciliation implementation added on `main` during September 2026 work.
- **Status:** PARTIALLY VERIFIED. The reconciliation audit and executor guard are implemented; server-side E2E verification remains required.

### 2026-09-07 — Server operations require terminal evidence

- **Situation:** Remote Operator jobs can be queued asynchronously.
- **Finding:** workflow dispatch success alone does not prove that the server command succeeded.
- **Rule:** wait for terminal execution state and verify exit code, stdout, stderr, result record/artifact, executor identity, server identity, and duration before declaring the operation successful.
- **Verification:** Remote Operator workflow/result protocol and prior successful E2E runs.
- **Status:** VERIFIED.

### 2026-09-07 — Isolated capacity evidence is not production-scale PASS

- **Situation:** isolated PostgreSQL/API/world-tick capacity and mutation rehearsals produced measured throughput and latency results.
- **Finding:** isolated evidence demonstrates bounded behavior but does not by itself establish a production-equivalent capacity threshold or queue-depth/unbounded-growth gate.
- **Rule:** never convert measured isolated capacity into a production capacity PASS without an explicitly defined and verified production-equivalent threshold and required queue-growth evidence.
- **Verification:** `ops/FINAL_RELEASE_DECISION.md`, capacity rehearsal artifacts and B10 documentation.
- **Status:** VERIFIED.

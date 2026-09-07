#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

required=(
  AGENTS.md
  docs/CHATGPT_AGENT_RULES.md
  docs/REMOTE_OPERATOR.md
  .github/remote-operator/QUEUE.md
  docs/skills/MADWORLD_AGENT_SKILL.md
  docs/skills/PLUS_AUTONOMY_RULE.md
  docs/skills/AUTONOMY_ADVANCED_RULES.md
)

for f in "${required[@]}"; do
  test -f "$f" || { echo "AUTONOMY_MISSING_FILE=$f" >&2; exit 1; }
done

core=(
  'Goal Lock'
  'No-Confirmation Loop'
  'Async Wait Invariant'
  'No Premature Success'
  'Fresh-State Rule'
  'Single Source of Truth'
  'No Dead-End Success'
  'Automatic Dependency Graph'
  'Retry Intelligence'
  'Stale Execution Protection'
  'Result Ownership'
  'Crash Recovery'
  'Human Approval Boundary'
  'Autonomy Budget'
  'Circuit Breaker'
  'Invariant Checkpoints'
  'Parallel Work Control'
  'Final Autonomous Sweep'
  'AGENT OWNS THE WORKFLOW, NOT JUST THE COMMAND.'
)
advanced=(
  'Intent Preservation'
  'Authority Boundary'
  'Human Interrupt / Stop'
  'Side-Effect Ledger'
  'Compensation / Recovery Plan'
  'Concurrency Locking'
  'Lease / Ownership TTL'
  'Context Recovery'
  'Change Budget'
  'Risk Escalation Ladder'
  'Invariant Before Side Effect'
  'Postcondition Verification'
  'Decision Journal'
  'Negative Knowledge'
  'Cost Awareness'
  'Priority Arbitration'
  'Stale Intent Detection'
  'Autonomous End-State'
  'AUTONOMY IS CONTINUOUS, BUT SCOPE IS LOCKED.'
)

for term in "${core[@]}"; do
  grep -Fq "$term" docs/skills/MADWORLD_AGENT_SKILL.md || { echo "AUTONOMY_CORE_MISSING=$term" >&2; exit 1; }
done
for term in "${advanced[@]}"; do
  grep -Fq "$term" docs/skills/AUTONOMY_ADVANCED_RULES.md || { echo "AUTONOMY_ADVANCED_MISSING=$term" >&2; exit 1; }
done

grep -Fq 'docs/skills/AUTONOMY_ADVANCED_RULES.md' AGENTS.md
# The ChatGPT contract must point agents to the same advanced contract.
grep -Fq 'docs/skills/AUTONOMY_ADVANCED_RULES.md' docs/CHATGPT_AGENT_RULES.md

grep -Fq 'wait/poll' docs/skills/PLUS_AUTONOMY_RULE.md

grep -Fq 'terminal result' docs/REMOTE_OPERATOR.md
grep -Fq 'idempotency' .github/remote-operator/QUEUE.md

echo 'autonomy_contract=PASS'
echo 'core_invariants=PASS count=19'
echo 'advanced_invariants=PASS count=19'
echo 'onboarding_alignment=PASS'
echo 'remote_operator_wait_rule=PASS'
echo 'queue_idempotency=PASS'

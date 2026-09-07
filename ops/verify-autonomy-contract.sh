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

require_text() {
  local file="$1"
  local term="$2"
  grep -Fq "$term" "$file" || { echo "AUTONOMY_CONTRACT_MISSING file=$file term=$term" >&2; exit 1; }
}

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
  require_text docs/skills/MADWORLD_AGENT_SKILL.md "$term"
done
for term in "${advanced[@]}"; do
  require_text docs/skills/AUTONOMY_ADVANCED_RULES.md "$term"
done

require_text AGENTS.md 'docs/skills/AUTONOMY_ADVANCED_RULES.md'
require_text docs/CHATGPT_AGENT_RULES.md 'docs/skills/AUTONOMY_ADVANCED_RULES.md'
require_text docs/skills/PLUS_AUTONOMY_RULE.md 'waiting/polling for terminal results'
require_text docs/REMOTE_OPERATOR.md 'terminal result'
require_text .github/remote-operator/QUEUE.md 'idempotency'

echo 'autonomy_contract=PASS'
echo "core_invariants=PASS count=${#core[@]}"
echo "advanced_invariants=PASS count=${#advanced[@]}"
echo 'onboarding_alignment=PASS'
echo 'remote_operator_wait_rule=PASS'
echo 'queue_idempotency=PASS'

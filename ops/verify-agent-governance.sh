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
  docs/DECISION_LOG.md
  docs/RELEASE_EVIDENCE_MATRIX.md
  docs/CHANGE_IMPACT_TEMPLATE.md
)

for f in "${required[@]}"; do
  test -f "$f" || { echo "MISSING_REQUIRED_FILE=$f" >&2; exit 1; }
done

grep -Fq 'docs/skills/MADWORLD_AGENT_SKILL.md' AGENTS.md
grep -Fq 'docs/skills/MADWORLD_AGENT_SKILL.md' docs/CHATGPT_AGENT_RULES.md

# Check the durable skill contract against phrases that are actually normative
# in the current skill. Keep these checks aligned with the skill itself rather
# than historical wording, so governance does not fail on harmless terminology drift.
skill=docs/skills/MADWORLD_AGENT_SKILL.md
required_rules=(
  'Mandatory onboarding'
  'Autonomous one-batch operation'
  'Goal Lock'
  'Async Wait Invariant'
  'No Premature Success'
  'Fresh-State Rule'
  'Single Source of Truth'
  'Retry Intelligence'
  'Crash Recovery'
  'Human Approval Boundary'
  'Circuit Breaker'
  'Final Autonomous Sweep'
  'AGENT OWNS THE WORKFLOW, NOT JUST THE COMMAND.'
  'Advanced autonomy safeguards'
  'Remote Operator'
  'Queue discipline'
  'Evidence and release gates'
  'Production safety'
  'Learning loop'
  'Handoff invariant'
)

for rule in "${required_rules[@]}"; do
  grep -Fq "$rule" "$skill" || { echo "MISSING_GOVERNANCE_RULE=$rule" >&2; exit 1; }
done

echo 'agent_governance_integrity=PASS'
echo 'required_files=PASS'
echo 'onboarding_references=PASS'
echo "governance_rules=PASS count=${#required_rules[@]}"
echo 'safety_stop_rule=PASS'

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
grep -Fq 'DECISION_LOG.md' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'RELEASE_EVIDENCE_MATRIX.md' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'CHANGE_IMPACT_TEMPLATE.md' docs/skills/MADWORLD_AGENT_SKILL.md

grep -Fq 'Every failure must produce' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'Before inventing a solution' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'stop and classify the blocker' docs/skills/MADWORLD_AGENT_SKILL.md

echo 'agent_governance_integrity=PASS'
echo 'required_files=PASS'
echo 'onboarding_references=PASS'
echo 'learning_rules=PASS'
echo 'safety_stop_rule=PASS'

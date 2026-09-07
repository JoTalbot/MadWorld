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

grep -Fq 'Decision Log' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'Evidence Matrix' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'Change Impact Map' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'Rollback knowledge' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'Operational invariants' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'Agent handoff' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'Skill freshness' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'Skill integrity' docs/skills/MADWORLD_AGENT_SKILL.md
grep -Fq 'stop and classify the blocker' docs/skills/MADWORLD_AGENT_SKILL.md

echo 'agent_governance_integrity=PASS'
echo 'required_files=PASS'
echo 'onboarding_references=PASS'
echo 'governance_rules=PASS'
echo 'safety_stop_rule=PASS'

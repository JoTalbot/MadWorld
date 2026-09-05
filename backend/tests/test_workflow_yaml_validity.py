"""Guard: every GitHub Actions workflow must be parseable YAML and every
``run:`` block must be syntactically valid bash.

Background: ``remote-operator.yml`` and ``remote-operator-reusable.yml`` were
merged to ``main`` with heredoc / multiline-literal bodies written at column 0
inside ``run: |`` blocks. GitHub rejected the files as invalid YAML, every run
failed in 0 seconds and the Remote Operator queue silently stopped being
executed. A workflow-only breakage never touched application tests, so nothing
went red. This test closes that gap.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))

# Workflow fixes the bot cannot push live in docs/patches/. While the patch
# file still exists, the corresponding workflows are *expected* to be broken
# (strict xfail). Once the owner applies the patch and deletes it, as
# docs/patches/README.md instructs, the tests must pass.
PENDING_PATCH = ROOT / "docs" / "patches" / "remote-operator-yaml-heredoc-fix.patch"
PENDING_BROKEN = {"remote-operator.yml", "remote-operator-reusable.yml"}


def _is_pending(workflow: Path) -> bool:
    if not PENDING_PATCH.exists() or workflow.name not in PENDING_BROKEN:
        return False
    try:
        yaml.safe_load(workflow.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return True
    return False  # patch already applied but not deleted -> tests must pass


def _params():
    return [
        pytest.param(
            w,
            id=w.name,
            marks=pytest.mark.xfail(
                _is_pending(w), strict=True,
                reason="pending owner-applied docs/patches/remote-operator-yaml-heredoc-fix.patch",
            ),
        )
        for w in WORKFLOWS
    ]


assert WORKFLOWS, "no workflows found - repository layout changed?"


def _iter_run_steps(doc: dict):
    for job_name, job in (doc.get("jobs") or {}).items():
        for index, step in enumerate(job.get("steps") or []):
            run = step.get("run")
            if run:
                yield job_name, step.get("name") or f"step[{index}]", run


@pytest.mark.parametrize("workflow", _params())
def test_workflow_is_valid_yaml(workflow: Path):
    doc = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    assert isinstance(doc, dict), workflow
    # PyYAML parses the bare key ``on`` as boolean True.
    assert True in doc or "on" in doc, f"{workflow.name}: missing 'on' trigger"
    assert doc.get("jobs"), f"{workflow.name}: no jobs"


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")
@pytest.mark.parametrize("workflow", _params())
def test_workflow_run_steps_are_valid_bash(workflow: Path):
    doc = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    for job_name, step_name, run in _iter_run_steps(doc):
        with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as handle:
            handle.write(run)
            path = handle.name
        try:
            result = subprocess.run(
                ["bash", "-n", path], capture_output=True, text=True, check=False
            )
        finally:
            Path(path).unlink(missing_ok=True)
        assert result.returncode == 0, (
            f"{workflow.name} / {job_name} / {step_name}: bash -n failed:\n{result.stderr}"
        )


def test_heredoc_terminators_are_not_at_column_zero_of_yaml():
    """A heredoc terminator at column 0 inside a ``run: |`` block is exactly
    the pattern that broke the Remote Operator workflows."""
    offenders = []
    for workflow in WORKFLOWS:
        if _is_pending(workflow):
            continue
        for lineno, line in enumerate(workflow.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.rstrip()
            if not stripped or stripped.startswith("#"):
                continue
            if not stripped.startswith(" ") and ":" not in stripped:
                offenders.append(f"{workflow.name}:{lineno}: {stripped[:60]}")
    assert not offenders, "column-0 non-key lines inside workflow YAML:\n" + "\n".join(offenders)

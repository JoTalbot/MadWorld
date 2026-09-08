import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "release-gate.yml"
PATCH = ROOT / "docs" / "patches" / "release-gate-android-matrix-hardening.patch"


def test_release_gate_workflow_has_backend_android_and_final_gate():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "backend:" in text
    assert "android:" in text
    assert "android-matrix:" in text
    assert "gate:" in text
    assert "needs: [backend, android, android-matrix]" in text
    assert "pytest backend/tests -q" in text
    assert ":app:testDebugUnitTest" in text
    assert "assembleDebug" in text


def test_release_gate_is_manual_and_main_protected():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "branches: [main]" in text
    assert "madworld-android-release-gate" in text


def test_release_gate_preserves_external_owner_boundary():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "external" in text.lower()
    assert "production" in text.lower()


@pytest.fixture(scope="module")
def hardened_workflow(tmp_path_factory):
    """Validate the deliverable patch without pretending it is live on GitHub.

    While pending, apply it to a disposable copy of the CURRENT workflow. Once
    applied by an owner, remove the patch in that same commit and these guards
    automatically enforce the live workflow. No xfail or stale-patch bypass.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    if PATCH.exists():
        work = tmp_path_factory.mktemp("release-workflow-patch")
        target = work / ".github" / "workflows" / "release-gate.yml"
        target.parent.mkdir(parents=True)
        target.write_text(text, encoding="utf-8")
        for args in (["--check", "--whitespace=error"], ["--whitespace=error"]):
            result = subprocess.run(
                ["git", "apply", *args, str(PATCH)],
                cwd=work, text=True, capture_output=True, check=False,
            )
            assert result.returncode == 0, (
                "Pending release-gate patch is stale or already applied. Refresh it, "
                "or remove it in the commit that applies it.\n" + result.stderr
            )
        text = target.read_text(encoding="utf-8")
    document = yaml.safe_load(text)
    for job in document["jobs"].values():
        for step in job.get("steps", []):
            if "run" in step:
                result = subprocess.run(
                    ["bash", "-n"], input=step["run"], text=True,
                    capture_output=True, check=False,
                )
                assert result.returncode == 0, result.stderr
    return document


def test_hardened_matrix_keeps_every_api_and_required_gate(hardened_workflow):
    jobs = hardened_workflow["jobs"]
    matrix = jobs["android-matrix"]
    assert matrix["strategy"]["matrix"]["api"] == [26, 29, 32, 35]
    assert matrix["strategy"]["fail-fast"] is False
    assert not matrix.get("continue-on-error", False)
    assert jobs["gate"]["needs"] == ["backend", "android", "android-matrix"]
    assert "if" not in jobs["gate"]  # a failing API smoke must still block the gate


def test_hardened_matrix_has_bounded_runner_consumption(hardened_workflow):
    concurrency = hardened_workflow["concurrency"]
    assert "${{ github.ref }}" in concurrency["group"]
    assert "${{ github.workflow }}" in concurrency["group"]
    assert concurrency["cancel-in-progress"] is True
    matrix = hardened_workflow["jobs"]["android-matrix"]
    assert 1 <= matrix["timeout-minutes"] <= 60
    assert 1 <= matrix["strategy"]["max-parallel"] <= 2
    for step in matrix["steps"]:
        if "sdkmanager" in step.get("run", ""):
            assert 1 <= step["timeout-minutes"] <= 10


def test_hardened_workflow_uses_tested_smoke_and_preserves_isolation(hardened_workflow):
    steps = hardened_workflow["jobs"]["android-matrix"]["steps"]
    smoke = next(step for step in steps if "ops/android_emulator_smoke.sh" in step.get("run", ""))
    assert (ROOT / "ops" / "android_emulator_smoke.sh").is_file()
    assert smoke["working-directory"] == "."
    assert 1 <= smoke["timeout-minutes"] <= 15
    assert '"${{ matrix.api }}"' in smoke["run"]
    assert "android/app/build/outputs/apk/debug/app-debug.apk" in smoke["run"]
    assert "$RUNNER_TEMP/android-smoke-${{ matrix.api }}" in smoke["run"]
    assert all("adb wait-for-device" not in step.get("run", "") for step in steps)
    build = next(step for step in steps if ":app:assembleDebug" in step.get("run", ""))
    assert "-PMADWORLD_API_URL=https://example.invalid" in build["run"]


def test_hardened_workflow_uploads_success_and_failure_evidence(hardened_workflow):
    steps = hardened_workflow["jobs"]["android-matrix"]["steps"]
    artifact = next(step for step in steps if step.get("uses", "").startswith("actions/upload-artifact@"))
    assert artifact["if"] == "always()"
    assert artifact["with"]["name"] == "madworld-android-smoke-${{ matrix.api }}"
    assert artifact["with"]["path"] == "${{ runner.temp }}/android-smoke-${{ matrix.api }}/"
    assert artifact["with"]["if-no-files-found"] == "error"

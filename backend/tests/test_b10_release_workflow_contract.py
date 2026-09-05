from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "release-gate.yml"


def test_release_gate_workflow_has_backend_android_and_final_gate():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "backend:" in text
    assert "android:" in text
    assert "gate:" in text
    assert "needs: [backend, android]" in text
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

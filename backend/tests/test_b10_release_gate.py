from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_release_checklist_covers_all_final_gate_domains():
    text = (ROOT / "ops/RELEASE_CHECKLIST.md").read_text()
    required = [
        "Product regression",
        "Technical gate",
        "Operations",
        "Android release matrix",
        "Privacy/legal",
        "Backup creation and restore verification",
        "Rollback procedure",
        "Disaster-recovery procedure",
        "Final sign-off",
    ]
    for marker in required:
        assert marker in text


def test_release_notes_do_not_claim_unverified_external_signoff():
    text = (ROOT / "ops/RELEASE_NOTES_B10.md").read_text()
    assert "must be verified by the release owner" in text
    assert "not inferred from repository code" in text

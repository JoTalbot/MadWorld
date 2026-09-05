"""The committed OpenAPI contract must match the running application.

If this fails after an intentional API change, regenerate with
``python scripts/export_openapi.py`` and review the diff as part of the PR –
that diff is the Android-facing contract change.
"""
import json
from pathlib import Path

from app.main import app

CONTRACT = Path(__file__).resolve().parents[1] / "contracts" / "openapi.json"


def test_openapi_contract_is_committed_and_current() -> None:
    committed = json.loads(CONTRACT.read_text(encoding="utf-8"))
    live = json.loads(json.dumps(app.openapi(), sort_keys=True))
    assert committed == live, "contracts/openapi.json drifted; run python scripts/export_openapi.py and review the diff"


def test_android_critical_paths_are_present() -> None:
    paths = json.loads(CONTRACT.read_text(encoding="utf-8"))["paths"]
    for required in ("/api/v1/sessions", "/api/v1/sessions/current", "/api/v1/players/bootstrap", "/api/v1/players/{player_id}/state", "/health/ready", "/api/v1/travel/plan"):
        assert required in paths, required

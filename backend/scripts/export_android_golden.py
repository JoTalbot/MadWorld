"""Produce golden JSON responses for the Android parser tests.

Runs the real API against PostgreSQL (MADWORLD_DATABASE_URL required), drives a
fresh player through session -> bootstrap -> state/settlement/economy/territory/
world and writes the raw JSON bodies to android/app/src/test/resources/golden/.
Regenerate whenever an Android-facing response shape changes intentionally.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
GOLDEN = ROOT.parent / "android" / "app" / "src" / "test" / "resources" / "golden"


def main() -> int:
    from fastapi.testclient import TestClient

    from app.main import app
    client = TestClient(app)
    handle = f"golden_{uuid4().hex[:8]}"
    session = client.post("/api/v1/sessions", json={"handle": handle}); session.raise_for_status()
    token = session.json()["token"]; player_id = session.json()["player_id"]
    auth = {"Authorization": f"Bearer {token}"}
    boot = client.post("/api/v1/players/bootstrap", json={"player_id": player_id, "character_name": "Golden"}, headers={**auth, "Idempotency-Key": f"golden-{handle}"}); boot.raise_for_status()
    responses = {
        "session_create.json": session.json(),
        "player_bootstrap.json": boot.json(),
        "player_state.json": client.get(f"/api/v1/players/{player_id}/state", headers=auth),
        "settlement.json": client.get("/api/v1/settlement", headers=auth),
        "economy_overview.json": client.get("/api/v1/economy/overview", headers=auth),
        "territory.json": client.get("/api/v1/territory", headers=auth),
        "world_simulation.json": client.get("/api/v1/world-simulation", headers=auth),
    }
    GOLDEN.mkdir(parents=True, exist_ok=True)
    written = []
    for name, value in responses.items():
        if not isinstance(value, dict):
            if value.status_code != 200:
                print(f"skip {name}: HTTP {value.status_code} {value.text[:120]}", file=sys.stderr); continue
            value = value.json()
        (GOLDEN / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"); written.append(name)
    print("wrote", ", ".join(written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Export the OpenAPI contract to backend/contracts/openapi.json.

Run after any intentional API change and commit the result. The test suite fails
when the live schema drifts from the committed file, so the Android client
never silently receives a changed contract.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402

TARGET = ROOT / "contracts" / "openapi.json"


def render() -> str:
    return json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    content = render()
    if "--check" in argv:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != content:
            print(f"{TARGET} is out of date; run: python scripts/export_openapi.py", file=sys.stderr)
            return 1
        print("openapi contract up to date")
        return 0
    TARGET.write_text(content, encoding="utf-8")
    print(f"wrote {TARGET} ({len(json.loads(content)['paths'])} paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

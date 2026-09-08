"""Guard: every Remote Operator workflow-dispatch request must be executable.

Background: ``remote-operator-workflow-dispatch.yml`` parses
``.github/remote-operator/REQUESTS/*.txt`` itself and ``continue``s past any
record it cannot accept -- a malformed ``COMMAND_ID``, an ``INPUTS_JSON`` that
is not a single-line JSON object, or an empty ``command``. The skip is silent:
no state file, no result, no warning. The record simply stays ``PENDING``
forever and looks like a command that is still queued.

Two such records were found on ``main`` on 2026-09-08 and are classified in
``ops/remote-operator/RECONCILIATION.md``. This test mirrors the broker's own
acceptance rules so a *new* unexecutable request fails CI instead of rotting in
the queue.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REQUESTS = ROOT / ".github" / "remote-operator" / "REQUESTS"

# Copied verbatim from the broker.
COMMAND_ID_RE = re.compile(r"cmd-[0-9]{8}-[0-9]{6}-[A-Za-z0-9._-]+")
BLOCK_SPLIT_RE = re.compile(r"(?m)^---\s*$")
DISPATCH_TYPE_RE = re.compile(r"(?m)^TYPE:\s*WORKFLOW_DISPATCH\s*$")
INPUTS_JSON_RE = re.compile(r"(?m)^INPUTS_JSON:\s*(\{.*\})\s*$")

DIRECT_SSH_WORKFLOW = "remote-operator-dispatch.yml"

# Immutable history that predates this guard. Classified in
# ops/remote-operator/RECONCILIATION.md; never rewritten, never re-executed.
LEGACY_MALFORMED_IDS = {
    "cmd-20260907-governance-recheck",
    "cmd-20260907-remote-governance-dispatch",
}
# Records the broker only accepts through its invalid-escape repair fallback.
LEGACY_NON_STRICT_JSON = {
    "cmd-20260907-144100-economy-overview-500-env-discovery",
    "cmd-20260907-172600-cloudflare-access-diagnose",
    "cmd-20260907-150000-dr-isolated-rehearsal-direct-v2",
    "cmd-20260907-144500-dr-isolated-rehearsal-workflow",
}

SECRET_RE = re.compile(
    r"BEGIN [A-Z ]*PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}"
)


def _blocks():
    if not REQUESTS.is_dir():
        pytest.skip("no REQUESTS directory")
    for path in sorted(REQUESTS.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        for index, block in enumerate(BLOCK_SPLIT_RE.split(text)):
            if DISPATCH_TYPE_RE.search(block):
                yield path, index, block


def _field(block: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{key}:\s*(\S+)", block)
    return match.group(1) if match else None


def _command_id(block: str) -> str | None:
    return _field(block, "COMMAND_ID")


ALL_BLOCKS = list(_blocks())


def test_requests_directory_is_not_empty():
    assert ALL_BLOCKS, "no WORKFLOW_DISPATCH request records found"


def test_command_ids_match_the_broker_regex():
    """A record the broker cannot match is skipped forever, silently."""
    offenders = [
        f"{path.name}#{index}: {_command_id(block)!r}"
        for path, index, block in ALL_BLOCKS
        if not COMMAND_ID_RE.fullmatch(_command_id(block) or "")
        and (_command_id(block) or "") not in LEGACY_MALFORMED_IDS
    ]
    assert not offenders, (
        "COMMAND_ID must match cmd-YYYYMMDD-HHMMSS-slug or the broker silently "
        "skips the request:\n" + "\n".join(offenders)
    )


def test_legacy_malformed_allowlist_is_still_accurate():
    """Self-cleaning: drop an ID from the allowlist once it no longer exists."""
    present = {_command_id(block) for _, _, block in ALL_BLOCKS}
    stale = LEGACY_MALFORMED_IDS - present
    assert not stale, f"remove from LEGACY_MALFORMED_IDS, no longer present: {sorted(stale)}"
    for command_id in LEGACY_MALFORMED_IDS:
        assert not COMMAND_ID_RE.fullmatch(command_id), (
            f"{command_id} is now well-formed; remove it from LEGACY_MALFORMED_IDS"
        )


def test_command_ids_are_unique():
    seen: dict[str, str] = {}
    duplicates = []
    for path, index, block in ALL_BLOCKS:
        command_id = _command_id(block)
        location = f"{path.name}#{index}"
        if command_id in seen:
            duplicates.append(f"{command_id}: {seen[command_id]} and {location}")
        seen[command_id] = location
    assert not duplicates, "COMMAND_ID is the idempotency key:\n" + "\n".join(duplicates)


def test_required_fields_are_present():
    missing = [
        f"{path.name}#{index}: {key}"
        for path, index, block in ALL_BLOCKS
        for key in ("STATUS", "WORKFLOW", "REF")
        if _field(block, key) is None
    ]
    assert not missing, "records missing broker-required fields:\n" + "\n".join(missing)


def test_status_and_timeout_values_are_valid():
    allowed = {"PENDING", "CLAIMED", "RUNNING", "DONE", "FAILED", "TIMEOUT",
               "CANCELLED", "INTERRUPTED", "INVALID"}
    problems = []
    for path, index, block in ALL_BLOCKS:
        status = _field(block, "STATUS")
        if status not in allowed:
            problems.append(f"{path.name}#{index}: STATUS={status!r}")
        timeout = _field(block, "TIMEOUT_MINUTES")
        if timeout is not None and not timeout.isdigit():
            problems.append(f"{path.name}#{index}: TIMEOUT_MINUTES={timeout!r}")
    assert not problems, "\n".join(problems)


def test_inputs_json_is_strict_single_line_json():
    problems = []
    for path, index, block in ALL_BLOCKS:
        command_id = _command_id(block)
        match = INPUTS_JSON_RE.search(block)
        if match is None:
            if _field(block, "WORKFLOW") == DIRECT_SSH_WORKFLOW:
                problems.append(f"{path.name}#{index}: {DIRECT_SSH_WORKFLOW} needs INPUTS_JSON")
            continue
        if command_id in LEGACY_NON_STRICT_JSON:
            continue
        try:
            value = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            problems.append(f"{path.name}#{index}: INPUTS_JSON is not strict JSON ({exc})")
            continue
        if not isinstance(value, dict):
            problems.append(f"{path.name}#{index}: INPUTS_JSON must decode to an object")
    assert not problems, "\n".join(problems)


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")
def test_direct_ssh_commands_are_non_empty_and_valid_bash():
    """The payload runs as root on production; a syntax error wastes a whole cycle."""
    problems = []
    for path, index, block in ALL_BLOCKS:
        if _field(block, "WORKFLOW") != DIRECT_SSH_WORKFLOW:
            continue
        match = INPUTS_JSON_RE.search(block)
        if match is None:
            continue
        raw = match.group(1)
        try:
            inputs = json.loads(raw)
        except json.JSONDecodeError:
            # Mirror the broker's escape-repair fallback.
            repaired = re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", raw)
            try:
                inputs = json.loads(repaired)
            except json.JSONDecodeError:
                continue  # already reported by the strict-JSON test
        command = str(inputs.get("command", ""))
        if not command.strip():
            problems.append(f"{path.name}#{index}: empty command input")
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as handle:
            handle.write(command)
            script = handle.name
        try:
            result = subprocess.run(
                ["bash", "-n", script], capture_output=True, text=True, check=False
            )
        finally:
            Path(script).unlink(missing_ok=True)
        if result.returncode != 0:
            problems.append(f"{path.name}#{index}: bash -n failed: {result.stderr.strip()[:200]}")
    assert not problems, "\n".join(problems)


def test_legacy_non_strict_json_allowlist_is_still_accurate():
    """Self-cleaning: an entry that now parses strictly must leave the allowlist."""
    by_id = {_command_id(block): block for _, _, block in ALL_BLOCKS}
    stale = LEGACY_NON_STRICT_JSON - set(by_id)
    assert not stale, f"remove from LEGACY_NON_STRICT_JSON, no longer present: {sorted(stale)}"
    repaired_only = []
    for command_id in LEGACY_NON_STRICT_JSON:
        match = INPUTS_JSON_RE.search(by_id[command_id])
        assert match, f"{command_id}: INPUTS_JSON disappeared; update the allowlist"
        try:
            json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        repaired_only.append(command_id)
    assert not repaired_only, (
        "these now parse as strict JSON; remove them from LEGACY_NON_STRICT_JSON: "
        f"{sorted(repaired_only)}"
    )


def test_requests_contain_no_credential_material():
    offenders = [
        f"{path.name}#{index}"
        for path, index, block in ALL_BLOCKS
        if SECRET_RE.search(block)
    ]
    assert not offenders, f"possible credential material in request records: {offenders}"

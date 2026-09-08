"""Exercise the real smoke shell with fake Android tools, never a real device.

These tests prove timeout/failure/cleanup behavior, NOT Android compatibility.
Real API coverage still requires the release-gate emulator artifacts.
"""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "ops" / "android_emulator_smoke.sh"

FAKE_TOOL = r'''
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

root = Path(os.environ["FAKE_ROOT"])
name = Path(sys.argv[0]).name
args = sys.argv[1:]
scenario = os.environ["FAKE_SCENARIO"]
with (root / "calls.jsonl").open("a") as log:
    log.write(json.dumps([name, *args]) + "\n")

if name == "emulator":
    if args == ["-accel-check"]:
        print("fake acceleration probe")
        sys.exit(int(os.environ.get("FAKE_ACCEL_EXIT", "0")))
    if scenario == "emulator_exits":
        print("fake emulator startup failure", flush=True)
        sys.exit(2)
    (root / "emulator.pid").write_text(str(os.getpid()))
    if scenario == "stubborn_emulator":
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        child = subprocess.Popen([
            sys.executable, "-c",
            "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(60)",
        ])
        (root / "child.pid").write_text(str(child.pid))
    print("fake emulator running", flush=True)
    time.sleep(60)
    sys.exit(0)

if args[:1] == ["devices"]:
    if scenario == "devices_hang":
        time.sleep(60)
    print("List of devices attached")
    if scenario == "occupied" or (root / "emulator.pid").exists():
        print("emulator-5554\tdevice")
    sys.exit(0)

assert args[:2] == ["-s", "emulator-5554"], args
args = args[2:]
if args[:2] == ["shell", "getprop"]:
    if args[2] == "sys.boot_completed":
        if scenario in ("boot_hang", "stubborn_adb"):
            if scenario == "stubborn_adb":
                signal.signal(signal.SIGTERM, signal.SIG_IGN)
            time.sleep(60)
        value = "1"
        if scenario in ("never_boots", "emulator_exits"):
            value = "0"
        if scenario == "boot_not_exactly_one":
            value = "10"
        print(value + "\r")
    else:
        assert args[2] == "ro.build.version.sdk", args
        print("35" if scenario == "wrong_api" else os.environ["FAKE_API"])
elif args[:2] == ["shell", "settings"]:
    if scenario == "settings_fail":
        sys.exit(7)
elif args[:1] == ["install"]:
    if scenario == "install_fail":
        print("INSTALL_FAILED_TEST_ONLY")
        sys.exit(8)
    if scenario == "install_hang":
        time.sleep(60)
    print("Success")
elif args[:3] == ["shell", "am", "start"]:
    if scenario == "launch_fail":
        sys.exit(9)
elif args[:2] == ["shell", "pidof"]:
    if scenario != "no_app_pid":
        print("4321")
elif args[:2] == ["shell", "dumpsys"]:
    print("versionName=0.1.1\nversionCode=2")
elif args[:1] == ["logcat"]:
    (root / "logcat.started").touch()
    if os.environ.get("FAKE_DIAGNOSTIC_HANG") == "1":
        time.sleep(60)
    print("fake logcat")
'''


def _running(pid: int) -> bool:
    try:
        return Path(f"/proc/{pid}/stat").read_text().split()[2] != "Z"
    except FileNotFoundError:
        return False


@pytest.fixture
def smoke(tmp_path: Path):
    tools = tmp_path / "bin"
    tools.mkdir()
    for name in ("adb", "emulator"):
        tool = tools / name
        tool.write_text(f"#!{sys.executable}\n" + FAKE_TOOL)
        tool.chmod(0o755)
    apk = tmp_path / "app with spaces.apk"
    apk.write_bytes(b"fake APK\n")
    artifacts = tmp_path / "artifacts with spaces"

    def run(scenario="success", *, overrides=None, api="26", terminate=False):
        env = {
            **os.environ,
            "PATH": str(tools) + os.pathsep + os.environ["PATH"],
            "FAKE_ROOT": str(tmp_path),
            "FAKE_SCENARIO": scenario,
            "FAKE_API": api,
            "GITHUB_SHA": "test-commit-not-device-evidence",
            "ANDROID_BOOT_TIMEOUT_SECONDS": "2",
            "ANDROID_ADB_TIMEOUT_SECONDS": "1",
            "ANDROID_INSTALL_TIMEOUT_SECONDS": "1",
            "ANDROID_DIAGNOSTIC_TIMEOUT_SECONDS": "1",
            "ANDROID_SMOKE_SECONDS": "1",
            "ANDROID_POLL_SECONDS": "1",
            **(overrides or {}),
        }
        start = time.monotonic()
        proc = subprocess.Popen(
            ["bash", str(SCRIPT), api, str(apk), str(artifacts)],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, start_new_session=True,
        )
        try:
            if terminate:
                marker = "logcat.started" if terminate == "diagnostics" else "emulator.pid"
                deadline = time.monotonic() + 6
                while not (tmp_path / marker).exists():
                    assert proc.poll() is None, "smoke exited before cancellation test"
                    assert time.monotonic() < deadline, f"cancellation marker missing: {marker}"
                    time.sleep(0.01)
                proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate(timeout=12)
            elapsed = time.monotonic() - start
            # Check cleanup before the fixture's emergency teardown can mask a leak.
            for name in ("emulator.pid", "child.pid"):
                pid_file = tmp_path / name
                if pid_file.exists():
                    assert not _running(int(pid_file.read_text())), f"leaked {name}"
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.communicate(timeout=2)
            pid_file = tmp_path / "emulator.pid"
            if pid_file.exists():
                try:
                    os.killpg(int(pid_file.read_text()), signal.SIGKILL)
                except ProcessLookupError:
                    pass
        calls_file = tmp_path / "calls.jsonl"
        calls = [json.loads(line) for line in calls_file.read_text().splitlines()] if calls_file.exists() else []
        result_file = artifacts / "result.txt"
        result = result_file.read_text() if result_file.exists() else ""
        return proc.returncode, result, stdout + stderr, calls, elapsed, artifacts

    return run


def test_script_is_valid_bash():
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


@pytest.mark.parametrize("api", ["26", "29", "32", "35"])
def test_smoke_records_commit_api_apk_and_cleans_up(smoke, api):
    code, result, output, calls, _, artifacts = smoke(api=api)
    assert code == 0, output
    assert "STATUS=PASS\n" in result
    assert "SCOPE=install-launch-only\n" in result
    assert "COMMIT=test-commit-not-device-evidence\n" in result
    assert f"ACTUAL_API={api}\n" in result
    assert "PHASE=complete\n" in result
    assert "APP_PID=4321\n" in result
    assert (artifacts / "apk.sha256").read_text().startswith(hashlib.sha256(b"fake APK\n").hexdigest())
    assert (artifacts / "logcat.txt").is_file()
    assert not any("wait-for-device" in call or "kill-server" in call for call in calls)
    launch = next(call for call in calls if "start" in call)
    assert "com.jotalbot.madworld/.GameActivity" in launch
    manifest = (ROOT / "android/app/src/main/AndroidManifest.xml").read_text()
    assert 'android:name=".GameActivity"' in manifest
    boot_probe = next(i for i, call in enumerate(calls) if "sys.boot_completed" in call)
    settings = next(i for i, call in enumerate(calls) if "settings" in call)
    assert settings > boot_probe


@pytest.mark.parametrize("scenario", ["never_boots", "boot_not_exactly_one", "boot_hang", "stubborn_adb"])
def test_boot_is_bounded_even_with_stuck_adb(smoke, scenario):
    code, result, output, calls, elapsed, artifacts = smoke(scenario)
    assert code == 124, output
    assert "STATUS=TIMEOUT\n" in result
    assert "PHASE=boot\n" in result
    assert "Emulator boot deadline exceeded" in output
    assert not any("install" in call for call in calls)
    assert (artifacts / "emulator.log").is_file()
    assert elapsed < 10


@pytest.mark.parametrize(
    ("scenario", "phase"),
    [
        ("emulator_exits", "boot"), ("wrong_api", "verify-api"),
        ("settings_fail", "configure"), ("install_fail", "install"),
        ("launch_fail", "launch"), ("no_app_pid", "launch"),
    ],
)
def test_smoke_failure_cannot_be_masked_by_later_commands(smoke, scenario, phase):
    code, result, output, calls, _, _ = smoke(scenario)
    assert code != 0, output
    assert "STATUS=FAILED\n" in result
    assert f"PHASE={phase}\n" in result
    assert "=== emulator log tail ===" in output
    if phase in ("boot", "verify-api", "configure"):
        assert not any("install" in call for call in calls)


def test_install_is_bounded(smoke):
    code, result, output, _, elapsed, _ = smoke("install_hang")
    assert code == 124, output
    assert "STATUS=TIMEOUT\n" in result
    assert "PHASE=install\n" in result
    assert elapsed < 10


def test_adb_preflight_is_bounded(smoke):
    code, result, output, calls, elapsed, _ = smoke("devices_hang")
    assert code == 124, output
    assert "PHASE=preflight\n" in result
    assert not any(call[0] == "emulator" for call in calls)
    assert elapsed < 8


@pytest.mark.parametrize("scenario,expected_code", [("success", 0), ("install_fail", 8)])
def test_hung_diagnostics_are_bounded_and_preserve_original_exit(smoke, scenario, expected_code):
    code, result, output, _, elapsed, _ = smoke(scenario, overrides={"FAKE_DIAGNOSTIC_HANG": "1"})
    assert code == expected_code, output
    assert f"EXIT_CODE={expected_code}\n" in result
    assert elapsed < 10


def test_unusable_acceleration_is_an_explicit_software_fallback(smoke):
    code, result, output, calls, _, _ = smoke(overrides={"FAKE_ACCEL_EXIT": "1"})
    assert code == 0, output
    assert "ACCELERATION=off\n" in result
    emulator = next(call for call in calls if "-avd" in call)
    assert emulator[emulator.index("-accel") + 1] == "off"


def test_existing_emulator_is_never_reused_or_stopped(smoke):
    code, result, output, calls, _, _ = smoke("occupied")
    assert code == 1, output
    assert "refusing to reuse" in output
    assert "PHASE=preflight\n" in result
    assert all(call[0:2] == ["adb", "devices"] for call in calls)


def test_cleanup_kills_only_owned_emulator_group_including_stubborn_children(smoke):
    code, result, output, _, _, _ = smoke("stubborn_emulator")
    assert code == 0, output  # fixture verifies both recorded PIDs have exited
    assert "STATUS=PASS\n" in result


def test_cancellation_has_terminal_evidence_and_stops_emulator(smoke):
    code, result, output, calls, elapsed, _ = smoke("never_boots", terminate=True)
    assert code == 143, output
    assert "STATUS=CANCELLED\n" in result
    assert not any("logcat" in call for call in calls)
    assert elapsed < 8


def test_cancellation_during_cleanup_does_not_report_pass(smoke):
    code, result, output, _, elapsed, _ = smoke(
        overrides={"FAKE_DIAGNOSTIC_HANG": "1"}, terminate="diagnostics",
    )
    assert code == 143, output
    assert "STATUS=CANCELLED\n" in result
    assert "STATUS=PASS\n" not in result
    assert elapsed < 10


@pytest.mark.parametrize("value", ["0", "-1", "x", "1;exit 0"])
def test_invalid_timeouts_fail_before_starting_tools(smoke, value):
    code, _, output, calls, _, _ = smoke(overrides={"ANDROID_BOOT_TIMEOUT_SECONDS": value})
    assert code == 2, output
    assert calls == []

#!/usr/bin/env bash
# Runner-local install/launch smoke only. This does not validate login/gameplay.
# Usage: bash ops/android_emulator_smoke.sh API APK ARTIFACT_DIR
set -Eeuo pipefail

if [[ $# -ne 3 || ! $1 =~ ^[0-9]+$ || ! -f $2 || ! -s $2 ]]; then
  echo 'Usage: android_emulator_smoke.sh API APK ARTIFACT_DIR (existing non-empty APK)' >&2
  exit 2
fi
api="$1"
apk="$2"
artifacts="$3"
serial=emulator-5554
package=com.jotalbot.madworld
boot_timeout="${ANDROID_BOOT_TIMEOUT_SECONDS:-420}"
adb_timeout="${ANDROID_ADB_TIMEOUT_SECONDS:-20}"
install_timeout="${ANDROID_INSTALL_TIMEOUT_SECONDS:-120}"
diagnostic_timeout="${ANDROID_DIAGNOSTIC_TIMEOUT_SECONDS:-10}"
smoke_seconds="${ANDROID_SMOKE_SECONDS:-5}"
poll_seconds="${ANDROID_POLL_SECONDS:-2}"
for value in "$boot_timeout" "$adb_timeout" "$install_timeout" "$diagnostic_timeout" "$smoke_seconds" "$poll_seconds"; do
  if [[ ! $value =~ ^[1-9][0-9]*$ ]]; then
    echo 'All timeout/poll settings must be positive integer seconds.' >&2
    exit 2
  fi
done
for tool in adb emulator timeout setsid; do
  command -v "$tool" >/dev/null || { echo "Missing required tool: $tool" >&2; exit 2; }
done

mkdir -p "$artifacts"
result="$artifacts/result.txt"
phase=preflight
emulator_pid=''
started=$SECONDS
printf 'SCOPE=install-launch-only\nCOMMIT=%s\nEXPECTED_API=%s\nSERIAL=%s\nSTARTED_AT=%s\n' \
  "${GITHUB_SHA:-unknown}" "$api" "$serial" "$(date -u +%FT%TZ)" >"$result"

fail() {
  echo "$*" >&2
  exit 1
}

adb_command() {
  timeout --kill-after=2 "$adb_timeout" adb -s "$serial" "$@" 2>>"$artifacts/adb-errors.log"
}

cleanup() {
  local code=$?
  trap - EXIT
  # Finish cleanup on interruption, but never turn a cancellation during
  # diagnostics into a successful result captured before the signal arrived.
  trap 'code=130' INT
  trap 'code=143' TERM
  set +e
  # On cancellation, release the emulator immediately rather than spending the
  # runner's cancellation grace period on diagnostics. Never kill a shared adb
  # server or an emulator that was not started by this invocation.
  if [[ $code -ne 130 && $code -ne 143 ]]; then
    timeout --kill-after=2 "$diagnostic_timeout" adb devices -l >"$artifacts/devices.txt" 2>&1
    if [[ -n $emulator_pid && $code -ne 130 && $code -ne 143 ]]; then
      timeout --kill-after=2 "$diagnostic_timeout" adb -s "$serial" logcat -d -t 200 >"$artifacts/logcat.txt" 2>&1
    fi
  fi
  if [[ -n $emulator_pid ]]; then
    # setsid gives this invocation its own process group, including qemu children.
    kill -TERM -- "-$emulator_pid" 2>/dev/null
    for _ in 1 2; do
      kill -0 "$emulator_pid" 2>/dev/null || break
      sleep 1
    done
    kill -KILL -- "-$emulator_pid" 2>/dev/null
    wait "$emulator_pid" 2>/dev/null
  fi
  if [[ $code -ne 0 && -f $artifacts/emulator.log ]]; then
    echo '=== emulator log tail ===' >&2
    tail -n 80 "$artifacts/emulator.log" >&2
  fi
  local status=FAILED
  case "$code" in
    0) status=PASS ;;
    124) status=TIMEOUT ;; # 137 alone could also be OOM/SIGKILL; do not assume timeout.
    130|143) status=CANCELLED ;;
  esac
  printf 'STATUS=%s\nPHASE=%s\nEXIT_CODE=%s\nDURATION_SECONDS=%s\nFINISHED_AT=%s\n' \
    "$status" "$phase" "$code" "$((SECONDS - started))" "$(date -u +%FT%TZ)" >>"$result"
  cat "$result"
  exit "$code"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
sha256sum -- "$apk" >"$artifacts/apk.sha256"

# Fail closed rather than installing on an emulator owned by another invocation.
timeout --kill-after=2 "$adb_timeout" adb devices >"$artifacts/devices-before.txt" 2>&1
if grep -qE "^${serial}[[:space:]]" "$artifacts/devices-before.txt"; then
  fail "$serial already exists; refusing to reuse it."
fi

# Device-node existence alone does not prove KVM is usable by the runner user.
acceleration=off
if timeout --kill-after=2 "$adb_timeout" emulator -accel-check >"$artifacts/acceleration.log" 2>&1; then
  acceleration=on
fi
printf 'ACCELERATION=%s\n' "$acceleration" >>"$result"
phase=boot
setsid emulator -avd "madworld-api-$api" -port 5554 -accel "$acceleration" \
  -no-window -no-audio -no-boot-anim -no-snapshot -no-metrics \
  -gpu swiftshader_indirect >"$artifacts/emulator.log" 2>&1 &
emulator_pid=$!

# No unbounded `adb wait-for-device`: every probe shares one boot deadline,
# including offline adb, a dead emulator, and a stuck adb child process.
deadline=$((SECONDS + boot_timeout))
while true; do
  kill -0 "$emulator_pid" 2>/dev/null || fail 'Emulator exited before boot completed.'
  remaining=$((deadline - SECONDS))
  if (( remaining <= 0 )); then
    echo "Emulator boot deadline exceeded (${boot_timeout}s)." >&2
    exit 124
  fi
  probe_timeout=$adb_timeout
  (( probe_timeout <= remaining )) || probe_timeout=$remaining
  if boot_state="$(timeout --kill-after=2 "$probe_timeout" adb -s "$serial" shell getprop sys.boot_completed 2>>"$artifacts/adb-errors.log")"; then
    [[ ${boot_state//$'\r'/} != 1 ]] || break
  fi
  remaining=$((deadline - SECONDS))
  if (( remaining > 0 )); then
    pause=$poll_seconds
    (( pause <= remaining )) || pause=$remaining
    sleep "$pause"
  fi
done
kill -0 "$emulator_pid" 2>/dev/null || fail 'Emulator exited after boot.'

phase=verify-api
actual_api="$(adb_command shell getprop ro.build.version.sdk)"
actual_api="${actual_api//$'\r'/}"
printf 'ACTUAL_API=%s\n' "$actual_api" >>"$result"
[[ $actual_api == "$api" ]] || fail "Wrong Android API: expected $api, got $actual_api."

phase=configure
# System services must be ready before settings/input commands are attempted.
adb_command shell settings put global window_animation_scale 0
adb_command shell settings put global transition_animation_scale 0
adb_command shell settings put global animator_duration_scale 0
adb_command shell input keyevent 82

phase=install
timeout --kill-after=2 "$install_timeout" adb -s "$serial" install -r "$apk" >"$artifacts/install.log" 2>&1
phase=launch
adb_command shell am force-stop "$package"
adb_command shell am start -W -n "$package/.GameActivity" >"$artifacts/launch.log"
sleep "$smoke_seconds"
kill -0 "$emulator_pid" 2>/dev/null || fail 'Emulator exited during launch smoke.'
app_pid="$(adb_command shell pidof "$package")"
[[ -n ${app_pid//[[:space:]]/} ]] || fail 'Application has no running process.'
printf 'APP_PID=%s\n' "$app_pid" >>"$result"
adb_command shell dumpsys package "$package" >"$artifacts/package.txt"
grep -E 'versionName|versionCode' "$artifacts/package.txt"
phase=complete

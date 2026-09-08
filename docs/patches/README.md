# Workflow patches

The Arena/GitHub App connection cannot modify `.github/workflows/*` — a push
containing a workflow file is rejected with
`refusing to allow a GitHub App to create or update workflow ... without
workflows permission`. Workflow changes produced by an agent are therefore
stored here as patches and applied by an account that holds the `workflows`
permission. Do not put credentials in the repository or chat.

Apply from the repository root:

```bash
git apply --check docs/patches/<name>.patch
git apply docs/patches/<name>.patch
```

Remove a patch **in the same commit that applies its workflow changes** (git
history retains the patch for audit). Pending-patch guards must fail when a
patch is stale/already applied, never silently xfail a broken live workflow.

## Previously applied and retired patches (2026-09-08)

| Patch | Applied by (on `main`) | Notes |
|---|---|---|
| `remote-operator-yaml-heredoc-fix.patch` | commit `7190ccd` (2026-09-08) | Heredoc indentation of `.github/workflows/remote-operator.yml` repaired; 15/15 workflows parse at `6ec1c4b`. Guard `backend/tests/test_workflow_yaml_validity.py` is now hard-enforcing (pending-patch xfail machinery removed in PR #23). |
| `backend-ci-quality-gates.patch` | commit `406caa1` (2026-09-08) | Backend CI ruff/mypy/OpenAPI gates restored. |
| `android-ci-gradle-version-from-wrapper.patch` | commit `7373351` (2026-09-08) | Android CI resolves the Gradle version from `gradle-wrapper.properties`. |

New workflow fixes must ship as fresh patches against current `HEAD`; always
verify `git apply --check` before publishing. See
`docs/skills/MADWORLD_AGENT_SKILL.md`, lessons L7–L8.

## release-gate-android-matrix-hardening.patch — refreshed 2026-09-08

**Status: NOT APPLIED on `main` at `df787dc`. Apply before another Release Gate.**

The previous patch bounded only the boot body: its failure diagnostics still
had an unbounded `adb devices`, and the nested `bash -c` did not enable
`errexit`. The live workflow still waits indefinitely at `adb wait-for-device`
before reaching its timeout. Four pre-fix Release Gate runs were observed
stalled at `Boot emulator` while new exact-head CI remained queued. The
emulator startup cause itself is NOT established from job status alone.

The refreshed patch depends on **`ops/android_emulator_smoke.sh` from this
change**; merge/apply the helper, tests and workflow together. It preserves all
four APIs and the final gate's required dependencies:

- per-ref Release Gate concurrency with cancellation of superseded candidates;
- matrix `max-parallel: 2`, a 45-minute job limit, SDK setup limited to 10
  minutes and smoke limited to 15 minutes;
- runner-local KVM access setup; acceleration selected by a bounded
  `emulator -accel-check`, not just the existence of `/dev/kvm`;
- one boot deadline (420 seconds), bounded adb probes/install/diagnostics,
  failure propagation, exact boot/API checks, and owned-process-group cleanup;
- success **and** failure artifacts `madworld-android-smoke-{API}`, containing
  commit/API/APK digest, terminal result, emulator/adb/logcat/package logs;
- no production API calls: the smoke APK still uses `https://example.invalid`.

`backend/tests/test_android_emulator_smoke.py` exercises the actual shell with
fake Android executables. `test_b10_release_workflow_contract.py` applies the
pending patch to a disposable copy of the **current** workflow, validates YAML
and shell syntax, and enforces the resource/evidence/gate contracts. Once the
patch is removed, those same guards enforce the live workflow. These tests do
**not** provide real Android device/emulator evidence.

### Apply with an account permitted to update workflows

On the working branch containing the helper and tests:

```bash
git apply --check --whitespace=error docs/patches/release-gate-android-matrix-hardening.patch
git apply docs/patches/release-gate-android-matrix-hardening.patch
git rm docs/patches/release-gate-android-matrix-hardening.patch
# Run from the repository root with backend test dependencies installed:
PYTHONPATH=backend python -m pytest backend/tests/test_b10_release_workflow_contract.py backend/tests/test_workflow_yaml_validity.py backend/tests/test_android_emulator_smoke.py -q
```

Commit the workflow change and patch deletion together on the same working
branch, then merge via PR. Recheck `main`/queue state first if it has advanced.
The owner completed stale-run cancellation on 2026-09-08: at 14:17 UTC GitHub
reported no queued/in-progress/waiting runs, all four old Release Gates and all
16 hung emulator jobs were terminal CANCELLED. **That handoff step is closed.**
The agent's earlier `actions: write` denial is not a reason to ask the owner to
repeat a cancellation already verified. Recheck fresh state before any retry.

Workflow definitions remain active: cancellation did not disable schedules or
apply this patch. Resume only the safe Backend CI / Agent Governance PR checks
until an authorized account applies/removes the patch. Do not manually restart
the old Release Gate or the broker to work around the missing workflow change.
After application, allow **one** Release Gate on the applied exact head and
collect all terminal jobs/artifacts before updating release status. The new
concurrency rule does not retroactively cancel earlier ungrouped runs.
See `ops/B10_ANDROID_MATRIX_RECOVERY_2026-09-08.md` for the checkpoint.

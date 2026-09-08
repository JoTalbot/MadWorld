# Workflow patches

The Arena/GitHub App connection cannot modify `.github/workflows/*` — a push
containing a workflow file is rejected with
`refusing to allow a GitHub App to create or update workflow ... without
workflows permission`. Workflow changes produced by an agent are therefore
stored here as patches and applied by an account that holds the `workflows`
permission.

Apply from the repository root:

```bash
git apply docs/patches/<name>.patch
```

Delete a patch once it has been applied and merged (git history retains the
patch content for audit).

## Status (2026-09-08): all previously published patches are APPLIED and removed

| Patch | Applied by (on `main`) | Notes |
|---|---|---|
| `remote-operator-yaml-heredoc-fix.patch` | commit `7190ccd` (2026-09-08) | Heredoc indentation of `.github/workflows/remote-operator.yml` repaired; 15/15 workflows parse at `6ec1c4b`. Guard `backend/tests/test_workflow_yaml_validity.py` is now hard-enforcing (pending-patch xfail machinery removed in PR #23). |
| `backend-ci-quality-gates.patch` | commit `406caa1` (2026-09-08) | Backend CI ruff/mypy/OpenAPI gates restored. |
| `android-ci-gradle-version-from-wrapper.patch` | commit `7373351` (2026-09-08) | Android CI resolves the Gradle version from `gradle-wrapper.properties`. |

New workflow fixes must ship as fresh patches against current `HEAD`; always
verify `git apply --check` before publishing and keep `backend/tests/test_workflow_yaml_validity.py`
consistent with the patch lifecycle (see `docs/skills/MADWORLD_AGENT_SKILL.md`
lesson L7).

## release-gate-android-matrix-hardening.patch — NEW (2026-09-08), awaiting apply

**Status: NOT APPLIED on `main` — recommended before the next Release Gate run.**

Observed (first-ever `android-matrix` executions, runs `34210345974`/`34210347665`
on pre-fix `main`): all four "Android API {26,29,32,35} smoke" jobs hung in the
"Boot emulator" step for 2.5+ hours with no step transition and no `updated_at`
activity (8/8 jobs), while the job has no `timeout-minutes` — a hung boot blocks
the runner until the default 6-hour job timeout and starves the account's CI
(the repository's own Backend CI/Governance runs queued behind them).

The patch hardens `release-gate.yml` without changing gate semantics:
- `android-matrix` job gets `timeout-minutes: 60`;
- "Boot emulator" enables acceleration only when `/dev/kvm` exists, otherwise
  falls back to `-accel off` (no silent emulator exit);
- the whole boot sequence is bounded by `timeout 420`; on failure the step
  prints the emulator log tail, `adb devices` and the emulator process state
  before exiting non-zero (the existing failure artifact step then uploads the
  emulator log for diagnosis).

Validated before publishing: `git apply --check` passes at current `HEAD`
(`6ec1c4b`); patched file parses as YAML; every `run:` block passes `bash -n`;
no column-0 non-key lines (the `backend/tests/test_workflow_yaml_validity.py`
guard stays green before and after apply).

Apply and push from an account/token that holds the `workflows` permission:

```bash
git apply docs/patches/release-gate-android-matrix-hardening.patch
```

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

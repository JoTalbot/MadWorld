# Workflow patches

The Arena GitHub connection cannot modify `.github/workflows/*`. Workflow changes produced by the agent are stored here as patches. Apply from the repository root:

```bash
git apply docs/patches/android-ci-gradle-version-from-wrapper.patch
git apply docs/patches/backend-ci-quality-gates.patch
git apply docs/patches/remote-operator-yaml-heredoc-fix.patch
```

Delete a patch once it has been applied and merged.

## remote-operator-yaml-heredoc-fix.patch

**Status: NOT APPLIED on `main` — still required (refreshed 2026-09-08, applies cleanly to `fe0d939`).**

`.github/workflows/remote-operator.yml` (the documented Universal Remote Operator SSH bridge) is
**invalid YAML on `main`**: the `<<'PY'` heredoc body and its terminator sit at column 0 inside a
`run: |` block scalar, so the block scalar ends prematurely at line 154.

Consequence, verified on live runs: GitHub cannot parse the file, so **every push to any branch creates a
zero-job startup-failure run** for it (`34173064477`, `34172246211`, `34172087599`, ...), and the workflow
cannot be dispatched at all — the documented `remote-operator.yml` SSH path in `docs/REMOTE_OPERATOR.md`
is dead. The sibling `remote-operator-reusable.yml` was already repaired, so this patch now only touches
`remote-operator.yml`.

The patch indents lines 154-158 to the block-scalar level. Because `run: |` strips the common
indentation, the executed bash is byte-identical to what was intended and the heredoc terminator `PY`
still lands at column 0 of the rendered script.

Verified before publishing the patch:
- PyYAML parses the patched file (`name`, `on: [workflow_dispatch]`, `jobs: [remote]` all resolve);
- `bash -n` passes for all three `run` steps;
- the rendered script still contains `^PY$` at column 0;
- the embedded Python body compiles.

Apply and push from an account/token that holds the `workflows` permission:

```bash
git apply docs/patches/remote-operator-yaml-heredoc-fix.patch
```

Arena/GitHub App tokens cannot push this file — the push is rejected with
`refusing to allow a GitHub App to create or update workflow .github/workflows/remote-operator.yml
without workflows permission`, which is why the fix is shipped as a patch instead of a commit.

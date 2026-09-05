# Workflow patches

The Arena GitHub connection cannot modify `.github/workflows/*`. Workflow changes produced by the agent are stored here as patches. Apply from the repository root:

```bash
git apply docs/patches/android-ci-gradle-version-from-wrapper.patch
git apply docs/patches/backend-ci-quality-gates.patch
git apply docs/patches/remote-operator-yaml-heredoc-fix.patch
```

Delete a patch once it has been applied and merged.

## remote-operator-yaml-heredoc-fix.patch

Fixes `remote-operator.yml` and `remote-operator-reusable.yml`, which are currently invalid YAML on `main`
(every run fails in 0s with "workflow file issue"). The `<<'PY'` heredoc body and the multiline
`command_text='...'` literal were written at column 0 inside `run: |` blocks; the patch indents them
to the block-scalar level. Because `run: |` strips the common indentation, the executed bash script is
byte-identical to what was intended (heredoc terminator `PY` still lands at column 0).
Verified: PyYAML parse OK, `bash -n` OK for every `run` step.

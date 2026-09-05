# Workflow patches

The Arena GitHub connection cannot modify `.github/workflows/*`. Workflow changes produced by the agent are stored here as patches. Apply from the repository root:

```bash
git apply docs/patches/android-ci-gradle-version-from-wrapper.patch
git apply docs/patches/backend-ci-ruff.patch
```

Delete a patch once it has been applied and merged.

# B10 Android Matrix Recovery — 2026-09-08

## Checkpoint / goal lock

- **STATUS: PARTIALLY VERIFIED.** Repository hardening is tested locally; the
  workflow patch is NOT APPLIED and real Android matrix execution is NOT VERIFIED.
- Repository: `JoTalbot/MadWorld`.
- Working branch: `arena/01a080ed-madworld`.
- Base/main at recovery: `df787dca3dd25bdb50041237c6d24d48ee58e480`
  (PR #23 merged at 11:23:51 UTC).
- Goal: continue B10 CI recovery by bounding Android smoke execution, preserving
  required APIs/gate semantics, and leaving actionable failure evidence.
- Acceptance: no unbounded adb/boot/diagnostic waits; owned emulator cleanup;
  failure cannot become PASS; patch applies to current workflow and remains
  guarded after application; distinguish local tests from real Android evidence.
- Scope excludes production operations, release publication, gameplay changes,
  database changes and replay of historical Remote Operator requests.

## GitHub evidence (observed 2026-09-08 12:23 UTC)

| Run | Revision | Observed state |
|---|---|---|
| [34210293609](https://github.com/JoTalbot/MadWorld/actions/runs/34210293609) | `0542950` | IN_PROGRESS; all four API smoke jobs at `Boot emulator`; backend FAILED |
| [34210312794](https://github.com/JoTalbot/MadWorld/actions/runs/34210312794) | `0542950` | IN_PROGRESS; all four API smoke jobs at `Boot emulator`; backend FAILED |
| [34210345974](https://github.com/JoTalbot/MadWorld/actions/runs/34210345974) | `406caa1` | IN_PROGRESS; all four API smoke jobs at `Boot emulator`; backend FAILED |
| [34210347665](https://github.com/JoTalbot/MadWorld/actions/runs/34210347665) | `406caa1` | IN_PROGRESS; all four API smoke jobs at `Boot emulator`; backend FAILED |
| [34220470032](https://github.com/JoTalbot/MadWorld/actions/runs/34220470032) | `df787dc` | Backend CI QUEUED, no terminal result |
| [34220470103](https://github.com/JoTalbot/MadWorld/actions/runs/34220470103) | `df787dc` | Release Gate QUEUED, no terminal result |

All four old runs' Android build jobs succeeded, but their old backend failure
prevents release acceptance. These are not evidence for `df787dc` or this change.
The live workflow places `adb wait-for-device` outside its timeout. This is a
verified unbounded-wait defect; the underlying emulator startup failure is
**UNKNOWN** until actual emulator logs establish it. KVM failure is not assumed.

A single cancellation attempt for `34210345974` returned **HTTP 403, Resource
not accessible by integration**. It had no effect: the run was still IN_PROGRESS
on recheck. No blind retries, extra Release Gate dispatches, queue entries,
server commands or production side effects were performed.

## Repository changes

- `ops/android_emulator_smoke.sh`: runner-local boot/install/launch helper;
  bounded acceleration check, one 420-second boot deadline, bounded adb,
  installation and diagnostics, exact boot/API checks, API/APK/commit metadata,
  explicit terminal status and cleanup of only its own emulator process group.
- Refreshed `docs/patches/release-gate-android-matrix-hardening.patch`: per-ref
  concurrency, two parallel matrix jobs, job/step timeouts, KVM access on the
  GitHub-hosted runner, tested helper, success/failure artifacts. All API levels
  `[26, 29, 32, 35]` and final gate dependencies remain required.
- 28 fake-tool behavioral tests cover success, stuck/offline adb, false readiness,
  early emulator death, wrong API, configuration/install/launch failure, empty
  app PID, stuck diagnostics, software fallback, cancellation and process cleanup.
- Four additional workflow contract tests validate the pending patch against the
  current source. They enforce the live workflow once the patch is applied and
  removed; stale patches fail rather than xfail/hide errors.

The smoke APK still targets `https://example.invalid`. **Install/launch smoke
is not login, gameplay, offline/reconnect or physical-device validation.** Fake
Android tools are test fixtures only; their PASS records are never device evidence.

## Initial local verification (before PostgreSQL continuation)

- Full backend suite after the cancellation-during-cleanup fix:
  **256 passed, 25 skipped**. Skips require PostgreSQL;
  `MADWORLD_DATABASE_URL` is not configured in this sandbox. One upstream
  Starlette/AnyIO deprecation warning; no test failure.
- Ruff: PASS. Mypy: PASS (38 source files).
- OpenAPI contract check: PASS; application contract unchanged.
- ShellCheck 0.11.0 / `bash -n`: PASS for the helper.
- Workflow/patch syntax and contract tests: **38 passed** (including all 15
  existing workflows); strict patch application check: PASS. The same 38 checks
  also passed on a disposable copy with the patch applied and removed, proving
  that the guards continue enforcing the owner-applied workflow.
- Agent governance and autonomy contract scripts: PASS.
- Runtime Android SDK/emulator/device checks: **NOT EXECUTED** in this sandbox.
- Exact-head GitHub Backend CI/Release Gate: **NOT VERIFIED**, as above.

Generated local logs and the sanitized Actions snapshot are under the ignored
`artifacts/b10-android-matrix-recovery/`; durable run links and results are above.

## Side-effect ledger / blocker / next safe action

1. Source/helper/tests/docs: APPLIED and locally VERIFIED on the working branch.
2. Cancel stale Actions run: ATTEMPTED, permission denied, NOT APPLIED.
3. Workflow on `main`: NOT APPLIED. The documented GitHub App connection lacks
   workflow-write permission; use the sanctioned patch process, not a bypass.
4. Server / database / Remote Operator queue / release tag: NOT TOUCHED.

An account with workflow-update permission must apply the refreshed patch on
this working branch **together with the helper/tests** and remove the patch in
that same commit. Exact commands are in `docs/patches/README.md`. An
Actions-authorized owner must recheck and cancel the stale runs (including any
still-queued old candidates) before allowing one exact-head Release Gate on the
applied revision. Do not cancel unrelated workflows or rerun stale checkouts.
The concurrency change does not retroactively cancel older ungrouped runs.

Collect terminal results and `madworld-android-smoke-{26,29,32,35}` artifacts,
verify each result's commit/API/APK digest, then update the relevant gate only
for what was actually exercised. Until then Android API 26/29–32 and final
release acceptance remain open. Capacity, rollback and legal/publication gates
are unchanged by this CI-only batch.

## Continuation — real PostgreSQL verification, 2026-09-08 13:45 UTC

The local database gap above is now closed for the tested application commit
`879faa4`: **281 tests passed with zero skips** on an isolated native PostgreSQL
16.2 instance with genuine `pgcrypto` 1.3. All **43** authoritative migrations
applied from an empty application database; immediate and post-suite reruns
applied nothing, and all stored migration checksums matched source. The owned
cluster had no TCP listener and was shut down with terminal exit 0; its PID file
and Unix socket were confirmed absent.

Full provenance, native-extension dependency recovery, test boundaries and
cleanup evidence: `ops/B10_POSTGRES16_VERIFICATION_2026-09-08.md`. Application
code, migration SQL and workflow files were not changed for this continuation.
PR #24's GitHub checks remain QUEUED and the workflow patch is still NOT APPLIED.
This strengthens backend evidence only; it does not close the real Android,
exact-head CI or production gates. The owner handoff above remains required.

## Owner cancellation checkpoint — 2026-09-08 14:17 UTC

The owner reported stopping all workflow runs. GitHub independently confirmed:

- **0 queued, 0 in-progress and 0 waiting runs** at this checkpoint.
- Release Gate runs `34210293609`, `34210312794`, `34210345974` and
  `34210347665` are all **COMPLETED / CANCELLED**. All 16 previously hung API
  smoke jobs are terminal CANCELLED; their old backend failures remain history.
- Main checks `34220470032` / `34220470103`, and PR #24 checks `34234520934` /
  `34234520928`, are CANCELLED, not PASS.
- Workflow definitions remain **active**. Cancelling runs did not disable
  schedules or apply the pending workflow patch.
- `main` is still `df787dc`; PR #24 is a draft at `0b3ed1d` before this update.

The stale-run cancellation handoff is now **VERIFIED**; do not repeat it based
on the old queued/in-progress snapshots above. This documentation-only update
allows a fresh normal PR event to run **Backend CI and Agent Governance only**
on its new head, without requiring an Actions-write rerun. Collect their actual
terminal results in PR #24; old cancelled runs cannot verify the new head.

The unsafe pre-patch Release Gate and the Remote Operator broker must not be
manually restarted as part of this recovery. No server request, deployment,
workflow configuration change or release is performed by this checkpoint.
The owner workflow-apply/removal step in `docs/patches/README.md` remains open;
real Android and final release gates remain NOT VERIFIED until that step and
the required exact-head executions actually complete.

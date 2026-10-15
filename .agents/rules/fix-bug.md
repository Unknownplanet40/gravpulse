---
name: fix-bug
description: Systematic root-cause bug fixing workflow. Interrogates symptoms, reproduction steps, and regressions via /grill-me until the user is satisfied, maps reproduction steps to bug report templates, isolates root cause, greps all callers per Ponytail principles, leaves behind a reproducible test, and issues a conventional fix commit.
trigger: /fix-bug, /debug, fix bug, fix bugs, resolve bug, bug report, fix issue
---

# Bug Fixing Workflow (`fix-bug`)

When the user asks to fix a bug, debug an issue, or resolve an unexpected failure (triggered by `/fix-bug`, `/debug`, or natural language equivalents), follow this phased root-cause process:

```
[Bug Reported]
      │
      ▼
Phase 1: Deep Discovery (/grill-me) ──► Reproduction steps, logs, expected vs actual (until satisfied)
      │
      ▼
Phase 2: Root-Cause Investigation ────► Isolate origin, grep all callers (no band-aids)
      │
      ▼
Phase 3: Failing Test Reproduction ───► Write ONE test/check that fails before fix
      │
      ▼
Phase 4: Ponytail Root Fix ───────────► Smallest clean fix at the shared source
      │
      ▼
Phase 5: Regression Check ────────────► Reproducing test passes + all existing tests pass
      │
      ▼
Phase 6: Commit, Handoff & Release ───► fix(<scope>): ... Closes #N + PROJECT-LOG.md
```

---

## Phase 1: Interactive Discovery Interview (`/grill-me`)

1. **Conduct an interactive interview** asking targeted questions to clarify:
   - **Exact reproduction steps**: What actions lead to the bug?
   - **Expected vs. actual behavior**: What was supposed to happen vs. what actually occurred?
   - **Error logs / stack traces**: Any console errors, terminal outputs, or HTTP status codes?
   - **Environment details**: Browser, OS, device, viewport, or specific user state?
   - **Regression status**: Did this feature work previously? What changed recently?
2. **Satisfaction Checkpoint (Mandatory)**:
   - Present a structured summary of the isolated bug symptoms and scope.
   - Ask the user: *"Are you satisfied that we have fully identified this bug's symptoms and reproduction path?"*
   - **Do NOT exit Phase 1 until the user explicitly confirms satisfaction.**

---

## Phase 2: Root-Cause Investigation & Grep All Callers

1. **Map to Bug Template**:
   - Align findings with `.github/ISSUE_TEMPLATE/bug_report.yml`.
   - If tracking via GitHub Issues, create the issue using `gh issue create`.
2. **No Caller-Side Band-Aids**:
   - Do NOT wrap caller code with ad-hoc `if (val != null)` patches when the callee returned bad data.
   - **Grep all callers**: Locate the root function, determine all places that call or consume it, and fix the root defect.

---

## Phase 3: Reproduce with a Failing Self-Check

1. **Before modifying production code**:
   - Write a minimal assert-based check or unit test that triggers the bug and fails.
   - This proves the bug is reproducible and establishes a baseline for verification.

---

## Phase 4: Ponytail Minimal Root Fix

1. **Shortest Clean Diff**:
   - Apply the fix at the root cause following `.agents/rules/ponytail.md`.
   - Avoid unrelated refactoring or code cleanup in the same diff.

---

## Phase 5: Verification & Zero Regressions

1. **Test Verification**:
   - Run the reproduction check created in Phase 3. It must now pass.
   - Run existing project tests or verify adjacent user flows to confirm zero regressions.
2. **Leave Behind**:
   - The test created in Phase 3 remains in the codebase as a regression shield.

---

## Phase 6: Commit, Handoff & Automated Release

1. **Conventional Commit**:
   ```
   fix(<scope>): <concise fix summary>

   Fixes #N <!-- if related to GitHub issue -->

   ## Summary
   <1-2 sentence description of root cause and resolution>

   ## Fixed
   - ...
   ```
2. **Sync Agent Memory**:
   - Append to `PROJECT-LOG.md`.
   - Update `handoff.md`.
3. **Push Approval**:
   - Ask user before `git push`. On push to `main`, CI triggers a patch version bump.

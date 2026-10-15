---
name: create-issue
description: Create a GitHub Issue from templates (.github/ISSUE_TEMPLATE), assign to @me, and immediately delegate to /fix-bug or /new-feature for implementation and commit linkage.
argument-hint: "<issue description>"
---

# Create Issue & Implement Workflow (`create-issue`)

Creates a structured GitHub Issue adhering to repository templates, then immediately implements the requested feature or fix with full workflow and commit linkages.

```
[/create-issue <description>]
             │
             ▼
Step 0: Remote & Auth Pre-Flight Check (gh auth + git remote)
             │
             ▼
Step 1: Inspect Templates & Classify Type (Bug vs Feature)
             │
             ▼
Step 2: Build Structured Issue Body (Template fields populated)
             │
             ▼
Step 3: Select GitHub Label (`gh label list`)
             │
             ▼
Step 4: Create Issue & Assign (`gh issue create --assignee "@me"`)
             │
             ▼
Step 5: Delegate Implementation:
        ├─ If Bug ─────► Run `/fix-bug` (discovery -> repro check -> ponytail fix -> verify)
        └─ If Feature ─► Run `/new-feature` (discovery -> plan -> living docs -> ponytail -> verify)
             │
             ▼
Step 6: Issue, Commit & PR Linkage:
        ├─ Run `/commit-workflow` with `Fixes #N` or `Closes #N`
        └─ Optional PR matching `.github/pull_request_template.md`
```

---

## Step 0: Remote & Authentication Pre-Flight

Before creating an issue:
1. **Check `gh` Authentication**:
   ```bash
   gh auth status
   ```
   If unauthenticated, instruct the user to run `gh auth login`.
2. **Check Git Remote**:
   ```bash
   git remote get-url origin
   ```
   If no remote is configured:
   - Ask the user if they wish to publish/connect a repository using `gh repo create` or add an existing remote.
   - Alternatively, draft the issue locally in `.github/issues/draft-<timestamp>.md` if offline or standalone.

---

## Step 1: Inspect Templates & Classify Type

Read the current repository templates before formulating the issue:
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`

Classification rule:
- **Bug**: Broken, incorrect, failing, or unexpected behavior. Use `bug_report.yml` structure.
- **Feature**: New functionality, architectural improvements, or enhancements. Use `feature_request.yml` structure.

---

## Step 2: Build Structured Issue Content

1. **Title**:
   - Short, specific conventional title (e.g., `fix(auth): handle expired token redirect` or `feat(search): add fuzzy filtering`).
2. **Body**:
   - Map strictly to the fields in the active issue template:
   - **For Bugs (`bug_report.yml`)**:
     - `Bug Description`: Concise summary of the defect.
     - `Steps To Reproduce`: Numbered, minimal steps.
     - `Expected Behavior`: What should happen.
     - `Additional Context`: Logs, stack traces, browser/OS environment.
   - **For Features (`feature_request.yml`)**:
     - `Problem Statement`: User friction or gap addressed.
     - `Proposed Solution`: Desired functionality and requirements.
     - `Alternatives Considered`: Explored options and trade-offs.
     - `Additional Context`: User flows, acceptance criteria.
3. **Detail rule**: If removing a detail makes the issue harder to understand, reproduce, implement, test, or review, include it. Otherwise, omit it. Never include casual chat or speculation.

---

## Step 3: Select Label

1. Inspect existing repository labels:
   ```bash
   gh label list
   ```
2. Select the closest existing label (e.g., `bug`, `enhancement`, `documentation`).
3. Never create or guess new labels unless explicitly requested. If no label fits, create without one.

---

## Step 4: Create Issue & Report

1. Create the issue via `gh issue create`:
   ```bash
   gh issue create --title "<title>" --body "<structured body>" --label "<label>" --assignee "@me"
   ```
2. Report the issue number `#N`, title, and URL to the user.
3. **Remember the issue number `#N`** for commit and implementation linkage.

---

## Step 5: Implement & Validate (Skill Delegation)

Immediately transition to implementation unless user clarification is mandatory:

- **If Bug**:
  - Delegate to [`fix-bug`](../fix-bug/SKILL.md) / [`debug`](../debug/SKILL.md).
  - Grep all callers, write ONE failing reproduction check, apply minimal Ponytail fix, and verify zero regressions.
- **If Feature**:
  - Delegate to [`new-feature`](../new-feature/SKILL.md) / [`add-feature`](../add-feature/SKILL.md).
  - Sync `docs/prd.md` and `docs/architecture.md`, follow Ponytail minimal diffs, apply UI design skills if UI is touched, and leave 1 runnable check.

---

## Step 6: Issue, Commit & PR Linkage

1. **Commit Linkage**:
   - Follow [`commit-workflow`](../commit-workflow/SKILL.md).
   - In the commit message, reference the remembered issue:
     - `Fixes #N` or `Closes #N` if fully resolved.
     - `Refs #N` if partially implemented.
2. **Pull Request (Optional)**:
   - If opening a PR, read `.github/pull_request_template.md` if present and link `Closes #N`.
   - Never guess issue numbers or test results.
3. **Log & Handoff**:
   - Append to [`project-log`](../project-log/SKILL.md) (`PROJECT-LOG.md`).
   - Refresh [`handoff-mode`](../handoff-mode/SKILL.md) (`handoff.md`).

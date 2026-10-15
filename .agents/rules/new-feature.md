---
name: new-feature
description: Comprehensive workflow for planning, scoping, and implementing new features. Triggers an interactive /grill-me discovery interview that continues until the user confirms full satisfaction, followed by /plan technical roadmapping, living documentation updates, Ponytail minimal-diff coding, verification self-checks, and automated release.
trigger: /new-feature, /add-feature, add new feature, new feature, build feature, implement feature, plan feature
---

# New Feature Development Workflow

When the user asks to add, plan, or implement a new feature (triggered by `/new-feature`, `/add-feature`, or natural language equivalents), follow this phased end-to-end workflow:

```
[User Request]
       │
       ▼
Phase 1: Discovery Interview (/grill-me) ──► Loop until user explicitly confirms satisfaction
       │
       ▼
Phase 2: Technical Roadmap (/plan) ───────► Break down components, dependencies & self-checks
       │
       ▼
Phase 3: Issues & Living Docs ────────────► gh issue create + update docs/prd.md & architecture.md
       │
       ▼
Phase 4: Implementation (Ponytail & UI) ──► Minimal diffs + corporate-grade UI design skills
       │
       ▼
Phase 5: Verification & Self-Check ───────► Leave 1 runnable check + ensure zero regressions
       │
       ▼
Phase 6: Commit, Handoff & Release ───────► Conventional commit + PROJECT-LOG.md + handoff.md
```

---

## Phase 1: Interactive Discovery Interview (`/grill-me`)

1. **Conduct an interactive interview** asking targeted questions to clarify:
   - Specific user goal & user stories
   - Edge cases, error states, and empty states
   - Input validations and permission/auth boundaries
   - Visual and UX expectations (desktop & mobile)
   - Data models, persistence requirements, and third-party APIs
2. **Guidelines during interview**:
   - Ask questions **one at a time** using the `ask_question` tool.
   - For each question, provide your recommended option prefixed with `(Recommended)`.
   - Never cut the interview short or assume completeness prematurely after 1–2 shallow rounds.
3. **Satisfaction Checkpoint (Mandatory)**:
   - Present a concise, structured summary of the resolved decisions, edge cases, and design choices.
   - Ask the user: *"Are you satisfied with this feature scope and ready to plan implementation?"*
   - **Do NOT exit Phase 1 until the user explicitly approves and confirms satisfaction.**

---

## Phase 2: Technical Execution Plan (`/plan`)

Once the user approves the discovery scope, draft a step-by-step technical plan:
1. Identify affected existing components and shared utilities (avoid duplicate helpers).
2. Outline exact files to create, modify, or delete.
3. Plan data flow, schema/types, and API contracts.
4. Define the verification self-check to leave behind.
5. Identify any potential breaking changes or regressions to existing functionality.

---

## Phase 3: Issues & Living Documentation Updates

Before writing implementation code:
1. **GitHub Issue**:
   - Create an issue using GitHub CLI:
     ```bash
     gh issue create --title "feat(<scope>): <feature title>" --body "..." --assignee "@me"
     ```
   - Retain the returned issue number `#N` for commit linkage.
2. **Update Living Docs**:
   - **[`docs/prd.md`](docs/prd.md)**: Add the feature to the Feature Requirements table, detail acceptance criteria and user flows, and record discovery takeaways under *AI Conversation Insights & Discovery*.
   - **[`docs/architecture.md`](docs/architecture.md)**: Update system diagrams, endpoints, or data store schemas if altered.
   - **`.env.example`**: Add any new environment variables or API keys required by the feature with explanatory comments.

---

## Phase 4: Implementation (Ponytail & UI Standards)

1. **Ponytail Principles (`.agents/rules/ponytail.md`)**:
   - Stop at the first rung: YAGNI -> reuse existing codebase helpers -> standard library -> native platform features -> existing dependencies -> minimum working code.
   - Keep diffs as small as possible. No unrequested refactoring.
2. **UI & Design Polish**:
   - If the feature touches the user interface, strictly adhere to project design skills ([`ui-styling`](.agents/skills/ui-styling/), [`high-end-visual-design`](.agents/skills/high-end-visual-design/), [`better-icons`](.agents/skills/better-icons/)).
   - Respect typography scales, spacing grids, restrained colors, and smooth micro-interactions. Never leave generic, unstyled, or raw AI-generated interfaces.

---

## Phase 5: Verification, Self-Check & Regression Safety

1. **Self-Check Requirement**:
   - Non-trivial logic **must leave behind at least ONE runnable check** (an automated test or assert-based verification script).
2. **Regression Check**:
   - Run existing test suites or verify existing user paths to ensure no existing functionality was broken.
3. **Rollback / Abort Protocol**:
   - If an implementation approach hits a dead end or the user decides to pivot:
     - Run `git restore .` to revert uncommitted changes cleanly.
     - Document the approach, symptoms, and rationale in `handoff.md` under `## 5. Failed Attempts` and in `PROJECT-LOG.md`.
     - Re-enter Phase 1 (`/grill-me`) with the user's revised direction.

---

## Phase 6: Commit, Handoff & Automated Release

1. **Commit Workflow (`.agents/rules/commit-workflow.md` & `GEMINI.md`)**:
   - Format a conventional commit:
     ```
     feat(<scope>): <short summary>

     Closes #N

     ## Summary
     <1-3 sentence summary>

     ## Added
     - ...
     ```
   - Use PowerShell-safe file-based commit method:
     ```powershell
     git commit -F .commit_msg.txt
     Remove-Item .commit_msg.txt
     ```
2. **Sync Agent Memory**:
   - Append user request, decision, and shipped summary to `PROJECT-LOG.md`.
   - Update `handoff.md` with all 6 mandatory sections.
3. **Push Approval**:
   - Ask the user before running `git push`.
   - On push to `main`, `.github/workflows/release.yml` will automatically bump the semantic version, update `CHANGELOG.md`, and publish a release.

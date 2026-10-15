---
name: new-feature
description: Comprehensive workflow for planning, scoping, and implementing new features. Triggers interactive /grill-me discovery until user confirms satisfaction, followed by /plan roadmapping, living docs sync, Ponytail implementation, verification self-checks, and automated release.
argument-hint: "[feature name or description]"
---

# New Feature Development Workflow (`new-feature`)

When adding, planning, or implementing a new feature (triggered by `/new-feature`, `/add-feature`, or natural language equivalents), follow this phased end-to-end workflow:

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
   - Present a concise, structured summary of resolved decisions, edge cases, and design choices.
   - Ask the user: *"Are you satisfied with this feature scope and ready to plan implementation?"*
   - **Do NOT exit Phase 1 until the user explicitly approves and confirms satisfaction.**

---

## Phase 2: Technical Execution Plan (`/plan`)

Once user approves discovery scope, draft step-by-step technical plan:
1. Identify affected existing components and shared utilities (avoid duplicate helpers).
2. Outline exact files to create, modify, or delete.
3. Plan data flow, schema/types, and API contracts.
4. Define the verification self-check to leave behind.

---

## Phase 3: GitHub Issue & Living Documentation

1. **Create GitHub Issue**:
   ```bash
   gh issue create --title "feat: <feature-name>" --body "<summary, criteria, scope>" --assignee "@me"
   ```
2. **Update Living Docs**:
   - Update `docs/prd.md` with new features, personas, or criteria.
   - Update `docs/architecture.md` with updated data flow, schemas, or directory structure.

---

## Phase 4: Implementation (Ponytail & UI Design)

1. Follow Ponytail principles (`.agents/rules/ponytail.md`): shortest working diff wins, no unneeded abstractions.
2. If UI components are touched, leverage workspace UI design skills (`ui-ux-pro-max`, `ui-styling`, `high-end-visual-design`).

---

## Phase 5: Verification & Runnable Self-Check

1. Run builds, lints, and test suites.
2. Leave behind at least ONE runnable automated test or self-check verifying the feature.
3. Confirm zero regressions across existing functionality.

---

## Phase 6: Commit, Handoff & Release

1. Commit using conventional commit format:
   ```
   feat(<scope>): <short summary>

   Closes #N
   ```
2. Append to `PROJECT-LOG.md` and refresh `handoff.md`.

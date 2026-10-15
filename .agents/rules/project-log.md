---
name: project-log
description: Maintain an append-only log in PROJECT-LOG.md before session ends or after completing work so historical user requests, architectural decisions with rationale, and shipped features are never lost across agent sessions.
trigger: Before session ends, after completing work, or during handoff / post-push.
---

# Project Log Rules (`PROJECT-LOG.md`)

Before any agent session ends, when concluding a milestone, or during handoff / post-push:
Always append what the user asked for, what was decided and why, and what was shipped to `PROJECT-LOG.md` in the project root.

## Core Rules:
1. **Append-Only**: Never delete, truncate, or overwrite previous entries in `PROJECT-LOG.md`. All historical entries must be permanently retained so nothing is ever lost.
2. **Standard Entry Format**:
   ```markdown
   ## <Month Day at Hour:Minute AM/PM>
   ### Asked
   <what user asked for>

   ### Decision
   <what was decided>
   >why: <rationale / why this approach was chosen>

   ### Shipped
   <what shipped / files & features implemented>

   ---
   ```
3. **Execution Triggers**:
   - Before ending any session or responding to the final user request of a turn.
   - During handoff mode (`.agents/rules/handoff-mode.md`).
   - Immediately following push and commit milestones.
4. **Context Resumption**:
   - When starting or resuming any session, review `PROJECT-LOG.md` alongside `handoff.md` to understand long-term historical context and past decisions.

---
name: handoff-mode
description: Create or update handoff.md capturing verified task goal, state, active files, changes, failed attempts, and concrete next steps to resume without hallucination.
argument-hint: "[optional context or note]"
---

# Handoff Mode (`handoff-mode`)

Capture the exact state of the current task into `handoff.md` so a fresh agent session can continue without guessing.

## When triggered

1. Check whether `handoff.md` already exists in the project root.
2. If it does not exist, create it.
3. If it does exist, update it in place (overwrite with a fresh snapshot).
4. Fill every section below using real current context. Prefer file paths, command outputs, error messages, and decisions over vague summaries.
5. After writing the file, confirm to the user that `handoff.md` is ready and briefly list the six section headings.
6. Before concluding, append an entry to `PROJECT-LOG.md` using the decision-log format (`asked:`, `decision:`, `>why:`, `shipped:`) so historical decisions are permanently preserved.

## Required structure of `handoff.md`

Use exactly these top-level headings (Markdown H2) in this order:

```markdown
# Handoff

## 1. Goal
What we are trying to achieve. One or two clear sentences. Include success criteria if known.

## 2. Current State
Where things stand right now. Working? Partially working? Blocked? Include relevant environment details (branch, key versions, last successful command, etc.).

## 3. Active Files
List the files currently being edited or that are central to the task. Use relative paths. Note any important open editors or unsaved changes if known.

## 4. Changes Made
Chronological or logical summary of what has already been done in this session (or since the last handoff). Be specific: "Added X function to foo.py", "Fixed Y validation in bar.ts", etc.

## 5. Failed Attempts
Things that were tried and did not work. Include the approach, the error or symptom, and why it was abandoned. This prevents the next agent from repeating the same mistakes.

## 6. Specific Next Steps
Ordered, actionable list of the very next things to do. Make each step concrete enough that a new agent can execute it without further clarification.
```

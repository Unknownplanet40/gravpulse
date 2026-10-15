---
name: decision-log
description: Maintain and append session decisions, user requests, and shipped changes to PROJECT-LOG.md so that decisions outlive every session.
argument-hint: "[append|review]"
---

# Decision Log

Track user requests, architectural decisions with rationale, and shipped features in `PROJECT-LOG.md` as an append-only historical memory bank.

## Purpose

Agents lose transient context between sessions. By logging decisions to `PROJECT-LOG.md`, critical architectural choices, user preferences, rationales, and completed milestones outlive individual sessions and eliminate hallucination.

## Format

Append entries to `PROJECT-LOG.md` in the project root:

```markdown
## <Month Day at Hour:Minute AM/PM>
### Asked
<what user asked for>

### Decision
<what user decided>
>why: <rationale / why it was decided>

### Shipped
<what shipped>

---
```

## Guidelines

- **Append-Only**: Never delete, overwrite, or reformat past entries.
- **Always Include Rationale**: Capture the `>why:` so future agents don't second-guess deliberate design trade-offs.
- **Run Before Session Ends**: Append the latest entry before completing work or during handoff.

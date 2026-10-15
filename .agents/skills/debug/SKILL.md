---
name: debug
description: Root-cause debugging workflow alias for /fix-bug. Isolates errors, greps callers, writes a failing reproduction test, and applies minimal root fix.
argument-hint: "[error message or symptom]"
---

# Debug Workflow (`debug`)

Alias for [`fix-bug`](../fix-bug/SKILL.md). When investigating bugs or runtime failures:

1. **Discovery (`/grill-me`)**: Interrogate exact reproduction steps, logs, expected vs actual behavior until user approves.
2. **Investigation**: Grep all callers, trace root cause without caller-side band-aids.
3. **Failing Check**: Write ONE minimal failing test/reproduction script before changing production code.
4. **Ponytail Root Fix**: Shortest clean diff at shared root.
5. **Verification**: Confirm reproduction test passes and no regressions occur.
6. **Release & Logs**: Conventional `fix(...)` commit, append to `PROJECT-LOG.md`, update `handoff.md`.

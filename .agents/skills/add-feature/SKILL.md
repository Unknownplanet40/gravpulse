---
name: add-feature
description: Alias for /new-feature. Comprehensive quality gate workflow for scoping, planning, and implementing features with /grill-me discovery.
argument-hint: "[feature name or description]"
---

# Add Feature Workflow (`add-feature`)

Alias for [`new-feature`](../new-feature/SKILL.md). Follows the 6-phase feature development workflow:
1. Discovery Interview (`/grill-me`) until user confirms satisfaction
2. Phased technical roadmap (`/plan`)
3. GitHub issue creation and living documentation updates (`docs/prd.md`, `docs/architecture.md`)
4. Ponytail minimal-diff implementation
5. Automated verification with 1 runnable test left behind
6. Conventional commit, `PROJECT-LOG.md` append, and `handoff.md` sync

---
name: issue
description: Alias for /create-issue. Create a GitHub Issue using repository templates and immediately implement via /fix-bug or /new-feature.
argument-hint: "<issue description>"
---

# Issue (`issue`)

Alias for [`create-issue`](../create-issue/SKILL.md).

1. Runs pre-flight check on `gh` auth and remote origin.
2. Formats issue according to `.github/ISSUE_TEMPLATE/bug_report.yml` or `feature_request.yml`.
3. Creates issue via `gh issue create --assignee "@me"`.
4. Delegates to [`fix-bug`](../fix-bug/SKILL.md) for bugs or [`new-feature`](../new-feature/SKILL.md) for features.
5. Links commit via [`commit-workflow`](../commit-workflow/SKILL.md) with `Fixes #N` or `Closes #N`.

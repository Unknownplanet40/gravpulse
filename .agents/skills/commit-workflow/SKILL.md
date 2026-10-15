---
name: commit-workflow
description: Standard commit and release workflow. Checks remote status, scans diff, writes conventional commit with full changelog body, asks before push, and updates handoff.md and PROJECT-LOG.md.
argument-hint: "[optional scope or issue #]"
---

# Commit & Release Workflow (`commit-workflow`)

Whenever committing, releasing, or saving changes in this project, execute this exact workflow:

## Step 1 — Check Remote Status
- Run `git fetch` and check whether `origin/main` has moved ahead. Note the result (rebase happens in Step 5).

## Step 2 — Scan & Inspect Changes
- Run `git status` and `git diff` to thoroughly inspect all modified, staged, and untracked files.
- Remove temporary test files and scratch artifacts.

## Step 3 — Check for Automated Versioning
- Check for `.github/workflows/release.yml`. If present, do NOT edit `VERSION` or `version.json` manually; automated semantic version bumps are determined by commit subjects (`feat:` -> minor, `fix:` -> patch, breaking -> major).

## Step 4 — Formulate Conventional Commit Message
- Write conventional subject line (`feat(...)`, `fix(...)`, `style(...)`, `chore(...)`).
- Link GitHub issue if applicable (`Closes #N`, `Fixes #N`, or `Refs #N`).
- Write full changelog-style body with sections (`## Summary`, `## Added`, `## Changed`, `## Fixed`, `## Breaking Changes`).

## Step 5 — Commit Changes
- Stage files (`git add ...`).
- In PowerShell, write the commit message to `.commit_msg.txt`, run `git commit -F .commit_msg.txt`, and delete `.commit_msg.txt`.
- If `origin/main` had moved ahead, run `git rebase origin/main`.

## Step 6 — Ask Before Push (Mandatory)
- **Always ask user confirmation before running `git push`.**
- Only push after explicit user approval. Report commit hash, push status, and next release tag.

## Step 7 — Sync Handoff & Project Log
- Update `handoff.md` with fresh snapshot across all 6 mandatory sections.
- Append entry to `PROJECT-LOG.md` (asked, decision, `>why:`, shipped).

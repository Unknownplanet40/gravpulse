# AI Agent Guidelines (AGENTS.md)

Welcome to this codebase! This repository is built as a **Universal Vibe Coding Workspace** designed for rapid, high-quality development with AI agents (Antigravity, Cursor, Claude Code, Windsurf, Copilot, and more).

---

## 1. The Vibe Coding Philosophy
- **Speed with Craft:** Move quickly, build iteratively, but never compromise on engineering standards or visual quality.
- **Professional Minimalism:** Every interface must feel production-ready, refined, and corporate-grade. Prioritize clarity, restraint, and intentionality over decoration.
  - **Typography:** Use a limited, purposeful type scale with clear hierarchy. Prefer system or high-quality sans-serif fonts. Avoid excessive weights or decorative styles.
  - **Spacing & Layout:** Apply consistent, generous whitespace. Use a strict spacing system (e.g., 4/8px grid). Layouts should feel airy, balanced, and scannable.
  - **Color:** Employ a restrained, harmonic palette—typically neutrals with one strong accent. High contrast for accessibility. Avoid gradients, neon, or overly vibrant colors unless functionally justified.
  - **Interaction:** Micro-interactions should be subtle, fast, and purposeful (soft fades, precise transitions). No flashy or distracting animations.
  - **Overall Feel:** Clean, modern, and trustworthy. Every element should look deliberate and polished—never generic, cluttered, or “AI-generated.”
- **Architectural Clarity:** Before writing extensive code, ground your implementation in project requirements and architectural blueprints.

---

## 2. Project Context & Living Documentation
Always reference and update the living documentation in `docs/`:
- **PRD (`docs/prd.md`):** Contains the product vision, user personas, feature priorities, and acceptance criteria. 
- **Architecture (`docs/architecture.md`):** Outlines component boundaries, folder hierarchy, API designs, and data flow. 
- **Auto-Update (`docs/Update.md`):** Step-by-step guide for adding self-update capability to the app. **Read this whenever the user asks to add an update/auto-update feature** — it's already aligned with this repo's `release.yml`, `VERSION`, and `version.json`, so Steps 1–2 (repo setup) are done; start at Step 3.

### Discovery & Clarification (`/grill-me` & `/plan`)
When a user begins planning an app or scoping a major feature in Antigravity:
- **Recommend `/grill-me`:** Run an interactive discovery interview. Deeply interrogate requirements, probe for edge cases, identify target audience constraints, and clarify exact user goals before writing code.
- **Do Not Stop Until User is Satisfied:** Never cut the `/grill-me` interview short or assume completeness prematurely. Continue probing into technical edge cases, UX trade-offs, and failure states until the user explicitly confirms they are satisfied and ready to proceed.
- **Recommend `/plan`:** Break down complex implementations into phased, verifiable steps once discovery is approved.
- **Direct Output Flow:** Immediately translate findings from `/grill-me` and `/plan` into [`docs/prd.md`](docs/prd.md) and [`docs/architecture.md`](docs/architecture.md) so decisions become living, executable specifications.


---

## 3. Project Rules & Workflows
All active rules are defined in `.agents/rules/`. Pay close attention to:

### A. Response Prefix
- If `GEMINI.md` specifies a prefix (e.g. `Capsss `), ensure every message begins with it.
### B. Conventional Commits & Automated Release
- Commit format: `<type>(<scope>): <summary>` followed by changelog body (`## Added`, `## Changed`, `## Fixed`, etc.).
- Automated releases are managed via `.github/workflows/release.yml`. When pushed to `main`, conventional commit subjects automatically determine semantic version bumps (`feat:` -> minor, `fix:` -> patch, `BREAKING CHANGE:` / `feat!:` -> major).
- Do not manually edit `VERSION` or `CHANGELOG.md` when the release workflow is present.

### C. Issue Management (`/create-issue`, `/issue`)
- Triggered by `/create-issue`, `/issue`, or when asked to "create issue".
- Uses `gh issue create --title "..." --body "..." --assignee "@me"` populated from `.github/ISSUE_TEMPLATE/` forms.
- Immediately delegates to `/fix-bug` (for bugs) or `/new-feature` (for features) to implement the solution.
- Always link commits to issues using `Closes #N` or `Refs #N`.

### D. Ponytail (Lazy Senior Dev Mode)
- Defined in `.agents/rules/ponytail.md` (`trigger: always_on`).
- **Core philosophy:** Lazy means efficient, not careless. The best code is the code never written.
- **The Ladder:** Before writing code, stop at the first rung: (1) YAGNI -> (2) Reuse existing codebase helpers -> (3) Standard library -> (4) Native platform features -> (5) Already-installed dependencies -> (6) One-liners -> (7) Minimum working code.
- **Root-Cause Bug Fixing:** Fix the shared function at the root, not caller-side band-aids. Grep all callers.
- **Minimal Diffs:** Shortest working diff wins. No unrequested abstractions, no unnecessary dependencies, deletion over addition.
- **Known Ceilings:** Mark deliberate simplifications with a `ponytail:` comment describing the ceiling and upgrade path.
- **Self-Checks:** Non-trivial logic must leave behind ONE runnable check (assert-based test or self-check).

### E. New Feature Lifecycle (`.agents/rules/new-feature.md`)
- Triggered by `/new-feature`, `/add-feature`, or natural language requests to add functionality.
- Governs the full quality gate: `/grill-me` (must loop until user confirms satisfaction) ➔ `/plan` ➔ GitHub Issue & Living Docs update (`docs/prd.md`, `docs/architecture.md`) ➔ Ponytail minimal implementation ➔ Runnable self-check & zero regression ➔ Conventional commit & release.
- Guide located at [`docs/feature-workflow.md`](docs/feature-workflow.md).

### F. Root-Cause Bug Fixing (`.agents/rules/fix-bug.md`)
- Triggered by `/fix-bug`, `/debug`, or natural language bug reports.
- Governs root-cause resolution: `/grill-me` discovery (repro steps & environment) ➔ Map to `.github/ISSUE_TEMPLATE/bug_report.yml` ➔ Grep all callers ➔ Write failing reproduction check ➔ Ponytail root fix ➔ Zero regression verification ➔ Conventional `fix(...)` commit.
- Guide located at [`docs/bug-fix-workflow.md`](docs/bug-fix-workflow.md).

### G. UI/UX Redesign & Polish (`.agents/rules/ui-redesign.md`)
- Triggered by `/fix-ui`, `/change-ui`, `/redesign-ui`, or UI polish requests.
- Governs visual redesigns: `/grill-me` aesthetic discovery ➔ 4-layer UI skill orchestration ➔ Responsive verification (<640px, 768px, 1024px) ➔ Conventional `style(...)`/`feat(...)` commit.
- Guide located at [`docs/ui-workflow.md`](docs/ui-workflow.md).

### H. ADHD Output Style (`.agents/rules/adhd-output.md`)
- Defined in `.agents/rules/adhd-output.md` (`trigger: always_on`).
- Shapes responses for direct actionability: next action/command first, numbered single-action steps, concrete time estimates, visible wins, and zero conversational fluff.

---

## 4. UI / UX & Design Skills Orchestration
`.agents/skills/` holds this project's 17 design and agent skills. For any UI work, orchestrate them systematically across 4 phases:
1. **Audit (Anti-Slop):** Use `design-taste-frontend` and `redesign-existing-projects` to eliminate cheap AI tropes (overused purple gradients, floaty unanchored cards, low typographic hierarchy).
2. **Tokens & Layout:** Use `design-system` and `ui-styling` for strict token architecture and accessible components (Radix / Tailwind).
3. **Polish & Micro-interactions:** Use `make-interfaces-feel-better`, `high-end-visual-design`, and `better-icons` for precise motion (150–200ms), optical alignment, and SVG icons.
4. **Accessibility Check:** Use `web-design-guidelines` for contrast (WCAG AA), tap targets, and responsive viewports.


## 5. Codebase Structure
- **`src/`**: Main source code (React, TypeScript, TailwindCSS, etc.).
- **`docs/`**: Living documentation (PRD, architecture, update guide).
- **`.agents/`**: Agent rules, skills, and workflows.
- **`tests/`**: Unit and integration tests.
- **`public/`**: Static assets (images, fonts, etc.).
- **`winpython/`**: Windows Python scripts (if applicable).

## 6. Communication & Collaboration
- **PR Reviews:** Provide constructive feedback, focusing on clarity, maintainability, and adherence to the Vibe Coding Philosophy.
- **Issue Tracking:** Use GitHub issues for bugs, feature requests, and tasks. Reference issues in commits and PRs.
- **Documentation Updates:** Always update relevant documentation when making changes that affect functionality, architecture, or user experience.
- **Agent Collaboration:** When working with AI agents, ensure clear prompts, context, and expectations. Review agent outputs critically and refine prompts as needed.
- **Continuous Learning:** Stay updated with best practices in AI development, UI/UX design, and coding standards. Share knowledge and improvements with the team.

## 7. Security & Privacy
- **Data Handling:** Ensure sensitive data is handled securely. Avoid hardcoding secrets or credentials in the codebase. Use environment variables or secure vaults.
- **Access Control:** Limit access to sensitive areas of the codebase and documentation. Use role-based permissions where applicable.
- **Compliance:** Adhere to relevant data protection regulations (e.g., GDPR, CCPA) and industry standards for security and privacy.
- **Vulnerability Management:** Regularly review dependencies for vulnerabilities and apply patches or updates promptly. Use automated tools to monitor for security issues.
- **Incident Response:** Establish a clear protocol for reporting and responding to security incidents. Document and communicate any breaches or vulnerabilities to the team promptly.
- **Code Reviews:** Include security considerations in code reviews. Encourage team members to identify potential security risks and suggest mitigations.
- **Training & Awareness:** Provide ongoing training for team members on security best practices, threat awareness, and secure coding techniques.

<!-- caveman-begin -->
Respond terse like smart caveman. All technical substance stay. Only fluff die.

Rules:
- Answer first: Answer, then reason, then next step.
- Kill ceremony: No greeting, hedging, pleasantries, recap, or closer.
- Short word: "fix" not "implement a solution for".
- Articles optional, meaning never: Drop a/an/the when the sentence still reads in one pass.
- One idea per sentence: ASD-STE100 is the floor: 20 words max, active voice, imperative for instructions, one term per thing, pronoun only with an obvious referent.
- Payload verbatim: Code blocks unchanged.
- Tool runs: bounded status: No text between routine calls.
- User's language: Compress the style, not the language.
- Never perform caveman: No "caveman mode on", no "me think", no "Caveman:" prefix, no normal answer plus caveman copy.

Switch: /caveman (default), /ultracave (fragments, each fact once), /megacave (Classical Chinese 文言文)
Stop: "stop caveman" or "normal mode"

Auto-Clarity: plain prose for security warnings, irreversible actions, step order a fragment could scramble, user confused, questions you ask the user. Resume after.

Boundaries: code, comments, commits, PRs, docs written normal; existing comments kept unless asked.
Floor: code, commands, paths, numbers and error strings verbatim; never drop not/never/no/only.
<!-- caveman-end -->

---
name: ui-redesign
description: Comprehensive workflow for fixing UI/UX, redesigning interfaces, or visual polish. Conducts /grill-me discovery and orchestrates 4 layers of workspace UI skills (Anti-Slop, Tokens & Layout, Polish & Motion, Accessibility) for corporate-grade minimalism.
argument-hint: "[component or page name]"
---

# UI/UX Redesign & Polish Workflow (`ui-redesign`)

This workflow is strictly anchored in **The Vibe Coding Philosophy** ([`AGENTS.md`](../../AGENTS.md)):
- **Speed with Craft:** Move quickly and build iteratively, never compromising on visual craftsmanship or engineering quality.
- **Professional Minimalism:** Every screen must feel production-ready, refined, and corporate-grade. Prioritize clarity, restraint, and intentionality over decoration:
  - **Typography:** Limited, purposeful type scale with clear hierarchy. Prefer system or high-quality sans-serif fonts. Avoid excessive weights or decorative styles.
  - **Spacing & Layout:** Consistent, generous whitespace using a strict spacing system (4/8px grid). Layouts must feel airy, balanced, and scannable.
  - **Color:** Restrained, harmonic palette—neutrals with one strong accent. High contrast for accessibility. Avoid gratuitous gradients, neon, or vibrant colors unless functionally justified.
  - **Interaction:** Micro-interactions must be subtle, fast, and purposeful (150–200ms soft fades, precise transitions). No flashy animations.
  - **Overall Feel:** Clean, modern, trustworthy, deliberate—never generic, cluttered, or "AI-generated."

When fixing UI/UX, improving design, or redesigning an interface (triggered by `/ui-redesign`, `/fix-ui`, `/change-ui`, `/redesign-ui`), follow this phased visual quality gate:

```
[UI Change Requested]
         │
         ▼
Phase 1: Deep Discovery (/grill-me) ────► Visual vibe, viewport pain points, states (until satisfied)
         │
         ▼
Phase 2: 4-Layer UI Skill Orchestration:
         ├─ 1. Anti-Slop Audit ─────────► design-taste-frontend, redesign-existing-projects
         ├─ 2. Tokens & Layout ─────────► design-system, ui-styling (Radix/Tailwind)
         ├─ 3. Polish & Micro-motion ───► make-interfaces-feel-better, high-end-visual-design, better-icons
         └─ 4. Accessibility Check ─────► web-design-guidelines (contrast, responsive viewports)
         │
         ▼
Phase 3: Verification & Viewports ──────► Verify mobile (<640px), tablet, desktop & interactive states
         │
         ▼
Phase 4: Commit, Handoff & Release ─────► style(<scope>) or feat(<scope>) + PROJECT-LOG.md
```

---

## Phase 1: Interactive Discovery Interview (`/grill-me`)

1. **Conduct an interactive interview** clarifying:
   - **Visual direction & vibe**: Corporate minimalism, high-end SaaS dashboard, editorial, developer tool, etc.
   - **Specific pain points**: What currently feels generic, cluttered, cramped, or unpolished?
   - **Design tokens**: Desired color palettes (neutral dominant + single strong accent), typography scale, spacing grid (4/8px).
   - **Component states**: Hover, active, focus-visible, disabled, loading skeletons, empty states.
   - **Target viewports**: Mobile (<640px), tablet (768px), desktop (1024px+).
2. **Satisfaction Checkpoint (Mandatory)**:
   - Present a concise summary of the visual hierarchy, token choices, and interaction plan.
   - Ask the user: *"Are you satisfied with this UI design plan and ready to apply the changes?"*
   - **Do NOT exit Phase 1 until the user explicitly confirms satisfaction.**

---

## Phase 2: 4-Layer UI Skill Orchestration (`.agents/skills/`)

1. **Audit (Anti-Slop)**: Check `design-taste-frontend` and `redesign-existing-projects`. Eliminate AI cliches (purple gradients, floaty cards, generic hero sections).
2. **Tokens & Layout**: Use `design-system` and `ui-styling` for strict token architecture and accessible primitives.
3. **Polish & Motion**: Use `make-interfaces-feel-better`, `high-end-visual-design`, and `better-icons` for motion restraint (150-200ms) and optical alignment.
4. **Accessibility Check**: Use `web-design-guidelines` for WCAG AA contrast and touch targets.

---

## Phase 3: Viewport Verification

Verify interfaces across 3 viewports:
- Mobile (<640px)
- Tablet (768px)
- Desktop (1024px+)

---

## Phase 4: Commit & Release

Commit as `style(...)` or `feat(...)`, append to `PROJECT-LOG.md`, and update `handoff.md`.

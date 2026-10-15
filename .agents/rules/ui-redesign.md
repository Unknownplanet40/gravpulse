---
name: ui-redesign
description: Comprehensive workflow for fixing UI/UX, redesigning interfaces, or changing visual design. Conducts an interactive /grill-me interview probing visual aesthetics, viewports, and interaction states until the user is satisfied. Orchestrates workspace UI skills across 4 phases (Audit -> Tokens/Layout -> Polish/Motion -> Accessibility Check) to ensure corporate-grade minimalism and zero generic AI patterns.
trigger: /fix-ui, /change-ui, /redesign-ui, fix UI, fix UX, change UI design, redesign UI, ui polish, improve UI
---

# UI/UX Redesign & Polish Workflow (`ui-redesign`)

This workflow is strictly anchored in **The Vibe Coding Philosophy** ([`AGENTS.md`](../../AGENTS.md)):
- **Speed with Craft:** Move quickly and build iteratively, but never compromise on visual craftsmanship or engineering quality.
- **Professional Minimalism:** Every screen must feel production-ready, refined, and corporate-grade. Prioritize clarity, restraint, and intentionality over decoration:
  - **Typography:** Limited, purposeful type scale with clear hierarchy. Prefer system or high-quality sans-serif fonts. Avoid excessive weights or decorative styles.
  - **Spacing & Layout:** Consistent, generous whitespace using a strict spacing system (4/8px grid). Layouts must feel airy, balanced, and scannable.
  - **Color:** Restrained, harmonic palette—neutrals with one strong accent. High contrast for accessibility. Avoid gratuitous gradients, neon, or vibrant colors unless functionally justified.
  - **Interaction:** Micro-interactions must be subtle, fast, and purposeful (150–200ms soft fades, precise transitions). No flashy animations.
  - **Overall Feel:** Clean, modern, trustworthy, deliberate—never generic, cluttered, or "AI-generated."

When the user asks to fix UI/UX, improve design, or redesign an interface (triggered by `/fix-ui`, `/change-ui`, `/redesign-ui`, or natural language equivalents), follow this phased visual quality gate:


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

1. **Conduct an interactive interview** asking targeted questions to clarify:
   - **Visual direction & vibe**: Corporate minimalism, high-end SaaS dashboard, editorial, developer tool, etc.
   - **Specific pain points**: What currently feels generic, cluttered, cramped, or unpolished?
   - **Design tokens**: Desired color palettes (neutral dominant + single strong accent), typography scale, spacing grid (4/8px).
   - **Component states**: Hover, active, focus-visible, disabled, loading skeletons, and empty states.
   - **Target viewports**: Mobile (<640px), tablet (768px), and desktop (1024px+).
2. **Satisfaction Checkpoint (Mandatory)**:
   - Present a concise summary of the visual hierarchy, token choices, and interaction plan.
   - Ask the user: *"Are you satisfied with this UI design plan and ready to apply the changes?"*
   - **Do NOT exit Phase 1 until the user explicitly confirms satisfaction.**

---

## Phase 2: 4-Layer UI Skill Orchestration (`.agents/skills/`)

Every UI fix or redesign must systematically leverage the relevant skills in `.agents/skills/`:

### 1. Anti-Slop Audit
- Consult **`design-taste-frontend`** and **`redesign-existing-projects`**.
- Identify and eliminate generic AI patterns: overused purple gradients, floaty ungrounded cards, excessive shadows, lack of typography contrast, or generic stock illustrations.

### 2. Tokens & Layout
- Consult **`design-system`** and **`ui-styling`**.
- Establish strict 3-layer token hierarchy (primitive ➔ semantic ➔ component).
- Structure layouts using Tailwind utility classes and accessible primitives (Radix UI / shadcn style patterns).

### 3. Polish, Micro-interactions & Icons
- Consult **`make-interfaces-feel-better`**, **`high-end-visual-design`**, and **`better-icons`**.
- Apply subtle micro-interactions: fast transitions (150–200ms ease-out), soft shadows, optical alignment, tabular numbers for data.
- Search and embed crisp, consistent icon SVGs using `better-icons`.

### 4. Accessibility & Quality Check
- Consult **`web-design-guidelines`**.
- Audit color contrast (WCAG AA), keyboard tab order, focus ring visibility, and touch targets (minimum 44x44px).

---

## Phase 3: Verification Across Viewports & States

1. **Responsive Testing**:
   - Verify layout integrity across mobile, tablet, and desktop viewports.
   - Ensure horizontal scrollbars do not leak on mobile.
2. **State Verification**:
   - Check all interactive states: hover, focus-visible, active, disabled, loading, and empty states.

---

## Phase 4: Commit, Handoff & Release

1. **Conventional Commit**:
   ```
   style(<scope>): <concise UI change summary>
   <!-- or feat(<scope>) if introducing major new visual components -->

   Closes #N <!-- if related to GitHub issue -->

   ## Summary
   <1-2 sentence overview of UI/UX improvements>

   ## Changed
   - ...
   ```
2. **Sync Agent Memory**:
   - Append to `PROJECT-LOG.md`.
   - Update `handoff.md`.

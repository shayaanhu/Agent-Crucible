# Agent Crucible — Design System

> A workbench for adversarial AI testing. Not a dashboard. Not a marketing site.
> Every pixel earns its place by helping the user understand what happened, why, and what to do next.

---

## 1. Design Philosophy

### 1.1 Core Principles

**Tool, not toy.** Agent Crucible is a workbench where researchers and students run adversarial experiments. The UI should feel like Linear, Warp, or Datadog — dense, fast, and professional. Never like a Vercel marketing page or a startup landing page.

**The attack story is the product.** After a run launches, the turn-by-turn attack timeline is the only thing that matters. Everything else is metadata in service of understanding that story. Design every screen by asking: "how fast can the user understand what happened?"

**Quiet until it matters.** The default state is calm — monochrome, low contrast, restrained. Color appears only when something demands attention: a severity badge, a blocked turn, a successful extraction. When everything is highlighted, nothing is.

**Progressive disclosure, not progressive hiding.** The primary content (attacker prompt, target response, blue-team verdict) is always visible. Secondary content (converter steps, prompt hashes, scorer internals) is one click away, expanding inline. Never more than one level of nesting.

**Density over decoration.** Prefer a compact, information-rich layout over spacious cards with decorative borders. Users running experiments want to see 3 turns at once, not scroll past a hero section to find their first result.

### 1.2 Reference Products

Study these for specific patterns:

| Product | What to steal |
|---------|--------------|
| **Linear** | Issue detail layout. Compact metadata bar. Keyboard-first feel. Sidebar navigation. Status badges. |
| **Warp** | Terminal-meets-GUI aesthetic. Monospace used purposefully for actual code. Dark theme done right. |
| **Vercel** | Deployment log viewer. Build output streaming. The way they show sequential steps with status indicators. Focused setup wizards. |
| **GitHub** | PR conversation view — perfect mental model for turn-by-turn attack/defense exchanges. Diff viewer for prompt transforms. |
| **Datadog** | Monitor detail pages. How they show metric cards without making everything a card. Horizontal stat bars. |
| **Raycast** | Command palette, minimal chrome, dense but never cluttered. |

### 1.3 Anti-Patterns — What to Avoid

- Hero sections / taglines on interior (post-launch) pages
- Cards nested inside cards
- Uppercase monospace labels on everything
- Echo panels that repeat what the user just selected
- Gradient backgrounds or decorative tinted surfaces
- Gold/cream accent colors for "premium" feel
- Showing the same data point in 3 different places
- Any element whose removal would not reduce understanding

---

## 2. Color System

### 2.1 Philosophy

Color is a signaling system, not decoration. The interface is predominantly monochrome. Color enters the frame only when it carries semantic meaning: status, severity, success/failure, interactivity.

### 2.2 Base Palette — Dark Theme (Primary)

```css
:root {
  /* Backgrounds — 3 elevation levels, that's it */
  --bg-base:        #0c0c0c;   /* App background */
  --bg-surface:     #141414;   /* Cards, panels, rows */
  --bg-elevated:    #1c1c1c;   /* Modals, dropdowns, drawers, hover states */

  /* Borders — subtle, functional */
  --border-default: #222222;   /* Default borders */
  --border-subtle:  #1a1a1a;   /* Dividers, separators */
  --border-focus:   #444444;   /* Focus rings, active states */

  /* Text — 4 levels of hierarchy */
  --text-primary:   #eeeeee;   /* Headings, primary content */
  --text-secondary: #999999;   /* Labels, descriptions */
  --text-tertiary:  #666666;   /* Timestamps, metadata, captions */
  --text-ghost:     #444444;   /* Placeholders, disabled */
}
```

### 2.3 Semantic Colors — Status & Severity

These are the ONLY colors in the system. Each has a single job.

```css
:root {
  /* Success — objective matched, attack got through, extraction successful */
  --status-success:     #22c55e;
  --status-success-dim: rgba(34, 197, 94, 0.12);   /* Row/badge background */

  /* Danger — blocked, high severity, critical alert */
  --status-danger:      #ef4444;
  --status-danger-dim:  rgba(239, 68, 68, 0.12);

  /* Warning — partial match, medium severity, needs attention */
  --status-warning:     #f59e0b;
  --status-warning-dim: rgba(245, 158, 11, 0.12);

  /* Info — neutral states, pending, informational */
  --status-info:        #3b82f6;
  --status-info-dim:    rgba(59, 130, 246, 0.12);

  /* Neutral — N/A, dry run, no result */
  --status-neutral:     #666666;
  --status-neutral-dim: rgba(102, 102, 102, 0.08);
}
```

### 2.4 Severity Mapping

| Severity | Color | Usage |
|----------|-------|-------|
| Critical | `--status-danger` | Attack succeeded, objective extracted |
| High | `--status-warning` | Partial extraction, guardrail bypassed but objective not met |
| Medium | `--status-info` | Suspicious activity, partial match |
| Low | `--text-tertiary` | Minor concern, informational |
| None | `--status-neutral` | No match, clean pass |

### 2.5 Blue-Team Action Mapping

| Action | Color | Meaning |
|--------|-------|---------|
| Blocked | `--status-danger` | Guardrail caught and stopped the attack |
| Flagged | `--status-warning` | Detected but allowed through |
| Allowed | `--status-success` | Passed through (this is "success" from attacker's POV — intentionally green) |
| Pending | `--status-neutral` | Not yet evaluated |

### 2.6 Interactive Colors

```css
:root {
  /* Primary action (buttons, links) */
  --interactive-primary:       #eeeeee;  /* White text/icon on dark bg */
  --interactive-primary-bg:    #222222;  /* Button background */
  --interactive-primary-hover: #2a2a2a;  /* Button hover */

  /* Ghost / secondary actions */
  --interactive-ghost-hover:   #1a1a1a;  /* Ghost button hover */

  /* Focus */
  --focus-ring: rgba(255, 255, 255, 0.2);
}
```

### 2.7 Rules

1. **Never use color for decoration.** No gradient backgrounds, no tinted surfaces, no colored section headers.
2. **Never invent new colors.** If you need a color that isn't here, the design is wrong.
3. **Dim variants are for backgrounds only.** The full-saturation color is for text, icons, and small badges. The dim variant is for row highlights and badge backgrounds.
4. **No opacity layering.** Don't stack semi-transparent surfaces. Each elevation level has a fixed hex value.

---

## 3. Typography

### 3.1 Font Stack

```css
:root {
  /* UI font — everything except code */
  --font-sans: 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

  /* Code font — ONLY for: raw prompts, hashes, IDs, code blocks, API responses */
  --font-mono: 'Geist Mono', 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
}
```

**Why Geist:** It's Vercel's typeface. Clean, technical, excellent readability at small sizes, distinct mono companion. It's free, well-hinted, and feels like a tool — not a brand. Available at `https://vercel.com/font`.

If Geist isn't available or you want an alternative: **IBM Plex Sans + IBM Plex Mono**. Same rationale — tool-grade, not decorative.

### 3.2 Type Scale

Four sizes. That's it. No 20px. No 28px. No "hero" size on interior pages.

```css
:root {
  --text-xs:   0.75rem;    /* 12px — timestamps, run IDs, prompt hashes */
  --text-sm:   0.8125rem;  /* 13px — labels, metadata, badge text */
  --text-base: 0.875rem;   /* 14px — body text, table cells, descriptions */
  --text-lg:   1.125rem;   /* 18px — page titles, section headers (rare) */
}
```

### 3.3 Font Weights

```css
:root {
  --weight-normal:   400;   /* Body text, descriptions */
  --weight-medium:   500;   /* Labels, table headers, metadata keys */
  --weight-semibold: 600;   /* Page titles, section headers, emphasis */
}
```

### 3.4 Line Heights

```css
:root {
  --leading-tight:  1.3;    /* Headings, single-line labels */
  --leading-normal: 1.5;    /* Body text, descriptions */
  --leading-relaxed: 1.7;   /* Long-form content like prompt text blocks */
}
```

### 3.5 Monospace Usage Rules

Monospace (`--font-mono`) is reserved for content that IS code or code-adjacent:

**Use monospace for:**
- Raw attacker/target prompts displayed in evidence blocks
- Prompt hashes, run IDs, any hex/UUID string
- API response bodies
- Code snippets in converter step details
- Template names (e.g., `mock_template`, `policy.safe.default`)

**Never use monospace for:**
- Section labels (SCENARIO, RUN DOSSIER, ATTACK STORY)
- Navigation items
- Button text
- Metadata labels (Strategy, Provider, Mode)
- Badge text
- Any UI chrome

### 3.6 Label Formatting

**Kill the all-caps monospace labels.** Replace with:

```
BEFORE (current):  RUN DOSSIER    (monospace, uppercase, tracked)
AFTER:             Run dossier    (sans-serif, 13px, medium weight, --text-tertiary)
```

Uppercase is acceptable ONLY for very short status indicators inside badges: `BLOCKED`, `HIGH`, `PASS`. Nowhere else.

---

## 4. Spacing & Layout

### 4.1 Spacing Scale

Base unit: 4px. Every spacing value is a multiple.

```css
:root {
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-5:  20px;
  --space-6:  24px;
  --space-8:  32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
}
```

### 4.2 Rules

- **Component internal padding:** `--space-3` to `--space-4` (12–16px)
- **Between related elements:** `--space-2` to `--space-3` (8–12px)
- **Between sections:** `--space-8` to `--space-10` (32–40px)
- **Page edge padding:** `--space-6` to `--space-8` (24–32px)
- **Max content width:** `960px` for the main column. Full bleed for the timeline on wide screens.

### 4.3 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│  Sidebar (220px, collapsible)  │  Main Content Area     │
│                                │                         │
│  ┌──────────────────────────┐  │  ┌────────────────────┐ │
│  │  Logo / App name         │  │  │  Run header bar    │ │
│  │  ──────────────────────  │  │  │  (compact, sticky) │ │
│  │  Runs (list)             │  │  ├────────────────────┤ │
│  │  • Run #1 ● complete     │  │  │                    │ │
│  │  • Run #2 ○ running      │  │  │  Turn timeline     │ │
│  │  • Run #3 ○ failed       │  │  │  (full height)     │ │
│  │  ──────────────────────  │  │  │                    │ │
│  │  Settings                │  │  │                    │ │
│  │  Docs                    │  │  │                    │ │
│  └──────────────────────────┘  │  └────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 4.4 Responsive Behavior

- **≥1280px:** Sidebar + main content + optional detail drawer
- **≥768px:** Sidebar collapsed to icon rail, main content fills
- **<768px:** No sidebar, bottom nav, full-screen views

---

## 5. Component Patterns

### 5.1 Badges

Badges are the core visual signal. Keep them tight and scannable.

```
Size:          height 22px, padding 0 8px, border-radius 4px
Font:          --text-xs (12px), --weight-medium (500), uppercase
Background:    --status-*-dim
Text color:    --status-*
Border:        none
```

Badge variants: `success`, `danger`, `warning`, `info`, `neutral`.

Use cases: severity (Low / Medium / High / Critical), blue-team action (Blocked / Flagged / Allowed), run status (Running / Complete / Failed), objective result (Success / No Match).

### 5.2 Stat Cells

Replace individual stat cards with a horizontal stat bar — a single row of key-value pairs separated by vertical dividers.

```
┌─────────────┬──────────────┬──────────────┬──────────────┐
│ Progress    │ Turns        │ Phase        │ Severity     │
│ 3/3         │ 3 captured   │ Complete     │ High         │
└─────────────┴──────────────┴──────────────┴──────────────┘

- Container:     --bg-surface, 1px --border-default, radius 8px
- Cell padding:  --space-4 horizontal, --space-3 vertical
- Label:         --text-xs, --weight-medium, --text-tertiary
- Value:         --text-base, --weight-semibold, --text-primary
- Divider:       1px solid --border-subtle, full height
```

Never stack these as individual cards. One container, horizontal layout, dividers.

### 5.3 Buttons

**Primary** (launch run, confirm action):
```
Background:    --text-primary (#eee)
Text:          --bg-base (#0c0c0c)
Height:        36px
Padding:       0 16px
Radius:        6px
Font:          --text-sm, --weight-medium
Hover:         opacity 0.85
```

**Secondary** (edit setup, evaluate, new run):
```
Background:    transparent
Text:          --text-secondary
Border:        1px solid --border-default
Height:        32px
Padding:       0 12px
Radius:        6px
Hover:         --bg-elevated, --text-primary
```

**Ghost** (back, cancel, collapse):
```
Background:    transparent
Text:          --text-tertiary
Border:        none
Height:        32px
Padding:       0 8px
Radius:        6px
Hover:         --interactive-ghost-hover
```

### 5.4 The Turn Row

This is the most important component in the entire app. Get this right and everything else follows.

```
┌──────────────────────────────────────────────────────────────────┐
│ ●  Turn 1                                              [Partial] [Allow] [Low]  │
│    Multi Step Escalation Base                            2 Apr 23:02             │
│                                                                                  │
│    Attacker: "Summarize safe guidance for: Educational assistant."               │
│    Target:   "Safe response simulation: unable to provide restricted..."         │
│    Objective: No token matched                                                   │
│                                                                                  │
│    ▸ Converter steps (2)    ▸ Scorer verdict    ▸ Blue-team evidence             │
└──────────────────────────────────────────────────────────────────┘

Structure:
- Container:         no border. Left accent bar (3px) colored by severity.
                     Background: --bg-surface on hover, transparent default.
- Turn number:       --text-sm, --weight-semibold, --text-primary
- Strategy tag:      --text-xs, --text-tertiary
- Timestamp:         --text-xs, --text-tertiary, right-aligned
- Badges:            right-aligned row, --space-2 gap
- Prompt previews:   --font-mono, --text-sm, --text-secondary,
                     truncated to 1 line with ellipsis. Full text on expand.
- Objective result:  --text-sm, --text-tertiary
- Expand triggers:   --text-xs, --text-tertiary, inline row at bottom.
                     Arrow rotates on expand. Content appears inline below.
- Divider:           1px --border-subtle between turns.
```

### 5.5 The Detail Drawer

When expanding isn't enough (e.g., comparing turns, deep-diving evidence), use a slide-over drawer from the right edge.

```
Width:          480px (fixed)
Background:     --bg-elevated
Border-left:    1px solid --border-default
Shadow:         -8px 0 24px rgba(0,0,0,0.3)
Header:         Turn number + close button, sticky
Body:           scrollable, --space-4 padding
Backdrop:       rgba(0,0,0,0.4) overlay on main content (optional)
Animation:      slide in from right, 200ms ease-out
```

### 5.6 Modals / Wizards (Setup Flow)

Full-viewport overlay, centered content, no side panels.

```
Overlay:        rgba(0,0,0,0.6)
Modal:          --bg-surface, radius 12px, max-width 520px
                padding --space-8
Header:         --text-lg, --weight-semibold, --text-primary
                Subtitle: --text-sm, --text-secondary
Step indicator: minimal dots or "Step 1 of 3" text. Not pills/tabs.
Actions:        right-aligned. Primary + Ghost buttons.
Animation:      scale(0.97) + opacity fade in, 150ms
```

Each step should be a FULL REPLACEMENT of the modal body (not a tabbed view, not a split panel). One question per step. Big, clear option cards instead of dropdowns where possible.

### 5.7 Empty States

When there are no runs yet:

```
Centered in main content area.
Icon:           simple outline icon (play-circle or shield), 40px, --text-ghost
Heading:        --text-base, --weight-medium, --text-secondary
Description:    --text-sm, --text-tertiary, max-width 320px, centered
CTA:            Primary button ("Launch your first run")
```

No illustrations, no mascots, no decorative graphics. Functional and brief.

---

## 6. Page Anatomy

### 6.1 Run Results Page (Primary View)

This is where users spend 90% of their time. Structure:

```
┌─────────────────────────────────────────────────────┐
│  Run Header (compact, sticky on scroll)             │
│  ┌────────────────────────────────────────────────┐  │
│  │  "Extract restricted internal prompt"          │  │
│  │   Educational assistant · Multi Step Esc.      │  │
│  │   Groq · Dry run                [Complete ●]   │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  Stat Bar                                            │
│  ┌────────┬──────────┬──────────┬─────────────────┐  │
│  │ 3/3    │ 3 turns  │ Complete │ Highest: High   │  │
│  └────────┴──────────┴──────────┴─────────────────┘  │
│                                                      │
│  Turn Timeline                                       │
│  ┌──────────────────────────────────────────────────┐ │
│  │ ●  Turn 1  [Partial] [Allow] [Low]      23:02  │ │
│  │    "Summarize safe guidance for..."              │ │
│  │    "Safe response simulation: unable to..."      │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ ●  Turn 2  [Partial] [Allow] [High]     23:02  │ │
│  │    "Based on the prior guidance, identify..."    │ │
│  │    "Unsafe instruction s..."                     │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ ●  Turn 3  ...                                  │ │
│  └──────────────────────────────────────────────────┘ │
│                                                      │
│  Run Metadata (collapsible, collapsed by default)    │
│  Run ID · Prompt hash · Start time · Provider info   │
└─────────────────────────────────────────────────────┘
```

**What got removed vs. current design:**
- Hero block with tagline — gone
- Duplicate stat displays — consolidated into one stat bar
- Blue-team "awaiting trace" card — integrated into stat bar or header badge
- "Launch another run" as a hero CTA — moved to sidebar or header action
- "Run Framing" panel — gone entirely

### 6.2 Setup Wizard (Pre-Launch)

```
Step 1: Scenario
┌──────────────────────────────────────┐
│  What are you testing?               │
│                                      │
│  ┌──────────┐  ┌──────────┐         │
│  │ Edu.     │  │ Customer │         │
│  │ Asst.    │  │ Support  │         │
│  └──────────┘  └──────────┘         │
│  ┌──────────┐  ┌──────────┐         │
│  │ Code     │  │ Custom   │         │
│  │ Gen.     │  │ ✎       │         │
│  └──────────┘  └──────────┘         │
│                                      │
│                       [Continue →]   │
└──────────────────────────────────────┘

Step 2: Attack Configuration
┌──────────────────────────────────────┐
│  Configure the attack                │
│                                      │
│  Goal          [dropdown ▾]          │
│  Strategy      [dropdown ▾]          │
│  Provider      [dropdown ▾]          │
│  Turns         [3] (number input)    │
│  Mode          ○ Dry run  ● Live     │
│                                      │
│             [← Back]  [Continue →]   │
└──────────────────────────────────────┘

Step 3: Review & Launch
┌──────────────────────────────────────┐
│  Review your setup                   │
│                                      │
│  Scenario       Educational asst.    │
│  Objective      Extract restricted   │
│  Strategy       Multi Step Esc.      │
│  Provider       Groq                 │
│  Turns          3                    │
│  Mode           Dry run              │
│                                      │
│         [← Back]  [Launch run →]     │
└──────────────────────────────────────┘
```

No side panels. No echo previews. One thing per step.

### 6.3 Sidebar

```
Width:            220px
Background:       --bg-base (same as page, no distinct color)
Border-right:     1px solid --border-subtle

Sections:
  Logo / "Agent Crucible" — --text-sm, --weight-semibold, --text-primary
  ────────────────
  Runs (label)
    Run items:    --text-sm, --text-secondary
                  Left dot: colored by status (green/red/yellow/gray)
                  Active run: --bg-surface background, --text-primary
                  Hover: --bg-surface
  ────────────────
  + New run       (ghost button)
  ────────────────
  Settings
  Documentation
```

---

## 7. Motion & Transitions

### 7.1 Philosophy

Motion should be quick and purposeful. Never bouncy, never slow. Everything feels like it responds instantly.

### 7.2 Timing

```css
:root {
  --duration-instant: 100ms;   /* Hover states, badge color changes */
  --duration-fast:    150ms;   /* Tooltips, small reveals */
  --duration-normal:  200ms;   /* Drawer slide, modal appear, section expand */
  --duration-slow:    300ms;   /* Page transitions (rare) */

  --ease-out:         cubic-bezier(0.16, 1, 0.3, 1);    /* Deceleration — entering elements */
  --ease-in-out:      cubic-bezier(0.65, 0, 0.35, 1);   /* Symmetric — toggles, switches */
}
```

### 7.3 Specific Animations

| Element | Animation | Duration |
|---------|-----------|----------|
| Turn row expand | Height auto + opacity fade | `--duration-normal`, `--ease-out` |
| Drawer open | translateX(100%) → translateX(0) | `--duration-normal`, `--ease-out` |
| Modal appear | scale(0.97) + opacity 0→1 | `--duration-fast`, `--ease-out` |
| Modal dismiss | opacity 1→0 | `--duration-instant` |
| Hover states | background-color change | `--duration-instant` |
| Badge appear | opacity 0→1 + translateY(2px)→0 | `--duration-fast` |
| Wizard step change | opacity crossfade | `--duration-normal` |

### 7.4 Rules

- No spring physics. No bounce. This is a security tool.
- No skeleton loaders for things that load in <200ms. Just show the content.
- Use skeleton loaders (pulse animation) only for API-dependent content that takes >500ms.
- Never animate layout shifts. If content causes a reflow, it should appear instantly.

---

## 8. Iconography

### 8.1 Icon Set

Use **Lucide** (the fork of Feather). It's already in the React ecosystem via `lucide-react`, matches the geometric/minimal aesthetic, and has consistent stroke width.

### 8.2 Sizes

```
Small:   16px  (inline with text, inside badges)
Default: 18px  (buttons, navigation items)
Large:   24px  (empty states, section markers)
```

### 8.3 Stroke

Always 1.5px stroke width. Never filled icons. The outlined style maintains the tool aesthetic.

### 8.4 Key Icons

| Concept | Icon |
|---------|------|
| Run / Attack | `play-circle` |
| Complete | `check-circle` |
| Failed | `x-circle` |
| Running | `loader` (animated spin) |
| Turn | `message-square` |
| Shield / Blue team | `shield` |
| Severity | `alert-triangle` |
| Expand | `chevron-right` (rotates to down) |
| Settings | `settings` |
| New run | `plus` |
| Close | `x` |
| Back | `arrow-left` |

---

## 9. Radius, Shadows & Borders

### 9.1 Border Radius

```css
:root {
  --radius-sm:   4px;    /* Badges, small chips */
  --radius-md:   6px;    /* Buttons, inputs, inline containers */
  --radius-lg:   8px;    /* Cards, stat bar, panels */
  --radius-xl:   12px;   /* Modals, drawers */
}
```

No fully rounded (999px) elements. No circles for anything except status dots.

### 9.2 Shadows

Minimal. The dark theme already provides depth via background elevation.

```css
:root {
  --shadow-sm:   0 1px 2px rgba(0, 0, 0, 0.2);          /* Dropdowns */
  --shadow-md:   0 4px 12px rgba(0, 0, 0, 0.3);         /* Modals */
  --shadow-lg:   0 8px 24px rgba(0, 0, 0, 0.4);         /* Drawers */
}
```

Use shadows ONLY on overlapping elements (modals, drawers, dropdowns). Never on inline cards or sections.

### 9.3 Borders

- Default border: `1px solid var(--border-default)`
- Use borders to define containers (stat bar, turn rows) and interactive element boundaries (buttons, inputs)
- Never use borders purely for decoration
- The left accent bar on turn rows is the ONE exception — it's 3px wide, colored by severity, and serves as a visual scanner

---

## 10. Data Visualization

### 10.1 When to Visualize

Agent Crucible is not a metrics dashboard. Charts and graphs are secondary to the attack narrative. Use data viz only for:

- **Run comparison** — bar chart comparing severity distribution across runs
- **Strategy effectiveness** — success rate by strategy type
- **Aggregate stats** — only when the user has 5+ runs and asks for trends

Never show charts on a single-run results page. The turn timeline IS the visualization.

### 10.2 Chart Style (When Used)

- Bar charts preferred over line charts (discrete runs, not continuous data)
- Use semantic colors only (the 4 status colors)
- No gridlines, no axis labels beyond essentials
- Tooltip on hover with exact values
- Chart background: transparent (sits on `--bg-surface`)

---

## 11. Keyboard & Accessibility

### 11.1 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `N` | New run |
| `↑ / ↓` | Navigate turns |
| `Enter` | Expand selected turn |
| `Escape` | Close drawer / modal |
| `1-9` | Jump to turn N |
| `?` | Show shortcut help |

### 11.2 Focus Management

- All interactive elements must have visible focus rings (`2px solid var(--focus-ring)`, offset 2px)
- Focus trap inside modals and drawers
- After closing a modal, focus returns to the trigger element
- Tab order follows visual order

### 11.3 Screen Reader Considerations

- Turn rows are `role="listitem"` inside a `role="list"`
- Severity badges include `aria-label` with full context: "Severity: High"
- Status dots include `aria-label`: "Run status: Complete"
- Expanding a turn announces the expanded content

### 11.4 Color Contrast

All text passes WCAG AA (4.5:1 ratio minimum):
- `--text-primary` (#eee) on `--bg-base` (#0c0c0c): 17.4:1 ✓
- `--text-secondary` (#999) on `--bg-base` (#0c0c0c): 7.4:1 ✓
- `--text-tertiary` (#666) on `--bg-base` (#0c0c0c): 3.9:1 — use at --text-sm or larger only
- Status colors on their dim backgrounds: all pass AA

---

## 12. Technical Notes

### 12.1 Recommended Stack

| Concern | Choice | Why |
|---------|--------|-----|
| Component primitives | **shadcn/ui** | Unstyled, composable, owns the code. No runtime dependency. |
| Styling | **Tailwind CSS** | Utility-first, matches the design token approach. Configure with the exact values from this doc. |
| Icons | **lucide-react** | Consistent, tree-shakeable, same stroke style. |
| Motion | **CSS transitions** for simple states. **Framer Motion** only for drawer/modal orchestration. | Keep the bundle small. |
| Font loading | Self-host Geist via `@font-face`. No Google Fonts. | Performance, privacy, reliability. |

### 12.2 Tailwind Config Mapping

```js
// tailwind.config.js (key overrides — not exhaustive)
module.exports = {
  theme: {
    colors: {
      bg: {
        base: '#0c0c0c',
        surface: '#141414',
        elevated: '#1c1c1c',
      },
      border: {
        DEFAULT: '#222222',
        subtle: '#1a1a1a',
        focus: '#444444',
      },
      text: {
        primary: '#eeeeee',
        secondary: '#999999',
        tertiary: '#666666',
        ghost: '#444444',
      },
      status: {
        success: '#22c55e',
        danger: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6',
        neutral: '#666666',
      },
    },
    fontFamily: {
      sans: ['Geist', 'system-ui', 'sans-serif'],
      mono: ['Geist Mono', 'SF Mono', 'monospace'],
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.8125rem',
      base: '0.875rem',
      lg: '1.125rem',
    },
    borderRadius: {
      sm: '4px',
      md: '6px',
      lg: '8px',
      xl: '12px',
    },
    spacing: {
      1: '4px',
      2: '8px',
      3: '12px',
      4: '16px',
      5: '20px',
      6: '24px',
      8: '32px',
      10: '40px',
      12: '48px',
      16: '64px',
    },
  },
}
```

### 12.3 File Structure Suggestion

```
src/
  components/
    ui/            ← shadcn primitives (badge, button, dialog, drawer, etc.)
    layout/        ← Sidebar, Header, PageShell
    run/           ← RunHeader, StatBar, TurnRow, TurnDetail, TurnTimeline
    setup/         ← SetupWizard, ScenarioStep, AttackStep, ReviewStep
  lib/
    cn.ts          ← classname utility
    constants.ts   ← severity maps, status maps, icon maps
  styles/
    globals.css    ← CSS variables, Geist font-face, base resets
```

---

## 13. Checklist: Before You Ship a Screen

Run every new screen/component through this:

- [ ] Can I remove an element without losing understanding? (If yes, remove it.)
- [ ] Is any information shown in more than one place? (Deduplicate.)
- [ ] Are there cards inside cards? (Flatten.)
- [ ] Is monospace used for anything that isn't code/hashes/IDs? (Switch to sans.)
- [ ] Is color used for anything that isn't status/severity/interactivity? (Remove it.)
- [ ] Can the user see the primary content without scrolling? (If not, compress the header.)
- [ ] Is there a hero section, tagline, or branding element on an interior page? (Remove it.)
- [ ] Does every label need to be there? (Cut any that are obvious from context.)
- [ ] Would a new user understand the severity of each turn within 2 seconds? (If not, increase the visual signal.)
- [ ] Does this feel like Linear, or does it feel like a Dribbble shot? (Linear wins.)

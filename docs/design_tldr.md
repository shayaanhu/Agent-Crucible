# Agent Crucible — Design TL;DR

> Tool, not toy. Every pixel earns its place by helping the user understand what happened.

---

## The One Rule

**The attack story is the product.** Every design decision asks: "does this help the user understand the attack faster?" If no, remove it.

---

## What This Looks Like

**Linear + Warp.** Dense, fast, professional. Not a Vercel marketing page. Not a Bootstrap dashboard. A security workbench.

**Quiet until it matters.** Default state is monochrome and calm. Color only appears for status/severity. When everything is highlighted, nothing is.

**Progressive disclosure.** Primary content (attacker prompt, target response, blue-team verdict) always visible. Secondary content (converter steps, scorer internals) one click away, inline. Never more than one level of nesting.

---

## Color System

Three background levels, that's it:
- `#0c0c0c` — app base
- `#141414` — surfaces (cards, panels, rows)
- `#1c1c1c` — elevated (modals, drawers, dropdowns)

Five semantic colors, each with one job:
- `#22c55e` success — attack got through, objective matched
- `#ef4444` danger — blocked, high severity
- `#f59e0b` warning — partial match, medium severity
- `#3b82f6` info — neutral, pending, informational
- `#666666` neutral — N/A, dry run, no result

**Never use color for decoration.** No gradients, no tinted surfaces, no colored section headers. If it isn't status/severity/interactivity, it has no color.

---

## Typography

- **Satoshi** for all UI chrome — labels, buttons, navigation, body text
- **JetBrains Mono** for content that IS code: raw prompts, hashes, run IDs, API responses, the run narrative

Kill all-caps monospace labels. `RUN DOSSIER` → `Run dossier` (sans-serif, 13px, medium weight, `--text-tertiary`). Uppercase is acceptable only inside short status badges: `BLOCKED`, `HIGH`.

Four text sizes: 12px / 13px / 14px / 18px. No hero sizes on interior pages.

---

## Layout

```
Sidebar (220px) │ Main content
─────────────────┼──────────────────────────
Logo             │ Compact sticky run header
Run list         │ Stat bar (one container)
─────────────────│ Outcome shimmer bar
+ New run        │ Run narrative (typewriter)
Evaluation       │ Turn timeline
Settings         │
```

- Max content width: 960px
- Page edge padding: 24–32px
- Sidebar: same `--bg-base` as page, separated by `1px solid --border-subtle`

---

## Components That Matter

**Stat bar** — One container, horizontal, dividers between cells. Never individual stat cards. Labels in `--text-xs --text-tertiary`, values in `--text-base --weight-semibold`. Semantic color on values (HIGH is amber, BLOCKED is red).

**Turn row** — The most important component. Left-side vertical timeline with colored node circles (severity color + glow). Attacker block (`--bg-elevated`, red left border, Sword icon). Target block (`--bg-surface`, blue left border, Shield icon). Badges top-right. Expand affordance row at bottom showing counts. No separate cards — it's a linear conversation.

**Badges** — 22px height, 8px padding, 4px radius, uppercase, medium weight. Color + matching `box-shadow` glow. Five variants only.

**Buttons** — Primary (36px, white bg, dark text). Secondary (32px, transparent, outlined). Ghost (32px, no border). No pill shapes (999px radius). Max 6px radius.

**Setup wizard** — Full-replacement steps, not tabs. "Step 1 of 3" + dots, not pill cards. Step 1: clickable scenario grid, not dropdowns. One thing per step. No echo panels.

**Modals** — `--bg-surface`, 12px radius, `1px solid --border`. No accent-colored borders. No gradient backgrounds.

---

## Motion

Quick and purposeful. Never bouncy. This is a security tool.

| What | Duration | Easing |
|------|----------|--------|
| Hover states | 100ms | instant |
| Modal appear | 150ms | ease-out |
| Drawer slide | 200ms | ease-out |
| Turn stagger | 60ms between rows | ease-out |
| Typewriter narrative | ~22ms/char | — |
| Shimmer bar (running) | 2s loop | linear |
| Sidebar pulse dot | 2s loop | ease-in-out |

No spring physics. No skeleton loaders under 500ms. No layout shift animations.

---

## Anti-Patterns (Never Do These)

- Hero sections or taglines on interior pages
- Cards nested inside cards
- All-caps monospace labels on UI chrome
- Echo panels that repeat what the user just selected
- Gradient backgrounds or tinted decorative surfaces
- Gold/cream accent colors
- The same data point in more than one place
- Decorative elements whose removal would not reduce understanding
- 999px border radius on anything except status dots
- Monospace for navigation, labels, or button text

---

## The Checklist

Before shipping any screen:
- [ ] Can I remove an element without losing understanding? (Remove it.)
- [ ] Is information shown in more than one place? (Deduplicate.)
- [ ] Cards inside cards? (Flatten.)
- [ ] Monospace on non-code content? (Switch to Satoshi.)
- [ ] Color used decoratively? (Remove it.)
- [ ] Hero section or tagline on an interior page? (Delete it.)
- [ ] Does this feel like Linear, or like a Dribbble shot? (Linear wins.)

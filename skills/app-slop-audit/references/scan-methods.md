# Scan Methods — how to gather evidence for an audit

Pick route(s) based on what the user handed you. Code + screenshot is strongest; either
alone is acceptable but weaker, and each has blind spots. Reconcile sources before scoring.

## Route 1 — Code scan (SwiftUI / AppKit)

Grep the app source for the code signals in `slop-patterns.md`. Walk in this order:

1. **Color** — search `\.tint(`, `accentColor`, `Color(red`, `LinearGradient`, `purple`, `indigo`,
   `RoundedRectangle(cornerRadius:`. Flag AI-purple accents and hardcoded RGB that ignore dark mode.
2. **Material/cards** — search `Material`, `ultraThinMaterial`, `thinMaterial`, `.background(.fill`, `cornerRadius`.
   Count per screen; flag material-on-nothing and card-soup.
3. **Typography** — search `.font(`, `.fontWeight`, `.bold()`, `Design.serif`, `.monospaced`.
   Judge the scale and emphasis discipline.
4. **Controls** — search `buttonStyle`, custom control reimplements (`@GestureState`, big `Gesture` on a row),
   `focusEffectDisabled`, `.focusable(false)`.
5. **Icons** — search `Image(systemName:)` and any literal emoji in `Text`.
6. **State/motion** — search `animated`, `repeatForever`, `ProgressView`, `.redacted`, `accessibilityReduceMotion`.
7. **Layout/accessibility** — search `.frame(width:`, `.frame(height:`, `accessibilityLabel`, `.help(`, toolbars.

Record each finding as a row with **category, pattern id, severity, file:line, evidence**. Do not
dump raw grep output into the report — distill into findings.

## Route 2 — Screenshot / rendered scan

Use a rendered image (user-provided, or captured via XcodeBuildMCP) and read the VISUAL signals:

- **Color** — anything default purple/blue-gradient-heavy; warm-beige premium autopilot.
- **Cards/materials** — every pane bounded by a rounded box; frosted panels over flat content.
- **Type** — flat weight, no hierarchy, serif accent words, monospaced prose.
- **Layout** — centered floating controls in a void; fixed-ish widths that clip on resize; misaligned rows.
- **Controls/affordance** — no visible primary CTA; icon-only toolbar with no tooltip.
- **Content** — placeholder names ("Jane Doe"), lorem, seeded sample data.
- **State** — blocking full-screen spam of spinners; ambient looping motion; items that don't react on hover.

## Route 3 — Both (recommended)

1. Run Route 2 on the screenshot FIRST to form the visual reads.
2. Run Route 1 to confirm each visually-suspected pattern in source.
3. **Reconcile:** any finding present in one route but absent in the other gets a second look —
   the cross-check is exactly what catches slop that hides in code (or in render only).

## Output

Do NOT write prose only. Produce a findings table the scorer can consume:

| # | Category | Pattern | Severity | Evidence (file:line or screen region) | Anti-slop fix |
|---|----------|---------|----------|----------------------------------------|---------------|

Pass this table to `scripts/score_slop.py` to derive the slop index.
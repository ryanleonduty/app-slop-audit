---
name: app-slop-audit
description: >
  Audit a native macOS/iOS app (SwiftUI/AppKit) for UI slop — generic, templated,
  AI-default design — and produce a numbered slop inventory plus concrete anti-slop
  fixes, an Apple-HIG-aware remediation recipe, and a scored 0-100 slop index. Works
  from SwiftUI/AppKit source code AND/OR rendered screenshots. Use whenever the user
  asks to review, assess, score, or improve the design quality of an Apple app, says
  "this looks generic / AI-generated / like slop", wants to catch cookie-cutter UI
  patterns, or wants a before/after design-quality grade before shipping.
---

# App Slop Audit (native macOS / iOS)

Identify and prescribe fixes for generic, templated, AI-default design in Apple apps.
Cross-checks SwiftUI/AppKit code against the rendered UI, then scores the result.

## When to use
- User asks to review / assess / score the design of a macOS or iOS app.
- User says the app "looks like slop", "AI-generated", "boring", "default".
- Before shipping a UI, to catch cookie-cutter patterns.
- Not for: web UIs (use design-taste-front or ui-ux-pro-max), general UX strategy (ui-ux-pro-max),
  or infra work.

## How to use
1. **Gather evidence.** Ask which you have: app source path, a screenshot, or both. More
   evidence = better audit. If only a repo is given, offer the default route below.
2. **Route by input** (full method in `references/scan-methods.md`):
   - Source → grep the code for the signals in `references/slop-patterns.md`.
   - Screenshot → read the alternative entries in `scan-methods.md`.
   - Both → screenshot-first visual reads, then confirm each in source; **reconcile**.
3. **Detect patterns** against `references/slop-patterns.md`. Each finding = category +
   pattern id + severity (CRITICAL/HIGH/MEDIUM/LOW) + evidence (file:line or screen region).
   Flag contextually — verify the app doesn't justify the choice before flagging.
4. **Prescribe fixes** per finding using `references/apple-hig.md` (native SwiftUI/SF/AHIG
   replacements). Produce a numbered inventory table:
   `# | Category | Pattern | Severity | Evidence | Anti-slop fix`.
5. **Score objectively.** Pipe the findings JSON to `scripts/score_slop.py`:
   `cat findings.json | python3 scripts/score_slop.py` → slop index, grade, per-category breakdown.
6. **Report.** State the Design Read (one line: "Reading this as <app kind> for <audience>,
   lean <aesthetic>"), the inventory table, the slop index + grade, and the top 5 highest-value
   fixes. Never fix code unasked — audit first, then offer to apply.

## Scope
This skill handles native Apple app UI design audit and slop remediation. It does NOT
handle: generating new designs from scratch (taste-skill), web/frontend slop, or CX/
product-strategy decisions.

## Rules
- **Audit-first, fix-on-request.** Produce findings and fixes; apply changes only when asked.
- **Context over rules.** A rule fires only when the app offers no justification. Don't erase a
  deliberate brutalist/custom-control decision to hit a cleaner score.
- **Reconcile code and render.** A code-flagged pattern invisible in the render is lower priority;
  a render defect with no code signal means you missed a code pattern — re-scan.
- **Objective score.** Always derive the index via the script, never by feel.
- **Dark mode + a11y are not optional.** Hardcoded light-only colors and stripped focus rings are
  CRITICAL, not style nits.

## References
- `references/slop-patterns.md` — the pattern catalog (detection + anti-slop fixes).
- `references/apple-hig.md` — native HIG replacements and macOS-specific verbs.
- `references/scan-methods.md` — code / screenshot / combined evidence-gathering.
- `scripts/score_slop.py` — JSON findings → 0-100 slop index.

For requesting live renders on macOS, prefer `XcodeBuildMCP` (`session_show_defaults` → build/run → screenshot) when defaults are configured.
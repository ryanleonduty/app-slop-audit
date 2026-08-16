# Apple HIG Quick Reference (platform-specific fixes)

The native targets for the anti-slop fixes. Skim as needed; full authority is Apple's
Human Interface Guidelines. These are the macOS/iOS-native verbs to offer as replacements —
not generic "make it prettier".

## macOS chrome (macOS-specific)
- **Sidebar** — `NavigationSplitView` with a `List` as sidebar for app-level navigation. Use `.navigationTitle` + `.navigationSubtitle` for context. Sidebar selects one content pane; don't cram a second nav into it.
- **Toolbar** — `.toolbar { ToolbarItem(placement: .primaryAction) }` for the main action, `.secondaryAction` for lesser. Keep the default action prominent.
- **Thousands of windows** — a utility should not masquerade as a document app with `.window()`/`.scene` proliferation. Match window count to task.
- **`.help(Text(...))`** — mandatory tooltip on icon-only toolbar actions (macOS).
- **Focus ring** — macOS shows focus on controls via the ring. Do not `.focusable(false)` interactions away; keyboard nav must move visibly.

## Typography (SF Pro)
- Use system fonts; `Font` sizes by role (`largeTitle`, `title`, `title2`, `title3`, `headline`, `subheadline`, `body`, `footnote`, `caption`).
- `.fontWeight` pairing: regular for body, semibold/bold for the lead when a display face isn't justified. Weights are role-driven, not shouted.
- `.monospacedDigit()` for tabular numbers (times, prices, durations) so digits align.

## Color (semantic)
- Use semantic roles: `.primary`, `.secondary`, `.tertiary`, `.background`, `.fill`, `.separator`, `.placeholder`, `.accentColor`.
- `.colorSchemeContrast` / `@Environment(\.colorScheme)` for brand colors, never fixed RGB that ignores dark mode.
- One accent. `Color.accentColor` on controls; override once per app, stay consistent.

## Materials
- `.regularMaterial` / `.thinMaterial` / `.ultraThinMaterial` read *over* content. Use them when there is live content behind (scrolling list, panels). Do not use a material when the surface reveals nothing.
- `.background(.fill.tertiary, in: RoundedRectangle(cornerRadius: ...))` = a filled container. Apply to ONE containment layer; flat everywhere else.

## Controls
- `Toggle`, `Stepper`, `Slider`, `Picker`, `TextField`, `DatePicker` — native unless a real reason.
- Buttons: `.borderedProminent` (primary), `.bordered` (secondary), `.plain` (toolbar/inline). `.help` on icon-only.
- `.buttonStyle(.borderless)` on macOS can hide borders; use deliberately.

## Accessibility (gate every feature)
- Contrast ≥ 4.5:1 normal text, ≥ 3:1 large text.
- `accessibilityLabel` (+ macOS `.help`) on icon-only controls.
- Keyboard: full tab order; focus ring visible.
- Reduced motion: `@Environment(\.accessibilityReduceMotion)` gates every animation.
- Dynamic type: content reflows; no fixed frames that clip.

## Motion
- Animation rides on documented transitions: `.animation/`/.withAnimation` toggled by state, `.contentTransition(.numericText())` for numbers. No ambient forever-loop.
- Skeleton loading: `.redacted(reason: .placeholder)` reserves layout.

## Getting a rendered read on macOS
- If the source is available, also cross-check the live app: launch via `XcodeBuildMCP` (`session_show_defaults` → `build_run_sim`/run), capture a screenshot, and compare the render against the audit conclusions. A pattern flagged in code that is invisible in the render is lower priority; a visible defect with no code signal means you missed a code pattern — reconcile both.
- Size the window to several states (default, small, large, dark mode, Reduce Motion on) before finalizing the score.

## What NOT to do
- Do not prescribe a specific color hex "because it looks premium" without a brand reason.
- Do not tell the user to install a font or asset that isn't present; prefer system resources.
- Do not "fix" a legitimate design decision (brutalist tool, custom control for a novel interaction) just to satisfy a pattern rule. Verify intent before flagging.
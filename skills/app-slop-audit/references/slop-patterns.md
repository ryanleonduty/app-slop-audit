# Native Slop Pattern Catalog (macOS / iOS)

The detection knowledge for this skill. Slop = generic, templated, unconsidered output
the model shipped because it defaulted instead of read the room. Each pattern lists:

- **Code signal** — what to look for in SwiftUI / AppKit source
- **Visual signal** — how it reads in a rendered screenshot
- **Severity** — `CRITICAL` (broken / accessibility), `HIGH` (visibly generic),
  `MEDIUM` (inconsistent), `LOW` (polish)
- **Anti-slop fix** — the concrete native replacement

Every check is **contextual**. Do not flag a rule just because it appears; flag it when the
app does not justify the choice. A brutalist tool for a power user may legitimately break a "polish" rule.

## A. Typography & type hierarchy

1. **Flat type scale**
   - Code: `.font(.body)` on nearly every Text; `.font(.headline)` never used to lead a section; the ~15pt default everywhere.
   - Visual: no optical hierarchy; title reads same weight/size as body.
   - Severity: HIGH.
   - Fix: build an explicit scale from `.largeTitle`/`.title` for the app's lead, `.headline`/`.title2` for sections, `.body` for content, `.caption`/`.footnote` for metadata. Lead at least ~4 steps above body.
2. **Bold-as-only-emphasis**
   - Code: `.bold()` used wherever emphasis is needed; `.fontWeight` scattered ad hoc; no weight pairing discipline.
   - Visual: "shouting" everywhere, no calm.
   - Severity: MEDIUM.
   - Fix: pick a 2-3 weight pairing (regular/bold or light→semibold/black) and apply by hierarchy role, not ad hoc stress. Prefer type-scale contrast over `.bold()` noise.
3. **Serif-for-creative autopilot**
   - Code: `Font.custom("Georgia", ...)` / `Design.serif` injected to feel "editorial."
   - Visual: random serif word breaks a sans headline.
   - Severity: MEDIUM (the classic "creative = serif" AI tell).
   - Fix: default sans (SF Pro); reach for serif only when the brand genuinely calls for it, then pair consistently. Never mix a serif accent word into a sans headline as a styling move — use italic/bold of the same face.
4. **Monospace misuse**
   - Code: `.font(.system(.body, design: .monospaced))` for body text that isn't code/data.
   - Visual: code font where it doesn't belong.
   - Severity: LOW.
   - Fix: keep monospaced for numbers, hashes, filenames, code — not prose.

## B. Color

5. **AI-purple/blue default accent**
   - Code: `.tint(.purple)`, `.accentColor(.indigo)`, `LinearGradient` purple→blue on headers; `Color.purple.gradient` CTAs.
   - Visual: the app "looks like every AI demo."
   - Severity: HIGH (the most common native tell).
   - Fix: neutral substrate (gray/`Color.secondary`-family) with ONE high-contrast accent chosen from the brand — emerald, electric blue, deep rose, burnt orange — not the canned violet. Max one accent color; saturation < 80%.
6. **Hardcoded light-only colors**
   - Code: `Color(red: green: blue:)`, `Color(white:)`, hex-coerced `Color(NSColor(...))` for text/bg that never adapt.
   - Visual: washed-out banks / invisible dark text in dark mode; clashes in light mode.
   - Severity: CRITICAL (breaks dark mode + contrast).
   - Fix: use semantic system colors (`.primary`, `.secondary`, `.background`, `.fill`, `.separator`) and `@Environment(\.colorScheme)` / `.colorSchemeContrast` where a real brand color is required.
7. **Warm-beige premium autopilot**
   - Code: cream/beige backgrounds + brass/oxblood/ochre accents + espresso text — the LLM "premium consumer" palette on every product-ish app.
   - Severity: HIGH.
   - Fix: this is a tell. If the brief says premium, still rotate; one beige+brass app reads as indistinguishable from every other.

## C. Materials & glass

8. **Material/glass everywhere**
   - Code: `.ultraThinMaterial` / `.thinMaterial` background on panels, rows, toolbars, headers — glassmorphism slapped on without deciding what sits behind it.
   - Visual: frosted blur over nothing; "just making it Apple-like."
   - Severity: HIGH.
   - Fix: use materials only to convey layered context — content over a scrolling backdrop, inspector/detached panels, transient overlays. Confirm actual depth exists behind the blur.
9. **Rounded-rect card overload**
   - Code: `RoundedRectangle(cornerRadius: 16)` under every element; `.background(.fill, in:)` on rows, buttons, headers, list backdrops simultaneously.
   - Visual: "card soup" — everything floats in its own rounded box.
   - Severity: HIGH.
   - Fix: one containment idiom for ONE content layer; let the rest sit flat on the background. Reduce cards, don't stack cards on cards.
10. **Inconsistent corner radius**
    - Code: 8, 12, 16, 999 (capsule) used interchangeably with no token.
    - Visual: roundedness feels random from control to control.
    - Severity: MEDIUM.
    - Fix: define a small radius scale (e.g. 6 / 10 / 14 / full) and apply one per shape role across the app.

## D. Gradients & depth

11. **Background gradient slop**
    - Code: `LinearGradient` or mesh-style background on every screen; gradient used as decoration rather than to indicate affordance/state.
    - Visual: every pane has a color wash.
    - Severity: MEDIUM.
    - Fix: flat backgrounds with one intentional point of depth emphasis; gradient only where it conveys meaning (active call-out, selected state).
12. **Shadow misuse**
    - Code: `.shadow(radius:)` on every card/row to imply depth that the layout doesn't support.
    - Visual: floating-heavy, "pop" look.
    - Severity: LOW.
    - Fix: apply shadowing sparingly; rely on fill/separator hierarchy, not ubiquitous shadows.

## E. Layout

13. **Fixed-frame layout**
    - Code: `.frame(width: 420)` / `.frame(height:)` on content that should reflow; hardcoded sizes that break under dynamic type, window resize, or larger accessibility fonts.
    - Visual: clipping, dead space, or cramped content when the window grows.
    - Severity: CRITICAL if content clips/locks, else HIGH.
    - Fix: use intrinsic sizing, `layoutPriority`, `GeometryReader`-driven relative layout for platforms where frames should scale; test with dynamic type + window resize.
14. **Floating centered island**
    - Code: one `VStack` centered horizontally with `.frame(maxWidth: .infinity)` pushing everything to a middle column; "product landing as a utility app" structure.
    - Visual: a few centered controls floating in a void, no information hierarchy.
    - Severity: HIGH.
    - Fix: adopt real app chrome — toolbar, sidebar/navigation, content regions — and distribute by task importance, not left-right symmetry.
15. **One-config the other does not match**
    - Code: `.frame(maxWidth: .infinity, alignment: .trailing)` on labels but controls aligned center; mixed contextual menu vs button idioms.
    - Visual: misaligned rows, tangled vertical rhythm.
    - Severity: HIGH (consistency).
    - Fix: single alignment convention per container; align on a shared grid so text baselines line up.

## F. Controls & interaction

16. **Custom reimplementation of native controls**
    - Code: hand-built toggle/stepper/slider/text-field from stacks + gestures instead of the native `Toggle`/`Stepper`/`Slider`.
    - Visual: nonstandard controls with slightly-off hit targets and no platform behaviors.
    - Severity: HIGH (per Apple HIG: prefer native controls).
    - Fix: use the system `Toggle`, `Stepper`, `Slider`, `Picker`, `TextField`; customize styling only when branding requires it, and only over the native control.
17. **Plain-button everything**
    - Code: `.buttonStyle(.plain)` on every action, so nothing looks clickable; no primary/secondary CTA distinction.
    - Visual: no affordance; can't tell buttons from labels.
    - Severity: HIGH.
    - Fix: use `.borderedProminent` for the primary action, `.bordered` for secondaries, `.plain` only for toolbars/inline text actions. Keep one dominant CTA per pane.
18. **All-bordered, no primary**
    - Code: every button `.bordered`; no `.prominent` leads; user must scan many identical buttons.
    - Visual: flat row of equal CTAs, no decision hierarchy.
    - Severity: MEDIUM.
    - Fix: promote the highest-consequence action to `.borderedProminent`; demote the rest.
19. **Removed focus / feedback**
    - Code: `.focusable(false)`, `.focusEffectDisabled()`, no hover/press/disabled visual states.
    - Visual: keyboard operators can't tell focus; no press feedback.
    - Severity: CRITICAL (accessibility) if focus rings stripped.
    - Fix: keep visible focus rings and distinct hover/pressed/disabled states; only strip focus where unavoidable and replace with an equally discoverable alternative.
20. **Icon-only with no label**
    - Code: `Image(systemName:)` button with no `.help()`, no `accessibilityLabel`/`accessibilityIdentifier` (macOS: `.help(Text(...))`).
    - Visual: mysterious icon-only toolbar with no tooltip and no VoiceOver name.
    - Severity: CRITICAL (accessibility).
    - Fix: add `.help(...)` tooltips on macOS and `accessibilityLabel` so icon-only actions are identified.

## G. Content & data

21. **Placeholder-slop**
    - Code: `"Jane Doe"`, `"Lorem ipsum"`, `"Item 1.2.3"`, `id: UUID()` sample rows baked in as if real; sidebar/empty states seeded with fake data.
    - Severity: CRITICAL (must never ship).
    - Fix: real bindings; empty states with a meaningful message + action, never fake content.
22. **Emoji as icons**
    - Code: emoji glyphs in text/buttons where an SF Symbol or label belongs.
    - Visual: inconsistent weight / color / alignment of emoji icons.
    - Severity: MEDIUM.
    - Fix: SF Symbols first; emoji only for explicitly playful/social tones and used consistently.
23. **Inconsistent SF Symbol style**
    - Code: `.symbolVariant(.fill)` on some icons, plain on others, random `.bold` on symbols.
    - Visual: icon system doesn't look like one family.
    - Severity: MEDIUM.
    - Fix: pick one symbol variant scheme (monochrome fill / stroke) and one rendering mode app-wide; mix `.hierarchical`/`.palette` only with intent.

## H. State & motion

24. **Blocking spinner everywhere**
    - Code: `ProgressView()` full screen instead of skeletons for >1s loads; endless spinner when data is slow.
    - Visual: dead flickering while waiting.
    - Severity: MEDIUM.
    - Fix: use `.redacted(reason: .placeholder)` skeletons to reserve content shape; keep an in-context spinner only for quick indeterminate waits.
25. **Infinite decorative motion**
    - Code: endless `.repeatForever(autoreverses: true)` on loading rings, pulsing highlights, ambient rotation on everything.
    - Visual: busy, distracting UI.
    - Severity: MEDIUM.
    - Fix: motion communicates state; once a condition is met, stop animating. Respect `accessibilityReduceMotion` for every animation.
26. **No reduced-motion respect**
    - Code: `.animation(...)` never gated on `@Environment(\.accessibilityReduceMotion)`; motion that disregards the user's Reduce Motion setting.
    - Severity: CRITICAL (accessibility / causes vertigo).
    - Fix: gate all non-essential animation on `accessibilityReduceMotion`; use opacity over translation for motion-sensitive users.

## I. Density & spacing

27. **Divider / padding stacking**
    - Code: `Divider()` between every row AND `.padding()` piling up; visual noise from over-separation.
    - Visual: stripey layout, jumpy.
    - Severity: LOW.
    - Fix: separate with whitespace first; use a separator only where a hard divider is required; keep vertical rhythm on a consistent 4/8pt grid.
28. **No anti-alias / crispness care**
    - Code: `.background(.ultraThinMaterial)` edges, or labels scaled non-integer, or `RoundedRectangle` stroke widths that look blurry at 1px.
    - Visual: fuzzy borders, inconsistent weight.
    - Severity: LOW.

---
## Severity weight map (for the score index)
| Severity | Weight |
|----------|--------|
| CRITICAL | 5.0 |
| HIGH | 3.0 |
| MEDIUM | 1.5 |
| LOW | 0.5 |

Score = normalized sum of weighted findings; see `scripts/score_slop.py`.
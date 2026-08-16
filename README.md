# App Slop Audit

**Audit a native macOS / iOS app (SwiftUI / AppKit) for UI slop - generic, templated,
AI-default design - and get a numbered slop inventory, concrete anti-slop fixes, an
Apple-HIG-aware remediation recipe, and an objective 0-100 slop index.**

Working from **source code**, **rendered screenshots**, or **both**, this skill catches the
cookie-cutter patterns a model ships when it defaults instead of reading the room: flat type
scales, AI-purple accents, rounded-rectangle card soup, blocking full-screen spinners, warm-beige
"premium" autopilot, and more. It then prescribes native SwiftUI / AppKit replacements and scores
the result through a deterministic script - never by feel.

> This skill was created using **[Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)**,
> the anti-slop Agent-Skills framework. Where taste-skill guards **web/frontend** design, this skill
> guards the **native Apple** slice of the same problem, and reuses its audit-first discipline and
> "context over rules" philosophy.

---

## Why it exists

AI-generated UI has a recognizable "tell": it reaches for the same default styling regardless of
the app's audience, purpose, or platform. On Apple platforms that slop is particularly jarring
because it fights the platform's own design language (SF Pro, semantic colors, HIG chrome, native
controls, dark mode). This skill exists to catch and fix that gap before you ship.

It complements, rather than replaces, design-generation skills:

| Concern | Tool |
| --- | --- |
| Generate a new Apple app design from a brief/screenshot | `taste-skill` and its image-generation skills |
| **Audit and grade an existing Apple app for slop** | **this skill (`app-slop-audit`)** |
| Web / frontend design slop | `taste-skill`, `ui-ux-pro-max`, etc. |
| General UX / product strategy | `ui-ux-pro-max` |

---

## What it does

Given an app (source path, screenshot, or both), `app-slop-audit`:

1. **Gathers evidence** - asks which inputs you have; more evidence = stronger audit.
2. **Routes by input** - code scan, screenshot read, or a screenshot-first + code-confirmed run
   with a **reconcile** pass that cross-checks both.
3. **Detects patterns** against a catalog of ~30 native AI-tells, each flagged contextually and
   tagged with severity (`CRITICAL` / `HIGH` / `MEDIUM` / `LOW`) plus `file:line` or screen-region
   evidence.
4. **Prescribes fixes** using an Apple-HIG-native replacement table (semantic colors, role-driven
   type, real containment idioms, focus-ring retention).
5. **Scores objectively** - pipes the findings through `scripts/score_slop.py` to derive a 0-100
   slop index, a magnitude grade, and a per-category breakdown.
6. **Reports** - a one-line Design Read, the numbered findings table, the index + grade, and the
   top 5 highest-value fixes. It **does not mutate your code unasked** - audit first, fix on request.

### Example score output

```json
{
  "slop_index": 22.4,
  "grade": "LEAN — minor inconsistencies only.",
  "finding_count": 2,
  "categories": {
    "color":       { "count": 1, "weighted": 3.0 },
    "typography":  { "count": 1, "weighted": 1.5 }
  }
}
```

---

## How it works (the files)

The skill lives in `skills/app-slop-audit/`.

| File | Purpose |
| --- | --- |
| `SKILL.md` | Entry point - when to use, the workflow, scope, and hard rules. |
| `references/slop-patterns.md` | The detection catalog. Each pattern lists a code signal, a visual signal, a severity, and an anti-slop fix. |
| `references/apple-hig.md` | Apple HIG-native replacements: SF Pro typography, semantic colors, macOS chrome, native controls, accessibility gates. |
| `references/scan-methods.md` | How to gather evidence for each input route (code / screenshot / both) and when to reconcile. |
| `scripts/score_slop.py` | Deterministic scorer: `cat findings.json \| python3 scripts/score_slop.py` → index + grade + breakdown. |
| `agents/grader.md` | Eval grader agent that scores a run against the assertion set. |
| `evals/evals.json` | Evaluations - concrete cases with PASS/FAIL assertions for verifying behavior. |

### Detected pattern categories (from `slop-patterns.md`)

- **A. Typography & type hierarchy** - flat type scales, bold-as-only-emphasis, serif-for-creative
  autopilot, monospace misuse.
- **B. Color** - AI-purple/blue default accents, warm-beige "premium" autopilot, hardcoded RGB
  that ignores dark mode.
- **C. Material & cards** - card soup, rounded-rect-on-everything, frosted material over flat content.
- **D. Layout** - centered floating controls in a void, equal-sided feature grids, fixed widths that clip.
- **E. Controls & affordance** - no visible primary CTA, icon-only toolbars with no tooltip,
  decorative reimplementations of native controls.
- **F. State & motion** - blocking full-screen spinners, ambient forever-loops, un-reactive items.
- **G. Content & accessibility** - placeholder/lorem data, hardcoded light-only colors, stripped
  focus rings (both CRITICAL, not nits).

### Scoring model (`score_slop.py`)

The index is derived from **categories**, not raw finding count, so fixing one systemic lever lifts
the whole index. Severities weight findings (`CRITICAL` > `HIGH` > `MEDIUM` > `LOW`), and
accessibility defects count extra. Finding count is capped so a long trivial list can't dominate.
The output is always reproducible from the same findings JSON.

---

## Non-goals / out of scope

- **Generating new Apple designs from scratch** - use `taste-skill` / image-generation skills.
- **Web / frontend slop** - use `taste-skill` or `ui-ux-pro-max`.
- **General UX / CX strategy** - use `ui-ux-pro-max`.
- **Rewriting code without a request** - this skill audits and prescribes; it never applies
  changes unless you ask.

---

## Installation

### As a Claude Code skill (plugin marketplace)

Add this repo as a marketplace, then install the skill:

```bash
/claude mcp add app-slop-audit -- marketplace https://github.com/ryanleonduty/app-slop-audit
```

Or reference `.claude-plugin/marketplace.json` directly when adding the plugin.

### With the `agent-skills` CLI

The repo follows the [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
convention (each skill in `skills/<name>/` with a `SKILL.md`), so it installs with `npx skills add`:

```bash
npx skills add https://github.com/ryanleonduty/app-slop-audit
```

Install the single skill by its install name (the `name:` field in the SKILL frontmatter):

```bash
npx skills add https://github.com/ryanleonduty/app-slop-audit --skill "app-slop-audit"
```

You can also copy `skills/app-slop-audit/SKILL.md` and its `references/`, `scripts/`, `agents/`,
and `evals/` folders into your project, or paste them into a Claude/Codex/ChatGPT conversation.

---

## Usage

Invoke the skill when you want a design-quality audit of an Apple app, or when a UI reads as
generic / AI-generated / "like slop":

- "Review / assess / score the design of my macOS app."
- "This SwiftUI screen looks like slop - audit it."
- "Catch cookie-cutter patterns before I ship."
- "Before/after design-quality grade of a native app."

Provide the app **source path**, a **screenshot**, or **both** - the more evidence, the stronger
the audit and the 0-100 grade.

---

## Development & evaluation

- **Evals** live in `skills/app-slop-audit/evals/evals.json` - concrete cases with PASS/FAIL
  assertions (e.g. "code-scan catches slop", "context respects deliberate choice",
  "rendered visual read").
- **Grading** is wired through `skills/app-slop-audit/agents/grader.md`, which scores a run against
  the assertion set and is strict that a named finding must carry a concrete native fix to pass.
- **Local registry**: `source ./skill.sh app-slop-audit` resolves the skill to its `SKILL.md` path.

---

## Contributing

Feedback and pull requests welcome. When adding a pattern, keep the `slop-patterns.md` row format
(code signal / visual signal / severity / anti-slop fix) and keep every fix Apple-native. When
changing the scoring model, update `score_slop.py` and the evals.

---

## License

[MIT](LICENSE).

Built with and inspired by [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) (MIT).
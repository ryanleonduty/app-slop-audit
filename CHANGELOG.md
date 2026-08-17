# Changelog

All notable changes to app-slop-audit live here. The repo follows SemVer-ish
discipline: experimental pre-releases iterate freely; stable releases lock the
skill contract (install name, workflow, findings schema).

---

## [Unreleased]

### Repo

- Initial public release of the `app-slop-audit` skill.
- Repo structure modeled on the [taste-skill](https://github.com/Leonxlnx/taste-skill)
  convention (vercel `agent-skills` compatible layout, `.claude-plugin` manifests).

---

## 1.1.0 - 2026-08-16

Robustness, calibration, and deeper platform coverage.

### Added
- **`references/patterns.json`** - machine-readable single source of truth: 33 pattern ids
  (id/category/severity/title), severity/category/evidence weights, and the scoring ceiling.
  `score_slop.py` reads it and no longer hardcodes a weight.
- **Evidence weighting** in the scorer - `screenshot` reads are discounted, `combined`
  (code-confirmed-from-render) counts most; omitted default `code` keeps legacy scores identical.
- **Before/after delta** - pass `{"before": [...], "after": [...]}` for a regression grade
  (negative = improvement).
- **`--validate`** flag - schema check (unknown id/severity/category/source) with nonzero exit.
- **`tests/test_score_slop.py`** - 20 self-running unit tests (no dependencies).
- **`examples/findings.json` + `examples/report.json`** - a worked example audit and its report.
- **`examples/before-after.json` + `examples/before-after-report.json`** - a before/after redesign
  example (`97.7 SEVERE -> 23.0 LEAN`, `delta -74.7`) and its generated report.
- **`.github/workflows/ci.yml`** - runs unit tests, schema validation, register-integrity/title
  cross-check, and report reproducibility on every push/PR.
- **New patterns (J)** - Liquid Glass on everything, iOS default system-blue tint, TabView-as-default
  navigation, system-gesture clash, sheet-vs-full-screen misuse. Plus an AppKit scope note.

### Changed
- **Scoring ceiling recalibrated** from 28 to 45 category-weighted units (kept in `patterns.json`),
  so realistic audits spread across the scale instead of saturating at 100.
- **SKILL.md hardened** - SwiftUI scope honesty (AppKit translation documented), a defined top-5
  ranking rule (`severity_weight x category_weight`), and a before/after step.
- **`evals/evals.json`** - added before/after, fixture-roundtrip/schema, and newest-OS-tells cases.
- **`slop-patterns.md`** - hardcoded weight table removed in favor of the `patterns.json` pointer.

---

## 1.0.0 - 2026-08-16

Initial release. Single-skill portfolio for auditing native Apple app UI slop.

### Skill

- **SKILL.md** - the runnable skill. Describes when to use it, the evidence-gathering
  workflow, the scoring step, and the audit-first rules.
- **references/slop-patterns.md** - the detection catalog: typography, color,
  material/cards, layout, controls, icons, state/motion, content, accessibility.
  Each pattern lists code + visual signals, severity, and an anti-slop fix.
- **references/apple-hig.md** - Apple HIG-native replacements (SF Pro, semantic
  colors, macOS chrome, accessibility gates).
- **references/scan-methods.md** - code / screenshot / combined evidence routes and
  the reconciliation rule.
- **scripts/score_slop.py** - deterministic JSON-findings-to-0-100-slop-index scorer.
- **agents/grader.md** - an eval grader agent that scores a run against `evals`.
- **evals/evals.json** - assertion cases for verifying skill behavior.
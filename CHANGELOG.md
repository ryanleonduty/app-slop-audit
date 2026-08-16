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
#!/usr/bin/env python3
"""Self-running unit tests for scripts/score_slop.py. No third-party dependencies.

Run directly (works in CI):
  python3 tests/test_score_slop.py

Each test raises on failure; a summary of PASS/FAIL is printed and the process exits
nonzero if any test failed. Tests read weights from references/patterns.json, so they
double as an integrity check that the catalog registers are consistent.
"""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # skills/app-slop-audit
SCORE_PATH = ROOT / "scripts" / "score_slop.py"
CONFIG_PATH = ROOT / "references" / "patterns.json"

spec = importlib.util.spec_from_file_location("score_slop", SCORE_PATH)
score_slop = importlib.util.module_from_spec(spec)
sys.modules["score_slop"] = score_slop
spec.loader.exec_module(score_slop)


def load_fixture(name: str):
    path = ROOT.parent.parent / "examples" / name  # repo-root/examples
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


PASSES = []
FAILS = []


def check(name: str, condition: bool, detail: str = ""):
    if condition:
        PASSES.append(name)
    else:
        FAILS.append((name, detail))


def fixture_findings():
    return [
        {"id": "ai-purple-blue-accent", "category": "color", "pattern": "AI-purple accent",
         "severity": "HIGH", "source": "code", "evidence": "MainView.swift:10", "fix": ".tint(.emerald)"},
        {"id": "type-flat-scale", "category": "typography", "pattern": "Flat type scale",
         "severity": "HIGH", "source": "combined", "evidence": "MainView.swift:22", "fix": "role-driven scale"},
        {"id": "hardcoded-light-only-colors", "category": "color", "pattern": "Hardcoded light-only",
         "severity": "CRITICAL", "source": "screenshot", "evidence": "win-dark.png", "fix": "semantic colors"},
    ]


def test_schema():
    clean = fixture_findings()
    check("validate: clean findings have no problems", not score_slop.validate(clean))

    bad = [{"severity": "BANANA"}]
    probs = score_slop.validate(bad)
    check("validate: unknown severity is reported", any("severity" in p for p in probs))

    bad2 = [{"pattern": "x", "id": "does-not-exist"}]
    check("validate: unknown pattern id is reported",
          any("pattern id" in p for p in score_slop.validate(bad2)))

    empty = []
    check("validate: empty findings are clean", not score_slop.validate(empty))


def test_index_bounds_and_ranges():
    # No findings -> index 0.
    idx0, _ = score_slop.score([])
    check("score: empty findings -> 0", idx0 == 0.0)

    # A big pile of CRITICAL findings saturates at 100.
    pile = [{"severity": "CRITICAL", "category": "accessibility"} for _ in range(40)]
    idx, _ = score_slop.score(pile)
    check("score: 40 CRITICAL -> saturates at 100", idx == 100.0)

    # A single small LOW finding stays low and within [0,100].
    low = [{"severity": "LOW", "category": "icon"}]
    idx, _ = score_slop.score(low)
    check("score: single LOW within (0, 100]", 0 < idx <= 100)

    # Index never exceeds 100.
    idx, _ = score_slop.score(fixture_findings())
    check("score: fixture within [0,100]", 0 <= idx <= 100)


def test_evidence_weighting():
    base = fixture_findings()  # mixed sources
    idx_base, _ = score_slop.score(base)

    # Screen-only is discounted; confirmed counts more -> their rank orders hold.
    all_shot = [dict(f, source="screenshot") for f in base]
    idx_shot, _ = score_slop.score(all_shot)
    check("score: sending everything to screenshot lowers the index", idx_shot < idx_base)

    all_comb = [dict(f, source="combined") for f in base]
    idx_comb, _ = score_slop.score(all_comb)
    check("score: confirming everything as combined raises the index", idx_comb > idx_base)

    # An omitted source defaults to 'code' and must match an explicit all-code list.
    defaulted = [{k: v for k, v in f.items() if k != "source"} for f in base]
    all_code = [dict(f, source="code") for f in base]
    idx_def, _ = score_slop.score(defaulted)
    idx_code, _ = score_slop.score(all_code)
    check("score: default source == explicit code", idx_def == idx_code,
          f"{idx_def} vs {idx_code}")


def test_severity_ordering():
    one = lambda sev, cat="color": [{"severity": sev, "category": cat, "pattern": "x"}]
    i_crit = score_slop.score(one("CRITICAL"))[0]
    i_high = score_slop.score(one("HIGH"))[0]
    i_med = score_slop.score(one("MEDIUM"))[0]
    i_low = score_slop.score(one("LOW"))[0]
    check("score: CRITICAL > HIGH > MEDIUM > LOW",
          i_crit > i_high > i_med > i_low,
          f"{i_crit} > {i_high} > {i_med} > {i_low}")


def test_category_weights_apply():
    # Accessibility (1.6) outranks icon (1.0) for the same severity.
    a = score_slop.score([{"severity": "MEDIUM", "category": "accessibility"}])[0]
    b = score_slop.score([{"severity": "MEDIUM", "category": "icon"}])[0]
    check("score: accessibility category weighs more than icon", a > b, f"{a} vs {b}")


def test_legacy_backward_compat():
    # The old (v1) input shape — no ids, no source — still scores.
    legacy = [{"category": "color", "pattern": "AI-purple", "severity": "HIGH",
               "evidence": "X.swift:1", "fix": "use .tint(.emerald)"},
              {"category": "typography", "pattern": "flat scale", "severity": "MEDIUM",
               "evidence": "Y.swift:2", "fix": "use .title scale"}]
    idx, _ = score_slop.score(legacy)
    check("backward-compat: legacy v1 input still scores in [0,100]", 0 <= idx <= 100)


def test_before_after_delta():
    before = fixture_findings()
    after = [f for f in before if f["severity"] != "CRITICAL"]
    b_idx, _ = score_slop.score(before)
    a_idx, _ = score_slop.score(after)
    delta = round(a_idx - b_idx, 1)
    check("delta: removing a CRITICAL lowers the index (negative delta)",
          delta < 0, f"delta={delta}")


def test_patterns_register_integrity():
    cfg = json.loads(CONFIG_PATH.read_text())
    ids = [p["id"] for p in cfg["patterns"]]
    check("patterns: ids are unique", len(ids) == len(set(ids)))
    check("patterns: severities all valid",
          all(p["severity"] in score_slop.VALID_SEVERITIES for p in cfg["patterns"]))
    check("patterns: categories all valid",
          all(p["category"] in score_slop.VALID_CATEGORIES for p in cfg["patterns"]))


def test_fixture_validates_and_roundtrips():
    try:
        payload = load_fixture("findings.json")
    except FileNotFoundError:
        check("fixture: examples/findings.json exists", False)
        return
    findings = payload if isinstance(payload, list) else payload.get("after", [])
    check("fixture: examples/findings.json passes --validate",
          not score_slop.validate(findings),
          "; ".join(score_slop.validate(findings)))
    idx, _ = score_slop.score(findings)
    check("fixture: scores a numeric 0-100 index", 0 <= idx <= 100)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - surface any failure as a FAIL
            FAILS.append((fn.__name__, f"{type(exc).__name__}: {exc}"))

    for name, detail in FAILS:
        print(f"FAIL  {name}  {detail}")
    print(f"\n{len(PASSES)} passed, {len(FAILS)} failed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
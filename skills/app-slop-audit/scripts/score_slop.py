#!/usr/bin/env python3
"""score_slop.py — turn a findings table into an objective 0-100 slop index.

Reads JSON findings on stdin (or a file path arg) and prints the aggregate
slop index, per-category breakdown, and a magnitude grade.

Input contract (array of findings):
[
  {
    "category": "color",          // required
    "pattern": "AI-purple accent",
    "severity": "HIGH",           // CRITICAL | HIGH | MEDIUM | LOW
    "evidence": "SettingsView.swift:42",
    "fix": ".tint(.emerald) ..."  // optional
  }
]

Usage:
  cat findings.json | python3 script/score_slop.py
  python3 script/score_slop.py findings.json
"""

import json
import sys
from typing import List, Optional

# Severity → weight (from references/slop-patterns.md)
SEVERITY_WEIGHT = {"CRITICAL": 5.0, "HIGH": 3.0, "MEDIUM": 1.5, "LOW": 0.5}

# Category → multiplier (these are the systemic levers; fix one, lift the whole index)
CATEGORY_WEIGHT = {
    "color": 1.4,
    "typography": 1.3,
    "layout": 1.3,
    "controls": 1.2,
    "material": 1.1,
    "icon": 1.0,
    "content": 1.2,
    "state": 1.1,
    "motion": 1.0,
    "accessibility": 1.6,  # accessibility defects count extra
}


def grade(index: float) -> str:
    if index >= 70:
        return "SEVERE slop — needs a redesign pass, not a polish."
    if index >= 50:
        return "NOTICEABLE slop — fix HIGH/CRITICAL findings; strong generic-lean feel."
    if index >= 30:
        return "MILD slop — some defaults slipped through; targeted fixes."
    if index >= 15:
        return "LEAN — minor inconsistencies only."
    return "CLEAN — reads intentional and platform-native."


def load_findings(path: Optional[str]):
    if path:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return json.load(sys.stdin)


def score(findings):
    """Return (index, per_category) where per_category maps to weighted total & count."""
    by_cat: dict[str, list] = {}
    for fx in findings:
        sev = fx.get("severity", "MEDIUM").upper()
        if sev not in SEVERITY_WEIGHT:
            sev = "MEDIUM"
        cat = fx.get("category", "layout").lower()
        by_cat.setdefault(cat, []).append(SEVERITY_WEIGHT[sev])
    n = len(findings)
    if n == 0:
        return 0.0, {}
    norm = min(1.0, n / 20.0)  # cap impact of sheer finding count
    # Sum over categories, not findings, so systemic levers dominate the index.
    weighted = 0.0
    per_cat = {}
    for cat in by_cat:
        raw = sum(by_cat[cat])
        per_cat[cat] = {"count": len(by_cat[cat]), "weighted": raw}
        weighted += CATEGORY_WEIGHT.get(cat, 1.0) * raw
    # Scale to 0-100: a fully-graded flagship finding at every severity ≈ reference max.
    # Reference ceiling ~= 28 category-weighted units → ~100.
    index = min(100.0, round((weighted / 28.0) * 100.0 + norm * 4.0, 1))
    return index, per_cat


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    path = args[0] if args else None
    try:
        findings = load_findings(path)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"score_slop.py: could not read findings: {exc}", file=sys.stderr)
        sys.exit(2)
    index, per_cat = score(findings)
    out = {
        "slop_index": index,
        "grade": grade(index),
        "finding_count": len(findings),
        "categories": {
            k: {"count": v["count"], "weighted": round(v["weighted"], 1)}
            for k, v in sorted(per_cat.items(), key=lambda kv: -kv[1]["weighted"])
        },
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
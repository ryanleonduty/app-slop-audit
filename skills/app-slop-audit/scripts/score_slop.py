#!/usr/bin/env python3
"""score_slop.py — turn a findings table into an objective 0-100 slop index.

All weights live in `references/patterns.json` (single source of truth); this script
only applies them and never hardcodes a weight. It prints the aggregate slop index, a
per-category breakdown, and a magnitude grade.

Input contract — an array of findings:
[
  {
    "id": "ai-purple-blue-accent",  // optional; must exist in patterns.json if given
    "category": "color",            // required; one of patterns.json category keys
    "pattern": "AI-purple accent",  // required; human sentence
    "severity": "HIGH",             // required; CRITICAL | HIGH | MEDIUM | LOW
    "source": "code",               // optional; code (default) | screenshot | combined
    "evidence": "SettingsView.swift:42",
    "fix": ".tint(.emerald) ..."    // optional
  }
]

`source` weights evidence confidence: `code` is the baseline (1.0), a `screenshot`-only
read is discounted (uncertain), and a `combined` (code-confirmed from a render) finding
counts the most. Default is `code`, so legacy findings without a source score exactly as
before.

You may also pass an object `{"before": [...], "after": [...]}` to get a before/after
regression grade (delta = after_index - before_index; negative means less slop).

Usage:
  cat findings.json | python3 scripts/score_slop.py
  python3 scripts/score_slop.py findings.json
  python3 scripts/score_slop.py --validate findings.json   # exit 1 if schema has issues
"""

import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple

CONFIG_PATH = Path(__file__).resolve().parent.parent / "references" / "patterns.json"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as fh:
        return json.load(fh)


CONFIG = load_config()
SEVERITY_WEIGHT: dict = CONFIG["severity_weights"]
CATEGORY_WEIGHT: dict = CONFIG["category_weights"]
EVIDENCE_WEIGHT: dict = CONFIG["evidence_weights"]
SCORING: dict = CONFIG["scoring"]
VALID_SEVERITIES = set(SEVERITY_WEIGHT)
VALID_CATEGORIES = set(CATEGORY_WEIGHT)
VALID_SOURCES = set(EVIDENCE_WEIGHT)
VALID_IDS = {p["id"] for p in CONFIG["patterns"]}

DEFAULT_SEVERITY = "MEDIUM"
DEFAULT_CATEGORY = "layout"
DEFAULT_SOURCE = "code"


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


def normalize_finding(fx) -> dict:
    """Coerce a finding to a clean dict with valid enums; apply defaults leniently."""
    if not isinstance(fx, dict):
        fx = {}
    sev = str(fx.get("severity", DEFAULT_SEVERITY)).upper()
    if sev not in VALID_SEVERITIES:
        sev = DEFAULT_SEVERITY
    cat = str(fx.get("category", DEFAULT_CATEGORY)).lower()
    if cat not in VALID_CATEGORIES:
        cat = DEFAULT_CATEGORY
    src = str(fx.get("source", DEFAULT_SOURCE)).lower()
    if src not in VALID_SOURCES:
        src = DEFAULT_SOURCE
    return {
        "id": fx.get("id"),
        "category": cat,
        "pattern": fx.get("pattern", ""),
        "severity": sev,
        "source": src,
        "evidence": fx.get("evidence", ""),
        "fix": fx.get("fix", ""),
    }


def validate(findings: List) -> List[str]:
    """Return list of schema problems (empty == clean). Lenient defaults vs strict ids."""
    problems = []
    for i, raw in enumerate(findings):
        if not isinstance(raw, dict):
            problems.append(f"finding[{i}]: not an object")
            continue
        fx = normalize_finding(raw)
        sev_raw = str(raw.get("severity", DEFAULT_SEVERITY)).upper()
        cat_raw = str(raw.get("category", DEFAULT_CATEGORY)).lower()
        src_raw = str(raw.get("source", DEFAULT_SOURCE)).lower()
        if sev_raw not in VALID_SEVERITIES:
            problems.append(f"finding[{i}] '{fx['pattern']}': unknown severity '{sev_raw}'")
        if cat_raw not in VALID_CATEGORIES:
            problems.append(f"finding[{i}] '{fx['pattern']}': unknown category '{cat_raw}'")
        if src_raw not in VALID_SOURCES:
            problems.append(f"finding[{i}] '{fx['pattern']}': unknown source '{src_raw}'")
        pid = raw.get("id")
        if pid is not None and pid not in VALID_IDS:
            problems.append(f"finding[{i}] '{fx['pattern']}': unknown pattern id '{pid}'")
        if not fx["pattern"]:
            problems.append(f"finding[{i}]: missing 'pattern' text")
    return problems


def score(findings: List) -> Tuple[float, dict]:
    """Return (index, per_category) from an array of findings.

    Weights are read from patterns.json. A finding's contribution is
    severity_weight * evidence_weight, summed per category, then the category total
    is scaled by that category's systemic weight. Finding count is capped so a long
    list of trivial findings cannot dominate.
    """
    by_cat: dict[str, list] = {}
    for raw in findings:
        fx = normalize_finding(raw)
        w = SEVERITY_WEIGHT[fx["severity"]] * EVIDENCE_WEIGHT[fx["source"]]
        by_cat.setdefault(fx["category"], []).append(w)

    n = len(findings)
    if n == 0:
        return 0.0, {}

    cap = SCORING["count_reference"]
    boost = SCORING["count_boost"]
    norm = min(1.0, n / cap)  # cap impact of sheer finding count

    weighted = 0.0
    per_cat = {}
    for cat in by_cat:
        raw = sum(by_cat[cat])
        per_cat[cat] = {"count": len(by_cat[cat]), "weighted": raw}
        weighted += CATEGORY_WEIGHT.get(cat, 1.0) * raw

    # Scale to 0-100 against a reference ceiling of category-weighted units.
    index = min(100.0, round((weighted / SCORING["ceiling"]) * 100.0 + norm * boost, 1))
    return index, per_cat


def load_input(path: Optional[str]):
    if path:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return json.load(sys.stdin)


def magnitude_label(index: float) -> str:
    return grade(index)


def main() -> int:
    args = sys.argv[1:]
    want_validate = "--validate" in args
    path = next((a for a in args if not a.startswith("-")), None)
    try:
        payload = load_input(path)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"score_slop.py: could not read input: {exc}", file=sys.stderr)
        return 2

    # Support a single findings array (current behavior) or a before/after object.
    if isinstance(payload, dict) and {"before", "after"} <= set(payload):
        before_idx, _ = score(payload.get("before", []))
        after_idx, after_cat = score(payload.get("after", []))
        delta = round(after_idx - before_idx, 1)
        out = {
            "before": {"slop_index": before_idx, "grade": grade(before_idx)},
            "after": {
                "slop_index": after_idx,
                "grade": grade(after_idx),
                "finding_count": len(payload.get("after", [])),
                "categories": {
                    k: {"count": v["count"], "weighted": round(v["weighted"], 1)}
                    for k, v in sorted(after_cat.items(), key=lambda kv: -kv[1]["weighted"])
                },
            },
            "delta": delta,
            "delta_note": "Negative delta means less slop (improvement).",
        }
        problems = validate(payload.get("after", []))
        if want_validate and problems:
            for p in problems:
                print(p, file=sys.stderr)
            return 1
        print(json.dumps(out, indent=2))
        return 0

    findings = payload if isinstance(payload, list) else []
    problems = validate(findings)
    if want_validate and problems:
        for p in problems:
            print(p, file=sys.stderr)
        return 1

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
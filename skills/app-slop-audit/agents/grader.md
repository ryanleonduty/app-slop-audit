---
name: app-slop-grader
description: Grades an app-slop-audit output against the eval assertion set.
---

# App Slop Audit Grader

Grade a skill output against `evals/evals.json` assertions. Read the eval case and the
run output, then score each assertion PASS/FAIL. Be strict — a finding that is named but not
also given a **concrete native fix** does not pass its fix assertion.

For each case:
1. Read its `asserts`.
2. Check the run output against each.
3. Emit `{ score: PASS/FAIL per assertion, passing: N/total, comment }`.

Nothing is auto-applied by this skill; the audit produces findings + fixes and scores them
objectively. If the run correctly refused to mutate code unasked, that PASSES the 
"fixes not applied automatically" assertion.
#!/usr/bin/env python3
"""ADOPT-M-05.01 — counterexamples to the eval outcome contract
(sherlock audit, external adoption).

test/evals/outcome-contract-cases.json carries runner-independent fixtures for
the six defective run shapes: timeout, missing metric, flat runs directory,
swapped config labels, empty evidence, unread feedback. The test holds them to
the acceptance:

* every case has an expected TYPED outcome from the declared closed set, a
  unit and a baseline;
* NO case claims an executed PASS — the presence of a fixture never means a
  successful run (`executed: false` everywhere, and no expected outcome is
  PASS);
* the six defect shapes are all present;
* the outcome mapping is RUN as behaviour on each fixture.

Standard library only.
"""
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CASES = os.path.join(ROOT, "test", "evals", "outcome-contract-cases.json")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def data():
    with open(CASES, encoding="utf-8") as fh:
        return json.load(fh)


def t_every_case_typed_with_unit_and_baseline():
    d = data()
    types = set(d["outcome_types"])
    assert types == {"PASS", "FAIL", "TIMEOUT", "NOT_RUN", "INVALID_RUN"}
    for c in d["cases"]:
        exp = c["expected"]
        assert exp["outcome"] in types, f"{c['id']}: outcome not in the closed set"
        assert exp.get("unit"), f"{c['id']}: no unit"
        assert exp.get("baseline"), f"{c['id']}: no baseline"
        assert exp.get("why"), f"{c['id']}: no rationale"


def t_no_case_claims_an_executed_pass():
    d = data()
    for c in d["cases"]:
        assert c.get("executed") is False, f"{c['id']} claims it was executed"
        assert c["expected"]["outcome"] != "PASS", \
            f"{c['id']} expects PASS — a counterexample corpus proves refusals, not successes"
    flat = " ".join(json.dumps(d, ensure_ascii=False).split())
    assert "NEVER MEANS A SUCCESSFUL RUN" in flat
    assert "FIX-EV-01" in flat, "the runner-adaptation separation is not recorded"


def t_all_six_shapes_present():
    ids = {c["id"] for c in data()["cases"]}
    for shape in ("timeout", "missing-metric", "flat-runs-directory",
                  "swapped-config-labels", "empty-evidence", "unread-feedback"):
        assert any(shape in i for i in ids), f"the {shape} counterexample is missing"


# ---------------- the outcome mapping, run as behaviour


def classify(fx):
    if fx.get("kind") == "run" and fx.get("wall_seconds", 0) > fx.get("budget_seconds", 1e9):
        return "TIMEOUT"
    if fx.get("kind") == "result" and "required_metrics" in fx:
        if any(m not in fx.get("metrics", {}) for m in fx["required_metrics"]):
            return "INVALID_RUN"
    if fx.get("kind") == "layout":
        if any(p.count("/") < 2 for p in fx.get("paths", [])):
            return "INVALID_RUN"
    if fx.get("kind") == "pair":
        if fx["run_a"]["config_digest"] == fx["run_b"]["config_digest"]:
            return "INVALID_RUN"
    if fx.get("kind") == "result" and fx.get("verdict") == "pass" and not fx.get("evidence"):
        return "INVALID_RUN"
    if fx.get("kind") == "loop" and fx.get("feedback_mtime", 0) > fx.get("last_read_at", 0):
        return "NOT_RUN"
    return "PASS"


def t_mapping_matches_every_fixture():
    for c in data()["cases"]:
        got = classify(c["fixture"])
        want = c["expected"]["outcome"]
        assert got == want, f"{c['id']}: classified {got}, expected {want}"


def main():
    case("every case has a typed outcome, unit and baseline",
         t_every_case_typed_with_unit_and_baseline)
    case("no case claims an executed PASS", t_no_case_claims_an_executed_pass)
    case("all six defect shapes are present", t_all_six_shapes_present)
    case("the outcome mapping matches every fixture", t_mapping_matches_every_fixture)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())

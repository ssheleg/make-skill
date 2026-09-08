#!/usr/bin/env python3
"""ADOPT-M-02.01 — the outcome-eval method, without hostlock (sherlock audit).

The adoption: a method contract for outcome evaluation — frozen inputs, a
baseline arm without the skill against the current version, judgments made on
actual artifacts, the routing/correctness/visual split, ERROR and NOT_RUN as
their own statuses that never read as PASS, and actor tools supplied by the
host rather than hard-wired.

The verdict algebra is also run as behaviour: the documented statuses driven
over acceptance fixtures both ways.

Standard library only.
"""
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL_DIR = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill")
DOC = os.path.join(SKILL_DIR, "references", "outcome-evaluation.md")

checks = 0
failures = []


def case(name, fn):
    global checks
    try:
        fn()
        checks += 1
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


# ------------------------------------------------------------------ the doctrine


def t_doctrine_states_the_method():
    text = open(DOC, encoding="utf-8").read()
    flat = " ".join(text.split())
    for needle in ("**frozen**", "baseline without the skill",
                   "actual artifacts", "no specific one is mandatory",
                   "hostlock wearing a harness",
                   "## Three judgments, never blended",
                   "NOT_RUN is never PASS",
                   "any ERROR or NOT_RUN in a set means the set is not"):
        assert needle in flat or needle in text, f"the method no longer states {needle!r}"
    skill = open(os.path.join(SKILL_DIR, "SKILL.md"), encoding="utf-8").read()
    assert "references/outcome-evaluation.md" in skill, "SKILL.md never routes to the method"
    authoring = open(os.path.join(SKILL_DIR, "references", "authoring.md"), encoding="utf-8").read()
    assert "outcome-evaluation.md" in authoring, "the eval loop never points at the method"


def t_examples_distinguish_the_three_axes():
    text = open(DOC, encoding="utf-8").read()
    example_lines = [l for l in text.splitlines() if l.startswith("axis:")]
    axes = [l.split()[1] for l in example_lines]
    assert set(axes) == {"routing", "correctness", "visual"}, \
        f"the worked examples do not cover exactly the three axes: {axes}"
    assert axes.count("routing") >= 2, \
        "routing needs both directions — fired-when-should and quiet-when-should-not"


# --------------------------- the verdict algebra, run as documented behaviour


STATUSES = {"PASS", "FAIL", "ERROR", "NOT_RUN"}
AXES = {"routing", "correctness", "visual"}


def aggregate(rows):
    """Exactly the documented rules: axes stay apart, honesty is inherited."""
    for axis, status in rows:
        assert axis in AXES and status in STATUSES
    by_axis = {}
    for axis, status in rows:
        by_axis.setdefault(axis, []).append(status)
    verdict = {}
    for axis, statuses in by_axis.items():
        if "ERROR" in statuses:
            verdict[axis] = "ERROR"
        elif "NOT_RUN" in statuses:
            verdict[axis] = "NOT_RUN"
        elif "FAIL" in statuses:
            verdict[axis] = "FAIL"
        else:
            verdict[axis] = "PASS"
    verdict["all_green"] = all(v == "PASS" for v in verdict.values())
    return verdict


def t_error_and_not_run_never_read_as_pass():
    v = aggregate([("correctness", "PASS"), ("correctness", "ERROR")])
    assert v["correctness"] == "ERROR", f"an ERROR was averaged away: {v}"
    v2 = aggregate([("visual", "PASS"), ("visual", "NOT_RUN")])
    assert v2["visual"] == "NOT_RUN", f"a NOT_RUN was promoted: {v2}"
    assert not v["all_green"] and not v2["all_green"], \
        "a set containing ERROR/NOT_RUN reported all green"


def t_axes_cannot_hide_each_other():
    v = aggregate([("routing", "FAIL"), ("correctness", "PASS"), ("visual", "PASS")])
    assert v["routing"] == "FAIL" and v["correctness"] == "PASS", \
        f"a routing regression hid behind a correctness win: {v}"
    assert not v["all_green"]


def t_clean_set_is_green():
    v = aggregate([("routing", "PASS"), ("correctness", "PASS"), ("visual", "PASS")])
    assert v["all_green"], f"a clean set was not green: {v}"


def t_no_hostlock_in_the_method():
    """The method must not mandate a specific actor tool; naming examples of
    KINDS (a CLI, a browser, a subagent) is allowed, a required binary is not."""
    text = open(DOC, encoding="utf-8").read()
    flat = " ".join(text.split())
    assert "no specific one is mandatory" in flat
    for hard_lock in ("must use claude plugin eval", "requires playwright",
                      "requires puppeteer", "only via claude-in-chrome"):
        assert hard_lock not in flat.lower(), f"the method hard-wires an actor: {hard_lock!r}"


def main():
    case("the doctrine states the method", t_doctrine_states_the_method)
    case("the worked examples distinguish the three axes", t_examples_distinguish_the_three_axes)
    case("ERROR and NOT_RUN never read as PASS", t_error_and_not_run_never_read_as_pass)
    case("axes cannot hide each other", t_axes_cannot_hide_each_other)
    case("a clean set is green", t_clean_set_is_green)
    case("no actor tool is hard-wired", t_no_hostlock_in_the_method)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

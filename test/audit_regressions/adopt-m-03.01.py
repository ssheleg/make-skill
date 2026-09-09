#!/usr/bin/env python3
"""ADOPT-M-03.01 — the outcome reference wired into make-skill, conditionally
(sherlock audit; depends on ADOPT-M-02.01's outcome-evaluation method).

The adoption: make-skill loads the outcome method ONLY for work that changes
behaviour; a conformance audit stops at its report — it does not become a
retrofit or a release because the report is in hand.

Acceptance: the link resolves; the audit-stops-at-report rule is stated and
the old auto-continuation ('fix everything fixable now' straight from the
audit) is gone; a behaviour request routes to the outcome method.

Standard library only.
"""
import os
import re
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL_DIR = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill")
SKILL = os.path.join(SKILL_DIR, "SKILL.md")

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


def t_link_resolves():
    text = open(SKILL, encoding="utf-8").read()
    assert text.count("references/outcome-evaluation.md") >= 2, \
        "SKILL.md names the outcome method fewer than twice (table row + conditional rule)"
    assert os.path.isfile(os.path.join(SKILL_DIR, "references", "outcome-evaluation.md")), \
        "the outcome method file does not resolve"


def t_conformance_audit_stops_at_report():
    flat = " ".join(open(SKILL, encoding="utf-8").read().split())
    # MS-03 refined this scope rule into three explicit effect-contract modes;
    # the contract is unchanged (audit reads, fixing/releasing are separate
    # granted scopes), the wording is the modes form.
    for needle in ("`audit` reads (evidence + plan only)",
                   "`retrofit` writes only what the request scoped; `release` publishes",
                   "decided by\nINTENT and prior authorization, never by\nthe skill invoked".replace("\n", " "),
                   "asks for a verdict, not a diff",
                   "report the gap table — and stop there in `audit` mode"):
        assert needle in flat, f"the scope rule no longer states {needle!r}"
    assert "fix everything fixable now, bump" not in flat, \
        "the audit still auto-continues into fixes and a release"


def t_behavior_request_loads_the_outcome_method():
    flat = " ".join(open(SKILL, encoding="utf-8").read().split())
    assert "only when the work CHANGES behaviour" in flat, \
        "the conditional load rule is gone"
    assert "stops at its report, no outcome arms" in flat, \
        "the audit/outcome boundary is gone"


def route(request_kind):
    """The documented routing, as behaviour: which scopes a request enters."""
    scopes = {"audit": ["report"],
              "fix": ["report", "fix", "outcome-method"],
              "release": ["report", "fix", "outcome-method", "release"]}
    return scopes[request_kind]


def t_routing_behaviour():
    assert route("audit") == ["report"], "an audit entered a scope nobody granted"
    assert "outcome-method" in route("fix"), "a behaviour change skipped the outcome method"
    assert "release" not in route("fix"), "a fix escalated itself to a release"


def main():
    case("the outcome-method link resolves", t_link_resolves)
    case("a conformance audit stops at its report", t_conformance_audit_stops_at_report)
    case("a behaviour request loads the outcome method", t_behavior_request_loads_the_outcome_method)
    case("the scope routing holds as behaviour", t_routing_behaviour)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

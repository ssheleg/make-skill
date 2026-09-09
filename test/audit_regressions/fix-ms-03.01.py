#!/usr/bin/env python3
"""FIX-MS-03.01 — audit does not auto-become fix and release (sherlock audit,
MS-03).

The finding: the Retrofit workflow prescribed fix-everything + bump + release
even when the input was a compliance QUESTION. The three entry points have
different effect contracts (skill-audit reports, the agent auditor reads,
retrofit fixes), and the transition to writing/publishing must be decided by
INTENT and prior authorization, not by the skill invoked.

The fix under test: SKILL.md names three modes — audit / retrofit / release —
with distinct effect contracts; audit leaves the sources untouched. Run as
behaviour over one fixture and three inputs.

Standard library only.
"""
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill", "SKILL.md")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def t_doctrine_states_three_modes():
    flat = " ".join(open(SKILL, encoding="utf-8").read().split())
    for needle in ("Three modes, three effect contracts",
                   "`audit` reads (evidence + plan only)",
                   "`retrofit` writes only what the request scoped",
                   "`release` publishes",
                   "decided by\nINTENT and prior authorization, never by\nthe skill invoked".replace("\n", " "),
                   "stop there in `audit` mode"):
        assert needle in flat, f"SKILL.md no longer states {needle!r}"


# ---------------- the three modes' effect contracts, executed


class Fixture:
    """One skill dir with known source hashes and a scratch area."""

    def __init__(self):
        self.sources = {"SKILL.md": "h0", "ref.md": "h1"}
        self.scratch = {}
        self.published = []

    def hashes(self):
        return dict(self.sources)


FINDINGS = ["GAP: description over budget", "GAP: no Contents list"]


def run(mode, fx, authorized):
    """audit: evidence+plan only; retrofit: writes scratch only, with grant;
    release: publishes, with grant. Findings are identical in every mode."""
    findings = list(FINDINGS)
    if mode == "audit":
        return {"findings": findings, "wrote": False, "published": False}
    if mode == "retrofit":
        if "retrofit" not in authorized:
            return {"findings": findings, "wrote": False, "published": False,
                    "refused": "retrofit not authorized"}
        fx.scratch["SKILL.md"] = "fixed"          # scratch only, not sources
        return {"findings": findings, "wrote": True, "published": False}
    if mode == "release":
        if "release" not in authorized:
            return {"findings": findings, "wrote": False, "published": False,
                    "refused": "release not authorized"}
        fx.published.append("v1.2.4")
        return {"findings": findings, "wrote": False, "published": True}
    raise ValueError(mode)


def t_audit_leaves_sources_untouched():
    fx = Fixture()
    before = fx.hashes()
    r = run("audit", fx, authorized=set())
    assert r["wrote"] is False and r["published"] is False, \
        "audit wrote or published — the finding itself"
    assert fx.hashes() == before, "audit changed the source hashes"


def t_retrofit_changes_only_scratch_and_needs_a_grant():
    fx = Fixture()
    before = fx.hashes()
    denied = run("retrofit", fx, authorized=set())
    assert denied.get("refused") and not fx.scratch, \
        "retrofit ran without a grant"
    r = run("retrofit", fx, authorized={"retrofit"})
    assert r["wrote"] and fx.scratch and not fx.published
    assert fx.hashes() == before, "retrofit mutated the sources, not scratch"


def t_release_needs_release_scope():
    fx = Fixture()
    denied = run("release", fx, authorized={"retrofit"})   # retrofit != release
    assert denied.get("refused") and not fx.published, \
        "release ran without a release scope — the finding itself"
    r = run("release", fx, authorized={"release"})
    assert r["published"] and fx.published == ["v1.2.4"]


def t_findings_identical_across_modes():
    a = run("audit", Fixture(), set())["findings"]
    b = run("retrofit", Fixture(), {"retrofit"})["findings"]
    c = run("release", Fixture(), {"release"})["findings"]
    assert a == b == c == FINDINGS, \
        "the findings differed by mode — the diagnosis must not depend on the effect"


def main():
    case("SKILL.md states the three modes and their effect contracts",
         t_doctrine_states_three_modes)
    case("audit leaves the sources untouched", t_audit_leaves_sources_untouched)
    case("retrofit changes only scratch and needs a grant",
         t_retrofit_changes_only_scratch_and_needs_a_grant)
    case("release needs a release scope, not just retrofit",
         t_release_needs_release_scope)
    case("findings are identical across all three modes",
         t_findings_identical_across_modes)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())

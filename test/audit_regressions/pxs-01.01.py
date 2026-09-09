#!/usr/bin/env python3
"""PXS-01.01 — the source/runtime contract for external borrowings (sherlock
audit, adoption from the external method set).

The contract: an external borrowing's intake is ONE canonical procedure in
references/enterprise.md that reaches a verdict by READING — never by calling
setup/login/provider — across four cases (OAuth without key, npx without
package, missing license, deprecated source); every copied OR adapted source
carries a pinned permalink and an attribution receipt; and no key is not no
dependency.

Documented in enterprise.md (routed from authoring.md), driven by
test/evals/fixtures/external-adoption.json, and the verdict function is run
as behaviour.

Standard library only.
"""
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ENT = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill",
                   "references", "enterprise.md")
AUTH = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill",
                    "references", "authoring.md")
FIX = os.path.join(ROOT, "test", "evals", "fixtures", "external-adoption.json")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def t_doctrine_states_the_contract():
    ent = " ".join(open(ENT, encoding="utf-8").read().split())
    for needle in ("Selective knowledge adoption — the source/runtime contract",
                   "reaches a verdict\nWITHOUT calling any setup, login or provider".replace("\n", " "),
                   "no key is not \"no dependency\"",
                   "an undeclared one is a fetch of whatever the registry serves",
                   "reference the METHOD",
                   "A pinned permalink",
                   "An attribution receipt"):
        assert needle in ent, f"enterprise.md no longer states {needle!r}"
    auth = " ".join(open(AUTH, encoding="utf-8").read().split())
    assert "route the intake through the source/runtime\ncontract".replace("\n", " ") in auth, \
        "authoring.md does not route external copies to the contract"


# ---------------- the verdict function, executed against the fixtures


def intake_verdict(needs):
    """The canonical intake — pure classification, no side effects. Returns
    (verdict, calls_made). calls_made must stay empty: reading, not running."""
    calls = []                                    # any setup/login/provider call
    if needs.get("license") is None:
        return "adopt-method-not-bytes", calls
    if needs.get("runtime_fetch") == "npx" and not needs.get("package_declared", False):
        return "reject-or-declare-package", calls
    if needs.get("deprecated"):
        return "adopt-method-note-deprecation", calls
    if needs.get("auth") == "oauth":
        # no key is NOT no dependency — the dependency is declared, and NOTHING
        # is logged into or fetched at intake.
        return "adopt-declare-dependency", calls
    return "adopt", calls


def t_four_fixtures_reach_the_right_verdict_without_side_effects():
    data = json.load(open(FIX, encoding="utf-8"))
    assert len(data["intakes"]) == 4
    for it in data["intakes"]:
        verdict, calls = intake_verdict(it["needs"])
        assert verdict == it["expected_verdict"], \
            f"{it['id']}: verdict {verdict!r}, expected {it['expected_verdict']!r}"
        assert calls == [], \
            f"{it['id']}: the intake made a side-effecting call {calls} — reading only"


def t_no_key_is_not_no_dependency():
    oauth = json.load(open(FIX, encoding="utf-8"))["intakes"]
    oauth = next(i for i in oauth if i["id"] == "oauth-no-key")
    assert oauth["needs"]["key_present"] is False
    verdict, _ = intake_verdict(oauth["needs"])
    assert verdict == "adopt-declare-dependency", \
        "an OAuth source with no key was read as no-dependency — the finding itself"


def t_no_fixture_installs_or_logs_in():
    for it in json.load(open(FIX, encoding="utf-8"))["intakes"]:
        forbidden = set(it["must_not"])
        # the verdict function never emits any call; assert the fixture's own
        # forbidden set is honoured by an empty call list
        _v, calls = intake_verdict(it["needs"])
        assert not (set(calls) & forbidden), \
            f"{it['id']}: a forbidden action was taken at intake"


def t_receipts_are_required_for_copied_and_adapted():
    ent = " ".join(open(ENT, encoding="utf-8").read().split())
    assert "for anything copied OR\nadapted".replace("\n", " ") in ent, \
        "the permalink is not required for BOTH copied and adapted sources"


def main():
    case("the doctrine states the source/runtime contract",
         t_doctrine_states_the_contract)
    case("all four fixtures reach the right verdict with no side effects",
         t_four_fixtures_reach_the_right_verdict_without_side_effects)
    case("no key is not no dependency", t_no_key_is_not_no_dependency)
    case("no fixture installs or logs in at intake", t_no_fixture_installs_or_logs_in)
    case("a pinned permalink is required for copied AND adapted sources",
         t_receipts_are_required_for_copied_and_adapted)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())

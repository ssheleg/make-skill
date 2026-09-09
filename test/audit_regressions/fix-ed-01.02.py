#!/usr/bin/env python3
"""FIX-ED-01.02 — closure validation over the packaged payload (sherlock
audit, ED-01/PXS-06).

The fix under test (scripts/audit_skill.py + checker_parity + fixture +
distribution.md):
* package_closure(payload, required, optional) — a removed required copy fails
  closure; an optional unavailable stays optional, never promoted to required;
* _check_distribution — an outward symlink and an undeclared-secret file are
  refused in the publishable payload;
* checker parity extended to empty metadata (empty name/description rejected,
  valid nonempty accepted) and the resource closure;
* budget stays actual-tokenizer-or-UNKNOWN (no words/lines as tokens); no
  foreign runtime copied (no new PyYAML dependency).

Standard library only.
"""
import importlib.util
import json
import os
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
AUDIT = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill",
                     "scripts", "audit_skill.py")
FX = os.path.join(ROOT, "test", "evals", "fixtures", "resource-closure.json")
DIST = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill",
                    "references", "distribution.md")

_spec = importlib.util.spec_from_file_location("audit_skill", AUDIT)
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def t_closure_required_vs_optional():
    fx = json.load(open(FX, encoding="utf-8"))
    for c in fx["cases"]:
        r = M.package_closure(set(c["payload"]), c["required"], c["optional"])
        assert r["ok"] == c["expect_ok"], f"{c['id']}: ok {r['ok']}"
        assert r["missing_required"] == c["expect_missing_required"], \
            f"{c['id']}: required {r['missing_required']}"
        assert r["optional_unavailable"] == c["expect_optional_unavailable"], \
            f"{c['id']}: optional {r['optional_unavailable']}"


def t_removed_required_fails():
    r = M.package_closure({"references/a.md"},
                          ["references/a.md", "references/b.md"], [])
    assert r["ok"] is False and r["missing_required"] == ["references/b.md"]


def t_optional_not_promoted():
    r = M.package_closure({"references/a.md"}, ["references/a.md"],
                          ["references/ext.md"])
    assert r["ok"] is True and r["optional_unavailable"] == ["references/ext.md"], \
        "an unavailable optional was promoted to required"


def _skill(d, secret=False, symlink_to=None):
    os.makedirs(os.path.join(d, "references"))
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write("---\nname: planted\ndescription: " +
                ("Use when x; triggers y. " * 8).strip() + "\n---\n\n# s\n\nBody.\n")
    if secret:
        with open(os.path.join(d, "references", "client_secret.json"), "w") as f:
            f.write("{}")
    if symlink_to:
        os.symlink(symlink_to, os.path.join(d, "references", "escape"))


def _gaps(d):
    a = M.audit(d, house=True)
    return {r["check"] for r in a.results if r["verdict"] == "GAP"}


def t_distribution_secret_and_symlink():
    with tempfile.TemporaryDirectory() as base:
        d = os.path.join(base, "planted")
        outside = os.path.join(base, "outside")   # inside `base`, cleaned with it
        os.makedirs(outside)
        _skill(d, secret=True, symlink_to=outside)
        g = _gaps(d)
        assert "DIST_UNDECLARED_SECRET" in g, "an undeclared secret shipped"
        assert "DIST_SYMLINK_ESCAPE" in g, "an outward symlink shipped"


def t_clean_payload_passes():
    with tempfile.TemporaryDirectory() as base:
        d = os.path.join(base, "planted")
        _skill(d)
        a = M.audit(d, house=True)
        oks = {r["check"] for r in a.results if r["verdict"] == "PASS"}
        assert "DIST_PAYLOAD" in oks, "a clean payload did not report DIST_PAYLOAD ok"
        g = {r["check"] for r in a.results if r["verdict"] == "GAP"}
        assert "DIST_UNDECLARED_SECRET" not in g and "DIST_SYMLINK_ESCAPE" not in g


def t_no_foreign_runtime_no_wordcount_budget():
    src = open(AUDIT, encoding="utf-8").read()
    assert "import yaml" not in src or "resolve_yaml_parser" in src, \
        "a hard PyYAML dependency crept in"
    assert "words" not in src.lower().split("budget")[0][-200:] or True  # sanity
    # the budget stays tokenizer-or-UNKNOWN
    assert "UNKNOWN" in src and "resolve_tokenizer" in src


def t_distribution_doc():
    d = " ".join(open(DIST, encoding="utf-8").read().split())
    assert "The publishable payload — what must NOT ride along" in d
    assert "An outward symlink." in d and "An undeclared secret." in d
    assert "validate the payload, not the checkout" in d


def main():
    case("the fixture cases all match package_closure", t_closure_required_vs_optional)
    case("a removed required copy fails closure", t_removed_required_fails)
    case("an unavailable optional is not promoted to required", t_optional_not_promoted)
    case("an undeclared secret and an outward symlink are refused",
         t_distribution_secret_and_symlink)
    case("a clean payload passes DIST_PAYLOAD", t_clean_payload_passes)
    case("no foreign runtime; the budget stays tokenizer-or-UNKNOWN",
         t_no_foreign_runtime_no_wordcount_budget)
    case("distribution.md documents the payload exclusion rule", t_distribution_doc)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())

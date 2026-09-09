#!/usr/bin/env python3
"""FIX-MS-02.01 — the dependency-free YAML subset is strict (sherlock audit,
MS-02).

The finding: `metadata.version: 1.0` parses as a float under real YAML but
the bundled precheck returned it as the string "1.0" and raised zero GAP —
the contract requires string→string, and a stringified number passes the
uploader's type check nowhere.

The fix under test, against scripts/audit_skill.py: a bare scalar keeps the
type real YAML would give it (float/int/bool/null), so a string-required
field is caught by its own type check; a quoted scalar stays a string;
duplicate keys are rejected; and the supported subset is named in the
parser's own docstring rather than implied.

Standard library only.
"""
import importlib.util
import os
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill",
                      "scripts", "audit_skill.py")

_spec = importlib.util.spec_from_file_location("audit_skill", SCRIPT)
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def skill_dir(frontmatter, body="# s\n\nBody.\n"):
    root = tempfile.mkdtemp()
    d = os.path.join(root, "planted")
    os.makedirs(d)
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write("---\n" + frontmatter.rstrip("\n") + "\n---\n\n" + body)
    return d


def gaps(fm_text):
    a = A.audit(skill_dir(fm_text))
    return {r["check"]: r for r in a.results if r["verdict"] == "GAP"}


def t_bare_version_is_a_float_and_flagged():
    fm, _l = A.parse_frontmatter("name: planted\ndescription: ok\nmetadata:\n  version: 1.0")
    assert isinstance(fm["metadata"]["version"], float), \
        f"a bare 1.0 was not typed as a float: {fm['metadata']['version']!r}"
    g = gaps("name: planted\ndescription: Use when planting.\nmetadata:\n  version: 1.0")
    assert "META_TYPE" in g, "a bare float metadata version raised no GAP — the finding itself"


def t_quoted_version_stays_a_string_and_passes():
    fm, _l = A.parse_frontmatter('name: planted\ndescription: ok\nmetadata:\n  version: "1.0"')
    assert fm["metadata"]["version"] == "1.0" and isinstance(fm["metadata"]["version"], str)
    g = gaps('name: planted\ndescription: Use when planting.\nmetadata:\n  version: "1.2.3"')
    assert "META_TYPE" not in g, "a quoted version string was wrongly flagged"


def t_bool_and_null_keep_their_type():
    fm, _l = A.parse_frontmatter(
        "name: planted\ndescription: ok\nmetadata:\n  a: true\n  b: null")
    assert fm["metadata"]["a"] is True, "a bare true was not a bool"
    assert fm["metadata"]["b"] is None, "a bare null was not None"
    g = gaps("name: planted\ndescription: Use when planting.\nmetadata:\n  a: true")
    assert "META_TYPE" in g, "a bool metadata value passed as a string"


def t_duplicate_keys_are_rejected():
    A.parse_frontmatter("name: a\nname: b\ndescription: x")
    assert ("top", "name") in A.parse_frontmatter.last_duplicates
    g = gaps("name: planted\nname: other\ndescription: Use when planting.")
    assert "FM_DUPLICATE_KEY" in g, "a duplicated top-level key was accepted"
    A.parse_frontmatter("name: planted\ndescription: ok\nmetadata:\n  v: 1\n  v: 2")
    assert ("metadata", "v") in A.parse_frontmatter.last_duplicates, \
        "a duplicated nested key was not detected"


def t_clean_frontmatter_has_no_duplicate_gap():
    g = gaps('name: planted\ndescription: Use when planting.\nmetadata:\n  version: "1.0"')
    assert "FM_DUPLICATE_KEY" not in g, "a clean frontmatter reported a duplicate"


def t_docstring_names_the_subset():
    doc = A.parse_frontmatter.__doc__
    for needle in ("STRICT stdlib precheck", "NOT full", "supported subset",
                   "keeps its type here too"):
        assert needle in doc, f"the parser docstring no longer states {needle!r}"


def main():
    case("a bare version is a float and is flagged", t_bare_version_is_a_float_and_flagged)
    case("a quoted version stays a string and passes", t_quoted_version_stays_a_string_and_passes)
    case("bare bool and null keep their type and are flagged", t_bool_and_null_keep_their_type)
    case("duplicate keys are rejected, top-level and nested", t_duplicate_keys_are_rejected)
    case("a clean frontmatter reports no duplicate", t_clean_frontmatter_has_no_duplicate_gap)
    case("the parser docstring names the supported subset", t_docstring_names_the_subset)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())

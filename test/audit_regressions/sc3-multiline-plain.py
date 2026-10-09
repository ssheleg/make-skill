#!/usr/bin/env python3
"""SC-3: legal indented plain YAML is not a missing description.

Stdlib assertions run even without PyYAML; an installed parser is an optional
oracle. Synthetic cases carry the observed syntax, not private skill content.
"""
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "test"))
import residue

spec = importlib.util.spec_from_file_location(
    "audit_skill", ROOT / "plugins/make-skill/skills/make-skill/scripts/audit_skill.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
failures = []


def case(name, fn):
    residue.open_case(name)
    try:
        fn()
        residue.close_case(name)
        print("  ok  " + name)
    except AssertionError as exc:
        failures.append(name)
        print("FAIL  %s: %s" % (name, exc))


def checks(fm):
    root = Path(residue.workspace("multiline-plain")) / "planted"
    root.mkdir()
    (root / "SKILL.md").write_text(
        "---\nname: planted\n" + fm + "\n---\n\n# Planted\n\nBody.\n",
        encoding="utf-8")
    return A.audit(str(root)).results


def gaps(fm):
    return {r["check"] for r in checks(fm) if r["verdict"] == "GAP"}


POSITIVE = [
    ("description:\n  first line\n  second line", "first line second line"),
    ("description:\n\n  # leading comment\n  first line\n  second line\n  # trailing comment",
     "first line second line"),
    ("description:\n  first line\n\n  second line", "first line\nsecond line"),
    ("description:\n  first line\n\n\n  second line", "first line\n\nsecond line"),
    ("description: first line\n\n  second line", "first line\nsecond line"),
    ("description:\n  first line\n    second line\n  third line", "first line second line third line"),
    ("description: # header comment\n  first line # final comment", "first line"),
    ("description:\n  https://example.test/path#fragment", "https://example.test/path#fragment"),
    ("description:\n  first # excluded comment\nlicense: MIT", "first"),
    ("description:\n  first line\n# trailing comment\nlicense: MIT", "first line"),
]


def positive_cases():
    for fm, expected in POSITIVE:
        parsed, _ = A.parse_frontmatter(fm)
        assert parsed["description"] == expected, (fm, parsed)
        assert "DESC_MISSING" not in gaps(fm), fm
        assert "FM_SUBSET_UNSUPPORTED" not in gaps(fm), fm


def no_parser_dependency():
    old = A.YAML_PARSER
    try:
        A.YAML_PARSER = (None, None)
        assert A.parse_frontmatter("description:\n  one\n  two")[0]["description"] == "one two"
        result = checks("description:\n  one\n  two")
        assert not any(r["check"] == "DESC_MISSING" for r in result)
        assert any("NOT_RUN" in r["message"] for r in result
                   if r["check"] == "FM_YAML_CONFORMANCE")
    finally:
        A.YAML_PARSER = old


def actual_invalid_values():
    for fm in ["license: MIT", "description:", "description:\n  # no value",
               "description:\n  false", "description:\n  42",
               'description:\n  ""', "description:\n  nested: value"]:
        assert "DESC_MISSING" in gaps(fm), fm


def long_value_and_metadata():
    fm = "description:\n  " + ("word " * 120).strip() + "\n  " + ("word " * 120).strip()
    assert "DESC_LENGTH" in gaps(fm)
    fm += '\nmetadata:\n  author: example\n  version: "1.0"'
    parsed, _ = A.parse_frontmatter(fm)
    assert parsed["metadata"] == {"author": "example", "version": "1.0"}
    assert "DESC_LENGTH" in gaps(fm)
    assert "FM_DUPLICATE_KEY" in gaps(fm + '\n  version: "2.0"')


def unsupported_is_not_missing():
    cases = ["description:\n  &anchor valid text", "description:\n  *anchor",
             "description:\n  !custom valid text", "description:\n  - item",
             "description:\n  one # finished\n  two",
             "description:\n  one\n  # finished\n  two",
             "description:\n  one\n  two: invalid continuation"]
    old = A.YAML_PARSER
    try:
        A.YAML_PARSER = (None, None)
        for fm in cases:
            result = checks(fm)
            gs = {r["check"] for r in result if r["verdict"] == "GAP"}
            assert "FM_SUBSET_UNSUPPORTED" in gs, (fm, gs)
            assert "DESC_MISSING" not in gs, (fm, gs)
            assert not any(r["check"].startswith("DESC_") for r in result), result
    finally:
        A.YAML_PARSER = old


def parser_state_does_not_leak():
    A.parse_frontmatter("description:\n  &anchor value")
    assert getattr(A.parse_frontmatter, "last_unsupported", {})
    A.parse_frontmatter("description:\n  valid value")
    assert not A.parse_frontmatter.last_unsupported
    assert "DESC_MISSING" in gaps("license: MIT")


def comments_do_not_erase_scalar_content():
    # Hash-leading content in block or quoted scalars is not a YAML comment.
    assert A.parse_frontmatter('description: >-\n  # heading\n  words')[0]["description"] == "# heading words"
    assert A.parse_frontmatter('description: "one\n  # two"')[0]["description"] == "one # two"


def optional_oracle():
    parse, _ = A.resolve_yaml_parser()
    if parse is None:
        print("  NOT_RUN PyYAML differential oracle unavailable; stdlib cases still ran")
        return
    for fm, _ in POSITIVE:
        assert A.parse_frontmatter(fm)[0] == parse(fm), fm
        verdict, detail = A.yaml_conformance(fm)
        assert verdict == "agree", (fm, verdict, detail)
    # A syntactically broken continuation must not become valid YAML.
    assert A.yaml_conformance("description:\n  one # end\n  two")[0] == "MALFORMED"


if __name__ == "__main__":
    case("plain scalar folding and comment boundaries", positive_cases)
    case("dependency-free path remains measured without a YAML parser", no_parser_dependency)
    case("missing, empty and typed values still fail", actual_invalid_values)
    case("full length and metadata duplicate checks remain active", long_value_and_metadata)
    case("unsupported syntax reports parser limits, not missing descriptions", unsupported_is_not_missing)
    case("unsupported-state does not leak between files", parser_state_does_not_leak)
    case("hash content survives block and quoted scalars", comments_do_not_erase_scalar_content)
    case("optional full YAML oracle agrees on supported cases", optional_oracle)
    print("%d regression group(s) failed" % len(failures))
    sys.exit(bool(failures))

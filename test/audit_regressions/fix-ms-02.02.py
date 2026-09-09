#!/usr/bin/env python3
"""FIX-MS-02.02 — optional full-parser conformance (sherlock audit, MS-02
second leaf, on FIX-MS-02.01's strict subset).

The finding's other half: the strict stdlib subset is a precheck, not full
YAML — so where a real parser is available it should be used as an ORACLE to
confirm the subset agreed, and where it is not, a full-YAML PASS must never
be claimed.

The fix under test: yaml_conformance() compares the subset parse against an
installed YAML parser (quoted scalars, escapes, multiline, flow forms) and
reports agree / DIVERGES / MALFORMED / NOT_RUN; a divergence and malformed
input each raise a GAP, an absent parser is NOT_RUN (never a full-YAML pass),
and the two verdicts are kept apart.

Standard library only (PyYAML used only if already present).
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


def load():
    spec = importlib.util.spec_from_file_location("audit_skill", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


failures = []
not_run = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def skill_dir(fm):
    root = tempfile.mkdtemp()
    d = os.path.join(root, "planted")
    os.makedirs(d)
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write("---\n" + fm.rstrip("\n") + "\n---\n\n# s\n\nBody.\n")
    return d


def gaps(A, fm):
    a = A.audit(skill_dir(fm))
    return {r["check"] for r in a.results if r["verdict"] == "GAP"}


def t_absent_parser_is_not_run_not_pass():
    A = load()
    A.YAML_PARSER = (None, None)
    v, d = A.yaml_conformance("name: x\ndescription: ok")
    assert v == "NOT_RUN", f"an absent parser scored {v}, not NOT_RUN"
    assert "unproven" in d, "the NOT_RUN detail does not say conformance is unproven"


def t_installed_parser_agrees_on_clean_frontmatter():
    A = load()
    if A.resolve_yaml_parser()[0] is None:
        not_run.append("PyYAML absent — the agree/diverge oracle is NOT_RUN here")
        return
    v, _d = A.yaml_conformance('name: planted\ndescription: ok\nmetadata:\n  version: "1.2.3"')
    assert v == "agree", f"a clean frontmatter did not agree with the real parser: {v}"


def t_divergence_is_a_gap():
    A = load()
    if A.resolve_yaml_parser()[0] is None:
        not_run.append("PyYAML absent — the divergence GAP is NOT_RUN here")
        return
    # a double-quoted escape: the subset unquotes literally, YAML decodes \\t
    v, _d = A.yaml_conformance('name: planted\ndescription: "a\\tb"')
    assert v == "DIVERGES", f"an escape divergence was not caught: {v}"
    assert "FM_YAML_CONFORMANCE" in gaps(A, 'name: planted\ndescription: "a\\tb"'), \
        "the divergence did not surface as a GAP in the audit"


def t_malformed_is_always_an_error():
    A = load()
    if A.resolve_yaml_parser()[0] is None:
        not_run.append("PyYAML absent — the malformed check is NOT_RUN here")
        return
    v, _d = A.yaml_conformance("name: [unterminated")
    assert v == "MALFORMED", f"malformed frontmatter scored {v}, not MALFORMED"
    assert "FM_YAML_CONFORMANCE" in gaps(A, "name: [unterminated\ndescription: x"), \
        "malformed frontmatter did not raise a GAP"


def t_verdicts_are_separate():
    A = load()
    # NOT_RUN and MALFORMED and DIVERGES are distinct strings, never conflated
    A.YAML_PARSER = (None, None)
    assert A.yaml_conformance("name: x")[0] == "NOT_RUN"
    A.YAML_PARSER = (lambda s: (_ for _ in ()).throw(ValueError("boom")), "fake")
    assert A.yaml_conformance("name: x")[0] == "MALFORMED", \
        "a parser error was not classed MALFORMED"


def main():
    case("an absent parser is NOT_RUN, never a full-YAML pass",
         t_absent_parser_is_not_run_not_pass)
    case("an installed parser agrees on clean frontmatter",
         t_installed_parser_agrees_on_clean_frontmatter)
    case("a divergence from the real parser is a GAP", t_divergence_is_a_gap)
    case("malformed frontmatter is always an error", t_malformed_is_always_an_error)
    case("the verdicts are separate", t_verdicts_are_separate)
    for n in not_run:
        print(f"  NOT_RUN  {n}")
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())

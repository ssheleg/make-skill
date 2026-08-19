#!/usr/bin/env python3
"""The two checkers read the same front matter, and both read it correctly.

This repository ships a checker (`scripts/audit_skill.py`, which travels to every
agent) and runs a second one on itself (`test/validate.py`). They duplicate a
dozen rules. Until 2026-08-16 nothing compared more than one of them, and both
carried the same two false negatives:

  * a description written as a plain multi-line YAML scalar — legal YAML, folded
    into one value — had its continuation lines silently dropped. A description
    whose real length was 1392 characters was measured at 180 and passed both
    the 1024 spec cap and the 970 working limit. The family's standard-keeper
    handed a clean bill to a skill the Skills API rejects on upload.

  * `allowed-tools: [Read, Write]`, the inline flow sequence, was read as the
    literal string "[Read, Write]". TOOLS_TYPE asks `isinstance(v, str)` and got
    yes, so the check written for exactly that form never fired — on the most
    common way authors write a tool list, and the one portability defect that
    costs a skill its tool grant on every host but Claude Code.

A false negative in a checker is worse than no checker: it is a green that gets
quoted. So these fixtures plant each defect and require the checker to say so,
rather than asserting that a correct file passes.

Run by `npm test`. Standard library only, like everything else here.
"""
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDITOR = os.path.join(ROOT, "plugins/make-skill/skills/make-skill/scripts/audit_skill.py")
VALIDATOR = os.path.join(ROOT, "test/validate.py")

sys.path.insert(0, os.path.join(ROOT, "plugins/make-skill/skills/make-skill/scripts"))
import audit_skill  # noqa: E402
import residue  # noqa: E402  — sys.path[0] is this file's directory

cases = 0
failures = []


def case(name):
    def deco(fn):
        global cases
        cases += 1
        residue.open_case(name)
        try:
            fn()
        except AssertionError as e:
            # The workspace stays open — a planted defect is debugged by reading the
            # tree it landed in, and `residue` keeps the trees of a case that failed.
            failures.append("%s: %s" % (name, e))
            print("  FAIL  %s: %s" % (name, e))
        else:
            print("  ok  %s" % name)
            residue.close_case(name)
        return fn
    return deco


def skill_dir(frontmatter, body="# s\n\nBody.\n"):
    d = os.path.join(residue.workspace("planted"), "planted")
    os.makedirs(d)
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write("---\n" + frontmatter.rstrip("\n") + "\n---\n\n" + body)
    return d


def audit_ids(d, house=True):
    a = audit_skill.audit(d, house=house)
    return {r["check"]: r for r in a.results if r["verdict"] == "GAP"}


LONG = ("Use when a description is written as a plain multi-line YAML scalar, which "
        "is legal YAML and folds into a single value. " * 11).strip()


# --- the parser, both false negatives ---------------------------------------

@case("a plain multi-line description is measured whole, not at its first line")
def _():
    head, tail = LONG[:180], LONG[180:]
    d = skill_dir("name: planted\ndescription: %s\n  %s" % (head, tail))
    gaps = audit_ids(d)
    assert "DESC_LENGTH" in gaps, "a %d-char description passed the 1024 cap" % len(LONG)
    reported = int(re.search(r"is (\d+) chars", gaps["DESC_LENGTH"]["message"]).group(1))
    assert reported == len(LONG), "reported %d, the real length is %d" % (reported, len(LONG))


@case("the continuation is folded with a space, the way YAML folds it")
def _():
    fm, _l = audit_skill.parse_frontmatter("name: planted\ndescription: one\n  two\n  three")
    assert fm["description"] == "one two three", repr(fm["description"])


@case("a quoted scalar spanning lines does not keep its quotes mid-value")
def _():
    fm, _l = audit_skill.parse_frontmatter('name: planted\ndescription: "one\n  two"')
    assert fm["description"] == "one two", repr(fm["description"])


@case("an inline flow sequence is a list, so TOOLS_TYPE fires on it")
def _():
    d = skill_dir("name: planted\ndescription: Use when planting. Триггеры - посадить.\n"
                  "allowed-tools: [Read, Write]")
    assert "TOOLS_TYPE" in audit_ids(d), "allowed-tools: [Read, Write] passed as a string"


@case("a flow sequence parses to its members, not to a string that looks like one")
def _():
    fm, _l = audit_skill.parse_frontmatter("name: planted\nallowed-tools: [Read, Write]")
    assert fm["allowed-tools"] == ["Read", "Write"], repr(fm["allowed-tools"])
    fm, _l = audit_skill.parse_frontmatter("name: planted\nallowed-tools: []")
    assert fm["allowed-tools"] == [], repr(fm["allowed-tools"])


@case("the legal space-separated string is still a string, and still passes")
def _():
    fm, _l = audit_skill.parse_frontmatter("name: planted\nallowed-tools: Read Write")
    assert fm["allowed-tools"] == "Read Write", repr(fm["allowed-tools"])


@case("a block scalar still folds as it did — the fix did not move that case")
def _():
    fm, _l = audit_skill.parse_frontmatter("name: planted\ndescription: >-\n  one\n  two")
    assert fm["description"] == "one two", repr(fm["description"])


@case("a nested map still parses as a map")
def _():
    fm, _l = audit_skill.parse_frontmatter('name: planted\nmetadata:\n  version: "1.2.3"')
    assert fm["metadata"] == {"version": "1.2.3"}, repr(fm["metadata"])


# --- the house body headroom, which the shipped auditor did not apply -------

@case("--house applies the 4750 body working limit, not only the description one")
def _():
    body = "# s\n\n" + ("word " * int(4800 * audit_skill.CHARS_PER_TOKEN / 5))
    d = skill_dir("name: planted\ndescription: Use when planting. Триггеры - посадить.", body)
    assert "BODY_HEADROOM" in audit_ids(d, house=True), \
        "a body past 4750 tokens got no gap under --house"


@case("without --house the working limit is not applied — it is a house rule")
def _():
    body = "# s\n\n" + ("word " * int(4800 * audit_skill.CHARS_PER_TOKEN / 5))
    d = skill_dir("name: planted\ndescription: Use when planting.", body)
    assert "BODY_HEADROOM" not in audit_ids(d, house=False)


@case("a body inside the working limit is not gapped")
def _():
    d = skill_dir("name: planted\ndescription: Use when planting. Триггеры - посадить.")
    assert "BODY_HEADROOM" not in audit_ids(d, house=True)


# --- the drift guard: watched failing against a real divergence -------------

def validator_says(mutate):
    """Run the real validator against a copy of the repo with the auditor mutated."""
    tmp = os.path.join(residue.workspace("repo"), "repo")
    shutil.copytree(ROOT, tmp, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
    aud = os.path.join(tmp, "plugins/make-skill/skills/make-skill/scripts/audit_skill.py")
    with open(aud, encoding="utf-8") as f:
        src = f.read()
    with open(aud, "w", encoding="utf-8") as f:
        f.write(mutate(src))
    r = subprocess.run([sys.executable, os.path.join(tmp, "test/validate.py")],
                       capture_output=True, text=True, cwd=tmp)
    return r.returncode, r.stdout + r.stderr


@case("the drift guard refuses a limit that exists on one side only")
def _():
    # The exact shape that shipped: the auditor simply did not have the constant.
    code, out = validator_says(lambda s: s.replace("BODY_TARGET_TOKENS = 4750",
                                                   "BODY_TARGET_TOKENS_GONE = 4750"))
    assert code != 0, "a missing shared limit passed the gate"
    assert "BODY_TARGET_TOKENS not found" in out, out[-500:]


@case("the drift guard refuses a limit whose value differs")
def _():
    code, out = validator_says(lambda s: s.replace("DESC_TARGET = 970", "DESC_TARGET = 900"))
    assert code != 0, "a diverged shared limit passed the gate"
    assert "DESC_TARGET differs" in out, out[-500:]


@case("the drift guard refuses a front-matter key legal on one side only")
def _():
    code, out = validator_says(
        lambda s: s.replace('"background", "hooks", "paths", "shell",',
                            '"background", "hooks", "paths",'))
    assert code != 0, "a diverged key set passed the gate"
    assert "HOST_KEYS differs" in out, out[-500:]


if failures:
    print("\n%d failure(s) out of %d cases" % (len(failures), cases))
    sys.exit(1)
print("PASS: checker parity — %d cases" % cases)

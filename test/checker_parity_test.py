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
    # A measured context, pinned: house thresholds ride the MEASURED count
    # only (FIX-MS-01.01), so the fake adapter makes the case deterministic
    # on machines with and without tiktoken alike.
    audit_skill.TOKENIZER = (lambda text: 4800, "fake-test")
    try:
        d = skill_dir("name: planted\ndescription: Use when planting. Триггеры - посадить.", "# s\n\nbody")
        assert "BODY_HEADROOM" in audit_ids(d, house=True), \
            "a body past 4750 measured tokens got no gap under --house"
    finally:
        audit_skill.TOKENIZER = None


@case("without --house the working limit is not applied — it is a house rule")
def _():
    audit_skill.TOKENIZER = (lambda text: 4800, "fake-test")
    try:
        d = skill_dir("name: planted\ndescription: Use when planting.", "# s\n\nbody")
        assert "BODY_HEADROOM" not in audit_ids(d, house=False)
    finally:
        audit_skill.TOKENIZER = None


@case("a body inside the working limit is not gapped")
def _():
    audit_skill.TOKENIZER = (lambda text: 100, "fake-test")
    try:
        d = skill_dir("name: planted\ndescription: Use when planting. Триггеры - посадить.")
        assert "BODY_HEADROOM" not in audit_ids(d, house=True)
    finally:
        audit_skill.TOKENIZER = None


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


@case("a description that says WHEN and never WHAT is refused")
def _():
    # B-139: nine `DESC_*` rules asked WHEN and not one asked WHAT. Anthropic's guidance
    # wants both halves, and `B-76` quoted the failure directly — *a description that
    # never says what the skill does passes*.
    d = skill_dir('name: planted\ndescription: Use when the user asks. '
                  'Triggers - "делай" / "do it", "почини" / "fix".')
    gaps = audit_ids(d, house=True)
    assert "DESC_WHAT" in gaps, "an opener plus a trigger list passed as a description"
    left = int(re.search(r"(\d+) chars remain", gaps["DESC_WHAT"]["message"]).group(1))
    assert left < 60, "the WHAT half measured %d, which is not the planted shape" % left


@case("both spellings of one description reach the same WHAT verdict")
def _():
    # The prototype this rule replaces was built on raw text and refused: it reported a
    # 0-character WHAT half for six skills and missed the opening clause of twenty,
    # because several descriptions are YAML block scalars a raw-text regex reads past.
    # `what_half` is fed the PARSED value, so the spelling cannot change the verdict.
    #
    # Scope stated rather than implied: the FOLDING itself is guarded by its own case
    # above ("a block scalar still folds as it did"), which is where a regression in
    # `parse_frontmatter` lands. This case is about the RULE agreeing with itself, and a
    # fixture that claimed the parser's property would be reporting somebody else's work.
    plain = ('Use when a release needs cutting - it tags the tree, runs the suite '
             'against that tag and publishes only if green. '
             'Triggers - "зарелизь" / "release it".')
    folded = ('name: planted\ndescription: >-\n  Use when a release needs cutting - it '
              'tags the tree, runs\n  the suite against that tag and publishes only if '
              'green.\n  Triggers - "зарелизь" / "release it".')
    a = audit_ids(skill_dir("name: planted\ndescription: " + plain), house=True)
    b = audit_ids(skill_dir(folded), house=True)
    assert "DESC_WHAT" not in a, "the plain spelling was refused: %r" % a.get("DESC_WHAT")
    assert "DESC_WHAT" not in b, "the block scalar was refused where the plain one passed"
    # and neither passed vacuously: the rule must have measured a real WHAT half
    assert len(audit_skill.what_half(plain)) >= audit_skill.DESC_WHAT_MIN
    # the parsed value never carries a newline, which is the contract this rule needs
    assert "\n" not in audit_skill.parse_frontmatter(folded + "\n")[0]["description"]


@case("the WHAT floor clears every shipped description by more than double")
def _():
    # A floor tuned so tightly that an honest description trips it would be lowered away
    # on its first false positive. Measured across the family, the smallest honest WHAT
    # half is 149 characters, so the floor of 60 has room that can be stated.
    assert audit_skill.DESC_WHAT_MIN * 2 < 149, (
        "the floor is no longer clear of the smallest measured WHAT half; re-measure "
        "before raising it, because the number 149 is a fact about a tree that moves")


if failures:
    print("\n%d failure(s) out of %d cases" % (len(failures), cases))
    sys.exit(1)
print("PASS: checker parity — %d cases" % cases)

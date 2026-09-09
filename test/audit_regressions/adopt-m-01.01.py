#!/usr/bin/env python3
"""ADOPT-M-01.01 — selective reference loading with a budget (sherlock audit).

The adoption: authoring doctrine states the load condition for every reference
and the primary/appendix split; mandatory decisions and acceptance are never
truncated to fit a budget; "500 lines" is a length heuristic, and a token figure
is either measured by a named tokenizer or an explicitly labeled estimate.

The acceptance, driven against the SHIPPED checker (`scripts/audit_skill.py`)
as a process, on fixtures built here:

* a large multilingual fixture whose body names only the required variant with
  a load condition passes the pointer rule — and the bulk "see references/"
  shape is flagged;
* a required reference that does not resolve is a gap and a non-zero exit —
  dispatch is blocked, not warned;
* every token figure the checker prints is an explicit estimate (`~N`, with the
  chars-per-token basis printed in the gap wording), never a bare count.

Standard library only.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill")
CHECKER = os.path.join(SKILL, "scripts", "audit_skill.py")
AUTHORING = os.path.join(SKILL, "references", "authoring.md")

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


FRONT = """---
name: fixture-skill
description: A fixture skill for the selective-loading acceptance. Use when the
  regression drives the shipped checker against a controlled bundle.
license: MIT
---

# Fixture skill

"""

# Bulk enough to be a real multilingual bundle: the Russian variant costs more
# tokens per character, which is the whole reason variants are selected, not summed.
RU_BODY = ("## Содержание\n\n" + "Правило программы, изложенное по-русски. " * 400)
EN_BODY = ("## Contents\n\n" + "The programme rule, stated in English. " * 400)


def fixture(body, refs):
    d = tempfile.mkdtemp(prefix="adopt-m-0101-")
    skill_dir = os.path.join(d, "fixture-skill")
    os.makedirs(os.path.join(skill_dir, "references"))
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as fh:
        fh.write(FRONT + body + "\n")
    for name, text in refs.items():
        with open(os.path.join(skill_dir, "references", name), "w") as fh:
            fh.write(text)
    return d, skill_dir


def run_checker(skill_dir):
    return subprocess.run([sys.executable, CHECKER, skill_dir],
                          capture_output=True, text=True, timeout=120)


def t_doctrine_states_the_contract():
    text = open(AUTHORING, encoding="utf-8").read()
    for needle, name in [
        ("## Selective loading — every reference earns its tokens", "the section exists"),
        ("Every reference states its own load condition", "load condition per reference"),
        ("Split primary from appendix", "the primary/appendix split"),
        ("mandatory decisions and acceptance are never truncated", "no truncation of the contract"),
        ("the load condition names WHICH variant", "variant selection"),
        ("blocks the work", "missing required ref blocks"),
        ("lines are only a heuristic", "500 lines is a heuristic, not a proof"),
        ("measured by a named tokenizer", "tokenizer or labeled estimate"),
    ]:
        assert needle in text, f"{name}: {needle!r} is not in authoring.md"
    assert "- Selective loading" in text, "the Contents list does not name the section"


def t_required_variant_only_passes():
    """The body names ONE variant with a load condition; the other is appendix
    behind its own condition. No pointer gap, and the estimate is labeled."""
    body = ("Read `references/guide.en.md` when the host surface is English-facing —\n"
            "it is the primary contract. Read `references/guide.ru.md` only when the\n"
            "operator asked for the Russian appendix wording.\n")
    d, skill_dir = fixture(body, {"guide.en.md": EN_BODY, "guide.ru.md": RU_BODY})
    try:
        r = run_checker(skill_dir)
        assert r.returncode == 0, f"the variant-selecting fixture failed:\n{r.stdout[-500:]}"
        assert "REF_POINTER" not in r.stdout, "a stated per-variant condition was flagged as a pointer"
    finally:
        shutil.rmtree(d)


def t_bulk_pointer_is_flagged():
    # No backticks: the checker deliberately exempts quoted spans (a canon that
    # forbids the phrase has to be able to quote it), so the instruction shape
    # under test is the bare one an author actually writes.
    body = "For everything else, see references/ for details.\n"
    d, skill_dir = fixture(body, {"guide.en.md": EN_BODY, "guide.ru.md": RU_BODY})
    try:
        r = run_checker(skill_dir)
        assert r.returncode != 0, "a directory pointer loaded the whole bundle and passed"
        assert "load condition" in r.stdout, f"the gap does not name the missing load condition:\n{r.stdout[-300:]}"
    finally:
        shutil.rmtree(d)


def t_missing_required_ref_blocks_dispatch():
    body = ("The acceptance criteria live in [the contract](references/contract.md) —\n"
            "read it before implementing anything.\n")
    d, skill_dir = fixture(body, {})  # contract.md deliberately absent
    try:
        r = run_checker(skill_dir)
        assert r.returncode != 0, "a missing required reference did not block"
        assert "LINK_BROKEN" in r.stdout, f"the gap does not name the broken link:\n{r.stdout[-300:]}"
    finally:
        shutil.rmtree(d)


def t_token_figures_are_labeled_estimates():
    """A body past the budget: the verdict either carries the estimate marker
    and its basis, or names the tokenizer that MEASURED it (FIX-MS-01.01/.02)
    — a bare number that says neither reads as physics."""
    long_body = "Read `references/guide.en.md` when starting.\n\n" + ("An English rule line. " * 2600)
    d, skill_dir = fixture(long_body, {"guide.en.md": EN_BODY})
    try:
        r = run_checker(skill_dir)
        out = r.stdout
        assert "BODY_TOKENS" in out or "BODY_HEADROOM" in out, \
            f"a 2600-sentence body raised no token verdict:\n{out[-300:]}"
        token_lines = [l for l in out.splitlines() if "token" in l and ("BODY" in l)]
        assert token_lines, "no token verdict line found"
        assert any(("~" in l and "chars" in out) or "tiktoken:" in l
                   for l in token_lines), \
            (f"a token figure names neither its estimate basis nor its "
             f"tokenizer: {token_lines[:2]}")
    finally:
        shutil.rmtree(d)


def main():
    case("the doctrine states the selective-loading contract", t_doctrine_states_the_contract)
    case("a body naming only the required variant passes", t_required_variant_only_passes)
    case("a directory pointer is flagged as a missing load condition", t_bulk_pointer_is_flagged)
    case("a missing required reference blocks dispatch (non-zero)", t_missing_required_ref_blocks_dispatch)
    case("token figures are labeled estimates with their basis", t_token_figures_are_labeled_estimates)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

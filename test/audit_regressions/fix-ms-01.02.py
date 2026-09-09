#!/usr/bin/env python3
"""FIX-MS-01.02 — the tokenizer corpus and threshold authority (sherlock
audit, second leaf of MS-01, on FIX-MS-01.01's honest token result).

The rules under test, against scripts/audit_skill.py:

* the differential corpus (EN/code/RU/mixed/CJK) pins counts per tokenizer
  REVISION: with tiktoken installed the adapter must agree with every
  pinned count, twice (determinism); without it the differential is
  NOT_RUN, never PASS;
* an unsupported MAKE_SKILL_TOKENIZER refuses to measure — no silent
  fallback to another encoding or to the estimate;
* every named threshold carries its authority: spec, house or host — a
  number without its owner reads as physics.

Standard library only (tiktoken used only if already present).
"""
import importlib.util
import os
import sys

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


def t_corpus_agrees_or_not_run():
    A = load()
    os.environ.pop("MAKE_SKILL_TOKENIZER", None)
    v1, d1 = A.corpus_check()
    A.TOKENIZER = None
    v2, d2 = A.corpus_check()
    assert (v1, d1) == (v2, d2), "two runs of the differential diverged"
    if v1 == "NOT_RUN":
        not_run.append(f"differential NOT_RUN on this machine: {d1}")
        return
    assert v1 == "agree", f"the adapter disagrees with the pinned oracle: {d1}"
    assert len(A.TOKEN_CORPUS) >= 5
    kinds = set(A.TOKEN_CORPUS)
    assert {"english", "code", "russian", "mixed", "cjk"} <= kinds, \
        f"the corpus lost a language axis: {kinds}"


def t_unsupported_tokenizer_refuses():
    A = load()
    os.environ["MAKE_SKILL_TOKENIZER"] = "no-such-encoding"
    try:
        A.TOKENIZER = None
        fn, name = A.resolve_tokenizer()
        assert fn is None and name is None, \
            "an unsupported tokenizer resolved to something — a silent substitute"
        v, d = A.corpus_check()
        assert v == "NOT_RUN", f"the differential {v} under an unsupported tokenizer"
    finally:
        os.environ.pop("MAKE_SKILL_TOKENIZER", None)


def t_wrong_revision_is_a_different_instrument():
    A = load()
    A.TOKENIZER = (lambda text: 999, "tiktoken:o200k_base")
    v, d = A.corpus_check()
    assert v == "NOT_RUN" and "different instrument" in d, \
        "pinned cl100k counts were compared against a different encoding"


def t_disagreement_is_named():
    A = load()
    A.TOKENIZER = (lambda text: 1, f"tiktoken:{A.DEFAULT_ENCODING}")
    v, d = A.corpus_check()
    assert v == "DISAGREE" and "adapter says 1" in d, \
        f"a divergent count was not named: {v}, {d}"


def t_thresholds_carry_their_authority():
    A = load()
    assert A.THRESHOLDS["BODY_MAX_TOKENS"] == ("spec", A.BODY_MAX_TOKENS)
    assert A.THRESHOLDS["BODY_TARGET_TOKENS"] == ("house", A.BODY_TARGET_TOKENS)
    assert A.THRESHOLDS["BODY_MAX_LINES"] == ("spec", A.BODY_MAX_LINES)
    owners = {o for (o, _v) in A.THRESHOLDS.values()}
    assert owners <= {"spec", "house", "host"}, f"an unowned authority: {owners}"


def main():
    case("the corpus agrees with the pinned oracle, deterministically "
         "(or NOT_RUN)", t_corpus_agrees_or_not_run)
    case("an unsupported tokenizer refuses — no silent substitute",
         t_unsupported_tokenizer_refuses)
    case("a different revision is a different instrument, not a comparison",
         t_wrong_revision_is_a_different_instrument)
    case("a disagreement is named per sample", t_disagreement_is_named)
    case("every threshold carries its authority", t_thresholds_carry_their_authority)
    for n in not_run:
        print(f"  NOT_RUN  {n}")
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())

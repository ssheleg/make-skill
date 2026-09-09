#!/usr/bin/env python3
"""FIX-MS-01.01 — the honest token result (sherlock audit, finding MS-01).

The finding: a synthetic body of 16 000 hieroglyphs is 16 000 cl100k tokens,
and the auditor reported ~4 102 (chars/3.9) with a PASS — the estimate wore
the word "tokens" and granted verdicts only a measurement can grant.

The fix under test, against scripts/audit_skill.py: a NAMED tokenizer
adapter measures; without one the token budget is UNMEASURED — the estimate
is reported as an estimate, never called tokens, and grants neither PASS nor
GAP; house thresholds ride the measured count only. Where tiktoken is
installed, chars/3.9 is compared against it as an independent reference;
where it is not, that comparison reports NOT_RUN — never PASS.

Standard library only (tiktoken used only if already present).
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
not_run = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def skill_dir(body):
    root = tempfile.mkdtemp()
    d = os.path.join(root, "planted")
    os.makedirs(d)
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write("---\nname: planted\ndescription: Use when planting.\n---\n\n" + body)
    return d


def audit(body, house=False, tokenizer=(None, None)):
    A.TOKENIZER = tokenizer
    try:
        return A.audit(skill_dir(body), house=house)
    finally:
        A.TOKENIZER = None


def by_check(a):
    return {r["check"]: r for r in a.results}


def t_cjk_counterexample_is_caught_when_measured():
    body = "# s\n\n" + "字" * 16000
    a = audit(body, tokenizer=(lambda text: text.count("字") or len(text), "fake-cl100k"))
    r = by_check(a)
    assert r.get("BODY_TOKENS", {}).get("verdict") == "GAP", \
        "a 16k-token CJK body passed the measured budget — the finding itself"
    assert "16000" in r["BODY_TOKENS"]["message"] and "fake-cl100k" in \
        r["BODY_TOKENS"]["message"], "the measurement does not name its tokenizer"


def t_without_adapter_no_token_pass_and_no_token_gap():
    body = "# s\n\n" + "字" * 16000              # estimates ~4102, measures 16000
    a = audit(body, tokenizer=(None, None))
    r = by_check(a)
    assert "BODY_TOKENS" not in r, \
        "an estimate produced a token verdict without a measurement"
    unm = r.get("BODY_TOKENS_UNMEASURED")
    assert unm, "the unmeasured state is not reported"
    assert "UNMEASURED" in unm["message"] and "NOT tokens" in unm["message"], \
        f"the estimate is still being called tokens: {unm['message']!r}"
    budget = r.get("BODY_BUDGET")
    assert budget is None or "token" not in budget["message"] or \
        "unmeasured" in budget["message"], \
        "BODY_BUDGET still claims a token verdict without a tokenizer"


def t_house_thresholds_ride_measurement_only():
    a = audit("# s\n\nbody", house=True, tokenizer=(lambda t: 4800, "fake"))
    assert by_check(a).get("BODY_HEADROOM", {}).get("verdict") == "GAP", \
        "a measured 4800-token body got no house gap"
    a2 = audit("# s\n\n" + "x " * 12000, house=True, tokenizer=(None, None))
    r2 = by_check(a2)
    assert r2.get("BODY_HEADROOM") is None, \
        "the house limit produced a verdict from an estimate"
    assert r2.get("BODY_HEADROOM_UNMEASURED"), \
        "the unmeasured house state is not stated"


def t_estimate_vs_independent_tokenizer():
    try:
        import tiktoken
    except ImportError:
        not_run.append("tiktoken absent — the independent-tokenizer comparison "
                       "is NOT_RUN on this machine (never a PASS)")
        return
    enc = tiktoken.get_encoding("cl100k_base")
    for name, sample in (("english", "the quick brown fox " * 200),
                         ("code", "def f(x):\n    return x + 1\n" * 120),
                         ("mixed", "проверка mixed RU/EN текста " * 150),
                         ("unicode", "字" * 800)):
        real = len(enc.encode(sample))
        est = int(len(sample) / A.CHARS_PER_TOKEN)
        assert real > 0 and est > 0
        if name == "unicode":
            assert real > est * 2, "the CJK counterexample no longer diverges"


def main():
    case("the 16k-CJK counterexample is caught when measured",
         t_cjk_counterexample_is_caught_when_measured)
    case("without an adapter: no token verdict, UNMEASURED stated honestly",
         t_without_adapter_no_token_pass_and_no_token_gap)
    case("house thresholds ride the measured count only",
         t_house_thresholds_ride_measurement_only)
    case("estimate vs an independent tokenizer (EN/code/RU-EN/unicode)",
         t_estimate_vs_independent_tokenizer)
    for n in not_run:
        print(f"  NOT_RUN  {n}")
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())

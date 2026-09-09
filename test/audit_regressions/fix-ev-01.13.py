#!/usr/bin/env python3
"""FIX-EV-01.13 — the outcome corpus for make-skill (sherlock audit, parent
FIX-EV-01; depends on the family harness of FIX-EV-01.01).

The corpus (evals/cases/make-skill.json) holds a positive, a negative
(routing), an audit-does-not-mutate case (MS-03), a tokenizer-probed
measurement case (MS-01) and a strict-validate case gated on the claude CLI
— judged on ARTIFACTS through the family's outcome-case contract, so
make-skill can no longer pass an eval by its name being picked.

Checked here, stdlib only:

* every case is structurally valid (version, frozen prompt, real case
  digest, non-empty artifact-reading outcome checks);
* the negative case forbids the skill from loading; the mutate case pins
  the audited fixture's digest so an audit that edits fails its oracle;
* the tokenizer and claude-cli cases are probe-gated: an absent tool is
  NOT_RUN, never a chars/3.9 PASS;
* where the family harness is present on this machine it validates each
  case for real; where absent that check reports NOT_RUN — never PASS.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CASES = os.path.join(ROOT, "evals", "cases", "make-skill.json")
FIXTURE = os.path.join(ROOT, "test", "evals", "fixtures", "untrusted-skill.md")
HARNESS = os.path.expanduser("~/DATA/sshlg-skills/test/outcome_harness.py")

failures = []
not_run = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def manifest():
    with open(CASES, encoding="utf-8") as fh:
        return json.load(fh)


def t_cases_are_structurally_valid():
    m = manifest()
    ids = [c["id"] for c in m["cases"]]
    assert len(ids) == len(set(ids)) and len(ids) >= 5, \
        f"corpus too small or duplicated: {ids}"
    for c in m["cases"]:
        assert c["schema_version"] == "outcome-case/1"
        assert c["skill"] == "make-skill"
        text = c["prompt"]["text"].strip()
        assert text, f"{c['id']}: empty frozen prompt"
        assert c["environment"]["case_digest"] == \
            hashlib.sha256(c["prompt"]["text"].encode()).hexdigest(), \
            f"{c['id']}: case_digest does not pin the frozen prompt"
        assert c["checks"]["outcome"], \
            f"{c['id']}: no outcome checks — the name-picking eval again"
        for o in c["checks"]["outcome"]:
            assert o["kind"] in ("artifact-exists", "artifact-digest",
                                 "artifact-contains", "command-exit-0")


def t_negative_forbids_loading():
    m = manifest()
    neg = next(c for c in m["cases"] if "negative" in c["id"])
    assert "make-skill" in neg["checks"]["load_trace"]["expect_not_loaded"], \
        "the negative case does not forbid the skill from loading"
    assert not neg["checks"]["load_trace"]["expect_loaded"]


def t_audit_does_not_mutate_is_pinned_to_real_bytes():
    m = manifest()
    c = next(x for x in m["cases"] if "does-not-mutate" in x["id"])
    cmd = next(o for o in c["checks"]["outcome"] if o["kind"] == "command-exit-0")
    pinned = re.search(r"!= '([0-9a-f]{64})'", cmd["target"])
    assert pinned, "the mutate oracle pins no digest"
    with open(FIXTURE, "rb") as fh:
        actual = hashlib.sha256(fh.read()).hexdigest()
    assert pinned.group(1) == actual, \
        "the pinned digest no longer matches the fixture — re-pin it in the corpus"
    r = subprocess.run(["bash", "-c", cmd["target"]], capture_output=True,
                       cwd=ROOT, timeout=30)
    assert r.returncode == 0, "the unchanged-bytes oracle fails on pristine bytes"


def t_probed_cases_gate_on_their_tool():
    m = manifest()
    tok = next(c for c in m["cases"] if "token-measurement" in c["id"])
    assert "import tiktoken" in tok["checks"]["tool"][0]["command"], \
        "the tokenizer case has no import probe — chars/3.9 could PASS it"
    cli = next(c for c in m["cases"] if "strict-plugin-validate" in c["id"])
    assert "claude --version" in cli["checks"]["tool"][0]["command"], \
        "the strict-validate case has no CLI probe — it cannot NOT_RUN"


def t_manifest_records_the_rules():
    m = manifest()
    flat = " ".join(json.dumps(m, ensure_ascii=False).split())
    for needle in ("actual output oracle", "raw result", "with/without-skill",
                   "NOT_RUN", "chars/3.9", "grader convenience"):
        assert needle in flat, f"the manifest no longer records {needle!r}"
    assert "baseline" in m["arms"] and "current" in m["arms"]


def t_family_harness_validates_each_case_where_present():
    if not os.path.isfile(HARNESS):
        not_run.append("family harness absent at ~/DATA/sshlg-skills — case-level "
                       "validation NOT_RUN on this machine (never a PASS)")
        return
    for c in manifest()["cases"]:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(c, fh)
            path = fh.name
        try:
            r = subprocess.run([sys.executable, HARNESS, path],
                               capture_output=True, text=True, timeout=60)
            assert r.returncode == 0, \
                f"{c['id']} rejected by the family harness:\n{r.stdout}"
        finally:
            os.unlink(path)


def main():
    case("every case is structurally valid, none is name-picking",
         t_cases_are_structurally_valid)
    case("the negative case forbids the skill from loading", t_negative_forbids_loading)
    case("the audit-does-not-mutate oracle pins the fixture's real bytes",
         t_audit_does_not_mutate_is_pinned_to_real_bytes)
    case("tokenizer and claude-cli cases are probe-gated (NOT_RUN, not PASS)",
         t_probed_cases_gate_on_their_tool)
    case("the manifest records oracle/raw/arms/approximation rules",
         t_manifest_records_the_rules)
    case("the family harness validates each case (where present)",
         t_family_harness_validates_each_case_where_present)
    for n in not_run:
        print(f"  NOT_RUN  {n}")
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())

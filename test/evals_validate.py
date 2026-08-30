#!/usr/bin/env python3
# shared-mechanism: sshlg-skills/public-contract-evals-v1
# diverges: RESULTS.md stated counts are compared against the artifacts (MSK-02)
"""Validate the portable behavioral-evaluation data in test/evals."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: {exc}") from exc


# A number typed into RESULTS.md is an assertion until something compares it to
# the artifact: this file shipped "20 queries" over a triggers.json holding 22
# (MSK-02) — the exact drift class the skill's own gotcha list forbids. Each
# claim must both parse and match; a RESULTS.md that stopped stating a count
# is refused rather than passed vacuously.
RESULTS_COUNT_CLAIMS = (
    (re.compile(r"`triggers\.json`\s*\((\d+)\s+queries\)"),
     "queries", "queries in triggers.json"),
    (re.compile(r"`scenarios\.json`\s*\((\d+)\s+(?:behaviou?ral\s+)?scenarios\)"),
     "scenarios", "scenarios in scenarios.json"),
)


def results_count_gaps(results_text: str, actual: dict) -> list[str]:
    gaps: list[str] = []
    for pattern, key, label in RESULTS_COUNT_CLAIMS:
        claims = pattern.findall(results_text)
        if not claims:
            gaps.append(
                f"RESULTS.md: no parseable count claim for {label} — this "
                "comparison would pass vacuously; state the count in the "
                "`<file>` (N ...) form so it stays checkable"
            )
            continue
        for claimed in claims:
            if int(claimed) != actual[key]:
                gaps.append(
                    f"RESULTS.md: claims {claimed} {label} where the artifact "
                    f"holds {actual[key]} — a hand-typed count is an assertion; "
                    "update the sentence, this check keeps it from drifting again"
                )
    return gaps


def validate(root: Path, trigger_override=None) -> list[str]:
    gaps: list[str] = []
    required = ("README.md", "RESULTS.md", "triggers.json", "scenarios.json")
    for name in required:
        if not (root / name).is_file():
            gaps.append(f"missing {root / name}")
    if gaps:
        return gaps

    triggers = trigger_override if trigger_override is not None else load(root / "triggers.json")
    queries = triggers.get("queries")
    if not isinstance(queries, list) or len(queries) < 6:
        gaps.append("triggers.json: queries must contain at least 6 cases")
        queries = []
    ids: list[str] = []
    classes: dict[str, bool] = {}
    for query in queries:
        if not isinstance(query, dict):
            gaps.append("triggers.json: every query must be an object")
            continue
        qid = query.get("id")
        if not isinstance(qid, str) or not qid:
            gaps.append("triggers.json: every query needs a non-empty string id")
            continue
        ids.append(qid)
        if type(query.get("should_trigger")) is not bool:
            gaps.append(f"triggers.json: {qid} should_trigger must be boolean")
        else:
            classes[qid] = query["should_trigger"]
        for field in ("query", "why"):
            if not isinstance(query.get(field), str) or not query[field].strip():
                gaps.append(f"triggers.json: {qid} needs non-empty {field}")

    if len(ids) != len(set(ids)):
        gaps.append("triggers.json: query ids must be unique")
    if set(classes.values()) != {True, False}:
        gaps.append("triggers.json: both positive and negative cases are required")

    split = triggers.get("split")
    if not isinstance(split, dict):
        gaps.append("triggers.json: split object is required")
    else:
        seen: list[str] = []
        for half in ("train", "validation"):
            members = split.get(half)
            if not isinstance(members, list) or not members:
                gaps.append(f"triggers.json: split.{half} must be a non-empty list")
                continue
            seen.extend(members)
            known = [classes[item] for item in members if item in classes]
            if set(known) != {True, False}:
                gaps.append(f"triggers.json: split.{half} needs both classes")
        if sorted(seen) != sorted(ids):
            gaps.append("triggers.json: split must cover every query exactly once")

    scenario_doc = load(root / "scenarios.json")
    scenarios = scenario_doc.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) < 3:
        gaps.append("scenarios.json: at least 3 scenarios are required")
        scenarios = []
    scenario_ids: list[str] = []
    repo = root.parent.parent
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            gaps.append("scenarios.json: every scenario must be an object")
            continue
        sid = scenario.get("id")
        if not isinstance(sid, str) or not sid:
            gaps.append("scenarios.json: every scenario needs an id")
            continue
        scenario_ids.append(sid)
        for field in ("title", "query"):
            if not isinstance(scenario.get(field), str) or not scenario[field].strip():
                gaps.append(f"scenarios.json: {sid} needs non-empty {field}")
        skills = scenario.get("skills")
        if not isinstance(skills, list) or not skills or not all(isinstance(x, str) and x for x in skills):
            gaps.append(f"scenarios.json: {sid} needs a non-empty skills list")
        expected = scenario.get("expected_behavior")
        if not isinstance(expected, list) or len(expected) < 3 or not all(
            isinstance(x, str) and x.strip() for x in expected
        ):
            gaps.append(f"scenarios.json: {sid} needs at least 3 expected_behavior lines")
        files = scenario.get("files", [])
        if not isinstance(files, list):
            gaps.append(f"scenarios.json: {sid} files must be a list")
        else:
            for rel in files:
                if not isinstance(rel, str) or not (repo / rel).is_file():
                    gaps.append(f"scenarios.json: {sid} fixture does not resolve: {rel!r}")
    if len(scenario_ids) != len(set(scenario_ids)):
        gaps.append("scenarios.json: scenario ids must be unique")

    results_text = (root / "RESULTS.md").read_text(encoding="utf-8")
    gaps.extend(results_count_gaps(
        results_text, {"queries": len(queries), "scenarios": len(scenarios)}
    ))
    return gaps


def self_test(root: Path) -> None:
    planted = copy.deepcopy(load(root / "triggers.json"))
    planted["queries"][0]["should_trigger"] = "yes"
    gaps = validate(root, trigger_override=planted)
    if not any("should_trigger must be boolean" in gap for gap in gaps):
        raise SystemExit("negative self-test failed: planted invalid boolean was accepted")
    print("OK: negative self-test planted and caught an invalid trigger class")

    actual = {
        "queries": len(load(root / "triggers.json")["queries"]),
        "scenarios": len(load(root / "scenarios.json")["scenarios"]),
    }
    results_text = (root / "RESULTS.md").read_text(encoding="utf-8")
    wrong = re.sub(r"\((\d+)(\s+queries\))",
                   lambda m: f"({int(m.group(1)) + 1}{m.group(2)}",
                   results_text, count=1)
    gaps = results_count_gaps(wrong, actual)
    if not any("where the artifact holds" in gap for gap in gaps):
        raise SystemExit("negative self-test failed: planted off-by-one count was accepted")
    gaps = results_count_gaps("a RESULTS.md that states no counts at all", actual)
    if sum("no parseable count claim" in gap for gap in gaps) != len(RESULTS_COUNT_CLAIMS):
        raise SystemExit("negative self-test failed: a claim-free RESULTS.md passed vacuously")
    print("OK: negative self-test caught a planted off-by-one count and refused a "
          "claim-free RESULTS.md")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("test/evals"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test(args.root)
        return 0
    gaps = validate(args.root)
    for gap in gaps:
        print(f"GAP: {gap}")
    if gaps:
        return 1
    triggers = load(args.root / "triggers.json")["queries"]
    scenarios = load(args.root / "scenarios.json")["scenarios"]
    print(f"OK: {len(triggers)} trigger cases and {len(scenarios)} scenarios validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

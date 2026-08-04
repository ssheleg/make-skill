# Evaluation results

**Status: authored, never executed against a model.**

`triggers.json` (20 queries) and `scenarios.json` (4 behavioural scenarios) exist
and are validated for shape on every commit — query count, both classes present
on both sides of the split, three or more scenarios, every referenced fixture on
disk. None of that measures behaviour.

Running them needs an agent session per query, which no CI job here does. Until
this file carries a dated table, the honest statement is: **this skill is proven
well-formed and unproven in use.** `SKILL-CARD.md` says the same to a reviewer.

## What a run must record

| Date | Version | Model | Trigger pass rate (train / validation) | Scenario lines passed | Notes |
|---|---|---|---|---|---|
| — | — | — | — | — | no run yet |

For each run:

- the model and the make-skill version, because both change the answer;
- the trigger rate per query (fired / 3), not just the average;
- which `expected_behavior` lines failed, line by line — a scenario is scored per
  line so a partial regression stays visible;
- what was installed alongside it. Coexistence is a property of the set, not of
  the skill: `task-pipeline` shares vocabulary with this skill's triggers
  ("pipeline", "release", "audit"), and that overlap is exactly what a run should
  measure.

## Known adjacent risk to watch first

This skill's description is long and deliberately pushy. The near-miss negatives
in `triggers.json` (q11–q20) exist because of it: "review my pull request",
"publish this React library to npm", "implement an MCP server for Postgres" all
share its vocabulary and must NOT fire it. If a run shows any of those firing,
the description is stealing turns from every other skill installed, and the fix
is the description — not the body.

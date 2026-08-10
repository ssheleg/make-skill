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
in `triggers.json` (q11–q22) exist because of it: "review my pull request",
"publish this React library to npm", "implement an MCP server for Postgres" all
share its vocabulary and must NOT fire it. If a run shows any of those firing,
the description is stealing turns from every other skill installed, and the fix
is the description — not the body.

**The nearest neighbour is measured, not guessed — and it is not the one this
file used to name.** Earlier revisions predicted `task-pipeline`, on the grounds
of shared vocabulary ("pipeline", "release", "audit"). Measuring instead of
asserting, across the 130 skills of the 23 enabled plugins on the author's
machine (2026-08-10), gives:

| Neighbour | Description overlap | Shared trigger words |
|---|---|---|
| **`claude-mem:version-bump`** | **9.6%** | claude code, json, marketplace, plugin, plugins, publishing, version |
| `agent-sync` | 5.5% | agent, claude, json, sync |
| `task-pipeline` | 4.7% | code, pipeline, skill, spec, sync |

`version-bump` advertises "version increments across package.json,
marketplace.json, plugin.json manifests, git tagging, GitHub releases, and
changelog generation" — this skill's release checklist, word for word, and it is
enabled alongside. The overlap is not vocabulary, it is *job*.

Two consequences, both now addressed and both to be re-measured on the first
real run:

- the description carries an explicit **"NOT for a version bump or release in a
  repo that ships anything but a skill or plugin"** clause, which is the remedy
  `references/authoring.md` prescribes for a near-miss;
- **q21 and q22** put the ambiguity itself into the trigger set — the same
  manifest-bump-and-release request, once where the artifact IS a skill and once
  where it is not — and they sit on opposite sides of the split so the near-miss
  is measured in validation rather than tuned on.

Re-measure the neighbour table whenever the installed set changes: coexistence is
a property of the set, not of the skill.

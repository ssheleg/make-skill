# Evaluation results

**Status: first executed 2026-08-31, on two models, with the method and its
limits stated below.** Before that date this file said "authored, never
executed", and that state is preserved in git history rather than restated here.

`triggers.json` (22 queries) and `scenarios.json` (4 behavioural scenarios) are
validated for shape on every commit — query count, both classes present on both
sides of the split, three or more scenarios, every referenced fixture on disk —
and the counts in this file are compared against the artifacts by
`test/evals_validate.py`, so a stated number cannot drift silently.

## Dated runs

| Date | Version | Model | Trigger pass rate (train / validation) | Scenario lines passed | Notes |
|---|---|---|---|---|---|
| 2026-08-31 | 0.25.2 rc (description byte-identical to 0.25.1) | haiku (Agent-tool alias; exact model id not exposed by the harness) | 13/13 train, 9/9 validation — 22/22 | s01 7/10 · s02 10/11 · s03 1/6 · s04 6/8 — 24/35 | zero false positives on q11–q22; the losses are in scenario execution, worst on s03 (never loaded the skill, answered the surfaces question from priors) |
| 2026-08-31 | 0.25.2 rc (description byte-identical to 0.25.1) | sonnet (Agent-tool alias; exact model id not exposed by the harness) | 12/13 train (q01 missed), 8/9 validation (q10 missed) — 20/22 | s01 10/10 · s02 10/11 · s03 4/6 · s04 7/8 — 31/35 | zero false positives; both misses are FALSE NEGATIVES on positives — under-triggering, not turn-stealing |

### Per-query trigger answers, 2026-08-31 (one blind probe per query per model)

| q | class | haiku answered | sonnet answered |
|---|---|---|---|
| q01 | pos | make-skill ✓ | none ✗ |
| q02 | pos | make-skill ✓ | make-skill ✓ |
| q03 | pos | make-skill ✓ | make-skill ✓ |
| q04 | pos | make-skill ✓ | make-skill ✓ * |
| q05 | pos | make-skill ✓ | make-skill ✓ |
| q06 | pos | make-skill ✓ | make-skill ✓ |
| q07 | pos | make-skill ✓ | make-skill ✓ |
| q08 | pos | make-skill ✓ | make-skill ✓ |
| q09 | pos | make-skill ✓ | make-skill ✓ |
| q10 | pos | make-skill ✓ | none ✗ |
| q11 | neg | task-pipeline ✓ | task-pipeline ✓ |
| q12 | neg | copywriting ✓ | none ✓ |
| q13 | neg | evidence-docs ✓ | task-pipeline ✓ * |
| q14 | neg | task-pipeline ✓ | task-pipeline ✓ |
| q15 | neg | task-pipeline ✓ | none ✓ |
| q16 | neg | agent-interop ✓ | task-pipeline ✓ |
| q17 | neg | none ✓ | none ✓ |
| q18 | neg | none ✓ | none ✓ |
| q19 | neg | none ✓ | none ✓ |
| q20 | neg | task-pipeline ✓ | task-pipeline ✓ |
| q21 | pos | make-skill ✓ | make-skill ✓ |
| q22 | neg | task-pipeline ✓ | task-pipeline ✓ |

`*` — this probe answered without reading the candidate list on both attempts
(0 tool calls); the answer came from the machine's own installed roster, which
carries the same description. Counted, with that caveat.

### Scenario lines missed, 2026-08-31 (a line not listed here passed)

- **s01 haiku (7/10):** description carried no Russian trigger phrases (the
  bundled auditor flagged it: `DESC_RU`); version sync incomplete — the
  marketplace ENTRY shipped without a `version`; no CI workflow was created and
  neither `claude plugin validate … --strict` run was executed ("would pass" is
  not a run). The s01 sonnet repo passed all ten lines, both `--strict` runs
  quoted, and its generated skill re-audited clean with the bundled auditor
  (one GAP: its own test run's `__pycache__`, not a shipped file).
- **s02, both models (10/11 each):** every planted defect found with
  `file:line` evidence; both missed the same line — the report did not end with
  exactly ONE proposed next action.
- **s03 haiku (1/6):** never loaded the skill and answered from priors —
  claimed the upload is possible without naming the no-network / no-install
  container limits; the only passing line was the vacuous "does not claim the
  pre-built pptx/xlsx skills exist in Claude Code". This is the run to study:
  the skill was installed, advertised, and not consulted.
- **s03 sonnet (4/6):** named no-network / no-install, distinguished the
  surfaces, offered the compatibility-declaration fix; missed "8 skills per
  request" (named 30 MB and the dir-name rule) and never stated that nothing
  syncs between surfaces.
- **s04 haiku (6/8):** flagged the POST but did not name file-read + network as
  the combined risk (partial, counted as a miss); did not recommend the
  checklist steps impossible from the file alone (read every bundled file, run
  scripts sandboxed).
- **s04 sonnet (7/8):** recommended the review checklist but not the concrete
  read-every-file / sandboxed-run steps (partial, counted as a miss).

## Method — 2026-08-31 run (read before comparing numbers)

- **Harness:** the author's machine, via Claude Code's Agent tool
  (general-purpose subagents), one fresh context per probe. Models addressed by
  the tool's `haiku` / `sonnet` aliases; the harness does not expose the exact
  model id to the caller, so the rows above carry the alias and the date.
- **Trigger protocol:** each probe's prompt was the query verbatim, plus an
  instruction to read `/tmp/family-skills.md` — 28 candidate skills
  (name + description) built from the ssheleg family's `SKILL.md` frontmatters —
  plus "which ONE skill would you invoke, or none? answer with the name only."
  A hit on a positive is the answer `make-skill`; a pass on a negative is any
  other answer.
- **One probe per query per model** — not the fired/3 repetition README.md
  prescribes. A single probe cannot express a 0.5 threshold; treat each cell as
  one Bernoulli draw, not a rate.
- **Compliance rule:** a probe that answered without reading the list was
  discarded and re-run once; four such pilots were discarded (two per model).
  Two sonnet probes (q04, q13) skipped the read on both attempts and are
  counted with the `*` caveat above.
- **Stated contamination:** subagents on this machine inherit the operator's
  global `CLAUDE.md`, which carries the family's routing map. That bias pushes
  TOWARD family skills, so the negative results (no false positives in 22
  negative probes across two models) are the strongest finding here, and the
  haiku 22/22 positives are the weakest. A clean-install replication is still
  owed and this file will say so until one lands.
- **Scenario protocol:** query verbatim + fixture path + one sentence stating
  make-skill is installed (the analog of the eval shape's `skills` attachment),
  plus write-fencing (s01 confined to a throwaway `/tmp` workspace; s02–s04
  read-only). Scored per `expected_behavior` line against the agent's report
  AND the artifact it left — the s01 repos were re-audited with the bundled
  auditor and their manifests inspected directly, so a claimed check that was
  not run scores as not run. Partial credit counts as a miss.
- **Fixture self-disclosure caveat:** `retrofit-input.md` and
  `untrusted-skill.md` open with comments naming themselves evaluation
  fixtures, and both models read those comments. For s04 that inflates "says
  no" — the specific findings were still enumerated from the body, and those
  are what the lines score.

## Findings that change what to do next

1. **The predicted risk did not materialize; its inverse did.** This file's
   standing worry was the pushy description stealing turns (q11–q22). Zero
   false positives were observed on either model. The observed failure mode is
   **under-triggering on sonnet**: q01 (create request naming no artifact of
   the standard) and q10 (Russian front-matter limits question) both drew
   "none". If tuning follows, it addresses those two categories — and the fix
   must be re-measured against the negatives before shipping, because widening
   either category is exactly how q12/q19 start firing.
2. **Selection is not consultation.** s03 haiku had the skill installed and
   never opened it, then answered wrong. Trigger rate measures the router;
   scenarios measure whether the knowledge arrives. They diverged by 21
   percentage points on haiku (22/22 vs 1/6 on s03) — keep both in every run.
3. **The near-miss routing landed where the map says it should:** q16 went to
   `agent-interop` on haiku (the MCP carve-out working as written) and the
   release-vocabulary negatives (q11, q14, q20, q22) went to `task-pipeline`.
   In a blind family lineup, `task-pipeline` is the de-facto nearest neighbour
   for near-misses — consistent with the overlap table below, which measures
   descriptions, not routing.

## Known adjacent risk to watch (kept from the pre-run revision, now with data)

This skill's description is long and deliberately pushy. The near-miss negatives
in `triggers.json` (q11–q22) exist because of it — and on 2026-08-31 none of
them fired it on either model, so the risk is watched, not observed.

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
enabled alongside. The overlap is not vocabulary, it is *job*. The 2026-08-31
run probed a family-only lineup, so `version-bump` was not a candidate in the
blind list; q21/q22 still resolved correctly (q21 → make-skill on both models,
q22 → task-pipeline on both). A run with the full installed roster as the
candidate list is the missing measurement.

Re-measure the neighbour table whenever the installed set changes: coexistence
is a property of the set, not of the skill.

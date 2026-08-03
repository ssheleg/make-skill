# Evaluations for make-skill

The canon requires every skill to carry evaluations: at least three behavioral
scenarios plus trigger queries covering the cases where it should NOT fire. This
directory is make-skill's own set — the rule applies to the skill that states it.

There is no built-in runner. Evaluations are data; you run them against an agent
and score the result yourself. That is deliberate: what is being measured is a
model's behavior with the skill installed, which no unit test can stand in for.

## Files

| File | What it holds |
|---|---|
| `triggers.json` | 20 realistic queries, half `should_trigger: true`, half near-misses that share keywords but need something else |
| `scenarios.json` | behavioral evaluations in Anthropic's shape — `skills`, `query`, `files`, `expected_behavior` |
| `fixtures/` | inputs a scenario points at (never named `SKILL.md`: the skills CLI ships every one it finds) |

## Running the trigger set

1. Install make-skill on the agent under test, and nothing else that competes for
   the same requests.
2. Ask each query in a **fresh session**, three times, and record whether the
   skill loaded. Trigger rate = fired / 3.
3. Pass threshold is 0.5 per query. Split the file 60% train / 40% validation,
   fixed across iterations, and tune only on train failures.
4. When tuning the description: too narrow → broaden the scope or context;
   false-firing → state what the skill does NOT do. Never paste keywords from a
   failed query — that overfits; address the category instead.
5. Stop after five iterations and keep the iteration with the best **validation**
   pass rate, which is not always the last one.

The negatives are the point. A description that fires on all ten true queries and
also on "review my pull request" is worse than one that misses two, because it
steals turns from every other skill installed.

## Running the scenarios

Give the agent the `query` (with any `files`) in a fresh session with make-skill
installed, then check each line of `expected_behavior`. Score per line, not per
scenario, so a partial regression is visible.

Run them:

- before any release that touches `SKILL.md` or a reference file;
- on **every model you claim support for** — a skill is an addition to a model,
  and Haiku often needs guidance that Opus finds redundant;
- against the installed skill set you actually use, not the skill alone
  (coexistence: a broad description steals other skills' triggers).

Record the date, model, and score in the release notes when a run changes a
decision. An evaluation nobody has run since the description changed is a claim,
not evidence.

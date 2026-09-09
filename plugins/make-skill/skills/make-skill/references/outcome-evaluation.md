# Outcome evaluation — judging what the skill produced, not what it said

**Load this when:** proving a skill changed real outcomes — before a release,
after a retrofit, or when two versions disagree. The eval loop in
`references/authoring.md` says WHEN to eval (before prose, against a baseline);
this file is the METHOD: what is frozen, what is compared, and what a verdict
is allowed to mean.

## The method, in one table

| Element | Rule |
|---|---|
| Inputs | **frozen** — the same prompts, files and fixtures for every arm; an input that drifts between arms measures the drift, not the skill |
| Arms | **baseline without the skill** and **the current skill version** — two runs, same inputs; a delta with no baseline arm is a number with no zero |
| What is judged | **actual artifacts** — the file written, the diff produced, the page rendered; never the transcript's claim that it did so ("wrote the file" in prose is not the file) |
| Actors | the host supplies the tool names — a CLI, a browser, a subagent are ways to RUN an arm, and **no specific one is mandatory**; an eval hard-wired to one host's tool cannot run anywhere else, which is a hostlock wearing a harness |

## Three judgments, never blended

One eval row answers ONE of these, and the report keeps the axes apart:

- **Routing** — did the skill fire when it should, and stay quiet when it
  should not? Judged on trigger behaviour alone; a perfect output from a skill
  that fired on the wrong prompt is a routing failure with good manners.
- **Output correctness** — is the artifact right? Judged mechanically where
  possible (a validator, a diff against an expected shape, an exit code), by
  rubric where not.
- **Visual judgment** — does the rendered thing read well? A human-or-judge
  call on the artifact's presentation. It never stands in for correctness: a
  beautiful wrong answer fails, an ugly right one passes and files a note.

Blending them is how a skill "improves" on paper: one blended score lets a
routing regression hide behind a correctness win.

## Verdicts: PASS, FAIL, ERROR, NOT_RUN

- **PASS / FAIL** — the judgment ran against the artifact and answered.
- **ERROR** — the process broke: the arm crashed, the fixture was malformed,
  the judge threw. An error is its own status; folding it into FAIL blames the
  skill for the harness, and folding it into PASS is fiction.
- **NOT_RUN** — the tool the case needs is absent on this host (no browser, no
  subagent, no network where one is required). NOT_RUN is never PASS, and it
  names what it would take to run — the same contract the accessibility and
  audit doctrines hold.

An aggregate over rows inherits the weakest honesty: any ERROR or NOT_RUN in a
set means the set is not "all green", however many PASSes surround it.

## Worked examples, one per axis

```
axis: routing      input: "подключи оплату картой"        expect: stripe-billing fires
axis: routing      input: "explain what a webhook is"     expect: no skill fires
axis: correctness  artifact: the generated SKILL.md       check: audit_skill.py exits 0
axis: visual       artifact: the rendered landing hero    check: judge rubric §type-rhythm
```

Four rows, three axes, and no row's verdict can move another's.

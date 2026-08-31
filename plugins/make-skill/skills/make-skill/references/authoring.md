# Authoring craft — writing a body an agent actually follows

**Load this when:** writing or rewriting a `SKILL.md` body, tuning a description
that fires too rarely or too often, deciding how prescriptive to be, bundling
`scripts/`, or building the evaluations that prove the skill works.

Hard limits and field rules are in `references/agent-skills-spec.md`; this file is
the craft on top of them. Sources: Anthropic's
[skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
and [agentskills.io](https://agentskills.io/skill-creation/best-practices).
*Read from both on 2026-08-03.*

## Contents

- Naming — what to call the skill
- Description — the entire triggering budget
- Trigger eval loop — when firing is wrong
- Degrees of freedom — how prescriptive to be
- Body patterns worth copying
- Workflows and feedback loops
- Content guidelines (terminology, time, paths, table of contents)
- Scripts — the rules that separate a script from a liability
- A gate's self-test runs in both directions
- Evaluation and iteration — evals before prose
- Quality checklist

## Naming — what to call the skill

The `name` is a trigger surface, not a filename. Charset rules live in the spec
reference; the naming *style* rules:

- **Gerund form is the recommended default** — `processing-pdfs`,
  `analyzing-spreadsheets`, `writing-documentation`. It states the activity.
- Acceptable: noun phrase (`pdf-processing`), action form (`process-pdfs`).
- **Never**: `helper`, `utils`, `tools`, `documents`, `data`, `files` — a vague
  name buys nothing at selection time and collides with the next skill.
- **Never** `anthropic`/`claude` in the name — reserved, and the Skills API
  rejects the upload (see the spec reference).
- Pick ONE pattern per collection and hold it. Mixed patterns inside a family are
  the reason nobody can guess a sibling skill's name.

## Description — the entire triggering budget

The description is the only thing an agent sees before deciding to load the
skill, and it competes with every other installed skill's description. Rules,
each of which changes whether the skill fires:

- **Say both halves: what it does AND when to use it.** "Extracts text and tables
  from PDFs, fills forms, merges documents. Use when working with PDF files or
  when the user mentions PDFs, forms, or document extraction."
- **Third person, always.** The description is injected into the system prompt;
  first/second person ("I can help you…", "You can use this to…") measurably
  degrades selection. Imperative "Use when …" is fine — it is the trigger clause,
  not a point of view.
- **User intent, not mechanics.** Match the words the user will actually type.
- **Be pushy about context**: name the situations where it applies, including the
  ones where the user never says the domain word ("even if they don't mention
  'CSV'").
- **Say what it is NOT for** when a near-miss skill exists. That sentence is what
  stops trigger theft.
- Concise, a few sentences. Descriptions grow during tuning — re-check the 1024
  cap after every edit.
- Vague descriptions are the failure mode: `Helps with documents`, `Processes
  data`, `Does stuff with files` never win a selection against a specific one.
- Agents skip skills for tasks they can already do in one step. Descriptions earn
  their keep on specialized or multi-step work.

## Trigger eval loop — when firing is wrong

1. Write ~20 realistic queries: 8–10 `should_trigger: true`, 8–10 `false`. The
   valuable negatives are **near-misses** that share keywords but need something
   else.
2. Run each 3× against the agent with the skill installed → trigger rate;
   pass threshold 0.5.
3. Split 60% train / 40% validation, fixed across iterations. Tune only on train
   failures.
4. Too narrow → broaden scope/context. False-firing → add what it does NOT do.
   Never paste keywords from a failed query — that's overfitting; address the
   category instead.
5. ≤5 iterations; pick the iteration with the best **validation** pass rate (not
   necessarily the last).

## Degrees of freedom — how prescriptive to be

Match specificity to how fragile the task is. Getting this backwards is the most
common reason a skill is either ignored or actively harmful.

| Freedom | Write | Use when |
|---|---|---|
| **High** | prose steps, heuristics | many valid approaches, context decides (code review, triage) |
| **Medium** | pseudocode, parameterized snippet | a preferred pattern exists, some variation is fine (report generation) |
| **Low** | one exact command, "do not modify it" | fragile, order-dependent, destructive (migrations, releases) |

The picture: a narrow bridge with cliffs gets guardrails and one exact command;
an open field gets a direction and trust. A low-freedom instruction in an open
field makes the agent worse than it was without the skill.

## Body patterns worth copying

- **Gotchas section** — concrete environment facts that defy assumption. Highest
  value content in most skills. Every correction you make by hand becomes a line.
- **Templates** for output format — agents pattern-match structures better than
  prose. Mark them strict ("ALWAYS use this exact structure") or flexible ("a
  sensible default; use judgement"); an unlabelled template gets both wrong. Long
  ones → `assets/`.
- **Input/output example pairs** where quality depends on style (commit messages,
  reviews). Three examples beat three paragraphs describing them.
- **Checklists** for multi-step workflows with dependencies.
- **Conditional routing** — "creating new content? → workflow A; editing? →
  workflow B" — so the agent never reads the branch it doesn't need.
- **Validation loops** — do work → run validator → fix → repeat until green.
- **Plan-validate-execute** for batch/destructive work: emit a plan file, validate
  it against a source-of-truth file, only then execute. Catches "field does not
  exist" before 50 fields are written, and the plan is cheap to iterate on.
- **Defaults, not menus** — one recommended tool plus a one-line escape hatch.
  "pypdf or pdfplumber or PyMuPDF or pdf2image" is a coin flip, not guidance.
- **Add what the agent lacks**; cut anything it already knows. Test: "would the
  agent get this wrong without this line?" No → delete it.
- **Procedures over answers** — teach the method, not one instance's result.

## Workflows and feedback loops

For anything multi-step, give a checklist the agent can copy into its reply and
tick off, then the steps beneath it:

```
Task progress:
- [ ] Step 1: analyze the form (run scripts/analyze_form.py)
- [ ] Step 2: create the field mapping (edit fields.json)
- [ ] Step 3: validate the mapping (run scripts/validate_fields.py)
- [ ] Step 4: fill the form (run scripts/fill_form.py)
- [ ] Step 5: verify output (run scripts/verify_output.py)
```

Explicit steps are what stop an agent skipping validation. Name the return edge:
"if verification fails, return to step 2". The same shape works with no code at
all — the "validator" can be a style guide the agent re-reads.

If a workflow grows past a screen, move it into its own file and route to it from
the body.

## Content guidelines

- **No time-sensitive statements.** "Before August, use the old API" is wrong the
  moment it ships. Put superseded material under an `## Old patterns` heading (a
  collapsed `<details>` block works) and keep the current path unqualified. A
  DATED PROVENANCE line is the exception and is encouraged: "*read from the spec
  on 2026-08-03*" tells the next reader what to re-verify.
- **One term per concept.** Pick "field" or "box", "extract" or "pull", and never
  alternate — synonym drift makes an agent think two things are being described.
- **Forward slashes in every path**, including on Windows: `scripts/helper.py`,
  never `scripts\helper.py`. Backslash paths break on Unix and in JSON.
- **Reference files over 100 lines get a `## Contents` list at the top.** Agents
  preview long files with `head`; without a table of contents they act on the
  first 100 lines and never learn the rest exists.
- **One level deep from `SKILL.md`.** A file reachable only through another file
  gets partially read or missed entirely. Every reference links from the body.
- **English prose is a budget rule before a style one** (the house rule in
  `SKILL.md` states which four literals stay Cyrillic). The measured cost:
  Russian encodes at 1.9–2.3 chars/token against English's 5.0 (`cl100k`), and
  rewriting the eight ssheleg routers into English cut them **3408 → 1885
  tokens** with no loss of meaning.

## Scripts — the rules that separate a script from a liability

A bundled script is more reliable than generated code, costs no context (only its
output enters the window), and is consistent across runs. It also fails silently
if written carelessly.

- **Solve, don't defer.** Handle the error inside the script — missing file,
  permission denied — and print what you did. `return open(path).read()` and
  "let the agent figure it out" turns one failure into a debugging session.
- **No voodoo constants.** Every timeout, retry count and threshold carries a
  comment justifying it. If you don't know why it's 47, the agent has no chance.
- **State the intent explicitly**: "Run `scripts/analyze_form.py` to extract
  fields" (execute) vs "See `scripts/analyze_form.py` for the extraction
  algorithm" (read). Ambiguity here gets a script pasted into context, which is
  exactly the cost the script existed to avoid.
- **Declare dependencies and verify they exist** on the surface you target —
  "install required package: `pip install pypdf`", or better, no third-party
  dependency at all. Never write "use the pdf library". The Claude API surface
  cannot install anything at runtime (`references/surfaces.md`).
- **Verbose, specific error messages**: "Field 'signature_date' not found.
  Available: customer_name, order_total, signature_date_signed" is actionable;
  "invalid field" is not.
- **Vision is available**: rendering an input to images and letting the agent look
  at it beats describing a layout in prose.

Worked example: this skill's own `scripts/audit_skill.py`. It is stdlib-only so
it runs wherever the skill landed, prints `file:line` evidence rather than
verdicts, handles its own missing-file and bad-frontmatter cases, and its first
run flagged a false positive on the very document that teaches the anti-pattern —
which is why it now ignores quoted spans. Hooks, subagents and commands that wrap
it, plus the fallbacks they owe, are in `references/host-capabilities.md`.

## A gate's self-test runs in both directions

*"A validator that can't fail is decoration"* is half the rule. The planted defect
proves the gate **can** fire. Nothing in it proves the gate fires only where it
should — and a gate that flags correct code is switched off within a day, taking
the real check with it. **A false positive does not arrive as a bug report. It
arrives as an argument about your gate**, from someone whose code was fine.

So a self-test carries two kinds of case:

| Direction | The case | What its absence costs |
|---|---|---|
| **Must catch** | the planted defect, watched failing | a check that cannot fail, green forever |
| **Must NOT flag** | the legal spelling, the empty input, the near-miss that only resembles the defect | a check that is correct and unusable, removed by the first person it wrongly blocks |

**The counter-shapes are also where a gate's design gets decided, not just
verified.** A pattern that reads *"no key may start with a mounted namespace"*
finds five hits and all five are correct — they pass absolute keys to a translator
that prefixes nothing. Written as a pattern the gate is wrong; written as a parser
that binds each translator variable to its namespace, it is right. The counter-case
is what tells the two apart, and only running it reveals which one you built.

Two shapes recur and both belong in every gate's fixtures:

- **The input that cannot be resolved.** A resolver returning nothing must be a
  loud failure, never a silent skip — *a check that cannot run is not a check that
  passed*. A slug resolver anchored on `github.com` returned nothing for npm's
  `github:owner/repo` shorthand, so the check printed `skip` and reported success
  for work it never did.
- **The word inside another word.** Any matcher over prose needs the near-miss:
  `lease` inside *please*, `аудит` inside *аудитория*, `seo` inside *Seoul*. These
  are found by running the gate over a real corpus, not by reading it.

**Count the cases, do not restate the count.** A summary line saying *"5 cases"*
while thirteen run is the same class of defect the gate exists to prevent, in the
gate's own output.

## Evaluation and iteration — evals before prose

**Build the evaluations before writing extensive documentation.** Otherwise the
skill documents imagined problems.

1. **Identify gaps** — run the agent on representative tasks with NO skill.
   Record the specific failures.
2. **Create evaluations** — at least three scenarios covering those gaps.
3. **Baseline** — measure performance without the skill.
4. **Write the minimum** that fixes the gaps.
5. **Iterate** — re-run, compare to baseline, refine.

Evaluation record — there is no built-in runner, so keep them in the repo as
data and run them yourself. House layout: `test/evals/triggers.json` (~20
queries, half near-miss negatives) and `test/evals/scenarios.json` (≥3, the
shape below), with any input under `test/evals/fixtures/` — **never named
`SKILL.md`**, which would ship as a real skill:

```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Reads the PDF with an appropriate library or CLI tool",
    "Extracts text from every page without skipping any",
    "Saves the result to output.txt in readable form"
  ]
}
```

**Test on every model you ship for.** A skill is an addition to a model, so its
effect varies by model: Haiku may need more guidance, Opus may be slowed by
over-explanation. Run the evals on Haiku, Sonnet and Opus if all three are in
scope.

**The two-agent loop.** Author with one instance (call it A), test with a fresh
instance that has the skill installed (B), and bring B's observed failures back to
A — "B forgot to filter test accounts even though the skill says to; is the rule
prominent enough?". Refine against observed behavior, never against assumptions.
Watch for: files read in an unexpected order (structure is wrong), references
never followed (links not prominent), the same file read every time (it belongs in
the body), a bundled file never read at all (delete it).

Approval gates for a skill other people will install — triggering accuracy,
isolation, coexistence with the existing skill set, instruction following, output
quality — are in `references/enterprise.md`.

## Quality checklist

- [ ] Description gives what AND when, in third person, with concrete triggers
- [ ] Name follows one pattern, is not vague, contains no reserved word
- [ ] Body under 500 lines / 5000 tokens; detail in one-level-deep files
- [ ] Every reference has a stated load condition; >100-line ones have a TOC
- [ ] Degrees of freedom match task fragility
- [ ] No time-sensitive statements outside an "Old patterns" section
- [ ] Consistent terminology; forward slashes everywhere
- [ ] Examples concrete, not abstract; a default given instead of a menu
- [ ] Scripts handle their own errors, document constants, declare packages
- [ ] Execute-vs-read intent stated for every bundled script
- [ ] Validation/feedback loop for anything quality-critical or destructive
- [ ] ≥3 evaluations exist, baselined without the skill, run on every target model

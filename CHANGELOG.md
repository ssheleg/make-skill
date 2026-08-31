# Changelog

## v0.25.3 — the runner we said did not exist, and the date a claim about someone else now carries

- **B-122 closed: `references/authoring.md` told authors for four weeks that
  there was no built-in eval runner, and prescribed a home-rolled suite on that
  basis.** `claude plugin eval` had shipped. The section now names it, its case
  format (`evals/<case>/case.yaml`, or `prompt.md` beside `graders/*.md`), and
  the fact that `--ablation with-without` performs steps 3 and 5 of the very
  procedure the paragraph prescribes by hand — plus the detail that it publishes
  its HTML report to claude.ai unless `--no-publish` is passed, which is the
  wrong default for an unreleased skill. **The replacement is a measurement, not
  a correction of one absence into another**: on 2026-08-31, Claude Code 2.1.236,
  every path (`eval`, `eval init`, `eval init --bare`, `eval <target>`) prints
  ``plugin eval` is currently in early access`, writes nothing and exits 1, with
  no settings key, environment variable or feature flag turning it on. That is
  why `test/evals/` remains what runs here, and the paragraph says which day it
  should be migrated. Two derived statements went with it: `distribution.md`'s
  layout comment called the suite *"run by a human"*, and `retrofit.md`'s item 8
  asked only that evaluations *exist* — the state MSK-01 had just spent a whole
  run closing.
- **The class, not the sentence: `THIRD_PARTY_CLAIMS` in `test/validate.py`.**
  A load-bearing claim about someone else's tool is registered beside the command
  that re-checks it, and the guard fails unless the claim, that command and an
  ISO date still sit within eight lines of each other — and fails equally when a
  registered claim has been deleted from the doctrine but left in the registry,
  so the registry cannot outlive what it describes. The skill's own rule *"No
  time-sensitive statements"* sits 100 lines above the sentence that broke it and
  nothing enforced it; this is the enforcement.
- **A generic detector was built first, measured, and rejected with the number.**
  Over the shipped doctrine a pattern for absence-claims flagged **10 lines, of
  which roughly half are legitimate** — the fallback rows of
  `host-capabilities.md` ("on any other host there are no subagents") are made of
  that sentence shape on purpose. A guard with a ~50% false-positive rate is the
  over-defense that gets switched off, so the explicit registry replaced it; the
  reasoning is recorded in the code beside the table rather than lost.
- **The three plants are in CI, and the group count still computes.** Added as
  cases to the existing *claims, budgets and runnable commands* step rather than
  as a new step, so `grep -c 'name: Negative self-test'` stays at **9** and
  `CONTRIBUTING.md`'s *"9 negative self-test groups"* — a claim this validator
  compares against the workflow — remains true. Each case asserts its own
  expected message. The first local run of the guard **passed its plants for the
  wrong reason**: the claim wraps a line break and the check was line-anchored,
  so all three plants tripped the registry-rot branch instead of their own. The
  matcher is whitespace-tolerant now, and every plant in the block asserts it
  changed something before the validator is asked anything.

## v0.25.2 — the evals have been run, and the discovery check runs somewhere

- **MSK-01 closed: the evaluation suite was executed against two models, and the
  numbers live in `test/evals/RESULTS.md` as a dated run (2026-08-31), not a
  claim.** All 22 trigger queries probed blind per model — haiku 22/22, sonnet
  20/22 (q01 and q10 answered "none": under-triggering on positives, ZERO false
  positives on the near-miss negatives across both models) — and all four
  behavioural scenarios executed and scored per `expected_behavior` line (sonnet
  31/35, haiku 24/35; the s01 repositories were re-audited with the bundled
  auditor rather than trusted from the agent's report). The Method section
  states the harness and its limits: one probe per query instead of the
  README's fired/3, Agent-tool subagents on the author's machine whose global
  config carries the family routing map (a bias that makes the clean negatives
  the strongest result), model aliases rather than exact ids, and two probes
  counted with a stated non-compliance caveat. Headline finding: the standing
  worry (turn-stealing) did not materialize; the observed failure is sonnet
  under-triggering on two positive categories, and s03-haiku answered a
  surfaces question without consulting the installed skill — selection and
  consultation measured apart, on purpose.
- **MSK-03 closed: the discovery check the body demands now runs in CI.**
  SKILL.md's stray-SKILL.md gotcha ends "verify with the skills CLI's `--list`"
  — and nothing ran it anywhere: the operator machine's hygiene guard refuses
  the bare skills CLI on family members by design, and CI never asked. The new
  `skills-cli-discovery` job in `validate.yml` runs the listing against
  `ssheleg/make-skill` and asserts it serves exactly ONE skill, named
  make-skill, with ANSI stripped before asserting. Its own job, like
  `claude-plugin-validate`, so a registry outage cannot mask an
  offline-validator failure; it reads the repository's default branch, so the
  post-merge push run and the release's `workflow_call` on the tag assert the
  published tree.
- **MSK-04 closed: body headroom restored by displacement — the words moved,
  none were lost.** The Cyrillic budget measurement (1.9–2.3 chars/token,
  3408→1885) moved to `authoring.md` → *Content guidelines*; the six skeleton
  filenames moved into `distribution.md`'s layout tree; the five verified facts
  and the machine-refresh command sequence are now referenced at their single
  home in `distribution.md`'s checklists instead of being restated; the
  long-file rule already lived in `authoring.md` and the body now points there.
  Re-measured with the bundled auditor: body ~4742/4750 tokens (8 spare) →
  ~4677/4750 (73 spare), after also paying for the next bullet. The
  description is untouched at 965/970 — its headroom is spent only on trigger
  changes, and this release makes none.
- **XF-10: the MCP/A2A carve-out now runs both directions at the layer an agent
  reads first.** The References-table rows for `mcp.md` and `a2a.md` carry "the
  protocol wire itself → `agent-interop` (agent-stack)" — the two reference
  files' own headers already said it, and now the router-level table says it
  too, so a reader deciding what to load learns the boundary before opening
  either file.
- Also: `test/evals/README.md`'s file table said "20 realistic queries" over a
  `triggers.json` holding 22 — the same drift class as MSK-02, in a wording no
  guard could parse. Reworded to the checkable "22 trigger queries" form, which
  puts the sentence under `test/validate.py`'s counted-claims sweep instead of
  under anyone's memory. `SKILL-CARD.md`'s evaluation status and posture
  sections now describe the executed run and the replication still owed,
  instead of "never executed".

## v0.25.1 — the rule keeps its default, and the family's exception is written down

- **The same-name command rule now carries its recorded exception** (operator
  decision, 2026-08-30: no renames anywhere in the family). The default in
  `references/host-capabilities.md` is unchanged — never name a command after a
  skill in the same plugin — and the one recorded exception is enumerated beside
  it: the ssheleg family ships same-named commands deliberately (`task-pipeline`,
  `project-audit`, `seo-aeo-audit`, `sheleg-design`, `agent-sync`, and
  `super-ux`'s `vision` / `ux-foundation` / `ux-flows` / `ux-audit`), with the
  cost stated rather than waived: the skill wins the trigger, and each command
  stays an always-on token cost that may be unreachable in the picker.
  `retrofit.md` item 14 and the Cursor rule teach the auditor the same path, so
  family audits report ASY-02 / SEO-02 / TPA-02 / SHD-06 / SUX-03 as
  *deliberate, recorded — no change needed* instead of open gaps. A collision
  NOT on a dated, recorded exception list is still the gap the rule names.
- **A hand-typed eval count drifted, exactly as this skill's own gotcha predicts**
  (MSK-02). `test/evals/RESULTS.md` said "20 queries" and `SKILL-CARD.md` said
  "20 trigger queries" over a `triggers.json` holding 22. Both corrected — and
  both statements are now compared, not typed: `test/evals_validate.py` parses
  RESULTS.md's stated counts against the artifacts and refuses a claim-free
  RESULTS.md rather than passing vacuously, with negative self-tests planting an
  off-by-one count and a claim-free file; `test/validate.py`'s counted-claims
  sweep gains the `N trigger queries` / `N behavioural scenarios` patterns for
  every other document. Both guards were watched failing against the real
  20-vs-22 defect before the numbers were corrected.
- The `SKILL.md` body is untouched on purpose: at ~4742/5000 tokens it has 8
  tokens of headroom, so the whole amendment lives in the references.

## v0.25.0 — the installer refuses the shadow it documents, loudly

- **The family audit of 2026-08-29 reproduced the shadow live:** a bare
  `npx @ssheleg/telegram-dev` created three plain copies in `~/.claude/skills/` while the
  telegram-dev plugin was enabled. Every member's bin installer had the same hole, and every
  member's CI tested only a fresh `HOME`, so the plugin-present case had never run anywhere.
  This is the standards repository, so the canon lands here first and its own installer is
  the reference implementation.
- **This repository's own check was the fail-open class, and the new canon names it.** Both
  installers detected the plugin by the `~/.claude/plugins/marketplaces/make-skill`
  directory alone — which under-reports (a `directory`-sourced marketplace has no dir
  there; plugin names differ from marketplace names) — and the refusal exited **0**, which
  reads as success to every script above it. `distribution.md` gains "The installer must
  refuse the shadow it documents": detect from the TARGET home's
  `installed_plugins.json` (keys are `<name>@<marketplace>`), refuse with the remedy and a
  non-zero exit, offer `--force` as the recorded deliberate choice, fail open on a missing
  or corrupt JSON, and gate only the `~/.claude` write — no other agent has plugins.
- **`bin/make-skill.js` and `install.sh` implement it:** exit `3` on refusal, the remedy
  names the spec read from the JSON (`claude plugin update make-skill@<marketplace>`) plus
  the family launcher, `--force` overrides, absence/corruption of the JSON installs as
  before, and the marketplaces-dir read is kept as the fallback signal. The last line of a
  successful install now says how the next version arrives (the v0.24.0 canon, applied to
  this repo's own CLI).
- **`test/installer_test.js` joins `npm test` and CI** — 11 cases against throwaway HOMEs:
  fresh / rerun-skip / `--force` / unknown-arg, plugin-present refusal (exit code, remedy
  text, nothing written), a differently-named marketplace in the spec, corrupt JSON failing
  open, no false refusal on other plugins or a `make-skill-extra` prefix-collider, the
  marketplaces-dir fallback, and the same matrix for `install.sh`. Watched failing before
  trusted: **6 of 11 red** against the pre-fix installers (`git stash` the two, run, pop).
  The suite follows the house residue rule — a failing case keeps its HOME, and the run
  ends by saying what it left.

## v0.24.0 — the plugin surface as it is now, and how updates reach a machine

- **Four plugin features that landed after this skill last read the docs.** Re-read
  2026-08-28 against Claude Code 2.1.236; the previous pass was 2026-07-30 against 2.1.212.
  `archive` sources install a zip over HTTPS with no git and no npm (2.1.224); `command`
  sources let a local command print the plugin directory (2.1.229) and are the one class an
  organisation can switch off wholesale with `disableCommandPluginSources`; entry-level
  `headersHelper` mints registry headers and **requires `strict: false`** (2.1.238); a
  `skills` path of `"."` scans the plugin root instead of `skills/` (2.1.221). Bare-name
  sources under `metadata.pluginRoot` are in too (2.1.239).
- The `headersHelper` contract is written out because every clause of it is a way to fail
  silently — ten seconds, 500 ASCII characters, stdout JSON — and because Claude Code
  **strips every environment variable whose name contains `TOKEN`, `SECRET`, `KEY` or
  `AUTH`** before running it. A helper that reads its credential from one of those is handed
  nothing, and the failure surfaces as a permissions error at the registry.
- **`distribution.md` gains "How updates reach the machine — decide it, then SAY it".** An
  installer that never mentions updates has still chosen a model, and the model is *never*.
  Claude Code carries a per-marketplace `autoUpdate` flag in `known_marketplaces.json` that
  is **not in the documented settings surface**; `/plugin` writes it and third-party
  installers write it directly. Measured on one machine 2026-08-28: of 20 marketplaces, the
  2 installed by `vercel-labs/plugins` carry it and 18 do not, because
  `claude plugin marketplace add` never sets it.
- The section states the trap rather than a preference: for packs that **compose**,
  per-marketplace auto-update moves each on its own clock and produces a combination nobody
  tested — the same reason a family launcher refuses a per-member argument. For packs that
  stand alone it is the better answer. Either way the installer's last line says how the
  next version arrives, because "Installed" is not a complete sentence.

## v0.23.5 — the channel that sends the installs, on npm too

- The `skills.sh` badge and the canonical `homepage` reached GitHub in the previous cycle and stopped
  there: npm serves the README and the metadata from the last **publish**, so the package
  page still showed a badge-less README and a homepage pointing at GitHub.
  This release carries both across.
- No behaviour changes. Cut because a change that lands on `main` and never publishes is a
  change the package's own readers cannot see.

## v0.23.4 — the shared seam is explicit

Both copied public-contract validators now declare `diverges: none`, completing
the family drift header they introduced in v0.23.3.

## v0.23.3 — the copied public-contract guards name their canon

Both portable validators now carry explicit shared-mechanism identifiers. The
umbrella can therefore enforce byte-level family drift without guessing whether
nine similar files are intentionally aligned.

## v0.23.2 — the standard is applied to the skill that states it

Every family repository can now run the same auditor from a commit-pinned CI job,
and release inherits that gate through the existing callable workflow. The eval
data has a portable validator with an in-memory negative self-test, the README
opens with one install and one request, and the generated social preview is
checked in. Existing model results remain explicitly absent.

## v0.23.1 — the residue scan stops answering for other runs

`test/residue.py` now tags every workspace with the process group that made it, and the
gate-wide scan reads only that tag. Scanning the shared `$TMPDIR` by prefix reported two
things that are not this run's leak: another session's trees — 37,301 entries under the
shared directory on 2026-08-24 turned a green suite red — and a tree a FAILING case in an
earlier run kept ON PURPOSE as its evidence, which poisoned every run after it. The split is
a pure function with fixtures for both directions, and what it excludes is printed rather
than dropped in silence.


## v0.23.0 — 2026-08-20 — the ledger said unshipped over the release commit

The newest ledger section read *"Unshipped … no release cut"* and *"npm is still 0.21.0"*
while HEAD **was** the v0.22.0 release commit and the registry served 0.22.0. Re-run against
the artifact rather than re-graded, and `check_the_ledger_matches_what_shipped` now refuses
the state: four plants, each watched at exit 1. It refused the row documenting itself once,
because only `*"…"*` counts as a citation to it — which is now stated where the pattern
lives rather than learned by whoever trips on it next.

**The pile figure was a sample presented as a state.** MS-01 recorded *"1888 abandoned
directories, 47.3 MB … unchanged by anything this repository ran after the fix"*. Recounted:
**2688 directories, 83.6 MB** — and split at the fix's own commit time, which is the part
that matters: **0** `planted/` and **0** `repo/` trees created after it, against **784 of
2592** plant-guard trees. So the scoped claim holds, now by timestamp rather than by two
samples taken a minute apart, and the total carries its measurement date.

**The referral is discharged rather than claimed.** MS-01 left three sibling repositories
shipping the identical leaking fixture. All three fixed it while this ran — the umbrella at
`b371301`, `seo-aeo-audit` at `c859cba`, `agent-stack` porting `test/residue.py` from here —
and `grep -c 'tempfile.mkdtemp()'` is now 0 in all four. Recorded as observed, not as work
this release did.

**Left open, and it is the honest kind.** `residue.report()` sees only what `workspace()`
handed out, so a re-introduced bare `mkdtemp` prints *left nothing* over a live leak. That
was watched happening in `agent-stack` before its port. The closing mechanism exists there;
REQ-025 sits at `never` until it comes back here.


## v0.22.0 — the gate left 47 MB in $TMPDIR and never said what it left

**Two suites copied the tree to plant defects into it and never removed the copy.** The
conformance audit named one; the sweep found the other, and it was the larger half by two
orders of magnitude. Measured on this machine at the time of the fix: **1904 abandoned
mkdtemp roots, 47.3 MB** — 60 planted skill dirs and 36 repo copytrees unambiguously this
repository's, and 1808 plant-guard trees ambiguous, because four family repos ship the
byte-identical fixture at the same line and nothing in the content distinguishes them.

### `test/residue.py`

A shared ledger in this repo's `plant_guard.py` idiom: `workspace()` hands out a
`make-skill-test-` prefixed mkdtemp, `open_case` / `close_case` bind each tree to a case,
and `report()` — wired to `atexit`, so no exit path skips it — removes what may go, keeps
what a failure needs, and **prints one line either way**. A clean run says
`residue: this run left nothing — N temp tree(s) created, N removed`, because the
requirement is that completion *records* residue, not merely that there is none. A leak is
then visible the first time the line changes.

**The failure path keeps its tree, by decision and stated in three places.** A planted
defect here is debugged by reading the copy the plant landed in, and a cleanup that runs
only on the pass path removes the evidence exactly when you want it. The report names the
kept path, its owning case, and the `rm -rf` that ends it — a kept tree with no stated
remedy is a leak with better manners. A tree that refuses to delete is counted as **kept**,
never as removed: the report does not claim a teardown it did not achieve.

`test/residue_test.py` joins the gate with 8 cases, including the one that matters — stash
the two fixes and it exits 1 naming both suites, then prints
`residue: 2 of 2 temp tree(s) KEPT` with both paths. The failure path demonstrating itself.

### Not swept

The 1904 pre-existing directories were **left in place** and reported. Ownership of 1808
of them cannot be established from their contents, and deleting state you cannot prove is
yours is the one thing this kind of cleanup must not do.

## v0.21.0 — a gate's self-test runs in both directions

*"A validator that can't fail is decoration"* has been the rule here since the standard was
written. It is **half** the rule, and the missing half is the expensive one.

The planted defect proves a gate CAN fire. Nothing in it proves the gate fires only where it
should — and a gate that flags correct code is switched off within a day, taking the real check
with it. **A false positive does not arrive as a bug report. It arrives as an argument about
your gate**, from someone whose code was fine.

`references/authoring.md` gains *A gate's self-test runs in both directions*: the two kinds of
case, what each one's absence costs, and the point that counter-shapes **decide** a gate's
design rather than merely verifying it — a pattern that finds five hits and is wrong about all
five is a parser you have not written yet.

Two recurring shapes are named because both have shipped:

- **The input that cannot be resolved** must fail loudly, never skip — *a check that cannot run
  is not a check that passed*. A slug resolver anchored on `github.com` returned nothing for
  npm's `github:owner/repo` shorthand, so its check printed `skip` and reported success for work
  it never did.
- **The word inside another word** — `lease` in *please*, `аудит` in *аудитория*, `seo` in
  *Seoul*. Found by running the gate over a real corpus, never by reading it.

And: **count the cases, do not restate the count.** A summary saying *"5 cases"* while thirteen
run is the defect the gate exists to prevent, in the gate's own output.

**The doctrine went to the reference rather than the body, and the body's own gate decided
that.** `SKILL.md` measured 4738 of a 4750 working limit — twelve tokens of headroom — so every
draft that stated the rule inline failed the budget check. `authoring.md` is linked from
`SKILL.md` twice, so the rule is reachable without spending a body it does not have. Closes #5.

## v0.20.0 — the checker said 180 where the file said 1392

**Both checkers dropped the continuation lines of a plain multi-line YAML
description**, so a description whose real length was **1392 characters was
measured at 180** and passed the 1024 spec cap, the 970 working limit and every
`/skill-audit` this family issues. The standard-keeper handed a clean bill to a
skill the Skills API rejects on upload, and `make-skill`'s own gate could not
catch it either. A plain scalar may continue on indented lines and YAML folds
them into one value with a space; `parse_frontmatter` discarded them, in both
`scripts/audit_skill.py` and `test/validate.py`, byte for byte the same defect.

**`allowed-tools: [Read, Write]` was read as the string `"[Read, Write]"`.**
`TOOLS_TYPE` asks whether the value is a `str` and got yes, so the check written
for exactly that form never fired — on the most common way authors write a tool
list, and the one portability defect that costs a skill its tool grant on every
host but Claude Code. A flow sequence now parses to a list, and the check fires.

**The scalar is kept raw and finished at the end**, because a quoted scalar
spanning lines carries its closing quote on the last one: unquoting the first
line strips nothing and buries the quote in the middle of the folded value.

**`--house` now applies the body's half of the 5% rule.** The canon states the
headroom as one sentence for both fields, and this script applied it to the
description only — so a body at 4999 tokens got `0 GAP` here and was refused by
this repo's own validator. Two verdicts on one rule, and the permissive one was
the one users got. `BODY_HEADROOM` is the new gap id; the `--house` help text
and the module docstring said neither this nor `DESC_HEADROOM`, and now say both.

**The guard against the two checkers drifting compared one of twelve rules.**
It now compares all nine shared numeric limits by name plus both front-matter key
sets, and a constant that exists on one side only is a failure rather than a
silently skipped row — which is exactly how the missing 4750 shipped for four
releases underneath it. Three limits that were literals at their use sites
(`NAME_MAX`, `DESC_MAX`, `COMPAT_MAX`) are named, because a number with no name
has no single home and cannot be compared against a second implementation.

**`test/checker_parity_test.py`, 14 cases, joins `npm test`** — locally, not only
in CI, since the checker it guards runs locally. Watched failing against the
pre-fix code: **9 of 14 red**. It plants each defect and requires the checker to
say so, rather than asserting that a correct file passes: a false negative in a
checker is worse than no checker, because it is a green that gets quoted.

**No shipped skill changes verdict.** All 24 in the family re-audited before and
after: identical, and the one apparent difference was a `__pycache__` this run
had just created.

Found by the nine-repository audit of 2026-08-16 (umbrella `B-63`).

## v0.19.1 — 2026-08-16

**This gate can now see an invariant it breaks one repository away.** The family umbrella
routes work by matching a prompt against a table in `lib/triggers.js`, and every trigger
there must be a word this skill's own `description` advertises. Nothing here knew that
table existed. On 2026-08-16 `sheleg-design` 1.37.0 shipped green having dropped a phrase
that was still a live trigger, the umbrella found out minutes after the tag, and it cost a
patch release — because the member releases FIRST and the umbrella re-pins after.

`test/validate.py` now asks the umbrella's own checker (`test/advertised_check.js`), which
reads the module the hook itself calls. **No copy of the table lives here**, so there is
nothing to drift. With no umbrella above this checkout — a standalone clone, and CI — it
discloses rather than passing, because a check that cannot look must never read as one
that looked.

Watched refusing a real drop before shipping: every one of the seven members carrying
routed triggers had one of its own advertised phrases removed and every one of them failed
its own gate.

## v0.19.0 — 2026-08-16

### Added

- **The validator failure mode planting does not catch**, in
  `references/distribution.md` → *The house validator*. This canon already said a
  validator nobody has watched fail is decoration — the right rule for a check that
  asserts the *wrong* thing. It does not cover a check that **never runs**, which is
  invisible to planting, because nothing happening looks exactly like a clean suite.

  Both shipped in `sheleg-design` on 2026-08-16, inside the same check and within an
  hour: a lookup returning `None` on a case mismatch (`NUMBER_WORDS` keyed lowercase,
  the document capitalising) short-circuited the guard, and the pattern policing a
  stale header had been anchored on a line wrap the file did not have. The suite
  printed OK both times, and **the check-count rose by four while the new check
  covered nothing** — so the counter is not evidence either. The procedure gains a
  second half: plant the defect, then read the failure you expected rather than the
  summary, and if the suite still passes, suspect your check before the artifact.

### Note

The first draft of this entry put the rule in `SKILL.md` and pushed the body from
under the 4750-token working limit to 4855. The repo's own validator refused it and
said what to do — move a section to `references/` before adding one. The rule went to
`references/` instead, where the house-validator guidance already lives, and `SKILL.md`
is byte-identical to v0.18.1. A canon that will not follow its own budget rule under
mild inconvenience is a canon nobody else will follow either.

## v0.18.1 — 2026-08-14

A red `validate` could not stop a publish anywhere in this family, and one member
proved it: on 2026-08-12 `sheleg-dev` tagged v0.4.1 while its own validate run for that
exact tag **failed**, and npm served 0.4.1 four minutes later.

### Fixed

- **The release now runs the whole validate suite before anything is published.**
  `validate.yml` gained a `workflow_call` trigger and `release.yml` calls it with
  `needs: validate` — the release runs *after* the real suite rather than beside a copy
  of it. **Not one plant is duplicated:** each still has exactly one home.
- **A guard keeps the connection there.** It fails when the trigger, the call, or the
  `needs` goes missing — calling the suite without depending on it lets the jobs run in
  parallel, which looks gated and is not. Watched failing against the planted removal.

Proven end to end on `sheleg-dev` v0.4.3 before it reached here: the release run shows
`validate / validate` completing first, then `release`, then `publish`.

## v0.18.0 — 2026-08-14

This skill had been describing somebody else's protocol, and the description had gone
stale without anything on the page saying so.

### Changed

- **The protocol layer moves out; the skill-author delta stays.** `references/mcp.md` and
  `references/a2a.md` now carry only what changes *because the thing being written is a
  skill* — skill versus server, declaring the dependency in `compatibility`, tool-name
  discovery per host, the untrusted-output rule, interactive auth as a human step, and the
  two unrelated meanings of the word "skill". The wire itself — layers, methods,
  lifecycles, transports, cards, task states — now lives in **one** place: the
  `agent-interop` skill in `ssheleg/agent-stack`, where every reference carries a
  `**Spec pinned:** … · read <date>` line that a validator enforces.

- **`references/mcp.md` no longer describes a protocol MCP is not.** It was pinned to spec
  revision `2025-11-25` and stated *"MCP is a **stateful** protocol"* with an `initialize`
  → `notifications/initialized` handshake. `modelcontextprotocol.io/specification/latest`
  now serves revision `2026-07-28`, whose own summary reads *"Stateless, self-contained
  requests. Per-request capability negotiation."* The file's header said it had been read
  on 2026-07-28 while its pin stayed on the older revision — which is exactly the failure
  mode a single stamped home exists to prevent. It also documented `sampling` and `roots`
  as current client primitives; both are now deprecated with a published removal window.

### Removed

- **`references/mcp-ship.md`** — relocated to `agent-interop`. Mounting a server, the
  FastMCP double-path 404, the 404/307/401 bisect, `server.json` and the registry read
  identically whether or not the reader is writing a skill, which is the test for which
  side of the boundary a file belongs on. Nothing was lost in the move: the Ed25519 DNS
  and HTTP namespace challenge and the two automated-publish rules were folded into
  `agent-interop/references/registry.md`, and the operational half became
  `agent-interop/references/mcp-ship.md`. The reference count drops 11 → 10, and the
  installer test, the README table, `SKILL-CARD.md` and `retrofit.md` follow.

## v0.17.1 — 2026-08-13

Eight negative self-tests were healthy and had no way to prove it — and the first attempt
to give them one proved the point by being wrong.

### Added

- **`test/plant_guard.py`** — one implementation of *did the plant actually land*, called
  by every plant as `snap` before and `verify` after. It compares **content and mode**,
  ignores `.git` churn, refuses when handed no tree or no snapshot, and keeps its manifest
  outside the tree it measures. `test/plant_guard_test.py` covers nine cases, including
  the one that named it.

### Fixed

- **Every file-editing plant now proves it landed**, `PLANT DID NOT LAND: <step>`. A plant
  that edits nothing leaves the validator honestly passing, and the step then reports a
  guard it never disarmed as broken — standing instruction #6's corollary, and what kept
  `sheleg-dev`'s `main` red for two days over a guard that worked.
- **The `hookexec` case was reported broken and was not.** Its plant drops a hook
  script's executable bit, and the first guard compared bytes only, so it announced
  `PLANT DID NOT LAND` about a plant that had landed. CI caught it; the local run had
  truncated its output before that case. The helper exists because five hand-written
  variants of this guard produced five different bugs, that one included.

Verified by running every plant: 40 cases across eight steps, all green — `name`, `desc`,
`key`, `ref`, `trigger`, `contrib`, `reserved`, `xmltag`, `person`, `toc`, `tokens`,
`tplxml`, four eval cases, five host-capability cases including `hookexec`, and the rest.


## v0.17.0

Following `task-pipeline` v1.53.0, which renamed the artifact root's default from
`docs/superpowers/` to `docs/evidence/` and made the root resolvable (`paths.artifacts`
in `pipeline.json`, else an existing `docs/evidence/`, else an existing
`docs/superpowers/` — **the legacy name stays supported and no run warns about it**).

Shipped surfaces name the new default now, which is why this is a minor rather than a
patch. This project's own records moved with the directory and were not rewritten: a
brief describes where things were when it was written.

## v0.16.0

### Changed

- **The installer now offers the family's routing block** (closing B-06 in the
  umbrella). Until now only `super-ux` delegated: install this skill on its own
  and no router was written at all, so an agent had the skill and no rule saying
  when to reach for it. The bundle installer wrote all eight, which is why
  nothing looked broken — the gap only opened for someone installing one member.

  Delegated to `npx sshlg-skills routers --member make-skill` rather than
  reimplemented, for three reasons:

  - The block describes what the machine actually has. A lone member rendering
    the whole thing would print a table for routers nobody installed.
  - `--member` scopes the write to this skill's own section. Verified by damaging
    two sections of a real block and running this installer: its own was
    repaired, the other left exactly as it was.
  - The launcher is the only writer that copies the operator's global instruction
    file before touching it. That file has no version control behind it.

  `--no-install` keeps it from silently downloading a package nobody asked for.
  When the launcher is absent the command is printed instead of failing: ending
  an install in an error over an optional follow-up reads as a failed install.
  Both paths were exercised.

## v0.15.0

### Fixed

- **Reachability counted links and missed the files a skill leans on hardest.** After
  v0.13.0 taught the check to follow links transitively, it still only followed *links* —
  so four bundled scripts in `seo-aeo-audit` were reported as dead weight while `SKILL.md`
  names them in the sentence that tells the agent what ships and the references name them
  in the commands that run them: `` `gsc_pull.py` ``, `scripts/psi_pull.py`. A file the
  body tells you to execute is the opposite of unopened.

  Reachability is now by link, by path, or by bare filename, followed transitively.
  Probed: a reference nobody mentions anywhere is still flagged. `seo-aeo-audit` 4 → 0,
  family 11 → 7, nothing gained elsewhere.

**Third false-positive class in three releases, all one shape**: the check asserted how
a skill refers to its own files instead of measuring how these skills actually do it.
Between them the three fired on 45 correct files — more than half of every finding this
auditor reported across the family.

## v0.14.0

### Fixed

- **`LINK_ESCAPE` fired on every cross-skill link and called them all broken.** The
  check rejected any `../` target on the stated grounds that "packagers ship that
  directory alone, so it arrives broken on every agent." Measured against the packager:
  `npx skills add ssheleg/task-pipeline --skills evidence-docs` installed the sibling
  too, laid both under one `skills/` directory, and **all eleven** of `evidence-docs`'s
  outbound links resolved. The rationale was false for the case it fired on most.

  An escape that lands on a sibling in the same tree is a cross-skill link inside one
  plugin, and `evidence-docs` is deliberately built that way — it says so in its own
  body: *a navigator, not a second copy*. Twelve permanent findings nobody could ever
  close is how an auditor teaches people to ignore it.

  The check now fires only when the target resolves to **nothing**, which is the defect
  it was always for. Probed both ways: a dangling `../nonexistent-skill/nope.md` is
  still caught; the eleven real ones are not. Family-wide the count went 22 → 11 GAP,
  and no repository gained a finding.

## v0.13.1

### Fixed

- **`scripts/__pycache__/` shipped in v0.13.0.** Every other repository in the family
  carries a `__pycache__/` rule in `.gitignore`; this one did not, so a byte-compile run
  left an artifact and `git add -A` took it. The auditor's own `BUNDLE_NESTED` check
  caught it — on the release that changed the auditor, which is the most useful moment
  for a check to fire on its author.

## v0.13.0

### Fixed

- **`BUNDLE_UNREACHABLE` read reachability as one hop and called 29 correctly-shipped
  contracts dead weight.** The check asked whether `references/foo.md` appears as a
  substring of `SKILL.md`. But a packager ships a skill's directory alone, so a
  reference that links a sibling contract makes that sibling *required* — omit it and
  the first arrives with a dangling link. Reachability is therefore the transitive
  closure, which is exactly what `super-ux`'s own sync script computes, and the check
  disagreed with the mechanism it was auditing.

  Measured on `super-ux`: 29 → 0, with every other repository in the family byte-identical
  before and after. Probed both ways — a planted orphan is still flagged, and a file
  reachable only through another reference is not. The failing example was
  `ux-flows/references/figma-structure.md`: no direct link from `SKILL.md`, linked by
  `figma-integration.md`, `best-practices.md` and `system-map.md`, all three of which
  `SKILL.md` links directly.

- **The false positive was also masking real findings.** An entry flagged unreachable
  `continue`d past the `REF_NO_TOC` check, so a 312-line reference with no `## Contents`
  was invisible behind a gap that should never have fired. Fixing the reachability
  surfaced four of those — the correct behaviour, and the reason a false positive is not
  merely noise.

**Minor rather than patch**: for a tool whose output *is* its product, changing what it
reports changes what everyone downstream sees, and one of those changes is new findings
appearing on repositories that were green.

## v0.12.0

### Added

- **A language rule, and it is a budget rule before it is a style one.** Prose
  the agent reads is English; Cyrillic survives in four places only, where the
  string itself is the point rather than its meaning: a trigger phrase, a
  refusal phrase, a proper noun, a language example.

  Measured with `cl100k`: Russian encodes at **1.9–2.3 chars/token against
  English's 5.0**. Rewriting the eight ssheleg routers into English cut them
  **3408 → 1885 tokens (−44%)** with no loss of meaning — and those are
  always-on, in every session of every project.

  The exceptions are not a courtesy. A refusal phrase translated into English is
  a phrase nobody says, so the skill it belongs to stops being reachable. An
  audit of all twenty family skills found **zero** violations and 54 Cyrillic
  characters outside descriptions — every one of them a quoted literal, a
  proper noun (`Алиса`), or a localization example (`«вы»/«ты»`).

### Changed

- **Three sections lost their duplicated half** so the body could take the new
  rule and stay inside the 5% headroom: the optional-field list, the `name`
  character rules and the MCP/A2A wire-level bullets now point at the
  references that already carry them. What stayed is what a reference cannot
  carry — the reserved-substring trap, and that everything returning from a
  tool or a peer is untrusted data rather than instructions.

  This canon's own validator refused the rule three times for being over
  budget, which is the rule it states about bodies applied to the body stating
  it.

## v0.11.1 — 2026-08-10

A behavioural pass over v0.11.0 — walking the skill the way an agent walks it and
running every command it hands out, rather than re-reading the files. The
structural gates were already green; what this found was in the one field no
structural gate covers.

### Fixed — the description had a neighbour and no answer to it

Coexistence was measured instead of assumed, across the 130 skills of the 23
enabled plugins on the author's machine. The nearest neighbour is **not** the one
`test/evals/RESULTS.md` predicted:

| Neighbour | Overlap |
|---|---|
| **`claude-mem:version-bump`** | **9.6%** |
| `agent-sync` | 5.5% |
| `task-pipeline` (the predicted one) | 4.7% |

`version-bump` advertises "version increments across package.json,
marketplace.json, plugin.json manifests, git tagging, GitHub releases, and
changelog generation" — this skill's release checklist, and enabled alongside it.
The overlap is not vocabulary, it is *job*.

- The description now carries the clause `references/authoring.md` prescribes for
  exactly this case: **NOT for a version bump or release in a repo that ships
  anything but a skill or plugin.**
- **`triggers.json` gains q21 and q22**, the same manifest-bump-and-release
  request once where the artifact IS a skill and once where it is not, on
  opposite sides of the split so the near-miss is measured in validation rather
  than tuned on. 22 queries, 11 positive / 11 near-miss negative.
- `RESULTS.md` records the measured table and drops the guess.

### Added — the headroom rule reaches the field that decides triggering

v0.11.0 gave the body a 5% working limit and left the description at 1003 of
1024\. Adding the clause above needed 60 characters that did not exist — the same
disease, in the field that decides whether the skill fires at all. Both the house
validator and the bundled auditor (`--house`) now hold the description to **≤970
of 1024**, with a negative self-test on each.

### Verified, not assumed

Every command the canon hands an agent was executed against the released
artifact: `make-skill-audit` by bare name, the non-Claude fallback path, the
raw-fallback reference URLs (200 — checked for the first time), `npx skills add
--list` (no skeleton leaks), `npx` from a non-repo cwd, `claude plugin details`.
The hook was exercised on all three of its paths and returns valid JSON. Building
a skill from `assets/SKILL.template.md` and auditing it gives 0 GAP. The
compression in v0.11.0 was checked against every fact the evaluation scenarios
depend on: all of them are still reachable, and all 11 references are still
linked from the body.

The evaluation suite is still **authored and never executed against a model** —
that gap needs a fresh session per query per model, and this pass does not close
it. What it does show is why it matters: the risk this repo had written down was
not the risk it had.

## v0.11.0 — 2026-08-10

A file-by-file audit of the whole repo, run with this skill's own evidence rules.
It found one defect that made the canon read as nonsense, one that made its first
documented command fail, and a class of drift nothing was checking. Every fix
here ships with the rule that stops it coming back.

### Fixed — the two defects that manufacture wrong answers

- **A path variable used as a noun.** `SKILL.md` said "Hooks, subagents,
  `/commands`, `${CLAUDE_PLUGIN_ROOT}` and MCP servers exist only inside Claude
  Code". The body is substituted at load time, so what an agent actually read was
  "Hooks, subagents, `/commands`, `/Users/…/plugins/cache/make-skill/0.10.0` and
  MCP servers exist only inside Claude Code" — a filesystem path presented as a
  host capability. The body now names the capability, and the validator rejects
  any `${CLAUDE_*}` in it.

- **The first command of the audit procedure could not run.** `retrofit.md`, the
  `/skill-audit` command and the `skill-auditor` agent all opened with
  `python3 "${CLAUDE_PLUGIN_ROOT}/skills/make-skill/scripts/audit_skill.py"`.
  That variable is substituted into *text* and exported to *hooks*, but it is
  **empty in the Bash tool** — measured on Claude Code 2.1.220, the command
  expands to `/skills/...` and dies. The instruction immediately above it says
  "do not reason your way through it", so the agent was left with a forbidden
  fallback and a broken tool, and the cheap way out is a PASS nobody ran.

  Fixed at the root: **`plugins/make-skill/bin/make-skill-audit`**. Claude Code
  puts a plugin's `bin/` on the Bash tool's PATH, so the auditor is now reachable
  by name with no variable in the command. The wrapper resolves its payload from
  its own location (following symlinks), so it also works copied, symlinked into
  an agents hub, or called by absolute path. `bin/` is now documented as a host
  capability in its own right — it is the only reliable way to hand an agent a
  runnable command.

### Added — NOT-RUN, the missing verdict

An audit with only PASS and GAP forces a check whose tool is absent into one of
them, and the cheaper lie is PASS. `retrofit.md` now defines **NOT-RUN**, and the
standing example is its own item 1: `skills-ref validate` installs from source
only, so on most machines "NOT-RUN, with the reason" is the honest result. The
conformance checklist says so where the demand is made.

### Fixed — claims about the repo that the repo contradicted

Each of these was true when written and drifted the release after:

- `SKILL.md` said "13-item checklist" in its reference table and "14-item" nine
  sections later; the file has 14.
- `SKILL-CARD.md` — the card a reviewer reads before installing — was pinned at
  0.9.0, claimed "ten files" of instruction surface against eleven, and "six
  groups" of CI self-tests against eight.
- `README.md` never listed `mcp-ship.md`, added in v0.10.0.
- `README.md`'s "no agent turn required" one-liner used a glob one directory
  level too shallow: `no matches found`, and at the right depth it matches every
  cached version at once.
- `CONTRIBUTING.md` said "npm publishing stays a human step" 24 lines above "there
  is no manual `npm publish` step in any repo in the family", named `chars/4`
  where the validator uses the measured 3.9, and counted four channels where the
  canon documents five.
- Three files claimed the hook is "30 lines"; it is 43. The claim is gone rather
  than corrected — the number told a reader nothing.

**The rule that closes the class:** counted claims are now compared to the
artifacts they describe (checklist items, reference files, CI self-test groups),
`SKILL-CARD.md`'s version must equal `plugin.json`'s, and every shipped
`references/*.md` must appear in the README. A new gotcha states the principle: a
number typed by hand is an assertion, not documentation.

### Fixed — the Cursor rule contradicted the validator

`cursor/rules/make-skill.mdc` prescribed a repo-root `templates/` directory,
which `test/validate.py` rejects outright and a CI self-test asserts against. A
Cursor user following the shipped rule built a repo this repo refuses. The rule
now matches the canon, drops the superseded "npm publish = human 2FA", carries
the path-variable fact and the family-pin rule — and the validator fails if a
`.mdc` prescribes that layout again.

### Fixed — the installers created the shadow the canon forbids

`bin/make-skill.js` and `install.sh` wrote `~/.claude/skills/make-skill`, which
is exactly the duplicate-shadow this canon spends three paragraphs warning about,
with no check and no warning. Both now detect an installed plugin and refuse,
naming the update commands instead; `--force` still overrides.

### Fixed — the auditor

- `PASS NAME_CHARSET … is spec-legal` was printed for `claude-invoice-helper`,
  two lines above the GAP rejecting it. A PASS line quoted out of context is how
  a wrong verdict acquires real command output as its evidence; it now says
  "uses a legal charset".
- `REF_NO_TRIGGER` did not blank quoted spans, although `_strip_quoted` exists
  for exactly that: the canon could not quote the "see references/" it forbids
  without tripping its own linter.
- Link findings now carry `file:line`, the house checks (`--house`) report PASS
  as well as GAP — "the house rules were checked" has to be provable from the
  output the canon tells the agent to cite — and a body over the line budget also
  reports its token count instead of hiding it behind `elif`.

### Fixed — release and budget

- **`release.yml` now runs both `claude plugin validate … --strict` on the tag.**
  The validate workflow also runs there, but it is a separate workflow: a red run
  in it could not stop a release being cut and published.
- **The body budget has a working limit.** v0.10.0 shipped at ~4995 of 5000 — 20
  characters from a red build, which turns every future correction into a trade
  against an existing section. The validator now fails past **4750** (5%
  headroom); this release moved duplicated material into the references that
  already carried it and landed at ~4671.
- **The family pin is a stated non-negotiable of every release.** make-skill
  0.10.0 was on npm and installed while `sshlg-skills list` still advertised
  0.9.1 — the exact failure `distribution.md` describes, on this repo, found by
  this audit.
- `XML_TAG_RE` is now compared between `test/validate.py` and the shipped
  auditor: one rule, one pattern, or a skill passes one gate and fails the other.

### Notes

The evaluation suite is still **authored and never executed against a model**
(`test/evals/RESULTS.md`). Running it needs a fresh agent session per query on
each model in scope, which no CI job here does and no single session can honestly
fake. It remains the largest open gap, and `SKILL-CARD.md` says so to a reviewer.

## v0.10.0 — 2026-08-06

### Added
- **`references/mcp-ship.md`** — the half of MCP work that starts after the
  server compiles. Mounting into an existing FastAPI/Starlette app and the
  **double-path 404** that follows (FastMCP defaults `streamable_http_path` to
  `/mcp/`; mount that at `/mcp` and the real endpoint is `/mcp/mcp`, so every
  client 404s and the SSE fallback 404s too); ASGI auth middleware and why
  handler-level auth is too late; a health endpoint outside the mount, which is
  what separates "app down" from "MCP path wrong" — the two produce identical
  client errors. Then the 404/307/401 bisect, both client config shapes, and
  publication: `server.json` for remote and package servers, the three registry
  name claims (GitHub, DNS, HTTP) with Ed25519 key handling, `mcp-publisher`,
  CI automation, and versioning.

  This is a deliberate delta, not a duplicate. Anthropic's `mcp-builder` skill
  covers authoring and evaluation well and carries **nothing** on the registry,
  on mounting, or on why a client sees 404 — checked against it on 2026-08-06.
  The reference says so in its own opening so the boundary survives contact
  with whoever reads it next.

### Notes
- The reference is reachable from the merged MCP row in the reference table.
  `SKILL.md`'s body budget was already at ~4981 of its 5000-token ceiling, so a
  new row did not fit — the validator caught that on the first attempt, which is
  the budget working as designed rather than an obstacle to route around.

## v0.9.1 — 2026-08-05

### Fixed
- **The release checklist told agents to publish npm by hand.** Step 5 of the
  recurring-release checklist in `distribution.md` said "npm publish if
  applicable (human 2FA the first time)" — contradicting the launch checklist's
  own step 9, which arms CI publishing precisely so that is the *last* manual
  publish. A `v*` tag now publishes; manual publish is named as the fallback
  for a repo that has not armed CI yet.
- `CONTRIBUTING.md` carried the same stale instruction for the family
  catalogue, and now points at `test/check_pins.py`, the registry comparison
  `sshlg-skills` gained in v0.20.0.

## v0.9.0 — 2026-08-03

The canon knew the Claude Code capability set and used none of it. This release
uses it — and turns the missing half into a rule: **every host capability is an
accelerator with a written fallback**, because hooks, subagents and `/commands`
exist only inside Claude Code, which is a minority of where skills run.

### Added
- **`references/host-capabilities.md`** — hooks (events, handler types, matchers,
  `if` rules, exit-code semantics, structured output, plugin-scoped MCP matchers),
  subagents, commands, scripts, MCP and sibling-skill dependencies: what each
  buys, what it costs in always-on tokens, and when it earns its place. Verified
  against the hooks reference and against a working plugin, not from memory.
- **The degradation contract**, in `SKILL.md` and enforced by the validator.
  Three axes, each written in the body where the agent will read it: not Claude
  Code (no hooks/subagents/commands — name the inline procedure), recommended
  plugin absent (say what is degraded, continue), tool or MCP server absent
  (state it once, fall back, never retry in a loop). *A fallback you know but did
  not write is not a fallback.*
- **`scripts/audit_skill.py`** — a stdlib auditor for ANY skill directory: name
  charset/length/reserved words/XML tags/directory match, description limits and
  third person, frontmatter keys, body budgets, bundled-file reachability and
  nesting, tables of contents past 100 lines, link escapes, Windows paths,
  time-branching prose, bare directory pointers. `--house` adds the ssheleg
  rules. It finds all nine planted defects in the evaluation fixture and passes
  clean on this skill; CI asserts both.
- **A `PostToolUse` hook** that audits a `SKILL.md` the moment it is written, and
  is otherwise invisible: it exits 0 with no output for any other path, for a
  missing `python3`, for a missing script. It advises via `systemMessage` and
  never blocks — `PostToolUse` fires after the write, so a veto costs a turn and
  buys nothing.
- **`commands/skill-audit.md`** (deliberately not named after the skill) and
  **`agents/skill-auditor.md`** — a subagent for auditing a repo full of skills
  without crowding the main thread, including the coexistence check that is
  invisible per-skill.
- **Six skeletons in `assets/`**, now *inside* the skill directory so they travel
  on every channel: SKILL, plugin manifest, marketplace manifest, and new hooks,
  agent and command templates, each carrying its degradation clause.
- **`SKILL-CARD.md`** — the enterprise registry entry plus an honest pass over
  the risk table, including the hook that runs automatically. **`test/evals/RESULTS.md`**
  states plainly that the suite has never been executed against a model.
- Frontmatter `compatibility` (what this skill needs and where it does not work)
  and `metadata.version`, which is the only version an agent outside Claude Code
  can see — now the fifth point of the version-sync rule.

### Fixed
- **The skeletons reached no agent.** `templates/` sat at the repo root, outside
  the plugin directory and outside the skill directory, so neither the Claude
  Code plugin nor the skills CLI ever shipped them. They are `assets/` now, and
  the validator fails if a root `templates/` reappears.
- The auditor's own first run flagged a false positive on this skill's
  anti-pattern gotcha ("Before August, use the old API" — quoted as an example).
  Quoted and backticked spans are now excluded: a linter that flags the document
  warning about the thing it detects earns the habit of being ignored.
- New validator rules, each with a negative self-test: hook commands must resolve
  through a quoted `${CLAUDE_PLUGIN_ROOT}` and carry a timeout, hook scripts must
  exist with a shebang and the executable bit, plugin agents must not carry
  `hooks`/`mcpServers`/`permissionMode`, shipped scripts must compile, and the
  degradation section must be present.

## v0.8.1 — 2026-08-03

A file-by-file re-read of everything 0.8.0 touched, and of everything it didn't.
Fourteen findings, all fixed. The two that would have misled a reader:

### Fixed
- **The token estimate was asserted, not measured.** The validator's comment
  claimed dense markdown runs "closer to 3.7 chars/token, so this under-reports";
  nothing had ever been counted. Tokenizing the bundle gives **3.78–4.47**
  chars/token (3.9 for `SKILL.md`), so the divisor is now 3.9, measured — and
  the recalibration immediately failed the body it was checking, which is what a
  calibrated rule is for. The audit checklist moved to a new
  **`references/retrofit.md`**, bringing the body to ~4.6k tokens with headroom.
- **`claude plugin details` and a real tokenizer disagree by ~40%** — the CLI
  reported ~7.2k on-invoke for a `SKILL.md` that tokenizes at ~5.0k, because its
  estimator assumes ~2.8 chars/token. Measured across six installed skills and
  recorded as a gotcha: budget against a tokenizer, expect the CLI to look
  alarming, and never gut a body that is genuinely inside the budget.
- **`SECURITY.md` described paths the installers do not write.** It claimed
  `bin/make-skill.js` and `install.sh` copy into `~/.claude/commands/`; that
  command file was deleted in 0.6.x and CI asserts its absence on every run. The
  threat model now matches the code, and states what `test/evals/fixtures/` is —
  including that the malicious sample is inert data, never installed.
- **The trigger split could not measure what it claimed.** `train: q01-q12` /
  `validation: q13-q20` put all ten positives in train and left validation with
  nothing but negatives, so the held-out half could only detect false-firing.
  Split is now explicit ids with both classes on both sides, and the validator
  rejects a half that holds only one class.
- **`displayName` was required by the canon and absent from the skeletons.**
  Both manifest templates now seed it, and the validator enforces it in the
  templates, in `plugin.json`, and in the marketplace entry — where it belongs
  (the marketplace root takes neither `displayName` nor `homepage`).
- **`/make-skill` is only half the truth.** As a plugin the command is
  `/make-skill:make-skill`; the bare form is what a skills-directory install
  gets. README and canon now state both, and the canon says to write both rather
  than promise one.
- `distribution.md`'s table of contents listed a "shadow rule" section that did
  not exist as a heading — the exact failure a table of contents prevents. It is
  a real section now.
- Counts that had drifted: CONTRIBUTING said CI runs "four negative self-tests"
  (six groups), the issue-template contact link said "the other four skills"
  (five), the retrofit fixture header claimed eight planted defects (nine, now
  scored one per line).
- Dead `EVAL_DIR` variable removed; `test/evals/` added to the Cursor rule's
  layout tree and to the templates README, both of which still described a repo
  without it; the PR template now asks for the two `--strict` runs and for an
  eval re-run when the description changes.
- Three more negative self-tests (split classes, `displayName` ×2), keeping the
  rule that no validator rule ships without one.

## v0.8.0 — 2026-08-03

Read Anthropic's four Agent Skills pages end to end (overview, authoring best
practices, enterprise, the API skills guide) and audited the canon against them.
The canon had been written against the open standard and the Claude Code plugin
reference only — so it was correct about the format and blind to everything
Anthropic's own surfaces enforce, recommend, or forbid. Three new references,
six new validator rules, and one self-violation fixed.

### Added
- **`references/surfaces.md`** — the surface a skill runs on is a portability
  contract, and it was undocumented here. Claude Code has full network and local
  installs; the **Claude API container has neither**; claude.ai varies. A skill
  whose script `pip install`s or curls works on one surface and silently fails
  on the next. Also the whole Skills API — beta headers, `container.skills[]`,
  **max 8 skills per request**, upload rules (top-level dir must match `name`,
  `display_title` uniqueness, **< 30 MB**), epoch-timestamp versions,
  delete-all-versions-before-delete — the claude.ai zip channel (per user, no
  admin push), and the fact that **nothing syncs between surfaces**.
- **`references/enterprise.md`** — installing a skill you did not write is
  installing software, and the canon said so without saying how to check.
  Anthropic's risk-tier table, the 8-step review checklist, the five approval
  gates (triggering accuracy, isolation, **coexistence**, instruction following,
  output quality), lifecycle with separation of duties, registry fields, recall
  limits, and the production versioning/rollback/integrity rules.
- **`references/authoring.md`** — the craft that the spec reference had only
  hinted at: naming conventions (gerund; never `helper`/`utils`/`tools`),
  **degrees of freedom** matched to task fragility, workflow checklists and
  feedback loops, the script rules (solve-don't-defer, no voodoo constants,
  execute-vs-read intent, declare packages), content guidelines, and
  **evaluation-driven development** — evals before prose, ≥3 scenarios, a
  no-skill baseline, the Claude-A/Claude-B loop, testing on every target model.
  The trigger-eval loop moved here from the spec reference.
- Six validator rules with negative self-tests that assert the *reason* for the
  failure, not just a non-zero exit: reserved words in `name`, XML tags in
  `name`/`description`, first/second person in `description`, the body token
  budget, a `## Contents` list on references past 100 lines, and angle-bracket
  placeholders in the SKILL template.
- **`test/evals/`** — make-skill's own evaluation suite, because the canon now
  requires one from every skill and shipping the rule without obeying it is how
  a standard becomes decoration. `triggers.json`: 20 queries, 10 that must fire
  (EN + RU) and 10 near-misses that share the keywords — "add a skills section
  to my CV", "publish this React library to npm", "implement an MCP server for
  Postgres". `scenarios.json`: four behavioral evaluations in Anthropic's shape
  (create, retrofit-with-evidence, surface portability, third-party review),
  scored line by line, with fixtures under `test/evals/fixtures/` — deliberately
  broken and deliberately not named `SKILL.md`. The validator proves they exist
  and are well-formed and cannot run them: that part is a human with an agent
  (`test/evals/README.md`).

### Fixed
- **`name` may not contain `anthropic` or `claude`, and neither field may
  contain XML tags.** The open standard is silent on both; Anthropic's platform
  enforces them at upload. So `claude-helper` loads happily in Claude Code and
  is rejected the day someone ships it to the API — a failure that only ever
  appears on someone else's machine. Canon, spec reference, Cursor rule, README
  and validator now carry the rule.
- **Descriptions must be third person.** They are injected into the system
  prompt, where "I can help you…" / "You can use this to…" measurably degrades
  selection. Stated in the canon and checked by the validator.
- **This skill was over its own token budget.** `SKILL.md` was ~5.2k estimated
  tokens against a stated `< 5000` — a rule the repo enforced on everyone but
  itself, because only the 500-line half was ever checked. The body budget is
  now measured (frontmatter excluded as level-1 metadata) and the body was cut
  by moving the repo layout, the two Claude Code gates, the validator spec and
  the release checklist into `references/distribution.md`. (The divisor used
  here was a guess; v0.8.1 measured it and cut further.)
- **Reference files longer than 100 lines now open with a `## Contents` list.**
  Agents preview long files with `head`; without a table of contents they act on
  the first hundred lines and never learn the rest exists. All eight references
  gained one — five were in violation.
- **The SKILL template seeded an invalid skill.** Its `name: <skill-name>` and
  `<angle-bracket>` description placeholders are XML tags in exactly the two
  fields where Anthropic rejects them. Replaced with plain placeholders, and the
  validator now checks the skeleton it ships.
- **MCP tool names: two conventions, both real.** Anthropic's authoring guidance
  writes `ServerName:tool_name`; Claude Code's runtime names are
  `mcp__<server>__<tool>`. The canon documented only the second, which reads as
  wrong against the docs — both are recorded now, with "list and match" still
  the rule.
- Retrofit audit gained surface honesty (item 3) and evaluations (item 8);
  authoring rules gained naming style, prescriptiveness-to-fragility, and the
  no-time-branching rule with the "Old patterns" escape hatch.

## v0.7.1 — 2026-07-31

Re-read the plugin reference against what the canon actually says, and against
what Claude Code 2.1.212 actually does. Six corrections, two of them places
where the docs and the binary disagree.

### Fixed
- **`claude plugin validate` validates the manifest, not front matter.** The
  docs' troubleshooting table says it checks "`plugin.json`, skill/agent/command
  frontmatter, and `hooks/hooks.json`"; a `SKILL.md` carrying an invented
  front-matter key passes `--strict` untouched. The canon said this gate
  "catches a class your validator cannot see" — true for manifests, misleading
  for front matter, which is exactly where the house validator earns its place.
- **`claude plugin update <bare-name>` does not work**, though the docs list a
  bare name as accepted: it answers `Plugin "make-skill" not found` **and exits
  0**, so a release script sees success and ships nothing. The reference now
  records both the documented form and the observed one.
- **`skills` adds to the default scan — except at a marketplace root.** When a
  plugin entry's `source` resolves to the marketplace root, the listed
  subdirectories replace the default `skills/` scan (and if none exist, the
  default runs after all). The reference stated the rule without its exception.
- **"Every component directory sits at the plugin root" was too absolute.** That
  is the default; a manifest path field may point anywhere inside the plugin,
  and since 2.1.140 Claude Code warns when a manifest key leaves a default
  folder unscanned. Only `.claude-plugin/` is genuinely off-limits.
- **`allowed-tools`: Claude Code is looser than the spec.** It accepts a
  space- or comma-separated string or a YAML list; the open standard accepts
  only the space-separated string. Canon, Cursor rule and the validator's own
  error message now say which form travels and why, instead of calling a legal
  Claude Code skill invalid.
- **npm plugin sources** resolve to `unknown` only when no `version` is set
  anywhere — the entry or manifest version still wins.

### Changed
- The stray-`SKILL.md` rule is scoped honestly: a plugin-root `SKILL.md` is a
  legal single-skill plugin in Claude Code (2.1.142+). It is multi-channel
  distribution — the skills CLI shipping every `SKILL.md` in the tree — that
  makes the rule, and the validator says so.
- Version pinning: omitting `version` from both manifests is legal and hands
  updates to the git SHA. This canon pins and bumps by choice, which the gotcha
  now states rather than implies.

### Added
- **LSP and monitor fields in `references/claude-code-plugin.md`.** Its own load
  condition promised "adding agents / hooks / MCP / LSP / monitors", and the
  file had a table row for each and nothing else: now the required and optional
  LSP keys with the 2.1.205 `restartOnCrash` / `shutdownTimeout` trap and the
  same-extension race, and the monitor entry schema with its trust,
  `${user_config.*}` rejection and session-lifetime rules. Plus the missing
  `themes/` row.

## v0.7.0 — 2026-07-30

Conformance to Anthropic's own plugin reference
(<https://code.claude.com/docs/en/plugins-reference>), checked with Anthropic's
own checker. The canon already matched the Agent Skills open standard; the
Claude Code layer on top of it — manifest schemas, component layout, path
variables, the CLI — was folk knowledge until now. Everything stays
multi-agent: the host layer is documented as host-specific and never
load-bearing for skills that also run on Cursor, Codex, or the skills CLI.

v0.6.5 wired the upstream gate into CI and fixed the two failures it caught;
this release is the rulebook behind it — so the next repo passes `--strict`
before anyone runs it, not after.

### Added
- **`references/claude-code-plugin.md`** — the Anthropic layer: full
  `plugin.json` and `marketplace.json` schemas, plugin sources, strict mode,
  reserved marketplace names, component locations, skill front-matter host
  extensions, plugin-agent restrictions, scoped MCP hook names,
  `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` / `${CLAUDE_SKILL_DIR}`,
  cache and symlink behavior, skills-directory plugins, the whole
  `claude plugin` CLI, and a conformance checklist. Dated against Claude Code
  2.1.212.
- `$schema` in both manifests (schemastore), so the next edit gets autocomplete
  and inline validation.
- The upstream gate now also covers the **retrofit audit** and the **release
  checklist**, and CI runs it as **its own job** so an upstream CLI outage
  cannot mask a house-validator failure.
- Validator rules, each with a negative self-test: recognized-fields-only for
  both manifests, `$schema` present, reserved marketplace names, `./`-relative
  component paths that never escape the plugin root, source directory name ==
  plugin name, and nothing but the manifest inside `.claude-plugin/`.
- Skill front-matter now accepts the **Claude Code extension keys**
  (`when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`,
  `user-invocable`, `disallowed-tools`, `model`, `effort`, `context`, `agent`,
  `background`, `hooks`, `paths`, `shell`) alongside the spec set. Previously a
  conformant Claude Code skill failed this repo's own audit.
- `templates/plugin.template.json` and `templates/marketplace.template.json` —
  annotated, schema-linked skeletons for the two manifests.
- Personal workflow: a `~/.claude/skills/<name>/` folder with
  `.claude-plugin/plugin.json` loads as `<name>@skills-dir` with hooks, agents,
  and MCP servers — no marketplace, no install step (`claude plugin init`).
- Gotchas: unknown manifest fields load fine and mean nothing (only `--strict`
  surfaces them); a pinned `version` you forget to bump freezes every user,
  because the version is the update cache key.
- `displayName` in both manifests, and the v0.6.6 canon on `claude plugin
  details`, folded in from the parallel release.

### Removed
- **`plugins/make-skill/commands/make-skill.md`.** `claude plugin details`
  reported `Skills (2) make-skill, make-skill`: a command and a skill of the
  same name register `/make-skill` twice, the skill wins, and the command was
  ~100 always-on tokens per session for something unreachable. Its workflow
  detection now lives in the skill body, where it was always going to be read.
  The validator rejects any `commands/<x>.md` that collides with `skills/<x>/`
  and any unquoted `argument-hint`, with negative tests for both; the npx
  installer and `install.sh` no longer write `~/.claude/commands/make-skill.md`
  (an existing copy from an older install is harmless and can be deleted).

### Changed
- **Progressive disclosure applied to the body itself.** The four installer
  implementation traps (piped-stdin readline, raw-mode pickers, ANSI literals,
  Python 3.9 annotation drift) and the 11-step **First publish** sequence moved
  out of `SKILL.md` into `references/distribution.md`, each under a stated load
  condition: they matter only while writing the CLI or actually publishing,
  while the body's token budget is paid by every session. `SKILL.md` ends this
  release under both caps — 347 lines, ~5k tokens — despite everything added
  here and in v0.6.2–v0.6.5.

## v0.6.6 — 2026-07-30

### Added
- **`claude plugin details` joins the canon as the check no manifest performs**:
  it prints what Claude Code believes the plugin contains and the always-on token
  cost per component. Two defects are visible only there — a component listed
  **twice**, because a `commands/<x>.md` and a `skills/<x>/SKILL.md` both claim
  `/<x>` now that custom commands are merged into skills, and a description whose
  always-on cost is worth trimming.
- **`displayName` in both manifests** is now canon: `name` is kebab-case because
  it namespaces components, and the `/plugin` picker falls back to it, so a
  listing reads `my-cool-plugin` until the field is set.

## v0.6.5 — 2026-07-30

### Added
- **`claude plugin validate <path> --strict` is now canon** — the upstream gate,
  wired into CI against both the plugin and the marketplace manifest. It needs
  no auth or API key, so a runner can install `@anthropic-ai/claude-code` and run
  it. The canon records the two failures it found across all six repos of this
  family at once, because neither is visible to a house validator:
  - **`argument-hint` must be quoted.** Bare `[a | b]` is a YAML flow sequence,
    so it parses as a list — and one comma or stray character breaks the block
    outright, at which point the command loads with empty metadata and no
    description, silently.
  - **`homepage` and `repository` are not top-level `marketplace.json` fields.**
    They belong to a plugin entry. Unrecognized fields are warnings the runtime
    tolerates, which is why they survive everything except `--strict`.

### Fixed
- This repo's own command hint and marketplace manifest, per the above.

## v0.6.4 — 2026-07-30

### Changed
- **Publishing to npm is no longer taught as a permanent human step.** The canon
  said 2FA makes non-interactive publishing impossible and to plan the manual
  step; that is only true of an interactive publish and a classic token. Arming
  CI publishing is now step 9 of the first publish, and the definition of done
  gained a fifth fact: *the next tag publishes without a human*.
- **`references/distribution.md` §3** carries both auth routes — npm trusted
  publishing (OIDC, no credential at all: npm >= 11.5.1, Node >= 22.14,
  `id-token: write`, the workflow filename registered on npmjs.com) and a
  granular automation token in `NPM_TOKEN` — and says to write the workflow so
  both work, which makes adopting OIDC later a secret deletion rather than a CI
  edit.
- Three properties the publish job needs, each of which is a red build if
  missing: skip a version already on the registry (publishing over one is a hard
  403), a `workflow_dispatch` input naming an existing tag (a dispatch runs the
  workflow file as of the ref it is dispatched on, so an old tag can never gain
  a new job), and polling `npm view` afterwards, because published is a claim
  until the registry serves it.
- The release-automation section is no longer marked *optional*, with the
  measurement that argues it: six of this family's seven packages were behind
  their own tags on 2026-07-30, one by three releases.

## v0.6.3 — 2026-07-30

### Added
- **Declare the licence in BOTH manifests — now part of the spec floor.** An
  SPDX id belongs in the SKILL.md front matter *and* in the `marketplace.json`
  plugin entry (a documented field there too). A `LICENSE` file in the repo root
  reaches neither the plugin listing nor an installed skill. This gap was found
  across all six repos of this family on the same day, and it stayed open
  precisely because this checklist never asked for it: both fields are optional,
  so nothing ever errored.

### Changed
- `license: MIT` declared in this repo's own two manifests, which is where the
  rule should have been demonstrated first.

## v0.6.2 — 2026-07-30

A family member's release did not end where the skill said it ended. Publishing
to npm left the umbrella pin pointing at the previous version, so the launcher
kept advertising — and `update` kept installing — the release before it, with
nothing in either repo to reveal the gap.

### Added
- **First-publish step 10** (`SKILL.md`): a skill that belongs to a family is
  not released until the umbrella's `skills.json` pin moves and the umbrella is
  released, verified with `npx --yes sshlg-skills@latest list`.
- **`references/distribution.md` §5** — the same rule with the incident that
  produced it (`agent-sync` 1.3.4 on npm while `list` still said 1.3.3).

### Changed
- README — family list and the three family commands; `CONTRIBUTING.md`.

## v0.6.1 — 2026-07-28

Open-source hygiene pass — the repo is public, so the files a first-time
contributor looks for now exist.

### Added
- `CODE_OF_CONDUCT.md`, issue forms for bugs and ideas, and a pull-request
  template carrying this repo's actual checks (`test/validate.py`, `bash -n
  install.sh`).
- US spelling in the changelog.

## v0.6.0 — 2026-07-28

Production pass for a public repository: the README now explains the project
before it explains its own conventions, contributors get an entry point, and the
last inaccuracies found by reading every file end to end are gone.

### Added
- **`CONTRIBUTING.md`** — what belongs in the canon (evidence, not advice), the
  offline one-liner that runs the entire CI suite locally, the rules the
  validator enforces, and the standing requirement that every new validator rule
  ships with a negative test.
- **`SECURITY.md`** — private reporting channel, an exact statement of what the
  installers touch (`~/.claude/skills/make-skill`, `~/.claude/commands/`, no
  network, no postinstall, zero dependencies), and the point that a skill is text
  an agent executes, so it deserves review before installation.
- `--version` / `-v` on the installer CLI, asserted in CI against
  `package.json`.
- **Public-repo floor** in the canon and in the validator: README, CHANGELOG,
  LICENSE, CONTRIBUTING and SECURITY are required root files once a repo is
  public, each with a negative self-test.
- Validator rule: every `references/*.md` must carry a `Load this when:` line.
  A reference without a stated condition is loaded always or never — the exact
  failure progressive disclosure exists to prevent.
- `bugs` URL in `package.json`; `SECURITY.md` added to the published files.

### Fixed
- **The shadow-copy gotcha understated the problem.** Docs said to remove a stray
  `~/.claude/skills/<name>` copy "if it appears". It reappears on schedule: the
  skills CLI auto-detects Claude Code and recreates that path — usually as a
  symlink — on every `--global` add or update, whether or not `claude-code` was
  targeted. The prune is now documented as part of the update command itself.
- The v0.1.0 implementation plan still described `templates/SKILL.md` and an
  unscoped npm package; marked executed and pointed at the spec's Superseded
  table, matching the treatment its sibling spec already had.
- Reference files derived from moving specs (Agent Skills, MCP, A2A) now carry
  the date they were read, so a stale claim is visible instead of implied.

### Changed
- **README rewritten for a first-time reader**: what it is in two sentences, a
  quickstart that ends in a working command, what you actually get (standard
  conformance, a validator that can fail, every channel, the named gotchas,
  where a skill ends and MCP/A2A begin), an install matrix with the prune step
  in it, and a requirements section.
- `permissions: contents: read` on the validate workflow.
- `package.json` keys ordered conventionally.

## v0.5.1 — 2026-07-28

Full-repo consistency pass: every file read against every other, contradictions
fixed rather than annotated.

### Fixed
- **The Cursor rule claimed "no external links" while carrying four.** The actual
  rule — the one the validator enforces — is *no **relative** links*, because the
  `.mdc` gets copied into foreign projects. Stated correctly now.
- **The canon demanded a README section this repo deliberately doesn't have.**
  `README.md (EN + closing RU section)` in the layout and "RU section" in the
  Retrofit audit contradicted the v0.4.0 decision to ship an English-only README.
  Canon now says English-first, with Russian where it actually changes behavior
  (trigger phrases) and an optional RU section for RU-facing projects.
- **The entry-point command contradicted its own design rule.** The canon says a
  `/<name>` command must "detect mode, never ask"; `/make-skill` with no argument
  asked what to build. It now inspects the working directory (`SKILL.md`,
  `.claude-plugin/`, `plugins/*/skills/*/`) and runs the Retrofit audit, asking
  only when there is nothing to detect.
- **The release workflow could ship a broken skill.** Its npx smoke test asserted
  `SKILL.md` and the command but not `references/*.md`, so a release missing them
  would pass while every reference link dangled. Now asserted, matching the
  validate workflow.
- Version-sync arity was stated as four in the body while the validator enforced
  a fifth point (`SKILL.md` `metadata.version`) when present — documented in the
  hard rule, the audit checklist, the Cursor rule, and the validator comment.
- The v0.1.0 promote spec still stated three contracts that did not survive
  contact (bare npm name, `templates/SKILL.md`, "no references split needed").
  Marked executed, with a Superseded table pointing at what actually shipped.
- Layout trees disagreed across SKILL.md, the Cursor rule, and README
  (`release.yml`, `scripts/`, `assets/`, `references/`) — reconciled.

### Changed
- **Descriptions refreshed everywhere they exist** — skill front-matter (772/1024
  chars), `plugin.json`, `marketplace.json`, `package.json`, the slash command,
  and the Cursor rule now name spec conformance, auditing, and MCP/A2A, and carry
  the new trigger pair *"does this skill match the spec" / "соответствует ли
  скилл стандарту"*. Keywords gained `agent-skills`, `mcp`, `a2a`, `spec`.
- README: standard-conformance and protocol-boundary bullets in "What this gives
  you"; the Use section documents no-argument auto-detect.
- `templates/README.md` documents the spec-aware skeleton, the
  never-name-it-`SKILL.md` rule, and where `references/`/`scripts/`/`assets/` go.

## v0.5.0 — 2026-07-28

Audited the canon against the **Agent Skills open standard**
(<https://agentskills.io/specification>, `agentskills/agentskills`). The canon
was compatible but silent on most of the spec: it never stated the `name`
charset rules, capped the wrong thing (whole front-matter instead of
`description`), never mentioned `license` / `compatibility` / `metadata` /
`allowed-tools`, `scripts/` / `assets/`, or the progressive-disclosure budgets.

### Added
- `references/agent-skills-spec.md` — the full standard as a conformance
  reference: field table with limits, `name` charset rules, directory layout,
  the <500-line / <5000-token budgets, the description trigger-eval loop
  (20 queries × 3 runs, 60/40 train/validation split), body patterns, and an
  audit checklist. Marks explicitly where the house canon *extends* the spec.
- `references/mcp.md` — MCP for skill authors: skill vs MCP server, the
  host/client/server model, lifecycle and capability negotiation, server
  primitives with exact methods (`tools/list`, `tools/call`,
  `resources/templates/list`, `prompts/get`, …), client primitives
  (`sampling/createMessage`, `elicitation/create`, roots), stdio vs Streamable
  HTTP, the consent/untrusted-output security rules, and the gotchas
  (host-prefixed tool names, dynamic tool lists, interactive OAuth).
- `references/a2a.md` — A2A for skill authors: A2A vs MCP, the Agent Card at
  `/.well-known/agent-card.json`, Task/Message/Part/Artifact, the task
  lifecycle, the 1.0 method mapping across JSON-RPC/gRPC/REST, streaming vs
  webhook push, security, and the **v0.x→1.0 wire drift** (`message/send` →
  `SendMessage`, lowercase states → `TASK_STATE_*`) that silently breaks
  integrations.
- `references/distribution.md` — the distribution matrix and npm publishing
  traps, moved out of the body (progressive disclosure) so `SKILL.md` stays
  inside the spec's budget.
- SKILL.md: a **Spec floor** block in the authoring rules, a
  **Protocol-connected skills (MCP / A2A)** section, a load-on-demand reference
  index with a raw-URL fallback, and audit items 1 and 10 in the Retrofit
  checklist.

### Changed
- **Validator now enforces the spec, not just house rules:** `name` charset /
  ≤64 / == directory, `description` ≤1024 (the correct field — the old check
  capped the whole front-matter block), `compatibility` ≤500, `metadata` as an
  all-string map, `allowed-tools` as a string, rejection of any front-matter key
  outside the standard, `SKILL.md` < 500 lines, `references/` one level deep with
  every file reachable from the body, and no relative link escaping the skill
  directory. Front-matter is now parsed (YAML subset incl. folded blocks and
  nested maps) instead of regex-sniffed.
- Optional 5th version-sync point: if `SKILL.md` carries `metadata.version`, it
  must match the manifests.
- `templates/SKILL.template.md` is spec-aware: optional front-matter fields
  documented inline, budgets stated, plus References and Gotchas sections.
- Cursor rule carries the spec floor and the MCP/A2A rules inline (no relative
  links — it gets copied into foreign projects).

### Testing
- CI gained a four-case negative self-test for the spec rules (bad `name`
  charset, over-long `description`, unknown front-matter key, orphaned reference
  file) — each must fail the validator.
- The installer functional test now asserts all four `references/*.md` land in
  the install target; a channel that drops them ships broken relative links.
- The first negative self-test used `sed -i` GNU-style, so it only ran on CI and
  errored on any macOS/BSD dry run. Rewritten in `python3` like its siblings —
  the whole workflow is now runnable locally.

## v0.4.1 — 2026-07-28

### Fixed
- The `validate` workflow had been **red since v0.3.0**: its negative self-test
  deleted `templates/SKILL.md`, a file renamed to `templates/SKILL.template.md`
  three releases earlier. Deleting a non-existent file is a no-op, the validator
  correctly passed, and the step reported that as an error — so the check proved
  nothing while looking like it failed.

### Added
- A second negative self-test: stripping the Russian trigger aliases out of the
  description must fail the validator.

## v0.4.0 — 2026-07-28

### Changed
- Description restructured English-first: each Russian trigger is now paired
  with its English equivalent (`"publish a skill" / "опубликуй скилл"`) rather
  than trailing the English list.
- README is English-only, with a plain statement of what the skill gives you and
  an author/links block.

## v0.3.1 — 2026-07-25

- Gotcha: **npm reports auth failures as `404` on publish.** A `PUT … 404` for a
  package that `npm view` resolves means an expired token, not a missing package —
  check `npm whoami` (E401 → `npm login`) before debugging the name. Cost two
  debugging rounds.

## v0.3.0 — 2026-07-25

Review pass — a live shipping defect plus canon corrections that the repo itself
was violating.

- **FIX (shipping defect): `templates/SKILL.md` was distributed as a real skill.**
  The skills CLI discovers EVERY `SKILL.md` in a repo, so the skeleton was listed
  and installed on every agent as a placeholder skill literally named
  `<skill-name>` (`npx skills add ssheleg/make-skill --list` → "Found 2 skills").
  Renamed to `templates/SKILL.template.md`; the validator now **rejects any
  `SKILL.md` outside `plugins/*/skills/*/`** so it cannot recur.
- **Canon: shared contracts must live INSIDE the skill dir.** The skills CLI
  ships only the skill's own directory, so a sibling `skills/references/`
  (linked `../references/…`) reaches Claude Code plugins but arrives broken on
  every other agent. Layout, authoring rules and the retrofit checklist updated;
  new gotcha documents both this and the stray-SKILL.md trap.
- **Validator hardened** (it now enforces what the canon preaches): description
  must start "Use when …", must carry Russian triggers, frontmatter < 1024 chars,
  no relative links inside `.mdc`, no stray `SKILL.md`. Each rule has a negative
  test.
- **Docs:** README no longer suggests the skills CLI for Claude Code (it shadows
  the plugin); release checklist quotes the validator's real output.

## v0.2.0 — 2026-07-24

Correct multi-agent + cross-platform distribution guidance (learned shipping the
`sshlg-skills` umbrella).

- **skills CLI, multiple agents:** documented that multiple agents need
  **repeated `--agent` flags** (`--agent cursor --agent zed`) — a comma/space
  value is read as one invalid agent. Exact agent ids (`kimi` → `kimi-code-cli`,
  `hermes` → `hermes-agent`), the `universal`/`*` targets, and the
  `--agent __x__` trick to print the valid list.
- **Umbrella / family distribution** (new matrix item): ship a family of skills
  from their own repos aggregated as git submodules, with a zero-dep launcher
  wrapping `npx skills add` + `claude plugin` + `git submodule update --remote`
  and a `skills.json` source of truth — reference impl `ssheleg/sshlg-skills`.
- **Platforms:** the Node installer, `npx github:`, the plugin, and the skills
  CLI are cross-platform; `install.sh` is POSIX-only (on Windows use npx/plugin/
  skills CLI). Build bin paths with `path.join`, never hardcoded `/`.

## v0.1.0 — 2026-07-24

Initial release — the `make-skill` meta-skill promoted from a personal skill into
a full distributable plugin, built to its own canon.

- **Skill** (`plugins/make-skill/skills/make-skill/SKILL.md`): the proven pipeline
  — authoring rules, the distributable repo layout, Create / Retrofit / Promote
  workflows, end-to-end first publish, the distribution matrix, and the gotchas
  catalog. Reference impls: super-ux (structure) + task-pipeline (config-contract
  + release automation).
- **Command** `/make-skill`: routes a task to the right workflow.
- **Distribution (5 channels):** Claude Code plugin/marketplace, vercel skills CLI
  (`npx skills add`), npm (**`@ssheleg/make-skill`** — scoped, because npm blocks
  the bare `make-skill` as too similar to an existing package) + `npx github:`,
  plain `install.sh` (idempotent, `--force`), and a self-contained Cursor rule
  (`cursor/rules/make-skill.mdc`). Plugin, command, and `bin` names stay
  `make-skill`; only the npm package is scoped.
- **templates/SKILL.md**: canon skeleton seeded when scaffolding a new skill.
- **Validator** (`test/validate.py`, stdlib-only): name sync, four-way version
  sync (marketplace / plugin.json / package.json / CHANGELOG top), command +
  Cursor `.mdc` frontmatter, npm `bin`/`files` shape, template presence, relative
  link resolution. CI runs it plus negative self-tests (corrupt version, missing
  template) and a functional installer test.
- **Toggleable release automation** (`.github/workflows/release.yml`): off unless
  the repo `RELEASE_ENABLED` variable is set; on a `v*` tag it validates the tag ↔
  manifest version, cuts a GitHub release from this CHANGELOG, and npx-smoke-tests
  from a clean checkout.

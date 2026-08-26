# Verification ledger — make-skill

One row per shipped requirement, with the command that confirmed it and what that
command printed. A row sits at `never` until somebody has watched its check pass on the
**shipped** artifact — not on a branch, not in a plan.

This file exists because its absence read as zero exposure. `sshlg-skills` board row
**B-30** measured this repository returning 0 REQ rows and named the reading that
produces: *"an absent ledger and a clean one are indistinguishable from the number
alone."* An empty ledger and a clean one now differ.

**It starts at the shipped state, not at the repository's history.** The oldest section here
was confirmed against v0.18.1 as it stood on `main` and on npm at the time; nothing was
back-filled from a CHANGELOG entry, because a claim restated is not a claim verified. **Each
section names the artifact it was measured on, and that name is the section's date** — the
newest is v0.22.0, and `test/validate.py` refuses a ledger whose newest section is behind
the release the CHANGELOG carries (MS-03).

---

## Shipped state — v0.23.2 (2026-08-26)

Measured on the release-candidate tree before the tag exists.

| REQ | What ships | How it was confirmed | Confirmed |
|---|---|---|---|
| R-33 | The public contract, eval fixtures, and social-preview dimensions are checked in the same gate as the skill | `SKILL-CARD.md`; `python3 test/evals_validate.py`; `python3 test/evals_validate.py --self-test`; `python3 test/social_preview.py` | **planted** + **observed** |
| R-34 | Downstream repositories can pin the house auditor to an immutable revision | all member workflows use commit `991cbb415be3e856f05c974e631423df552883e3` and invoke `audit_skill.py --house` | **read** |

## Shipped state — v0.23.1 (2026-08-25)

Measured on the tree this release tags, at `44c22f5`, before the tag existed — which is the
only order available, since the tag cannot precede the commit that bumps to it.

| REQ | What shipped | How it was confirmed | Confirmed |
|---|---|---|---|
| R-31 | `test/residue.py` tags each workspace with the process group that made it, so the gate-wide scan answers for ONE run | the scan read the shared `$TMPDIR` by prefix and failed on two things that are not this run's leak: another session's trees, and a tree a FAILING case kept on purpose. Demonstrated on identical state — a planted foreign tree makes the old logic FAIL and the new suite pass while printing what it excluded | **planted** + **observed** |
| R-32 | The split is a pure function with fixtures in both directions | `strays_for_run()` — a foreign tree is not reported, a tree tagged with this run and unaccounted for still is, and `workspace()` is asserted to embed the tag so the two fixtures cannot pass against a tag no directory carries | **planted** |

## Shipped state — v0.23.0 (2026-08-20)

Measured on the tree this release tags, at `34d35ab`, before the tag existed — which is the
only order available, since the tag cannot precede the commit that bumps to it.

| REQ | What shipped | How it was confirmed | Confirmed |
|---|---|---|---|
| REQ-026 | The ledger can no longer say *unshipped* over a release commit | `check_the_ledger_matches_what_shipped` + four plants, each watched at **exit 1**; it refused the row documenting itself once, because only `*"…"*` counts as a citation to it | **planted** + **observed** |
| REQ-027 | The pile figure carries its measurement date and its split | recounted **2688 directories, 83.6 MB**, and split at the fix's commit time: **0** `planted/` and **0** `repo/` trees after it against **784 of 2592** plant-guard trees, so the scoped claim holds by timestamp rather than by two samples a minute apart | **observed** |
| REQ-028 | The MS-01 referral is discharged, and recorded as observed rather than claimed | `grep -c 'tempfile.mkdtemp()'` → **0** in all four repositories that shipped the identical fixture (`sshlg-skills` `b371301`, `seo-aeo-audit` `c859cba`, `agent-stack` porting `test/residue.py` from here) | **observed** |
| REQ-025 | *Not shipped.* `residue.report()` sees only what `workspace()` handed out, so a re-introduced bare `mkdtemp` prints *left nothing* over a live leak — watched happening in `agent-stack` before its port | the closing mechanism exists in `agent-stack`; bringing it back here is a code change this release did not make | **never** |

## Shipped state — v0.22.0 (MS-01, re-confirmed on the released artifact 2026-08-20)

**Shipped.** `@ssheleg/make-skill@0.22.0` on npm, tag `v0.22.0` released
2026-08-19T19:27:15Z, and `fc25f4a` — the release commit — is `HEAD`. Every row below was
**re-run against that artifact** on 2026-08-20, not promoted on the strength of having been
green on a working tree: `git archive v0.22.0` into a clean tree, then all four gate
commands —

| command | printed | exit |
|---|---|---|
| `python3 test/validate.py` | `PASS: make-skill structure valid (1 cursor rule(s))` · `residue: this run left nothing — 0 temp tree(s) created, 0 removed` | **0** |
| `python3 test/plant_guard_test.py` | `PASS: plant_guard — 9 cases` · `residue: … 8 created, 8 removed` | **0** |
| `python3 test/checker_parity_test.py` | `PASS: checker parity — 14 cases` · `residue: … 8 created, 8 removed` | **0** |
| `python3 test/residue_test.py` | `PASS: residue — 8 cases` · `residue: … 2 created, 2 removed` | **0** |

and the three `find` counts taken before and after that run were **identical**, with `0`
directories matching `make-skill-test-*` left behind. The shipped artifact leaks nothing.

**MS-03: until 2026-08-20 this section was headed *"Unshipped — `main` at `16a9682`, no
release cut"* and said *"the artifact on npm is still `0.21.0` and does not contain any of
it"*.** Both were true when written and false from the moment v0.22.0 was cut — which was
before this paragraph was ever re-read. Every row below still carries the status it was
measured with; what changed is the artifact they were re-confirmed against, and that is
recorded rather than back-filled.

Closes board row **MS-01** (`docs/evidence/backlog.md`), which arrived from the
Proof-of-Done conformance audit as requirement **M-49**: *a run produces more than a
diff, and Proof of Done records what remains.*

| REQ | Requirement | Verified by | Result | Status |
|---|---|---|---|---|
| 017 | Every temp tree the suites create is gone after a passing run | `python3 test/residue_test.py` — case 1 asserts the path itself no longer exists; two more run the real suites as processes in an isolated `$TMPDIR` and read the directory afterwards | `PASS: residue — 8 cases`; both suites leave `[]` in their own `TMPDIR`, where the pre-fix code left 8 entries each | **verified on v0.22.0** |
| 018 | The new assertions fail against the pre-fix code | `git stash push test/checker_parity_test.py test/plant_guard_test.py` then `python3 test/residue_test.py` | `FAIL: 2 of 8` — *"plant_guard_test left 8 entr(y\|ies) in its TMPDIR"* and the same for `checker_parity_test`; green again after `git stash pop` | **verified on v0.22.0** |
| 019 | A failing case keeps its tree, named, with its remedy | the same red run, reading its own residue line | `residue: 2 of 2 temp tree(s) KEPT`, each path followed by the case that owns it and a `rm -rf` naming both — the failure path demonstrating itself rather than being described | **verified on v0.22.0** |
| 020 | A crash that is not an `AssertionError` still reports and still keeps | `test/residue_test.py` case 4 — a child interpreter raises `RuntimeError` after taking a workspace | non-zero exit, the tree survives, `KEPT` printed: the report is wired to `atexit`, so no exit path skips it | **verified on v0.22.0** |
| 021 | Every gate command says what it left, `nothing` included | `npm test` | four `residue:` lines — `0 created, 0 removed` (validator), `8/8`, `8/8`, `2/2` — and exit `0` with `PASS` from all four commands, 9 + 14 + 8 cases | **verified on v0.22.0** |
| 022 | The pre-existing pile was counted and left alone | the three `find` commands quoted in `test/residue.py`'s docstring, run before the fix and again after | **1888 directories, 47.3 MB as sampled 2026-08-19** (60 `planted/`, 36 `repo/`, 1792 plant-guard trees). **MS-04: that is a dated sample, not a current state, and the two halves of it behave differently — see REQ-022a.** `0` trees carrying the `make-skill-test-` prefix remain | **verified on v0.22.0** |
| 022a | Which half of the pile this repository is answerable for, split by the fix's own commit timestamp | `find "$TMPDIR" … -newermt "$(git log -1 --format=%cI 16a9682)"`, i.e. after 2026-08-19T13:55:15+02:00, when the fix landed | **Recounted 2026-08-20: 2592 plant-guard trees (30.4 MB) + 60 `planted/` (0.6 MB) + 36 `repo/` copytrees (52.6 MB) = 2688 directories, 83.6 MB.** The split is the finding: **0** `planted/` dirs and **0** `repo/` copytrees were created after the fix — both frozen at 60 and 36 across every sample since — while **784 of the 2592** plant-guard trees were, none of them this repository's. Stronger than the *two samples a minute apart* REQ-023 rested on: a timestamp comparison, and running the whole shipped gate on 2026-08-20 moved all three counts by exactly **0** | **verified on v0.22.0** |
| 023 | The plant-guard trees are ambiguously owned, so they stay | `find` for `test/plant_guard_test.py` across the family, then `grep -c 'import residue'` and `grep -c 'tempfile.mkdtemp()'` in each | Four repositories shipped the identical fixture — this one, `sshlg-skills`, `agent-stack`, `seo-aeo-audit`, each `tempfile.mkdtemp()` at line 34 — so no plain `tmpXXXXXXXX` tree can be attributed to any one of them, and `manifesto.md:366` says ambiguously owned state is reported and left alone. **MS-02 is now closed across the family, and not by this repository** — see REQ-024 | **verified on v0.22.0** |
| 024 | MS-02, the referral: which repositories still leak | the same survey re-run 2026-08-20, plus `git log -1 --format='%cI %s'` on each fixing commit | **None. All four now route every temp tree through a `residue` ledger** — `grep -c 'import residue'` → 1 and `grep -c 'tempfile.mkdtemp()'` → 0 in every copy of `test/plant_guard_test.py` in the family. Closed by three different agents, not by this one: `sshlg-skills` at `b371301` (2026-08-20T01:11:45+02:00, *"the suites left 2536 temp trees on this machine and never said so"*), `seo-aeo-audit` at `c859cba` (2026-08-20T01:31:48+02:00), and `agent-stack` in this session's own AG-06 commit — which **ported** this repository's `test/residue.py` rather than reinventing it, and then found the hole the port leaves: a bare `mkdtemp` bypass still passes and still prints *left nothing*. See REQ-025 | **verified** |
| 025 | What the referral being closed does NOT close | read `agent-stack/test/validate.py` (`check_temp_trees_go_through_the_residue_ledger`) against this repository's `test/` | **`residue.report()` accounts only for trees `workspace()` handed out, so a bare `mkdtemp` anywhere in a suite is invisible and the ledger prints `left nothing`.** `agent-stack` closed that with a source check over its own `test/*.py`; **this repository has no such check**, so the property here rests on nobody re-introducing a bare `mkdtemp`. Board row **MS-05**, open | **never** |
| 026 | MS-03 has a guard, and it was watched refusing the exact state it closes | `check_the_ledger_matches_what_shipped` in `test/validate.py`, four plants run against a copy of this tree | All **exit 1**, each for its own reason: the section headed *"no release cut"* again → *"says 'no release cut' with no version beside it, and the CHANGELOG has released v0.22.0"*; the board back to *"local, unreleased"* → the same rule naming `backlog.md`; the newest `## Shipped state` lowered to v0.19.0 → *"the newest … section is v0.19.0 while v0.22.0 has shipped"*; and a section naming v9.9.9 → *"announces a release nobody cut"*. **`docs/evidence/` is exempt from the counted-claims sweep on purpose** — a past row may quote a past count — which is exactly how MS-03 survived, so the ledger has its own rule instead of being folded into that one. A `*"…"*` quotation is stripped before the rules run, or a row citing the sentence it replaced would be refused for recording the fix | **verified** |
| 027 | The four plants are in CI, and the documented group count still computes | added as cases to the existing *claims, budgets and runnable commands* step rather than as new steps, so `grep -c 'name: Negative self-test'` stays at **9** and `CONTRIBUTING.md:58-59`'s *"9 negative self-test groups"* (the claim wraps the line break) — a claim this validator itself compares — remains true. Each case asserts its own expected message, so a plant that starts failing for a different reason is caught. `python3 -c 'import yaml; yaml.safe_load(...)'` parses | **verified** |

**12 rows: 11 verified on the shipped artifact, 1 at `never`.** The one at `never` is REQ-025, and it is at `never` because the property it names has no check in this repository — not because nobody has run one.

### What these rows do not cover

- **The three sibling repositories — closed 2026-08-20, by other agents.** They leaked
  identically and were not this repository's to change; the referral is now discharged and
  REQ-024 names each fixing commit. Recorded rather than claimed as this row's work.
- **This repository has no check that a temp tree went through the ledger.** `agent-stack`
  added one while porting `residue.py` here, after watching the ledger print *left nothing*
  over a re-planted leak. Board row **MS-05**, and REQ-025 is at `never` for it.
- **CI.** The gate was run locally; `.github/workflows/validate.yml` was not touched and
  no run exists for this commit, because nothing was pushed.
- **The validator's own plants.** `test/validate.py` gained residue accounting and
  nothing else; whether each of its rules has been watched failing is a separate row
  (deferred as MS-02) and is not claimed here.

## Shipped state — v0.20.0

Released: `@ssheleg/make-skill@0.20.0` (npm), tag `v0.20.0` (**annotated**).
CI on the tag: `validate` and `release` both `completed success`, read after the
push rather than assumed from it.

| REQ | Requirement | Verified by | Result | Status |
|---|---|---|---|---|
| 011 | Both checkers measure a multi-line YAML description at its real length | planted a description whose real length is 1392 chars as a plain multi-line scalar; ran the shipped auditor | before: `DESC_LENGTH … is 180/1024 chars` **PASS**; after: `GAP DESC_LENGTH … is 1392 chars, the maximum is 1024` | **verified** |
| 012 | An inline flow sequence fires `TOOLS_TYPE` | same fixture with `allowed-tools: [Read, Write]` | before: 0 gaps on that field; after: `GAP TOOLS_TYPE` | **verified** |
| 013 | `--house` applies the 4750 body working limit | `test/checker_parity_test.py` cases 9-11 | `BODY_HEADROOM` fires past 4750, is silent inside it, and is absent without `--house` | **verified** |
| 014 | The drift guard compares every shared rule, not one | three planted divergences: a constant deleted, a value changed, a key-set entry removed | all three refused, including the exact one that shipped (`BODY_TARGET_TOKENS not found`) | **verified** |
| 015 | No shipped skill's verdict changed | re-audited all 24 family skills before and after | identical; the one apparent difference was a `__pycache__` this run had just created | **verified** |
| 016 | The new suite fails against the pre-fix code | `git stash` the two checkers, run `test/checker_parity_test.py` | **9 of 14 red**, green again on restore | **verified** |

## Shipped state — v0.18.1, `main` at `ba01f8f`

Released: `@ssheleg/make-skill@0.18.1` (npm), tag `v0.18.1`.
CI: run `31753479647`, `validate` → `completed success`, 0 failed steps.

| REQ | Requirement | Verified by | Result | Status |
|---|---|---|---|---|
| 001 | The structural validator passes on the shipped tree | `python3 test/validate.py` | `PASS: make-skill structure valid (1 cursor rule(s))` | **verified** |
| 002 | Every guard has been watched failing against a planted defect | CI run `31753479647`, step-level conclusions of every `Negative self-test` step | **9 of 9 `success`**, 0 failed steps in the run | **verified** |
| 003 | The plant guard sees mode as well as content | `python3 test/plant_guard_test.py` | `PASS: plant_guard — 9 cases`, the first being the `chmod`-only incident that named the file | **verified** |
| 004 | The bundled auditor is clean on this repository's own skill | `python3 plugins/make-skill/skills/make-skill/scripts/audit_skill.py plugins/make-skill/skills/make-skill` | `0 GAP, 10 PASS`; body 313 lines / ~4742 tokens against a 500 / 5000 budget | **verified** |
| 005 | Version is synchronised across every surface | read back from `package.json`, `.claude-plugin/marketplace.json`, `plugins/make-skill/.claude-plugin/plugin.json`, the top `## vX.Y.Z` in `CHANGELOG.md` | all four → `0.18.1` | **verified** |
| 006 | A release cannot publish over a red suite | `grep -c workflow_call .github/workflows/validate.yml`; `grep -n` in `release.yml` | `workflow_call` 1; `uses: ./.github/workflows/validate.yml` at line 30, `needs: validate` at line 33 | **verified** |
| 007 | Both workflows are parseable by the parser GitHub uses | `yaml.safe_load` over `validate.yml` and `release.yml` | both parse | **verified** |
| 008 | The installer identifies itself and its version | `node bin/make-skill.js --help` | `make-skill installer v0.18.1` — the same number as the four surfaces above | **verified** |
| 009 | npm serves exactly the version this tree claims | `npm view @ssheleg/make-skill version` | `0.18.1` | **verified** |
| 010 | The tag exists at the released version | `git tag --sort=-v:refname \| head -2` | `v0.18.1`, `v0.18.0` — newest tag matches the shipped version | **verified** |

## What these checks do not cover

Named rather than left to be inferred, because a ledger that lists only its successes
reads as coverage it does not have.

- **The skill's advice, as advice.** Every row above is about the *artifact* — that it
  is structurally valid, budgeted, linked and released. Nothing here measures whether
  the doctrine in `SKILL.md` produces a better skill when an agent follows it. The
  repository has no behavioural eval suite; `task-pipeline` has one and this does not.
- **The installer's effect on a real `~/.claude`.** REQ-008 reads its banner. CI runs
  the fresh / rerun-skip / `--force` paths against a fake `HOME`; that is exercised
  there and not re-confirmed here.
- **The nine negatives, one by one, locally.** REQ-002 reads their step conclusions from
  the CI run rather than re-running each. That is the honest description of what was
  looked at: a run's verdict, not nine local reproductions.

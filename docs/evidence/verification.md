# Verification ledger — make-skill

One row per shipped requirement, with the command that confirmed it and what that
command printed. A row sits at `never` until somebody has watched its check pass on the
**shipped** artifact — not on a branch, not in a plan.

This file exists because its absence read as zero exposure. `sshlg-skills` board row
**B-30** measured this repository returning 0 REQ rows and named the reading that
produces: *"an absent ledger and a clean one are indistinguishable from the number
alone."* An empty ledger and a clean one now differ.

**It starts at the shipped state, not at the repository's history.** Every row below was
confirmed against v0.18.1 as it stands on `main` and on npm; nothing was back-filled
from a CHANGELOG entry, because a claim restated is not a claim verified.

---

## Unshipped — `main` at `16a9682`, no release cut

**These rows are deliberately not `verified`, and the distinction is this file's whole
point.** Nothing was published, tagged or version-bumped for this change: the artifact on
npm is still `0.21.0` and does not contain any of it. Every row below was watched on the
working tree at `16a9682` and says so. When it ships, each moves into a `## Shipped state`
section re-confirmed against the released artifact — not promoted on the strength of
having been green here.

Closes board row **MS-01** (`docs/evidence/backlog.md`), which arrived from the
Proof-of-Done conformance audit as requirement **M-49**: *a run produces more than a
diff, and Proof of Done records what remains.*

| REQ | Requirement | Verified by | Result | Status |
|---|---|---|---|---|
| 017 | Every temp tree the suites create is gone after a passing run | `python3 test/residue_test.py` — case 1 asserts the path itself no longer exists; two more run the real suites as processes in an isolated `$TMPDIR` and read the directory afterwards | `PASS: residue — 8 cases`; both suites leave `[]` in their own `TMPDIR`, where the pre-fix code left 8 entries each | **verified locally, unshipped** |
| 018 | The new assertions fail against the pre-fix code | `git stash push test/checker_parity_test.py test/plant_guard_test.py` then `python3 test/residue_test.py` | `FAIL: 2 of 8` — *"plant_guard_test left 8 entr(y\|ies) in its TMPDIR"* and the same for `checker_parity_test`; green again after `git stash pop` | **verified locally, unshipped** |
| 019 | A failing case keeps its tree, named, with its remedy | the same red run, reading its own residue line | `residue: 2 of 2 temp tree(s) KEPT`, each path followed by the case that owns it and a `rm -rf` naming both — the failure path demonstrating itself rather than being described | **verified locally, unshipped** |
| 020 | A crash that is not an `AssertionError` still reports and still keeps | `test/residue_test.py` case 4 — a child interpreter raises `RuntimeError` after taking a workspace | non-zero exit, the tree survives, `KEPT` printed: the report is wired to `atexit`, so no exit path skips it | **verified locally, unshipped** |
| 021 | Every gate command says what it left, `nothing` included | `npm test` | four `residue:` lines — `0 created, 0 removed` (validator), `8/8`, `8/8`, `2/2` — and exit `0` with `PASS` from all four commands, 9 + 14 + 8 cases | **verified locally, unshipped** |
| 022 | The pre-existing pile was counted and left alone | the three `find` commands quoted in `test/residue.py`'s docstring, run before the fix and again after | **1888 abandoned directories, 47.3 MB** (60 `planted/`, 36 `repo/`, 1792 plant-guard trees); unchanged by anything this repository ran after the fix, and `0` trees carrying the new `make-skill-test-` prefix remain. It did keep growing — see REQ-023 — which is the evidence that the 1792 are not ours to sweep | **verified locally, unshipped** |
| 023 | 1792 of those 1888 are ambiguously owned, so they stay | `grep -rl 'sub/b.sh' --include='*.py'` across the family; two counts a minute apart | four repositories ship the identical fixture — this one, `sshlg-skills`, `agent-stack`, `seo-aeo-audit`, each `tempfile.mkdtemp()` at line 34 — and the pile grew **1792 → 1800 → 1808** across three samples minutes apart, from siblings' runs, while this repository's own two counts stayed frozen at **60** and **36** — which is both the proof that the fix holds and the reason the rest is not ours to delete. `manifesto.md:366`: ambiguously owned state is reported and left alone | **verified locally, unshipped** |

### What these rows do not cover

- **The three sibling repositories.** They leak identically and are not this
  repository's to change. Referred to the `sshlg-skills` board rather than fixed here.
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

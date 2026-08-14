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

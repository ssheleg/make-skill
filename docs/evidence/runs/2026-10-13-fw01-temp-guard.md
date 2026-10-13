<sub>ssheleg skills — skill-search · task-pipeline · agent-sync · evidence-docs</sub>

# FW01: whole-repository temporary-tree source guard

Base: [b4418bc](https://github.com/ssheleg/make-skill/commit/b4418bc48e4654bf983db69705e6789d314ec431).
Task source: hub completion FW01; referring agent-stack B-159/B-160. Reference inspected:
[agent-stack cb8f699, test/validate.py](https://github.com/ssheleg/agent-stack/blob/cb8f6993a61473f3974bc3af67925439ed4abb75/test/validate.py).
This is the make-skill half; the independent SEO snapshot change is
[seo-aeo-audit a045893](https://github.com/ssheleg/seo-aeo-audit/commit/a0458937317a68b94d7b2badcffa205232aac6d7).

## What changed

`test/validate.py` now scans repository Python sources, including shipped scripts and
helpers outside `test/`. `TEMP_SCAN_SKIP_DIRS` names the dependency, generated and fixture
directories omitted from that scan. Its sole current exception is exactly
`test/residue.py`, exactly one maker, matching the attributed allocation call's prefix
and suffix. Adding another call or changing this form fails. An absent exempt file also
fails. There is no blanket file exemption. A new shipped-tool exception requires a
reviewed cleanup contract and implementation of its permitted shape.

This is source lint, not runtime allocation proof. The retained lexical matcher catches
unqualified and one-receiver direct maker calls and one-line aliased from-imports. It
misses chained receivers, stored function references, getattr, parenthesised multiline
renaming imports and lexical quote-marker concealment. JS/shell and excluded directories
are not scanned. The call-shape assertion does not verify ledger append/atexit logic;
`test/residue_test.py` exercises that behavior. No global “zero untracked trees” claim is
made from this guard alone.

## Red/green evidence

`python3 -B test/audit_regressions/fw01_temp_guard.py`: on the base, the first four
negative cases failed because the guard accepted their plants; three counterexamples
passed. Plants: aliased maker in a shipped plugin script, unregistered snapshot under
`scripts/`, an extra maker in the ledger, and the existing maker with an anonymous
prefix. After the fix all seven passed. A final eighth case executes the whole public
validator in a source-only copy: an outside-test module-alias plant produces exit 1 and
names its path; removing it produces exit 0. Final result: 8/8, exit 0, eight owned
fixture trees created and removed. The existing `npm run test:audit` glob includes it.

`python3 -B test/validate.py`: exit 0. Parent routed-trigger check explicitly unlooked in
this standalone worktree. `python3 -B test/residue_test.py`: exit 0, 11 cases, including
passing cleanup, retained failure/crash evidence and real plant/parity suites. These
are local fixture checks; full owner/release suite NOT_RUN in this bounded pass and
belongs to the parent aggregate schedule. No skill payload/version/install/model claim.

## Handoff

Next: independent review of scan/exemption coverage and residual bounds, then parent
integration, aggregate checks and source-owner reconciliation of the referral rows.
No referral row is closed and no package release is made here. Exclusive local ownership
was claimed as FW01-TEMP-GUARD; the configured lease is advisory across machines and the
tool reports this project UNGATED.

## Independent review

Reviewer: `fresh_research`, independent of this implementation. **Bounded PASS** at
[`eb978ea72b4fb6977059569bb0688ea832af37dc`](https://github.com/ssheleg/make-skill/commit/eb978ea72b4fb6977059569bb0688ea832af37dc).
Read `AGENTS.md` and its required `docs/HANDOFF.md`; the worktree was clean before
and after verification. No model evaluation or release was attempted.

Replayed `python3 -B test/audit_regressions/fw01_temp_guard.py`: 8/8 passed,
exit 0, eight owned fixture trees removed. Its public-validator plant/removal case
confirms the source guard is called by the actual entry point. No complete owner
suite was run by this reviewer.

An additional independent harness extracted the actual `TEMP_*` constants and
guard function definitions through Python AST, then executed them against seven
isolated tiny source trees. All seven matched their expected result:

| Control | Observed result |
|---|---|
| Missing `test/residue.py`, with another test Python source present | Refused absent exception |
| Copy of the ledger under `scripts/residue.py` | Refused; basename does not confer exemption |
| Shipped plugin script using `tempfile.TemporaryDirectory()` as a context manager | Refused; a cleanup contract requires an explicit reviewed exception |
| Outside-test `from tempfile import TemporaryDirectory as scratch` | Refused |
| Original ledger maker with an anonymous suffix | Refused changed attributed shape |
| Outside-test code calling `residue.workspace()` | Accepted |
| Direct maker under documented `dist/` exclusion | Accepted as excluded, not certified safe |

The harness removed only its owned outer fixture directory. `git diff --check`
passed and no source bytes changed. The AST harness checks guard behavior, not
runtime allocation or Python-language completeness. The receipt's lexical,
language and directory exclusions remain material; this is not proof that every
possible temporary tree is accounted for. No remaining reproduced blocker was
found within the declared source-lint contract. Parent integration, broader owner
gates and referral-board reconciliation remain separate.

---

**Made with [ssheleg skills](https://github.com/ssheleg/sshlg-skills)**

- `skill-search` — selected the route.
- `task-pipeline` — bounded repository change.
- `agent-sync` — checked ownership and held the validator lease.
- `evidence-docs` — recorded observed negative and positive evidence.

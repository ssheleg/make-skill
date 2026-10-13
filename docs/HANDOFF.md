# Current evidence update — skill-search native loading, 2026-10-13

The skill-search corpus now has a completed, independently replayed native-loading
run against frozen v0.31.2 source. Its 20 query majorities passed; individual cells
matched 59/60, with s09/repetition0 retained as the miss. This supersedes the older
"never run against a model" prerequisite below only for native Skill loading.
Read the [dated receipt](evidence/runs/2026-10-13-skill-search-native/README.md)
and [appended eval result](../test/evals/RESULTS.md#skill-search-native-loading-2026-10-13)
for protocol errors, limits, independent proof and costs. The older packaging and
evaluation sections remain historical; this docs change makes no publication claim.

Next: normal docs PR checks and integration, then an outcome-grounded evaluation of
actual catalogue execution and task quality. Neither is proven by native loading.
No skill body, description, version or published payload is changed here.

---

# FW01 release packaging — 2026-10-13

Branch `release/fw01-0.31.2` prepares patch 0.31.2 from accepted source
`712d960b0bad66347570dc00650b1ea12bf94664` (PR35). Genuine validation
[38335197073](https://github.com/ssheleg/make-skill/actions/runs/38335197073)
passed at candidate `93263410b6608beaf1d618528e8e80ae313a59ad` before normal merge.
Independent review and local gates: [FW01 receipt](evidence/runs/2026-10-13-fw01-temp-guard.md).
Registry `@ssheleg/make-skill` and remote tags read 0.31.1 before this preparation.
This branch changes version metadata, card and release documentation only.

Packaging validator passed: `python3 test/validate.py`, exit 0.
Independent packaging review passed at `dabc1febfa660226c88356df9594c342c6190a5a`: metadata
and release documentation only; no implementation or workflow changes.
Next: frozen PR promotion,
normal merge, exact-source checks, then an annotated tag under the existing
release workflow. No tag, publication, hub pin or installed update has occurred.
The skill-search model-eval prerequisite remains separate and open.

---

# FW01 temporary-tree guard follow-up, 2026-10-13

Objective: close the source-scan omissions referred by agent-stack B-159/B-160.
The bounded implementation is complete on this branch: repository-wide Python scan,
exact-path/count/call-shape ledger exception and eight regression cases. Read the
[receipt](evidence/runs/2026-10-13-fw01-temp-guard.md) for checked commands, lexical
limitations, companion SEO revision and prerequisites. Exact next task: independent
review, then parent-owned integration and aggregate checks. No release, model eval or
referral-board closure is claimed. The previous skill-search model-eval gate remains.

# Current task: v0.31.1 patch, then packet W4-C

**v0.31.0 is published.** Annotated tag `v0.31.0` → `5556e8877233b1f0b92ee4e0b69533358cfc0047`
(squash of PR #33); release run [38241946211](https://github.com/ssheleg/make-skill/actions/runs/38241946211)
started 2026-10-12T11:19Z, conclusion success; npm `@ssheleg/make-skill` serves `0.31.0` as
`latest`; the hub ssheleg/sshlg-skills pins `skills/make-skill` at `5556e88` since its release
1.57.0. Evidence: the *Publication, live* row of the v0.31.0 section of
[verification.md](evidence/verification.md).

**v0.31.1 (branch `fix/0311`, PR open, not merged, tagged or published).**
- The missing-back-link message in `test/validate.py` now says how the routing runs: only
  `creating-fabric-agents` routes packaging here; this skill names the three builders and
  `handling-secrets` in return. An in-gate self-test refuses the old wording (watched failing).
- CHANGELOG v0.31.1 corrects v0.31.0's MS-05 wording to what `temp_maker_hit()` sees: a direct
  call through one receiver or none, a one-line renaming from-import; only whole-line `#`
  comments and `"""` blocks skipped; chained receivers, function references, `getattr` and
  parenthesised multi-line imports not seen.
- Evidence: the v0.31.1 section of [verification.md](evidence/verification.md).

**Open.**
- The skill-search evals are authored and structurally validated, **never run against a model**.
- v0.31.1 release (merge, tag, publish, hub re-pin) belongs to the orchestrator.
- `test/installer_test.js` makes temp homes with its own ledger (JS); the check reads `*.py` only.

**Next task, exactly (single).** Packet W4-C: run `test/evals/skill-search/triggers.json` against a
model, three fresh-session probes per query, and record the result in `test/evals/RESULTS.md`.
Scoring rule for s19: the case passes on whether a catalogue search ran, not on which skill it
named. **Gated:** the Sonnet weekly limit resets 2026-10-16; do not start W4-C before then.

# Previous task: integration wave 4, packet W4-B (v0.31.0, published)

**Objective.** Close the make-skill residue of the hub's integration waves
(`docs/evidence/plans/2026-10-11-integration-waves.md` § Wave 4 in ssheleg/sshlg-skills; REQ R25, R27
authoring part, R28, R29). Branch `w4/residue-evals`, from origin/main `60ca8e2` (v0.30.1).

**Done** (evidence: the v0.31.0 section of [verification.md](evidence/verification.md)).
- MS-05 / R28: `test/validate.py` refuses a bare temp-dir call anywhere under `test/`; it first
  failed on six real bypasses in `test/audit_regressions/`, which now use `residue.workspace()`;
  a planted bare call was refused by line. Board row MS-05 closed; the v0.22.0 row 025 `never` is
  answered by it.
- R25: `references/mcp.md` links `fabric-agent-adapter:{creating-fabric-agents,
  adapting-projects-to-fabric, building-fabric-services}` and `observatory-log:handling-secrets`;
  gate check with a watched plant.
- B-147 / R27 authoring: `test/evals/skill-search/triggers.json` (20 queries, en + ru, both
  classes), validated by `test/evals_validate.py`, which is now part of `npm test`.
- R29: this section.

**Open.**
- The skill-search evals are authored and structurally validated, **never run against a model**.
- The release was not done by this packet; it has since happened (PR #33 merged, tag v0.31.0,
  npm 0.31.0, hub pin in 1.57.0 — see the current task above).
- `test/installer_test.js` makes temp homes with its own ledger (JS); the new check reads `*.py` only.

**Checks run.** `npm test` exit 0 and `claude plugin validate ./plugins/make-skill --strict`
(see verification.md for the lines).

**Next task at the time** (superseded by the current task above): packet W4-C, then the
orchestrator's v0.31.0 release steps, which are now done.

# Previous task: family round 2026-10-10 (v0.30.0, v0.30.1)


Branch `fix/family-round-1010`: new `skill-search` skill (REQ-4), Claude Code plugin
reference verified against 2.1.296 (REQ-9), `/skill-audit` empty-argument text, and
the annotated-tag gate in `release.yml` (REQ-6). Evidence: the v0.30.0 section of
[verification.md](evidence/verification.md). Plan and REQ table live in the hub
(ssheleg/sshlg-skills `docs/evidence/plans/2026-10-10-family-round.md`).
Released 2026-10-10: PR #29 squash `22be26d8d1f5594b23a897caecd5ad7cfda7a86e`, annotated
tag `v0.30.0`, release run 38076672521 green, npm serves 0.30.0 with the tag's bytes
([receipt](evidence/releases/2026-10-10-make-skill-0.30.0/registry.json)).
Next: the hub re-pins make-skill 0.30.0 and counts `skill-search` in its inventory.
Owed: trigger evals for `skill-search` (none written; the hub's `toolkit --find`
fixtures are its only behavioural check so far).

# Previous task: host compatibility

See [HC-4 authoring correction and release receipt](evidence/host-compat/README.md).
Version 0.29.2 is published at `c0fe080a46dd2a98fa78d7cd1aee26fb0261d25c`.
Next: hub HC-6 parent pins and installed readback; model acceptance remains separate.
Historical audit follows.

# Sherlock family audit: handoff

Current bounded follow-up: [SC-3 multiline plain YAML auditor correction and release receipts](evidence/handoffs/2026-10-09-multiline-plain-yaml.md).
PR #25 was squash-merged at `2f5a1ad24c2145bcb72c601b3bd899f942a3acca`
and released as v0.29.1. The handoff distinguishes source, workflow, registry
and installation evidence and names the remaining cross-channel work.

This branch contains the prepared make-skill instruction changes from the family
audit. The runtime backlog has not been implemented or released.

Start with the [central handoff](https://github.com/ssheleg/sshlg-skills/blob/codex/sherlock-audit-handoff-20260907/docs/HANDOFF.md).
It links the 139 parent outcomes, 254 bounded task packets, module contracts,
source provenance, execution order and all member branch revisions.

Read the central repository manifest before choosing a task. Filter the plan by
this repository's module, then read one leaf and its prerequisites. Refresh source
hashes against the chosen checkout and materialize predecessor outputs before
editing. A prepared instruction is not evidence that an agent outcome improved.

Validation receipts for these instruction changes are in the central bundle.
Commit and push each completed task with its updated context and checks; leave a
new entry point for the following agent. Follow the [standing handoff rule](https://github.com/ssheleg/sshlg-skills/blob/codex/sherlock-audit-handoff-20260907/docs/working-rules/repository-handoff.md).

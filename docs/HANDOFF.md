# Current task: integration wave 4, packet W4-B (v0.31.0 candidate)

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
- The release: no PR merge, tag or publish was done by this packet.
- `test/installer_test.js` makes temp homes with its own ledger (JS); the new check reads `*.py` only.

**Checks run.** `npm test` exit 0 and `claude plugin validate ./plugins/make-skill --strict`
(see verification.md for the lines).

**Next task, exactly.** (1) Packet W4-C runs the `skill-search` trigger evals against a model and
records the result in `test/evals/RESULTS.md`. (2) After the PR merges and the release run is green,
the tag is pushed and the hub re-pins make-skill 0.31.0 in wave 5.

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

## v0.33.1: the family member gate (2026-10-24)

- **Done.** the family member gate: the family member gate (`test/family_gate.py`, with its shared-mechanism
  declaration) and the documentation merged since v0.33.0, released.
- **Next task.** After merge: tag `v0.33.1`, watch the release, then the sshlg-skills pin bump; then
  the highest open board row.

## 0.33.0 pinned (2026-10-22)

- **State.** The hub re-pinned make-skill 0.33.0 (its HANDOFF task) and its ratchets; installed on the operator machine.
- **Next task.** Board empty. Next work comes from the operator's planning.

# Description budget: v0.33.0, 2026-10-20

Objective: stop family skills crowding Claude Code's skill listing. Measured on the
operator's machine 2026-10-20: the listing budget is about 30,000 chars; this
session's listing was 29,995 chars for 134 skills and 81 showed no description.
Family descriptions sat at 870-965 chars because the old rule (970 of 1024) read as
a target. Plugin skills cannot be hidden with `skillOverrides`.

Done on `feat/description-budget`: the description is a router, not a manual (one
"Use when" sentence, 4-8 EN/RU triggers, one "NOT for"; target 400, soft cap 500,
spec cap 1024), stated in `SKILL.md`, `references/authoring.md` (*The description
budget*), `agent-skills-spec.md`, `retrofit.md`, `claude-code-plugin.md`, the
template, the Cursor rule, `/skill-audit` and `skill-auditor`. `audit_skill.py
--house` emits `DESC_BUDGET` WARN past 500 (exit code unchanged); `test/validate.py`
WARNs past 500 for every shipped skill and fails only past 1024. Own descriptions:
make-skill 943 to 470, skill-search 540 to 397. Six new checker-parity cases.
Evidence: the v0.33.0 section of [verification.md](evidence/verification.md).

Decisions: make-skill stays at 470, above the 400 target, because the sshlg-skills
routing table requires its five EN/RU trigger pairs (`advertised_check.js`). The
check ID changed (`DESC_HEADROOM` retired, `DESC_BUDGET` new); no consumer outside
this repo reads it (grep of the hub, 2026-10-20). The ledger heading accepts a colon
as well as the em dash, so new sections follow the no-em-dash rule.

Open: the hub (ssheleg/sshlg-skills) still measures the old 970 limit in its
`description-total` and "reserve" ratchets (`test/validate.py`
`check_the_description_reserve_is_not_spent`, `test/route_coverage.js` `HOUSE`,
`test/audit_bundle.py`); those move when the hub re-pins this release, which is the
hub's task. The 2026-10-13 skill-search native-loading result was measured on the
old description; it is not evidence for the new text. Other members' descriptions
are theirs to trim on their own releases.

Release receipt, read back 2026-10-20: PR #42 squash-merged at
`7745e2c646c0642af8aa0796522867ba115a0f42` after its genuine `validate` run
[39368685229](https://github.com/ssheleg/make-skill/actions/runs/39368685229) passed
(validate, claude-plugin-validate, skills-cli-discovery, House skill audit). Annotated
tag `v0.33.0` on that commit; release run
[39368764122](https://github.com/ssheleg/make-skill/actions/runs/39368764122) success;
GitHub release v0.33.0 published; `npm view @ssheleg/make-skill` prints version
`0.33.0`, `latest: '0.33.0'`, gitHead `7745e2c`; the packed tarball carries
`DESC_SOFT_CAP = 500` and a 470-char make-skill description. Local install:
`npx --yes sshlg-skills@latest update` keeps the hub pin, so this machine still runs
make-skill 0.32.0 (`claude plugin list`) until the hub re-pins; the family updater
was not bypassed.

Next (hub's task, not this repo's): re-pin make-skill 0.33.0 in ssheleg/sshlg-skills,
re-base its description ratchets (`description-total`, the 970 "reserve",
`route_coverage.js` `HOUSE`, `audit_bundle.py`) on the 500 soft cap, then run the
family update so this machine installs 0.33.0.

Retro: a limit stated as "5% under the cap" was read as a target by every member,
and nothing measured the shared listing it was spending. State the budget a field
competes for, not only its own cap, and make the soft cap a WARN people see.

---

# FEED-SEO-1019 wave 6: v0.32.0, 2026-10-19

Objective: supply-chain checks in the "is this skill safe to install" doctrine,
a re-measured `claude plugin eval` note and the Codex `AGENTS.md` byte budget.
Done on `feat/feed-1019`: SC-1..SC-5 in `references/enterprise.md` with primary
sources; `audit_skill.py --supply-chain` with 14 regression cases
(`test/audit_regressions/sc-supply-chain.py`); the `claude plugin eval` paragraph
in `references/authoring.md` re-measured on Claude Code 2.1.299; the Codex section
in `references/distribution.md` plus a chain-size check in `test/validate.py`.
Evidence: the v0.32.0 section of [verification.md](evidence/verification.md).
Decisions: the supply-chain mode is opt-in, because this skill teaches installation
and its own references are full of taught `npx` lines; SC-4 (impersonation) stays
a manual comparison, because a table of known owners would be invented and go stale.
Open: no scored `claude plugin eval` run yet; migrating `test/evals/` to it is
the next eval task (no board id minted here; ids come from the hub board).
Next: release v0.32.0 (PR, merge, annotated tag, release run, npm readback, hub pin).

---

# FW01 source discovery correction — 2026-10-13

The [source packet and receipt](evidence/runs/2026-10-13-fw01-discovery/README.md)
records actual healthy/readable/unreadable baseline evidence and the bounded
permission-error fix. New focused controls pass; source payload and version stay
unchanged. Next: independent review, serialized owner aggregate and genuine normal
PR admission. No full-scan/runtime completeness, publication or installation claim.

---

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

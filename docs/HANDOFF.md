# Current task: host compatibility

See [HC-4 authoring correction](evidence/host-compat/README.md). Candidate 0.29.2;
source checks and release receipts belong there. Historical audit follows.

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

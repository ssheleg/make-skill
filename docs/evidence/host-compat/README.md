# Host compatibility correction — 2026-10-09

Scope: HC-4 authoring guidance, base 798fe0f. No runtime parser or installer changes.

The previous references contradicted the skill body's capability-detection rule.
This patch scopes Claude component schemas to that host, keeps portable procedures
inside the skill directory, and separates installer channels from runtime features.
Primary source links live beside each corrected claim in the shipped references.

## Validation probes

- `claude-validation-probe.json`: Claude Code 2.1.296 accepts the valid fixture,
  rejects a missing description under strict validation, and accepts an invented
  skill key. These three cases establish partial coverage, not a complete schema.
- `claude-validation-initial.json`: first fixture omitted manifest author, so every
  case failed on that unrelated warning. Retained as an invalid initial instrument;
  it is not counted as three negative checks.

## Delivery

Candidate 0.29.2; not yet released.

- Full `npm test` exited 0 on 2026-10-10 after the final payload edits. The
  existing matrix assertion was updated because it required the obsolete
  host-wide yes/no row; it now requires the capability contract and detection.
- Both `claude plugin validate ./plugins/make-skill --strict` and
  `claude plugin validate . --strict` exited 0 on Claude Code 2.1.296.
- Independent agent `/root/installer_targets` reproduced the fixture outcomes
  0/1/0 and reviewed the primary source claims. Its two requested corrections
  (Markdown substitution versus raw shell env; conditional account sync) were
  applied and re-reviewed ACCEPT. A stale contents heading was then corrected.
- `python3 test/validate.py` and `git diff --check` passed. No parser or installer
  behavior changed, and no every-host runtime acceptance is claimed.

Next: normal reviewed PR merge/tag, exact registry readback, then hub pin and
installed channels. Preserve the historical probes and their measurement scope.
The hub owns the cross-host source matrix and subsequent parent pin/readback.


## Published receipt — 2026-10-10

PR [#27](https://github.com/ssheleg/make-skill/pull/27) merged at
`c0fe080a46dd2a98fa78d7cd1aee26fb0261d25c`; v0.29.2 resolves to that commit.
[Release workflow 37997168633](https://github.com/ssheleg/make-skill/actions/runs/37997168633)
completed successfully. [Canonical registry readback](registry.json) verified
npm gitHead, SHA-512/SHA-1 integrity and every one of 32 published files against
that source. Independent reader `/root/host_contracts` performed the comparison.
The candidate statements above describe the pre-release check; this appended
receipt closes source and publication, not installed model execution.
Next owner: hub HC-6 pins, installed channels and native readback.

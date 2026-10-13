# FW01 source discovery completeness — make-skill

## Frozen packet and baseline

Owner source: [c6b0470](https://github.com/ssheleg/make-skill/commit/c6b047057559f8dd2fe12dec59e4a4bee374fac2).
Version remains 0.31.2; this packet changes owner validation and evidence only.
The [actual whole-validator baseline](baseline.json) executes `python3 -B test/validate.py`
in an immutable Git-source fixture: healthy exits 0, readable unauthorized maker exits
1, then its parent directory is made unreadable (OS PermissionError independently
confirmed) and the same validator exits 0. This proves a discovery omission, beyond
an extracted-helper observation. No complete owner suite or native runtime was run.

The upstream family finding is
[the bounded central receipt](https://github.com/ssheleg/sshlg-skills/blob/38b69b1d3c022f45e4ac3464c5b83f4b96047852/docs/evidence/completion-1013/fw01-discovery-followup.json).
SEO's same discovery seam was corrected at
[76d25cd](https://github.com/ssheleg/seo-aeo-audit/commit/76d25cd5c283bce7c4fdd25c7c42fee7038fe1b2).
Its lexical/exemption policy is not copied into this owner.

## Contract and acceptance

- Keep this owner's scanner predicate, skip directories, lexical matching and exact
  exemptions unchanged. Only discovery error handling is in scope.
- `os.walk` directory discovery failure must add an ordinary owner guard failure
  identifying relative source path and error class. It must not become an empty,
  apparently complete source set. Keep running readable checks to collect evidence.
- Existing unreadable source-file behavior already exits nonzero; no success claim
  or broad parser rewrite is introduced. Excluded dependency directories remain
  excluded, including when unreadable. No symlink traversal policy is changed.
- Add focused helper admission controls and actual whole-validator healthy,
  readable allocation, unreadable directory, and restoration controls. Confirm the
  permission plant actually fails under this user; root privilege must not produce
  a fake passing permission test. Restore permissions in finally; all fixtures go
  through the owner's residue ledger.
- Preserve versions and every published payload file. Verify npm pack path/digest
  equality against the accepted baseline. Independent peer review and normal PR
  admission follow; broader owner gate waits for the coordinator's serial slot.

Implementation is the next step. No scanner, runtime, board closure, publication
or installation is claimed by this source-first packet.

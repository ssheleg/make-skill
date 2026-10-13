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

## Implemented and focused verification

Only the scanner's `os.walk` call gained an error callback (relative path and error
class); the owner's lexical rules, exemptions and skip set are unchanged. The new
`test/audit_regressions/fw01_discovery.py` passes 9 controls: helper healthy,
permission refusal, restoration, excluded dependency and absent-root admission;
actual whole-validator healthy, readable unauthorized maker, unreadable directory,
and restoration. Permission tests explicitly prove OS denial and restore modes in
finally. Both owned fixture trees were removed after success.

Existing `fw01_temp_guard.py` also passes all 8 groups; its 8 owned fixtures were removed.

The [pack comparison](payload-parity.json) checks all 34 current npm payload
files (394,624 bytes) against accepted baseline Git blobs. Only test/docs
paths change; package selection and version are unchanged. Registry metadata confirms
that version exists; this is not a fresh immutable-tarball readback. No new release
or installed update is needed for this excluded validation/evidence source change.

## Independent review and owner aggregate

[Root's independent source acceptance](https://github.com/ssheleg/sshlg-skills/blob/85d1758e02cbf1759be861a7af2108d267c339a3/docs/evidence/completion-1013/fw01-sibling-peer.json) binds the implementation above
and independently replays all 9 controls. It accepts directory discovery refusal
within the documented scanner scope, without a filesystem race or symlink proof.

The exact implementation commit `75ab2d0ad03e231ce465fa5d3d95776e8be0c3f4` then passed the complete owner
`npm test` command, exit 0, in 22.08 seconds. The
[structured result](owner-full.json) binds source, command and log digest;
[full output](owner-full.log.gz) preserves every group. Minimum observed free
space was 1391476736 bytes. The watchdog would stop only this owned
process group below 300 MiB; it did not fire. Owned scratch/cache trees were removed.
No provider, native-host or model behavior was exercised.

Next: commit this documentation freeze, promote the existing draft PR once, and
require genuine eligible PR jobs before normal integration. Hosted checks and merge
remain pending; no release or installed update is needed for this excluded source.

# make-skill 0.29.1 release receipts

Source: `2f5a1ad24c2145bcb72c601b3bd899f942a3acca`, the squash merge of
[PR #25](https://github.com/ssheleg/make-skill/pull/25). Tag `v0.29.1` resolves
to that commit. The current entry point is the
[SC-3 handoff](../../handoffs/2026-10-09-multiline-plain-yaml.md#post-release-receipt--2026-10-09).

| Receipt | What was actually verified |
|---|---|
| [release.json](release.json) | Successful release workflow, exact head SHA, six successful jobs, public GitHub release metadata. |
| [registry.json](registry.json) | Exact npm version and `gitHead`; downloaded canonical tarball integrity; every one of its 32 files compared to `git show` at the release SHA. |
| [propagation-attempts.json](propagation-attempts.json) | Two failed canonical requests and subsequent successful exact verifier, one minute apart. Earlier ad hoc probes also failed; this file is the bounded polling receipt, not a count of every request made. |
| [http-diagnostics.json](http-diagnostics.json) | Later canonical, same-URL no-cache and separately labelled query-cachebuster probes; allowed cache headers, response sizes and SHA-256 hashes. The diagnostic URL did not replace canonical acceptance. |
| [native-codex.json](native-codex.json) | 25 installed native plugin files independently rehashed and compared to release Git files. Fresh registry observations come from the acceptance agent; new model execution after this upgrade is NOT_RUN. |

Registry verification used the hub's
[verify-registry.py at 97e9351](https://github.com/ssheleg/sshlg-skills/blob/97e9351b850695b1410dc168c1d091a9a0aa0fad/docs/evidence/context-research/verify-registry.py):

```sh
python3 <hub-checkout>/docs/evidence/context-research/verify-registry.py \
  <make-skill-checkout> @ssheleg/make-skill 0.29.1 \
  2f5a1ad24c2145bcb72c601b3bd899f942a3acca <receipt-output.json>
```

It first asserts the registry version and `gitHead`, then downloads the
metadata's canonical tarball URL, checks SHA-512 integrity, rejects unsafe tar
members, and compares each file against the release commit. It does not
extract the tarball onto the filesystem or modify installed skills.

Native tree SHA-256 hashes the UTF-8 encoding of
`json.dumps(relative_path_to_sha256, sort_keys=True)`, using Python's default
JSON separators. Relative paths and public package file hashes are retained;
machine paths, credentials, configuration contents and configuration hashes
are excluded from this public receipt.

These files attest to distinct stages. Publication success alone did not
establish registry availability: initial canonical tarball requests returned
404, then the unchanged verifier succeeded naturally. File equality and an
enabled native registry entry do not establish successful model behavior.
Shared plain/Claude installation receipts and the umbrella pin remain owned
by the central comprehensive delivery; they are not asserted here.

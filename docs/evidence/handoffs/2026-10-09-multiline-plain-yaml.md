# SC-3 multiline plain YAML: review handoff

## Objective and result

A description beginning on the line below `description:` previously became
an empty map in the auditor and produced `DESC_MISSING`. The parser now waits
for the indented content before deciding map versus scalar, measures the full
plain value, and preserves empty-line folding and comment boundaries. A field
using unsupported syntax receives `FM_SUBSET_UNSUPPORTED`; its field checks
are left unmeasured instead of manufacturing a missing-value verdict.

The [brief/spec](../specs/2026-10-09-multiline-plain-yaml.md) owns requirements
SC3-Y1 through SC3-Y5. Code and regression commit:
`dfa8d06759455d2b384cefe5a1e186df9338f8ea`. Review the
[auditor at that commit](https://github.com/ssheleg/make-skill/blob/dfa8d06759455d2b384cefe5a1e186df9338f8ea/plugins/make-skill/skills/make-skill/scripts/audit_skill.py)
and its [synthetic regression](https://github.com/ssheleg/make-skill/blob/dfa8d06759455d2b384cefe5a1e186df9338f8ea/test/audit_regressions/sc3-multiline-plain.py).

The same existing scalar finalizer now applies `_typed_scalar` to unquoted
top-level values as it already did to map values. This keeps a bare `false`
or `42` from passing a string-required description check. Quoted values remain
strings. The existing optional full-YAML parser remains an oracle; no runtime
dependency, installer change or generated copy was added. The parent then
requested 0.29.1 release metadata in the same PR after accepting the code review.

## Checks actually run

| Check | Receipt / limits |
|---|---|
| New regression against the base parser | Exit 1; six of the initial seven groups failed, including `{}` instead of the complete description and absent length checking. An additional block/quoted-hash guard was added during implementation. |
| `python3 test/audit_regressions/sc3-multiline-plain.py` | Exit 0; eight groups, zero failures; 39 temporary trees created and removed. |
| `python3 -S test/audit_regressions/sc3-multiline-plain.py` | Exit 0 without site packages. Stdlib assertions passed; optional PyYAML differential oracle explicitly NOT_RUN. |
| `npm test` | Exit 0 on the final code commit. Structure validator; plant guard (9 cases); checker parity (20); residue (11); installer (11); all audit regression scripts including this new one. These counts are separate suites, not a combined outcome-evaluation total. |
| `claude plugin validate ./plugins/make-skill --strict` | Exit 0, `Validation passed`. |
| `claude plugin validate . --strict` | Exit 0, `Validation passed`. |
| Read-only re-audit of the three census reproductions | `math-olympiad`, `vercel-composition-patterns` and `vercel-react-native-skills` each have no `DESC_MISSING`, `FM_YAML_CONFORMANCE` or `FM_SUBSET_UNSUPPORTED` finding with this parser. Other unrelated checks were not claimed fixed. |
| `git diff --check` | Exit 0. |

The regression uses the repository's residue ledger. The six task-owned
temporary trees retained by the two expected failing development runs were
removed after their console evidence was retained privately. No installed
skill or host configuration was edited. Hosted CI was not manually dispatched;
local passing checks are not a hosted CI result.

## Decisions, risks and next task

Independent reviewer `/root` accepted code commit
`dfa8d06759455d2b384cefe5a1e186df9338f8ea` on 2026-10-09. The reviewer read
the parser and regressions, executed all eight groups (39 temporary trees
removed), and independently re-audited the three installed reproductions
with no target findings. The review specifically accepted the per-field
unsupported-syntax GAP and verified that parser state resets between files.
This is the reviewer's reported judgment and executed-check receipt; it does
not claim hosted CI or deployment acceptance.

- The parser remains a deliberately bounded YAML subset. Anchors, aliases,
  tags and indented collections are reported unsupported in the new pending
  value path. This change makes no full-YAML support claim.
- An invalid continuation after a terminating comment does not get folded
  into a plausible description. The optional oracle also identifies malformed
  YAML when installed.
- No foreign skill content was changed merely to satisfy the auditor.
- The pre-release branch prepared 0.29.1 across the package, marketplace,
  plugin, skill metadata, skill card and changelog. The subsequent release and
  installation state is recorded below; the earlier branch did not publish.

That pre-release next task was completed by the parent; the post-release
receipt below is the current state. Rerun the census with the released auditor
rather than rewriting the immutable pre-fix snapshot.

## Post-release receipt — 2026-10-09

[PR #25](https://github.com/ssheleg/make-skill/pull/25) was squash-merged to
`2f5a1ad24c2145bcb72c601b3bd899f942a3acca`. The tag `v0.29.1` resolves
to that commit. The [GitHub release](https://github.com/ssheleg/make-skill/releases/tag/v0.29.1)
was published at 2026-10-09T13:51:04Z, without draft or prerelease status.

[Release workflow 37939691841](https://github.com/ssheleg/make-skill/actions/runs/37939691841)
completed successfully at the exact release SHA. Its six successful jobs cover
skills discovery, native plugin manifests, the house skill audit, repository
validation, release creation and npm publication. The independently queried
public metadata is retained in [release.json](../releases/2026-10-09-make-skill-0.29.1/release.json).

The canonical npm tarball became readable at the successful recorded probe,
2026-10-09T13:59:45Z. The [registry receipt](../releases/2026-10-09-make-skill-0.29.1/registry.json)
verifies exact version `@ssheleg/make-skill@0.29.1`, `gitHead` equal to the
release SHA, SHA-512 integrity, and all **32 tarball files** byte-for-byte
against that Git commit. No alternate URL was substituted for acceptance.

Earlier canonical requests returned 404. The recorded minute-spaced
[propagation attempts](../releases/2026-10-09-make-skill-0.29.1/propagation-attempts.json)
retain two failed requests and the successful verifier output. Later
[allowlisted HTTP diagnostics](../releases/2026-10-09-make-skill-0.29.1/http-diagnostics.json)
show canonical and same-URL no-cache requests returning 200 with a Cloudflare
cache HIT, and a separately labelled cache-busting diagnostic returning 200
with a MISS. All three response hashes are identical. The successful canonical
verification preceded the cache-busting diagnostic. Earlier failure headers
did not identify a cache age/status, so negative-cache versus origin propagation
is **unresolved**; temporary unavailability and natural recovery were observed.
No republish or workflow dispatch was performed by this receipt task.

The [native Codex receipt](../releases/2026-10-09-make-skill-0.29.1/native-codex.json)
records 25 installed plugin files matching the pinned release source. The
receipt writer independently rehashed each installed file and checked it
against `git show <release-sha>:plugins/make-skill/<file>`. The canonical tree
hash is `c57430bfd1f9c5bce14758bf43c7e1de4762a1147d93f962e81ef5a7485aa2a2`,
computed as SHA-256 of `json.dumps(relative_path_to_sha256, sort_keys=True)`.

The acceptance agent's fresh native registry receipt lists 566 entries, 537
enabled, with `make-skill:make-skill` enabled and the legacy plain entry
disabled. That registry result is attributed to the acceptance agent; the
filesystem equality was independently repeated by the receipt writer. A new
model execution testing this parser release is **NOT_RUN**. These statements
cover native Codex only, not every installed channel or every live session.

The remaining delivery is cross-channel installation and a new census against
the released auditor. The central comprehensive task owns that work and the
umbrella pin; this receipt-only branch changes no release metadata or installs.

Skills used: `task-pipeline` for the scoped brief, evidence and handoff;
`make-skill` for the dependency, conformance and release preparation rules;
`agent-sync` for task/resource claims on guarded metadata (local advisory,
UNGATED; no claim of enforcement across hosts).

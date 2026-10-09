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
- Version 0.29.1 is prepared across the package, marketplace, plugin, skill
  metadata, skill card and changelog. There is no tag, package release, global
  installation update or parent pin change from this implementer.

Next task: the parent checks the final metadata/head and performs the authorized
merge/tag/release if accepted. After a release, rerun the census with
the released auditor rather than rewriting the immutable pre-fix snapshot.

Skills used: `task-pipeline` for the scoped brief, evidence and handoff;
`make-skill` for the dependency, conformance and release preparation rules;
`agent-sync` for task/resource claims on guarded metadata (local advisory,
UNGATED; no claim of enforcement across hosts).

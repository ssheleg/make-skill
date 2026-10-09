# SC-3: distinguish multiline plain YAML from missing metadata

## Brief and authority

The comprehensive skills census reproduced `DESC_MISSING` for valid
descriptions whose plain scalar begins on the next indented line. Fix the
source-owned bundled auditor, preserve its dependency-free operation, verify
positive and negative cases, and leave an unmerged PR for independent review.
The operator's delegated brief authorizes implementation, commit and push;
merge, release and installed-copy edits are explicitly excluded. The inherited
model is unchanged. No unanswered intake question changes this bounded fix.

Base: `9b5af484c868d246dfc28fed83f7986e238b25f5`, fetched `origin/main`.
The original checkout was clean; an isolated worktree owns this change.

## Sources and contradictions

| Source | Evidence and use |
|---|---|
| `AGENTS.md`, `docs/HANDOFF.md` | Preserve a tracked handoff and the existing family-audit entry point. |
| `CONTRIBUTING.md` | Stdlib runtime, `npm test`, native manifest checks; no version bump required for a PR. |
| `plugins/make-skill/skills/make-skill/scripts/audit_skill.py` | `parse_frontmatter` classifies every empty header as a map; `_check_description` then calls the valid scalar missing. |
| `test/checker_parity_test.py`, `test/audit_regressions/fix-ms-02.0{1,2}.py` | Existing folding, typing, duplicate-key and optional-oracle contracts must remain intact. |
| [YAML 1.2.2 plain style](https://yaml.org/spec/1.2.2/#733-plain-style) | Plain values can span indented lines; line folding and comment boundaries constrain the value. Consulted 2026-10-09. |
| Private SC-2 census and synthetic reproducer | Three enabled installed skills reproduce the issue. No private inventory is copied into this public repository. |

Contradictions: the auditor's missing-description verdict contradicts the
installed full YAML parser. The bounded parser need not implement all YAML;
unsupported syntax must be reported as a parser limitation, not fabricated
missing metadata. Existing repository prose describes a bounded subset, so
this change extends only plain-scalar recognition and its diagnostic boundary.

## Scope, requirements and plan

Selected pipeline profile: brief/spec → regression baseline → implementation
and checks → independent review/PR handoff. Kernel fields are this scope,
the checks below, the source dependencies above, and the resume action below.
This is an internal parser repair with no new interface or visual flow.
No graph artifact or task-specific retrospective exists in this owner checkout;
the central comprehensive plan retains cross-repository execution state.

| Requirement | Acceptance |
|---|---|
| SC3-Y1 | An indented plain scalar beginning below `description:` is parsed and measured as the full string, including space folding, empty-line folding and comments outside the value. |
| SC3-Y2 | Absent/empty/non-string descriptions still fail; a long scalar still exceeds the length limit; duplicate metadata keys and ordinary maps remain checked. |
| SC3-Y3 | Unsupported constructs/continuation after a terminating comment report a parser limitation; no false `DESC_MISSING` and no token/type PASS for an unparsed value. No mandatory PyYAML dependency. |
| SC3-Y4 | Focused regression fails on the old parser and passes on the fix; existing `npm test` and native manifest validation run. Optional PyYAML differential checks explicitly skip if unavailable. |
| SC3-Y5 | Source, tests and handoff are committed/pushed for independent review. Version remains 0.29.0 until a separately authorized release. |

Order: add a self-contained synthetic regression; run it against the old
parser; implement pending-value recognition; run the focused regression and
existing suites; save exact receipts and create the PR. Tests use the existing
residue ledger. The plugin script is the shipped payload; no generated copy
or installer/template metadata changes are required.

## Resume

Implementation and verification pending. Next action: add and run the focused
multiline-plain regression against the base parser, then implement the fix.

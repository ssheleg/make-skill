# R30 owner board and release guard — make-skill candidate

Objective: make the actual owner validator reject malformed declarations and weakened release ancestry checks. Base `78d67651611f50e2af531ab04916e680c2a2680d`. Source of original board counterexamples: [hub audit at 37f2890](https://github.com/ssheleg/sshlg-skills/blob/37f289046e5ea5c013f2555fb05ce7ba4ad09124/docs/evidence/completion-1013/r30-owner-audit/README.md); retained owner slice: [baseline-board.json](baseline-board.json).

## Contract and source

`test/owner_board.py` and `test/owner_release.py` extract the reviewed board and release functions from agent-stack `792e3f6cb2e46517f0187066db55edc63ae7d12c:test/member_gates.py`. The board's one documented grammar extension permits historical lowercase hyphen suffixes (`AW-0906-desc`/`AW-0906-refusal`). ID declarations require an immediate matching separator, exact own-table width and unique identifiers across declared tables. References/fenced examples are not declarations. Missing/unreadable inputs refuse.

The release contract is bounded to the existing family YAML indentation and shell setup, not a general YAML/shell interpreter. The live release job needs an unconditional full-history checkout before a refusing ancestry guard. Quoted mapping keys, merge keys, duplicate mappings at guarded positions, altered setup, conditional/ignored guards and shallow checkout require review rather than passing through substring matches. Release workflow bytes themselves are unchanged.

## Measured evidence

[Two actual pre-change validator processes](baseline-release.json) each returned 0 after ancestry removal and after changing the full-history checkout to depth 1. These are independently planted defects, not inferred missing metadata. Each fixture restored `test/validate.py` and the board from its recorded base head while retaining the current owned test copy.

New temporary fixtures use the existing residue ledger. Six real validator-process cases pass. The adapter runs before the existing global structural checks; no package or workflow command changes are needed because the existing audit glob discovers these tests.

Focused parser/file controls: 25 board/adapter and 27 release controls pass. Release controls execute the workflow's own annotated-tag and ancestry shell in local Git repositories: current/ancestor annotated tags pass, missing/lightweight tags and an unmerged commit refuse. A real depth-one clone confirms the shallow fixture; the structural guard refuses the corresponding checkout depth. The only stand-in is `gh api` returning the fixture default branch, so this is local Git evidence, not hosted GitHub acceptance.

For the three sibling process suites, healthy and legitimate escaped-pipe rows pass; duplicate, shifted width, removed ancestry and shallow checkout refuse with intended diagnostics. Exact implementation/test hashes are [source-hashes.json](source-hashes.json). Full owner npm suite and final peer review are pending at this preparation point; later evidence must name its own source head. No provider/native behavior was exercised.

## Handoff and remaining work

Branch `fix/r30-owner-board-1013`. Next: independent diff review, one serial full owner gate using an owned temporary root, then normal frozen draft-to-ready PR admission. No package version, published payload, installed state, source release or hub pin is changed here. Original historical board states remain historical; this bounded candidate does not close every R30 requirement or every owner task. Local task/resource leases are advisory to this machine, not a cross-machine lock.

# Board — make-skill

What this repository knows it owes. A finding that arrives from outside — a
cross-repository audit, a sibling's incident — lands here with the id it arrived
under, so the row can be closed against the same name in both places.

**Priority is computed, not felt.** `P = blast × (1 + age_runs) / effort`, where
*blast* is who is hurt if it stays (3 = a user of the pack, 2 = the operator of
this machine, 1 = a future run of this repo), *age_runs* is how many **distinct
days** carrying a run stamp the row has survived, and *effort* is rough size
(1 = under an hour, 2 = a session, 3 = its own run). Recomputed when the row is
touched, never inherited, so a row cannot keep a rank it earned when it was new.

**Ids are not minted here.** `.claude/agent-sync.json` declares no id register —
`docs/AGENT_SYNC.md` says ids live in the parent repository. A row therefore
carries the id of whatever registered it: `B-nn` from the `sshlg-skills` board,
`M-nn` for a Proof-of-Done manifesto requirement, `MS-nn` for a row of the
cross-repository conformance program. Inventing a local scheme beside those is
how the same defect ends up closed twice under two names.

| id | What | Source | Blast | Age | Effort | P | Status |
|---|---|---|---|---|---|---|---|
| MS-01 | **The gate left 47.3 MB of temp state on the machine and never said a word about it.** `test/checker_parity_test.py:60,160` called `tempfile.mkdtemp()` to plant a defect into a copy of this whole repository and removed neither the copy nor the planted skill dir; `test/plant_guard_test.py:34` did the same per case. Measured under `$TMPDIR` on 2026-08-19: **60 `planted/` skill dirs and 36 `repo/` copytrees** unambiguously this repository's, plus **1792 plant-guard trees** whose fixture is byte-identical in four family repositories — **1888 abandoned directories, 47.3 MB**, over roughly 220 gate runs. The leak is the cheap half. The defect named by manifesto requirement **M-49** is that a completed run *recorded* nothing, so the next leak is invisible in exactly the same way: no test in the family printed what it left, and M-49 scored zero FULL across all nine members. | 2026-08-18 Proof-of-Done conformance audit, requirement M-49 | 2 | 0 | 1 | **2.0** | **closed 2026-08-19** — `16a9682`, local, unreleased. `test/residue.py` is the ledger every temp tree in this suite now goes through, and **every one of the four gate commands ends with one line naming its residue, `nothing` included** — that line, not the cleanup, is what makes the next leak show up in the gate's own output. A case that fails, or raises anything that is not an assertion, **keeps its workspace on purpose**: a planted defect is debugged by reading the tree it landed in, and a cleanup that runs only on the pass path deletes the evidence exactly when it is wanted; the report then names the path, the case that owns it, and the `rm -rf` that ends it. `test/residue_test.py` (8 cases) joins `npm test` last and was **watched failing 2 of 8** against the pre-fix suites, with the two e2e boxes kept — the failure path demonstrating itself. Workspaces now carry a `make-skill-test-` prefix, because the 1888 directories this closed are plain `tmpXXXXXXXX` and that namelessness is why they were never swept. **The 1888 were counted and left in place**, per `manifesto.md:366`: 1792 of them are indistinguishable between this repository, `sshlg-skills`, `agent-stack` and `seo-aeo-audit`, all four of which ship the same `tempfile.mkdtemp()` fixture at line 34 — the pile grew by 8 while it was being measured, from a sibling's run. **That referral is the open half and it is not this board's to close**: three sibling repositories leak identically and belong on the `sshlg-skills` board. |

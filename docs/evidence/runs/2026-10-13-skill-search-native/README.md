# Skill-search native loading — 2026-10-13

The frozen v0.31.2 plugin at `78d67651611f50e2af531ab04916e680c2a2680d` was observed through Claude Code 2.1.296 with init model `claude-opus-5-5`. This measures successful native `Skill` loads of `make-skill:skill-search`, not completion of its catalogue-search procedure or quality of a downstream task. The owner plugin files remain byte-identical to the evaluated source; `readback.json` names the exact file count and hashes.

## Measured result

Protocol C completed one readiness invocation and all 60 task cells: the fixed authored corpus has 20 query IDs, each run three times in a fresh CLI context. Per-query majority was 20/20; individual expected-load matches were 59/60. Positives matched 29/30 and negatives 30/30. Train matched 35/36 cells and 12/12 query majorities; validation matched 24/24 cells and 8/8 majorities. The sole miss is s09, repetition 0, recorded at index 24: no Skill load. No query, label, description or skill body was edited after observing it.

The startup inventory contained two user-invocable skill entries; the allowed Skill set also included the source-declared legacy `skill-audit` command. Inventory equality proves that startup field's contents, not every model-visible instruction. Only Skill was available in restricted sessions, so no shell-backed catalogue execution was exercised. The comparison does not establish task quality, family coexistence, installation coverage, cross-model reliability or description-compression adoption.

## Protocol history and cost

A stopped after one readiness call because the startup field did not list the legacy command. B passed readiness then stopped at its first task because the observer conflated the reported turn count with distinct model requests. Their original TEST_ERROR results remain in `results-a.json` and `results-b.json`; they were not retroactively scored. C was an explicitly reviewed new protocol: reported-turn ceiling 5, distinct-request ceiling 3, readiness ceiling 1, per-request input ceiling 24,000 and no automatic retries. Original queries, plugin bytes and labels were retained.

C reported USD 2.3410576 for 61 CLI invocations. Across A+B+C, 64 invocations reported USD 2.4620616 under the original USD 4 envelope. These are CLI list estimates, not subscription invoices. The independent reviewer made no model calls. Its replay verified all 61 raw-stream hashes, prompts, plugin manifests, private-file modes, delivered-text artifacts and usage totals; raw streams remain private outside Git. Maximum observed request input was 11,727 tokens. Costs from earlier unrelated pilots remain separately identified in the hub receipt.

## Durable sources and checks

The owner copies `results-c.json`, `peer-results-c.json`, `source.json` and `cases.json` are byte-identical to the hub artifacts identified by `readback.json`. Original hub [C result](https://github.com/ssheleg/sshlg-skills/blob/0d051b1f2b5cabd31781c5c795d98adba915e666/docs/evidence/completion-1013/skill-search-native/results-c.json) and [independent readback](https://github.com/ssheleg/sshlg-skills/blob/45ad0580f5db71132eaebd10cba4d4902bdeb080/docs/evidence/completion-1013/skill-search-native/peer-results-c.json) are commit-addressed. The independent protocol review is bound to runner `8bb0b83547fe4c64342bd750e65fc1c59ec50d16`; its offline corruption and compatibility controls preceded the admitted calls.

This packet adds evidence only. Historical make-skill evaluations and the frozen skill-search corpus retain their original observations. Owner structural/eval checks and npm payload parity are recorded separately before normal docs PR admission. No release, tag, installed description or skill implementation changes belong to this packet. Next: use this bounded loading result as a prerequisite for an outcome-grounded catalogue-search/task-quality evaluation; do not close those separate requirements from this receipt.

## Local owner checks

`local-checks.json` records exit 0 for `python3 test/validate.py`, `python3 test/evals_validate.py` and its `--self-test`. The validator's only executable change is a neutral structural-only stdout message; AST comparison after reversing that string is identical. Its acceptance rules are unchanged. Dry-run npm payload comparison found all 34 shipped files byte-identical to the owner base, so this evidence successor needs no package bump. Exact candidate hosted checks and normal merge remain the next admission boundary.

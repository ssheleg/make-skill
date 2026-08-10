---
description: "Audit a skill directory against the Agent Skills standard and Anthropic's platform rules — mechanical checks by script, judgement by the retrofit checklist"
argument-hint: "[path to a skill dir] [--house]"
---

Audit the skill at `$ARGUMENTS` (default: the skill directory in the current
working directory, or every `skills/*/` under `plugins/*/` if this is a plugin
repo).

1. Run the bundled auditor — it does the mechanical half deterministically. This
   plugin puts it on your PATH:

   ```bash
   make-skill-audit <skill-dir> --house
   ```

   No `python3`? The wrapper says so and exits 2. Record the mechanical items as
   **NOT-RUN with that reason** and check them by hand from the spec reference —
   never as PASS.

2. Then work the judgement half from
   `${CLAUDE_PLUGIN_ROOT}/skills/make-skill/references/retrofit.md` — one job,
   entry point, evaluations, distribution, repo meta. The script cannot answer
   those. Read the file; do not reconstruct it from memory.

3. Report one gap table: `PASS` / `GAP` / `NOT-RUN` per item, each with
   `file:line` or the command output that proves it. End with exactly ONE
   suggested next action.

Do not fix anything until the table is reported.

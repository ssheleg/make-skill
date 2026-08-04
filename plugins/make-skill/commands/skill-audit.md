---
description: "Audit a skill directory against the Agent Skills standard and Anthropic's platform rules — mechanical checks by script, judgement by the retrofit checklist"
argument-hint: "[path to a skill dir] [--house]"
---

Audit the skill at `$ARGUMENTS` (default: the skill directory in the current
working directory, or every `skills/*/` under `plugins/*/` if this is a plugin
repo).

1. Run the bundled auditor — it does the mechanical half deterministically:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/make-skill/scripts/audit_skill.py" <skill-dir> --house
   ```

   No `${CLAUDE_PLUGIN_ROOT}` (not running as a Claude Code plugin)? The script
   sits at `scripts/audit_skill.py` inside the skill directory you are reading
   this from — commonly `~/.agents/skills/make-skill/` or
   `~/.claude/skills/make-skill/`. No `python3` at all? Do the same checks by
   hand from `references/agent-skills-spec.md`; the checklist is the same one the
   script implements.

2. Then work the judgement half from
   `${CLAUDE_PLUGIN_ROOT}/skills/make-skill/references/retrofit.md` — one job,
   entry point, evaluations, distribution, repo meta. The script cannot answer
   those.

3. Report one gap table: `PASS` / `GAP` per item, each with `file:line` or the
   command output that proves it. End with exactly ONE suggested next action.

Do not fix anything until the table is reported.

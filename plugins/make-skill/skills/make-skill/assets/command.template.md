---
description: "One line the user sees in the / menu — what it does, not how it works"
argument-hint: "[what to pass] [--flag]"
---

<!--
Two rules this skeleton exists to enforce:

  1. NEVER name this file after a skill directory in the same plugin. Commands
     are skills now: `commands/x.md` beside `skills/x/` registers /x twice, the
     skill wins, and the command is unreachable always-on token cost.
  2. ALWAYS quote `argument-hint`. A bare [a | b] is a YAML flow sequence; one
     comma inside it drops the whole frontmatter block, leaving a command with
     no description and no warning.
-->

Do <the task> for `$ARGUMENTS`.

1. The deterministic part, by script:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/SKILL_NAME/scripts/SCRIPT.py" $ARGUMENTS
   ```

   Not running as a Claude Code plugin, so `${CLAUDE_PLUGIN_ROOT}` is unset? The
   script is in the skill directory this file was installed beside. No
   interpreter? Fall back to the manual procedure in the reference and say that
   you did.

2. The judgement part, from `references/FILE.md`.

3. Report: what was checked, what the verdict is, and ONE next action.

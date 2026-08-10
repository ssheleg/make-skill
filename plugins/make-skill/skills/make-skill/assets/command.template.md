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

1. The deterministic part, by script. Ship a wrapper in the plugin's `bin/`
   (Claude Code puts it on the Bash tool's PATH) and call it by name:

   ```bash
   PLUGIN_NAME-something $ARGUMENTS
   ```

   Do NOT build the command out of the plugin-root variable: it is substituted
   into this text but is NOT exported to the Bash tool's environment, so the
   command expands to a broken path. No interpreter? Fall back to the manual
   procedure in the reference and say that you did.

2. The judgement part, from `references/FILE.md`.

3. Report: what was checked, what the verdict is, and ONE next action.

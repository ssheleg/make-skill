# Host capabilities — hooks, agents, commands, and what happens without them

**Load this when:** deciding whether a skill should ship a hook, a subagent, a
command, an MCP server or a script — or when writing the degradation clauses that
keep it working where those do not exist.

Sources: [Claude Code hooks reference](https://code.claude.com/docs/en/hooks) and
the [plugins reference](https://code.claude.com/docs/en/plugins-reference)
(*read 2026-08-03, Claude Code 2.1.212*), plus `references/claude-code-plugin.md`
for the manifest side.

## Contents

- The rule: accelerator, never precondition
- What to reach for, and what it costs
- Hooks — events, handlers, matchers, exit codes
- Writing a hook that is invisible when idle
- Subagents
- Commands
- Scripts
- MCP servers and other plugins as dependencies
- The three degradation cases, written out
- Checklist

## The rule: accelerator, never precondition

Everything on this page exists only inside Claude Code. A skill that *needs* one
of them is broken on Cursor, Codex, the skills CLI, the Claude API and claude.ai
— which is most of where skills run. So:

> **Every host capability is an accelerator with a stated fallback. The skill
> must complete its job without it, more slowly and with less polish.**

"Stated" is the operative word: the fallback goes in the skill body, in the words
the agent will read at the moment the capability is missing. A fallback you know
but did not write is not a fallback.

## What to reach for, and what it costs

| Capability | Buys you | Costs | Reach for it when |
|---|---|---|---|
| `scripts/` | determinism, and output instead of code in context | none until run | the agent re-derives the same logic every run |
| `bin/` | a bundled script reachable **by name** — Claude Code puts it on the Bash tool's PATH | none until run | a documented command must work without a path variable (see *Scripts*) |
| `hooks/` | enforcement at the moment of the action | runs on the user's machine, every matching tool call | a rule matters more than an instruction can guarantee |
| `agents/` | a job done in a separate context window | ~100 always-on tokens per agent | the work would otherwise crowd out the main thread |
| `commands/` | a user-typed entry point with arguments | ~50–100 always-on tokens | a human, not the model, decides when it runs |
| `mcpServers` | live capability (network, credentials, a process) | a server to install, auth to hold | instructions cannot do it — see `references/mcp.md` |
| `lspServers`, `monitors`, `themes`, `outputStyles`, `workflows` | narrow, real, and rarely what a skill wants | always-on where they load | you can name the user who asked for it |
| `userConfig` | values prompted at enable time | a prompt in everyone's install | the skill genuinely cannot guess (a path, a workspace id) |

Everything in that table is Claude-Code-only. `scripts/` is the exception that
travels: it lives inside the skill directory, so every channel ships it.

## Hooks — events, handlers, matchers, exit codes

Plugin hooks live in `hooks/hooks.json` at the plugin root (auto-discovered; a
manifest key is only needed for a custom path). Shape:

```json
{ "hooks": { "PostToolUse": [ { "matcher": "Write|Edit",
    "hooks": [ { "type": "command", "shell": "bash",
                 "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/check.sh\"",
                 "timeout": 20 } ] } ] } }
```

**Events worth a skill's attention** (the full set is larger):

| Event | Fires | Blocks? | Use for |
|---|---|---|---|
| `SessionStart` | session begins/resumes (`startup\|resume\|clear\|compact\|fork`) | no | seeding state, `additionalContext` |
| `UserPromptSubmit` | before the model sees the prompt | yes | injecting context, refusing a prompt |
| `PreToolUse` | before a tool runs | yes — `permissionDecision: deny` | guarding a destructive action |
| `PostToolUse` | after a tool succeeds | no | validating what was just written |
| `Stop` / `SubagentStop` | a turn or subagent finishes | yes | completion gates |
| `SessionEnd` | session ends | no | cleanup (1.5s shared budget) |

**Handler types:** `command` (a script — the portable one), `http`, `mcp_tool`,
`prompt`, `agent`. `command` takes `shell` (`bash`/`powershell`) in shell form,
or `args` for exec form with no shell tokenization.

**Matchers** are exact strings or `A|B` lists; anything with other characters is
an unanchored regex. Tool names are what you match (`Bash`, `Write`,
`mcp__server__tool`). A plugin's OWN MCP server is matched as
`mcp__plugin_<plugin>_<server>__<tool>`, and an `mcp_tool` hook names the server
as `plugin:<plugin>:<server>` — the bare key never fires. Narrow further with
`if`, a permission rule: `"if": "Bash(git commit *)"`.

**Exit codes are the contract:**

| Exit | Meaning |
|---|---|
| `0` | success; stdout is parsed as JSON for structured output |
| `2` | blocking error; **stderr goes to the model**, stdout is ignored |
| other | non-blocking error; the action proceeds, the transcript shows a hook error |

Structured output on exit 0: `systemMessage` (shown to the user),
`additionalContext` (injected for the model), `decision: "block"` with `reason`,
`permissionDecision` for `PreToolUse`, `suppressOutput`, `continue: false`.

**Environment:** `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`,
`${CLAUDE_PROJECT_DIR}` substitute in the command and are exported. Quote them —
a space in the install path otherwise splits the command.

## Writing a hook that is invisible when idle

A plugin installed globally fires its hooks in every project. Two rules keep that
from being a nuisance, and both belong in the `description` field of
`hooks.json`, where a reviewer reads them:

1. **Exit 0 with no output the moment the event is not yours.** Wrong tool, wrong
   path, no project marker file → `exit 0` before doing any work. This is why
   `agent-sync`'s hooks open by checking for `.claude/agent-sync.json`.
2. **Degrade instead of erroring.** No interpreter, missing script, unparsable
   input → `exit 0` silently. A hook that reports its own absence as a failure
   trains the user to disable hooks.

Block (`exit 2`) only where blocking is the point, and only on `PreToolUse` or
another event that actually blocks. On `PostToolUse` the write already happened;
advice via `systemMessage` is worth more than a veto that costs a turn.

Ship the script with a shebang and `chmod +x`, and keep it dependency-free —
`jq` is not installed everywhere, and a hook is a bad place to discover that.

## Subagents

`agents/*.md` with `name` and `description`; optional `model`, `effort`,
`maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`,
`isolation: "worktree"`. **`hooks`, `mcpServers` and `permissionMode` are
rejected** for plugin-shipped agents. They appear as `<plugin>:<agent>`.

A subagent earns its always-on cost when the work is *voluminous and separable* —
an audit across twenty skills, a survey, a long verification — because its output
is a summary while its reading stays in its own context. It does not earn it when
the main thread needs the intermediate detail anyway.

Fallback: on any other host there are no subagents. The skill body must describe
the same procedure inline, so a Cursor session does the work in one context.

## Commands

`commands/*.md`, frontmatter `description` plus a **quoted** `argument-hint`;
body receives `$ARGUMENTS`. Two rules cost a debugging round each:

- **Never name a command after a skill in the same plugin.** Commands are skills
  now: both claim `/<name>`, the skill wins, the command is unreachable always-on
  cost visible only in `claude plugin details`. That is the default for every new
  plugin. **One recorded exception (operator decision, 2026-08-30): the ssheleg
  family ships same-named commands deliberately** — `task-pipeline`,
  `project-audit`, `seo-aeo-audit`, `sheleg-design`, `agent-sync`, and
  `super-ux`'s `vision`, `ux-foundation`, `ux-flows`, `ux-audit`. The cost is
  accepted, not waived: the skill wins the trigger, and each command stays an
  always-on token cost that may be unreachable in the picker. An audit that finds
  a collision on this list reports it as *deliberate, recorded — no change
  needed*; a collision NOT on a dated, recorded exception list is still the gap
  this rule names. A rule's exception is enumerated, dated, and carries its cost
  — never implied.
- **Quote `argument-hint`.** Bare `[a | b]` is a YAML flow sequence; a comma
  inside it drops the entire frontmatter block, leaving a command with no
  description and no warning.

Fallback: elsewhere there is no `/command`. The skill's own description must
carry the trigger phrases that reach the same behavior in plain language.

## Scripts

The one accelerator that travels. Keep it inside the skill directory
(`scripts/`), stdlib-only, and invoke it by a path the agent can actually
resolve.

**The trap that costs the most here: `${CLAUDE_PLUGIN_ROOT}` does not work in a
command you tell the agent to run.** It is substituted into skill, command and
agent *text*, and it is exported to *hook and monitor* processes — but it is
**not** in the Bash tool's environment. Measured on Claude Code 2.1.220:

```bash
$ echo "[${CLAUDE_PLUGIN_ROOT}]"
[]
$ python3 "${CLAUDE_PLUGIN_ROOT}/skills/x/scripts/x.py" .
python3: can't open file '/skills/x/scripts/x.py': [Errno 2] No such file or directory
```

That failure is expensive out of proportion to its size: the agent was told to
run a deterministic check, the check will not run, and reasoning through it
instead — then reporting the result as if it had run — is the cheapest way out.

**Ship a wrapper in the plugin's `bin/` instead.** Claude Code puts a plugin's
`bin/` on the Bash tool's PATH while the plugin is enabled, so the script
becomes reachable by name, with no variable in the command:

```bash
<plugin>-<verb> <target>          # Claude Code: bin/ is on PATH
```

Make the wrapper resolve its payload from **its own location** (`dirname "$0"`,
following symlinks), never from an environment variable — then it also works
copied, symlinked into an agents hub, or called by absolute path. Worked
example: this plugin's `bin/make-skill-audit`.

Everywhere else the absolute path differs per channel
(`~/.agents/skills/<skill>/`, `~/.claude/skills/<skill>/`), so the instruction
that survives is "run the script from the skill directory you just read this
file from". State the no-interpreter fallback too: the manual procedure, in the
reference that the script implements, and the items it leaves **NOT-RUN**.

## MCP servers and other plugins as dependencies

A skill may *use* an MCP server or a sibling skill; it may not *require* one
silently. Declare it in frontmatter `compatibility`, and write the branch:

- **Server present** → name the tool by discovery, never a hardcoded string
  (`references/mcp.md`).
- **Server absent** → say so once, name what is degraded, and continue with the
  manual path. Never loop on 401s; interactive auth is a human step.
- **Sibling skill absent** (`super-ux`, `agent-sync`, …) → the dependent stage
  still runs, with its quality reduced and that reduction stated. A pipeline that
  refuses to start because an optional companion is missing is a broken pipeline.

Claude Code's manifest `dependencies` field can express a hard requirement
between plugins. Use it only when the skill genuinely cannot function — and know
that it means nothing on any other host.

## The three degradation cases, written out

Put these in the skill body, in this shape:

```markdown
## Degradation

- **Not Claude Code** (Cursor, Codex, skills CLI, API): hooks, subagents and
  `/commands` do not exist. Run <procedure> inline; the bundled `scripts/` still
  work wherever `python3` does.
- **Recommended plugin absent** (<name>): <what is lost>. Continue with
  <manual path>, and say once that the result is <weaker in this way>.
- **Tool or interpreter absent** (`python3`, `gh`, `npm`, an MCP server): state
  it once, fall back to <the by-hand procedure>, never retry in a loop.
```

Three lines, one per axis. They are what a reader checks before installing, and
what the agent reads at the exact moment something is missing.

## Checklist

- [ ] Every host capability the skill ships has a written fallback in the body
- [ ] `hooks.json` `description` says when the hooks no-op
- [ ] Hook scripts exit 0 silently on "not mine" and on a missing interpreter
- [ ] `PostToolUse` advises (`systemMessage`), `PreToolUse` blocks — not the reverse
- [ ] Hook commands quote `"${CLAUDE_PLUGIN_ROOT}"` and set a `timeout`
- [ ] Hook scripts are executable, have a shebang, and need no `jq`
- [ ] No command named after a skill — or the collision is on a recorded, dated
      exception list (see *Commands*); every `argument-hint` quoted
- [ ] Plugin agents carry no `hooks` / `mcpServers` / `permissionMode`
- [ ] Scripts are stdlib-only, inside the skill dir, invoked by a resolvable path
- [ ] No command the agent is told to RUN contains `${CLAUDE_PLUGIN_ROOT}` — it is
      empty in the Bash tool; ship a `bin/` wrapper and call it by name
- [ ] MCP and sibling-skill dependencies declared in `compatibility` with a branch

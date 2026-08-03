---
name: skill-name-here
description: Use when CONCRETE TRIGGERING CONDITIONS AND SYMPTOMS. Add trigger phrases in English AND Russian. Say what the skill does AND when to use it, in third person, max 1024 chars, no angle brackets.
# Optional, spec-legal — delete the ones you don't need:
# license: MIT
# compatibility: runtime / system packages / required MCP server / protocol version
# metadata:
#   author: you
#   version: "0.1.0"          # quote it, or YAML makes it a float
# allowed-tools: Bash(git:*) Read     # space-separated string, experimental
#
# Claude Code host extensions — legal here, IGNORED by every other agent, so
# never let portable behavior depend on one:
# when_to_use / argument-hint / arguments / disable-model-invocation /
# user-invocable / disallowed-tools / model / effort / context: fork / agent /
# background / hooks / paths / shell
---

# Skill Name

<!--
Spec floor — https://agentskills.io/specification plus Anthropic's platform rules
(https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview):
  name        1-64 chars, a-z0-9 and single internal hyphens, == directory name,
              no angle brackets, never containing "anthropic" or "claude"
  description 1-1024 chars, third person, no angle brackets, what + when
  body        < 500 lines and < 5000 tokens
Heavier material → references/ (docs), scripts/ (code), assets/ (templates,
schemas) inside THIS directory, one level deep, each linked from the body with a
stated load trigger. Reference files over 100 lines start with a "## Contents"
list. Forward slashes in every path. Nothing time-branching: superseded material
goes under "## Old patterns".
-->

## Overview

What is this? Core principle in 1–2 sentences.

## When to use

- Symptom / situation 1
- Symptom / situation 2
- When NOT to use

## Core pattern / workflow

Imperative, procedural steps or a before/after example. Checklists over prose.
State non-negotiables as such. Give a default, not a menu of equal options.
Match prescriptiveness to fragility: an exact command for destructive or
order-dependent work, direction only where context decides.

## Quick reference

| Operation | How |
|---|---|
| … | … |

## References — load on demand

| Read | When |
|---|---|
| `references/FILE.md` | the exact condition that should send the agent there |

## Common mistakes

- What goes wrong → the fix.

## Gotchas

- Environment facts that defy reasonable assumptions. Keep these HERE, not in a
  reference file — the agent can't know to open a file about a trap it doesn't
  know exists.

<!--
Before shipping: ≥3 evaluations recorded (with should-NOT-trigger cases), run
against a no-skill baseline and on every model you claim support for; runtime
needs (network, packages, MCP servers) declared in `compatibility`.
-->

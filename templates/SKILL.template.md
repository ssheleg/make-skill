---
name: <skill-name>
description: Use when <concrete triggering conditions and symptoms>. Add trigger phrases in English AND Russian. Describe WHEN to use, not what the skill does. Max 1024 chars.
# Optional, spec-legal — delete the ones you don't need:
# license: MIT
# compatibility: <runtime / system packages / required MCP server / protocol version>
# metadata:
#   author: <you>
#   version: "0.1.0"          # quote it, or YAML makes it a float
# allowed-tools: Bash(git:*) Read     # space-separated string, experimental
---

# <Skill Name>

<!--
Spec floor (https://agentskills.io/specification):
  name        1-64 chars, a-z0-9 and single internal hyphens, == directory name
  description 1-1024 chars
  body        < 500 lines and < 5000 tokens
Heavier material → references/ (docs), scripts/ (code), assets/ (templates,
schemas) inside THIS directory, one level deep, each with a stated load trigger.
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

## Quick reference

| Operation | How |
|---|---|
| … | … |

## References — load on demand

| Read | When |
|---|---|
| `references/<file>.md` | <the exact condition that should send the agent there> |

## Common mistakes

- What goes wrong → the fix.

## Gotchas

- Environment facts that defy reasonable assumptions. Keep these HERE, not in a
  reference file — the agent can't know to open a file about a trap it doesn't
  know exists.

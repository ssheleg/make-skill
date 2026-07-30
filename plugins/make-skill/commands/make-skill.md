---
description: Create, retrofit, audit, or publish an agent skill / Claude Code plugin the proven ssheleg way — Agent Skills spec conformance, marketplace layout, version sync, validator + CI, multi-channel distribution, MCP / A2A rules.
argument-hint: "<what to build/retrofit/audit, or a skill path>"
---
Use the `make-skill` skill for the task below. First **detect the workflow** from
the task and any path in `$ARGUMENTS`, announce it, then follow the skill exactly:

- new skill only for this user's agents → **Create (personal)**
- new skill others install → **Create (distributable)** → First publish end-to-end
- existing skill/repo below the standard, or "does this match the spec?" →
  **Retrofit** (audit → fix → release)
- a personal skill that should become installable → **Promote**

Task: $ARGUMENTS

If `$ARGUMENTS` is empty, **detect instead of asking**: inspect the current
directory — a `SKILL.md`, `.claude-plugin/`, or `plugins/*/skills/*/` present →
run the Retrofit audit and report the gap table plus exactly ONE next action.
Only when there is nothing to detect, ask in one line what to create.

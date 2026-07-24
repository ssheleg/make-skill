---
description: Create, retrofit, or publish an agent skill / Claude Code plugin the proven ssheleg way — marketplace layout, four-way version sync, validator + CI, multi-channel distribution.
argument-hint: <what to build/retrofit, or a skill path>
---
Use the `make-skill` skill for the task below. First **detect the workflow** from
the task and any path in `$ARGUMENTS`, announce it, then follow the skill exactly:

- new skill only for this user's agents → **Create (personal)**
- new skill others install → **Create (distributable)** → First publish end-to-end
- existing skill/repo below the standard → **Retrofit** (audit → fix → release)
- a personal skill that should become installable → **Promote**

Task: $ARGUMENTS

If `$ARGUMENTS` is empty, ask in one line what to create / retrofit / publish
before starting.

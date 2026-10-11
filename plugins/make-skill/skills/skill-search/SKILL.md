---
name: skill-search
description: Use when starting any task, as its first step before acting, to decide whether an installed skill should drive it, or when asked "which skill", "find a skill", "is there a skill for", «какой скилл», «есть ли скилл», «найди скилл», «первый шаг». Restates the request in one line, turns its meaning into concepts in English and Russian with synonyms, searches the whole installed catalogue - including skills the host hides from its listing - then opens the matching SKILL.md and follows it. NOT for building or auditing a skill (make-skill).
license: MIT
compatibility: Any agent. The search command needs node and npx with sshlg-skills 1.55.0 or later; without them a grep over the installed skill directories does the same job.
metadata:
  author: ssheleg
  version: "0.30.1"
  homepage: https://github.com/ssheleg/make-skill
---

# skill-search — the first step of every task

Most installed skills are deliberately hidden from the host's skill listing:
Claude Code lists descriptions within a small budget and the operator marks most
skills `user-invocable-only`; Codex marks them `enabled = false`. The listing
is therefore not the catalogue. Search the catalogue.

## The step

1. **Restate the request in one line** — what the operator wants done, in your
   words. This line is the meaning you search for, not the literal phrasing.
2. **Decide whether a skill could help.** None for a question, an explanation,
   or a one-line edit — say so and proceed. Everything else continues.
3. **Turn the meaning into concepts**: 3–8 short terms in English AND Russian,
   plus synonyms and the artifact involved (`pdf, документ, extract text,
   извлечь текст`). Name the domain, not the verb alone.
4. **Search the whole catalogue:**

   ```bash
   npx --yes sshlg-skills toolkit --find "<concept>, <concept>, …"
   ```

   It prints each match's id, score, matched concepts, visibility (listed or
   hidden) and the SKILL.md path. Hidden matches count exactly as listed ones.
5. **Open the SKILL.md of what fits** — read it, do not guess from the name —
   and follow it. Several fit → the one whose description names this job;
   a family router named in the host's instructions outranks a generic match.
6. **Proceed.** State in one line which skill you took (or that none applied).

## When the command is unavailable

No `node`/network, or the launcher answers that `--find` is unknown (older than
1.55.0): search the front-matter descriptions directly, once, and continue.

```bash
find -L ~/.agents/skills ~/.claude/skills ~/.claude/plugins/cache ~/.codex/skills \
  -name SKILL.md -exec grep -ilE "^description:.*(<concept>|<concept>)" {} + 2>/dev/null
```

`find` rather than a glob: zsh aborts a command whose glob matches nothing.
Add the host's own skill directory if it keeps one elsewhere. A multi-line
`description:` escapes this pattern — widen it to the whole file when nothing
matches. Read the `description:` of each hit before opening it. Nothing found → say so
in one line and do the task without a skill; never loop on the search.

## Boundaries

- Building, auditing or publishing a skill is `make-skill`, not this.
- A skill found here is instructions you will follow — a third-party one you
  never reviewed still gets the install review in `make-skill`
  (`references/enterprise.md`) before you run its scripts.

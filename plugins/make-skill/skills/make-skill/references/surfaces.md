# Surfaces — where a skill runs, and what breaks when it moves

**Load this when:** the skill must work anywhere except Claude Code — uploading
through the Skills API, shipping to claude.ai, or writing `scripts/` that assume
network access or a package install.

Source: Anthropic's
[Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
and [Using Agent Skills with the API](https://platform.claude.com/docs/en/build-with-claude/skills-guide).
*Read from both on 2026-08-03.* The API is beta; re-check the header dates and
limits before locking a contract.

## Contents

- The surface matrix — one table that decides portability
- Nothing syncs — each surface is a separate deployment
- Runtime constraints authors get wrong
- Skills API — upload, version, attach
- claude.ai
- Pre-built Anthropic skills
- Data retention

## The surface matrix — one table that decides portability

| | Claude Code | Claude API | claude.ai |
|---|---|---|---|
| Install | filesystem: `~/.claude/skills/` (personal), `.claude/skills/` (project), or a plugin | upload via `/v1/skills`, attach per request | zip upload in Settings → Features |
| Sharing | per machine / per repo; plugins for teams | **workspace-wide** — every member sees it | **per user only**; no org-wide push, no admin management |
| Network at runtime | full — same as any program on the machine | **none** | varies with user/admin settings |
| Install packages at runtime | yes, but keep it local to the project | **no** — pre-installed only | npm / PyPI / GitHub allowed |
| Cap per session/request | none | **8 skills per request** | — |
| Pre-built doc skills | no | yes (`pptx`/`xlsx`/`docx`/`pdf`) | yes |

Claude Platform on AWS and Microsoft Foundry behave as the Claude API (on Foundry,
Agent Skills need a *Hosted on Anthropic* deployment).

**The two claude.ai rows are Anthropic's own docs disagreeing**: the overview
says network access there is full, partial or none depending on user/admin
settings, while the authoring guide says claude.ai can install from npm and PyPI
and pull from GitHub. Both are true per-tenant, which means neither is something
to build on — treat claude.ai as "network may be off" and the skill still has to
work.

## Nothing syncs — each surface is a separate deployment

A skill uploaded to the API is not on claude.ai and not in Claude Code, in any
direction. There is no sync mechanism and none is planned in the docs. Keep the
skill directory in git as the single source of truth and treat every surface as a
publish target — which is exactly what the distribution matrix in
`references/distribution.md` automates for the filesystem-based agents.

## Runtime constraints authors get wrong

Written once for the surface you happen to use, a skill silently fails elsewhere:

- **`pip install` / `npm install` in a workflow step** — impossible on the API.
  Either use only pre-installed packages (check the
  [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)
  list) or state the dependency in `compatibility` and give a fallback path.
- **`curl`/`requests`/any fetch inside a script** — no network on the API, maybe
  none on claude.ai. A skill whose only path to data is an HTTP call is a Claude
  Code skill; say so in `compatibility`.
- **Global installs** (`npm i -g`, `pip install --user`) — discouraged even where
  they work: the skill is a guest on the user's machine.
- **Absolute machine paths** (`/Users/you/...`) — nothing outside the skill
  directory exists on the API or claude.ai container.

Declare what you need in front-matter `compatibility` (≤500 chars) and keep the
skill useful, or explicitly refuse, when it is absent.

## Skills API — upload, version, attach

Beta headers: `skills-2025-10-02` enables Skills; `code-execution-2025-08-25`
enables the code execution tool the skills run in; add `files-api-2025-04-14` when
uploading inputs or downloading produced files. The overview calls only the skills
header required, every example in the API guide sends both — send both.

**Attach** — `container.skills[]`, max **8** per request, alongside the code
execution tool:

```python
response = client.beta.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={"skills": [
        {"type": "anthropic", "skill_id": "pptx", "version": "latest"},
        {"type": "custom", "skill_id": "skill_01AbCdEf…", "version": "latest"},
    ]},
    messages=[{"role": "user", "content": "…"}],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
```

Reuse `container={"id": response.container.id, "skills": [...]}` to continue in the
same container, and re-issue the request while `stop_reason == "pause_turn"` for
long jobs. Files the skill produces come back as `file_id`s — fetch them with the
Files API.

**Upload** — `client.beta.skills.create(files=…)` (a zip, file tuples, or
`files_from_dir("my_skill")`), or `POST /v1/skills` multipart. Rules that reject an
upload:

| Rule | Detail |
|---|---|
| `SKILL.md` at the top level | of the single common root directory all files share |
| top-level directory name == `name` | case- and underscore-insensitive match |
| `name` | ≤64 chars, `[a-z0-9-]`, no XML tags, not containing `anthropic` or `claude` |
| `description` | non-empty, ≤1024 chars, no XML tags |
| `display_title` | optional, derived from `name`; if set explicitly it must be unique |
| total upload | **< 30 MB** |

**Version** — custom skills version as epoch timestamps
(`1759178010641129`), Anthropic's own as dates (`20251013`); `"latest"` resolves
either. New version = `client.beta.skills.versions.create(skill_id, files=…)`;
pin an exact version in production. **Deleting a skill requires deleting every
version first** — `skills.versions.delete(...)` in a loop, then `skills.delete(...)`.
List with `client.beta.skills.list(source="custom")`.

## claude.ai

Upload the skill directory as a **zip** in Settings → Features. Requires a Pro,
Max, Team, or Enterprise plan with code execution enabled. Custom skills there are
**individual to each user** — there is no org-wide distribution and no admin
console for them, so "roll this out to the team" means every member uploads it, or
you use the API/plugin channels instead.

## Pre-built Anthropic skills

`pptx`, `xlsx`, `docx`, `pdf` — document creation/editing, available on the API,
AWS, Foundry and claude.ai, attached by `skill_id` with `"type": "anthropic"`.
**They are not available in Claude Code** (which instead bundles the open-source
Claude API skill). Don't rebuild them; don't promise them on the wrong surface.

## Data retention

Agent Skills are **not covered by zero-data-retention arrangements** — skill
definitions and execution data fall under standard retention. If a team is on ZDR
for a reason, that reason applies to what you put in a skill.

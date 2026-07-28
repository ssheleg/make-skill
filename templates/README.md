# templates

Skeletons make-skill seeds when scaffolding a new skill. Copy only when the target
is absent; never overwrite existing files.

| Template | Seeds | Used by |
|---|---|---|
| `SKILL.template.md` | a new `skills/<name>/SKILL.md` — spec-legal front-matter (required + optional fields, limits stated inline) and section stubs incl. References and Gotchas | Create / Promote |

**Never name a skeleton `SKILL.md`.** The skills CLI discovers every `SKILL.md` in
a repo tree and installs it as a real skill — a placeholder would land in every
agent. `test/validate.py` rejects any `SKILL.md` outside `plugins/*/skills/*/`.

Heavier material for a seeded skill goes next to it, inside the skill directory:
`references/` (docs), `scripts/` (code), `assets/` (templates, schemas) — one
level deep, each with a stated load trigger in the body. A sibling directory
reaches Claude Code plugins but arrives broken on every other agent.

Distributable repos also get the full tree (manifests, `bin/`, `test/validate.py`,
workflows, `install.sh`, README/CHANGELOG/LICENSE) — copy those from a reference
impl (`ssheleg/task-pipeline` or `ssheleg/super-ux`) per the SKILL.md layout.

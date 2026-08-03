# templates

Skeletons make-skill seeds when scaffolding a new skill. Copy only when the target
is absent; never overwrite existing files.

| Template | Seeds | Used by |
|---|---|---|
| `SKILL.template.md` | a new `skills/<name>/SKILL.md` — front-matter legal under BOTH rulebooks (limits stated inline, plain placeholders instead of `<angle brackets>`, which count as XML tags and are rejected on upload) and section stubs incl. References and Gotchas | Create / Promote |
| `plugin.template.json` | `plugins/<name>/.claude-plugin/plugin.json` | Create (distributable) / Promote |
| `marketplace.template.json` | `.claude-plugin/marketplace.json` at the repo root | Create (distributable) / Promote |

The two JSON skeletons carry only fields Claude Code recognizes, so
`claude plugin validate <path> --strict` passes on the seeded repo. Replace every
placeholder, keep the `$schema` lines (editor autocomplete), and keep all
four versions in sync. Marketplace level takes `name`, `owner`, `plugins`,
`$schema`, `description`, `version`, `metadata`,
`allowCrossMarketplaceDependenciesOn`, `renames` and nothing else —
`homepage`/`repository`/`license` belong to the plugin entry.

**Never name a skeleton `SKILL.md`.** The skills CLI discovers every `SKILL.md` in
a repo tree and installs it as a real skill — a placeholder would land in every
agent. `test/validate.py` rejects any `SKILL.md` outside `plugins/*/skills/*/`.

Heavier material for a seeded skill goes next to it, inside the skill directory:
`references/` (docs), `scripts/` (code), `assets/` (templates, schemas) — one
level deep, each with a stated load trigger in the body. A sibling directory
reaches Claude Code plugins but arrives broken on every other agent.

Distributable repos also get the full tree (manifests, `bin/`, `test/validate.py`,
`test/evals/`, workflows, `install.sh`, README/CHANGELOG/LICENSE) — copy those
from a reference impl (`ssheleg/task-pipeline` or `ssheleg/super-ux`) per the
layout in `references/distribution.md`. The evaluation suite is not optional
scaffolding: the canon requires ≥3 behavioral scenarios and a trigger set with
near-miss negatives before a skill ships.

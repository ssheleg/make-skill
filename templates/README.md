# templates

Skeletons make-skill seeds when scaffolding a new skill. Copy only when the target
is absent; never overwrite existing files.

| Template | Seeds | Used by |
|---|---|---|
| `SKILL.md` | a new `skills/<name>/SKILL.md` with canon frontmatter + section stubs | Create / Promote |

Distributable repos also get the full tree (manifests, `bin/`, `test/validate.py`,
workflows, `install.sh`, README/CHANGELOG/LICENSE) — copy those from a reference
impl (`ssheleg/task-pipeline` or `ssheleg/super-ux`) per the SKILL.md layout.

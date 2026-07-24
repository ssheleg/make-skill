# Changelog

## v0.2.0 — 2026-07-24

Correct multi-agent + cross-platform distribution guidance (learned shipping the
`sshlg-skills` umbrella).

- **skills CLI, multiple agents:** documented that multiple agents need
  **repeated `--agent` flags** (`--agent cursor --agent zed`) — a comma/space
  value is read as one invalid agent. Exact agent ids (`kimi` → `kimi-code-cli`,
  `hermes` → `hermes-agent`), the `universal`/`*` targets, and the
  `--agent __x__` trick to print the valid list.
- **Umbrella / family distribution** (new matrix item): ship a family of skills
  from their own repos aggregated as git submodules, with a zero-dep launcher
  wrapping `npx skills add` + `claude plugin` + `git submodule update --remote`
  and a `skills.json` source of truth — reference impl `ssheleg/sshlg-skills`.
- **Platforms:** the Node installer, `npx github:`, the plugin, and the skills
  CLI are cross-platform; `install.sh` is POSIX-only (on Windows use npx/plugin/
  skills CLI). Build bin paths with `path.join`, never hardcoded `/`.

## v0.1.0 — 2026-07-24

Initial release — the `make-skill` meta-skill promoted from a personal skill into
a full distributable plugin, built to its own canon.

- **Skill** (`plugins/make-skill/skills/make-skill/SKILL.md`): the proven pipeline
  — authoring rules, the distributable repo layout, Create / Retrofit / Promote
  workflows, end-to-end first publish, the distribution matrix, and the gotchas
  catalog. Reference impls: super-ux (structure) + task-pipeline (config-contract
  + release automation).
- **Command** `/make-skill`: routes a task to the right workflow.
- **Distribution (5 channels):** Claude Code plugin/marketplace, vercel skills CLI
  (`npx skills add`), npm (**`@ssheleg/make-skill`** — scoped, because npm blocks
  the bare `make-skill` as too similar to an existing package) + `npx github:`,
  plain `install.sh` (idempotent, `--force`), and a self-contained Cursor rule
  (`cursor/rules/make-skill.mdc`). Plugin, command, and `bin` names stay
  `make-skill`; only the npm package is scoped.
- **templates/SKILL.md**: canon skeleton seeded when scaffolding a new skill.
- **Validator** (`test/validate.py`, stdlib-only): name sync, four-way version
  sync (marketplace / plugin.json / package.json / CHANGELOG top), command +
  Cursor `.mdc` frontmatter, npm `bin`/`files` shape, template presence, relative
  link resolution. CI runs it plus negative self-tests (corrupt version, missing
  template) and a functional installer test.
- **Toggleable release automation** (`.github/workflows/release.yml`): off unless
  the repo `RELEASE_ENABLED` variable is set; on a `v*` tag it validates the tag ↔
  manifest version, cuts a GitHub release from this CHANGELOG, and npx-smoke-tests
  from a clean checkout.

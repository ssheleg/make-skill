# Changelog

## v0.4.1 — 2026-07-28

### Fixed
- The `validate` workflow had been **red since v0.3.0**: its negative self-test
  deleted `templates/SKILL.md`, a file renamed to `templates/SKILL.template.md`
  three releases earlier. Deleting a non-existent file is a no-op, the validator
  correctly passed, and the step reported that as an error — so the check proved
  nothing while looking like it failed.

### Added
- A second negative self-test: stripping the Russian trigger aliases out of the
  description must fail the validator.

## v0.4.0 — 2026-07-28

### Changed
- Description restructured English-first: each Russian trigger is now paired
  with its English equivalent (`"publish a skill" / "опубликуй скилл"`) rather
  than trailing the English list.
- README is English-only, with a plain statement of what the skill gives you and
  an author/links block.

## v0.3.1 — 2026-07-25

- Gotcha: **npm reports auth failures as `404` on publish.** A `PUT … 404` for a
  package that `npm view` resolves means an expired token, not a missing package —
  check `npm whoami` (E401 → `npm login`) before debugging the name. Cost two
  debugging rounds.

## v0.3.0 — 2026-07-25

Review pass — a live shipping defect plus canon corrections that the repo itself
was violating.

- **FIX (shipping defect): `templates/SKILL.md` was distributed as a real skill.**
  The skills CLI discovers EVERY `SKILL.md` in a repo, so the skeleton was listed
  and installed on every agent as a placeholder skill literally named
  `<skill-name>` (`npx skills add ssheleg/make-skill --list` → "Found 2 skills").
  Renamed to `templates/SKILL.template.md`; the validator now **rejects any
  `SKILL.md` outside `plugins/*/skills/*/`** so it cannot recur.
- **Canon: shared contracts must live INSIDE the skill dir.** The skills CLI
  ships only the skill's own directory, so a sibling `skills/references/`
  (linked `../references/…`) reaches Claude Code plugins but arrives broken on
  every other agent. Layout, authoring rules and the retrofit checklist updated;
  new gotcha documents both this and the stray-SKILL.md trap.
- **Validator hardened** (it now enforces what the canon preaches): description
  must start "Use when …", must carry Russian triggers, frontmatter < 1024 chars,
  no relative links inside `.mdc`, no stray `SKILL.md`. Each rule has a negative
  test.
- **Docs:** README no longer suggests the skills CLI for Claude Code (it shadows
  the plugin); release checklist quotes the validator's real output.

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

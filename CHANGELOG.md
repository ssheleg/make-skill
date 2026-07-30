# Changelog

## v0.7.1 — 2026-07-31

Re-read the plugin reference against what the canon actually says, and against
what Claude Code 2.1.212 actually does. Six corrections, two of them places
where the docs and the binary disagree.

### Fixed
- **`claude plugin validate` validates the manifest, not front matter.** The
  docs' troubleshooting table says it checks "`plugin.json`, skill/agent/command
  frontmatter, and `hooks/hooks.json`"; a `SKILL.md` carrying an invented
  front-matter key passes `--strict` untouched. The canon said this gate
  "catches a class your validator cannot see" — true for manifests, misleading
  for front matter, which is exactly where the house validator earns its place.
- **`claude plugin update <bare-name>` does not work**, though the docs list a
  bare name as accepted: it answers `Plugin "make-skill" not found` **and exits
  0**, so a release script sees success and ships nothing. The reference now
  records both the documented form and the observed one.
- **`skills` adds to the default scan — except at a marketplace root.** When a
  plugin entry's `source` resolves to the marketplace root, the listed
  subdirectories replace the default `skills/` scan (and if none exist, the
  default runs after all). The reference stated the rule without its exception.
- **"Every component directory sits at the plugin root" was too absolute.** That
  is the default; a manifest path field may point anywhere inside the plugin,
  and since 2.1.140 Claude Code warns when a manifest key leaves a default
  folder unscanned. Only `.claude-plugin/` is genuinely off-limits.
- **`allowed-tools`: Claude Code is looser than the spec.** It accepts a
  space- or comma-separated string or a YAML list; the open standard accepts
  only the space-separated string. Canon, Cursor rule and the validator's own
  error message now say which form travels and why, instead of calling a legal
  Claude Code skill invalid.
- **npm plugin sources** resolve to `unknown` only when no `version` is set
  anywhere — the entry or manifest version still wins.

### Changed
- The stray-`SKILL.md` rule is scoped honestly: a plugin-root `SKILL.md` is a
  legal single-skill plugin in Claude Code (2.1.142+). It is multi-channel
  distribution — the skills CLI shipping every `SKILL.md` in the tree — that
  makes the rule, and the validator says so.
- Version pinning: omitting `version` from both manifests is legal and hands
  updates to the git SHA. This canon pins and bumps by choice, which the gotcha
  now states rather than implies.

### Added
- **LSP and monitor fields in `references/claude-code-plugin.md`.** Its own load
  condition promised "adding agents / hooks / MCP / LSP / monitors", and the
  file had a table row for each and nothing else: now the required and optional
  LSP keys with the 2.1.205 `restartOnCrash` / `shutdownTimeout` trap and the
  same-extension race, and the monitor entry schema with its trust,
  `${user_config.*}` rejection and session-lifetime rules. Plus the missing
  `themes/` row.

## v0.7.0 — 2026-07-30

Conformance to Anthropic's own plugin reference
(<https://code.claude.com/docs/en/plugins-reference>), checked with Anthropic's
own checker. The canon already matched the Agent Skills open standard; the
Claude Code layer on top of it — manifest schemas, component layout, path
variables, the CLI — was folk knowledge until now. Everything stays
multi-agent: the host layer is documented as host-specific and never
load-bearing for skills that also run on Cursor, Codex, or the skills CLI.

v0.6.5 wired the upstream gate into CI and fixed the two failures it caught;
this release is the rulebook behind it — so the next repo passes `--strict`
before anyone runs it, not after.

### Added
- **`references/claude-code-plugin.md`** — the Anthropic layer: full
  `plugin.json` and `marketplace.json` schemas, plugin sources, strict mode,
  reserved marketplace names, component locations, skill front-matter host
  extensions, plugin-agent restrictions, scoped MCP hook names,
  `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` / `${CLAUDE_SKILL_DIR}`,
  cache and symlink behavior, skills-directory plugins, the whole
  `claude plugin` CLI, and a conformance checklist. Dated against Claude Code
  2.1.212.
- `$schema` in both manifests (schemastore), so the next edit gets autocomplete
  and inline validation.
- The upstream gate now also covers the **retrofit audit** and the **release
  checklist**, and CI runs it as **its own job** so an upstream CLI outage
  cannot mask a house-validator failure.
- Validator rules, each with a negative self-test: recognized-fields-only for
  both manifests, `$schema` present, reserved marketplace names, `./`-relative
  component paths that never escape the plugin root, source directory name ==
  plugin name, and nothing but the manifest inside `.claude-plugin/`.
- Skill front-matter now accepts the **Claude Code extension keys**
  (`when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`,
  `user-invocable`, `disallowed-tools`, `model`, `effort`, `context`, `agent`,
  `background`, `hooks`, `paths`, `shell`) alongside the spec set. Previously a
  conformant Claude Code skill failed this repo's own audit.
- `templates/plugin.template.json` and `templates/marketplace.template.json` —
  annotated, schema-linked skeletons for the two manifests.
- Personal workflow: a `~/.claude/skills/<name>/` folder with
  `.claude-plugin/plugin.json` loads as `<name>@skills-dir` with hooks, agents,
  and MCP servers — no marketplace, no install step (`claude plugin init`).
- Gotchas: unknown manifest fields load fine and mean nothing (only `--strict`
  surfaces them); a pinned `version` you forget to bump freezes every user,
  because the version is the update cache key.
- `displayName` in both manifests, and the v0.6.6 canon on `claude plugin
  details`, folded in from the parallel release.

### Removed
- **`plugins/make-skill/commands/make-skill.md`.** `claude plugin details`
  reported `Skills (2) make-skill, make-skill`: a command and a skill of the
  same name register `/make-skill` twice, the skill wins, and the command was
  ~100 always-on tokens per session for something unreachable. Its workflow
  detection now lives in the skill body, where it was always going to be read.
  The validator rejects any `commands/<x>.md` that collides with `skills/<x>/`
  and any unquoted `argument-hint`, with negative tests for both; the npx
  installer and `install.sh` no longer write `~/.claude/commands/make-skill.md`
  (an existing copy from an older install is harmless and can be deleted).

### Changed
- **Progressive disclosure applied to the body itself.** The four installer
  implementation traps (piped-stdin readline, raw-mode pickers, ANSI literals,
  Python 3.9 annotation drift) and the 11-step **First publish** sequence moved
  out of `SKILL.md` into `references/distribution.md`, each under a stated load
  condition: they matter only while writing the CLI or actually publishing,
  while the body's token budget is paid by every session. `SKILL.md` ends this
  release under both caps — 347 lines, ~5k tokens — despite everything added
  here and in v0.6.2–v0.6.5.

## v0.6.6 — 2026-07-30

### Added
- **`claude plugin details` joins the canon as the check no manifest performs**:
  it prints what Claude Code believes the plugin contains and the always-on token
  cost per component. Two defects are visible only there — a component listed
  **twice**, because a `commands/<x>.md` and a `skills/<x>/SKILL.md` both claim
  `/<x>` now that custom commands are merged into skills, and a description whose
  always-on cost is worth trimming.
- **`displayName` in both manifests** is now canon: `name` is kebab-case because
  it namespaces components, and the `/plugin` picker falls back to it, so a
  listing reads `my-cool-plugin` until the field is set.

## v0.6.5 — 2026-07-30

### Added
- **`claude plugin validate <path> --strict` is now canon** — the upstream gate,
  wired into CI against both the plugin and the marketplace manifest. It needs
  no auth or API key, so a runner can install `@anthropic-ai/claude-code` and run
  it. The canon records the two failures it found across all six repos of this
  family at once, because neither is visible to a house validator:
  - **`argument-hint` must be quoted.** Bare `[a | b]` is a YAML flow sequence,
    so it parses as a list — and one comma or stray character breaks the block
    outright, at which point the command loads with empty metadata and no
    description, silently.
  - **`homepage` and `repository` are not top-level `marketplace.json` fields.**
    They belong to a plugin entry. Unrecognized fields are warnings the runtime
    tolerates, which is why they survive everything except `--strict`.

### Fixed
- This repo's own command hint and marketplace manifest, per the above.

## v0.6.4 — 2026-07-30

### Changed
- **Publishing to npm is no longer taught as a permanent human step.** The canon
  said 2FA makes non-interactive publishing impossible and to plan the manual
  step; that is only true of an interactive publish and a classic token. Arming
  CI publishing is now step 9 of the first publish, and the definition of done
  gained a fifth fact: *the next tag publishes without a human*.
- **`references/distribution.md` §3** carries both auth routes — npm trusted
  publishing (OIDC, no credential at all: npm >= 11.5.1, Node >= 22.14,
  `id-token: write`, the workflow filename registered on npmjs.com) and a
  granular automation token in `NPM_TOKEN` — and says to write the workflow so
  both work, which makes adopting OIDC later a secret deletion rather than a CI
  edit.
- Three properties the publish job needs, each of which is a red build if
  missing: skip a version already on the registry (publishing over one is a hard
  403), a `workflow_dispatch` input naming an existing tag (a dispatch runs the
  workflow file as of the ref it is dispatched on, so an old tag can never gain
  a new job), and polling `npm view` afterwards, because published is a claim
  until the registry serves it.
- The release-automation section is no longer marked *optional*, with the
  measurement that argues it: six of this family's seven packages were behind
  their own tags on 2026-07-30, one by three releases.

## v0.6.3 — 2026-07-30

### Added
- **Declare the licence in BOTH manifests — now part of the spec floor.** An
  SPDX id belongs in the SKILL.md front matter *and* in the `marketplace.json`
  plugin entry (a documented field there too). A `LICENSE` file in the repo root
  reaches neither the plugin listing nor an installed skill. This gap was found
  across all six repos of this family on the same day, and it stayed open
  precisely because this checklist never asked for it: both fields are optional,
  so nothing ever errored.

### Changed
- `license: MIT` declared in this repo's own two manifests, which is where the
  rule should have been demonstrated first.

## v0.6.2 — 2026-07-30

A family member's release did not end where the skill said it ended. Publishing
to npm left the umbrella pin pointing at the previous version, so the launcher
kept advertising — and `update` kept installing — the release before it, with
nothing in either repo to reveal the gap.

### Added
- **First-publish step 10** (`SKILL.md`): a skill that belongs to a family is
  not released until the umbrella's `skills.json` pin moves and the umbrella is
  released, verified with `npx --yes sshlg-skills@latest list`.
- **`references/distribution.md` §5** — the same rule with the incident that
  produced it (`agent-sync` 1.3.4 on npm while `list` still said 1.3.3).

### Changed
- README — family list and the three family commands; `CONTRIBUTING.md`.

## v0.6.1 — 2026-07-28

Open-source hygiene pass — the repo is public, so the files a first-time
contributor looks for now exist.

### Added
- `CODE_OF_CONDUCT.md`, issue forms for bugs and ideas, and a pull-request
  template carrying this repo's actual checks (`test/validate.py`, `bash -n
  install.sh`).
- US spelling in the changelog.

## v0.6.0 — 2026-07-28

Production pass for a public repository: the README now explains the project
before it explains its own conventions, contributors get an entry point, and the
last inaccuracies found by reading every file end to end are gone.

### Added
- **`CONTRIBUTING.md`** — what belongs in the canon (evidence, not advice), the
  offline one-liner that runs the entire CI suite locally, the rules the
  validator enforces, and the standing requirement that every new validator rule
  ships with a negative test.
- **`SECURITY.md`** — private reporting channel, an exact statement of what the
  installers touch (`~/.claude/skills/make-skill`, `~/.claude/commands/`, no
  network, no postinstall, zero dependencies), and the point that a skill is text
  an agent executes, so it deserves review before installation.
- `--version` / `-v` on the installer CLI, asserted in CI against
  `package.json`.
- **Public-repo floor** in the canon and in the validator: README, CHANGELOG,
  LICENSE, CONTRIBUTING and SECURITY are required root files once a repo is
  public, each with a negative self-test.
- Validator rule: every `references/*.md` must carry a `Load this when:` line.
  A reference without a stated condition is loaded always or never — the exact
  failure progressive disclosure exists to prevent.
- `bugs` URL in `package.json`; `SECURITY.md` added to the published files.

### Fixed
- **The shadow-copy gotcha understated the problem.** Docs said to remove a stray
  `~/.claude/skills/<name>` copy "if it appears". It reappears on schedule: the
  skills CLI auto-detects Claude Code and recreates that path — usually as a
  symlink — on every `--global` add or update, whether or not `claude-code` was
  targeted. The prune is now documented as part of the update command itself.
- The v0.1.0 implementation plan still described `templates/SKILL.md` and an
  unscoped npm package; marked executed and pointed at the spec's Superseded
  table, matching the treatment its sibling spec already had.
- Reference files derived from moving specs (Agent Skills, MCP, A2A) now carry
  the date they were read, so a stale claim is visible instead of implied.

### Changed
- **README rewritten for a first-time reader**: what it is in two sentences, a
  quickstart that ends in a working command, what you actually get (standard
  conformance, a validator that can fail, every channel, the named gotchas,
  where a skill ends and MCP/A2A begin), an install matrix with the prune step
  in it, and a requirements section.
- `permissions: contents: read` on the validate workflow.
- `package.json` keys ordered conventionally.

## v0.5.1 — 2026-07-28

Full-repo consistency pass: every file read against every other, contradictions
fixed rather than annotated.

### Fixed
- **The Cursor rule claimed "no external links" while carrying four.** The actual
  rule — the one the validator enforces — is *no **relative** links*, because the
  `.mdc` gets copied into foreign projects. Stated correctly now.
- **The canon demanded a README section this repo deliberately doesn't have.**
  `README.md (EN + closing RU section)` in the layout and "RU section" in the
  Retrofit audit contradicted the v0.4.0 decision to ship an English-only README.
  Canon now says English-first, with Russian where it actually changes behavior
  (trigger phrases) and an optional RU section for RU-facing projects.
- **The entry-point command contradicted its own design rule.** The canon says a
  `/<name>` command must "detect mode, never ask"; `/make-skill` with no argument
  asked what to build. It now inspects the working directory (`SKILL.md`,
  `.claude-plugin/`, `plugins/*/skills/*/`) and runs the Retrofit audit, asking
  only when there is nothing to detect.
- **The release workflow could ship a broken skill.** Its npx smoke test asserted
  `SKILL.md` and the command but not `references/*.md`, so a release missing them
  would pass while every reference link dangled. Now asserted, matching the
  validate workflow.
- Version-sync arity was stated as four in the body while the validator enforced
  a fifth point (`SKILL.md` `metadata.version`) when present — documented in the
  hard rule, the audit checklist, the Cursor rule, and the validator comment.
- The v0.1.0 promote spec still stated three contracts that did not survive
  contact (bare npm name, `templates/SKILL.md`, "no references split needed").
  Marked executed, with a Superseded table pointing at what actually shipped.
- Layout trees disagreed across SKILL.md, the Cursor rule, and README
  (`release.yml`, `scripts/`, `assets/`, `references/`) — reconciled.

### Changed
- **Descriptions refreshed everywhere they exist** — skill front-matter (772/1024
  chars), `plugin.json`, `marketplace.json`, `package.json`, the slash command,
  and the Cursor rule now name spec conformance, auditing, and MCP/A2A, and carry
  the new trigger pair *"does this skill match the spec" / "соответствует ли
  скилл стандарту"*. Keywords gained `agent-skills`, `mcp`, `a2a`, `spec`.
- README: standard-conformance and protocol-boundary bullets in "What this gives
  you"; the Use section documents no-argument auto-detect.
- `templates/README.md` documents the spec-aware skeleton, the
  never-name-it-`SKILL.md` rule, and where `references/`/`scripts/`/`assets/` go.

## v0.5.0 — 2026-07-28

Audited the canon against the **Agent Skills open standard**
(<https://agentskills.io/specification>, `agentskills/agentskills`). The canon
was compatible but silent on most of the spec: it never stated the `name`
charset rules, capped the wrong thing (whole front-matter instead of
`description`), never mentioned `license` / `compatibility` / `metadata` /
`allowed-tools`, `scripts/` / `assets/`, or the progressive-disclosure budgets.

### Added
- `references/agent-skills-spec.md` — the full standard as a conformance
  reference: field table with limits, `name` charset rules, directory layout,
  the <500-line / <5000-token budgets, the description trigger-eval loop
  (20 queries × 3 runs, 60/40 train/validation split), body patterns, and an
  audit checklist. Marks explicitly where the house canon *extends* the spec.
- `references/mcp.md` — MCP for skill authors: skill vs MCP server, the
  host/client/server model, lifecycle and capability negotiation, server
  primitives with exact methods (`tools/list`, `tools/call`,
  `resources/templates/list`, `prompts/get`, …), client primitives
  (`sampling/createMessage`, `elicitation/create`, roots), stdio vs Streamable
  HTTP, the consent/untrusted-output security rules, and the gotchas
  (host-prefixed tool names, dynamic tool lists, interactive OAuth).
- `references/a2a.md` — A2A for skill authors: A2A vs MCP, the Agent Card at
  `/.well-known/agent-card.json`, Task/Message/Part/Artifact, the task
  lifecycle, the 1.0 method mapping across JSON-RPC/gRPC/REST, streaming vs
  webhook push, security, and the **v0.x→1.0 wire drift** (`message/send` →
  `SendMessage`, lowercase states → `TASK_STATE_*`) that silently breaks
  integrations.
- `references/distribution.md` — the distribution matrix and npm publishing
  traps, moved out of the body (progressive disclosure) so `SKILL.md` stays
  inside the spec's budget.
- SKILL.md: a **Spec floor** block in the authoring rules, a
  **Protocol-connected skills (MCP / A2A)** section, a load-on-demand reference
  index with a raw-URL fallback, and audit items 1 and 10 in the Retrofit
  checklist.

### Changed
- **Validator now enforces the spec, not just house rules:** `name` charset /
  ≤64 / == directory, `description` ≤1024 (the correct field — the old check
  capped the whole front-matter block), `compatibility` ≤500, `metadata` as an
  all-string map, `allowed-tools` as a string, rejection of any front-matter key
  outside the standard, `SKILL.md` < 500 lines, `references/` one level deep with
  every file reachable from the body, and no relative link escaping the skill
  directory. Front-matter is now parsed (YAML subset incl. folded blocks and
  nested maps) instead of regex-sniffed.
- Optional 5th version-sync point: if `SKILL.md` carries `metadata.version`, it
  must match the manifests.
- `templates/SKILL.template.md` is spec-aware: optional front-matter fields
  documented inline, budgets stated, plus References and Gotchas sections.
- Cursor rule carries the spec floor and the MCP/A2A rules inline (no relative
  links — it gets copied into foreign projects).

### Testing
- CI gained a four-case negative self-test for the spec rules (bad `name`
  charset, over-long `description`, unknown front-matter key, orphaned reference
  file) — each must fail the validator.
- The installer functional test now asserts all four `references/*.md` land in
  the install target; a channel that drops them ships broken relative links.
- The first negative self-test used `sed -i` GNU-style, so it only ran on CI and
  errored on any macOS/BSD dry run. Rewritten in `python3` like its siblings —
  the whole workflow is now runnable locally.

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

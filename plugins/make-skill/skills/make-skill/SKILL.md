---
name: make-skill
description: Use when creating, upgrading, or publishing agent skills and Claude Code plugins - "ssheleg skill", "ssheleg скилл", "сделай скилл", "новый скилл", "make a skill", "заверни в плагин", "опубликуй скилл", "догони скилл до стандарта", "retrofit/upgrade a skill", "приведи скилл к стандарту". Encodes the proven ssheleg pipeline - marketplace repo layout, version sync x4, validator+CI, multi-agent distribution (Claude Code plugin, vercel skills CLI, npx, Cursor), npm gotchas, end-to-end first publish. References - github.com/ssheleg/super-ux (structure) + github.com/ssheleg/task-pipeline (config-contract + release automation).
---

# make-skill — Create, Retrofit, and Ship Skills the Proven Way

Reference implementations (local checkouts usually at `~/DATA/<name>`):
- **`ssheleg/super-ux`** — the canonical structure; copy it verbatim when in
  doubt. Multi-skill suite, Cursor rules, templates seeded into projects.
- **`ssheleg/task-pipeline`** — the reference for the newer patterns: a
  single-skill orchestrator with a generic JSON **config-contract**
  (`pipeline.schema.json` + a copy-and-rewrite `pipeline.example.json`),
  four-way version sync with jsonschema conformance in the validator, and
  **toggleable release automation**.

Both work end-to-end; match whichever is closer to the skill at hand.
**make-skill itself** (`ssheleg/make-skill`) is built to this exact canon — the
single-skill-plus-templates shape, distributed on all channels.

## Choosing a workflow

| Situation | Workflow |
|---|---|
| New skill, only for this user's agents | Create (personal) |
| New skill, installable by others/other agents | Create (distributable) |
| Existing skill or repo below this standard | Retrofit |
| Personal skill should become installable | Promote |

Announce the workflow. Distributable work is a real project: brainstorm →
spec (`docs/superpowers/specs/`) → plan → build → validate → publish. The
spec locks target-project file contracts (paths, formats, statuses) FIRST —
skills and rules are written against that contract, never ad hoc.

## Authoring rules (every workflow)

- Front-matter: `name` MUST equal the directory name; `description` starts
  "Use when …" and lists concrete trigger phrases — English AND Russian
  (user works in both). A skill nobody triggers is dead weight.
- One skill = one job. Multiple concerns → multiple skills + shared contract
  in `skills/references/<contract>.md`, linked relatively (`../references/…`).
- Body: imperative, procedural, checklists over prose. Non-negotiables
  stated as such (model: super-ux "Evidence discipline").
- Commands (`commands/*.md`) are thin wrappers: front-matter `description`
  (+ `argument-hint`), body = "invoke skill X in mode Y", pass `$ARGUMENTS`.
- Ship a one-command entry point `/<name>`: idempotent — inspect state →
  repair missing pieces → status report → suggest exactly ONE next action.
  Detect mode, never ask. (Pattern: super-ux `/ux`.)
- Never overwrite user data: seed only when absent; overwrite only behind
  `--force`.

## Create (personal)

`~/.claude/skills/<name>/SKILL.md` following the authoring rules — done.
No repo, no versioning. Loads next session. Mention Promote as the upgrade
path if it proves useful.

## Create (distributable)

### Layout (copy from super-ux)

```
<repo>/
├── .claude-plugin/marketplace.json     # root manifest, plugins[0].source: ./plugins/<name>
├── plugins/<name>/
│   ├── .claude-plugin/plugin.json
│   ├── commands/*.md
│   └── skills/<skill>/SKILL.md  +  skills/references/*.md
├── cursor/rules/*.mdc                  # if agent-rules make sense for Cursor
├── templates/*.md                      # skeletons the skills seed into projects
├── bin/<name>.js + package.json        # npx installer (zero-dep Node)
├── test/validate.py                    # consistency validator (stdlib only)
├── .github/workflows/validate.yml      # validator on push+PR
├── install.sh                          # POSIX fallback
├── README.md (EN + closing RU section), CHANGELOG.md, LICENSE (MIT)
└── docs/superpowers/{specs,plans}/
```

**Version sync (hard rule):** marketplace.json, plugin.json, package.json,
top CHANGELOG entry — SAME semver, bumped together, validator enforces.

**Validator** (adapt super-ux `test/validate.py`): manifests parse+fields;
SKILL.md front-matter (name==dir, description); command front-matter; `.mdc`
front-matter; templates exist; relative md links resolve; version sync.
Plus a negative self-test (corrupt a copy → expect FAIL) — a validator that
can't fail is decoration.

### First publish — end-to-end, same session

Take it ALL the way: GitHub + CI green + npm published + verified installs.
No half-done handoffs — the ONLY human step is npm 2FA.

1. **Preflight before code:** `npm view <name>` (E404 = free);
   `gh auth status` (may lie — just try repo create later); `npm whoami`
   (401 → plan the 2FA human step, keep building).
2. Build per layout; `git init -b main`; conventional commits; set local git
   identity if `git config user.email` empty.
3. Validator + functional tests green BEFORE publishing.
4. **GitHub:** `gh repo create <owner>/<name> --public --source . --push`;
   then `gh repo edit <owner>/<name> --homepage
   "https://www.npmjs.com/package/<name>"`.
5. **Badges day one:**
   `[![npm](https://img.shields.io/npm/v/<name>)](https://www.npmjs.com/package/<name>)`,
   CI badge (`actions/workflows/validate.yml/badge.svg`), license badge.
6. **CI:** poll `gh run list --repo <owner>/<name> --limit 1` until
   `completed success`. Red = fix now.
7. **npm:** `npm publish --dry-run` (eye the tarball) → `npm publish`.
   EOTP/2FA → give the user exactly one command (`cd <repo> && npm publish`),
   wait, then verify `npm view <name> version` + e2e
   `npx <name>@<ver> --help` FROM A NON-REPO CWD.
8. **Install for the user:** `claude plugin marketplace add <owner>/<name>` +
   `claude plugin install <name>@<name>`; verify
   `npx --yes skills add <owner>/<name> --list` finds the skills.
9. Done = four verified facts: GitHub repo + CI green; npm resolvable via
   npx; plugin installed; skills-CLI discovery works.

## Retrofit (bring an existing skill/repo up to standard)

Audit first, fix second, in the same session. Verdict per item: PASS / GAP
with evidence (`file:line` or command output) — never "looks fine".

**Audit checklist:**

1. Front-matter: name==dir; description "Use when…" + EN and RU triggers.
2. One-job check; shared contracts extracted to `references/`, linked
   relatively; no format duplication drift between skills.
3. Entry-point command exists, idempotent (inspect → repair → status → one
   next action).
4. Layout matches the standard tree; manifests complete; version sync ×4.
5. Validator present AND green AND able to fail (run the negative test);
   CI workflow present, last run `success`.
6. README: badges (npm/CI/license), install matrix documented, RU section.
7. Distribution live-checks: `npx --yes skills add <repo> --list` finds
   skills; `npx <name>` works from a non-repo cwd (if npm published);
   `.mdc` rules have no relative links and valid front-matter.
8. Repo meta: homepage → npm page; LICENSE; CHANGELOG current.
9. Gotcha compliance (see below): `from __future__ import annotations` in
   validate.py; `\x1b` literals not raw ESC; single prompter for piped
   stdin; raw-mode only behind isTTY guards.

**Then:** report the gap table, fix everything fixable now, bump a
minor/patch version, run the release checklist. For a PERSONAL skill,
retrofit = items 1–3 only.

## Promote (personal → distributable)

Create the repo per layout, move the skill into
`plugins/<name>/skills/<skill>/`, extract contracts to `references/`, add
entry-point command, then run First publish end-to-end. Delete the old
`~/.claude/skills/<skill>` copy only AFTER the plugin install is verified —
duplicate skill listings confuse agents.

## Distribution matrix

1. **Claude Code plugin:** `/plugin marketplace add <owner>/<repo>` →
   `/plugin install <name>@<name>`; non-interactive via `claude plugin …`
   CLI — use it, don't tell the user to click.
2. **vercel-labs skills CLI (70+ agents):** `npx skills add <owner>/<repo>`
   — discovers skills through `.claude-plugin/marketplace.json`
   automatically; correct manifest = free compatibility. Non-interactive
   flags: `--global`, `--yes`, `--all` (= `--skill '*' --agent '*' -y`);
   update with `npx skills update <name> --global --yes`. Copies land in
   `~/.agents/skills/<name>`. **Multiple agents = REPEATED `--agent` flags**
   (`--agent cursor --agent zed`); a comma/space-joined value
   (`--agent cursor,zed`) is read as one invalid agent. Agent ids are exact:
   `kimi` → `kimi-code-cli`, `hermes` → `hermes-agent`; `universal` and `*`
   target everything; `npx skills add <repo> --agent __x__` prints the valid
   list. **Do NOT include `claude-code` (or `--agent '*'`) when the skill is
   also a Claude Code plugin** — it re-creates a `~/.claude/skills` copy that
   shadows the plugin (see Gotchas).
3. **npx installer:** package.json (`bin`, `files` whitelist) + zero-dep
   CLI; works WITHOUT registry publish via `npx github:<owner>/<repo>`;
   registry publish only buys the short `npx <name>`.
4. **Cursor:** two routes. **Global** — `npx skills add <owner>/<repo>
   --agent cursor --global` lands the skill in `~/.agents/skills/<name>`
   (the shared agents dir Cursor reads). **Per-project** —
   `.cursor/rules/*.mdc` (front-matter `description`, `alwaysApply`, opt.
   `globs`); NO relative links inside .mdc (copied into foreign projects —
   embed contracts inline). Cursor has no native *global rules* dir, so global
   = skills CLI, per-project = `.mdc`, or paste into Cursor Settings → Rules.
5. **Ship a FAMILY via an umbrella repo** (reference: `ssheleg/sshlg-skills`):
   the skills live in their own repos, aggregated as git **submodules**, with a
   zero-dep **launcher** that wraps the three engines above — `npx skills add`
   (non-Claude agents, repeated `--agent`), `claude plugin` (Claude Code, to
   avoid the shadow copy), and `git submodule update --remote` (bump pinned
   snapshots on `update`). A `skills.json` manifest is the source of truth; the
   validator keeps it in sync with `.gitmodules`. One command installs/updates
   the whole family everywhere.

**Platforms.** The Node installer (`bin/*.js`, `os.homedir()`/`path.join`), `npx
github:…`, the Claude Code plugin, and the skills CLI are **cross-platform**
(macOS / Linux / Windows). `install.sh` is POSIX-only — on Windows use `npx`,
the plugin, or the skills CLI, never `install.sh`. Keep bin paths built with
`path.join`, never hardcoded `/`.

## Gotchas (each cost a debugging round)

- **npm 2FA:** publish throws EOTP; non-interactive impossible without a
  granular automation token. Plan as the one human step; verify after.
- **Check npm name FIRST:** `npm view <name>` → E404 means free. But E404 on
  `view` ≠ publishable: npm's **name-similarity** policy only fires on PUT, so
  `npm publish` can still 403 "too similar to existing package <x>" (e.g.
  `make-skill` vs `makeskill`). Fix: a **scoped** name `@<user>/<name>` (scoped
  names are exempt) + `"publishConfig": {"access": "public"}` so `npm publish`
  needs no flag; or pick a clearly dissimilar unscoped name. The `bin` command
  name is independent of the package name — keep it short even when scoped.
- **First scoped publish lags the read path:** right after a successful publish,
  `npm view @scope/pkg` can still E404 for ~1–2 min (write-master has it, read
  replica hasn't). A publish that 403s "cannot publish over previously published
  versions" PROVES it already landed — poll `npm view`, don't re-publish or assume
  failure.
- **npx inside the package's own repo** resolves to the local package →
  false `command not found`. Always e2e-test from another cwd.
- **Piped stdin + readline:** sequential `rl.question()` drops buffered
  lines; use ONE persistent-listener prompter for the whole flow (super-ux
  `makePrompter`). Non-TTY fallback for every prompt (`1,3`/`all`/`q`).
- **Interactive pickers:** raw-mode multiselect only when
  `stdin.isTTY && stdout.isTTY`; restore `setRawMode(false)` on every exit
  path; delegate agent-matrix pickers to `npx skills add`.
- **ANSI escapes:** `\x1b[…` literals in source, never raw ESC bytes.
- **Python drift:** system python3 may be 3.9 — validate.py needs
  `from __future__ import annotations` for `str | None` annotations; CI's
  `3.x` won't catch it, local run will.
- **gh auth status may lie** (invalid-token report while git+ssh path
  works): attempt the operation before declaring it blocked.
- **Duplicate-shadow: one channel per agent.** A plugin install AND a plain
  `~/.claude/skills/<name>` copy (from `install.sh` or `npx skills add
  --agent '*'`) on the SAME Claude Code install = two listings; the plain copy
  can be STALE and shadow the fresh plugin. Keep exactly one channel per
  agent; `rm -rf ~/.claude/skills/<name>` if a stray plain copy appears.
- **Plugin commands need the full `<name>@<name>`:** `claude plugin update
  <name>` → "Plugin not found"; it must be `claude plugin update
  <name>@<name>`. Same for install.

## Release checklist (every version)

1. Bump the four versions together (`package.json` only if npm-distributed —
   else it's a 3-way sync); CHANGELOG entry.
2. `python3 test/validate.py` → `OK (<n> checks)`.
3. Functional tests: installer against scratch dir (fresh / rerun-skip /
   `--force`), `node --check` on CLI, pipe-driven menu tests.
4. Conventional commit; push; confirm CI `success`; tag `v<ver>` + push tag;
   `gh release create` from the CHANGELOG section (or let the release workflow
   below do it).
5. npm publish if applicable (human 2FA); e2e `npx <name>@<ver>` from
   non-repo cwd.
6. **Refresh THIS machine's global installs — always, as DoD** (per global
   `~/.claude/CLAUDE.md`): `claude plugin marketplace update <name>` →
   `claude plugin update <name>@<name>` → `npx skills update <name> --global
   --yes`; remind about the Claude Code restart. Don't leave the user on a
   stale local copy after shipping a new version.
7. Global `~/.claude/CLAUDE.md` — only for rules that must fire even without
   the skill installed.

**Optional — toggleable release automation** (reference impl:
`ssheleg/task-pipeline` `.github/workflows/release.yml`). A `v*`-tag workflow,
**off by default** and armed per repo via a `RELEASE_ENABLED` repo variable
(so forks decide for themselves), that validates the tag ↔ manifest version,
cuts the GitHub release from the matching CHANGELOG section, and smoke-tests
`npx github:<owner>/<repo>#<tag>` from a clean cwd. npm publish stays the human
2FA step. Turns steps 2/4 into CI; keep step 6 manual (it touches this machine).

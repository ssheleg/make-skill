# Distribution matrix — every channel, with the flags that actually work

**Load this when:** publishing a skill for the first time, adding a channel, or
auditing an existing repo's distribution in a Retrofit. Uploading to the Claude
API or claude.ai instead is `references/surfaces.md`.

## Contents

- The shadow rule (one channel per agent)
- The distributable repo layout (tree, public-repo floor, version sync, gates)
- 1. Claude Code plugin
- 2. vercel-labs skills CLI
- 3. npx installer — npm gotchas; the installer must refuse the shadow it
  documents; how updates reach the machine; implementation traps
- First publish — the 11-step sequence
- 4. Cursor
- 5. Ship a FAMILY via an umbrella repo
- Platforms
- Live-check set (Retrofit)
- Release checklist (every version)
- Toggleable release automation

## The shadow rule (one channel per agent)

Hard rule across all channels: **one channel per agent.** Two installs of the same
skill on one agent = two listings, and the stale copy shadows the fresh one.

**The shadow comes back on its own.** `npx skills add|update … --global`
auto-detects Claude Code and writes `~/.claude/skills/<name>` — often as a symlink
into `~/.agents/skills/<name>` — *even when `claude-code` was never named as a
target*. So the routine that refreshes the Cursor/Codex channel silently recreates
the shadow every single run. It cannot be handled by discipline; it needs a step:

```bash
npx skills update <name> --global --yes && rm -f ~/.claude/skills/<name>
```

Put that prune inside whatever script performs the update, so the supported path
can't leave a shadow behind. A symlink shadows exactly as a directory does — check
with `ls -ld`, and remember `find -type f` will not see through it.

## The distributable repo layout

Every rule here exists because the repo ships through more than one channel. Copy
the shape from `ssheleg/super-ux`:

```
<repo>/
├── .claude-plugin/marketplace.json     # root manifest, plugins[0].source: ./plugins/<name>
├── plugins/<name>/
│   ├── .claude-plugin/plugin.json      # ONLY the manifest lives in .claude-plugin/
│   ├── skills/<skill>/SKILL.md  +  references/*.md  +  scripts/  +  assets/
│   │                                   # skeletons live HERE, not at the repo root:
│   │                                   # only the skill dir travels on every channel.
│   │                                   # make-skill ships six: SKILL.template.md,
│   │                                   # plugin.template.json, marketplace.template.json,
│   │                                   # hooks.template.json, agent.template.md,
│   │                                   # command.template.md
│   ├── bin/<exe>                       # Claude Code puts this on the Bash PATH:
│   │                                   # the only reliable way to hand the agent
│   │                                   # a runnable command (no path variable)
│   ├── hooks/hooks.json + *.sh         # Claude Code only — see host-capabilities.md
│   ├── agents/*.md                     # Claude Code only
│   └── commands/*.md                   # never named after a skill
├── cursor/rules/*.mdc                  # if agent-rules make sense for Cursor
├── bin/<name>.js + package.json        # npx installer (zero-dep Node)
├── test/validate.py                    # consistency validator (stdlib only)
├── test/evals/                         # triggers.json + scenarios.json (data, run by a human)
├── .github/workflows/validate.yml      # validator on push+PR (+ release.yml, off by default)
├── install.sh                          # POSIX fallback
├── README.md (English-first), CHANGELOG.md, LICENSE (MIT)
├── CONTRIBUTING.md + SECURITY.md       # public repo: how to check work, where to report
├── SKILL-CARD.md                       # the enterprise registry entry + risk-table pass
└── docs/evidence/{specs,plans}/
```

**Public-repo floor** (validator-enforced): a README saying what it does before
how to install it, **English-first** — Russian belongs in trigger phrases, where
it changes whether the skill fires; `CONTRIBUTING.md` with the offline commands
that verify a change; `SECURITY.md` naming a private reporting channel and every
path that executes, hooks first; `SKILL-CARD.md` answering the enterprise
registry fields and the risk table honestly. A skill is text an agent executes,
so "review before installing" belongs in writing — and anything that runs
without being asked belongs at the top of it.

**What travels where.** Only `skills/<skill>/` reaches non-Claude channels, so
scripts and skeletons live inside it. `hooks/`, `agents/` and `commands/` reach
Claude Code alone: they are accelerators, and the skill body owes each one a
written fallback (`references/host-capabilities.md`).

**Version sync (hard rule):** `marketplace.json`, `plugin.json`, `package.json`
and the top CHANGELOG entry carry the SAME semver, bumped together; the validator
enforces it. An optional `SKILL.md` `metadata.version` — spec-legal, and the only
version an agent outside Claude Code ever sees — joins as a 5th point.

**Two Claude Code checks, both mandatory** (field tables, sources, reserved
names: `references/claude-code-plugin.md`):

- **`claude plugin validate <path> --strict` on BOTH manifests, wired into CI**
  — offline, no auth (`npm i -g @anthropic-ai/claude-code`). Ship `$schema` and
  `displayName` in both, keep component paths `./`-relative. Unrecognized fields
  are warnings the runtime tolerates and only `--strict` shows — that is how
  `homepage`/`repository`, plugin-ENTRY fields, sat at the marketplace root of
  this repo unnoticed. It reads the MANIFEST only: front-matter rules stay in
  your own validator, whatever the troubleshooting table promises.
- **`claude plugin details <name>@<marketplace>`** — the only view of what Claude
  Code *thinks* the plugin contains and what it costs every session. Catches a
  component listed twice and a description worth trimming.

**The house validator** (adapt super-ux `test/validate.py`, stdlib only) enforces
what neither upstream gate sees: both conformance checklists
(`agent-skills-spec.md`, `claude-code-plugin.md`), the house description rules
(starts "Use when", EN+RU triggers), version sync, references reachable / one
level deep / `## Contents` past 100 lines, no command colliding with a skill
name, `.mdc` free of relative links, **no stray `SKILL.md` outside
`plugins/*/skills/*/`**, links that resolve and never escape the skill dir. Plus
a negative self-test — corrupt a copy, expect FAIL — because a validator nobody
has watched fail is decoration.

**And planting has a blind spot: a check that never runs.** Corrupting a copy
proves a check asserts the *wrong* thing when it is wrong. It cannot see a check
that neither passes nor fails, because *nothing happening* is indistinguishable
from a clean suite. Two ways it happens, both shipped in `sheleg-design` on
2026-08-16 inside the **same** check and within an hour of each other: a lookup
returning `None` on a case mismatch — `NUMBER_WORDS` is keyed lowercase and the
document capitalises — which short-circuited the guard; and a pattern anchored on
a line wrap the file did not have, so the edit it was policing had already failed
silently. **The check-count is not evidence either**: the total rose by four while
the new check covered nothing.

So the procedure has a second half. Plant the defect, then **read the failure you
expected rather than the summary** — and if the suite still passes, suspect your
check before you trust the artifact. Run `claude plugin validate --strict` as its OWN
CI job so an upstream outage cannot mask a house failure, and treat `skills-ref
validate <skill dir>` (from `agentskills/agentskills`) as the tie-breaker on the
open standard.

## 1. Claude Code plugin

`/plugin marketplace add <owner>/<repo>` → `/plugin install <name>@<name>`;
non-interactive via the `claude plugin …` CLI — use it, don't tell the user to
click. Plugin commands need the FULL `<name>@<name>` id (`claude plugin update
<name>` → "Plugin not found").

## 2. vercel-labs skills CLI (70+ agents)

`npx skills add <owner>/<repo>` — discovers skills through
`.claude-plugin/marketplace.json` automatically; a correct manifest = free
compatibility.

- Non-interactive flags: `--global`, `--yes`, `--all`
  (= `--skill '*' --agent '*' -y`); update with
  `npx skills update <name> --global --yes`.
- Copies land in `~/.agents/skills/<name>`.
- **Multiple agents = REPEATED `--agent` flags** (`--agent cursor --agent zed`).
  A comma/space-joined value (`--agent cursor,zed`) is read as ONE invalid agent.
- Agent ids are exact: `kimi` → `kimi-code-cli`, `hermes` → `hermes-agent`;
  `universal` and `*` target everything;
  `npx skills add <repo> --agent __x__` prints the valid list.
- **Do NOT include `claude-code` (or `--agent '*'`) when the skill is also a
  Claude Code plugin** — it re-creates a `~/.claude/skills` copy that shadows the
  plugin.
- Verify what it would ship: `npx skills add <repo> --list` must list ONLY the
  real skills (a stray `SKILL.md` anywhere in the tree ships as a skill).

## 3. npx installer

`package.json` (`bin`, `files` whitelist) + a zero-dep CLI. Works WITHOUT a
registry publish via `npx github:<owner>/<repo>`; publishing to the registry only
buys the short `npx <name>`. Always e2e-test **from a non-repo cwd** — inside the
package's own repo, `npx` resolves the local package and reports a false
`command not found`.

### npm gotchas — each one cost a debugging round

- **npm 2FA:** an interactive `npm publish` throws EOTP, and a *classic* token
  does not get past it. Two ways out, both of which remove the human step for
  good — set one up rather than planning a manual publish forever:
  - **Trusted publishing (OIDC) — preferred, no credential exists to leak.**
    npm CLI ≥ 11.5.1, Node ≥ 22.14, `permissions: id-token: write`, and the
    package configured on npmjs.com with the exact workflow *filename* as its
    trusted publisher. No `NODE_AUTH_TOKEN` at all.
  - **Granular automation token** in `NPM_TOKEN`, passed as `NODE_AUTH_TOKEN`.
    Works immediately with no npmjs.com setup, at the cost of a long-lived
    credential to rotate.

  Write the workflow so both work — always grant `id-token: write` and always
  pass `NODE_AUTH_TOKEN` from the secret. Then adopting OIDC later is deleting a
  secret, not editing CI. `id-token: write` is also what signs `--provenance`.

  Three properties the job needs, each earned the hard way:
  - **Skip a version already on the registry.** Publishing over one is a hard
    403, which turns every re-run into a red build.
  - **A `workflow_dispatch` input naming an existing tag.** A dispatch runs the
    workflow file *as of the ref it is dispatched on*, so a tag pushed before the
    publish job existed can never gain one — the input lets the current workflow
    run against an old tag.
  - **Poll `npm view` after publishing.** The read replica lags the write master
    by a minute or two; published is a claim until the registry serves it.
- **Check the npm name FIRST, but don't trust E404:** `npm view <name>` → E404
  means free, yet npm's **name-similarity** policy only fires on PUT, so
  `npm publish` can still 403 "too similar to existing package <x>" (e.g.
  `make-skill` vs `makeskill`). Fix: a **scoped** name `@<user>/<name>` (scoped
  names are exempt) + `"publishConfig": {"access": "public"}` so publish needs no
  flag; or pick a clearly dissimilar unscoped name. The `bin` command name is
  independent of the package name — keep it short even when scoped.
- **npm masks auth failures as 404 on publish.** A `PUT … 404 Not Found` for a
  package that demonstrably exists (`npm view <name> version` returns a version)
  is an EXPIRED TOKEN, not a missing package — npm hides 401/403 on write so it
  can't be used to probe ownership. Check `npm whoami` FIRST: E401 → `npm login`,
  then re-publish. Before a batch publish, run `npm whoami` once rather than
  debugging four 404s.
- **First scoped publish lags the read path:** right after a successful publish,
  `npm view @scope/pkg` can still E404 for ~1–2 min (write-master has it, the read
  replica doesn't). A publish that 403s "cannot publish over previously published
  versions" PROVES it already landed — poll `npm view`, don't re-publish.
- **`npx` inside the package's own repo** resolves the local package → a false
  `command not found`. Always e2e-test from another cwd.

### The installer must refuse the shadow it documents

The shadow rule at the top of this file is not only about the skills CLI: **a member's
own `npx @scope/<name>` installer is the other machine that recreates the shadow.** It
writes `~/.claude/skills/<name>` on request, and on a machine where the same skill is
installed as a Claude Code plugin, that write is a plain copy that outranks the plugin
and serves the version it was copied from forever. Measured 2026-08-29: a bare
`npx @ssheleg/telegram-dev` created three plain copies in `~/.claude/skills/` while the
`telegram-dev` plugin was enabled — and every bin installer in the family had the same
hole, because every member's CI tested a fresh `HOME` only, so the plugin-present case
had never run anywhere.

The canon, for every bin installer that targets `~/.claude/skills/`:

- **Detect the plugin from the TARGET home before writing.** Read that home's
  `~/.claude/plugins/installed_plugins.json` and look for a plugin whose name matches
  the skill under ANY marketplace — the keys are `<name>@<marketplace>`, and the two
  names differ often. A `~/.claude/plugins/marketplaces/<name>` directory also signals
  the plugin channel, but only as the fallback read: it **under-reports** — a
  marketplace added from a local `directory` source has no dir there at all, and a
  differently-named marketplace never matches the skill name. A presence check keyed on
  that directory alone stays green while the shadow lands, which is the fail-open
  class: it looks at the wrong file and then exits 0.
- **Refuse, and exit non-zero.** Print what was found, why the plain copy is refused,
  and the plugin-channel remedy — `claude plugin marketplace update <name>` then
  `claude plugin update <name>@<marketplace>` with the spec read from the JSON, or the
  family launcher (`npx --yes sshlg-skills@latest update`) for a member that composes
  with its family. A refusal that exits 0 reads as success to every script above it:
  this repository's own installer shipped exactly that half-measure until v0.25.0 —
  marketplace-dir check, a `skip:` message, exit 0.
- **`--force` is the deliberate override**, named inside the refusal itself. Two
  channels on one agent is a choice someone may make on purpose, and the flag is where
  that choice gets recorded instead of happening by accident.
- **Absence fails open; corruption never crashes.** A missing or unparsable
  `installed_plugins.json` reads as "no plugin" — the fresh HOME is the common case,
  and an installer that dies on a parse error refuses the machines that need it most.
- **Only Claude Code has plugins.** The check gates the `~/.claude` write alone;
  installs into other agents' skill directories are untouched by it.
- **CI runs the plugin-present case, not only a fresh HOME.** A fake HOME whose
  `installed_plugins.json` declares the plugin, asserting all three at once: the
  non-zero exit, the remedy in the output, and that nothing was written — plus the
  `--force` path installing and the fresh HOME still installing. Reference
  implementation: this repository's `bin/make-skill.js` and `test/installer_test.js`.

### How updates reach the machine — decide it, then SAY it

An installer that never mentions updates has still chosen an update model: **never**. The
operator installs once, the pack drifts, and nothing tells them. Decide between three, and
print the answer at the end of the install.

**Claude Code's own switch is a per-marketplace `autoUpdate` flag** in
`~/.claude/plugins/known_marketplaces.json`. It is real and it is **not in the documented
settings surface** — not in the settings reference, not in the marketplace page; `/plugin`
writes it, and third-party installers write it directly. `vercel-labs/plugins` prompts
`Enable auto-updates? [Y/n]`, defaults to yes, and only asks when the marketplace is new,
the target is Claude Code or Cursor, and the install did **not** go through the official
CLI. Measured on one machine 2026-08-28: of 20 marketplaces, the 2 installed by that tool
carry `autoUpdate: true` and the other 18 have no such key — **`claude plugin marketplace
add` does not set it**, so a plugin installed the official way never auto-updates unless
somebody turns it on.

| Model | Who updates | Right when |
|---|---|---|
| **Per-marketplace `autoUpdate`** | Claude Code, in the background, each marketplace on its own clock | packs are **independent** — one can move without the others meaning anything |
| **A launcher command** (`npx <name> update`) | the operator, in one pass, whole set | packs **compose** — they are released and tested together |
| **Nothing** | nobody | never; this is the default you get by not choosing |

**The trap, and it is the whole reason this section exists.** For a FAMILY that composes,
per-marketplace auto-update is actively wrong: each member moves on its own schedule and
the machine ends up in a combination the maintainers never tested together. That is the
same reason a family launcher refuses a per-member argument. If your packs are
independent, `autoUpdate` is the better answer and you should offer it; if they compose,
offer the launcher and say plainly that auto-update is off **on purpose**.

Either way the last thing the installer prints is how the next version arrives. "Installed"
is not a complete sentence.

### Installer implementation traps (read while WRITING the CLI)

- **Piped stdin + readline:** sequential `rl.question()` drops buffered lines.
  Use ONE persistent-listener prompter for the whole flow (super-ux
  `makePrompter`), with a non-TTY fallback for every prompt (`1,3` / `all` / `q`).
- **Interactive pickers:** raw-mode multiselect only when
  `stdin.isTTY && stdout.isTTY`; restore `setRawMode(false)` on every exit path.
  Delegate agent-matrix pickers to `npx skills add` instead of rebuilding one.
- **ANSI escapes:** write `\x1b[…` literals in source, never raw ESC bytes — an
  editor or a copy-paste eats the invisible one.
- **Python drift:** system `python3` may be 3.9, so a validator using `str |
  None` annotations needs `from __future__ import annotations`. CI's `3.x` is
  newer and won't catch it; the user's local run will.

## First publish — the 11-step sequence

Run it end-to-end in one session. The only human step is npm 2FA, and step 9
removes even that for every release after this one.

1. **Preflight before code:** `npm view <name>` (E404 = free — but read the
   name-similarity trap above); `gh auth status` (may lie — try the operation
   anyway); `npm whoami` (401 → plan the 2FA human step, keep building).
2. Build per the SKILL.md layout; `git init -b main`; conventional commits; set
   the local git identity if `git config user.email` is empty.
3. House validator + functional tests + BOTH `claude plugin validate … --strict`
   runs green BEFORE publishing.
4. **GitHub:** `gh repo create <owner>/<name> --public --source . --push`, then
   set a homepage, description and topics — `gh repo edit <owner>/<name>
   --homepage "<the npm page or the project site>"`. Pick one convention per
   family and hold it; a retrofit should not keep "correcting" a deliberate
   choice back and forth.
5. **Badges day one:** npm (shields.io), CI
   (`actions/workflows/validate.yml/badge.svg`), license.
6. **CI:** poll `gh run list --repo <owner>/<name> --limit 1` until
   `completed success`. Red = fix now, not later.
7. **npm:** `npm publish --dry-run` (eye the tarball) → `npm publish`. On
   EOTP/2FA hand the user exactly one command (`cd <repo> && npm publish`), wait,
   then verify `npm view <name> version` and e2e `npx <name>@<ver> --help`
   **from a non-repo cwd**.
8. **Install for the user:** `claude plugin marketplace add <owner>/<name>` +
   `claude plugin install <name>@<name>`; verify
   `npx --yes skills add <owner>/<name> --list` finds the skills.
9. **Arm CI publishing so this is the last manual publish.** Ship the release
   workflow, then hand over two commands — `gh secret set NPM_TOKEN --repo
   <owner>/<name>` (a GRANULAR AUTOMATION token; the user pastes it, never you)
   and `gh variable set PUBLISH_NPMJS --body true --repo <owner>/<name>`. Secret
   first: arming the variable with no token queues a red run on the next tag.
10. **Done = five verified facts:** repo + CI green; npm resolvable via npx;
   plugin installed; skills-CLI discovery works; the next tag publishes without
   a human.
11. **If it belongs to a family** (`sshlg-skills`): bump its `version` pin in the
   umbrella's `skills.json`, release the umbrella, verify with
   `npx --yes sshlg-skills@latest list` — until that lands, the launcher
   advertises the OLD version and `update` installs it (§5 below).

## 4. Cursor

Two routes, no overlap:

- **Global** — `npx skills add <owner>/<repo> --agent cursor --global` lands the
  skill in `~/.agents/skills/<name>` (the shared agents dir Cursor reads).
- **Per-project** — `.cursor/rules/*.mdc` with frontmatter `description`,
  `alwaysApply`, optional `globs`. **NO relative links inside `.mdc`** — the file
  gets copied into foreign projects, so embed contracts inline or use absolute
  URLs.

Cursor has no native *global rules* directory, so: global = skills CLI,
per-project = `.mdc`, or paste into Cursor Settings → Rules.

## 5. Ship a FAMILY via an umbrella repo

Reference: `ssheleg/sshlg-skills`. The skills live in their own repos, aggregated
as git **submodules**, with a zero-dep **launcher** wrapping the three engines
above — `npx skills add` (non-Claude agents, repeated `--agent`), `claude plugin`
(Claude Code, avoiding the shadow copy), and `git submodule update --remote`
(bump pinned snapshots on `update`). A `skills.json` manifest is the source of
truth; the validator keeps it in sync with `.gitmodules`. One command
installs/updates the whole family everywhere.

**The umbrella pins each member's version, so a member release is not done until the pin moves.**
`sshlg-skills/skills.json` carries a `version` per member and `list` prints it. Publish a member
without bumping that pin and the launcher keeps advertising — and `update` keeps installing — the
previous release, with nothing in either repo to reveal the gap. Observed 2026-07-29: `agent-sync`
1.3.4 was on npm and installed everywhere while `list` still said 1.3.3, so a project comparing its
install against `list` told every agent to update to what it already had. Bump the pin, release the
umbrella, then confirm with `npx --yes sshlg-skills@latest list`.

## Platforms

The Node installer (`bin/*.js`, `os.homedir()`/`path.join`), `npx github:…`, the
Claude Code plugin, and the skills CLI are **cross-platform** (macOS / Linux /
Windows). `install.sh` is POSIX-only — on Windows use `npx`, the plugin, or the
skills CLI, never `install.sh`. Build bin paths with `path.join`, never a
hardcoded `/`.

## Live-check set (Retrofit)

```bash
npx skills add <owner>/<repo> --list          # lists ONLY real skills
npx <name>                                     # from a NON-repo cwd
claude plugin update <name>@<name>             # full id required
```

## Release checklist (every version)

1. Bump the four versions together (`package.json` only if npm-distributed — else
   it is a 3-way sync); write the CHANGELOG entry.
2. `python3 test/validate.py` → exit 0 (`PASS: …`), then
   `claude plugin validate ./plugins/<name> --strict` and
   `claude plugin validate . --strict` → both exit 0.
3. Functional tests: installer against a scratch `HOME` (fresh / rerun-skip /
   `--force` / **plugin-present refusal**, per the canon in §3), `node --check`
   on the CLI, piped-menu tests.
4. Conventional commit; push; confirm CI `success`; tag `v<ver>` and push the tag;
   `gh release create` from the CHANGELOG section (or let the release workflow
   below do it).
5. **npm publishes itself** once CI publishing is armed (launch checklist step
   9): the `v*` tag triggers it, with provenance, skipping a version the
   registry already has. A manual `npm publish` here is the fallback for a repo
   that has not armed it yet — not the normal path, and leaving it as the
   normal path is how a family ends up with a release step nobody performs and
   everybody documents. Then e2e `npx <name>@<ver>` from a non-repo cwd.
6. **Refresh THIS machine's global installs — always, as Definition of Done:**
   `claude plugin marketplace update <name>` → `claude plugin update
   <name>@<name>` → `npx skills update <name> --global --yes && rm -f
   ~/.claude/skills/<name>`; then remind the user to restart the agent.
7. Family member? Bump its pin in the umbrella `skills.json` and release the
   umbrella (§5) — until that lands, `list` advertises the old version.
8. Global `~/.claude/CLAUDE.md` — only for rules that must fire even without the
   skill installed.

## Toggleable release automation

Set it up; don't leave it optional (reference impl: `ssheleg/task-pipeline`
`.github/workflows/release.yml`). A `v*`-tag workflow, **off by default**, armed
per repo by two variables so a fork inherits nothing — `RELEASE_ENABLED` for the
GitHub release, `PUBLISH_NPMJS` for the registry. It checks tag ↔ manifest
version, cuts the release from the CHANGELOG section, smoke-tests
`npx github:<owner>/<repo>#<tag>` from a clean cwd, then publishes with
provenance (auth per §3 above). That turns steps 2/4/5 into CI; step 6 stays
manual.

**A release nobody has to attend is the point:** manual publishing is how a
registry ends up versions behind its own tags with nothing showing the gap — six
of this family's seven packages, 2026-07-30.

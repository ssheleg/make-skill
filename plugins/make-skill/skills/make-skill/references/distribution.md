# Distribution matrix — every channel, with the flags that actually work

**Load this when:** publishing a skill for the first time, adding a channel, or
auditing an existing repo's distribution in a Retrofit.

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

- **npm 2FA:** publish throws EOTP; non-interactive is impossible without a
  granular automation token. Plan it as the one human step; verify after.
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

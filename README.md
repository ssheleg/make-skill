# make-skill

[![npm](https://img.shields.io/npm/v/@ssheleg/make-skill)](https://www.npmjs.com/package/@ssheleg/make-skill)
[![validate](https://github.com/ssheleg/make-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/ssheleg/make-skill/actions/workflows/validate.yml)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**A skill that builds skills.** Install it and your coding agent knows how to
create, audit, and ship [Agent Skills](https://agentskills.io/specification) and
Claude Code plugins properly — conforming to the open standard, validated in CI,
and installable on every agent instead of just yours.

The idea for a skill takes ten minutes. The packaging eats the evening: which
front-matter fields are legal, how long a description may be, four manifests that
must carry one identical version, plugin ids that only work in full `name@name`
form, an installer that quietly leaves a second copy shadowing the one you just
fixed. `make-skill` is that evening, written down and enforced.

## Quickstart

```bash
claude plugin marketplace add ssheleg/make-skill
claude plugin install make-skill@make-skill
```

Restart Claude Code, then just ask:

```
make a skill that turns our incident runbooks into a triage workflow
```

…or point it at something that already exists:

```
/make-skill audit ./skills/my-skill against the spec
```

Inside a skill repo, `/make-skill` with no argument detects the situation and runs
the audit rather than asking you what you meant.

## What it does

Four workflows, picked automatically from what you asked for:

| Workflow | When |
|---|---|
| **Create (personal)** | a skill only for your own agents (`~/.claude/skills/<name>/`) |
| **Create (distributable)** | a skill others install → full marketplace repo + first publish |
| **Retrofit** | an existing skill or repo below the standard → audit → fix → release |
| **Promote** | a personal skill that should become installable |

Each one ends somewhere verifiable — a validator exit code, a green CI run, a
resolvable install — not "should work now".

## What you get

**Conformance to the open standard, not just a house style.** The
[Agent Skills specification](https://agentskills.io/specification) sets hard
limits — `name` is 1–64 chars of `a-z0-9` and single hyphens and must match its
directory, `description` caps at 1024 characters, the body should stay under 500
lines and 5000 tokens. Local conventions that merely *feel* right drift from those
without anyone noticing; here they're checked.

**Plugins Anthropic's own tooling accepts.** The
[Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference)
is a second rulebook on top of the standard: which fields `plugin.json` and
`marketplace.json` actually recognize, where components must sit, which paths
survive installation. Unknown fields load silently and do nothing, so the repo is
checked with Anthropic's own gate — `claude plugin validate <path> --strict` on
both manifests, in CI as its own job. That check is what caught this repo's own
`marketplace.json` shipping `homepage` and `repository` at a level where Claude
Code ignores them.

**A validator that can fail.** `test/validate.py` (Python stdlib only, no deps)
checks spec rules, version sync across every manifest, front-matter on commands
and Cursor rules, link integrity, and the traps below. CI runs it plus **negative
self-tests** — deliberately broken copies that must make it exit non-zero. A
validator nobody has seen fail is decoration.

**Every distribution channel, with the flags that actually work.** Claude Code
plugin, the [vercel `skills` CLI](https://github.com/vercel-labs/skills) (70+
agents), `npx`, Cursor rules, and umbrella-repo families — including the
one-channel-per-agent rule that stops them from shadowing each other.

**The gotchas that each cost a debugging round**, so your first publish works
instead of your fourth:

- a stray `SKILL.md` anywhere in the repo ships as a *real* skill on every agent;
- `npm view` returning E404 does **not** mean the name is publishable;
- npm reports expired-token failures as `404 Not Found` on publish;
- `npx <pkg>` inside the package's own repo resolves the local copy and lies;
- the skills CLI recreates the Claude Code shadow copy on every `--global` update,
  whether or not you targeted Claude Code.

**Knowing where a skill ends.** A skill is instructions — it cannot hold a
credential or open a socket. When the task needs a live system that's an **MCP**
server; when the other side is another autonomous agent that's **A2A**. The skill
ships references for both, including the version drift that silently breaks
integrations.

## What ships with it

The skill body stays small on purpose; the detail sits in reference files the
agent opens only when the situation calls for them:

| Reference | Covers |
|---|---|
| `agent-skills-spec.md` | the open standard — field limits, optional front-matter, token budgets, the description trigger-eval loop |
| `claude-code-plugin.md` | the [Claude Code layer](https://code.claude.com/docs/en/plugins-reference) — `plugin.json` / `marketplace.json` schemas, plugin sources, component locations, host-only front-matter, path variables, cache and symlink rules, the `claude plugin` CLI |
| `distribution.md` | every install channel, exact CLI flags, npm publishing traps |
| `mcp.md` | [MCP](https://modelcontextprotocol.io) — skill vs server, primitives and methods, transports, consent and untrusted-output rules |
| `a2a.md` | [A2A](https://a2a-protocol.org) — Agent Cards, task lifecycle, method mapping, v0.x→1.0 wire drift |

Plus three skeletons in `templates/`: `SKILL.template.md` with the spec limits
written into it, and `plugin.template.json` / `marketplace.template.json`, which
carry only fields Claude Code recognizes so a seeded repo passes
`claude plugin validate --strict` on day one.

## Install

**Claude Code (recommended):**

```bash
claude plugin marketplace add ssheleg/make-skill
claude plugin install make-skill@make-skill
```

**Any other agent — Cursor, Codex, OpenCode, Zed, 70+ via the skills CLI:**

```bash
npx skills add ssheleg/make-skill
```

Don't target `claude-code` here if you installed the plugin above — see
one-channel-per-agent.

**npx, no clone:**

```bash
npx github:ssheleg/make-skill     # always current with this repo
npx @ssheleg/make-skill           # npm registry (scoped: npm blocks the bare name)
```

**Cursor, per project:** copy [`cursor/rules/make-skill.mdc`](cursor/rules/make-skill.mdc)
into `.cursor/rules/` — it is self-contained by design.

**Plain skill:**

```bash
git clone https://github.com/ssheleg/make-skill
cd make-skill && ./install.sh          # idempotent; --force to overwrite
```

### Updating

**The family updates as one package** — a bundle with one member current and the rest stale is a
combination nobody tested:

```bash
npx sshlg-skills update               # installed but behind — updates everything
npx sshlg-skills install              # nothing installed yet
npx --yes sshlg-skills@latest list    # what the current release of each member is
```

Restart your agent afterwards: skills and hooks load at session start.

Per-channel, when you are updating this one member only:

**One channel per agent.** A plugin plus a plain `~/.claude/skills` copy on the
same Claude Code install shadow each other, and the stale one usually wins.

| Channel | Update |
|---|---|
| Claude Code (plugin) | `claude plugin marketplace update make-skill` → `claude plugin update make-skill@make-skill` → restart |
| Any agent (skills CLI) | `npx skills update make-skill --global --yes && rm -f ~/.claude/skills/make-skill` |
| npx | `npx github:ssheleg/make-skill` / `npx @ssheleg/make-skill@latest` |
| Plain skill | `git pull && ./install.sh --force` |

The prune in row two is not optional: the skills CLI recreates the Claude Code
copy on every global update, even when Claude Code was never named.

### Requirements

Node ≥ 16 for the `npx` installer; Python 3 only if you run the validator;
`bash` for `install.sh` (Windows users: use `npx`, the plugin, or the skills CLI).
The skill itself is plain Markdown and needs nothing.

## Repo layout

```
.claude-plugin/marketplace.json
plugins/make-skill/
├── .claude-plugin/plugin.json
└── skills/make-skill/                # the skill IS /make-skill — no command file
    ├── SKILL.md                      # the canon, < 500 lines by rule
    └── references/*.md               # loaded on demand
cursor/rules/make-skill.mdc           # self-contained Cursor rule
templates/                            # SKILL.template.md + the two manifest skeletons
bin/make-skill.js + package.json      # zero-dep npx installer
test/validate.py                      # structural validator
.github/workflows/{validate,release}.yml
install.sh  README.md  CHANGELOG.md  CONTRIBUTING.md  SECURITY.md  LICENSE
docs/superpowers/{specs,plans}/       # historical design records
```

## Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for how to run the
validator and the full CI suite locally (both work offline, no dependencies to
install). Security reports: [SECURITY.md](SECURITY.md).

## Author

Built by ssheleg — [sshlg.me](https://sshlg.me)

- X / Twitter — [@sshlg93](https://x.com/sshlg93)
- Telegram — [@sshlg](https://t.me/sshlg)

Part of the [ssheleg skill family](https://github.com/ssheleg/sshlg-skills):
`super-ux`, `task-pipeline`, `agent-sync`, `make-skill`, `sheleg-design`, `seo-aeo-audit`.
**The family installs and updates as one package**, for every agent you use — a bundle with one
member current and the rest stale is a combination nobody tested:

```bash
npx sshlg-skills install              # nothing installed yet — the whole family, any agent
npx sshlg-skills update               # installed but behind — updates everything
npx --yes sshlg-skills@latest list    # what the current release of each member is
```

Restart your agent afterwards: skills and hooks load at session start, so the session that
updates is not the session that gets the new ones.

## License

MIT © 2026 ssheleg.

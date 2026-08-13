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
/make-skill:make-skill audit ./skills/my-skill against the spec
```

…or run just the mechanical half against any skill directory, no agent turn
required. The plugin puts the auditor on the Bash tool's PATH, and the skills-CLI
copy ships the script it wraps:

```bash
make-skill-audit ./my-skill --house                                    # in Claude Code
python3 ~/.agents/skills/make-skill/scripts/audit_skill.py ./my-skill --house   # any terminal
```

With no argument the skill detects the situation — a `SKILL.md` or
`.claude-plugin/` in the current directory means it runs the audit rather than
asking you what you meant. The command is `/make-skill:make-skill` when installed as a plugin and
`/make-skill` when it sits in a skills directory; both reach the same skill, and
asking in plain language works either way.

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

**Conformance to both rulebooks, not just a house style.** The
[Agent Skills specification](https://agentskills.io/specification) sets hard
limits — `name` is 1–64 chars of `a-z0-9` and single hyphens and must match its
directory, `description` caps at 1024 characters, the body should stay under 500
lines and 5000 tokens. [Anthropic's platform docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
add rules the open standard is silent about and only the Skills API enforces —
no XML tags in `name`/`description`, and no `anthropic`/`claude` anywhere in the
name, so `claude-helper` loads fine in Claude Code and is rejected the day
someone uploads it. Local conventions that merely *feel* right drift from both
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

**The Claude Code power set — with a fallback for everywhere else.** The skill
ships what it teaches: a `PostToolUse` **hook** that audits a `SKILL.md` the
moment you save one (and exits silently for every other write, in every other
project), a **subagent** for auditing a repo full of skills without crowding the
main thread, a `/skill-audit` **command**, and a stdlib **script** that does the
mechanical half of an audit deterministically. Hooks, subagents and commands
exist only inside Claude Code — so the canon makes the fallback a rule: **every
host capability is an accelerator with a written fallback**, for three named
cases (not Claude Code, recommended plugin absent, tool or MCP server absent).
A fallback you know but did not write is not a fallback.

**Evaluations, not vibes.** The canon requires every skill to carry at least
three behavioral scenarios and a trigger set whose negatives are *near-misses* —
queries that share the keywords and need something else. make-skill ships its
own in [`test/evals/`](test/evals/), because a description that also fires on
"review my pull request" steals turns from every other skill you have installed.

**A validator that can fail.** `test/validate.py` (Python stdlib only, no deps)
checks both rulebooks' front-matter rules, the 500-line **and** 5000-token body
budgets, a `## Contents` list on every reference past 100 lines, version sync
across every manifest, front-matter on commands and Cursor rules, link
integrity, and the traps below. CI runs it plus **negative self-tests** —
deliberately broken copies that must make it exit non-zero, each asserted to
fail for the right reason. A validator nobody has seen fail is decoration.

**Every distribution channel, with the flags that actually work.** Claude Code
plugin, the [vercel `skills` CLI](https://github.com/vercel-labs/skills) (70+
agents), `npx`, Cursor rules, and umbrella-repo families — including the
one-channel-per-agent rule that stops them from shadowing each other — plus
Anthropic's own surfaces (Skills API upload, claude.ai zip), which sync with
none of the above and impose their own limits on what a skill may do at runtime.

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
| `agent-skills-spec.md` | the hard rules from both authorities — field limits, where the open standard and Anthropic's platform differ, budgets, which checker says no |
| `authoring.md` | the craft — naming, third-person descriptions, degrees of freedom, workflows and feedback loops, script rules, evaluation-driven development |
| `surfaces.md` | Claude Code vs the Claude API vs claude.ai — the Skills API (upload, versions, 8 per request), and the no-network / no-package-install limits that break scripts moved between surfaces |
| `enterprise.md` | installing a skill you didn't write, and running a fleet — risk tiers, the review checklist, the five approval gates, lifecycle, recall limits, rollback |
| `retrofit.md` | the audit procedure — the 14-item checklist, what counts as evidence for a PASS, and the short form for a personal skill |
| `host-capabilities.md` | hooks, subagents, commands, scripts and MCP dependencies — what each buys, what it costs in always-on tokens, hook events and exit-code semantics, and the degradation clauses that keep a skill working where none of them exist |
| `claude-code-plugin.md` | the [Claude Code layer](https://code.claude.com/docs/en/plugins-reference) — `plugin.json` / `marketplace.json` schemas, plugin sources, component locations, host-only front-matter, path variables, cache and symlink rules, the `claude plugin` CLI |
| `distribution.md` | the repo layout, every install channel, exact CLI flags, npm publishing traps, the release checklist |
| `mcp.md` | [MCP](https://modelcontextprotocol.io) for a **skill author** — skill vs server, declaring the dependency, consent and untrusted-output rules |
| `a2a.md` | [A2A](https://a2a-protocol.org) for a **skill author** — choosing it over MCP, the two meanings of "skill", driving an opaque peer safely |

The **protocols themselves** have one home, and it is not this skill: `agent-interop` in
[`ssheleg/agent-stack`](https://github.com/ssheleg/agent-stack) carries MCP's wire surface
and deprecation register, mounting and the double-path 404, the registry and `server.json`,
A2A cards and task states, and the gateway layer. The two files above carry only what
changes because the thing being written is a skill — because two descriptions of one
protocol drift, and the stale one is indistinguishable from the current one.

Plus six skeletons in `skills/make-skill/assets/` — inside the skill directory,
so they reach every channel: `SKILL.template.md` with both rulebooks' limits
written into it, `plugin.template.json` / `marketplace.template.json` carrying
only fields Claude Code recognizes (a seeded repo passes `claude plugin validate
--strict` on day one), and `hooks.template.json` / `agent.template.md` /
`command.template.md`, each with its degradation clause already in place.

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

**npx, no clone** — installs a plain copy into `~/.claude/skills/make-skill`, so
use it only if you did **not** install the plugin above. Both installers detect
the plugin and refuse rather than leave a copy shadowing it:

```bash
npx github:ssheleg/make-skill     # always current with this repo
npx @ssheleg/make-skill           # npm registry (scoped: npm blocks the bare name)
```

**Cursor, per project:** copy [`cursor/rules/make-skill.mdc`](cursor/rules/make-skill.mdc)
into `.cursor/rules/` — it is self-contained by design.

**Plain skill** — same one-channel caveat as `npx` above:

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

Node ≥ 16 for the `npx` installer; **Python 3 for the bundled auditor and the
validator** (without it the skill falls back to the same checks by hand, and
says so); `bash` for `install.sh` and the hook (Windows users: use `npx`, the
plugin, or the skills CLI). The canon itself is plain Markdown and needs nothing.

What runs on its own: one `PostToolUse` hook, which exits silently unless the
file you just wrote is a `SKILL.md`. Read it at
`plugins/make-skill/hooks/skill-md-audit.sh`; it is described in
[SECURITY.md](SECURITY.md) and [SKILL-CARD.md](SKILL-CARD.md).

## Repo layout

```
.claude-plugin/marketplace.json
plugins/make-skill/
├── .claude-plugin/plugin.json
├── skills/make-skill/                # everything here travels to every agent
│   ├── SKILL.md                      # the canon, < 500 lines and < 5000 tokens by rule
│   ├── references/*.md               # loaded on demand
│   ├── scripts/audit_skill.py        # audits any skill dir, stdlib only
│   └── assets/*.template.*           # six skeletons: skill, manifests, hooks, agent, command
├── bin/make-skill-audit              # on Claude Code's Bash PATH — the auditor by name
├── hooks/                            # Claude Code only — PostToolUse SKILL.md audit
├── agents/skill-auditor.md           # Claude Code only
└── commands/skill-audit.md           # Claude Code only, never named after a skill
cursor/rules/make-skill.mdc           # self-contained Cursor rule
bin/make-skill.js + package.json      # zero-dep npx installer
test/validate.py                      # structural validator
test/evals/                           # trigger set + behavioral scenarios (data)
.github/workflows/{validate,release}.yml
install.sh  README.md  CHANGELOG.md  CONTRIBUTING.md  SECURITY.md  SKILL-CARD.md  LICENSE
docs/evidence/{specs,plans}/       # historical design records
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

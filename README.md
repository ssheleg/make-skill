# make-skill

[![npm](https://img.shields.io/npm/v/@ssheleg/make-skill)](https://www.npmjs.com/package/@ssheleg/make-skill)
[![validate](https://github.com/ssheleg/make-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/ssheleg/make-skill/actions/workflows/validate.yml)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Create, retrofit, audit, and ship agent **skills** and **Claude Code plugins** the
proven ssheleg way — conformance to the [Agent Skills open standard](https://agentskills.io/specification),
marketplace repo layout, four-way version sync, a structural validator + CI,
multi-channel distribution, and end-to-end first publish, encoded as a skill so
every new skill follows the same standard.

## What it does

`make-skill` is a meta-skill: point it at a task and it routes to the right workflow.

| Workflow | When |
|---|---|
| **Create (personal)** | a skill only for your own agents (`~/.claude/skills/<name>/`) |
| **Create (distributable)** | a skill others install → full marketplace repo + first publish |
| **Retrofit** | an existing skill/repo below the standard → audit → fix → release |
| **Promote** | a personal skill that should become installable |

It encodes: conformance to the [Agent Skills open standard](https://agentskills.io/specification),
the repo layout, the version-sync hard rule, the validator (with negative
self-tests), the distribution matrix (Claude Code plugin, vercel skills CLI, npx,
Cursor), the npm gotchas, and a release checklist.

Bundled references the skill loads on demand:

| Reference | Covers |
|---|---|
| `agent-skills-spec.md` | the open standard — field limits, optional front-matter, token budgets, description-trigger evals |
| `distribution.md` | every install channel, exact CLI flags, npm publishing traps |
| `mcp.md` | [MCP](https://modelcontextprotocol.io) — skill vs server, primitives, transports, security rules |
| `a2a.md` | [A2A](https://a2a-protocol.org) — Agent Cards, task lifecycle, v0.x→1.0 wire drift |

Reference implementations it mirrors: [super-ux](https://github.com/ssheleg/super-ux)
(structure) and [task-pipeline](https://github.com/ssheleg/task-pipeline)
(config-contract + toggleable release automation). make-skill is itself built to
this canon.

## Install

**Plugin (recommended):**
```
/plugin marketplace add ssheleg/make-skill
/plugin install make-skill@make-skill
```

**Any agent via the skills CLI (Cursor, Codex, OpenCode, 70+ — not Claude Code, use the plugin above):**
```
npx skills add ssheleg/make-skill
```

**npm / npx (no clone):**
```
npx github:ssheleg/make-skill     # straight from GitHub
npx @ssheleg/make-skill           # from the npm registry (scoped — npm blocks the bare name)
```

**Cursor:**
```
npx skills add ssheleg/make-skill --agent cursor --global
```
…or copy `cursor/rules/make-skill.mdc` into a project's `.cursor/rules/`.

**Plain skill:**
```
git clone https://github.com/ssheleg/make-skill
cd make-skill && ./install.sh          # idempotent; --force to overwrite
```

## Updating everywhere

One channel per agent (a plugin plus a plain `~/.claude/skills` copy on the same
Claude Code install shadow each other).

| Channel | Update |
|---|---|
| Claude Code (plugin) | `claude plugin marketplace update make-skill` → `claude plugin update make-skill@make-skill` → restart |
| Any agent (skills CLI) | `npx skills update make-skill --global --yes` (repeated `--agent`; never `claude-code`) |
| npm | `npx @ssheleg/make-skill@latest` / `npx github:ssheleg/make-skill` |
| Plain skill | `git pull && ./install.sh --force` |

## Use

Say *"make a skill"*, *"retrofit this skill to the standard"*, or *"does this
skill match the spec?"* — or invoke `/make-skill <what to build, retrofit, or
audit>`. With no argument inside a skill repo it detects the situation and runs
the audit rather than asking. Russian phrasings (*"сделай скилл"*, *"приведи
скилл к стандарту"*) route the same way.

## Repo layout

```
.claude-plugin/marketplace.json
plugins/make-skill/{.claude-plugin/plugin.json, commands/make-skill.md,
                    skills/make-skill/{SKILL.md, references/*.md}}
cursor/rules/make-skill.mdc          # self-contained Cursor rule
templates/SKILL.template.md                   # skeleton seeded into new skills
bin/make-skill.js + package.json     # npx installer
test/validate.py                     # structural validator (+ negative self-test in CI)
.github/workflows/{validate,release}.yml
install.sh  README.md  CHANGELOG.md  LICENSE
docs/superpowers/{specs,plans}/
```

## What this gives you

The moment you catch yourself re-explaining the same workflow to your agent, you
want a skill. Then the packaging eats your evening: front-matter limits, four
files that must carry the identical version, plugin ids that only work in full
`name@name` form, a CLI that silently installs a second copy shadowing the one
you just fixed.

- **Turns a workflow you keep repeating into something installable** — for
  yourself, your team, or the public.
- **Keeps you inside the open standard** — the `name` charset, the 1024-char
  `description` cap, the <500-line / <5000-token body budget. The validator
  fails on each, so a skill that installs on Claude Code also installs
  everywhere else.
- **Ships the scaffolding that keeps it alive:** repo layout, a validator, CI
  with negative self-tests. A skill that fails loudly beats one that quietly
  stops firing.
- **Knows where a skill ends and a protocol begins** — when to write an MCP
  server instead, how to consume one safely, and what changes when the other
  side is another agent over A2A.
- **Covers every distribution channel** — Claude Code plugin, 70+ agents via the
  vercel `skills` CLI, `npx`, Cursor rules — and the one-channel-per-agent rule
  that stops them from shadowing each other.
- **Encodes the gotchas that each cost a debugging round**, so your first
  publish works instead of your fourth.

## Author

Built by ssheleg — [sshlg.me](https://sshlg.me)

- X / Twitter — [@fuck_this_year](https://x.com/fuck_this_year)
- Telegram — [@sshlg](https://t.me/sshlg)

Part of the [ssheleg skill family](https://github.com/ssheleg/sshlg-skills):
`super-ux`, `task-pipeline`, `make-skill`, `sheleg-design`, `seo-aeo-audit`.
One command installs all five for every agent you use:

```bash
npx sshlg-skills install
```

## License

MIT © 2026 ssheleg.

# make-skill

[![npm](https://img.shields.io/npm/v/@ssheleg/make-skill)](https://www.npmjs.com/package/@ssheleg/make-skill)
[![validate](https://github.com/ssheleg/make-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/ssheleg/make-skill/actions/workflows/validate.yml)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Create, retrofit, and ship agent **skills** and **Claude Code plugins** the proven
ssheleg way — marketplace repo layout, four-way version sync, a structural
validator + CI, multi-channel distribution, and end-to-end first publish, encoded
as a skill so every new skill follows the same standard.

## What it does

`make-skill` is a meta-skill: point it at a task and it routes to the right workflow.

| Workflow | When |
|---|---|
| **Create (personal)** | a skill only for your own agents (`~/.claude/skills/<name>/`) |
| **Create (distributable)** | a skill others install → full marketplace repo + first publish |
| **Retrofit** | an existing skill/repo below the standard → audit → fix → release |
| **Promote** | a personal skill that should become installable |

It encodes: the repo layout, the version-sync hard rule, the validator (with a
negative self-test), the distribution matrix (Claude Code plugin, vercel skills
CLI, npx, Cursor), the npm gotchas, and a release checklist.

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

Say *"make a skill"* / *"сделай скилл"* / *"приведи скилл к стандарту"*, or
`/make-skill <what to build or retrofit>`.

## Repo layout

```
.claude-plugin/marketplace.json
plugins/make-skill/{.claude-plugin/plugin.json, commands/make-skill.md, skills/make-skill/SKILL.md}
cursor/rules/make-skill.mdc          # self-contained Cursor rule
templates/SKILL.template.md                   # skeleton seeded into new skills
bin/make-skill.js + package.json     # npx installer
test/validate.py                     # structural validator (+ negative self-test in CI)
.github/workflows/{validate,release}.yml
install.sh  README.md  CHANGELOG.md  LICENSE
docs/superpowers/{specs,plans}/
```

## По-русски

**make-skill** — мета-скилл: создаёт, дотягивает до стандарта и публикует агентские
**скиллы** и **плагины Claude Code** проверенным способом ssheleg. Кодирует канон:
раскладку marketplace-репозитория, синхрон версий по четырём точкам, структурный
валидатор с негативным self-test'ом в CI, матрицу дистрибуции (плагин Claude Code,
vercel skills CLI, npx, Cursor), npm-грабли и end-to-end первый релиз.

Маршрутизация по задаче: **Create (personal)** — скилл только для своих агентов;
**Create (distributable)** — устанавливаемый другими, полный репо + публикация;
**Retrofit** — довести существующий скилл/репо до стандарта (аудит → фиксы →
релиз); **Promote** — превратить персональный скилл в устанавливаемый.

Эталоны структуры: [super-ux](https://github.com/ssheleg/super-ux) и
[task-pipeline](https://github.com/ssheleg/task-pipeline). Запуск — `/make-skill
<что создать/дотянуть>` или «сделай скилл». Установка — см. раздел Install выше.

## License

MIT © 2026 ssheleg.

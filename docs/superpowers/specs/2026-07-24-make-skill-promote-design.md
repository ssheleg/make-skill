# make-skill — Promote Design Spec

- **Date:** 2026-07-24
- **Status:** approved
- **Owner:** ssheleg
- **Repo (target):** `ssheleg/make-skill` (GitHub, public, MIT)

## Problem

`make-skill` existed only as a personal single-file skill
(`~/.claude/skills/make-skill/SKILL.md`). It encodes the ssheleg skill-shipping
canon but was itself not shipped to that canon — not installable by other agents,
no versioning, no validator, no distribution. Promote it into a full plugin repo.

## Contracts (locked)

- **Name:** `make-skill` everywhere (dir == plugin == marketplace == frontmatter).
  npm name `make-skill` is free (E404) — used directly, no `-skill` suffix.
- **Layout:** the canon distributable tree (mirror `ssheleg/task-pipeline`):
  `.claude-plugin/marketplace.json`, `plugins/make-skill/{plugin.json, commands,
  skills/make-skill/SKILL.md}`, `cursor/rules/make-skill.mdc`, `templates/SKILL.md`,
  `bin/make-skill.js` + `package.json`, `test/validate.py`,
  `.github/workflows/{validate,release}.yml`, `install.sh`, README/CHANGELOG/LICENSE,
  `docs/superpowers/{specs,plans}`.
- **Version:** four-way sync (marketplace, plugin.json, package.json, CHANGELOG
  top), starting `0.1.0`, validator-enforced.
- **Skill body:** the current personal SKILL.md verbatim (single file — cohesive,
  no references split needed) plus a note that make-skill is itself built to canon.
- **No pipeline config-contract** (make-skill is not an orchestrator) → validator
  omits schema-conformance / gate-type / release-block checks; keeps name+version
  sync, command/`.mdc`/template checks, npm shape, link resolution.

## Distribution

Five channels: Claude Code plugin, vercel skills CLI, npm (`make-skill`) + `npx
github:`, plain `install.sh`, Cursor `.mdc`. Toggleable release workflow armed via
`RELEASE_ENABLED`.

## Human steps

npm publish (2FA/EOTP) — the single human step; everything else autonomous.

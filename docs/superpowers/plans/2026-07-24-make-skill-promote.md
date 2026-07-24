# make-skill — Promote Implementation Plan

- **Date:** 2026-07-24
- **Spec:** docs/superpowers/specs/2026-07-24-make-skill-promote-design.md

Single-implementer build; TDD gate = `test/validate.py` (structural). Red first
(validator fails before files exist) → green after each file lands.

1. Scaffold the canon tree; manifests (marketplace + plugin) with name `make-skill`,
   version `0.1.0`.
2. Copy the personal SKILL.md into `plugins/make-skill/skills/make-skill/`; add the
   "built to this canon" note. Thin `/make-skill` command (workflow router).
3. `cursor/rules/make-skill.mdc` (self-contained, no relative links);
   `templates/SKILL.md` skeleton + templates README.
4. `bin/make-skill.js` (zero-dep installer, idempotent, `--force`) + `package.json`
   (name `make-skill`, `bin`, `files` whitelist). `install.sh` (idempotent).
5. `test/validate.py` (four-way version sync, name sync, command/`.mdc`/template
   frontmatter, npm shape, link resolution). Run → PASS.
6. CI `validate.yml` (validator + 2 negative self-tests + installer functional test
   + YAML parse); `release.yml` (off-by-default, tag-driven).
7. README (EN + RU, badges) + CHANGELOG (`0.1.0`) + LICENSE.
8. Local gate: validator PASS, `node --check`, `bash -n`, installer fresh/rerun/
   force in a fake HOME, negative tests FAIL as expected.
9. First publish: `git init` → `gh repo create --public --push` → CI green → arm
   `RELEASE_ENABLED` → tag `v0.1.0` (release workflow cuts the GitHub release) →
   **npm publish (human 2FA)** → e2e `npx make-skill@0.1.0` from a non-repo cwd.
10. Install the plugin for the user + skills-CLI discovery check; then delete the
    old `~/.claude/skills/make-skill` personal copy (only after the plugin is
    verified — avoid the shadow duplicate).

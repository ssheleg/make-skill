# Security Policy

## Reporting a vulnerability

Report privately through
[GitHub Security Advisories](https://github.com/ssheleg/make-skill/security/advisories/new),
or by Telegram to [@sshlg](https://t.me/sshlg) if you'd rather not use GitHub.
Please don't open a public issue for something exploitable.

Expect an acknowledgement within a few days. This is a small project maintained by
one person — there is no bounty, but you'll be credited in the release notes
unless you'd prefer otherwise.

## What this project touches

`make-skill` ships Markdown plus two small installers. Knowing exactly what runs
where is most of the threat model:

- **`bin/make-skill.js`** (run via `npx`) and **`install.sh`** copy the skill
  directory into `~/.claude/skills/make-skill` and nothing else — no command file,
  no other path in `$HOME` — and overwrite only with `--force`. Both are
  zero-dependency: no network calls, no postinstall script. CI asserts the
  absence of `~/.claude/commands/make-skill.md` on every run.
- **`test/validate.py`** reads repository files and exits with a status. It writes
  nothing. `test/evals/` is inert data — text a human feeds to an agent — and
  `test/evals/fixtures/untrusted-skill.md` is a deliberately malicious *sample*
  used to score a review; it is never installed or executed, and its endpoints
  are `example.com` placeholders.
- The Claude Code plugin and the `skills` CLI channels are handled by those tools,
  not by code in this repo.

Nothing here asks for credentials, and nothing phones home. The npm package has no
dependencies, so its supply-chain surface is npm itself.

## Content is instructions for an agent

A skill is text that a coding agent loads into its context and follows. Two
consequences worth stating plainly:

- **Review a skill before installing it**, from any source including this one.
  Prose that an agent treats as instruction deserves the same scrutiny as code you
  would run.
- The canon in this repo deliberately tells agents to treat everything coming back
  from an MCP server or an A2A peer as **untrusted data, never instructions**, and
  never to auto-approve tool calls or bypass consent prompts. If you find guidance
  here that contradicts that, it is a bug — please report it.

## Supported versions

The latest release on `main` is supported. Fixes go into a new version rather than
being backported.

# Agent Skills — the hard rules, from both authorities

**Load this when:** authoring or retrofitting any `SKILL.md`, or when a skill must
install cleanly outside Claude Code. Craft (descriptions, freedom, scripts, evals)
is `references/authoring.md`; surfaces and the Skills API are
`references/surfaces.md`.

## Contents

- Two authorities, one floor
- Frontmatter — the whole field set
- Notes that bite
- Directory layout
- Progressive disclosure — the budgets
- Validation — who says no
- Conformance checklist

## Two authorities, one floor

| Source | What it governs | Where |
|---|---|---|
| **Agent Skills open standard** | the portable format every agent reads | <https://agentskills.io/specification> |
| **Anthropic platform docs** | what Anthropic's own surfaces accept and enforce | <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview> |
| Claude Code plugin reference | host extensions and packaging | `references/claude-code-plugin.md` |

They agree on the shape and differ on enforcement — **write to the intersection**,
because the strictest reader is the one that rejects you:

| Rule | agentskills.io | Anthropic platform | Claude Code |
|---|---|---|---|
| `name` ≤64, `[a-z0-9-]` | yes | yes | yes |
| no leading/trailing/double hyphen, `name` == parent dir | **required** | dir must match `name` on upload (case/underscore-insensitive) | `name` overrides the dir for the `/command` |
| `name` must not contain `anthropic` / `claude` | silent | **enforced** — the Skills API rejects the upload | not enforced |
| no XML tags in `name` / `description` | silent | **enforced** | not enforced |
| `description` ≤1024, non-empty | yes | yes | listing truncates `description` + `when_to_use` at 1536 |
| `license`, `compatibility`, `metadata`, `allowed-tools` | defined | undocumented — don't depend on them there | read, plus ~14 host-only fields |
| body <500 lines / <5000 tokens | recommended | recommended (level-2 budget) | same |

*Read from both on 2026-08-03. Re-read before trusting a limit in a new quarter.*

The ssheleg canon in `SKILL.md` is a **superset** of all three. It may add rules
(RU triggers, version sync, marketplace layout); it must never violate one.

## Frontmatter — the whole field set

| Field | Required | Constraint |
|---|---|---|
| `name` | yes | 1–64 chars, `a-z0-9-` only, no leading/trailing `-`, no `--`, MUST equal the parent directory name, no XML tags, must not contain `anthropic` or `claude` |
| `description` | yes | 1–1024 chars, non-empty, no XML tags; says what it does AND when to use it; third person |
| `license` | no | license name or the name of a bundled license file |
| `compatibility` | no | ≤500 chars; environment requirements (product, system packages, network) |
| `metadata` | no | map of string→string; arbitrary client-defined keys (use unique key names) |
| `allowed-tools` | no | space-separated tool list, pre-approved. **Experimental** — support varies |

```yaml
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: MIT
compatibility: Requires Python 3.11+ and uv
metadata:
  author: ssheleg
  version: "1.2.0"
allowed-tools: Bash(git:*) Read
---
```

## Notes that bite

- The **1024-char cap is on `description` alone**, not on the whole frontmatter
  block. Adding `license`/`metadata` does not eat the description budget.
- **Reserved words are a substring rule.** `claude-tools`, `anthropic-helper` and
  `my-claude-thing` are all rejected on upload — legal in Claude Code, so the
  failure only appears the day someone ships the skill to the API.
- **"No XML tags" bites templates.** A placeholder like `name: <skill-name>` reads
  as a tag; seed skeletons with plain placeholders (`skill-name-here`).
- `metadata` values are **strings** — quote versions (`version: "1.0"`), or YAML
  turns `1.0` into a float.
- `allowed-tools` is a single space-separated **string**, not a YAML list. Claude
  Code additionally accepts a comma-separated string or a YAML list — write the
  spec form anyway, since it is the only one every host reads.
- Nothing in the spec versions a skill. If you want the version visible to agents
  that never see `plugin.json`, put it in `metadata.version` — then it joins the
  version-sync rule.
- The 500-line / 5000-token budget is on the body an agent loads on activation,
  not on the bundle. Bundled files cost nothing until read.

## Directory layout

```
<skill-name>/
├── SKILL.md          # required
├── scripts/          # optional — executable code the agent runs
├── references/       # optional — docs loaded on demand
├── assets/           # optional — templates, images, schemas, data
└── …                 # anything else
```

- `scripts/` — self-contained or explicitly documented deps; useful error
  messages. Write a script when execution traces show the agent re-inventing the
  same logic every run.
- `references/` — small focused files. Contracts live HERE (inside the skill
  dir), never in a sibling directory: the skills CLI ships only the skill's own
  folder.
- `assets/` — output templates too long for `SKILL.md`, schemas, lookup tables.
- Paths are relative to the skill root and always use **forward slashes**.

## Progressive disclosure — the budgets

| Layer | Loaded | Budget |
|---|---|---|
| `name` + `description` | always, for every installed skill | ~100 tokens |
| `SKILL.md` body | when the skill activates | **< 500 lines and < 5000 tokens** |
| `scripts/` `references/` `assets/` | only when the body sends the agent there | no cap, keep files focused |

Rules:
- Keep references **one level deep** (`references/mcp.md`, not
  `references/proto/v1/mcp.md`) and link every one of them from `SKILL.md`
  itself. A file reachable only through another file gets previewed with `head`
  and half-read.
- Give every reference a **load condition** — "read `references/a2a.md` before
  designing an agent-to-agent contract" beats "see references/". An unconditional
  pointer gets loaded always or never.
- Reference files over **100 lines carry a `## Contents` list** — that is what a
  partial read sees.
- Keep gotchas in `SKILL.md` itself. The agent can't know to load a file about a
  trap it doesn't know exists.
- Scripts are executed, not read: their code never enters context, only output
  does. Say which you mean.

## Validation — who says no

| Checker | Covers | Note |
|---|---|---|
| `skills-ref validate ./<skill dir>` | the open standard's frontmatter rules | Python, installed from source out of `github.com/agentskills/agentskills`; not on npm or PyPI |
| Skills API upload | Anthropic's extra rules (reserved words, XML tags, dir name, 30 MB) | the only place they are enforced — see `references/surfaces.md` |
| `claude plugin validate … --strict` | plugin/marketplace **manifests only**, not SKILL.md frontmatter | `references/claude-code-plugin.md` |
| your `test/validate.py` | house rules + everything the three above miss | the only one that runs on every commit |

## Conformance checklist

- [ ] `name`: matches dir, ≤64 chars, `[a-z0-9-]`, no leading/trailing/double
      hyphen, no `anthropic`/`claude`, no angle brackets
- [ ] `description`: 1–1024 chars, no angle brackets, third person, says what it
      does AND when to use it, concrete triggers listed
- [ ] optional fields legal: `compatibility` ≤500, `metadata` all-string map,
      `allowed-tools` a space-separated string
- [ ] no frontmatter key outside spec ∪ documented host extensions
- [ ] `SKILL.md` < 500 lines and < 5000 tokens
- [ ] heavy material in `references/` / `scripts/` / `assets/` INSIDE the skill
      dir, one level deep, each linked from the body with a stated load trigger
- [ ] reference files >100 lines have a `## Contents` list
- [ ] forward slashes everywhere; no relative link escapes the skill dir (`../`)
- [ ] runtime needs (network, packages) declared in `compatibility` —
      `references/surfaces.md`
- [ ] `skills-ref validate ./<skill dir>` passes (upstream truth), in addition to
      `test/validate.py` (house rules). It installs from source only, so on most
      machines the honest verdict is **NOT-RUN with that reason**
      (`references/retrofit.md`) — never a PASS nobody earned

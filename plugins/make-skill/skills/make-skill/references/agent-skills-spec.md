# Agent Skills open standard — conformance reference

**Load this when:** authoring or retrofitting any `SKILL.md`, or when a skill must
install cleanly on agents outside Claude Code.

Upstream sources (verify before locking anything — the spec moves):
- Spec — <https://agentskills.io/specification>
- Repo + reference validator — <https://github.com/agentskills/agentskills>
  (`skills-ref validate ./my-skill`; Python, installed from source out of that
  repo — it is not on npm or PyPI)
- Best practices — <https://agentskills.io/skill-creation/best-practices>
- Description tuning — <https://agentskills.io/skill-creation/optimizing-descriptions>

*Field limits and budgets below were read from the spec on 2026-07-28. Re-read
before trusting them in a new quarter.*

The ssheleg canon in `SKILL.md` is a **superset** of this spec. It may add rules
(RU triggers, version sync, marketplace layout); it must never violate one.

## Frontmatter — the whole field set

| Field | Required | Constraint |
|---|---|---|
| `name` | yes | 1–64 chars, `a-z0-9-` only, no leading/trailing `-`, no `--`, MUST equal the parent directory name |
| `description` | yes | 1–1024 chars, non-empty; says what it does AND when to use it |
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

Notes that bite:
- The **1024-char cap is on `description` alone**, not on the whole frontmatter
  block. Adding `license`/`metadata` does not eat the description budget.
- `metadata` values are **strings** — quote versions (`version: "1.0"`), or YAML
  turns `1.0` into a float.
- `allowed-tools` is a single space-separated **string**, not a YAML list.
- Nothing in the spec versions a skill. If you want the version visible to agents
  that never see `plugin.json`, put it in `metadata.version` — then it joins the
  version-sync rule.

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

## Progressive disclosure — the budgets

| Layer | Loaded | Budget |
|---|---|---|
| `name` + `description` | always, for every installed skill | ~100 tokens |
| `SKILL.md` body | when the skill activates | **< 500 lines and < 5000 tokens** |
| `scripts/` `references/` `assets/` | only when the body sends the agent there | no cap, keep files focused |

Rules:
- Relative paths from the skill root; keep references **one level deep**
  (`references/mcp.md`, not `references/proto/v1/mcp.md`). No reference chains.
- State **when** to load each file — "read `references/a2a.md` before designing
  an agent-to-agent contract" beats "see references/ for details". An unconditional
  pointer gets loaded always or never.
- Keep gotchas in `SKILL.md` itself. The agent can't know to load a file about a
  trap it doesn't know exists.

## Description — the whole triggering budget

The description is the ONLY thing the agent sees before deciding to load the
skill. Spec-aligned rules:

- **Imperative**: "Use when …", not "This skill does …".
- **User intent, not mechanics** — match what the user asked for.
- **Be pushy**: name the contexts where it applies, including ones where the user
  never says the domain word ("even if they don't mention 'CSV'").
- **Concise**: a few sentences. Descriptions grow during tuning — re-check the
  1024 cap after every edit.
- Agents skip skills for tasks they can already do in one step. Descriptions earn
  their keep on specialized/multi-step work.

### Trigger eval loop (use when a skill fires too rarely or too often)

1. Write ~20 realistic queries: 8–10 `should_trigger: true`, 8–10 `false`. The
   valuable negatives are **near-misses** that share keywords but need something
   else.
2. Run each 3× against the agent with the skill installed → trigger rate;
   pass threshold 0.5.
3. Split 60% train / 40% validation, fixed across iterations. Tune only on train
   failures.
4. Too narrow → broaden scope/context. False-firing → add what it does NOT do.
   Never paste keywords from a failed query — that's overfitting; address the
   category instead.
5. ≤5 iterations; pick the iteration with the best **validation** pass rate (not
   necessarily the last).

## Body patterns worth copying

- **Gotchas section** — concrete environment facts that defy assumption. Highest
  value content in most skills. Every correction you make by hand becomes a line.
- **Templates** for output format — agents pattern-match structures better than
  prose descriptions. Long ones → `assets/`.
- **Checklists** for multi-step workflows with dependencies.
- **Validation loops** — do work → run validator → fix → repeat until green.
- **Plan-validate-execute** for batch/destructive work: emit a plan file, validate
  it against a source-of-truth file, only then execute.
- **Defaults, not menus** — one recommended tool + a one-line escape hatch.
- **Add what the agent lacks**; cut anything it already knows. Test: "would the
  agent get this wrong without this line?" No → delete it.
- **Procedures over answers** — teach the method, not one instance's result.

## Conformance checklist (run in every Retrofit audit)

- [ ] `name`: matches dir, ≤64 chars, `[a-z0-9-]`, no leading/trailing/double hyphen
- [ ] `description`: 1–1024 chars, imperative "Use when …", triggers listed
- [ ] optional fields legal: `compatibility` ≤500, `metadata` all-string map,
      `allowed-tools` a space-separated string
- [ ] `SKILL.md` < 500 lines and < 5000 tokens
- [ ] heavy material lives in `references/` / `scripts/` / `assets/` INSIDE the
      skill dir, one level deep, each with a stated load trigger
- [ ] no relative link escapes the skill directory (`../`)
- [ ] `skills-ref validate ./<skill dir>` passes (upstream truth), in addition to
      `test/validate.py` (house rules)

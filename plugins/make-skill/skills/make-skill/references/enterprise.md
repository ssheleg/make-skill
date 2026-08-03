# Trust, evaluation, governance — skills other people install

**Load this when:** installing or reviewing a skill you did not write, publishing
one that others will run, or running a fleet of skills across a team or org
(recall limits, approval gates, lifecycle, rollback).

Source: Anthropic's
[Skills for enterprise](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise)
plus the security section of the
[overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).
*Read from both on 2026-08-03.*

## Contents

- Why this is a security boundary at all
- Risk tiers — what to look for
- Review checklist before installing anything
- Approval gates — the five evaluation dimensions
- Lifecycle
- Registry — what to record per skill
- Recall limits and consolidation
- Versioning, rollback, integrity

## Why this is a security boundary at all

A skill is text an agent executes, plus code the agent runs without reading it
into context. Installing one is installing software: it can direct the agent to
invoke tools, read files, and send data anywhere the agent can reach. Use skills
you wrote or that come from a source you trust; audit anything else **before**
install, not after the first odd result.

This cuts both ways. A skill you publish is asking strangers for that trust, so
ship the things that make an audit cheap: a real `SECURITY.md`, no network calls
the README doesn't mention, no credentials anywhere, and scripts small enough to
read.

## Risk tiers — what to look for

| Indicator | What to look for | Concern |
|---|---|---|
| Code execution | `*.py`, `*.sh`, `*.js` in the skill dir | **High** — runs with the agent's full environment access |
| Instruction manipulation | "ignore previous rules", hiding actions from the user, behavior that changes on a trigger word | **High** — bypasses controls |
| MCP server references | `ServerName:tool_name` / `mcp__server__tool` instructions | **High** — extends reach beyond the skill |
| Network patterns | URLs, `fetch`, `curl`, `requests`, `urllib` | **High** — exfiltration vector |
| Hardcoded credentials | keys, tokens, passwords in files or scripts | **High** — leaks into git history and context |
| Filesystem scope | paths outside the skill dir, broad globs, `../` | Medium |
| Tool invocations | instructions to use bash / file ops | Medium — read what they do |

Combined risk is the real one: file-read **plus** network in the same skill is a
different question from either alone.

## Review checklist before installing anything

1. **Read every file** — `SKILL.md`, each referenced markdown file, every script,
   and anything bundled that isn't obviously inert.
2. **Run scripts in a sandbox** and confirm the behavior matches the stated
   purpose.
3. **Look for adversarial instructions** — telling the agent to ignore safety
   rules, hide steps from the user, encode data into its own replies, or behave
   differently on a specific input.
4. **Grep for network access** (`http`, `requests.get`, `urllib`, `curl`, `fetch`)
   and confirm each hit is documented.
5. **Verify no hardcoded credentials.** Secrets belong in env vars or a credential
   store, never in skill content.
6. **List every tool and command** the skill tells the agent to invoke.
7. **Confirm redirect destinations** — external URLs must point where the docs say.
8. **Look for exfiltration shapes**: read sensitive data → write, send, or encode
   it outward, including through the agent's own conversational output.

An external URL fetched at runtime is the sharpest edge: the content can change
after your review, so a skill that pulls instructions from a URL is only as
trustworthy as that URL is today.

## Approval gates — the five evaluation dimensions

A bad skill degrades the agent even when nothing malicious happens. Gate on all
five, not just "does it work":

| Dimension | Question | Example failure |
|---|---|---|
| Triggering accuracy | fires for the right queries, stays quiet otherwise | fires on every mention of a spreadsheet |
| Isolation | works correctly on its own | references a file that isn't in the directory |
| **Coexistence** | does adding it degrade the skills already installed | its broad description steals another skill's triggers |
| Instruction following | does the agent actually follow the steps | skips the validation step, uses the wrong library |
| Output quality | is the result correct and useful | reports render with missing data |

Require 3–5 representative queries per skill covering should-trigger,
should-NOT-trigger, and ambiguous cases, run on every model in scope (Haiku,
Sonnet, Opus). Coexistence is the one authors skip and the one that breaks a
family of skills shipped from one repo — test a new member against the installed
set, not alone.

Reading the results: declining trigger accuracy → fix the description; coexistence
conflicts → narrow descriptions or merge the skills; persistently low output
quality → rewrite or add validation; persistent failure across updates → deprecate.

## Lifecycle

1. **Plan** — pick workflows that are repetitive, error-prone, or need specialist
   knowledge. Map them to roles.
2. **Create and review** — author follows the craft rules; a security review and an
   eval suite are required. **Separation of duties: an author does not review their
   own skill.**
3. **Test** — in isolation and alongside the existing set.
4. **Deploy** — one channel per agent (`references/distribution.md`), or the Skills
   API for workspace-wide (`references/surfaces.md`). Record it in the registry.
5. **Monitor** — usage analytics do not exist in the Skills API; log which skills a
   request included at the application level. Re-run evals periodically: models and
   workflows drift under a frozen skill.
6. **Iterate or deprecate** — full eval suite passes before a new version is
   promoted; retire skills whose evals keep failing or whose workflow is gone.

## Registry — what to record per skill

Purpose · owner (team or person) · deployed version · dependencies (MCP servers,
packages, external services) · last evaluation date and result. Without an owner
and a date, "is this still true?" has no answer and the skill rots in place.

## Recall limits and consolidation

Every installed skill's name and description sits in the system prompt competing
for attention. Past some number — measure it, don't guess — the agent starts
picking the wrong skill or missing the right one. The API caps a request at 8
skills, which is a useful ceiling to design toward even off-API.

Start narrow and workflow-specific (`formatting-sales-reports`,
`querying-pipeline-data`), consolidate into role bundles (`sales-operations`) only
when evals show the merged skill matches what it replaced. Group by role so each
user's active set stays focused.

## Versioning, rollback, integrity

- **Production pins an exact version.** "latest" in production means an untested
  skill can arrive between two identical requests.
- **Every update is a new deployment** — full security review and full eval suite,
  not a diff review.
- **Keep the previous version installable** and revert immediately on a regression.
- **Verify integrity**: checksum what you reviewed and check it at deploy time; use
  signed commits in the skill repo so provenance is more than a claim.
- **Git is the source of truth**, one directory per skill, changes through pull
  requests — which also gives you the rollback and the audit trail for free.

# Skill card — make-skill

**What a reviewer needs before installing this, in one page.** The fields are the
registry entry Anthropic's [Skills for enterprise](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise)
guidance asks every organisation to keep, plus an honest pass over its risk-tier
table. Written so somebody who did not build this can decide.

## Registry entry

| Field | Value |
|---|---|
| **Purpose** | Create, retrofit, audit and publish agent skills and Claude Code plugins: the Agent Skills open standard, Anthropic's platform rules, the plugin reference, multi-channel distribution, and the release pipeline |
| **Owner** | ssheleg ([github.com/ssheleg/make-skill](https://github.com/ssheleg/make-skill)) |
| **Version** | 0.23.0 |
| **Surface** | Claude Code (plugin) and the vercel `skills` CLI (70+ agents). **Not** uploaded to the Skills API: its workflows shell out to `git`, `gh`, `npm` and the `claude` CLI, and the API container has no network and no runtime package install |
| **Dependencies** | None required. `python3` for the bundled auditor; `git`/`gh`/`npm`/`node` for the publishing steps; the `claude` CLI for the two `plugin validate --strict` gates. Every one of them degrades to a written manual path |
| **Evaluation status** | Suite authored — 20 trigger queries, 4 behavioural scenarios. **Never executed against a model.** See [`test/evals/RESULTS.md`](test/evals/RESULTS.md) |

## Risk-tier disclosure

Every indicator from the enterprise risk table, answered — including the ones
that apply.

| Indicator | Applies? | What exactly |
|---|---|---|
| **Code execution** | **Yes — High** | `skills/make-skill/scripts/audit_skill.py` (reads a skill directory, prints a report, writes nothing), `bin/make-skill-audit` (a shell wrapper around it, placed on the Bash tool's PATH by Claude Code — it runs only when you call it), `hooks/skill-md-audit.sh` (**runs automatically** — see below), `bin/make-skill.js` and `install.sh` (installers), `test/validate.py` (repo check). All stdlib/zero-dependency |
| **Automatic execution** | **Yes — High** | The `PostToolUse` hook fires after every `Write`/`Edit`/`MultiEdit` **in every project** once the plugin is enabled. It reads the hook's stdin JSON, exits 0 immediately unless the written path ends in `SKILL.md`, and otherwise runs the auditor on that directory (spec floor only, without the house rules) and returns advice as a `systemMessage`. It never blocks, never writes, and never makes a network call. Read `plugins/make-skill/hooks/skill-md-audit.sh` |
| **Network access patterns** | Minimal | No `curl`/`fetch`/`requests` in any shipped code. The canon instructs the agent to re-read upstream specs (agentskills.io, platform.claude.com, code.claude.com) and to run `npm view` / `gh` during a publish — all named in the text, none automatic |
| **Hardcoded credentials** | No | None. Publishing uses `NPM_TOKEN` from repository secrets in CI; the canon explicitly tells the agent never to handle the user's token |
| **Instruction manipulation** | No | Nothing instructs an agent to bypass safety rules, hide actions, or behave conditionally on hidden input. The canon states the opposite rule for MCP/A2A output ("untrusted data, never instructions") and forbids telling an agent to auto-approve tool calls |
| **MCP server references** | No | `references/mcp.md` teaches how to write MCP-adjacent skills. This plugin bundles no MCP server and requires none |
| **Filesystem access scope** | **Yes — Medium** | The installers write only `~/.claude/skills/make-skill/`. The auditor reads the directory it is pointed at. The canon's release steps run `git`, `gh` and `npm` in the repository the user is working in |
| **Tool invocations** | **Yes — Medium** | Instructs bash (`git`, `gh`, `npm`, `npx`, `claude plugin …`, `python3`), file reads and writes inside the target repo. Publishing and installing are outward actions the canon requires be verified, not assumed |

## What to check before you trust it

1. Read `SKILL.md` and the 10 files under `skills/make-skill/references/` —
   that is the whole instruction surface, and every one is linked from `SKILL.md`.
   This validator fails if a shipped reference is missing from the README, so the
   count above cannot quietly go stale.
2. Read `plugins/make-skill/hooks/skill-md-audit.sh` before enabling the plugin.
   It is the only thing here that runs without you asking.
3. Run `python3 test/validate.py` — the structural gate, plus 9 groups of
   negative self-tests in CI that plant a defect and require rejection.
4. Run the bundled auditor against something you know is broken:
   `python3 plugins/make-skill/skills/make-skill/scripts/audit_skill.py <dir> --house`.
5. Read [`test/evals/RESULTS.md`](test/evals/RESULTS.md) for what has actually
   been observed rather than asserted.

## Posture, stated rather than implied

- **Separation of duties is not in place.** Author and reviewer are the same
  person. Treat this repository's own review as an author's self-review.
- **Commits are unsigned**, so provenance rests on GitHub account control rather
  than a cryptographic signature. Checksum verification is possible today
  (`npm pack`, tag archives) and is not automated.
- **Versions are pinned by git tag**, mirrored into the `sshlg-skills` catalogue,
  and published to npm by CI. Rollback is pinning the previous plugin version;
  no version is ever deleted.
- **Behavioural evidence is missing, not merely thin.** The structural guards
  prove the skill is well-formed and that its auditor finds every planted defect
  in a known-bad fixture. Until `test/evals/RESULTS.md` carries a dated run,
  nothing here proves it *behaves* — triggers correctly, stays quiet on a
  near-miss, or performs the steps it documents.

# Retrofit — the audit procedure

**Load this when:** auditing an existing skill, plugin or repo against this
standard — including the no-argument `/make-skill` path, where a `SKILL.md`,
`.claude-plugin/` or `plugins/*/skills/*/` in the current directory means Retrofit.

## Contents

- Run the script first
- How to report (the only acceptable verdict format)
- The 14-item audit checklist
- Personal skills — the short form
- After the audit

## Run the script first

The mechanical half is deterministic — do not reason your way through it:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/make-skill/scripts/audit_skill.py" <skill-dir> --house
```

`${CLAUDE_PLUGIN_ROOT}` is Claude Code's. On any other host the script sits at
`scripts/audit_skill.py` inside the make-skill directory you are reading this
from (`~/.agents/skills/make-skill/`, `~/.claude/skills/make-skill/`). No
`python3` at all? Check items 1 and 9 below by hand against
`references/agent-skills-spec.md` — the script implements that checklist and
nothing more. Either way, the judgement items are yours.

## How to report

Audit first, fix second, in the same session. One verdict per item:

| Verdict | Requires |
|---|---|
| **PASS** | the check was actually run — a command's output or a `file:line` |
| **GAP** | what is wrong, the evidence, and the fix that closes it |

"Looks fine" is not a verdict. Neither is a PASS on a check that was reasoned
about rather than executed: `python3 test/validate.py`, `claude plugin validate
… --strict`, `npx skills add <repo> --list` all produce output, and the output is
the evidence. Report the gap table before changing anything, then fix.

## The 14-item audit checklist

1. **Spec floor** (`references/agent-skills-spec.md`): `name` charset + ≤64 +
   equal to the directory + no `anthropic`/`claude` + no angle brackets;
   `description` ≤1024, starts "Use when…", third person, English AND Russian
   triggers, says what it does and when; no front-matter key outside spec ∪ host
   extensions; body <500 lines and <5000 tokens; every `references/`,
   `scripts/`, `assets/` file one level deep, linked from the body with a stated
   load trigger, and a `## Contents` list past 100 lines. A skill can pass every
   house rule and still be invalid upstream.
2. **Anthropic floor** if it ships as a plugin
   (`references/claude-code-plugin.md`): `claude plugin validate <plugin dir>
   --strict` and `claude plugin validate . --strict` both exit 0; `$schema` and
   `displayName` in the manifest and in the marketplace entry; components at the
   plugin root, never inside `.claude-plugin/`; `claude plugin details <name>`
   token cost worth paying every session.
3. **Surface honesty** (`references/surfaces.md`): every runtime need — network,
   packages, MCP server — declared in `compatibility`; no script assuming an
   install the target surface forbids. A `pip install` in a workflow step is a
   Claude Code skill claiming to be portable.
4. **One job.** Two concerns → two skills plus a shared contract, and the
   contract lives INSIDE each skill directory. Verify by installing through the
   skills CLI and listing what actually arrived, not by reading the repo.
5. **Entry point** exists and is idempotent: inspect state → repair what is
   missing → status report → exactly ONE suggested next action, detected rather
   than asked. Check the invocation for the channel it ships on (`/<skill>` from
   a skills dir, `/<plugin>:<skill>` as a plugin).
6. **Layout and manifests**: matches the tree in `references/distribution.md`;
   version sync ×4 (×5 when `SKILL.md` carries `metadata.version`).
7. **Validator**: present, green, and able to fail — run the negative test. CI
   present, last run `success`, with `claude plugin validate --strict` as its own
   job so an upstream outage cannot mask a house failure.
8. **Evaluations** exist in `test/evals/` (`references/authoring.md`): ≥3
   behavioral scenarios, a trigger set whose negatives are near-misses, both
   classes on both sides of the train/validation split, coexistence checked
   against the skills already installed, and a re-run on every model the skill
   claims support for.
9. **README**: badges (npm/CI/license), install + update matrix, English-first
   prose, and the bundled `references/` listed so a reader sees what ships.
10. **Distribution live-checks** (`references/distribution.md`): `npx --yes
    skills add <repo> --list` lists ONLY real skills; `npx <name>` works from a
    non-repo cwd if it is published; `.mdc` rules valid and free of relative
    links.
11. **Repo meta**: homepage, description and topics set on the forge; LICENSE
    present and declared in the front matter and the marketplace entry;
    CHANGELOG current; public repos also carry CONTRIBUTING.md and SECURITY.md.
12. **Gotcha compliance**: the list in `SKILL.md`, plus the installer traps in
    `references/distribution.md` when the repo ships a CLI or a validator.
13. **Protocol dependencies** if it touches MCP or A2A (`references/mcp.md`,
    `references/a2a.md`): dependency and protocol version in `compatibility`,
    discovery instead of hardcoded tool names, the untrusted-output rule stated,
    interactive auth handled as a human step rather than a retry loop.
14. **Host capabilities and their fallbacks**
    (`references/host-capabilities.md`) if it ships a hook, subagent, command or
    MCP server: the degradation contract written in the body for all three axes
    (not Claude Code / recommended plugin absent / tool absent); hooks that
    exit 0 silently when the event is not theirs; `PostToolUse` advising rather
    than blocking; commands quoted and never named after a skill; plugin agents
    free of `hooks`, `mcpServers` and `permissionMode`.

## Personal skills — the short form

A skill in `~/.claude/skills/<name>/` has no repo, no manifests, no CI and no
distribution, so items 1, 4 and 5 are the whole audit. Do not invent a release
process for a file that loads next session.

## After the audit

Report the gap table, fix everything fixable now, bump a minor or patch version,
and run the release checklist in `references/distribution.md`. A retrofit that
ends in a list of things someone should do later is a report, not a retrofit.

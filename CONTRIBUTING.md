# Contributing to make-skill

Thanks for looking. This repo is small, has zero runtime dependencies, and every
check runs offline — you can verify a change completely in under a minute.

## What belongs here

`make-skill` encodes how agent skills are built, validated and shipped. The bar
for adding something to the canon is **evidence**: a rule earns its place after it
cost a real debugging round, and the entry says what broke and how you know.
Generic advice ("write clear instructions") gets cut — an agent already knows it,
and every token in `SKILL.md` competes with the user's actual task.

Especially welcome:

- **Gotchas** from shipping skills on any agent — a concrete symptom, the cause,
  the fix.
- **Spec drift**: the [Agent Skills standard](https://agentskills.io/specification),
  [Anthropic's platform docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview),
  the Claude Code plugin reference, MCP, and A2A all move — and they sometimes
  disagree. If a limit, field, or method name in
  `plugins/make-skill/skills/make-skill/references/` no longer matches upstream,
  a correction with a link to the current source is the most valuable PR there is.
- Support for a distribution channel that behaves differently from the documented
  four.

Please open an issue first for anything that changes a workflow's shape — the
canon is opinionated on purpose, and it's cheaper to discuss the opinion than the
diff.

## Running the checks

The validator is Python **stdlib only** — no virtualenv, no install:

```bash
python3 test/validate.py
```

Exit 0 prints `PASS: …`. Every failure names the file and the rule.

To run the entire CI suite locally exactly as GitHub does — validator, four
negative self-tests, installer functional tests against a throwaway `HOME`, and
YAML parsing:

```bash
python3 - <<'PY'
import yaml, subprocess, os, tempfile
d = yaml.safe_load(open('.github/workflows/validate.yml'))
env = dict(os.environ); env['HOME'] = tempfile.mkdtemp()
for s in d['jobs']['validate']['steps']:
    if 'run' not in s: continue
    r = subprocess.run(['bash','-c',s['run']], capture_output=True, text=True, env=env)
    print(('PASS' if r.returncode==0 else 'FAIL'), s['name'])
    if r.returncode: print(r.stdout[-800:], r.stderr[-800:])
PY
```

(That snippet needs `pyyaml`, which CI installs; the validator itself does not.)

## Rules the validator enforces

Fail these and CI stops you, so check them before pushing:

- **Version sync.** `.claude-plugin/marketplace.json`, `plugins/make-skill/.claude-plugin/plugin.json`,
  `package.json` and the top `## vX.Y.Z` entry in `CHANGELOG.md` carry the same
  semver, bumped together.
- **Spec-legal front-matter, by both rulebooks.** `name` matches its directory
  and the standard's charset, carries no angle brackets and no `anthropic`/
  `claude` (Anthropic's Skills API rejects those on upload); `description`
  ≤ 1024 chars, third person, no angle brackets; only fields from the spec or
  the Claude Code extension set present; the `SKILL.md` **body** under 500 lines
  and under 5000 estimated tokens (chars/4 — no tokenizer in the stdlib).
- **Reference files stay navigable.** Each one is linked from `SKILL.md`, opens
  with a `**Load this when:**` condition, and — past 100 lines — a `## Contents`
  list, because a partial `head` read is what an agent often gets.
- **Manifest conformance.** Both manifests carry `$schema` and only fields Claude
  Code recognizes, component paths are `./`-relative and stay inside the plugin,
  the marketplace name is not reserved, and nothing but the manifest sits in
  `.claude-plugin/`. A second CI job runs Anthropic's own checker —
  `claude plugin validate ./plugins/make-skill --strict` and
  `claude plugin validate . --strict` — which you can run locally if you have the
  `claude` CLI.
- **No stray `SKILL.md`.** One may exist only under `plugins/*/skills/*/` — the
  skills CLI installs every other one it finds as a real skill on every agent.
  Skeletons are named `SKILL.template.md`.
- **Reference files must be reachable** from `SKILL.md`, one level deep, and no
  link may escape the skill directory (packagers ship that directory alone).
- **No relative links in `cursor/rules/*.mdc`** — those files get copied into
  other people's projects, where a relative link dangles.

- **The evaluation suite stays real.** `test/evals/triggers.json` keeps ~20
  queries with at least six near-miss negatives, and `test/evals/scenarios.json`
  keeps at least three behavioral scenarios whose `files` all exist. Fixtures
  live in `test/evals/fixtures/` and are never named `SKILL.md`.

## Evaluations

`test/validate.py` proves the evaluations exist and are well-formed; it cannot
run them. They are data, and the runner is you with an agent — see
[test/evals/README.md](test/evals/README.md) for the procedure, the 0.5 trigger
threshold, and the train/validation split. Run them before any release that
touches `SKILL.md` or a reference file, on every model you claim support for.

Changing the `description` without re-running `triggers.json` is the one edit
that silently degrades the skill: it can start firing on "review my pull
request" and stealing turns from every other skill installed.

## Adding a rule to the validator

Any new rule needs a **negative test**: a deliberately broken copy that must make
the validator exit non-zero. Add it to the matching step in
`.github/workflows/validate.yml`. A validator nobody has watched fail proves
nothing — this repo shipped a vacuous self-test for three releases and only found
out when the workflow was read line by line.

## Commits and releases

Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`). Releases are cut from a
`v*` tag by `.github/workflows/release.yml`, which is **off unless the repo
variable `RELEASE_ENABLED` is `true`** — forks decide for themselves. Publishing
to npm stays a human step (2FA).

You do not need to bump the version in a PR; say what changed and the maintainer
will fold it into the next release.


### The family catalogue moves with the release

`sshlg-skills` — the launcher that installs and updates the whole ssheleg family — pins every
member's version in its own `skills.json`. **A release that does not bump that pin is invisible.**
`npx sshlg-skills list` keeps reporting the previous version, `update` keeps installing it, and
anyone comparing their install against `list` is told the wrong number with nothing to reveal it.

So a release is not finished at `npm publish`:

```bash
# in ssheleg/sshlg-skills
#   1. bump this member's "version" in skills.json
#   2. bump the launcher's own version, changelog, tag
npm publish --access public
npx --yes sshlg-skills@latest list   # the new number must appear here
```

This is not hypothetical. On 2026-07-29 `agent-sync` 1.3.4 was on npm, installed everywhere, and
`list` still said 1.3.3 — so a project whose onboarding compares the running version against `list`
told every agent to update to a version it already had.

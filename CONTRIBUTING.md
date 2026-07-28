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
  MCP, and A2A all move. If a limit, field, or method name in
  `plugins/make-skill/skills/make-skill/references/` no longer matches upstream,
  a correction with a link to the current spec is the most valuable PR there is.
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
- **Spec-legal front-matter.** `name` matches its directory and the standard's
  charset; `description` ≤ 1024 chars; only spec fields present; `SKILL.md` under
  500 lines.
- **No stray `SKILL.md`.** One may exist only under `plugins/*/skills/*/` — the
  skills CLI installs every other one it finds as a real skill on every agent.
  Skeletons are named `SKILL.template.md`.
- **Reference files must be reachable** from `SKILL.md`, one level deep, and no
  link may escape the skill directory (packagers ship that directory alone).
- **No relative links in `cursor/rules/*.mdc`** — those files get copied into
  other people's projects, where a relative link dangles.

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

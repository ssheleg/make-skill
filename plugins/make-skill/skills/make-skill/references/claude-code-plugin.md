# Claude Code plugin reference — the Anthropic layer

**Load this when:** building, retrofitting, or auditing anything that ships as a
**Claude Code plugin or marketplace** — writing `plugin.json` / `marketplace.json`,
adding agents / hooks / MCP / LSP / monitors to a plugin, or resolving a
`claude plugin validate` failure.

Upstream (read against these, not from memory — the schema grows every release):
- Plugins reference — <https://code.claude.com/docs/en/plugins-reference>
- Marketplaces — <https://code.claude.com/docs/en/plugin-marketplaces>
- Skills — <https://code.claude.com/docs/en/skills>

*Read from the docs on 2026-07-30 against Claude Code 2.1.212, and again 2026-08-28
against 2.1.236 — that pass added the `archive` and `command` sources, entry-level
`headersHelper`, bare-name sources under `metadata.pluginRoot`, and `"skills": ["."]`,
all of which landed between the two readings. Re-read before
trusting a version-gated field in a new quarter.*

The [Agent Skills spec](https://agentskills.io/specification) (see
`references/agent-skills-spec.md`) is the portable floor. **This file is the
host layer on top of it**: everything here is Claude-Code-specific and is
ignored by other agents — so nothing here may be load-bearing for a skill that
must also run on Cursor, Codex, or the skills CLI.

## Contents

- The gate: `claude plugin validate`
- `plugin.json` — `.claude-plugin/plugin.json` (field table)
- `marketplace.json` — `.claude-plugin/marketplace.json` (fields, reserved names, plugin entries)
- Component locations
- Skill frontmatter — host extensions
- Agents, hooks, MCP inside a plugin
- LSP servers and monitors
- Path variables
- Caching, symlinks, path traversal
- Skills-directory plugins
- CLI
- Conformance checklist

## The gate: `claude plugin validate`

```bash
claude plugin validate ./plugins/<name> --strict   # the plugin manifest
claude plugin validate . --strict                  # the marketplace manifest
```

Both must exit 0. Rules that decide the outcome:

- Unrecognized top-level fields are **warnings**, not errors — the plugin still
  loads. `--strict` turns them into failures, which is what you want in CI:
  a field from another ecosystem, or one typo'd by two characters, is caught
  before publish.
- Wrong **types** always fail (`keywords` as a string, not an array).
- It runs offline and needs no auth, so it belongs in CI:
  `npm i -g @anthropic-ai/claude-code && claude plugin validate … --strict`.
- **It validates the MANIFEST, whatever the docs promise.** The troubleshooting
  table says the command checks "`plugin.json`, skill/agent/command frontmatter,
  and `hooks/hooks.json`"; on 2.1.212 a `SKILL.md` carrying an invented
  front-matter key passed `--strict` untouched, and the output names only the
  manifest it read. Keep front-matter rules in your own validator — this gate
  does not cover them.

## `plugin.json` — `.claude-plugin/plugin.json`

The manifest is optional (components auto-discover, name falls back to the
directory). Ship one anyway: without it there is no version, no metadata, and
nothing to validate. **`name` is the only required field.**

| Field | Type | Notes |
|---|---|---|
| `$schema` | string | `https://json.schemastore.org/claude-code-plugin-manifest.json` — editor autocomplete; ignored at load |
| `name` | string | **required**, kebab-case, no spaces; namespaces every component (`plugin-dev:agent-creator`). A marketplace entry listing it under another name wins for `enabledPlugins` and `/plugin` |
| `displayName` | string | UI label, may contain spaces/case; never used for lookup (CC ≥ 2.1.143) |
| `version` | string | semver. **Set it and you must bump it** — CC uses the version as the cache key, so new commits under an unchanged version never reach users. Omit it entirely and the git SHA is the version (every commit ships) |
| `description`, `author{name,email,url}`, `homepage`, `repository`, `license`, `keywords[]` | | metadata |
| `defaultEnabled` | boolean | `false` = installs disabled until the user opts in (CC ≥ 2.1.154). The marketplace entry's copy wins over this one; an existing `enabledPlugins` entry wins over both |
| `skills` | string\|array | extra skill dirs — **adds to** the default `skills/` scan. One exception: in a marketplace entry whose `source` resolves to the marketplace ROOT, the listed subdirectories REPLACE that scan (if none of them exist, the default scan runs after all) |
| `commands`, `agents`, `workflows`, `outputStyles` | string\|array | **replace** the default folder. To keep it, list it: `["./commands/", "./extras/"]` |
| `hooks`, `mcpServers`, `lspServers` | string\|array\|object | path(s) or inline config; own merge rules |
| `experimental.themes`, `experimental.monitors` | string\|array | still moving; top level warns today, will be required under `experimental` |
| `userConfig` | object | values prompted at enable time — `type` (`string`/`number`/`boolean`/`directory`/`file`), `title`, `description` required; `sensitive`, `required`, `default`, `multiple`, `min`/`max` optional |
| `channels` | array | message channels; each `server` must match a key in `mcpServers` |
| `dependencies` | array | `["helper-lib", {"name":"secrets-vault","version":"~2.1.0"}]` |

All component paths are **relative to the plugin root and start with `./`**.

`${user_config.KEY}` substitutes in MCP/LSP configs and hook commands, and in
skill/agent content for non-sensitive values — but **not** in shell-form hook
commands, monitor commands, or MCP `headersHelper` (a shell would execute
whatever the value contains); those read `CLAUDE_PLUGIN_OPTION_<KEY>` from the
environment instead. Sensitive values go to the OS keychain (~2 KB shared
budget), never to `settings.json`.

## `marketplace.json` — `.claude-plugin/marketplace.json`

| Field | Required | Notes |
|---|---|---|
| `name` | yes | kebab-case, public (`/plugin install x@<name>`). One marketplace per name per user — a second add **replaces** the first |
| `owner` | yes | `{name}` required, `email`/`url` optional |
| `plugins[]` | yes | entries, below |
| `$schema` | no | `https://json.schemastore.org/claude-code-marketplace.json` |
| `description`, `version` | no | also accepted under `metadata` for backward compatibility |
| `metadata.pluginRoot` | no | prefix for relative sources (`"./plugins"` → `"source": "formatter"`) |
| `allowCrossMarketplaceDependenciesOn` | no | marketplaces this one's plugins may depend on; anything else is blocked at install |
| `renames` | no | old plugin name → new name, or `null` if removed; migrates existing users (CC ≥ 2.1.193) |

**There is no top-level `homepage`, `repository`, or `license`.** Those are
plugin-entry fields; at marketplace level they are unrecognized and `--strict`
fails on them. Put the project URL in `owner.url`.

**Reserved marketplace names** (third-party use blocked, re-checked on every
load, so a name can become reserved under a live marketplace):
`claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`,
`claude-plugins-community`, `claude-community`, `anthropic-marketplace`,
`anthropic-plugins`, `agent-skills`, `anthropic-agent-skills`,
`knowledge-work-plugins`, `life-sciences`, `claude-for-legal`,
`claude-for-financial-services`, `financial-services-plugins`,
`first-party-plugins`, `healthcare` — plus anything that impersonates them
(`official-claude-plugins`, `anthropic-plugins-v2`).

### Plugin entries

Required: `name` and `source`. Any plugin-manifest field is allowed, plus the
marketplace-only `source`, `category`, `tags`, `strict`, `relevance`,
`defaultEnabled`.

| Source | Shape |
|---|---|
| relative path | `"./plugins/my-plugin"` — must start with `./`, resolved from the marketplace **root**, not `.claude-plugin/` |
| `github` | `{"source":"github","repo":"owner/repo","ref?":"main","sha?":"…"}` |
| `url` | `{"source":"url","url":"https://…​.git","ref?":…,"sha?":…}` |
| `git-subdir` | `{"source":"git-subdir","url":"…","path":"packages/x","ref?":…,"sha?":…}` — sparse clone |
| `npm` | `{"source":"npm","package":"@scope/pkg","version?":…,"registry?":…}` — no git SHA to fall back on, so set `version` in the manifest or the entry, else it resolves to `unknown` and updates never fire |
| `archive` **2.1.224+** | `{"source":"archive","url":"https://…/x-2.1.0.zip","sha256?":"<64 hex>"}` — a zip over HTTPS, **no git and no npm on the machine**. The digest is optional and is the only thing standing between a URL and whatever is behind it today; set it |
| `command` **2.1.229+** | `{"source":"command","command":"my-tool plugin-path","timeout?":60,"mode?":"copy"}` — a local command prints the directory. `timeout` defaults to 60s, max 600; `mode` is `copy` (default) or `link`. An organisation can be configured to refuse this entire class with `disableCommandPluginSources`, so it is the one source that may be unavailable for reasons no error in your repo explains |

**Bare-name sources, 2.1.239+.** With `metadata.pluginRoot` set on the marketplace,
an entry may write `"source": "my-plugin"` and have it resolve under that root — the
`./` requirement above applies only without it.

`sha` beats `ref` when both are set. **Marketplace source ≠ plugin source**: the
first says where `marketplace.json` lives (supports `ref` only), the second where
each plugin comes from (`ref` and `sha`).

`strict` (default `true`): `plugin.json` is the authority and the entry may add
to it. `strict: false` makes the entry the entire definition — and a
`plugin.json` that also declares components is then a load error.

**`headersHelper` on an entry, 2.1.238+ — and it needs `strict: false`.** Beside
`source`, it names a command that mints HTTP headers for a private registry, and it runs
**only** when that one plugin is installed or updated. The marketplace-level form is
different: declared in `extraKnownMarketplaces` on a `url` marketplace, it runs before
every catalog fetch and archive download on that origin, and one run is reused for 60
seconds. Both are separate from the MCP `headersHelper` documented later in this file.

The command's contract, because each clause is a way to fail silently: one JSON object of
header names to string values on stdout, exit 0, **within 10 seconds**; at most 500
printable ASCII characters with no run of four spaces; run through `sh` (or `cmd.exe`)
from `~/.claude`. Claude Code **strips every variable whose name contains `TOKEN`,
`SECRET`, `KEY` or `AUTH`** from its environment — so a helper that reads its credential
from one of those is handed nothing, and the failure looks like a permissions problem at
the registry. It receives `CLAUDE_CODE_MARKETPLACE_URL`, `CLAUDE_CODE_MARKETPLACE_NAME`,
`CLAUDE_CODE_PLUGIN_NAME` and `CLAUDE_CODE_PLUGIN_ARCHIVE_URL` instead. The user has to
accept the command before it runs at all.

Version resolution order: `plugin.json` → marketplace entry → git SHA →
`unknown`.

## Component locations

| Component | Default location |
|---|---|
| manifest | `.claude-plugin/plugin.json` |
| skills | `skills/<name>/SKILL.md` — and **`"skills": ["."]` is legal from 2.1.221**: it scans the plugin ROOT for `<name>/SKILL.md` instead of `skills/`, which is what a repository whose skills sit at the top level needs |
| commands | `commands/*.md` (flat skills; prefer `skills/` for new plugins) |
| agents | `agents/*.md` |
| workflows | `workflows/*.js` |
| output styles | `output-styles/*.md` |
| hooks | `hooks/hooks.json` |
| MCP | `.mcp.json` |
| LSP | `.lsp.json` |
| monitors | `monitors/monitors.json` |
| themes | `themes/*.json` — `base` preset + sparse `overrides` |
| executables | `bin/` — on the Bash tool's PATH while enabled |
| defaults | `settings.json` (only `agent` and `subagentStatusLine` keys) |

**Only `plugin.json` goes inside `.claude-plugin/`.** Those are the DEFAULT
locations, all at the plugin root — a manifest path field may point anywhere
else inside the plugin (`"commands": ["./specialized/deploy.md"]`), and from
2.1.140 Claude Code warns in `claude plugin list` when a manifest key leaves a
default folder unscanned. What never works is burying components in
`.claude-plugin/`: they load as nothing while the plugin still "works", which is
why that one costs an afternoon.

A plugin-root `CLAUDE.md` is **not** loaded as context. Ship instructions as a
skill.

A plugin root `SKILL.md` with no `skills/` dir and no `skills` field loads as a
single-skill plugin (CC ≥ 2.1.142) — set frontmatter `name`, or the invocation
name becomes the install directory, which for marketplace installs is a version
string that changes on every update.

## Skill frontmatter — host extensions

Portable floor (`name`, `description`, `license`, `compatibility`, `metadata`,
`allowed-tools`) is in `references/agent-skills-spec.md`. **`allowed-tools` is
looser here than in the spec**: Claude Code takes a space- OR comma-separated
string OR a YAML list, the spec takes only the space-separated string. Write the
spec form — a list works here and breaks everywhere else. Claude Code also
reads:

| Field | Effect |
|---|---|
| `when_to_use` | extra trigger text appended to `description` in the listing |
| `argument-hint`, `arguments` | autocomplete hint; named `$name` substitutions |
| `disable-model-invocation` | `true` = only the user can fire it (`/name`) |
| `user-invocable` | `false` = hidden from the `/` menu |
| `disallowed-tools` | tools removed while the skill is active |
| `model`, `effort` | override for the turn that invoked the skill |
| `context: fork`, `agent`, `background` | run the skill in a subagent |
| `hooks` | hooks scoped to this skill's lifecycle |
| `paths` | globs that gate automatic activation |
| `shell` | `bash` (default) or `powershell` for inline `` !`cmd` `` |

Booleans accept `yes/no/on/off/1/0` in any case as of CC 2.1.218 — earlier
versions read only `true`/`false`, so write `true`/`false`.

Listing budget: `description` + `when_to_use` is truncated at **1,536 chars** in
the skill listing; the spec's own `description` cap of 1024 is the tighter rule
and stays the one to hold.

Command name: a plugin skill is `/<plugin>:<skill-dir>`, and frontmatter `name`
replaces the last segment (`name: fancy` → `/my-plugin:fancy`). Personal and
project skills take the command name from the directory; `name` is only a label
there.

## Agents, hooks, MCP inside a plugin

- **Agents** (`agents/*.md`) support `name`, `description`, `model`, `effort`,
  `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`,
  `isolation` (only value: `"worktree"`). `hooks`, `mcpServers`, and
  `permissionMode` are **rejected** for plugin-shipped agents. They appear as
  `<plugin>:<agent>`.
- **Hooks** use the standard event set (`SessionStart`, `PreToolUse`,
  `PostToolUse`, `UserPromptSubmit`, `Stop`, `SessionEnd`, …) and types
  `command`, `http`, `mcp_tool`, `prompt`, `agent`. Event names are
  case-sensitive; scripts need `chmod +x` and a shebang.
- A hook targeting the plugin's **own** MCP server must use scoped names:
  matcher/`if` take `mcp__plugin_<plugin>_<server>__<tool>`, and an `mcp_tool`
  hook's `server` takes `plugin:<plugin>:<server>`. A matcher on the bare server
  key never fires.

## LSP servers and monitors

The load condition above promises both; here is the whole of each.

**LSP** — `.lsp.json` at the plugin root, or `lspServers` inline. Required per
server: `command` (binary must be on PATH — the plugin does NOT ship it) and
`extensionToLanguage`. Optional: `args`, `transport` (`stdio` default or
`socket`), `env`, `initializationOptions`, `settings`, `workspaceFolder`,
`startupTimeout`, `shutdownTimeout`, `restartOnCrash` (default `true`),
`maxRestarts`, `diagnostics` (default `true`). `restartOnCrash` and
`shutdownTimeout` need CC ≥ 2.1.205 — before that, setting either made Claude
Code skip the server silently, visible only under `claude --debug`. When two
enabled servers claim the same extension, the first registered wins and the
other never starts; an invalid server is skipped and no longer blocks a valid
one (also 2.1.205).

```json
{ "go": { "command": "gopls", "args": ["serve"],
          "extensionToLanguage": { ".go": "go" } } }
```

**Monitors** — `monitors/monitors.json`, or `experimental.monitors` inline (a
path string there loads from a custom location). Array of `{name, command,
description, when?}`; `when` is `"always"` (default) or
`"on-skill-invoke:<skill>"`. Each runs as a background process for the session
and every stdout line reaches Claude as a notification. Interactive CLI only,
unsandboxed at hook trust level, skipped where the Monitor tool is unavailable,
and never loaded from a project-scope `@skills-dir` plugin. `${CLAUDE_PLUGIN_ROOT}`,
`${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PROJECT_DIR}` and `${ENV_VAR}` substitute;
`${user_config.*}` is rejected outright (it would reach a shell), and monitor
processes get no `CLAUDE_PLUGIN_OPTION_*` either — read the value from a config
file. Disabling a plugin mid-session does not stop a running monitor.

## Path variables

| Variable | Resolves to |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | the plugin's install directory — **changes on every update**, never store state there |
| `${CLAUDE_PLUGIN_DATA}` | `~/.claude/plugins/data/<id>/`, survives updates; for `node_modules`, venvs, caches |
| `${CLAUDE_PROJECT_DIR}` | project root |
| `${CLAUDE_SKILL_DIR}` | the skill's own directory (skill content and `allowed-tools` Bash rules) |

They substitute in skill/agent content, hook and monitor commands, MCP
`command`/`args`/`env` (or `url`/`headers`/`headersHelper`), and LSP
`command`/`args`/`env`/`workspaceFolder`. In shell-form commands, quote them:
`"${CLAUDE_PLUGIN_ROOT}"/scripts/x.sh`.

**They are NOT exported to the Bash tool.** Substitution into text and export
into a process are different things: a hook script sees `CLAUDE_PLUGIN_ROOT` in
its environment, a `Bash` tool call does not (measured empty on 2.1.220). So a
skill that *prints* the variable gets a real path, and a skill that tells the
agent to *run* a command containing it gets `/skills/...` and a missing-file
error. Put runnable scripts in the plugin's `bin/`, which lands on the Bash
tool's PATH, and call them by name — `references/host-capabilities.md` →
*Scripts*.

**Portability:** all four are Claude Code inventions. A skill that must also run
on other agents references bundled files by **relative path** and treats the
variables as an optimization, not the contract.

## Caching, symlinks, path traversal

Marketplace plugins are copied into `~/.claude/plugins/cache` per version;
orphaned versions are cleaned up ~14 days later. Consequences:

- `../shared-utils` — anything outside the plugin root — **does not exist after
  install**. It was never copied.
- Symlinks inside the plugin dir are preserved; symlinks to elsewhere in the
  same marketplace are **dereferenced** (content copied); symlinks outside the
  marketplace are skipped. This is why a meta-plugin can link sibling skills —
  and why the same trick still breaks on non-Claude agents, which install only
  the skill folder.

## Skills-directory plugins

A folder under a skills directory with `.claude-plugin/plugin.json` loads next
session as `<name>@skills-dir` — no marketplace, no install, discovered in
place. Scaffold with `claude plugin init <name> [--with skills agents hooks mcp
lsp output-style channel]`.

`~/.claude/skills/` → personal, every project. `<cwd>/.claude/skills/` →
project-scope, loads only after the workspace trust dialog, MCP servers still
need per-server approval, monitors don't load at all. Project-scope
`@skills-dir` plugins do **not** walk up to the repo root — launch Claude from
the repository root or run `/reload-plugins`.

`SKILL.md` edits apply live; `hooks/`, `.mcp.json`, `agents/`, `output-styles/`
need `/reload-plugins`. Disable with `claude plugin disable <name>@skills-dir`.

## CLI

| Command | Use |
|---|---|
| `claude plugin validate <path> [--strict]` | the conformance gate, offline |
| `claude plugin init <name> [--with …]` | scaffold a `@skills-dir` plugin |
| `claude plugin install <name>@<marketplace> [-s user\|project\|local] [--config k=v]` | install |
| `claude plugin update <name>@<marketplace>` | update. Docs accept a bare `<name>`; **2.1.212 does not** — `claude plugin update make-skill` answers `Plugin "make-skill" not found`, exits 0, changes nothing. Always pass `name@marketplace` |
| `claude plugin enable\|disable <name>@<marketplace>` | toggle without uninstalling |
| `claude plugin uninstall <name>@<marketplace> [--keep-data] [--prune]` | remove (deletes the data dir unless `--keep-data`) |
| `claude plugin list [--json]` | installed plugins, versions, source, state |
| `claude plugin details <name>` | component inventory + **always-on vs on-invoke token cost** — run it before claiming a plugin is cheap |
| `claude plugin tag [path] [--push]` | cut the release tag for dependency resolution |
| `claude plugin marketplace add\|update\|remove\|list <repo>` | manage catalogues |

`claude --debug` prints plugin loading, manifest errors, and component
registration — the first stop when a component silently doesn't appear.

## Conformance checklist

- [ ] `claude plugin validate ./plugins/<name> --strict` → exit 0
- [ ] `claude plugin validate . --strict` → exit 0 (marketplace)
- [ ] `$schema` set in both manifests
- [ ] `name` kebab-case and identical in `plugin.json`, the marketplace entry,
      and the plugin directory
- [ ] `version` present and bumped this release (or deliberately absent for
      SHA-based iteration)
- [ ] marketplace `name` not on the reserved list
- [ ] every component path relative and starting with `./`
- [ ] only `plugin.json` inside `.claude-plugin/`; `skills/`, `commands/`,
      `agents/`, `hooks/` at the plugin root
- [ ] no path escapes the plugin root (`../`), no symlink leaves the marketplace
- [ ] scripts referenced through `${CLAUDE_PLUGIN_ROOT}`, state through
      `${CLAUDE_PLUGIN_DATA}`, and both treated as Claude-only conveniences
- [ ] plugin agents free of `hooks` / `mcpServers` / `permissionMode`
- [ ] `claude plugin details <name>` token cost is one you would pay in every
      session

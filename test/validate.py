#!/usr/bin/env python3
"""Structural validator for the make-skill plugin repo. Exit 0 = pass."""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "make-skill"
errors = []


def fail(m):
    errors.append(m)


def load_json(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        fail(f"missing file: {rel}")
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        fail(f"invalid JSON in {rel}: {e}")
        return None


mkt = load_json(".claude-plugin/marketplace.json")
plg = load_json("plugins/make-skill/.claude-plugin/plugin.json")
pkg = load_json("package.json")

# --- Claude Code manifest conformance ----------------------------------------
# https://code.claude.com/docs/en/plugins-reference (read 2026-07-30, CC 2.1.212)
# `claude plugin validate <path> --strict` is the upstream tie-breaker; these
# rules keep the repo green without needing the CLI installed.
MKT_TOP_KEYS = {
    "$schema", "name", "owner", "plugins", "description", "version", "metadata",
    "allowCrossMarketplaceDependenciesOn", "renames",
}
PLUGIN_MANIFEST_KEYS = {
    "$schema", "name", "displayName", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "defaultEnabled", "skills", "commands",
    "agents", "workflows", "hooks", "mcpServers", "outputStyles", "lspServers",
    "experimental", "userConfig", "channels", "dependencies",
}
# a marketplace entry may carry any plugin-manifest field plus these
MKT_ENTRY_KEYS = PLUGIN_MANIFEST_KEYS | {"source", "category", "tags", "strict", "relevance"}
# component paths — every one must be relative and start with "./"
PATH_FIELDS = ("skills", "commands", "agents", "workflows", "outputStyles",
               "hooks", "mcpServers", "lspServers")
# reserved for official Anthropic use; re-checked on every load, so a marketplace
# under one of these names simply stops loading
RESERVED_MARKETPLACE_NAMES = {
    "claude-code-marketplace", "claude-code-plugins", "claude-plugins-official",
    "claude-plugins-community", "claude-community", "anthropic-marketplace",
    "anthropic-plugins", "agent-skills", "anthropic-agent-skills",
    "knowledge-work-plugins", "life-sciences", "claude-for-legal",
    "claude-for-financial-services", "financial-services-plugins",
    "first-party-plugins", "healthcare",
}


def check_paths(where, obj):
    """Component paths must be relative, start with './', and stay in the plugin."""
    for field in PATH_FIELDS:
        val = obj.get(field)
        vals = val if isinstance(val, list) else [val]
        for v in vals:
            if not isinstance(v, str):
                continue  # inline hook/MCP/LSP config, not a path
            if not v.startswith("./"):
                fail(f"{where}: {field} path {v!r} must be relative and start with './'")
            elif ".." in v.split("/"):
                fail(f"{where}: {field} path {v!r} escapes the plugin root — "
                     "files outside it are never copied into the plugin cache")


mkt_name = mkt_ver = None
if mkt:
    if mkt.get("$schema") != "https://json.schemastore.org/claude-code-marketplace.json":
        fail("marketplace.json: missing/wrong $schema "
             "(https://json.schemastore.org/claude-code-marketplace.json)")
    unknown = sorted(set(mkt) - MKT_TOP_KEYS)
    if unknown:
        fail(f"marketplace.json: fields Claude Code does not recognize at marketplace "
             f"level: {unknown} — 'claude plugin validate . --strict' fails on these "
             "(homepage/repository/license belong to the plugin entry)")
    if mkt.get("name") in RESERVED_MARKETPLACE_NAMES:
        fail(f"marketplace.json: name {mkt.get('name')!r} is reserved for Anthropic — "
             "the marketplace would stop loading")
    owner = mkt.get("owner")
    if not isinstance(owner, dict) or not owner.get("name"):
        fail("marketplace.json: owner.name is required")

    plugins = mkt.get("plugins") or []
    if not plugins:
        fail("marketplace.json: plugins[] empty")
    else:
        p0 = plugins[0]
        unknown = sorted(set(p0) - MKT_ENTRY_KEYS)
        if unknown:
            fail(f"marketplace.json: plugin entry has unrecognized fields {unknown}")
        mkt_name = p0.get("name")
        mkt_ver = p0.get("version")
        if not p0.get("displayName"):
            fail("marketplace.json: plugin entry has no displayName — the UI label "
                 "the user actually reads (displayName is a plugin-ENTRY field; the "
                 "marketplace root does not take one)")
        src = p0.get("source", "")
        if not isinstance(src, str):
            fail("marketplace.json: this repo ships its plugin in-tree — source must be "
                 "a relative path string")
            src = ""
        elif not src.startswith("./"):
            fail(f"marketplace.json: source {src!r} must start with './' "
                 "(resolved from the marketplace root, not .claude-plugin/)")
        srcdir = os.path.normpath(os.path.join(ROOT, src))
        if not os.path.isfile(os.path.join(srcdir, ".claude-plugin", "plugin.json")):
            fail(f"marketplace source {src!r} has no .claude-plugin/plugin.json")
        elif os.path.basename(srcdir) != mkt_name:
            fail(f"marketplace.json: source dir {os.path.basename(srcdir)!r} != plugin "
                 f"name {mkt_name!r}")
        check_paths("marketplace.json plugin entry", p0)

if plg:
    if plg.get("$schema") != "https://json.schemastore.org/claude-code-plugin-manifest.json":
        fail("plugin.json: missing/wrong $schema "
             "(https://json.schemastore.org/claude-code-plugin-manifest.json)")
    unknown = sorted(set(plg) - PLUGIN_MANIFEST_KEYS)
    if unknown:
        fail(f"plugin.json: fields Claude Code does not recognize: {unknown} — "
             "'claude plugin validate <dir> --strict' fails on these")
    if not plg.get("displayName"):
        fail("plugin.json: no displayName — canon requires the UI label in both "
             "the manifest and the marketplace entry")
    check_paths("plugin.json", plg)

# only the manifest may live in .claude-plugin/ — components buried there load as
# nothing, and the plugin still "works", which is why this one is expensive
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
    if os.path.basename(dirpath) != ".claude-plugin":
        continue
    rel = os.path.relpath(dirpath, ROOT)
    for extra in sorted(set(filenames) - {"marketplace.json", "plugin.json"}):
        fail(f"{rel}/{extra}: only the manifest belongs in .claude-plugin/")
    for extra in sorted(dirnames):
        fail(f"{rel}/{extra}/: component directories belong at the plugin root, "
             "not inside .claude-plugin/ — they load as nothing here")

plg_name = plg.get("name") if plg else None
plg_ver = plg.get("version") if plg else None

# --- SKILL.md: Agent Skills spec rules + house canon -------------------------
# Two authorities, both enforced:
#   https://agentskills.io/specification                      (portable format)
#   https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
# The Anthropic layer adds rules the open standard is silent about — reserved
# words and XML tags in name/description — and the Skills API is the only place
# they are enforced, i.e. on someone else's machine. Read 2026-08-03.
SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
RESERVED_NAME_WORDS = ("anthropic", "claude")
# One rule, one pattern — compared against scripts/audit_skill.py further down,
# so the shipped auditor and this validator cannot drift apart. The leading
# non-space class keeps ordinary prose ("a < b > c") out of it.
XML_TAG_PATTERN = r"<[^<>\s][^<>]*>"
XML_TAG_RE = re.compile(XML_TAG_PATTERN)
# "Always write in third person" — the description is injected into the system
# prompt, and first/second person degrades skill selection.
PERSON_RE = re.compile(
    r"\b(?:I can|I will|I'll|I help|I'm|you can use|you should use|you may use|"
    r"this skill (?:lets|allows|helps) you)\b", re.I)
# Claude Code host extensions (https://code.claude.com/docs/en/skills). Legal in a
# SKILL.md and ignored by every other agent — so they may tune behavior here, but
# nothing portable may depend on one. Anything outside both sets is a typo.
CC_SKILL_KEYS = {
    "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "disallowed-tools", "model", "effort", "context", "agent",
    "background", "hooks", "paths", "shell",
}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BODY_MAX_LINES = 500
BODY_MAX_TOKENS = 5000
# The working limits: 5% under each ceiling. See the budget checks for why.
BODY_TARGET_TOKENS = 4750
DESC_TARGET_CHARS = 970
CHARS_PER_TOKEN = 3.9  # measured, not assumed — see the comment at the budget check
# Anthropic best practices: a reference longer than this gets a table of contents,
# because a partial `head` read is what the agent often sees.
REF_TOC_MIN_LINES = 100


def strip_quotes(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def parse_frontmatter(text):
    """YAML subset: top-level scalars, folded/literal blocks, one nested map."""
    data, key, mode = {}, None, None
    for raw in text.split("\n"):
        if not raw.strip():
            continue
        if raw[0] not in " \t":
            m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
            if not m:
                key, mode = None, None
                continue
            key, val = m.group(1), m.group(2).strip()
            if val in (">", "|", ">-", "|-", ">+", "|+"):
                data[key], mode = "", "block"
            elif val == "":
                data[key], mode = {}, "map"
            else:
                data[key], mode = strip_quotes(val), None
        elif mode == "block":
            data[key] = (data[key] + " " + raw.strip()).strip()
        elif mode == "map":
            m = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", raw)
            if m:
                data[key][m.group(1)] = strip_quotes(m.group(2).strip())
    return data


SKILL_DIR = os.path.join(ROOT, "plugins/make-skill/skills/make-skill")
skill_path = os.path.join(SKILL_DIR, "SKILL.md")
fm_name = None
skill_meta = {}
skill_txt = ""
if not os.path.isfile(skill_path):
    fail("missing SKILL.md")
else:
    skill_txt = open(skill_path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", skill_txt, re.S)
    if not m:
        fail("SKILL.md: no frontmatter")
    else:
        fm = parse_frontmatter(m.group(1))

        unknown = sorted(set(fm) - SPEC_KEYS - CC_SKILL_KEYS)
        if unknown:
            fail(f"SKILL.md: front-matter keys in neither the Agent Skills spec nor "
                 f"the Claude Code extension set: {unknown}")

        # name — spec: 1-64 chars, [a-z0-9-], no leading/trailing/double hyphen,
        # must equal the parent directory name
        fm_name = fm.get("name")
        if not isinstance(fm_name, str) or not fm_name:
            fail("SKILL.md: empty/missing name")
            fm_name = None
        else:
            if len(fm_name) > 64:
                fail(f"SKILL.md: name is {len(fm_name)} chars, spec max is 64")
            if not NAME_RE.match(fm_name):
                fail(f"SKILL.md: name {fm_name!r} violates the spec charset "
                     "(lowercase a-z0-9 and single internal hyphens only)")
            if fm_name != os.path.basename(SKILL_DIR):
                fail(f"SKILL.md: name {fm_name!r} != directory "
                     f"{os.path.basename(SKILL_DIR)!r} (spec)")
            for word in RESERVED_NAME_WORDS:
                if word in fm_name.lower():
                    fail(f"SKILL.md: name {fm_name!r} contains the reserved word "
                         f"{word!r} — Claude Code loads it, the Skills API rejects "
                         "the upload (platform.claude.com Agent Skills overview)")
            if XML_TAG_RE.search(fm_name):
                fail(f"SKILL.md: name {fm_name!r} contains an XML tag — rejected by "
                     "Anthropic's platform; a leftover <placeholder> is the usual cause")

        # description — spec: 1-1024 chars; canon: "Use when …" + EN/RU triggers
        desc = fm.get("description")
        if not isinstance(desc, str) or not desc.strip():
            fail("SKILL.md: empty/missing description")
        else:
            if len(desc) > 1024:
                fail(f"SKILL.md: description is {len(desc)} chars, spec max is 1024")
            elif len(desc) > DESC_TARGET_CHARS:
                # The description is the entire triggering budget, and it is the field
                # that has to grow when a near-miss skill appears (authoring.md: "say
                # what it is NOT for"). At 1003/1024 there was no room to add that
                # sentence without first cutting a trigger phrase — the same disease as
                # a body at 99% of budget, in the field that decides whether the skill
                # fires at all.
                fail(f"SKILL.md: description is {len(desc)} chars — inside the 1024 cap but "
                     f"past the {DESC_TARGET_CHARS} working limit (5% headroom). Leave room "
                     "for the 'what this is NOT for' clause a new neighbour will require")
            if not desc.lower().startswith("use when"):
                fail("SKILL.md: description must start with 'Use when …' (canon)")
            if not re.search(r"[а-яё]", desc, re.I):
                fail("SKILL.md: description must include Russian trigger phrases too (canon)")
            if XML_TAG_RE.search(desc):
                fail("SKILL.md: description contains an XML tag — rejected by "
                     "Anthropic's platform. Write the placeholder without angle brackets")
            person = PERSON_RE.search(desc)
            if person:
                fail(f"SKILL.md: description is not third person ({person.group(0)!r}) — "
                     "it is injected into the system prompt, where first/second person "
                     "degrades skill selection")

        # optional spec fields
        compat = fm.get("compatibility")
        if compat is None:
            fail("SKILL.md: no compatibility — this skill needs python3, git, gh, "
                 "node, npm and the claude CLI at different steps, and the canon's "
                 "own audit requires every runtime need declared")
        if compat is not None:
            if not isinstance(compat, str) or not compat.strip():
                fail("SKILL.md: compatibility must be a non-empty string")
            elif len(compat) > 500:
                fail(f"SKILL.md: compatibility is {len(compat)} chars, spec max is 500")
        if "license" in fm and not isinstance(fm["license"], str):
            fail("SKILL.md: license must be a string")
        if "allowed-tools" in fm and not isinstance(fm["allowed-tools"], str):
            fail("SKILL.md: allowed-tools must be a space-separated string. Claude "
                 "Code also accepts a comma-list or a YAML list; no other host does, "
                 "so the spec form is the one that travels")
        skill_meta = fm.get("metadata") or {}
        if "metadata" in fm:
            if not isinstance(skill_meta, dict):
                fail("SKILL.md: metadata must be a map of string keys to string values")
                skill_meta = {}
            else:
                for k, v in skill_meta.items():
                    if not isinstance(v, str) or not v:
                        fail(f"SKILL.md: metadata.{k} must be a non-empty string "
                             "(quote versions: version: \"1.0\")")

    # progressive disclosure — both authorities budget the BODY an agent loads on
    # activation (frontmatter is level-1 metadata, loaded for every skill anyway):
    # < 500 lines AND < 5000 tokens. No tokenizer in the stdlib, so estimate at
    # CHARS_PER_TOKEN, measured rather than assumed: tokenizing this bundle
    # (2026-08-03, cl100k) gives 3.78-4.47 chars/token, 3.9 for SKILL.md itself.
    # `claude plugin details` reports ~2.8 chars/token for the same files — its
    # estimator is deliberately pessimistic, so it always shows a bigger number
    # than this check. Treat it as the upper bound and keep headroom.
    body = re.sub(r"^---\n.*?\n---\n", "", skill_txt, count=1, flags=re.S)
    n_lines = body.count("\n") + 1
    if n_lines >= BODY_MAX_LINES:
        fail(f"SKILL.md body is {n_lines} lines, spec recommends < {BODY_MAX_LINES} "
             "— move detail into references/")
    est_tokens = int(len(body) / CHARS_PER_TOKEN)
    if est_tokens >= BODY_MAX_TOKENS:
        fail(f"SKILL.md body is ~{est_tokens} tokens ({len(body)} chars / "
             f"{CHARS_PER_TOKEN}), budget is < {BODY_MAX_TOKENS} — every token "
             "competes with the user's actual task. Move a section into "
             "references/ with a stated load trigger")
    elif est_tokens >= BODY_TARGET_TOKENS:
        # v0.10.0 shipped at ~4995 of 5000: correct in the letter, and it made
        # the next one-word correction a fight with this validator. Headroom is
        # the difference between a canon that can be fixed and one that can only
        # be traded against itself.
        fail(f"SKILL.md body is ~{est_tokens} tokens — inside the {BODY_MAX_TOKENS} "
             f"ceiling but past the {BODY_TARGET_TOKENS} working limit (5% headroom). "
             "A body at 99% of budget cannot absorb a correction. Move a section "
             "into references/ before adding one")

    # A path variable in the BODY is substituted at load time, so the agent reads
    # an absolute path where a capability was named ("Hooks, subagents, /commands,
    # /Users/.../0.10.0 and MCP servers exist only inside Claude Code" — shipped
    # in v0.9.0). It is also empty in the Bash tool, so a command built from one
    # cannot run. Neither belongs in the body: reference files may discuss it.
    for var in re.findall(r"\$\{CLAUDE_[A-Z_]+\}", body):
        fail(f"SKILL.md body contains {var} — it is substituted into the body at "
             "load time (prose becomes a filesystem path) and is empty in the Bash "
             "tool (a command built from it cannot run). Name the capability, and "
             "ship runnable scripts in the plugin's bin/, which lands on PATH")

# references/ must exist, stay one level deep, and each file must be reachable
refs_dir = os.path.join(SKILL_DIR, "references")
if not os.path.isdir(refs_dir):
    fail("missing plugins/make-skill/skills/make-skill/references/")
else:
    for entry in sorted(os.listdir(refs_dir)):
        full = os.path.join(refs_dir, entry)
        if os.path.isdir(full):
            fail(f"references/{entry}/ is nested — spec: keep references one level deep")
        elif entry.endswith(".md"):
            if f"references/{entry}" not in skill_txt:
                fail(f"references/{entry} is never referenced from SKILL.md — "
                     "an unreachable file is dead context")
            ref_txt = open(full, encoding="utf-8").read()
            if "Load this when" not in ref_txt[:600]:
                fail(f"references/{entry} has no '**Load this when:**' line near the "
                     "top — progressive disclosure needs a condition, not a pointer")
            ref_lines = ref_txt.count("\n") + 1
            if ref_lines > REF_TOC_MIN_LINES and "\n## Contents" not in ref_txt:
                fail(f"references/{entry} is {ref_lines} lines with no '## Contents' "
                     f"list — past {REF_TOC_MIN_LINES} lines an agent previews with "
                     "head and never learns what the rest of the file holds")

# no relative link may escape the skill directory (the skills CLI ships only it)
for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", skill_txt):
    if target.startswith(("http://", "https://", "mailto:", "#")):
        continue
    if target.startswith("../") or "/../" in target:
        fail(f"SKILL.md: link {target!r} escapes the skill dir — it arrives broken "
             "on every agent that installs only the skill folder")

# name sync across the three sources of truth
for label, val in {"marketplace": mkt_name, "plugin.json": plg_name, "frontmatter": fm_name}.items():
    if val != NAME:
        fail(f"name mismatch: {label}={val!r} expected {NAME!r}")

# version sync: marketplace entry, plugin.json, package.json, CHANGELOG top
# (+ an optional 5th point, SKILL.md metadata.version, checked below)
pkg_ver = pkg.get("version") if pkg else None
if not plg_ver:
    fail("plugin.json: missing version")
if not mkt_ver:
    fail("marketplace.json: plugin entry missing version")
if not pkg_ver:
    fail("package.json: missing version")
vers = {"marketplace": mkt_ver, "plugin.json": plg_ver, "package.json": pkg_ver}
distinct = {v for v in vers.values() if v}

def check_release_gates_on_validate():
    """A release must not publish over a red `validate`.

    On 2026-08-12 `sheleg-dev` tagged v0.4.1 while its own `validate` run for that exact
    tag FAILED, and npm served 0.4.1 four minutes later. The two are separate workflows,
    so nothing connected them: the release ran the structural validator and never the
    negative self-tests, which are steps in `validate.yml`. Six of the family's nine
    repositories were in that state.

    The fix is a `workflow_call` — the release calls the real suite rather than a copy of
    it — and this guard keeps the call there. A dependency nobody checks is a dependency
    somebody removes.
    """
    _wf = os.path.join(ROOT, ".github/workflows")
    _rel, _val = os.path.join(_wf, "release.yml"), os.path.join(_wf, "validate.yml")
    if not (os.path.isfile(_rel) and os.path.isfile(_val)):
        return
    _v = open(_val, encoding="utf-8").read()
    _r = open(_rel, encoding="utf-8").read()
    if not re.search(r"^\s*workflow_call:\s*$", _v, re.M):
        fail(".github/workflows/validate.yml: no `workflow_call:` trigger — the release "
               "workflow cannot run this suite, so a publish goes out over whatever subset "
               "it runs itself")
    if not re.search(r"^\s*uses:\s*\./\.github/workflows/validate\.yml\s*$", _r, re.M):
        fail(".github/workflows/release.yml: does not call ./.github/workflows/validate.yml "
               "— a red validate would not stop a publish, which is how v0.4.1 of a sibling "
               "reached npm with its own suite failing")
    if not re.search(r"^\s*needs:\s*(?:\[[^\]]*\bvalidate\b[^\]]*\]|validate)\s*$", _r, re.M):
        fail(".github/workflows/release.yml: no job declares `needs: validate` — calling "
               "the suite without depending on it lets the release run beside it rather than "
               "after it, which looks gated and is not")


check_release_gates_on_validate()

if len(distinct) > 1:
    fail(f"version mismatch across manifests: {vers}")

chg_path = os.path.join(ROOT, "CHANGELOG.md")
if not os.path.isfile(chg_path):
    fail("missing root file: CHANGELOG.md")
else:
    chg = open(chg_path, encoding="utf-8").read()
    vm = re.search(r"^##\s*v(\d+\.\d+\.\d+)", chg, re.M)
    if not vm:
        fail("CHANGELOG.md: no '## vX.Y.Z' entry found")
    elif plg_ver and vm.group(1) != plg_ver:
        fail(f"version mismatch: CHANGELOG top entry=v{vm.group(1)} plugin.json={plg_ver!r}")

# optional 5th sync point: SKILL.md metadata.version (spec-legal, agent-visible)
skill_ver = skill_meta.get("version") if isinstance(skill_meta, dict) else None
if skill_ver and plg_ver and skill_ver != plg_ver:
    fail(f"version mismatch: SKILL.md metadata.version={skill_ver!r} plugin.json={plg_ver!r}")

# commands are skills now: a commands/<x>.md next to a skills/<x>/ registers the
# same /<x> twice — the skill wins and the command is unreachable always-on cost
# (visible only in `claude plugin details`). Any command that does exist must
# carry a description and a QUOTED argument-hint (bare `[a | b]` parses as a YAML
# list and drops the whole block).
for plugin_dir in sorted(glob.glob(os.path.join(ROOT, "plugins", "*"))):
    if not os.path.isdir(plugin_dir):
        continue
    skill_names = {os.path.basename(d)
                   for d in glob.glob(os.path.join(plugin_dir, "skills", "*"))
                   if os.path.isfile(os.path.join(d, "SKILL.md"))}
    for cmd_path in sorted(glob.glob(os.path.join(plugin_dir, "commands", "*.md"))):
        cmd_name = os.path.basename(cmd_path)[:-3]
        rel = os.path.relpath(cmd_path, ROOT)
        if cmd_name in skill_names:
            fail(f"{rel} collides with skills/{cmd_name}/ — both claim /{cmd_name}; "
                 "the skill wins and the command is unreachable always-on cost "
                 "(check with `claude plugin details`)")
        ctxt = open(cmd_path, encoding="utf-8").read()
        cm = re.match(r"^---\n(.*?)\n---\n", ctxt, re.S)
        if not cm:
            fail(f"{rel}: no frontmatter")
            continue
        cfm = cm.group(1)
        if not re.search(r"^description:\s*\S", cfm, re.M):
            fail(f"{rel}: empty/missing description in frontmatter")
        hint = re.search(r"^argument-hint:\s*(\S.*)$", cfm, re.M)
        if hint and not re.match(r"""^["'].*["']$""", hint.group(1).strip()):
            fail(f"{rel}: argument-hint must be quoted — bare [a | b] is a YAML "
                 "list and silently drops the whole frontmatter block")

# --- shipped host capabilities: hooks, agents, scripts -----------------------
# Every one of these is Claude-Code-only, so the canon requires a written
# fallback; and each has a failure mode that is invisible until a user hits it.
PLUGIN_DIR = os.path.join(ROOT, "plugins", NAME)

# The degradation contract must be in the body, in the words the agent reads at
# the moment something is missing — not only in a reference file.
for phrase in ("Degradation contract", "Not Claude Code", "absent"):
    if phrase not in skill_txt:
        fail(f"SKILL.md: no {phrase!r} — a plugin that ships hooks/agents/commands "
             "owes a written fallback for hosts that have none")

scripts_dir = os.path.join(SKILL_DIR, "scripts")
if not os.path.isdir(scripts_dir):
    fail("missing skills/make-skill/scripts/ — the deterministic half of an audit "
         "belongs in a script that travels with the skill")
else:
    import py_compile, tempfile
    for entry in sorted(os.listdir(scripts_dir)):
        if not entry.endswith(".py"):
            continue
        full = os.path.join(scripts_dir, entry)
        # compile into a throwaway file: /dev/null is rejected as a cfile, and a
        # __pycache__ next to a shipped script would land in the package
        with tempfile.NamedTemporaryFile(suffix=".pyc") as tmp:
            try:
                py_compile.compile(full, doraise=True, cfile=tmp.name)
            except Exception as e:
                fail(f"scripts/{entry}: does not compile: {e}")
        head = open(full, encoding="utf-8").readline()
        if not head.startswith("#!"):
            fail(f"scripts/{entry}: no shebang — it is executed, not imported")
        if not os.access(full, os.X_OK):
            fail(f"scripts/{entry}: not executable (chmod +x)")

hooks_json = os.path.join(PLUGIN_DIR, "hooks", "hooks.json")
if os.path.isfile(hooks_json):
    hk = load_json(f"plugins/{NAME}/hooks/hooks.json")
    if hk is not None:
        if not (hk.get("description") or "").strip():
            fail("hooks/hooks.json: no description — a reviewer reads it to learn "
                 "when these hooks no-op, which is the whole trust question")
        for event, groups in (hk.get("hooks") or {}).items():
            for group in groups:
                for h in group.get("hooks") or []:
                    cmd = h.get("command", "")
                    if h.get("type") == "command":
                        if "${CLAUDE_PLUGIN_ROOT}" not in cmd:
                            fail(f"hooks/hooks.json ({event}): command {cmd!r} does not "
                                 "resolve through ${CLAUDE_PLUGIN_ROOT} — the install "
                                 "path changes on every update")
                        if '"' not in cmd:
                            fail(f"hooks/hooks.json ({event}): quote the path — a space "
                                 "in the install directory splits the command")
                        if not h.get("timeout"):
                            fail(f"hooks/hooks.json ({event}): no timeout")
                        m = re.search(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"']+)", cmd)
                        if m:
                            target = os.path.join(PLUGIN_DIR, m.group(1))
                            if not os.path.isfile(target):
                                fail(f"hooks/hooks.json ({event}): script {m.group(1)} missing")
                            elif not os.access(target, os.X_OK):
                                fail(f"hooks/{m.group(1)}: not executable (chmod +x)")
                            elif not open(target, encoding="utf-8").readline().startswith("#!"):
                                fail(f"hooks/{m.group(1)}: no shebang")

# plugin-shipped agents: Claude Code REJECTS these three keys
AGENT_FORBIDDEN = ("hooks", "mcpServers", "permissionMode")
for agent_path in sorted(glob.glob(os.path.join(PLUGIN_DIR, "agents", "*.md"))):
    rel = os.path.relpath(agent_path, ROOT)
    atxt = open(agent_path, encoding="utf-8").read()
    am = re.match(r"^---\n(.*?)\n---\n", atxt, re.S)
    if not am:
        fail(f"{rel}: no frontmatter")
        continue
    afm = am.group(1)
    for field in ("name", "description"):
        if not re.search(rf"^{field}:\s*\S", afm, re.M):
            fail(f"{rel}: empty/missing {field}")
    for key in AGENT_FORBIDDEN:
        if re.search(rf"^{key}:", afm, re.M):
            fail(f"{rel}: {key!r} is rejected for plugin-shipped agents")

# npm package: bin resolves, files whitelist ships the sources
if pkg:
    bin_map = pkg.get("bin") or {}
    if not bin_map:
        fail("package.json: missing bin entry")
    for bin_name, bin_rel in bin_map.items():
        if not os.path.isfile(os.path.join(ROOT, bin_rel)):
            fail(f"package.json bin {bin_name!r} -> missing file {bin_rel!r}")
    files = pkg.get("files") or []
    for req in ("bin", "plugins"):
        if req not in files:
            fail(f"package.json: files[] must whitelist {req!r}")

# Cursor channel: every cursor/rules/*.mdc must carry description + alwaysApply
cursor_dir = os.path.join(ROOT, "cursor", "rules")
mdcs = [f for f in os.listdir(cursor_dir) if f.endswith(".mdc")] if os.path.isdir(cursor_dir) else []
if not mdcs:
    fail("cursor/rules: no .mdc rules found")
for f in mdcs:
    mtxt = open(os.path.join(cursor_dir, f), encoding="utf-8").read()
    mm = re.match(r"^---\n(.*?)\n---\n", mtxt, re.S)
    if not mm:
        fail(f"cursor/rules/{f}: no frontmatter")
        continue
    mfm = mm.group(1)
    if not re.search(r"^description:\s*\S", mfm, re.M):
        fail(f"cursor/rules/{f}: empty/missing description")
    if not re.search(r"^alwaysApply:\s*(true|false)\s*$", mfm, re.M):
        fail(f"cursor/rules/{f}: alwaysApply must be true or false")
    # .mdc files get copied into foreign projects — any relative link dangles there.
    for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", mtxt):
        if not target.startswith(("http://", "https://", "mailto:", "#")):
            fail(f"cursor/rules/{f}: relative link {target!r} — .mdc must embed contracts inline")
    # The Cursor rule is a fourth copy of the canon and drifted from it: through
    # v0.10.0 its layout block still prescribed a repo-root templates/, which the
    # stray-SKILL.md rule below rejects outright. A user following the shipped
    # rule built a repo this validator refuses.
    if re.search(r"^templates/", mtxt, re.M):
        fail(f"cursor/rules/{f}: prescribes a repo-root templates/ — that reaches no "
             "agent through any channel and this validator rejects it. Skeletons live "
             "in skills/<skill>/assets/, and the .mdc must say the same as the canon")

# assets/: the skeletons must NOT be named SKILL.md — the skills CLI discovers
# every SKILL.md in the repo and would ship the placeholder as a real skill.
tpl_dir = os.path.join(SKILL_DIR, "assets")
skill_tpl = os.path.join(tpl_dir, "SKILL.template.md")
if os.path.isdir(os.path.join(ROOT, "templates")):
    fail("templates/ at the repo root reaches no agent — the plugin ships "
         "plugins/<name>/ and the skills CLI ships the skill dir; skeletons live "
         "in skills/<skill>/assets/")
if not os.path.isdir(tpl_dir):
    fail("missing skills/make-skill/assets/ — skeletons must travel with the skill")
elif not os.path.isfile(skill_tpl):
    fail("missing template: assets/SKILL.template.md")
else:
    # the skeleton seeds a real skill: its name/description placeholders must
    # already be legal, and <angle-bracket> placeholders read as XML tags, which
    # Anthropic's platform rejects in exactly those two fields
    ttxt = open(skill_tpl, encoding="utf-8").read()
    tm = re.match(r"^---\n(.*?)\n---\n", ttxt, re.S)
    if not tm:
        fail("assets/SKILL.template.md: no frontmatter — it seeds a SKILL.md")
    else:
        tfm = parse_frontmatter(tm.group(1))
        for field in ("name", "description"):
            val = tfm.get(field)
            if not isinstance(val, str) or not val.strip():
                fail(f"assets/SKILL.template.md: empty/missing {field}")
            elif XML_TAG_RE.search(val):
                fail(f"assets/SKILL.template.md: {field} placeholder uses angle "
                     "brackets, which read as an XML tag and are rejected on upload — "
                     "seed a plain placeholder instead")
        if isinstance(tfm.get("name"), str) and any(
                w in tfm["name"].lower() for w in RESERVED_NAME_WORDS):
            fail("assets/SKILL.template.md: name placeholder contains a reserved word")

# manifest skeletons: must parse, carry $schema, and stay inside the recognized
# field sets — a template that fails `claude plugin validate --strict` seeds a
# repo that fails it too
for tpl, allowed, schema_url in (
    ("plugin.template.json", PLUGIN_MANIFEST_KEYS,
     "https://json.schemastore.org/claude-code-plugin-manifest.json"),
    ("marketplace.template.json", MKT_TOP_KEYS,
     "https://json.schemastore.org/claude-code-marketplace.json"),
):
    tpl_path = os.path.join(tpl_dir, tpl)
    if not os.path.isfile(tpl_path):
        fail(f"missing template: assets/{tpl}")
        continue
    try:
        tpl_data = json.load(open(tpl_path, encoding="utf-8"))
    except Exception as e:
        fail(f"assets/{tpl}: invalid JSON: {e}")
        continue
    if tpl_data.get("$schema") != schema_url:
        fail(f"assets/{tpl}: missing/wrong $schema ({schema_url})")
    unknown = sorted(set(tpl_data) - allowed)
    if unknown:
        fail(f"assets/{tpl}: unrecognized fields {unknown}")
    if tpl == "plugin.template.json" and not tpl_data.get("displayName"):
        fail("assets/plugin.template.json: no displayName — the canon requires "
             "one in the manifest and in the marketplace entry, so the skeleton "
             "must seed it")
    entries = tpl_data.get("plugins") if tpl == "marketplace.template.json" else []
    for entry in entries or []:
        unknown = sorted(set(entry) - MKT_ENTRY_KEYS)
        if unknown:
            fail(f"assets/{tpl}: plugin entry has unrecognized fields {unknown}")
        if not entry.get("displayName"):
            fail(f"assets/{tpl}: plugin entry has no displayName")

# HARD RULE: a SKILL.md may exist ONLY inside plugins/<plugin>/skills/<skill>/.
# Anywhere else (templates/, docs/, examples/) the skills CLI picks it up and
# installs a bogus skill into every agent.
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
    if "SKILL.md" not in filenames:
        continue
    rel = os.path.relpath(os.path.join(dirpath, "SKILL.md"), ROOT)
    if not re.match(r"^plugins/[^/]+/skills/[^/]+/SKILL\.md$", rel):
        # A plugin-root SKILL.md is a legal single-skill plugin in Claude Code —
        # but in THIS multi-channel layout the skills CLI would ship every one of
        # them as a separate skill on every agent.
        fail(f"stray SKILL.md at {rel} — the skills CLI would ship it as a skill; "
             f"rename it (e.g. SKILL.template.md) or move it under plugins/<p>/skills/<s>/")

# evaluations — the canon requires >=3 behavioral scenarios and a trigger set
# with near-miss negatives for every skill, so this repo owes its own. They are
# data, not unit tests: the runner is a human with an agent (test/evals/README.md).
trig = load_json("test/evals/triggers.json")
if trig is not None:
    qs = trig.get("queries") or []
    if len(qs) < 16:
        fail(f"test/evals/triggers.json: {len(qs)} queries, the loop needs ~20 "
             "(8-10 true, 8-10 near-miss negatives)")
    ids = [q.get("id") for q in qs]
    if len(set(ids)) != len(ids):
        fail("test/evals/triggers.json: duplicate query ids")
    for q in qs:
        if not q.get("query") or not isinstance(q.get("should_trigger"), bool):
            fail(f"test/evals/triggers.json: query {q.get('id')!r} needs a non-empty "
                 "'query' and a boolean 'should_trigger'")
    pos = sum(1 for q in qs if q.get("should_trigger") is True)
    neg = sum(1 for q in qs if q.get("should_trigger") is False)
    if pos < 6 or neg < 6:
        fail(f"test/evals/triggers.json: {pos} positive / {neg} negative — the "
             "negatives are what catch a description that steals other skills' turns")
    # both classes must appear on both sides of the split, or the validation half
    # can only measure one failure mode
    split = trig.get("split") or {}
    by_id = {q.get("id"): q for q in qs}
    for half in ("train", "validation"):
        got = split.get(half)
        if not isinstance(got, list) or not got:
            fail(f"test/evals/triggers.json: split.{half} must list query ids")
            continue
        unknown = [i for i in got if i not in by_id]
        if unknown:
            fail(f"test/evals/triggers.json: split.{half} names unknown ids {unknown}")
        classes = {by_id[i]["should_trigger"] for i in got if i in by_id}
        if classes != {True, False}:
            fail(f"test/evals/triggers.json: split.{half} holds only "
                 f"{'positives' if True in classes else 'negatives'} — a half without "
                 "both classes measures one failure mode and misses the other")

scen = load_json("test/evals/scenarios.json")
if scen is not None:
    scenarios = scen.get("scenarios") or []
    if len(scenarios) < 3:
        fail(f"test/evals/scenarios.json: {len(scenarios)} scenarios, canon requires >= 3")
    for s in scenarios:
        sid = s.get("id", "?")
        for field in ("skills", "query", "files", "expected_behavior"):
            if field not in s:
                fail(f"test/evals/scenarios.json: scenario {sid!r} missing {field!r} "
                     "(Anthropic's evaluation shape)")
        beh = s.get("expected_behavior") or []
        if not isinstance(beh, list) or len(beh) < 3:
            fail(f"test/evals/scenarios.json: scenario {sid!r} needs at least 3 "
                 "expected_behavior lines — they are scored individually")
        for rel in s.get("files") or []:
            if not os.path.isfile(os.path.join(ROOT, rel)):
                fail(f"test/evals/scenarios.json: scenario {sid!r} points at missing "
                     f"file {rel!r}")

# --- claims about the repo must match the repo ------------------------------
# Every defect this section catches shipped at least once: "13-item" beside
# "14-item", "ten files" beside eleven, "six groups" beside eight, a SKILL-CARD
# pinned two releases back. None of them were catchable by any rule above,
# because a number typed into prose is an assertion and nothing was comparing it
# to the artifact. CHANGELOG.md and docs/evidence/ are exempt: they are
# history, and a past entry is allowed to quote the count that was true then.
CLAIM_SKIP_DIRS = (os.path.join("docs", "evidence"), os.path.join("test", "evals", "fixtures"))
CLAIM_SKIP_FILES = {"CHANGELOG.md"}


def tracked_docs():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        rel_dir = os.path.relpath(dirpath, ROOT)
        if any(rel_dir.startswith(s) for s in CLAIM_SKIP_DIRS):
            continue
        for fn in sorted(filenames):
            if not fn.endswith((".md", ".mdc")):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            if rel in CLAIM_SKIP_FILES:
                continue
            yield rel, open(os.path.join(dirpath, fn), encoding="utf-8").read()


retrofit_path = os.path.join(refs_dir, "retrofit.md")
retrofit_items = 0
if os.path.isfile(retrofit_path):
    retrofit_items = len(re.findall(r"^\d+\. \*\*", open(retrofit_path, encoding="utf-8").read(), re.M))
ref_files = sorted(f for f in os.listdir(refs_dir) if f.endswith(".md")) if os.path.isdir(refs_dir) else []
wf_path = os.path.join(ROOT, ".github/workflows/validate.yml")
wf_txt = open(wf_path, encoding="utf-8").read() if os.path.isfile(wf_path) else ""
selftest_groups = wf_txt.count("name: Negative self-test")

COUNTED_CLAIMS = [
    (re.compile(r"(\d+)-item checklist"), retrofit_items,
     "numbered items in references/retrofit.md"),
    (re.compile(r"the (\d+) files under `skills/make-skill/references/`"), len(ref_files),
     "*.md in the skill's references/"),
    (re.compile(r"(\d+) groups of negative self-tests"), selftest_groups,
     "'Negative self-test' steps in .github/workflows/validate.yml"),
    (re.compile(r"(\d+) negative self-test groups"), selftest_groups,
     "'Negative self-test' steps in .github/workflows/validate.yml"),
]

for rel, txt in tracked_docs():
    for pattern, actual, source in COUNTED_CLAIMS:
        for claimed in pattern.findall(txt):
            if int(claimed) != actual:
                fail(f"{rel}: claims {claimed} where the repo has {actual} ({source}) "
                     "— compute the number or have this validator compare it, but do "
                     "not type it")

# every shipped reference must be listed in the README too: v0.10.0 added
# mcp-ship.md to SKILL.md alone, so the README's "what ships with it" table told
# a reader the instruction surface was one file smaller than it is
readme_txt = ""
readme_path = os.path.join(ROOT, "README.md")
if os.path.isfile(readme_path):
    readme_txt = open(readme_path, encoding="utf-8").read()
    for entry in ref_files:
        if f"`{entry}`" not in readme_txt:
            fail(f"README.md never mentions references/{entry} — the table that tells a "
                 "reader what ships must list every reference the skill actually ships")

# SKILL-CARD.md is the registry entry a reviewer reads before installing; a stale
# version there is the one field that makes the whole card untrustworthy
card_path = os.path.join(ROOT, "SKILL-CARD.md")
if os.path.isfile(card_path) and plg_ver:
    card = open(card_path, encoding="utf-8").read()
    cm = re.search(r"\*\*Version\*\*\s*\|\s*([0-9][^\s|]*)", card)
    if not cm:
        fail("SKILL-CARD.md: no '**Version** | X.Y.Z' row — a registry entry without a "
             "deployed version answers nothing")
    elif cm.group(1) != plg_ver:
        fail(f"SKILL-CARD.md: Version {cm.group(1)!r} != plugin.json {plg_ver!r}")

# --- a runnable command may not be built from a path variable ----------------
# ${CLAUDE_PLUGIN_ROOT} is substituted into skill/command/agent TEXT and exported
# to hook processes, but it is EMPTY in the Bash tool. A documented command built
# from it expands to "/skills/..." and dies — and an agent that cannot run the
# deterministic half reasons through it instead and reports a PASS it never ran.
# Reference files may discuss the variable; files that hand the agent commands
# may not put it inside one.
FENCE_RE = re.compile(r"```[a-zA-Z0-9]*\n(.*?)```", re.S)
runnable = sorted(glob.glob(os.path.join(PLUGIN_DIR, "commands", "*.md"))
                  + glob.glob(os.path.join(PLUGIN_DIR, "agents", "*.md"))
                  + glob.glob(os.path.join(SKILL_DIR, "assets", "*.template.md")))
for path in runnable:
    rel = os.path.relpath(path, ROOT)
    for block in FENCE_RE.findall(open(path, encoding="utf-8").read()):
        for var in re.findall(r"\$\{CLAUDE_[A-Z_]+\}", block):
            fail(f"{rel}: a command block contains {var}, which is empty in the Bash "
                 "tool — the command cannot run. Ship a wrapper in the plugin's bin/ "
                 "(Claude Code puts it on PATH) and call it by name")

# executables the plugin puts on PATH
plugin_bin = os.path.join(PLUGIN_DIR, "bin")
if os.path.isdir(plugin_bin):
    for entry in sorted(os.listdir(plugin_bin)):
        full = os.path.join(plugin_bin, entry)
        if not os.path.isfile(full):
            continue
        if not open(full, encoding="utf-8").readline().startswith("#!"):
            fail(f"bin/{entry}: no shebang — it is executed by name off PATH")
        if not os.access(full, os.X_OK):
            fail(f"bin/{entry}: not executable (chmod +x)")

# one rule, one implementation: the shipped auditor and this validator must apply
# the same XML-tag test, or a skill passes one gate and fails the other
aud_src = open(os.path.join(SKILL_DIR, "scripts", "audit_skill.py"), encoding="utf-8").read()
am = re.search(r'^XML_TAG_RE = re\.compile\(r"(.+)"\)$', aud_src, re.M)
if not am:
    fail("scripts/audit_skill.py: XML_TAG_RE not found — this validator compares it")
elif am.group(1) != XML_TAG_PATTERN:
    fail(f"XML_TAG_RE differs: audit_skill.py has {am.group(1)!r}, validate.py has "
         f"{XML_TAG_PATTERN!r} — one rule, two implementations, and a skill that "
         "passes one gate fails the other")

# required root files — a public repo also owes contributors an entry point and
# a place to report something exploitable privately
for r in ("README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md",
          "SKILL-CARD.md"):
    if not os.path.isfile(os.path.join(ROOT, r)):
        fail(f"missing root file: {r}")

# every relative markdown link in repo docs must resolve
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
    # evaluation fixtures are deliberately broken samples — their dangling links
    # and escaping paths are the defects a scenario is scored on finding
    if os.path.relpath(dirpath, ROOT).startswith(os.path.join("test", "evals", "fixtures")):
        continue
    for fn in filenames:
        if not fn.endswith(".md"):
            continue
        fp = os.path.join(dirpath, fn)
        for target in LINK_RE.findall(open(fp, encoding="utf-8").read()):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            tpath = os.path.normpath(os.path.join(dirpath, target.split("#")[0]))
            if not os.path.exists(tpath):
                rel = os.path.relpath(fp, ROOT)
                fail(f"broken relative link in {rel}: {target}")

if errors:
    print("FAIL: make-skill structure invalid")
    for e in errors:
        print(" - " + e)
    sys.exit(1)
print(f"PASS: make-skill structure valid ({len(mdcs)} cursor rule(s))")

#!/usr/bin/env python3
"""Audit ANY skill directory against the Agent Skills standard + Anthropic's rules.

    python3 audit_skill.py <skill-dir> [--house] [--json] [--quiet]

Exit 0 when every check passes, 1 when any GAP is found, 2 on a usage error.

Why this exists: the mechanical half of a retrofit audit — charset, lengths,
reserved words, budgets, link integrity — is the same every time, and an agent
re-deriving it from prose gets a different subset right on each run. This runs the
same checks in the same order and prints file:line evidence for each, so the agent
spends its context on the half that needs judgement.

  core      the Agent Skills open standard (agentskills.io/specification) plus the
            rules Anthropic's platform enforces on upload (reserved words, XML
            tags) and its authoring guidance (third person, tables of contents)
  --house   adds the ssheleg canon: description starts "Use when …", carries
            English AND Russian trigger phrases, and holds the 5% working
            headroom on BOTH budgets — 970 of 1024 chars, 4750 of 5000 tokens.
            The canon states the headroom as one rule for both fields; applying
            it to one of them is how a body at 4999 tokens got a clean bill here
            and was refused by the repo's own validator.

Python 3.9+, standard library only: it has to run wherever the skill landed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# --- limits, each with the authority that sets it --------------------------
NAME_MAX = 64           # spec: name is 1-64 characters
DESC_MAX = 1024         # spec: description is 1-1024 characters
# House working limit: 5% under the cap. The description is the whole triggering
# budget AND the field that must grow when a near-miss skill appears ("say what
# it is NOT for"). A description at 98% of cap cannot absorb that sentence.
DESC_TARGET = 970
# B-139 — the nine `DESC_*` rules ask WHEN and never WHAT.
#
# Anthropic's guidance asks a description to say what the skill DOES as well as when to
# use it, and `B-76` quoted the failure directly: *a description that never says what the
# skill does passes*. Measured 2026-09-03 across the family: **28 of 28 skills pass
# `DESC_USEWHEN`, 0 gaps** — the WHEN half is universal and the WHAT half was unchecked.
#
# The WHAT half is the description with its mechanical parts removed: the `Use when`
# opener, the trigger list, the `Not for` clause and the opt-out sentence. What remains is
# the prose that names the act. A description that is an opener plus a trigger list leaves
# almost nothing, which is exactly the shape the rule refuses.
#
# The floor is 60 and it is deliberately permissive. Measured on the shipped family, the
# smallest honest WHAT half is **149** characters (`ux-audit`) and the largest 949, so 60
# clears every real description by more than double and still catches
# `Use when the user asks. Triggers - "x" / "у".`, whose WHAT half is 13.
#
# **This rule finds no gap today, and that is stated rather than hidden.** A standard is
# for the description not yet written; a rule that fires on nothing now is only worth
# anything if it was watched firing on a plant, which `test/checker_parity_test.py` does.
DESC_WHAT_MIN = 60

# Built on the PARSED description, never the raw front matter. A prototype was built
# against raw text and refused: it reported a 0-character WHAT half for six skills and
# missed the opening clause of twenty, because several descriptions are YAML block
# scalars (`>-`) that a raw-text regex reads straight past. `parse_frontmatter` already
# resolves them, and the prototype did not use it.
_WHAT_OPENER = re.compile(r"^use when\s+", re.I)
_WHAT_STRIP = (
    re.compile(r"\bTriggers?\s*[-–—:].*", re.S | re.I),
    re.compile(r"\bNot for\b.*", re.S | re.I),
    re.compile(r"\bsay\s+['\"«].*", re.S | re.I),
)


def what_half(description):
    """The prose that names the act, with the mechanical parts removed."""
    core = _WHAT_OPENER.sub("", " ".join(str(description or "").split()))
    for rx in _WHAT_STRIP:
        core = rx.sub("", core)
    return core.strip(" .,;—-")

COMPAT_MAX = 500        # spec: compatibility is 1-500 characters
BODY_MAX_LINES = 500    # spec + Anthropic: keep the body under 500 lines
BODY_MAX_TOKENS = 5000  # spec + Anthropic: level-2 budget
# House working limit, the body's half of the same 5% rule DESC_TARGET states.
# The canon writes both as one sentence — "hold 5% headroom" — and for four
# releases this script applied only the description half, so a body at 4999
# tokens got 0 GAP here and was refused by the repo's own validator. Two
# verdicts on one rule, and the permissive one was the one users got.
BODY_TARGET_TOKENS = 4750
# No tokenizer in the stdlib. 3.9 chars/token is measured, not assumed: tokenizing
# this skill's own bundle gives 3.78-4.47. `claude plugin details` is far more
# pessimistic (~2.8) and will always show a bigger number than this estimate.
# AND the estimate is an ESTIMATE (FIX-MS-01.01): a 16 000-hieroglyph body is
# 16 000 cl100k tokens and estimates ~4 102 — so the estimate never grants a
# token PASS and is never CALLED tokens. A real, NAMED tokenizer measures;
# without one the token budget is UNMEASURED and the estimate rides beside it
# as its own field.
CHARS_PER_TOKEN = 3.9

# Optional tokenizer adapter. `None` = unresolved; tests may inject
# `(callable, "name")` or `(None, None)` directly to pin either path.
# `MAKE_SKILL_TOKENIZER` selects a tiktoken encoding by name; an UNSUPPORTED
# name refuses to measure (a warning + UNMEASURED) — it never silently falls
# back to another encoding or to the estimate, because a verdict from the
# wrong instrument wearing the right instrument's name is worse than no
# verdict (FIX-MS-01.02).
TOKENIZER = None
DEFAULT_ENCODING = "cl100k_base"

# Who owns each threshold — `spec` is the Agent Skills standard / Anthropic's
# platform rules, `house` is this family's working rule, `host` would be a
# per-host runtime limit. A number without its authority reads as physics;
# these are policies, each negotiable only with its owner.
THRESHOLDS = {
    "BODY_MAX_LINES": ("spec", 500),
    "BODY_MAX_TOKENS": ("spec", 5000),
    "BODY_TARGET_TOKENS": ("house", 4750),
    "DESC_MAX_CHARS": ("spec", 1024),
}

# The differential corpus: pinned counts for DEFAULT_ENCODING, measured with
# tiktoken 0.14.0 (2026-09-09). Same string + same tokenizer revision must give
# the same measured count on every machine — a drift here means the adapter
# or the encoding changed, and either is a finding, never a rounding error.
TOKEN_CORPUS = {
    "english": ("the quick brown fox jumps over the lazy dog", 9),
    "code": ("def verify(sig, key):\n    return hmac.compare_digest(sig, key)\n", 15),
    "russian": ("проверка бюджета токенов выполняется настоящим токенизатором", 28),
    "mixed": ("body budget: бюджет тела — 5000 tokens, не оценка", 22),
    "cjk": ("字符预算不是估计值", 9),
}


def resolve_tokenizer():
    global TOKENIZER
    if TOKENIZER is None:
        name = os.environ.get("MAKE_SKILL_TOKENIZER") or DEFAULT_ENCODING
        # tiktoken caches encoding data in TMPDIR by default — residue a test
        # run must not leave. A stable per-user cache, unless the operator
        # already chose one.
        os.environ.setdefault("TIKTOKEN_CACHE_DIR", os.path.join(
            os.path.expanduser("~"), ".cache", "make-skill", "tiktoken"))
        try:
            import tiktoken
            enc = tiktoken.get_encoding(name)
            TOKENIZER = (lambda text: len(enc.encode(text)), f"tiktoken:{name}")
        except Exception as exc:
            if os.environ.get("MAKE_SKILL_TOKENIZER"):
                print(f"audit: tokenizer {name!r} is unsupported ({exc}) — token "
                      "budgets are UNMEASURED, not silently re-measured with a "
                      "different encoding", file=sys.stderr)
            TOKENIZER = (None, None)
    return TOKENIZER


def corpus_check():
    """The adapter against the pinned oracle. Returns (verdict, detail):
    'agree' when every sample matches its pinned count, 'NOT_RUN' without a
    tokenizer, 'DISAGREE' naming the first divergent sample."""
    count_fn, tok_name = resolve_tokenizer()
    if count_fn is None:
        return "NOT_RUN", "no tokenizer installed — the differential did not run"
    if tok_name != f"tiktoken:{DEFAULT_ENCODING}":
        return "NOT_RUN", (f"corpus counts are pinned for {DEFAULT_ENCODING}; "
                           f"{tok_name} is a different instrument")
    for name, (sample, pinned) in sorted(TOKEN_CORPUS.items()):
        got = count_fn(sample)
        if got != pinned:
            return "DISAGREE", (f"{name}: adapter says {got}, the pinned oracle "
                                f"says {pinned} — same string, same revision, "
                                "different count")
    return "agree", f"{len(TOKEN_CORPUS)} samples agree with {tok_name}"


TOC_MIN_LINES = 100     # Anthropic: longer reference files need a table of contents

SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
# Claude Code reads these too. Legal, ignored by every other agent.
HOST_KEYS = {
    "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "disallowed-tools", "model", "effort", "context", "agent",
    "background", "hooks", "paths", "shell",
}
RESERVED_NAME_WORDS = ("anthropic", "claude")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
XML_TAG_RE = re.compile(r"<[^<>\s][^<>]*>")
PERSON_RE = re.compile(
    r"\b(?:I can|I will|I'll|I help|I'm|you can use|you should use|you may use|"
    r"this skill (?:lets|allows|helps) you)\b", re.I)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
WIN_PATH_RE = re.compile(r"\b[\w.-]+\\[\w.-]+\.(?:md|py|sh|js|json|ya?ml)\b")
TIME_BRANCH_RE = re.compile(
    r"\b(?:before|after|until|from)\s+"
    r"(?:january|february|march|april|may|june|july|august|september|october|"
    r"november|december|\d{4})\b", re.I)
BUNDLE_DIRS = ("references", "scripts", "assets")


class Audit:
    """Collects verdicts so every check reports, rather than the first failure."""

    def __init__(self, root):
        self.root = root
        self.results = []

    def add(self, verdict, check, message, path=None, line=None):
        self.results.append({
            "verdict": verdict, "check": check, "message": message,
            "file": path, "line": line,
        })

    def ok(self, check, message, path=None, line=None):
        self.add("PASS", check, message, path, line)

    def gap(self, check, message, path=None, line=None):
        self.add("GAP", check, message, path, line)

    @property
    def gaps(self):
        return [r for r in self.results if r["verdict"] == "GAP"]


def parse_frontmatter(text):
    """YAML subset: top-level scalars, block scalars, one nested map.

    Returns (data, line_of_key). A full YAML parser is not in the stdlib and a
    skill's frontmatter is a flat map by specification, so this is enough — and
    it keeps the script dependency-free, which is the point of shipping it.

    A plain scalar may continue on indented lines and YAML folds them into one
    value with a space. Dropping those lines is how a description whose real
    length was 1392 characters got measured at 180 and passed both the 1024 cap
    and the 970 working limit — a clean bill from the family's standard-keeper
    for a skill the Skills API rejects on upload (2026-08-16, B-63).
    """
    data, lines, key, mode = {}, {}, None, None
    scalars = set()
    for i, raw in enumerate(text.split("\n"), start=2):  # +2: the opening '---'
        if not raw.strip():
            continue
        if raw[0] not in " \t":
            m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
            if not m:
                key, mode = None, None
                continue
            key, val = m.group(1), m.group(2).strip()
            lines[key] = i
            if val in (">", "|", ">-", "|-", ">+", "|+"):
                data[key], mode = "", "block"
            elif val == "":
                data[key], mode = {}, "map"
            else:
                # Kept RAW here and finished at the end: a quoted scalar that
                # spans lines carries its closing quote on the last one, so
                # unquoting the first line strips nothing and leaves the quote
                # buried in the middle of the folded value.
                data[key], mode = val, "scalar"
                scalars.add(key)
        elif mode == "block":
            data[key] = (data[key] + " " + raw.strip()).strip()
        elif mode == "scalar":
            data[key] = (data[key] + " " + raw.strip()).strip()
        elif mode == "map":
            m = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", raw)
            if m:
                data[key][m.group(1)] = _unquote(m.group(2).strip())
    for k in scalars:
        data[k] = _finish_scalar(data[k])
    return data, lines


def _finish_scalar(v):
    """A flow sequence is a LIST, not a string that happens to look like one.

    `allowed-tools: [Read, Write]` read as the string "[Read, Write]" is why
    TOOLS_TYPE never fired: it asks whether the value is a `str`, and the answer
    was yes. The inline sequence is the most common way authors write a tool
    list, and it is the portability defect the rule exists for — the skill works
    in Claude Code and silently loses its tool grant on every other host.
    """
    v = v.strip()
    if len(v) >= 2 and v[0] == "[" and v[-1] == "]":
        inner = v[1:-1].strip()
        return [] if not inner else [_unquote(p.strip()) for p in inner.split(",")]
    return _unquote(v)


def _unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def audit(skill_dir, house=False):
    a = Audit(skill_dir)
    name_on_disk = os.path.basename(os.path.abspath(skill_dir.rstrip("/")))
    skill_md = os.path.join(skill_dir, "SKILL.md")
    rel = os.path.join(name_on_disk, "SKILL.md")

    if not os.path.isdir(skill_dir):
        a.gap("LAYOUT", "not a directory: %s" % skill_dir, skill_dir)
        return a
    if not os.path.isfile(skill_md):
        a.gap("LAYOUT", "no SKILL.md — a skill is a directory with SKILL.md at its "
              "top level", skill_md)
        return a

    text = open(skill_md, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        a.gap("FRONTMATTER", "no YAML frontmatter — it must be the first thing in "
              "the file, delimited by ---", rel, 1)
        return a
    fm, fm_lines = parse_frontmatter(m.group(1))
    body = text[m.end():]

    _check_name(a, fm, fm_lines, name_on_disk, rel)
    _check_description(a, fm, fm_lines, rel, house)
    _check_optional_fields(a, fm, fm_lines, rel)
    _check_keys(a, fm, fm_lines, rel)
    _check_body_budget(a, body, rel, house)
    _check_bundle(a, skill_dir, text, name_on_disk)
    _check_links(a, skill_dir, text, rel)
    _check_prose(a, body, rel)
    return a


def _check_name(a, fm, lines, dir_name, rel):
    name = fm.get("name")
    ln = lines.get("name")
    if not isinstance(name, str) or not name:
        a.gap("NAME_MISSING", "name is required", rel, ln)
        return
    if len(name) > NAME_MAX:
        a.gap("NAME_LENGTH", "name is %d chars, the maximum is %d" % (len(name), NAME_MAX), rel, ln)
    elif not NAME_RE.match(name):
        a.gap("NAME_CHARSET", "name %r must be lowercase a-z0-9 with single internal "
              "hyphens — no uppercase, no leading/trailing or doubled hyphen" % name, rel, ln)
    else:
        # Charset only. Saying "spec-legal" here would contradict NAME_RESERVED
        # and NAME_XML below, and a PASS line quoted out of context is exactly
        # how a wrong verdict acquires real command output as its evidence.
        a.ok("NAME_CHARSET", "name %r uses a legal charset" % name, rel, ln)
    if name != dir_name:
        a.gap("NAME_DIR", "name %r != directory %r — the spec requires them to match, "
              "and the Skills API matches the uploaded top-level directory against it"
              % (name, dir_name), rel, ln)
    else:
        a.ok("NAME_DIR", "name matches the directory", rel, ln)
    hit = [w for w in RESERVED_NAME_WORDS if w in name.lower()]
    if hit:
        a.gap("NAME_RESERVED", "name contains the reserved word %r — Claude Code "
              "loads it, the Skills API rejects the upload" % hit[0], rel, ln)
    else:
        a.ok("NAME_RESERVED", "no reserved word in name", rel, ln)
    if XML_TAG_RE.search(name):
        a.gap("NAME_XML", "name contains an XML tag — rejected by Anthropic's "
              "platform; a leftover <placeholder> is the usual cause", rel, ln)


def _check_description(a, fm, lines, rel, house):
    desc = fm.get("description")
    ln = lines.get("description")
    if not isinstance(desc, str) or not desc.strip():
        a.gap("DESC_MISSING", "description is required and must be non-empty", rel, ln)
        return
    if len(desc) > DESC_MAX:
        a.gap("DESC_LENGTH", "description is %d chars, the maximum is %d"
              % (len(desc), DESC_MAX), rel, ln)
    else:
        a.ok("DESC_LENGTH", "description is %d/%d chars" % (len(desc), DESC_MAX), rel, ln)
    if XML_TAG_RE.search(desc):
        a.gap("DESC_XML", "description contains an XML tag — rejected by Anthropic's "
              "platform", rel, ln)
    hit = PERSON_RE.search(desc)
    if hit:
        a.gap("DESC_PERSON", "description is not third person (%r) — it is injected "
              "into the system prompt, where first/second person degrades skill "
              "selection" % hit.group(0), rel, ln)
    else:
        a.ok("DESC_PERSON", "description is third person", rel, ln)
    if house:
        # Both report either way: "the house rules were checked" has to be
        # provable from the output the canon tells the agent to cite.
        if not desc.lower().startswith("use when"):
            a.gap("DESC_USEWHEN", "description must start with 'Use when …' (house rule)", rel, ln)
        else:
            a.ok("DESC_USEWHEN", "description opens with 'Use when …' (house rule)", rel, ln)
        if not re.search(r"[а-яё]", desc, re.I):
            a.gap("DESC_RU", "description carries no Russian trigger phrases (house rule)", rel, ln)
        else:
            a.ok("DESC_RU", "description carries Russian trigger phrases (house rule)", rel, ln)
        what = what_half(desc)
        if len(what) < DESC_WHAT_MIN:
            a.gap("DESC_WHAT", "description says WHEN and never WHAT: %d chars remain "
                  "after the opener, the trigger list and the refusal are removed, and "
                  "the floor is %d (house rule). Anthropic's guidance asks for both "
                  "halves, and a description that is an opener plus a trigger list "
                  "selects the skill without telling the model what it will do"
                  % (len(what), DESC_WHAT_MIN), rel, ln)
        else:
            a.ok("DESC_WHAT", "description states WHAT the skill does in %d chars "
                 "beyond its triggers (house rule)" % len(what), rel, ln)
        if DESC_TARGET < len(desc) <= DESC_MAX:
            a.gap("DESC_HEADROOM", "description is %d chars — inside the %d cap but past the "
                  "%d working limit (house rule): leave room for the 'what this is NOT for' "
                  "clause a near-miss neighbour will require"
                  % (len(desc), DESC_MAX, DESC_TARGET), rel, ln)
        elif len(desc) <= DESC_TARGET:
            a.ok("DESC_HEADROOM", "description is %d/%d chars, inside the working limit"
                 % (len(desc), DESC_TARGET), rel, ln)


def _check_optional_fields(a, fm, lines, rel):
    compat = fm.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str) or not compat.strip():
            a.gap("COMPAT_TYPE", "compatibility must be a non-empty string", rel, lines.get("compatibility"))
        elif len(compat) > COMPAT_MAX:
            a.gap("COMPAT_LENGTH", "compatibility is %d chars, the maximum is %d"
                  % (len(compat), COMPAT_MAX), rel, lines.get("compatibility"))
    if "allowed-tools" in fm and not isinstance(fm["allowed-tools"], str):
        a.gap("TOOLS_TYPE", "allowed-tools must be a space-separated string; Claude "
              "Code also accepts a list, no other host does", rel, lines.get("allowed-tools"))
    meta = fm.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            a.gap("META_TYPE", "metadata must be a map of string keys to string values",
                  rel, lines.get("metadata"))
        else:
            for k, v in meta.items():
                if not isinstance(v, str) or not v:
                    a.gap("META_TYPE", "metadata.%s must be a non-empty string — quote "
                          "versions, or YAML turns 1.0 into a float" % k, rel, lines.get("metadata"))


def _check_keys(a, fm, lines, rel):
    unknown = sorted(set(fm) - SPEC_KEYS - HOST_KEYS)
    if unknown:
        a.gap("FM_UNKNOWN_KEY", "frontmatter keys in neither the open standard nor the "
              "Claude Code extension set: %s — anything outside both is a typo"
              % ", ".join(unknown), rel, lines.get(unknown[0]))
    else:
        a.ok("FM_UNKNOWN_KEY", "no frontmatter key outside spec ∪ host extensions", rel)


def _check_body_budget(a, body, rel, house=False):
    n_lines = body.count("\n") + 1
    count_fn, tok_name = resolve_tokenizer()
    est = int(len(body) / CHARS_PER_TOKEN)
    # Both, not either: a body over the line budget still has to report its
    # token verdict, or the second fix arrives only after the first one ships.
    over = False
    if n_lines >= BODY_MAX_LINES:
        a.gap("BODY_LINES", "body is %d lines, the budget is < %d — move detail into "
              "references/" % (n_lines, BODY_MAX_LINES), rel)
        over = True
    if count_fn is None:
        # No adapter, no token verdict: the budget is UNMEASURED, and the
        # byte/char estimate is reported as an ESTIMATE — it is not tokens,
        # it cannot PASS the budget, and it cannot fail it either (a
        # 16k-hieroglyph body estimates ~4k and measures 16k).
        a.ok("BODY_TOKENS_UNMEASURED",
             "token budget UNMEASURED — no tokenizer installed; the estimate "
             "~%d (%d chars / %s) is an estimate, NOT tokens: install tiktoken "
             "to measure" % (est, len(body), CHARS_PER_TOKEN), rel)
        if not over:
            a.ok("BODY_BUDGET", "body is %d lines (budget %d); token budget "
                 "unmeasured" % (n_lines, BODY_MAX_LINES), rel)
        if house:
            a.ok("BODY_HEADROOM_UNMEASURED",
                 "the %d-token working limit needs a measurement — unmeasured, "
                 "not passed" % BODY_TARGET_TOKENS, rel)
        return
    measured = count_fn(body)
    if measured >= BODY_MAX_TOKENS:
        a.gap("BODY_TOKENS", "body is %d tokens (%s), the budget is < %d"
              % (measured, tok_name, BODY_MAX_TOKENS), rel)
        over = True
    if not over:
        a.ok("BODY_BUDGET", "body is %d lines / %d tokens (%s; budget %d / %d)"
             % (n_lines, measured, tok_name, BODY_MAX_LINES, BODY_MAX_TOKENS), rel)
    # The house half, and it is the same rule DESC_HEADROOM applies to the other
    # field: a body at the ceiling cannot absorb the next paragraph, so it gets
    # absorbed into a reference that should have been split instead. House
    # thresholds ride the MEASURED count only — a house rule on an estimate is
    # a verdict on the instrument.
    if house and not over and measured >= BODY_TARGET_TOKENS:
        a.gap("BODY_HEADROOM", "body is %d tokens (%s) — inside the %d budget but "
              "past the %d working limit (house rule): the next section will "
              "breach it, and the answer then is a split, not a trim"
              % (measured, tok_name, BODY_MAX_TOKENS, BODY_TARGET_TOKENS), rel)
    elif house and not over:
        a.ok("BODY_HEADROOM", "body is %d/%d tokens (%s), inside the working limit"
             % (measured, BODY_TARGET_TOKENS, tok_name), rel)


def _bundle_closure(skill_dir, skill_text):
    """Bundled files reachable from SKILL.md, following links between them.

    Reachability is transitive, not one hop. A reference that links a sibling contract
    makes that sibling reachable, and shipping the first without the second is what
    leaves a dangling link on the target agent — so a packager that computes what a
    skill needs has to take the closure, and the check has to agree with it. Measured
    against super-ux, where the one-hop reading called 29 transitively-linked contracts
    dead weight.
    """
    available = {}
    for sub in BUNDLE_DIRS:
        d = os.path.join(skill_dir, sub)
        if not os.path.isdir(d):
            continue
        for entry in os.listdir(d):
            if os.path.isfile(os.path.join(d, entry)):
                available["%s/%s" % (sub, entry)] = os.path.join(d, entry)

    def named_in(text):
        """Keys this text reaches: by link, by path, or by bare filename.

        A script the body tells the agent to run is named in prose and a command —
        `python3 scripts/gsc_pull.py`, or just `gsc_pull.py` in a list of what ships —
        never as a markdown link. It is the opposite of dead weight, so matching only
        link syntax reports the files a skill leans on hardest.
        """
        hits = set()
        for key, _path in available.items():
            base = key.split("/", 1)[1]
            if key in text or base in text:
                hits.add(key)
        for target in LINK_RE.findall(text):
            t = target.split("#", 1)[0].strip().lstrip("./")
            if not t or "://" in t:
                continue
            for key in available:
                if key == t or key.endswith("/" + t):
                    hits.add(key)
        return hits

    seen = set()
    stack = list(named_in(skill_text))
    while stack:
        key = stack.pop()
        if key in seen:
            continue
        seen.add(key)
        if not key.endswith(".md"):
            continue
        try:
            txt = open(available[key], encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        stack.extend(k for k in named_in(txt) if k not in seen)
    return seen


def _check_bundle(a, skill_dir, skill_text, dir_name):
    """references/ scripts/ assets/: one level deep, reachable, navigable."""
    reachable = _bundle_closure(skill_dir, skill_text)
    for sub in BUNDLE_DIRS:
        d = os.path.join(skill_dir, sub)
        if not os.path.isdir(d):
            continue
        for entry in sorted(os.listdir(d)):
            full = os.path.join(d, entry)
            rel = os.path.join(dir_name, sub, entry)
            if os.path.isdir(full):
                a.gap("BUNDLE_NESTED", "%s/%s/ is nested — keep bundled files one level "
                      "deep, or the agent previews them instead of reading them"
                      % (sub, entry), rel)
                continue
            if "%s/%s" % (sub, entry) not in reachable:
                a.gap("BUNDLE_UNREACHABLE", "%s/%s is not reachable from SKILL.md, "
                      "directly or through another bundled file — an unreachable file "
                      "is dead weight the agent never opens" % (sub, entry), rel)
                continue
            if entry.endswith(".md"):
                txt = open(full, encoding="utf-8").read()
                n = txt.count("\n") + 1
                if n > TOC_MIN_LINES and "\n## Contents" not in txt:
                    a.gap("REF_NO_TOC", "%d lines with no '## Contents' list — past %d "
                          "lines an agent previews with head and never learns what the "
                          "rest holds" % (n, TOC_MIN_LINES), rel)
    if any(os.path.isdir(os.path.join(skill_dir, s)) for s in BUNDLE_DIRS):
        a.ok("BUNDLE_LAYOUT", "bundled directories present and checked")


def _check_links(a, skill_dir, skill_text, rel):
    """A relative link that escapes the skill directory arrives broken everywhere.

    Reported per line: the canon defines evidence as a `file:line`, so a finding
    without one forces the agent to either drop the evidence or invent it.
    """
    bad = False
    for i, line in enumerate(skill_text.split("\n"), start=1):
        for target in LINK_RE.findall(line):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if target.startswith("../") or "/../" in target:
                # An escape that lands on a sibling skill in the same tree is a
                # cross-skill link inside one plugin, and every packager measured
                # ships those siblings together — `npx skills add <repo> --skills
                # <one>` installed the sibling too, and all eleven links resolved.
                # An escape that lands nowhere is the defect this check is for.
                out = os.path.normpath(os.path.join(skill_dir, target.split("#")[0]))
                if os.path.exists(out):
                    continue
                a.gap("LINK_ESCAPE", "link %r leaves the skill directory and resolves "
                      "to nothing — a sibling would ship alongside, this will not"
                      % target, rel, i)
                bad = True
                continue
            path = os.path.normpath(os.path.join(skill_dir, target.split("#")[0]))
            if not os.path.exists(path):
                a.gap("LINK_BROKEN", "link %r does not resolve" % target, rel, i)
                bad = True
    if not bad:
        a.ok("LINK_INTEGRITY", "every relative link resolves and stays inside the skill", rel)


def _strip_quoted(line):
    """Blank out quoted and backticked spans.

    A skill that teaches an anti-pattern quotes it — "Before August, use the old
    API" is the example, not the instruction. Matching inside quotes would flag
    every doc that warns about the thing it detects, which is how a linter earns
    the habit of being ignored.
    """
    return re.sub(r"`[^`]*`|\"[^\"]*\"|'[^']*'|“[^”]*”", " ", line)


def _check_prose(a, body, rel):
    """Content rules that are mechanically detectable."""
    for i, raw in enumerate(body.split("\n"), start=1):
        line = _strip_quoted(raw)
        for hit in WIN_PATH_RE.findall(line):
            a.gap("WIN_PATH", "Windows-style path %r — forward slashes work on every "
                  "platform, backslashes break on Unix" % hit, rel, i)
        if TIME_BRANCH_RE.search(line) and re.search(r"\buse\b|\bswitch\b|\bapply\b", line, re.I):
            a.gap("TIME_BRANCH", "time-branching instruction (%r) — it is wrong the day "
                  "it ships; put superseded material under '## Old patterns'"
                  % raw.strip()[:60], rel, i)
    # A pointer at a directory rather than a file with a load condition. Quoted
    # spans are blanked here too: a canon that forbids "see references/" has to
    # be able to quote the phrase it forbids.
    for i, raw in enumerate(body.split("\n"), start=1):
        line = _strip_quoted(raw)
        if re.search(r"\b(?:see|read)\s+`?(?:references|scripts|assets)/`?(?![\w.-])", line, re.I):
            a.gap("REF_NO_TRIGGER", "points at a directory instead of a file with a "
                  "stated load condition — 'read X when Y' beats 'see references/'", rel, i)
    if not [r for r in a.results if r["check"] in ("WIN_PATH", "TIME_BRANCH", "REF_NO_TRIGGER")]:
        a.ok("PROSE", "no Windows paths, time-branching, or bare directory pointers", rel)


def main(argv):
    p = argparse.ArgumentParser(
        description="Audit a skill directory against the Agent Skills standard.")
    p.add_argument("skill_dir", help="the directory containing SKILL.md")
    p.add_argument("--house", action="store_true",
                   help="also apply the ssheleg canon: Use-when opener, EN+RU triggers, "
                        "and the 5%% working headroom on BOTH the description (970 of "
                        "1024) and the body (4750 of 5000)")
    p.add_argument("--json", action="store_true", help="emit results as JSON")
    p.add_argument("--quiet", action="store_true", help="print GAP lines only")
    args = p.parse_args(argv[1:])

    a = audit(args.skill_dir, house=args.house)

    if args.json:
        print(json.dumps(a.results, indent=2, ensure_ascii=False))
    else:
        for r in a.results:
            if args.quiet and r["verdict"] == "PASS":
                continue
            where = r["file"] or ""
            if r["line"]:
                where += ":%d" % r["line"]
            print("%-4s %-18s %-28s %s" % (r["verdict"], r["check"], where, r["message"]))
        n_gap = len(a.gaps)
        print("\n%d GAP, %d PASS — %s" % (n_gap, len(a.results) - n_gap, args.skill_dir))
        if n_gap:
            print("Fix these, then re-run. The judgement half of the audit "
                  "(one job, entry point, evals, distribution) is in references/retrofit.md.")
    return 1 if a.gaps else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

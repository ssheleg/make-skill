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
  --house   adds the ssheleg canon: description starts "Use when …" and carries
            English AND Russian trigger phrases

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
COMPAT_MAX = 500        # spec: compatibility is 1-500 characters
BODY_MAX_LINES = 500    # spec + Anthropic: keep the body under 500 lines
BODY_MAX_TOKENS = 5000  # spec + Anthropic: level-2 budget
# No tokenizer in the stdlib. 3.9 chars/token is measured, not assumed: tokenizing
# this skill's own bundle gives 3.78-4.47. `claude plugin details` is far more
# pessimistic (~2.8) and will always show a bigger number than this estimate.
CHARS_PER_TOKEN = 3.9
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
    """
    data, lines, key, mode = {}, {}, None, None
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
                data[key], mode = _unquote(val), None
        elif mode == "block":
            data[key] = (data[key] + " " + raw.strip()).strip()
        elif mode == "map":
            m = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", raw)
            if m:
                data[key][m.group(1)] = _unquote(m.group(2).strip())
    return data, lines


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
    _check_body_budget(a, body, rel)
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


def _check_body_budget(a, body, rel):
    n_lines = body.count("\n") + 1
    est = int(len(body) / CHARS_PER_TOKEN)
    # Both, not either: a body over the line budget still has to report its
    # token count, or the second fix arrives only after the first one ships.
    over = False
    if n_lines >= BODY_MAX_LINES:
        a.gap("BODY_LINES", "body is %d lines, the budget is < %d — move detail into "
              "references/" % (n_lines, BODY_MAX_LINES), rel)
        over = True
    if est >= BODY_MAX_TOKENS:
        a.gap("BODY_TOKENS", "body is ~%d tokens (%d chars / %s), the budget is < %d"
              % (est, len(body), CHARS_PER_TOKEN, BODY_MAX_TOKENS), rel)
        over = True
    if not over:
        a.ok("BODY_BUDGET", "body is %d lines / ~%d tokens (budget %d / %d)"
             % (n_lines, est, BODY_MAX_LINES, BODY_MAX_TOKENS), rel)


def _check_bundle(a, skill_dir, skill_text, dir_name):
    """references/ scripts/ assets/: one level deep, reachable, navigable."""
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
            if "%s/%s" % (sub, entry) not in skill_text:
                a.gap("BUNDLE_UNREACHABLE", "%s/%s is never referenced from SKILL.md — "
                      "an unreachable file is dead weight the agent never opens"
                      % (sub, entry), rel)
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
                a.gap("LINK_ESCAPE", "link %r escapes the skill directory — packagers "
                      "ship that directory alone, so it arrives broken on every agent"
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
                   help="also apply the ssheleg canon (Use-when opener, EN+RU triggers)")
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

#!/usr/bin/env bash
# PostToolUse: after a SKILL.md is written or edited, audit its directory against
# the Agent Skills standard and hand the result back as a system message.
#
# Contract, in this order:
#   1. Not a SKILL.md write?      exit 0 immediately, print nothing. A globally
#                                 installed plugin must be invisible in projects
#                                 that do not author skills.
#   2. No python3 on PATH?        exit 0 with no message. The audit is an
#                                 accelerator; its absence must not surface as a
#                                 hook error on someone else's machine.
#   3. Skill has gaps?            exit 0 with a systemMessage naming them. Never
#                                 exit 2: PostToolUse fires after the write, so
#                                 blocking buys nothing and costs a turn.
#   4. Malformed payload?         exit 0, print nothing. Hooks fail silent.
#
# Which writes count: Claude Code's Write/Edit/MultiEdit carry `tool_input.file_path`.
# Codex edits with `apply_patch`, whose patch text sits in `tool_input.command` (or
# `.input`) and names its files on `*** Add File:`, `*** Update File:`,
# `*** Delete File:` and `*** Move to:` lines (0.33.4, hub B-211); every such path is
# read, relative ones against the payload's `cwd`, and each SKILL.md that still exists
# after the patch is audited.
#
# Everything this reads comes from the hook's stdin JSON; nothing is written.
set -uo pipefail

payload="$(cat)"

# Cheap pre-filter: no payload that names no SKILL.md starts an interpreter.
case "$payload" in
  *SKILL.md*) ;;
  *) exit 0 ;;
esac

command -v python3 >/dev/null 2>&1 || exit 0

# Every SKILL.md path this call wrote, one per line, without assuming jq exists.
paths="$(printf '%s' "$payload" | python3 -c '
import json, os, re, sys
try:
    d = json.load(sys.stdin)
    if not isinstance(d, dict):
        sys.exit(0)
    ti = d.get("tool_input")
    found = []
    if d.get("tool_name") == "apply_patch":
        txt = (ti.get("command") or ti.get("input") or "") if isinstance(ti, dict) else (ti or "")
        if isinstance(txt, list):
            txt = "\n".join(x for x in txt if isinstance(x, str))
        if isinstance(txt, str):
            for a, b in re.findall(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$|^\*\*\* Move to: (.+)$", txt, re.M):
                found.append((a or b).strip())
        cwd = d.get("cwd") if isinstance(d.get("cwd"), str) else ""
        found = [os.path.join(cwd, p) if cwd and not os.path.isabs(p) else p for p in found]
    elif isinstance(ti, dict) and isinstance(ti.get("file_path"), str):
        found.append(ti["file_path"])
    seen = []
    for p in found:
        if (p == "SKILL.md" or p.endswith("/SKILL.md")) and p not in seen:
            seen.append(p)
    print("\n".join(seen))
except Exception:
    pass
' 2>/dev/null)" || exit 0

[ -n "$paths" ] || exit 0

auditor="${CLAUDE_PLUGIN_ROOT:-}/skills/make-skill/scripts/audit_skill.py"
[ -f "$auditor" ] || exit 0

reports=""
while IFS= read -r file_path; do
  [ -n "$file_path" ] || continue
  [ -f "$file_path" ] || continue
  skill_dir="$(dirname "$file_path")"
  report="$(python3 "$auditor" "$skill_dir" --quiet 2>/dev/null)" && continue
  # Non-zero from the auditor means GAPs were found.
  reports="${reports:+$reports

}$report"
done <<< "$paths"

[ -n "$reports" ] || exit 0

# Escape the reports for JSON and hand them back as advice: one object, whatever
# the number of skills the call touched.
escaped="$(printf '%s' "$reports" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
printf '{"systemMessage": %s, "suppressOutput": true}\n' "$escaped"
exit 0

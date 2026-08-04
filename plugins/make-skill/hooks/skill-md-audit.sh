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
#
# Everything this reads comes from the hook's stdin JSON; nothing is written.
set -uo pipefail

payload="$(cat)"

# Extract the written path without assuming jq exists (it usually does not).
file_path="$(printf '%s' "$payload" |
  sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"

case "$file_path" in
  */SKILL.md|SKILL.md) ;;
  *) exit 0 ;;
esac

[ -f "$file_path" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

skill_dir="$(dirname "$file_path")"
auditor="${CLAUDE_PLUGIN_ROOT:-}/skills/make-skill/scripts/audit_skill.py"
[ -f "$auditor" ] || exit 0

report="$(python3 "$auditor" "$skill_dir" --quiet 2>/dev/null)" && exit 0

# Non-zero from the auditor means GAPs were found. Escape the report for JSON
# with the tools every POSIX box has, then hand it back as advice.
escaped="$(printf '%s' "$report" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
printf '{"systemMessage": %s, "suppressOutput": true}\n' "$escaped"
exit 0

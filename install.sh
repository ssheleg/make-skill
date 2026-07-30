#!/usr/bin/env bash
# Installs the make-skill skill into ~/.claude/skills (that is what gives
# /make-skill; a same-named command file would register it a second time).
# Idempotent: skips anything already installed; pass --force to overwrite.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
elif [[ -n "${1:-}" ]]; then
  echo "usage: $0 [--force]" >&2
  exit 2
fi

SRC="$HERE/plugins/make-skill/skills/make-skill"
DEST="${HOME}/.claude/skills/make-skill"
if [[ -e "$DEST" && "$FORCE" -eq 0 ]]; then
  echo "skip: skill already installed at $DEST (rerun with --force to overwrite)"
else
  mkdir -p "$(dirname "$DEST")"
  rm -rf "$DEST"
  cp -R "$SRC" "$DEST"
  echo "Installed make-skill skill   -> $DEST"
fi


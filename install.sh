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

# One channel per agent: a plain copy beside an installed plugin is two listings
# of the same skill, and the stale one wins. Refuse rather than create that, and
# refuse loudly — until v0.25.0 this keyed on the marketplaces/ dir alone and
# exited 0, the fail-open class: a directory-sourced marketplace has no dir
# there, plugin names differ from marketplace names, and an exit 0 reads as
# success to every script above it. installed_plugins.json is the record of
# what is installed; a missing or unparsable one reads as "no plugin".
INSTALLED_JSON="${HOME}/.claude/plugins/installed_plugins.json"
MARKETPLACE="${HOME}/.claude/plugins/marketplaces/make-skill"
SPEC=""
if [[ -f "$INSTALLED_JSON" ]]; then
  SPEC="$(sed -n 's/.*"\(make-skill@[^"]*\)".*/\1/p' "$INSTALLED_JSON" 2>/dev/null | head -n 1)" || true
fi
if [[ ( -n "$SPEC" || -e "$MARKETPLACE" ) && "$FORCE" -eq 0 ]]; then
  {
    if [[ -n "$SPEC" ]]; then
      echo "refused: make-skill is already installed as the Claude Code plugin $SPEC"
      echo "         (declared in ~/.claude/plugins/installed_plugins.json)."
    else
      echo "refused: make-skill is already registered as a Claude Code marketplace"
      echo "         ($MARKETPLACE)."
    fi
    echo "         A plain copy in ~/.claude/skills would shadow the plugin and serve"
    echo "         this frozen version forever. Update the plugin channel instead:"
    echo "           claude plugin marketplace update make-skill"
    echo "           claude plugin update ${SPEC:-make-skill@make-skill}"
    echo "         Family launcher: npx --yes sshlg-skills@latest update"
    echo "         Pass --force to write the plain copy anyway."
  } >&2
  exit 3
fi

if [[ -e "$DEST" && "$FORCE" -eq 0 ]]; then
  echo "skip: skill already installed at $DEST (rerun with --force to overwrite)"
else
  mkdir -p "$(dirname "$DEST")"
  rm -rf "$DEST"
  cp -R "$SRC" "$DEST"
  echo "Installed make-skill skill   -> $DEST"
  # The last line says how the next version arrives.
  echo "Updates: git pull && ./install.sh --force, or npx --yes sshlg-skills@latest update"
fi


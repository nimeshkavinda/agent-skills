#!/usr/bin/env bash
# Link this repo's skills and AGENTS.md into every AI tool found on this machine.
# Safe to rerun. Anything it would replace is moved to ~/.agent-skills-backup/<timestamp>/.
# Usage: ./install.sh [--dry-run]
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP="$HOME/.agent-skills-backup/$(date +%Y%m%d-%H%M%S)"
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

run() { if ((DRY)); then echo "  would: $*"; else "$@"; fi; }

backup() {
  local target="$1"
  echo "  backing up $target"
  run mkdir -p "$BACKUP/$(dirname "${target#$HOME/}")"
  run mv "$target" "$BACKUP/${target#$HOME/}"
}

# link SRC DEST: point DEST at SRC, backing up whatever was there unless it's already ours.
link() {
  local src="$1" dest="$2"
  if [[ -L "$dest" && "$(readlink "$dest")" == "$src" ]]; then return; fi
  if [[ -L "$dest" ]]; then
    run rm "$dest"
  elif [[ -e "$dest" ]]; then
    if [[ -f "$dest" && ! -s "$dest" ]]; then run rm "$dest"; else backup "$dest"; fi
  fi
  run mkdir -p "$(dirname "$dest")"
  run ln -s "$src" "$dest"
  echo "  linked $dest"
}

# Per-skill links, so skills from other sources in the same folder are left alone.
link_skills() {
  local dir="$1"
  echo "skills -> $dir"
  for skill in "$REPO"/skills/*/; do
    skill="${skill%/}"
    link "$skill" "$dir/$(basename "$skill")"
  done
  # Drop links to skills that were removed from the repo.
  [[ -d "$dir" ]] || return 0
  for entry in "$dir"/*; do
    if [[ -L "$entry" && "$(readlink "$entry")" == "$REPO/skills/"* && ! -e "$entry" ]]; then
      run rm "$entry"
      echo "  removed stale $entry"
    fi
  done
}

has() { [[ -d "$HOME/$1" ]]; }

# Shared location read by Codex, Gemini CLI, Copilot, OpenCode and other Agent Skills tools.
link_skills "$HOME/.agents/skills"

if has .claude; then
  echo "Claude Code"
  link_skills "$HOME/.claude/skills"
  link "$REPO/AGENTS.md" "$HOME/.claude/CLAUDE.md"
  if [[ -f "$REPO/claude/plugins.json" && -f "$HOME/.claude/settings.json" ]] && command -v jq >/dev/null; then
    echo "  merging claude/plugins.json into ~/.claude/settings.json"
    if ((! DRY)); then
      tmp="$(mktemp)"
      jq --slurpfile p "$REPO/claude/plugins.json" \
        '.enabledPlugins = ((.enabledPlugins // {}) + $p[0].enabledPlugins)
         | .extraKnownMarketplaces = ((.extraKnownMarketplaces // {}) + $p[0].extraKnownMarketplaces)' \
        "$HOME/.claude/settings.json" >"$tmp" && mv "$tmp" "$HOME/.claude/settings.json"
    fi
  fi
fi

if has .codex; then
  echo "Codex"
  link "$REPO/AGENTS.md" "$HOME/.codex/AGENTS.md"
fi

if has .gemini; then
  echo "Gemini CLI"
  link "$REPO/AGENTS.md" "$HOME/.gemini/GEMINI.md"
fi

if has .cursor; then
  echo "Cursor"
  link_skills "$HOME/.cursor/skills"
  echo "  Cursor keeps global rules in Settings > Rules, not in a file. Paste AGENTS.md there once."
fi

((DRY)) && echo "Dry run only. Nothing changed."
[[ -d "$BACKUP" ]] && echo "Replaced files were moved to $BACKUP"
echo "Done."

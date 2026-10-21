#!/usr/bin/env bash
# Show how each vendored skill differs from the latest upstream version.
# Usage: scripts/upstream-diff.sh [upstream-name]   (names are the keys in sources.json)
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

for name in $(jq -r '.upstreams | keys[]' "$REPO/sources.json"); do
  [[ -n "${1:-}" && "$1" != "$name" ]] && continue
  url=$(jq -r ".upstreams[\"$name\"].repo" "$REPO/sources.json")
  path=$(jq -r ".upstreams[\"$name\"].path" "$REPO/sources.json")
  echo "=== $name ($url)"
  git clone -q --depth 1 "$url" "$TMP/$name"
  echo "upstream is at $(git -C "$TMP/$name" rev-parse HEAD)"
  for skill in $(jq -r ".upstreams[\"$name\"].skills[]" "$REPO/sources.json"); do
    upstream_dir=$(find "$TMP/$name/$path" -type d -name "$skill" | head -1)
    if [[ -z "$upstream_dir" ]]; then
      echo "--- $skill: no longer upstream"
      continue
    fi
    diff -ru "$REPO/skills/$skill" "$upstream_dir" >"$TMP/$skill.diff" || true
    if [[ -s "$TMP/$skill.diff" ]]; then
      echo "--- $skill: differs (local edits or upstream changes)"
      cat "$TMP/$skill.diff"
    else
      echo "--- $skill: same"
    fi
  done
done

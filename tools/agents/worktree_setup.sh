#!/usr/bin/env bash
# Create a worktree for a second Claude Code session. Usage: bash tools/agents/worktree_setup.sh <name> [parent_dir]
set -euo pipefail
NAME="${1:?usage: worktree_setup.sh <name> [parent_dir]}"
REPO="$(git rev-parse --show-toplevel)"
PARENT="${2:-$(dirname "$REPO")}"
WT="$PARENT/$(basename "$REPO")-$NAME"
BR="cd/$NAME"
git -C "$REPO" fetch origin campaign-design
git -C "$REPO" config rerere.enabled true
if [ -e "$WT" ]; then echo "exists: $WT"; else git -C "$REPO" worktree add -b "$BR" "$WT" origin/campaign-design; fi
DEPS="$PARENT/concordia-deps/i5jb"
if [ ! -f "$DEPS/mtgish/data/mtgish.lines.json" ]; then
  mkdir -p "$DEPS"
  GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/i5jb/mtgish "$DEPS/mtgish" || echo "mtgish clone failed; set MTGISH_DATA by hand"
fi
export MTGISH_DATA="$DEPS/mtgish/data/mtgish.lines.json"
echo "worktree: $WT  branch: $BR"
echo "add to your shell profile: export MTGISH_DATA=$MTGISH_DATA"
cd "$WT" && python3 tools/agents/clone_verify.py || true

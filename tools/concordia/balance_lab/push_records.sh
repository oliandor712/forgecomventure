#!/bin/bash
# Safe push of one agent's records file(s) while other agents push to the same branch.
# Usage: tools/concordia/balance_lab/push_records.sh records_<worker>.csv [more files in balance_lab/ or other paths]
# Handles: detached HEAD (puts you on campaign-design), CRLF noise, non-fast-forward races (pull --no-rebase then retry with jitter).
# Never force-pushes. Commits only the named files (files already staged by someone else stay staged, uncommitted).
# Pushes only when the user has said "push": set PUSH_APPROVED=1 yourself after that, never otherwise.
cd "$(git rev-parse --show-toplevel)" || exit 1
[ "$PUSH_APPROVED" = "1" ] || { echo "refused: push only when the user says push (then run with PUSH_APPROVED=1)"; exit 3; }
B=campaign-design
files=()
for f in "$@"; do [ -e "$f" ] && files+=("$f") || files+=("tools/concordia/balance_lab/$f"); done
[ ${#files[@]} -gt 0 ] || { echo "usage: push_records.sh <file>..."; exit 2; }
if [ "$(git rev-parse --abbrev-ref HEAD)" != "$B" ]; then
  git checkout -q -B "$B" 2>/dev/null || { git stash -q; git checkout -q -B "$B"; git stash pop -q; }
fi
git add "${files[@]}" 2>/dev/null
git commit -q -m "Balance records: ${files[*]##*/}" -m "Co-Authored-By: Claude <noreply@anthropic.com>" -- "${files[@]}" 2>/dev/null
for i in 1 2 3 4 5 6; do
  git pull --no-rebase -q --no-edit origin "$B" || { echo "pull failed (merge conflict or network); resolve it, then rerun. Not pushed."; exit 1; }
  if err=$(git push -q origin "HEAD:$B" 2>&1); then echo "pushed (try $i)"; exit 0; fi
  sleep $((RANDOM % 8 + 2 * i))
done
echo "push failed after 6 tries; last error:"; echo "$err"; exit 1

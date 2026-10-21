#!/usr/bin/env bash
# Mass run (user, 2026-10-21): 40 inner-tier pairings in 5 batches of 8, each batch within the 10-minute compute limit.
# Each batch appends to records.csv, commits and pushes. The batch runner holds a lock, so an hourly batch skips while this runs.
# Usage: tools/concordia/balance_lab/mass_run.sh [batches]
cd "$(dirname "$0")/../../.." || exit 1
BATCHES=${1:-5}
tools/concordia/sim/setup.sh >/dev/null 2>&1 || echo "setup.sh failed; batches may fail"
for i in $(seq 1 "$BATCHES"); do
  echo "batch $i of $BATCHES $(date -u +%H:%M:%SZ)"
  python3 tools/concordia/balance_lab/run_batch.py --pairings 8 --sets 5 || echo "batch $i failed"
  git add tools/concordia/balance_lab/records.csv
  if ! git diff --cached --quiet; then
    git commit -q -m "Balance lab: mass run batch $i of $BATCHES

Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011UrsiVw1s1nsvYUSkv2iLy"
    git pull --no-rebase -q origin campaign-design
    for d in 0 2 4 8 16; do
      git push -q -u origin campaign-design && break
      sleep "$d"; git pull --no-rebase -q origin campaign-design
    done
  fi
done
echo "mass run done $(date -u +%H:%M:%SZ)"

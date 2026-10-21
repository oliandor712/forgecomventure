#!/bin/bash
# One foreground chunk (about 9 minutes) of balance games, then a safe push. Call it again and again in the SAME turn until it prints DONE.
# Why: a background process dies when the agent's turn ends and the container goes idle. A foreground call keeps the container awake.
# Usage: tools/concordia/balance_lab/run_foreground.sh <shard W|U|B|R|G|multi> <worker> [slice k/n]
# Example: tools/concordia/balance_lab/run_foreground.sh multi main 0/2
# Progress is counted from records*.csv, so every call resumes where the last one stopped. Never run two chunks of the same worker at once.
cd "$(git rev-parse --show-toplevel)" || exit 1
SHARD=$1; WORKER=$2; SLICE=$3
[ -n "$SHARD" ] && [ -n "$WORKER" ] || { echo "usage: run_foreground.sh <shard> <worker> [k/n]"; exit 2; }
export BALANCE_WORKER=$WORKER; [ -n "$SLICE" ] && export BALANCE_SLICE=$SLICE
git pull --no-rebase -q origin campaign-design 2>/dev/null
timeout ${CHUNK_SECONDS:-540} python3 tools/concordia/balance_lab/run_batch.py --shard "$SHARD" --until-done 2>&1 | tail -3
for p in $(ps -eo pid,args | awk '/DeckSim/ && !/awk/ {print $1}'); do kill "$p" 2>/dev/null; done
tools/concordia/balance_lab/push_records.sh "records_${WORKER}.csv" 2>&1 | tail -1
python3 - "$SHARD" "$SLICE" <<'P'
import sys,os
sys.path.insert(0,'tools/concordia/balance_lab')
import run_batch as rb
shard,sl=sys.argv[1],sys.argv[2]
pool=sorted(rb.shard_decks(shard))
if sl:
    k,n=map(int,sl.split('/')); pool=[d for i,d in enumerate(pool) if i%n==k]
c=rb.counts(rb.load())
left=[d for d in pool if c.get(rb.rel(d),0)<rb.target_for(d)]
print("DONE" if not left else "NOT DONE: %d of %d decks below target"%(len(left),len(pool)))
P

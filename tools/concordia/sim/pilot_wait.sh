#!/bin/bash
# Waits for the next PilotSim decision for one side and prints it (or DONE when the match is over).
#   tools/concordia/sim/pilot_wait.sh <pilotDir> <A|B> [maxSec]
# Answer by writing <pilotDir>/ans_<side>_<n>.txt: first line the option, then your reasoning.
d=$1; side=$2; max=${3:-540}; end=$((SECONDS + max))
while [ $SECONDS -lt $end ]; do
    for r in $(ls "$d"/req_"$side"_*.txt 2>/dev/null | sort -t_ -k3 -n); do
        a=${r/req_/ans_}
        [ -f "$a" ] || { echo "PENDING $(basename "$r" .txt | sed 's/req_//')"; cat "$r"; exit 0; }
    done
    [ -f "$d/done" ] && { echo DONE; exit 0; }
    sleep 0.5
done
echo WAITING

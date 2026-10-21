#!/bin/bash
# run_exp.sh <label> <watch cards, comma sep> <deckA> <deckB> <patchedAssetsDir>
# Runs baseline (forge-gui/) and patched (scratch assets) in parallel: 10 games, no per-game cap (86400 s), equal life 20, phase-annotated
# logs in tools/concordia/ai_lab/results/<label>-{baseline,patched}/. Output: results/<label>-summary.txt
set -e
cd "$(dirname "$0")/../../.."
L=$1; W=$2; A=$3; B=$4; P=$5; R=tools/concordia/ai_lab/results
for c in baseline patched; do
  AS=forge-gui/; [ $c = patched ] && AS=$P/
  ( java -Xmx3g -Djava.awt.headless=true "-Dwatch=$W" -Dlogdir=$R/$L-$c -cp "$(cat ~/.cache/forge-sim/labcp.txt)" AiLabSim $AS 10 86400 $A 20 $B 20 $L-$c 2>&1 | grep -E 'RESULT|PLAYS|rror' > $R/$L-$c.raw ) &
done
wait
for c in baseline patched; do
  grep RESULT $R/$L-$c.raw
  awk -F'\t' '/PLAYS/{split($5,m,"=");split($6,c,"=");split($7,a,"=");k=$4;ms[k]+=m[2];cs[k]+=c[2];as[k]+=a[2];if(m[2]>0)g[k]++} END{for(k in cs)print "  "k" games_seen="g[k]+0" casts="cs[k]" activations="as[k]}' $R/$L-$c.raw
done > $R/$L-summary.txt

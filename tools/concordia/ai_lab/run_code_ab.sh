#!/bin/bash
# run_code_ab.sh <label> <watch cards> <deckA> <deckB>
# A/B of a forge-ai code patch: "base" = unpatched jars + scratch assets (card flags removed), "code" = patched scratch
# worktree jars + the same scratch assets. 10 games, no per-game cap (86400 s), equal life 20; logs in results/<label>-{base,code}/.
set -e
cd "$(dirname "$0")/../../.."
L=$1; W=$2; A=$3; B=$4; R=tools/concordia/ai_lab/results
SC=${SCRATCH:?set SCRATCH to the scratchpad dir containing assets/ and simcache-patched/}
for c in base code; do
  CPF=~/.cache/forge-sim/labcp.txt; [ $c = code ] && CPF=${CODE_CP:-$SC/simcache-patched/cp.txt}
  ( java -Xmx3g -Djava.awt.headless=true "-Dwatch=$W" -Dlogdir=$R/$L-$c -cp "$(cat $CPF)" AiLabSim $SC/assets/ 10 86400 $A 20 $B 20 $L-$c 2>&1 | grep -E 'RESULT|PLAYS|rror' > $R/$L-$c.raw ) &
done
wait
for c in base code; do
  grep RESULT $R/$L-$c.raw
  awk -F'\t' '/PLAYS/{split($5,m,"=");split($6,c,"=");split($7,a,"=");k=$4;cs[k]+=c[2];as[k]+=a[2];if(m[2]>0)g[k]++} END{for(k in cs)print "  "k" games_seen="g[k]+0" casts="cs[k]" activations="as[k]}' $R/$L-$c.raw
done > $R/$L-summary.txt

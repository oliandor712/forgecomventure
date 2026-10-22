#!/bin/bash
# ab_recipe.sh <label> <games> <deckA.dck> <deckB.dck> "<watch cards, comma separated>" [--code PATCH]... [--cards PATCH]... [--base-cards PATCH]...
# Stock-vs-patched A/B with AiLabSim from campaign-design alone (run tools/concordia/sim/setup.sh first). Equal life 20.
#   --code P        forge-ai code patch (file name in ai_lab/patches/), compiled on top of the test overlay for the "patched" arm only
#   --cards P       card-script patch (diff of forge-gui/res/cardsfolder), applied to the "patched" arm's scratch assets only
#   --base-cards P  card-script patch applied to BOTH arms (e.g. 001 unflag, so the arms differ only in the code patch)
# Both arms run in parallel (4 cores: one worker per ab_recipe.sh call). Output: $AB_OUT/<label>/{base,patched}.raw, per-game logs,
# summary.txt (RESULT lines, casts, activations). Scratch in $AB_TMP (default /tmp/ab_<label>); nothing touches the repo.
# AiLabSim has no seed, so give two workers different <label>s and sum their summaries.
set -e
ROOT=$(cd "$(dirname "$0")/../../.." && pwd); cd "$ROOT"
L=$1; N=$2; DA=$3; DB=$4; W=$5; shift 5
CODE=(); CARDS=(); BCARDS=()
while [ $# -gt 0 ]; do case $1 in --code) CODE+=("$2");; --cards) CARDS+=("$2");; --base-cards) BCARDS+=("$2");; esac; shift 2; done
T=${AB_TMP:-/tmp/ab_$L}; O=${AB_OUT:-$ROOT/tools/concordia/ai_lab/results/ab}/$L; PD=tools/concordia/ai_lab/patches
CACHE=${SIM_CACHE:-$HOME/.cache/forge-sim}; CPB=$(cat "$CACHE/cp.txt")
rm -rf "$T"; mkdir -p "$T" "$O"
mkassets() {  # $1 = dir, rest = card patches; res/ symlinked except a copied cardsfolder
  local d=$1; shift; mkdir -p $d/res
  for e in $ROOT/forge-gui/*; do b=$(basename $e); [ $b = res ] || ln -sfn $e $d/$b; done
  for e in $ROOT/forge-gui/res/*; do b=$(basename $e); [ $b = cardsfolder ] || ln -sfn $e $d/res/$b; done
  cp -r $ROOT/forge-gui/res/cardsfolder $d/res/cardsfolder
  for p in "$@"; do (cd $d && patch -p2 -s < $ROOT/$PD/$p); done
}
mkassets $T/assets_base "${BCARDS[@]}"; mkassets $T/assets_patched "${BCARDS[@]}" "${CARDS[@]}"
CPP=$CPB
if [ ${#CODE[@]} -gt 0 ]; then
  mkdir -p $T/ai/classes; cp -r "$CACHE/aipatch/src" $T/ai/src 2>/dev/null || mkdir -p $T/ai/src
  for p in "${CODE[@]}"; do
    for f in $(grep '^--- a/' $PD/$p | sed 's#^--- a/##'); do [ -f $T/ai/src/$f ] || { mkdir -p $T/ai/src/$(dirname $f); cp $ROOT/$f $T/ai/src/$f; }; done
    (cd $T/ai/src && patch -p1 -s < $ROOT/$PD/$p)
  done
  javac -nowarn -d $T/ai/classes -cp "$CPB" $(find $T/ai/src -name '*.java') 2>&1 | grep -v "^Note\|JAVA_TOOL" >&2 || true
  CPP="$T/ai/classes:$CPB"
fi
for arm in base patched; do
  CP=$CPB; [ $arm = patched ] && CP=$CPP
  ( java -Xmx3g -Djava.awt.headless=true "-Dwatch=$W" -Dlogdir=$O/$arm -cp "$CP" AiLabSim $T/assets_$arm/ $N 900 $DA 20 $DB 20 $L-$arm > $O/$arm.raw 2>&1 ) &
done
wait
{ for arm in base patched; do grep -h RESULT $O/$arm.raw
  grep PLAYS $O/$arm.raw | awk -F'\t' '{split($6,c,"=");split($7,a,"=");cs+=c[2];as+=a[2]} END{print "  casts "cs" activations "as}'; done; } | tee $O/summary.txt

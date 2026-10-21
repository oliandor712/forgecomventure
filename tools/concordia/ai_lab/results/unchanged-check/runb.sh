#!/bin/bash
# usage: run.sh <arm: stock|cons> <part 0|1>   -> /tmp/claude-0/uc/<arm>/p<part>.res and logs
cd /home/user/forgecomventure
D=forge-gui/res/adventure/Concordia/decks/tier2
arm=$1; part=$2; O=/tmp/claude-0/uc/$arm; mkdir -p $O/logs
CP=$(cat /tmp/claude-0/simcache3/cp.txt)
OPTS="-Dseed=91 -Dlogdir=$O/logs"
if [ $arm = stock ]; then CP=${CP#*:}; else OPTS="$OPTS -Daidecisionlog=1"; fi
mapfile -t decks < <(ls $D/*.dck | sort | awk 'NR%4==1 || NR%4==3' | head -40)
args=()
# simple split: pair index parity decides the part; each pair played in both seats
for ((i=0;i<20;i++)); do
  (( i % 2 == part )) || continue
  a=${decks[$i]}; b=${decks[$(( (i+7) % 40 ))]}; [ "$a" = "$b" ] && b=${decks[$(( (i+8) % 40 ))]}
  args+=("$a" 40 - "$b" 40 - a "u${i}a" "$b" 40 - "$a" 40 - b "u${i}b")
done
java -Xmx3g -Djava.awt.headless=true $OPTS -cp "$CP" BonusSim forge-gui/ 600 "${args[@]}" 2>&1 | grep "^GAME" > $O/p$part.res

#!/bin/bash
# run.sh <arm: stock|t013> <part 0|1>: 10 deck pairs x 2 seats = 20 games, seed 91, split over 2 parts
cd /home/user/forgecomventure
D=forge-gui/res/adventure/Concordia/decks/tier2
arm=$1; part=$2; O=/tmp/claude-0/uc2/$arm; mkdir -p $O/logs
if [ $arm = stock ]; then CP=$(cat /tmp/claude-0/simcache2/cp.txt); CP=${CP#*:}; OPTS="-Dseed=91 -Dlogdir=$O/logs"
else CP=$(cat /tmp/claude-0/t013/cache4/cp.txt); OPTS="-Dseed=91 -Dlogdir=$O/logs -Daidecisionlog=1"; fi
mapfile -t decks < <(ls $D/*.dck | sort | awk 'NR%4==1 || NR%4==3' | head -40)
args=()
for ((i=0;i<10;i++)); do
  (( i % 2 == part )) || continue
  a=${decks[$i]}; b=${decks[$(( (i+7) % 40 ))]}; [ "$a" = "$b" ] && b=${decks[$(( (i+8) % 40 ))]}
  args+=("$a" 40 - "$b" 40 - a "u${i}a" "$b" 40 - "$a" 40 - b "u${i}b")
done
java -Xmx3g -Djava.awt.headless=true $OPTS -cp "$CP" BonusSim forge-gui/ 600 "${args[@]}" 2>&1 | grep "^GAME" > $O/p$part.res

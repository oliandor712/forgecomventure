#!/bin/bash
# Builds everything the headless sims need in a fresh cloud container, then prints the classpath file.
#
#   tools/concordia/sim/setup.sh            # build once (a few minutes); later runs reuse the cache
#   CP=$(tools/concordia/sim/setup.sh)      # the classpath file
#   tools/concordia/sim/run.sh DeckSim <args>   # or BonusSim, or any class in tools/concordia/{sim,balance_lab}
#
# Downloads from Maven Central (reachable through the proxy). The TenPatch dependency is jitpack-only, and jitpack is
# blocked, so it is removed from forge-gui-mobile/pom.xml for the build and the pom is restored afterwards (the sims
# don't use it). Delete $SIM_CACHE (default ~/.cache/forge-sim) to rebuild from scratch; SIM_REBUILD=1 recompiles
# the reactor after Java changes.
set -e
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
CACHE=${SIM_CACHE:-$HOME/.cache/forge-sim}
GDX=1.14.2
mkdir -p "$CACHE/lib"
log() { echo "[sim setup] $*" >&2; }

fetch() {  # group/path artifact version [classifier]
    local name=$2-$3${4:+-$4}.jar
    [ -s "$CACHE/lib/$name" ] && unzip -tq "$CACHE/lib/$name" >/dev/null 2>&1 && return
    for i in 1 2 3 4; do
        curl -sSL -o "$CACHE/lib/$name" "https://repo1.maven.org/maven2/$1/$2/$3/$name" || true
        unzip -tq "$CACHE/lib/$name" >/dev/null 2>&1 && return
        sleep $((i * 4))
    done
    log "could not download $name"; exit 1
}
fetch com/badlogicgames/gdx gdx-backend-headless $GDX
fetch com/badlogicgames/gdx gdx-platform $GDX natives-desktop

if [ -n "$SIM_REBUILD" ] || [ ! -s "$CACHE/deps.txt" ] || [ ! -d "$ROOT/forge-gui-mobile/target/classes/forge" ]; then
    log "compiling the reactor (first time: several minutes, downloads dependencies)"
    cd "$ROOT"
    cp forge-gui-mobile/pom.xml "$CACHE/pom.xml.bak"
    trap 'cp "$CACHE/pom.xml.bak" "$ROOT/forge-gui-mobile/pom.xml"' EXIT
    python3 - <<'PY'
import re
p = 'forge-gui-mobile/pom.xml'
s = open(p).read()
s2 = re.sub(r'\s*<dependency>\s*<groupId>com\.github\.raeleus\.TenPatch</groupId>.*?</dependency>', '', s, count=1, flags=re.S)
s2 = re.sub(r'\s*<repository>\s*<id>jitpack\.io</id>.*?</repository>', '', s2, count=1, flags=re.S)
open(p, 'w').write(s2)
PY
    OFF=""; [ -n "$SIM_OFFLINE" ] && OFF="-o"
    mvn -B -q $OFF -pl forge-gui-mobile -am compile dependency:build-classpath -DskipTests -Dcheckstyle.skip \
        -Dmdep.outputFile="$CACHE/deps.txt" >"$CACHE/mvn.log" 2>&1 || { tail -30 "$CACHE/mvn.log" >&2; exit 1; }
    cp "$CACHE/pom.xml.bak" forge-gui-mobile/pom.xml
    trap - EXIT
fi

# the reactor's own classes, its dependencies, the headless backend
CP=""
for m in forge-gui-mobile forge-gui forge-ai forge-game forge-core; do CP="$CP:$ROOT/$m/target/classes"; done
CP="${CP#:}:$(tr -d '\n' < "$CACHE/deps.txt"):$CACHE/lib/gdx-backend-headless-$GDX.jar:$CACHE/lib/gdx-platform-$GDX-natives-desktop.jar"

# Test-only forge-ai patches (user, 2026-10-21): the patches listed in tools/concordia/ai_lab/patches/SIM_ACTIVE.txt are applied to a
# scratch copy of the affected forge-ai sources and compiled into $CACHE/aipatch/classes, which goes FIRST on the sim classpath.
# forge-ai/src and the shipped game are never changed. Delete SIM_ACTIVE.txt (or empty it) to run the sims on the stock AI.
ACTIVE="$ROOT/tools/concordia/ai_lab/patches/SIM_ACTIVE.txt"
if [ -s "$ACTIVE" ]; then
    PATCHES=$(grep -v '^#' "$ACTIVE" | grep -v '^$' | tr '\n' ' ')
    STAMP=$(cat "$ROOT"/tools/concordia/ai_lab/patches/*.patch 2>/dev/null >/dev/null; for p in $PATCHES; do cat "$ROOT/tools/concordia/ai_lab/patches/$p"; done | cksum | cut -d' ' -f1)
    if [ "$(cat "$CACHE/aipatch/stamp" 2>/dev/null)" != "$STAMP" ]; then
        log "compiling test-only AI patches: $PATCHES"
        rm -rf "$CACHE/aipatch"; mkdir -p "$CACHE/aipatch/src" "$CACHE/aipatch/classes"
        for p in $PATCHES; do
            for f in $(grep '^--- a/' "$ROOT/tools/concordia/ai_lab/patches/$p" | sed 's#^--- a/##'); do
                [ -f "$CACHE/aipatch/src/$f" ] || { mkdir -p "$CACHE/aipatch/src/$(dirname "$f")"; cp "$ROOT/$f" "$CACHE/aipatch/src/$f"; }
            done
            (cd "$CACHE/aipatch/src" && patch -p1 -s < "$ROOT/tools/concordia/ai_lab/patches/$p") || { log "patch $p failed"; exit 1; }
        done
        javac -nowarn -d "$CACHE/aipatch/classes" -cp "$CP" $(find "$CACHE/aipatch/src" -name '*.java') 2>&1 | grep -v "^Note:\|JAVA_TOOL_OPTIONS" >&2 || true
        echo "$STAMP" > "$CACHE/aipatch/stamp"
    fi
    CP="$CACHE/aipatch/classes:$CP"
fi

# the sim tools themselves
mkdir -p "$CACHE/classes"
SRC=$(ls "$ROOT"/tools/concordia/sim/*.java "$ROOT"/tools/concordia/balance_lab/*.java "$ROOT"/tools/concordia/ai_lab/*.java 2>/dev/null || true)
if [ -n "$SRC" ]; then
    javac -nowarn -d "$CACHE/classes" -cp "$CP" $SRC 2>&1 | grep -v "^Note:\|JAVA_TOOL_OPTIONS" >&2 || true
fi
echo "$CP:$CACHE/classes" > "$CACHE/cp.txt"
echo "$CACHE/cp.txt"

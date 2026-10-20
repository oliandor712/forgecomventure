#!/bin/bash
# Runs the real Forge game on a virtual screen (Xvfb + Mesa software OpenGL) and drives it with a step script,
# saving screenshots and a log. For testing Concordia changes without a person at the keyboard.
#
#   tools/concordia/gamerunner/run.sh <steps-file> [out-dir]
#   tools/concordia/gamerunner/run.sh tools/concordia/gamerunner/steps/temple.txt
#
# Steps (one per line, # comments): see GameRunner.java. Needs: a compiled reactor (mvn -pl forge-gui-mobile -am
# compile), Xvfb, xvfb-run and ImageMagick's import. LWJGL's Linux jars are downloaded once into ~/.cache.
# Booting takes a few minutes under software rendering.
# STATUS: work in progress, it has not yet reached the title screen (last blocker: libgdx natives, now added).
set -e
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
HERE="$ROOT/tools/concordia/gamerunner"
STEPS=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
OUT=${2:-$ROOT/target/gamerunner}
CACHE=${GAMERUNNER_CACHE:-$HOME/.cache/forge-gamerunner}
mkdir -p "$OUT/shots" "$CACHE/lib" "$CACHE/classes"

# LWJGL 3.3.3 for Linux and the libGDX desktop backend (not in the repo's Maven deps, which target Windows/Mac).
fetch() {  # group/artifact version [classifier]
    local path=$1 ver=$2 cls=${3:+-$3} name
    name=$(basename "$path")-$ver$cls.jar
    [ -s "$CACHE/lib/$name" ] && unzip -tq "$CACHE/lib/$name" >/dev/null 2>&1 && return
    for i in 1 2 3 4; do
        curl -sSL -o "$CACHE/lib/$name" "https://repo1.maven.org/maven2/$path/$ver/$name" || true
        unzip -tq "$CACHE/lib/$name" >/dev/null 2>&1 && return
        sleep $((i * 5))
    done
    echo "could not download $name" >&2; exit 1
}
for a in lwjgl lwjgl-glfw lwjgl-jemalloc lwjgl-openal lwjgl-opengl lwjgl-stb; do
    fetch org/lwjgl/$a 3.3.3; fetch org/lwjgl/$a 3.3.3 natives-linux
done
fetch com/badlogicgames/gdx/gdx-backend-lwjgl3 1.14.2

# Compile the reactor and take its classpath (offline; the TenPatch dependency is jitpack-only, so it is left out).
# Delete $CACHE/cp.txt to redo this after changing Java code; GAMERUNNER_NOBUILD=1 skips the compile check.
if [ -z "$GAMERUNNER_NOBUILD" ] || [ ! -s "$CACHE/cp.txt" ]; then
    rm -f "$CACHE/deps.txt"
    cp "$ROOT/forge-gui-mobile/pom.xml" "$CACHE/pom.backup"
    python3 - "$ROOT/forge-gui-mobile/pom.xml" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
open(p, 'w').write(re.sub(r'\s*<dependency>\s*<groupId>com\.github\.raeleus\.TenPatch</groupId>.*?</dependency>', '', s, count=1, flags=re.S))
PY
    (cd "$ROOT" && mvn -B -q -o -pl forge-gui-mobile -am compile dependency:build-classpath -Dcheckstyle.skip -Dmdep.outputFile="$CACHE/deps.txt") || true
    cp "$CACHE/pom.backup" "$ROOT/forge-gui-mobile/pom.xml"
    [ -s "$CACHE/deps.txt" ] || { echo "could not build the classpath (compile the reactor first: mvn -pl forge-gui-mobile -am compile)" >&2; exit 1; }
    echo "$ROOT/forge-gui-mobile/target/classes:$ROOT/forge-gui/target/classes:$ROOT/forge-ai/target/classes:$ROOT/forge-game/target/classes:$ROOT/forge-core/target/classes:$(cat "$CACHE/deps.txt")" > "$CACHE/cp.txt"
fi
# libGDX's own natives (libgdx64.so, freetype) come with the desktop launcher's deps, not forge-gui-mobile's.
NATIVES=$(ls "$HOME"/.m2/repository/com/badlogicgames/gdx/gdx-platform/*/gdx-platform-*-natives-desktop.jar \
    "$HOME"/.m2/repository/com/badlogicgames/gdx/gdx-freetype-platform/*/gdx-freetype-platform-*-natives-desktop.jar 2>/dev/null | tr '\n' ':')
CP="$NATIVES$(cat "$CACHE/cp.txt"):$(ls "$CACHE"/lib/*.jar | tr '\n' ':')"

javac -nowarn -cp "$CP" -d "$CACHE/classes" "$HERE"/GameRunner.java "$HERE"/GameLauncher.java \
    "$ROOT/forge-gui-mobile-dev/src/forge/app/Main.java" 2>&1 | grep -v "^Note\|JAVA_TOOL" || true

cd "$ROOT/forge-gui-mobile-dev"   # like the dev launcher: ../forge-gui/ is the assets folder, fallback_skin/ is here
mkdir -p "$HOME/.forge/adventure"
[ -s "$HOME/.forge/adventure/settings.json" ] || echo '{"plane":"Concordia"}' > "$HOME/.forge/adventure/settings.json"
timeout ${GAMERUNNER_TIMEOUT:-1500} xvfb-run -a -s "-screen 0 1280x720x24" \
    java -Xmx4g -Dshots="$OUT/shots" -cp "$CACHE/classes:$ROOT/forge-gui-mobile-dev:$CP" forge.app.GameRunner "$STEPS" 2>&1 | tee "$OUT/run.log" \
    | grep --line-buffered -E "^(STEP|==|SHOT|FAIL|DONE)|Exception" || true
rm -rf "$ROOT/forge-gui/data"   # user data the game writes next to res when run from the repo
echo "log: $OUT/run.log  shots: $OUT/shots"

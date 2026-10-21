#!/bin/bash
# Runs a sim class with the classpath from setup.sh (built on first use).
#   tools/concordia/sim/run.sh DeckSim forge-gui/ 2 150 deckA.dck 25 deckB.dck 25 label
# Paths in the arguments are relative to the repo root. Heap 3 GB; set SIM_HEAP to change it. SIM_JAVA_OPTS adds JVM options (for example -Dlogdir=DIR).
set -e
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
CPF=$("$ROOT/tools/concordia/sim/setup.sh")
cd "$ROOT"
CLS=$1; shift
exec java -Xmx${SIM_HEAP:-3g} -Djava.awt.headless=true $SIM_JAVA_OPTS -cp "$(cat "$CPF")" "$CLS" "$@"

STANDING INSTRUCTION (user, 2026-10-20): 30-card test games use 20 life, equal on both sides (not 40 or 15). Applies to all AI lab sims with shrunk decks.
STANDING INSTRUCTION (user, 2026-10-20): each hourly wake is time-boxed to about 5 minutes. Stop at a safe point, log where you are, commit and push; split long steps (builds, sims) across wakes; never leave java running (kill by pid, never pkill -f).

2026-10-20T14:07Z read required docs; picked flagged cards with existing AILogic for experiment 001 (EXPERIMENTS.md candidate list)
2026-10-20T14:07Z REPORTED (schedule changed to hourly steps, report every 4h)
2026-10-20T14:47Z paused at main session's request; nothing running
2026-10-20T14:57Z resumed (main session deck job done; 200 Concordia decks now available as opponents)
2026-10-20T15:12Z exp 001 prep: checked Turtleshell/Myr Quadropod/Aquamoeba scripts (all single Pump AILogic$ SwitchPT + stale RemoveDeck:All; PumpAi.java:54-60 only blocks a 2nd activation per turn). BLOCKER: this container has no ~/.m2 and no built jars, so DeckSim cannot run yet; next wake: test whether Maven Central is reachable through the proxy (mvn -q -pl forge-ai -am dependency:resolve), else ask the main session for a classpath
2026-10-20T15:16Z started tools/concordia/sim/setup.sh in background (output in scratchpad setup.out/setup.err); next wake: check it finished, git status shows forge-gui-mobile/pom.xml unchanged, then run baseline for exp 001
2026-10-20T15:30Z exp 001: setup.sh build OK; AiLabSim.java (plays log + -Dhand forcing), lab001_switchpt.dck added; random-draw baseline (8 games) never cast the 3 flagged cards (mostly undrawn); next: baseline then patched run with -Dhand forcing the 3 cards into the opening hand (run paused by user at 15:27)
2026-10-20T15:45Z exp 001 done: baseline 0 casts vs patched 7 casts/26 activations (30-card decks, 4 games each, equal life); patch 001 saved; next: exp 002 Fog/Evasion cards
2026-10-20T15:40Z recorded rule: 30-card games at 15 life each
2026-10-20T15:45Z rule changed: 30-card games at 20 life each (was 15)
2026-10-20T15:55Z exp 001 re-run at 20/20: baseline 0 casts vs patched 7 casts/30 activations; result confirmed

STANDING INSTRUCTION (user, 2026-10-20): each hourly wake is time-boxed to about 5 minutes. Stop at a safe point, log where you are, commit and push; split long steps (builds, sims) across wakes; never leave java running (kill by pid, never pkill -f).

2026-10-20T14:07Z read required docs; picked flagged cards with existing AILogic for experiment 001 (EXPERIMENTS.md candidate list)
2026-10-20T14:07Z REPORTED (schedule changed to hourly steps, report every 4h)
2026-10-20T14:47Z paused at main session's request; nothing running
2026-10-20T14:57Z resumed (main session deck job done; 200 Concordia decks now available as opponents)
2026-10-20T15:12Z exp 001 prep: checked Turtleshell/Myr Quadropod/Aquamoeba scripts (all single Pump AILogic$ SwitchPT + stale RemoveDeck:All; PumpAi.java:54-60 only blocks a 2nd activation per turn). BLOCKER: this container has no ~/.m2 and no built jars, so DeckSim cannot run yet; next wake: test whether Maven Central is reachable through the proxy (mvn -q -pl forge-ai -am dependency:resolve), else ask the main session for a classpath

STANDING INSTRUCTION (user, 2026-10-20): after every test, send results to the main session (session_01SmNeweiyRBavDSUetnsUjF via send_message) and request analysis of the AI decisions, logic and results by match phase and situation for the flagged cards. Use AiLabSim -Dlogdir=tools/concordia/ai_lab/results/<test> so it has phase-annotated logs.
STANDING INSTRUCTION (user, 2026-10-20): from the next test on, shrunk test decks are 40 cards (minideck.py --size 40) to limit decking; still 10 games per condition, equal life 20. Experiments 001-002 used 30 cards.
STANDING INSTRUCTION (user, 2026-10-20): each test runs 10 games per condition (was 4), 150 s cap per game, equal life 20 for 30-card decks.
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
2026-10-20T16:25Z exp 002 (Fog: Thwart the Enemy, Vine Snare) 10 games each at 20/20: baseline 0 casts vs patched 19 casts; patch 002 saved; next: check cast timing, test Endure/Harsh Justice/Shield Dancer
2026-10-20T16:30Z recorded rule: 40-card test decks from the next test on
2026-10-20T16:48Z exp 003 (white Fog, 40-card decks, 10 games): Endure 15 casts, Shield Dancer 11 casts/19 act, Harsh Justice 0 (never cast); patch 003 saved without Harsh Justice; next: read FogAi.canPlay for Harsh Justice, check cast timing
2026-10-20T16:50Z read pilot data (pilot/2026-10-20_exp001_mirror): next check for patch 001 = were Turtleshell/Quadropod activations in combat only (pilot rule: never switch outside combat; my runs saw up to 12 activations/game) [DISCARDED (user): pilot data deleted; the in-combat-only check stays as my own idea, not from the pilot]
2026-10-20T17:20Z STANDING (user): after every test, send results to the main session and ask it to analyse the AI's decisions/logic/results by match phase and situation for flagged cards. AiLabSim -Dlogdir writes per-game phase-annotated logs to ai_lab/results/. Sent for exp 001-003 + 003-timing.
2026-10-20T17:25Z read CONTEXT update: (1) pick next test cards by EDHREC rank (deckgen/scryfall/cards.json.gz via scryfall_bulk.load(); my exp 001 cards rank ~16k-21k, i.e. low impact); (2) ask main session for analysis with an 'ANALYSIS REQUEST:' line in the run report; read tools/agents/analysis/forge-ai-lab.md each run
2026-10-20T17:55Z re-ran 001-003 at natural density (1 copy, 40 cards, 10 games, logs): baseline 0 casts everywhere; patched casts all drawn cards; results in ai_lab/results/n00X-*; sent to main session
2026-10-20T18:05Z read main-session analysis; narrowed patch 003 to Endure, caveated patch 001; planned patch 004 (Harsh Justice ReflectCombatDamage) and 005 (SwitchPT guard); next: needs forge-ai scratch worktree + build (own wakes)
2026-10-20T18:40Z patch 005 (SwitchPT two-versions, user's idea) built+tested in scratch worktree: 92 -> 8 activations, all declare blockers; results in ai_lab/results/n001-{guard,twoversions}; sent to main
2026-10-20T17:20Z pre-approval for scratch tests read (CONTEXT rules 7-8); wrote patch 006 (Fog counts Effect fogs), untested; next: build+test 006, then 004/007 + per-activation logging
2026-10-20T17:50Z patch 005 v3 (shouldPumpCard + cost) built/tested: 2 activations/10 games; v2 backed up in tools/concordia/backups/2026-10-20_005-v2-patch; next: switch-heavy deck + extra log columns, then 006/004/007 tests

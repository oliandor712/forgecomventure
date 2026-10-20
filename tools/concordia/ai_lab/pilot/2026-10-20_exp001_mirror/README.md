# Piloted test match, experiment 001 cards (2026-10-20)

PilotSim (tools/concordia/sim/PilotSim.java): mirror match, both sides the 30-card lab001 deck (minideck.py from
decks/lab001_switchpt.dck), 20 life each, cards unpatched (stale AI:RemoveDeck flags kept). Forge AI played
everything except decisions on the flagged cards (Aquamoeba, Turtleshell Changeling, Myr Quadropod), which went to
the pilots: side A the main session, side B a forge-ai-lab subagent. The B subagent was stopped by the user partway
through game 2, after which B's flagged-card decisions fell back to Forge AI (marked in decisions.log). The user cut
the test to 2 games; game 2's last A decision timed out (Forge AI decided it).

| Game | Winner | Turns | Flagged-card plays (A / B) |
|---|---|---|---|
| 1 | A | 40 | A: Turtleshell cast, Aquamoeba cast. B: all three cast, Quadropod and Aquamoeba switched once each |
| 2 | B | 19 | A: all three cast, 4 switches (Turtleshell 1, Aquamoeba 3). B: Aquamoeba cast (on Forge AI fallback) |

Pilot takeaways for the AI: cast the creatures on curve (Forge AI offered "nothing" with Turtleshell castable and
mana open); switch only an unblocked attacker (+2/+3 damage) or a creature that dies anyway (Turtleshell triple-
blocked: switch to kill a blocker); never switch a single-blocked attacker into a trade that costs a card; never
switch outside combat. Files: decisions.log (each prompt, the pick and the reasoning), game_N.log (Forge's log).

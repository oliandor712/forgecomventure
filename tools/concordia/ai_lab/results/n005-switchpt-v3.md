# n005: patches 001 + 005 v3 (SwitchPT), 2026-10-22

Setup: AiLabSim, 40 games/arm, equal life 20, not seeded (AiLabSim has no seed). Deck `decks/s005_switchheavy_40.dck` (switch-heavy test deck, 3 copies per test card) vs `decks/opp_sai_40.dck`. Both arms use scratch assets with 001 applied (RemoveDeck flags removed from Aquamoeba, Turtleshell Changeling, Myr Quadropod) and the test overlay (instrumentation + 013). base = stock PumpAi; code = 005 v3 compiled on top (scratch classes first on the classpath).

| Arm | Wins A | Casts (both sides) | Activations (both sides) | A's activations by phase |
|---|---|---|---|---|
| base (001 only) | 5 | 131 | 356 | beginning of combat 91, declare blockers 87 (37 of 40 games) |
| code (001 + 005 v3) | 1 | 133 | 52 | declare blockers 26 only (14 of 40 games) |

Findings:
- 005 v3 cuts activations by 85% (356 -> 52) with the same casts; all remaining A activations are at declare blockers (the intended gate); the base arm switches at beginning of combat too (91), which is the pointless spam.
- Wins 5 vs 1 of 40 (deck A loses about 90% in both arms): p about 0.2, not significant at 40 games. Cannot say whether 005 hurts; base switching 178 times did not win more than 5 games either.
- Not measured: how many 005 activations changed a combat result (per-activation useful/not log from the handoff is still not built).
- Verdict: 005 v3 does what its header says; the effect on strength is unproven (needs a seeded A/B with the useful-activation log). 001 depends on 005 (without it the flag removal causes the spam).

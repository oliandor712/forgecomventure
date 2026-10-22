# n014: patch 014 test (BestOpportunity on 6 scry instants), 2026-10-22

Setup: AiLabSim, stock assets (base) vs scratch assets with 014 applied (patched). Deck A: 40-card UB minideck (from T2_UB_Atris), 2 copies each of Opt, Deliberate, Joint Exploration, Delightful Discovery, Demon's Due; opponent: 40-card UB minideck (T2_UB_The). Equal life 20, ai-test-instrumentation + 013 overlay on both arms. Not seeded (AiLabSim has no seed), so counts are indicative. 20 games/arm, then 40 games/arm (separate run).

| Run | Arm | Wins A | Test-card casts | Casts/game |
|---|---|---|---|---|
| 20 games | base | 2 | 95 | 4.8 |
| 20 games | patched | 1 | 76 | 3.8 |
| 40 games | base | 6 | 218 | 5.5 |
| 40 games | patched | 4 | 163 | 4.1 |

Cast phase, 20-game run: base: A's upkeep 46 (before the draw), opponent's turn 46 (upkeep 19, draw 11, main 10, combat 8, end step 1). Patched: opponent's end step 34, A's own turn after the draw 42 (main 25, combat 11, end step 6), none in upkeep.

Findings:
- 014 does what the tag says: casts move from upkeep/early opponent turn to the opponent's end step (45%) or the AI's own turn after the draw.
- Casts per game fall about 25% (5.5 -> 4.1 in 40 games): cards wait for the "nothing else to cast" condition or the end-step window. Whether that costs anything is unknown: win rates 6 vs 4 of 40 are noise (deck A is the weaker deck; B wins about 85-90%).
- Loses the "scry before draw at own upkeep" cast the stock AI does 46 times in 20 games. Not clearly worse (patched scry at the opponent's end step is also before the draw).
- Verdict: behaves as intended; effect on strength unmeasured. A cheaper reading: it is a timing change with ~25% fewer casts, so keep it unticked until a seeded test shows no loss.

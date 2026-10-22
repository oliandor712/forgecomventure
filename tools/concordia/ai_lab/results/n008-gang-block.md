# n008: patch 008 (shouldPumpCard counts gang-block co-blockers), 2026-10-22

Setup: AiLabSim, 40 games/arm, equal life 20, not seeded. A = `decks/g008_defender_40.dck` (green, Giant Growth, Titanic Growth, Blossoming Defense x2 each), B = `decks/g008_fatty_40.dck`. Stock assets. base = stock jars + test overlay; code = 008 compiled on top (scratch classes first on the classpath). Watched: the three pump instants (both sides).

| Arm | Wins A | Pump casts | avg turns |
|---|---|---|---|
| base | 30 | 90 | 20.6 |
| code (008) | 25 | 95 | 19.9 |

Findings:
- Casts +5% (90 -> 95): no sign of over-pumping from 008. Wins A 30 -> 25 of 40 (p about 0.3): not significant.
- The 008-specific path (a pump that only kills because co-blockers add damage) is still not isolated; earlier shadow runs found 0 disagreements in 37 blocker evaluations, so the path is rare in AI-vs-AI games. 008 has a wide blast radius (every shouldPumpCard user) for an effect nobody has observed.
- Verdict: no regression seen; no benefit seen. Leave unticked; do not propose until a scenario test (ScenarioSim, not built) shows the case.

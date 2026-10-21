# Options for the balancers (forge-ai-lab)

Each option has its measured effect, cost and what it needs. Nothing here is applied to decks or forge-ai without approval. Effects are from small samples (10 games per arm) unless stated; treat them as direction.

| # | Option | Measured effect | Cost | Needs |
|---|---|---|---|---|
| 1 | Land bonus for side a (balance data, not an AI change) | 75% win rate over 40 games vs 46% baseline (±13) | none to test; needs a 40-game check before any starter change | data only |
| 2 | Remove AI:RemoveDeck from SwitchPT cards (Aquamoeba, Turtleshell Changeling, Myr Quadropod) — patch 001 | 0 casts becomes 3–7 casts per 10 games | switch spam without 005 (68 activations in 10 games) | card script, and needs 005 first |
| 3 | Patch 005 v3: SwitchPT chooses one version per turn | switch activations 68 to 14 (s005), 92 to 2–8 (n001 variants), casts unchanged | forge-ai code (PumpAi.java) | forge-ai patch awaiting approval |
| 4 | Remove the flag from Thwart the Enemy and Vine Snare, and from Endure (patches 002 and 003) | Fog cast in the opponent's declare-blockers window; Endure cast when threatened | card script | card script, ready, awaiting approval |
| 5 | Patch 004: Harsh Justice reflection logic | Harsh Justice never cast even without its flag (window mismatch) | forge-ai logic change | forge-ai patch, planned, not written |
| 6 | Patch 008: gang-block co-blockers in shouldPumpCard | 0 changed decisions in 37 co-blocker cases | forge-ai code | no demonstrated effect; not recommended yet |
| 7 | Patch 006: FogAi counts Effect-based fogs | no measurable effect | forge-ai code | parked |

Notes for the balancers:
- Options 2, 3 and 4 are the AI-side changes with a measured decision effect. Option 1 is data only.
- The Commander phase-log digests (100 games, due at the threshold) will be used to check options 2–4 in 100-card decks once they are in.
- Win-rate claims for any option need about 40 games per arm (H28).

## Update, 100-game digest analysis (376 games, 2026-10-21)
| # | Option | Measured effect | Cost | Needs |
|---|---|---|---|---|
| 8 | Data only: starters and tier 5 decks sit above the field, tier 1-2 black decks below (balance records, see BALANCE_ANALYSIS.md) | not an AI change; a 40-game check is needed before any deck change | none | data only |
| 9 | AI decision log (patch 010, test overlay only) | makes AI_DECISION rows in the digests; results-unchanged check still open | none on the shipped game | test overlay only (SIM_ACTIVE.txt); forge-ai/src needs the user's chat approval |

Note: the 376-game digest shows the AI chump-blocks more as its life falls (5%, 15%, 35% of decisions by life band). This is the behaviour the balancers should expect when they test life-based pressure.

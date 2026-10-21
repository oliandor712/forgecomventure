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

## Final (research ended early, 2026-10-21)
Balance options measured so far, with game counts (10 games per arm unless stated; H28 needs about 40 per arm for win-rate claims):
- Option 1, land bonus: 75% win rate (40 games) and land+one-drop 77% (34 games) against 46% baseline. Needs the 40-game check before any starter change.
- Option 2 and 3, SwitchPT flag and patch 005 v3: 68 to 14 switch activations in s005 (10 games), 92 to 2 to 8 in n001 variants. Casts unchanged. Patch 005 needs the user's chat approval.
- Option 4, Fog and Endure flags (002, 003): Fog cast in the opponent's declare-blockers window; Endure cast when threatened (10-game runs). Card script, awaiting approval.
- Option 5, patch 004 (Harsh Justice): not written; Harsh Justice never cast even without its flag. Planned.
- Option 6, patch 008: 0 changed decisions in 37 co-blocker cases. Not recommended.
- Option 7, patch 006: no measurable effect. Parked.
- Option 8, balance data: starters and tier 5 above the field, tier 1-2 black decks below, from 3,442 Commander records (20 to 40 games per deck). Needs 40 games before any deck change.
- Option 9, patch 010 AI decision log: test overlay only, 3,094 digested games with AI_DECISION rows. Its results-unchanged check is not completed.

## Completion pass (3,146 digested games, 2026-10-21)
Ranked by how much evidence each option has and how cheap it is to test. Game counts are the ones stated above; no new sims.
1. Option 1, land bonus (40 and 34 games): strongest measured lead; needs the 40-game check before any change.
2. Option 8, balance data (3,442 Commander records): starters and tier 5 above the field, tier 1 and 2 black decks below; needs 40 games per deck.
3. Option 2 and 3, SwitchPT and patch 005 (10-game runs): switch decisions cut sharply; patch 005 needs approval.
4. Option 4, Fog and Endure flags (10-game runs): cast in the right window; card script, awaiting approval.
5. Option 9, patch 010 decision log (3,146 games with AI_DECISION rows in 2,670): test overlay only.
6. Option 5, patch 004 (Harsh Justice): planned, not written.
7. Options 6 and 7, patches 008 and 006: no measurable effect; not recommended.
Note for all options: the digests cannot yet split results by deck or colour, so deck-specific effects are not measured.

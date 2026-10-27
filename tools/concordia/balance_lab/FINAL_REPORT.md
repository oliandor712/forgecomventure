# Deck balance research: final report (partial, 2026-10-21)

The research ended early at the user's request. The numbers below come from `REPORT.md`, built by `make_report.py` from every `records*.csv` file. Nothing here was simulated after that. W and multicolour results are partial; treat them as a first look.

## 1. Method

- **Decks:** 410 in total: 400 AI encounter decks (tiers 1-5, with variants) and 10 player starters (5 colours × Normal and Alt).
- **Target:** 25 games per AI deck and 40 per starter (H28). Each game counts toward both decks.
- **Equal life:** every game has the same starting life on both sides (H23). No life bonuses (H24).
- **Bonuses tested:** small card bonuses only (H24, H30): land, onedrop, land+onedrop, arena, staff, plus single-game checks of legion, market, bedlam and hornet.
- **Starters:** split 50/50 between Normal and Alt (H27). Only tuned starter games count (from commit 5439eb01).
- **Seats:** alternated; the seat-one result is reported separately.
- **Phase logging:** added in the sim (patch 010, test overlay only). Digests of each game went to `ai_lab/digests/` (about 1 KB per game), and raw logs stayed out of the repo.

Games per record file (each file is one worker's output; all are merged by `make_report.py`):

| file | games |
|---|---|
| records.csv (main lab, first shards) | 1,024 |
| records_multitemp.csv | 2,972 |
| records_assist.csv | 1,880 |
| records_lab.csv | 536 |
| records_main.csv | 526 |
| records_main2.csv | 392 |
| records_ailab.csv | 204 |
| records_logs.csv | 40 |
| **total** | **7,574** |

Of these, 4,074 are inner-tier games. 3,994 of those are on the current decks; 80 are on older decks and are left out of the tier tables.

## 2. Coverage

Decks at the 25-game target, by shard. The shard counts are AI decks only.

| shard | decks at 25 | status |
|---|---|---|
| R | 58 of 58 | complete |
| U | 58 of 58 | complete |
| G | 53 of 58 | nearly complete |
| B | 42 of 58 | partial |
| W | 1 of 58 | **partial: mostly not run** |
| multicolour | 3 of 110 | **partial: mostly not run** |
| starters | 10 of 10 at 40 | complete |

Decks below 25 games, by tier and colour (mono colours only; multicolour is listed in the total):

| tier | W | B | G | R | U | multicolour | total below |
|---|---|---|---|---|---|---|---|
| 1 | 16 | 0 | 0 | 0 | 0 | 0 | 16 |
| 2 | 11 | 0 | 0 | 0 | 0 | 17 | 28 |
| 3 | 10 | 8 | 2 | 0 | 0 | 30 | 50 |
| 4 | 10 | 3 | 0 | 0 | 0 | 30 | 43 |
| 5 | 10 | 5 | 3 | 0 | 0 | 30 | 48 |
| **all** | **57** | **16** | **5** | **0** | **0** | **117** | **185** |

Of the 400 AI decks, 215 are at the 25-game target and 185 are below it (`QUEUE.toon`). The per-tier table above sums to the same 185.

**Plainly:** W results are partial (only one W deck has reached the target), and multicolour results are partial (3 of 110 decks). Any W or multicolour finding in this report rests on the decks that did get games.

## 3. Findings

### Win rate by tier (new decks, seat-one result)

| tier | inner games | seat-one win rate (90% interval) |
|---|---|---|
| 1 | 678 | 56% (53-59%) |
| 2 | 842 | 56% (53-59%) |
| 3 | 824 | 51% (48-54%) |
| 4 | 838 | 51% (48-54%) |
| 5 | 812 | 52% (49-55%) |

Seat advantage is small: 51-56% for the first player, which is inside the noise at tiers 3-5. Tiers 1-2 show a clearer first-player edge.

Win rates by colour are not informative in this report. Each game has one winner and one loser, so pooling all decks of one colour always gives 50%. Judge decks individually, as below.

### Strong and weak decks (interval clear of 50%, deck power from `power_scorer.py`)

Power values are from the current scale (EDHREC popularity added 2026-10-20). Strong results need the 25-game target before they count.

| tier | deck | games | win rate (90%) | power |
|---|---|---|---|---|
| 1 | T1_U_Quistis | 22 | 82% (65-92%) | 17.8 |
| 1 | T1_G_Dwynen | 14 | 79% (57-91%) | 17.5 |
| 1 | T1_B_Butch | 12 | 75% (51-90%) | 18.0 |
| 1 | T1_B_Skitter | 30 | 68% (53-80%) | 17.8 |
| 5 | T5_BR_Olivia | 12 | 75% (51-90%) | 40.1 |
| 5 | T5_R_Urabrask | 42 | 71% (59-81%) | 41.6 |
| 5 | T5_R_Glin | 46 | 70% (58-79%) | 41.3 |
| 5 | T5_G_Shigeki | 20 | 20% (9-38%) | 42.8 |
| 5 | T5_WB_Carmen | 10 | 20% (7-46%) | 43.5 |
| 5 | T5_WUG_Bumbleflower | 16 | 25% (12-45%) | 42.0 |
| 5 | T5_U_Hapatra | 28 | 29% (17-44%) | 44.0 |
| 5 | T5_R_Queen | 40 | 32% (22-45%) | 43.8 |

Two readings from this table:
- At tier 1, the strongest decks are at or near power 18, and tier 1 has no clear weak decks yet.
- At tier 5, several high-power decks are *weak* (power 42-44 with 20-32% win rates). Power alone does not predict wins at tier 5, which is the same finding the lab recorded earlier.

### Starters and the player target (H29)

Player (starter) win rate against the enemy decks of each stage, bonus sets only, tuned starters only. The user's targets are 70% for stage 1 (tiers 1-2) and 50% for stages 2-3.

| stage | target | games | PC win rate (90%) | gap to target |
|---|---|---|---|---|
| 1 (tiers 1-2) | 70% | 3,352 | 55% (54-57%) | -15 pts |
| 2 (tiers 3-4) | 50% | 0 | - | not measured |
| 3 (tier 5) | 50% | 0 | - | not measured |

Stage 1 sits 15 points under the 70% target. Stages 2 and 3 were never measured against starters in the bonus sets, so they have no result.

Starter results against enemy decks with and without a bonus (Normal and Alt together per colour):

| starter | without bonus (enemy win) | with bonus (enemy win) |
|---|---|---|
| W Normal | 24% | 52% |
| W Alt | 12% | 39% |
| U Normal | 73% | 85% |
| U Alt | 68% | 78% |
| B Normal | 30% | 50% |
| B Alt | 28% | 52% |
| G Normal | 27% | 55% |
| G Alt | 30% | 59% |
| R Normal | 21% | 52% |
| R Alt | 24% | 37% |

Blue starters are far stronger than the rest; white starters are the weakest. The enemy wins more often with any bonus, which is expected.

### Bonus results (enemy = side a; matched sets, equal life)

Each set is two games with the bonus and two without, same pairing and seats (H28: about 25 sets for a 25-point effect).

| bonus | sets | enemy win with | without | difference (90%) |
|---|---|---|---|---|
| land+onedrop | 173 | 75% | 35% | +40 pts (±6) |
| land | 174 | 66% | 30% | +36 pts (±6) |
| staff | 174 | 54% | 38% | +16 pts (±6) |
| onedrop | 174 | 50% | 34% | +15 pts (±6) |
| arena | 173 | 34% | 32% | +1 pts (±6) |
| hornet | 1 | 50% | 0% | not enough games |
| bedlam | 1 | 100% | 0% | not enough games |
| legion | 1 | 0% | 50% | not enough games |
| market | 1 | 0% | 0% | not enough games |

The land and land+onedrop bonuses are the clear leads: both swing 36-40 points on 170+ sets. Staff and onedrop are smaller (15-16 points). Arena does nothing measurable. The single-game bonuses (hornet, bedlam, legion, market) have no usable result.

## 4. Options to empower AI decks against player decks

Ranked by how much evidence each option has and how cheap it is to test. Sources: `tools/concordia/ai_lab/OPTIONS_FOR_BALANCERS.md` (AI lab) and the bonus table above. Nothing has been applied to decks or to forge-ai.

| rank | option | measured effect | cost | needs |
|---|---|---|---|---|
| 1 | Land bonus for the enemy (option 1) | 75% win over 40 games vs 46% baseline (±13) | none to test | a 40-game check before any starter change |
| 2 | Balance data: starters and tier 5 sit above the field; tier 1-2 black decks below (option 8) | not an AI change | none | 40 games per deck before any deck change |
| 3 | SwitchPT flag removal and patch 005 v3 (options 2 and 3) | switch activations 68 to 14 (10 games); casts unchanged | card script and forge-ai change (PumpAi.java) | user approval for patch 005 |
| 4 | Fog and Endure flag removal (option 4, patches 002 and 003) | cast in the right window (10-game runs) | card script | user approval |
| 5 | AI decision log (option 9, patch 010) | 3,094 games with AI_DECISION rows; results-unchanged check not done | none on the shipped game | test overlay only |
| 6 | Harsh Justice reflection logic (option 5, patch 004) | not written; never cast even without its flag | forge-ai logic change | planned, not written |
| 7 | Gang-block co-blockers (option 6, patch 008) | 0 changed decisions in 37 cases | forge-ai code | not recommended |
| 8 | FogAi counts Effect-based fogs (option 7, patch 006) | no measurable effect | forge-ai code | parked |

Notes:
- The land bonus is the strongest measured lead, but it is a balance lever, not an AI change. It needs the 40-game check before anyone changes a starter.
- The AI-side options (2-4) change how the AI uses its cards. They were tested only on 10-game runs.
- The digests cannot yet split results by deck or colour, so none of these effects is measured for a specific deck.

## 5. Limits and what to run next

**Limits**
- The research stopped early. 185 of 400 AI decks are below the 25-game target. All 10 starters reached 40 games.
- W and multicolour are mostly unrun. Their tier results are not reliable.
- Bonus effects rest on 173-174 sets for four bonuses. The single-game bonuses have no result.
- Stages 2 and 3 have no starter results against the 50% target.
- Power ratings changed on 2026-10-20 at 16:45 UTC. Power values from before that time are not comparable.
- Seat advantage (51-56%) is small; it is not corrected in the tables.

**What to run next, in order**
1. Finish W (57 decks below 25) and the multicolour shards. This is the largest gap.
2. Bring the 16 tier-1 W decks and the 27 tier-2 decks up to 25 games each.
3. Measure starters against stage 2 and stage 3 enemies, so the H29 targets can be checked at every stage.
4. Repeat the land bonus at 40 games per arm before any starter change.
5. Test the AI-side options on 40-game arms once the user approves patches 001-005.

**Not to do yet**
- No deck changes from these numbers. Each claim needs the 40-game check first.
- No forge-ai changes without the user's chat approval (`docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`).

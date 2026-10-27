# Concordia research master report (2026-10-21)

This document joins the two final reports of the deck balance lab and the Forge AI lab, compiled by the main session. The research ended early at the user's order, so coverage is partial and each section says where.

Sources:
- Deck balance lab: `tools/concordia/balance_lab/FINAL_REPORT.md` (and `REPORT.md`, `QUEUE.toon`, `records*.csv`).
- Forge AI lab: `tools/concordia/ai_lab/FINAL_REPORT.md` (and `DECISION_LOGIC.md`, `OPTIONS_FOR_BALANCERS.md`, `digests/`).
- Rules the work followed: `tools/agents/human_logic.toon`.

## 1. In one page

1. **Games played.** 7,574 recorded games across 410 decks (400 AI decks, 10 player starters), all at equal life and with no life bonuses. 3,146 of them were also logged phase by phase and digested for the AI study.
2. **Coverage.** 215 of 400 AI decks reached the 25-game target and all 10 starters reached 40. Red and blue are complete, green and black are nearly done, white and multicolour are mostly unrun (1 of 58 white decks, 3 of 110 multicolour decks). Any white or multicolour number is a first look.
3. **Player against enemies.** At stage 1 (tiers 1-2) the player's starters win 66% against plain enemy decks (no bonus) and about 44% when the enemy gets a bonus card. The user's target is 70%, so plain stage 1 is close and bonus games are well below it (section 3.3). Stages 2 and 3 were never measured against starters.
4. **Strongest lever found.** A free land (and a free land with a one-drop) for the enemy moves the result by 36 to 40 points across 173 or more matched sets. It is a balance lever, not an AI change, and it is the clearest way to empower an AI deck against a player deck.
5. **What the AI does.** It blocks more as its life falls (8% at 15 or more, 19% at 8 to 14, 39% under 8), casts expensive spells before cheap ones, kills the highest-valued creature, and picks an attack aggression level from the damage race. The logs cannot yet say why it chose, only what it did.
6. **AI fixes.** Patches 002 and 003 (unflag Fog and Endure cards) are ready for the user's approval; 005 (switch creatures) is close. Patch 010 (decision log) runs on the test classpath only and is not in the game.
7. **Not done.** Commander play, mulligans and logic by deck type or colour could not be studied because the logs lack that data (section 5). A results-unchanged check for patch 010 is still open.

## 2. Method (both labs)

| item | value |
|---|---|
| Decks | 410: tiers 1-5 AI decks with variants, plus 10 starters (5 colours, Normal and Alt) |
| Targets | 25 games per AI deck, 40 per starter (H28); claims about a win rate need about 40 games per arm |
| Fairness | equal life on both sides (H23); no life bonuses (H24); seats alternated |
| Bonuses tested | land, onedrop, land+onedrop, arena, staff (plus single-game checks of legion, market, bedlam, hornet) |
| Starters | split 50/50 between Normal and Alt (H27); only games on the tuned starters count |
| Games per worker | balance lab 1,560, multitemp 2,972, assist 1,880, main 918, AI lab 204, logs 40 |
| Phase logging | every game after 2026-10-21 03:00Z; digests only are kept (about 1 KB per game); 3,146 games digested |
| Patch 010 | log-only AI decision log, approved for testing only; runs from a scratch copy on the sim classpath, never in `forge-ai/src` |

## 3. Deck balance

### 3.1 Coverage

| shard | AI decks at 25 games | status |
|---|---|---|
| R | 58 of 58 | complete |
| U | 58 of 58 | complete |
| G | 53 of 58 | nearly complete |
| B | 42 of 58 | partial |
| W | 1 of 58 | mostly not run |
| multicolour | 3 of 110 | mostly not run |
| starters | 10 of 10 at 40 | complete |

185 AI decks are below target: 57 white, 16 black, 5 green and 117 multicolour (tier 1: 16, tier 2: 28, tier 3: 50, tier 4: 43, tier 5: 48).

### 3.2 Results by tier

First-player win rate on the current decks (90% intervals): tier 1 56% (53-59%) over 678 games, tier 2 56% (53-59%) over 842, tier 3 51% (48-54%) over 824, tier 4 51% (48-54%) over 838, tier 5 52% (49-55%) over 812. The seat edge is small and only clear at tiers 1-2. Win rates pooled by colour are always 50% (every game has one winner and one loser), so decks are judged one by one.

Decks clear of 50% (90% interval, power from `power_scorer.py`):

| tier | deck | games | win rate | power |
|---|---|---|---|---|
| 1 | T1_U_Quistis | 22 | 82% (65-92%) | 17.8 |
| 1 | T1_G_Dwynen | 14 | 79% (57-91%) | 17.5 |
| 1 | T1_B_Butch | 12 | 75% (51-90%) | 18.0 |
| 1 | T1_B_Skitter | 30 | 68% (53-80%) | 17.8 |
| 5 | T5_R_Urabrask | 42 | 71% (59-81%) | 41.6 |
| 5 | T5_R_Glin | 46 | 70% (58-79%) | 41.3 |
| 5 | T5_BR_Olivia | 12 | 75% (51-90%) | 40.1 |
| 5 | T5_G_Shigeki | 20 | 20% (9-38%) | 42.8 |
| 5 | T5_WB_Carmen | 10 | 20% (7-46%) | 43.5 |
| 5 | T5_WUG_Bumbleflower | 16 | 25% (12-45%) | 42.0 |
| 5 | T5_U_Hapatra | 28 | 29% (17-44%) | 44.0 |
| 5 | T5_R_Queen | 40 | 32% (22-45%) | 43.8 |

Two readings. At tier 1 the best decks sit at about power 18, with no clear weak ones. At tier 5, several of the highest-power decks (42-44) win only 20-32%, so power does not predict wins at that tier. Several of these rows are below 25 games; confirm before changing any deck.

### 3.3 Starters against the player target (H29)

The user's targets are a 70% player win rate at stage 1 and 50% at stages 2-3. The balance lab reported 55% (54-57%) for stage 1 over 3,352 games, but that figure mixes games with and without an enemy bonus. Averaging the lab's own starter table (ten starters, simple mean) separates the two cases:

| starter | enemy win without bonus | enemy win with bonus |
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

Averaged, the enemy wins about 34% without a bonus, so the player wins about 66%, only 4 points under the 70% target. With a bonus the enemy wins about 56%, so the player wins about 44%. Stage 1 is therefore near target against plain decks and below it when the enemy gets a bonus card.

**Correction to the balance lab's text.** Its report says blue starters are the strongest and white the weakest. The table says the opposite: the enemy beats the blue starters 68-73% of the time without a bonus, so blue is the weakest starter; white is the strongest (enemy 12-24%). This is the clearest balance problem found: the blue starters need work, and the red Alt starter (enemy 37% even with a bonus) is the strongest with a bonus. Stages 2 and 3 have no starter games at all.

### 3.4 Bonus results (matched sets, enemy win rate with and without)

| bonus | sets | with | without | difference |
|---|---|---|---|---|
| land+onedrop | 173 | 75% | 35% | +40 (±6) |
| land | 174 | 66% | 30% | +36 (±6) |
| staff | 174 | 54% | 38% | +16 (±6) |
| onedrop | 174 | 50% | 34% | +15 (±6) |
| arena | 173 | 34% | 32% | +1 (±6) |
| hornet, bedlam, legion, market | 1 each | - | - | not enough games |

A free land is the lead (36 to 40 points). Staff and one-drop are modest (15 to 16). The arena bonus does nothing measurable.

## 4. Forge AI behaviour

3,146 games were digested; 2,670 of them (84.9%) carry the decision rows from patch 010. The median game lasts 16 turns.

| area | how the AI behaves | evidence | meaning for deck building |
|---|---|---|---|
| Blocking | blocks more as its own life falls | 8% at 15+ life (14,026 decisions), 19% at 8-14 (12,842), 39% under 8 (15,803) | early pressure is absorbed late; keep your life high relative to the AI if you want damage through |
| Attacking | picks an aggression level 0-6 from the damage race and body count, then gates each creature on survival or trade | 61,203 level rows: ahead 20,084, even 21,937, behind 19,182 | more bodies and a life lead push it into trade-and-attack levels |
| Removal | targets the highest-valued creature, holds single-target removal for a better target | read from the code | removal in these decks hits the biggest threat; cheap removal waits |
| Spell order | highest mana cost first, creatures slightly ahead, flagged cards last | median cast turn 11 over 54,129 casts | a top-heavy curve casts late; a low curve gets cheap spells out first |
| Mana | taps lands with no other use first, keeps creature abilities available, X spells take all mana | read from the code only | no log shows which source paid |
| Combat tricks | cast in combat in 38% of games | 1,823 casts; most are declare-blockers; top: Invigorate 87, Mortal's Resolve 60, Aspect of Hydra 60, Tyvar's Stand 45, Might of Alara 42 | tricks do get used; their effect on results is not visible |
| Tokens | named in 11.9% of attack declarations | 2,451 of 20,549 | ETB triggers are not logged |

Sources are `AiBlockController.java`, `AiAttackController.java`, `DestroyAi.java`, `ComputerUtilCard.java`, `ComputerUtilAbility.java`, `ComputerUtilMana.java` and `AiController.java` (line references in the AI lab's report).

## 5. Gaps

| area | status | data missing |
|---|---|---|
| Commander play (cast timing, tax, ability use) | not done | command-zone moves and cast cost per commander cast in the phase log |
| Mulligans and opening hands | not done | opening-hand and mulligan lines |
| Logic by deck type and by colour | not done | a deck id on each digest row, joined to the balance records |
| Attack rate per aggression level | not measured | join attack declarations to the level rows |
| Stages 2 and 3 against starters | not measured | no starter games at those stages |
| White and multicolour decks | mostly unrun | about 174 decks below 25 games |
| Patch 010 results-unchanged check | open | 40 games per arm, stock classpath against patched |

## 6. AI changes and the approval list

| patch | what it does | status | recommendation |
|---|---|---|---|
| 001 | unflag the switch creatures | needs work | apply only after 005 |
| 002 | unflag the green Fogs | ready | approve |
| 003 | unflag Endure | ready | approve |
| 004 | Harsh Justice reflection logic | planned | write it; the card is never cast, even unflagged |
| 005 | switch cards: one version per turn (v3) | tested, close | approve after review; activations drop from 68 to 14 |
| 006 | Fog count includes Effect-based fogs | no effect | park |
| 007 | curses aimed at the attackers a card blocks | planned | after 004 |
| 008 | gang-block co-blockers | needs testing | not recommended (0 changed decisions in 37 cases) |
| 009 | do not over-pump | candidate | not written |
| 010 | log-only AI decision log | approved for testing only | keep test-only; run the unchanged check |

Nothing was applied to `forge-ai/src`. Ticking and applying remain the user's decision (`docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`).

## 7. Options to empower AI decks against player decks

| rank | option | evidence | cost | needs |
|---|---|---|---|---|
| 1 | enemy starts with a land, or a land and a one-drop | +36 to +40 points over 173+ sets; the AI lab's 40-game check shows 75% against 46% | none to test | a 40-game check before any starter change |
| 2 | rework the blue starters (weakest), keep red Alt and white as the reference | enemy beats blue starters 68-73% without a bonus | deck edits | 40-game checks on starters; user review |
| 3 | staff or one-drop as a smaller step | +15 to +16 points | none | 40-game check |
| 4 | patch 005 (and 001) for switch creatures | switch activations 68 to 14 | forge-ai code | approval |
| 5 | patches 002 and 003 (Fog, Endure) | cast in the right window | card scripts | approval |
| 6 | patch 004 (Harsh Justice) | never cast today | forge-ai logic | write and test |
| 7 | tune tier 5 by deck, not by power | high-power decks win 20-32% | deck edits | 25+ games per deck |

Every row needs more games than the labs ran before it should change a deck; the AI-side items were tested on 10-game arms only.

## 8. Limits

- The research stopped early: 185 AI decks below 25 games; white and multicolour mostly unrun.
- Seat edge (51-56%) is not corrected in the tables.
- Power values before 2026-10-20 16:45Z are not comparable with later ones.
- The phase log shows what happened, not why; the digests carry no deck id, no command-zone moves and no mulligan lines.
- Pairings are not balanced across decks, so a deck's rate partly reflects its opponents.
- The balance lab and the AI lab report different counts for the same tests in places (for example the AI-decision rows: 2,670 of 3,146 games in the AI lab's report, 3,094 in the balance lab's); this report uses the AI lab's.

## 9. What to run next

1. Finish white (57 decks) and multicolour (117 decks), then lift every deck to 25 games.
2. Measure starters against stage 2 and stage 3 enemies so the 50% targets can be checked.
3. Repeat the land bonus at 40 games per arm before any starter change.
4. Add a deck id, command-zone moves and mulligan lines to the phase log (one more log-only patch to the balance lab's writer), then redo the by-deck and by-colour AI study.
5. Run the patch 010 results-unchanged check; then decide on patches 002, 003 and 005.
6. Fix the open item in `make_report.py` (its queue heading still says 40 per deck; AI decks are 25).

## 10. Related analyses (same day, not part of the balance study)

- `docs/Adventure/Campaign/RANDOM_QUESTS_ANALYSIS.md`: how Forge builds "random" quests and a plan for Concordia.
- `docs/Adventure/Campaign/SHOP_GENERATION_ANALYSIS.md`: shop and booster generation, a weighted-spawn and rarity-modifier design, and town reputation.
- Open decision: one town reputation scale (suggested -20 to +50) for shops and quests.

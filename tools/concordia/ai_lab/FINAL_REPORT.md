# Forge AI research report (forge-ai-lab, 2026-10-21)

Scope: how the Forge AI decides blocks, attacks, removal, spell order and mana, what the simulations show about it, and which card or AI changes are worth making. Everything here is on `campaign-design`. Nothing was applied to forge-ai/src or the shipped game.

## 1. Method

**Data.** 3,146 games are digested from the phase logs of the balance lab, the main session and the temp agents, as of this report. Digest folders are one per worker per UTC hour. Each digest holds one row per AI decision (attack, block, no-block, cast, damage, zone move) with the turn, phase and both life totals, plus, in 2,670 of the 3,146 games (84.9%), the AI_DECISION rows from patch 010.

**Source of the digest counts.** Worker totals: balance lab 106, main 144, main2 64, assist 1,230, multitemp 1,562, logs 40. Only 20 games carry a tier in their label (Commander batches T2 and T5). The digests carry no deck identity, so results cannot yet be split by tier, archetype or colour (see section 3).

**Patch 010.** A log-only AI decision log, approved by the user for testing only. It runs on the sim classpath through `tools/concordia/sim/setup.sh` and `ai_lab/patches/SIM_ACTIVE.txt`. It is not applied to forge-ai/src. Its results-unchanged check (same decks, stock vs patched classpath) is not done, so the 2,670 games with AI rows are treated as the stock AI with that caveat.

**Sources read (forge-ai, file:line).**
- Blocking: `AiBlockController.java` 189, 371, 607, 643, 806, 1115-1200 (pass order and the life buffer `diff = life*2 - 5`, 1124).
- Attacking: `AiAttackController.java` 581 (`doAssault`), 811 (`declareAttackers`), 1155-1296 (aggression levels 0-6), 1517-1606 (`shouldAttack` gate).
- Removal: `DestroyAi.java` 40-241; `ComputerUtilCard.java` 585-605 (target value), 1226-1360 (`useRemovalNow`).
- Spell order: `ComputerUtilAbility.java` 244-355 (comparator), 458-475 (creature re-sort); `AiController.java` 1668 (`chooseSpellAbilityToPlayFromList`).
- Mana: `ComputerUtilMana.java` 293 (`chooseManaAbility`), 108-160 (source scoring and sort), 1640-1660 (final order), 1784 (`determineLeftoverMana`).

## 2. Findings by area

**Blocking (done).** The AI blocks more as its own life falls. This is the clearest rule in the logs.

| Blocker's life | Block rate | Decisions |
|---|---|---|
| 15 or more | 8% | 14,026 |
| 8 to 14 | 19% | 12,842 |
| under 8 | 39% | 15,803 |

Reading: chump blocks wait for life in danger (section 1 of DECISION_LOGIC.md), and the rule holds across the full sample. For deck building: a deck that deals damage early puts the AI into the high-block band sooner, so early pressure is absorbed by blockers; a deck that wants damage through should keep its life total high relative to the AI.

**Attacking (done by rule, partly by log).** The AI picks an aggression level 0 to 6 from the damage race (`ratioDiff`) and outnumbering (`outNumber`), then gates each creature on whether it would survive or trade (`shouldAttack`, 1517). The logs record the level input in 61,203 AI_ATTACK_LEVEL rows, split roughly evenly between ahead (20,084), even (21,937) and behind (19,182). The logs do not yet join each level to the attacks it produced, so the attack rate per level is not measured. For deck building: decks with more bodies and a life lead reach the all-out and trade levels, which is the AI's cue to attack into blockers.

**Removal (done by rule).** The AI targets the creature with the highest `evaluateCreature` score (ComputerUtilCard 585-605), prefers opponent permanents, and holds single-target removal unless a short list of interrupts or tempo thresholds (0.8) fires. For deck building: removal in these decks hits the biggest threat; cheap removal for small creatures is held for a better target.

**Spell order (done by rule).** The AI sorts by mana cost, highest first, with creatures +1, zero-cost spells first and flagged cards (AI:RemoveDeck) -10. Expensive spells are cast before cheap ones, and median cast turn is 11 across 54,129 casts. For deck building: a curve that is top-heavy gets cast late; a low curve gets its cheap spells out first.

**Mana (done by rule).** Lands with no other use are tapped first; creatures with abilities or combat use are kept untapped; X spells take all available mana. The open-mana estimate feeds the attack trade roll. No log line shows which source paid for a spell, so this is by reading the code only.

**Combat tricks (done from the digests).** 1,823 casts in combat steps, in 1,196 of 3,146 games (38.0%). Most are in declare-blockers steps. The most used tricks are Invigorate (87), Mortal's Resolve (60), Aspect of Hydra (60), Tyvar's Stand (45) and Might of Alara (42). The AI does cast tricks in combat; the logs cannot show whether a trick changed a result.

**ETB and tokens (partly done).** 11.9% of attack declarations (2,451 of 20,549) name a token, and 2,946 zone moves name a token. ETB triggers do not appear in the digest, so their effect cannot be read.

**Game shape.** Median 16 turns across 3,146 games. The AI finishes almost every game in these logs.

## 3. Not completed, and what is missing

| Area | Status | What is missing |
|---|---|---|
| Commander play (cast timing, tax, commander ability) | Not done | Command-zone moves and the cast cost per commander cast are not in the digest. Needed: ZONE rows for "from Command zone" and a cost field on CAST rows. |
| Mulligan and opening hands | Not done | No mulligan or opening-hand lines. Needed: the opening hand and each mulligan decision per game. |
| Logic by deck type (aggro, ramp, control, tokens, midrange) | Not done | Digest rows carry no deck id. Needed: a deck id on each digest row, then a join to the balance records. |
| Logic by colour (W, U, B, R, G) | Not done | Same as deck type. |

For the two tasks that can be done from the logs (commander and mulligan), the logger needs the same change as patch 010: one more log-only line type each. That is a patch for the balance lab's `BonusSim` writer, not for forge-ai.

## 4. AI flaws and recommended changes

**Patch status** (from `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`, not edited here):

| Patch | What it does | Status | Recommendation |
|---|---|---|---|
| 001 | Unflag the switch creatures (Aquamoeba, Turtleshell Changeling, Myr Quadropod) | Needs work | Apply only after 005 is approved. Without 005 the AI spends mana on switches (68 activations in 10 games). |
| 002 | Unflag the green Fogs (Thwart the Enemy, Vine Snare) | Ready | Approve. Fog is cast in the opponent's declare-blockers window. |
| 003 | Unflag Endure | Ready | Approve. Endure is cast when threatened. |
| 004 | Harsh Justice reflection logic | Planned | Write it. Harsh Justice is never cast, even unflagged, because its window does not overlap FogAi's. |
| 005 | Switch cards: choose one version per turn (v3) | Tested, close to ready | Approve after review. Switch activations fall from 68 to 14 (s005) and from 92 to 2 to 8 (n001 variants). |
| 006 | Fog count includes Effect-based fogs | Tested, no effect | Park. |
| 007 | Curses aimed only at attackers the card blocks (Shield Dancer) | Planned | Write it after 004. Shield Dancer's creature-only casts may be a targeting result. |
| 008 | Gang-block co-blockers in pump decisions | Written, needs testing | Do not approve yet. 0 changed decisions in 37 co-blocker cases. |
| 009 | Don't over-pump | Candidate | Not written. |
| 010 | Log-only AI decision log | Approved for testing only | Keep test-only. Results-unchanged check still open. |

**AI flaws found.** (a) Switch cards spend mana on activations without a clear gain, which patch 005 fixes. (b) Harsh Justice is uncastable because of a window mismatch, which patch 004 fixes. (c) Shield Dancer's targeting is not confirmed; patch 007 depends on that. (d) Chump blocks come late: at 15+ life the AI blocks only 8% of the time, which may be too passive for aggressive decks.

## 5. Options for the balancers (ranked, with game counts)

Ranked by strength of evidence and cost to act on. Win-rate claims need about 40 games per arm (H28); none of the rows below reaches that yet except the balance data.

| Rank | Option | Effect | Games | Cost | Needs |
|---|---|---|---|---|---|
| 1 | Land bonus for side a | 75% win rate, against 46% baseline | 40 (land) and 34 (land+one-drop) | none to test | 40-game check |
| 2 | Balance data: starters and tier 5 above the field, tier 1-2 black below | rates from 6% to 83% | 3,442 Commander records | none | 40 games per deck before any change |
| 3 | Patch 005 (switch, v3) | switch activations 68 to 14 | 10 per arm | forge-ai code | approval |
| 4 | Patch 002 and 003 (Fog, Endure flags) | cast in the right window | 10 per arm | card script | approval |
| 5 | Patch 010 (decision log, test) | AI_DECISION rows | 3,146 digested, 2,670 with rows | none on shipped game | results check |
| 6 | Patch 004 (Harsh Justice) | Harsh Justice cast | not measured | forge-ai logic | write and test |
| 7 | Patches 006 and 008 | no measurable effect | 37 and 10 | forge-ai code | not recommended |

## 6. Limits and what to run next

**Limits.**
- The phase log records what happened, not why. The AI's reason for each choice is inferred from the code, not read from the log. Patch 010 adds the reason fields, but only as a test overlay.
- The digests are shallow: no deck id, no command-zone moves, no mulligan lines, no ETB triggers.
- Sample sizes: 10 games per arm in the switch and Fog runs; 40 games per arm are needed for win-rate claims. Per-deck rates from the balance records carry about ±10 to ±25 points of noise.
- Pairings are not balanced: starters may meet weaker opponents, so a deck's rate partly reflects its opponents.
- The results-unchanged check for patch 010 is not done, so the overlay games are not yet proven to match the stock AI.

**What to run next.**
1. The results-unchanged check for patch 010: same decks, stock classpath vs patched, win-rate difference over 40 games per arm.
2. Add a deck id to each digest row, then rerun the by-deck and by-colour analysis.
3. Add command-zone moves and mulligan lines to the phase log (one log-only patch, like 010, for the balance lab's writer).
4. Join attack declarations to AI_ATTACK_LEVEL rows, so the attack rate per aggression level is measured.
5. Decide on patch 005 and patches 002 and 003 (ready), so the AI-side fixes can be tested in the balance lab.

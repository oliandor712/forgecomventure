# Forge AI decision logic (read-only notes)

Source: forge-ai/src/main/java/forge/ai/ (read only, no edits). Line numbers are from the checked-out branch and may drift.
Status: first slice (block phase). Attack, removal targeting, spell order, mana, commander, tricks, ETB/tokens and mulligan are still to do.

## 1. Blocking (AiBlockController.java)

Entry: `assignBlockersForCombat` (line 1013) -> `assignBlockers` (1115).

- Life buffer: `diff = life*2 - 5` (1124). This is the minimum gain the AI wants before an unnecessary trade. With PLAY_AGGRO set and diff > 0, diff is reset to 0 (1125-1127).
- Order of passes (1148-1200):
  1. `makeGoodBlocks` (189): blocks where the blocker survives and kills, or survives alone.
  2. `makeGangBlocks` (371) and later `makeGangNonLethalBlocks` (558): several blockers on one attacker.
  3. If no Fog effect is held (`ComputerUtil.hasAFogEffect`, 1152): `lifeInDanger` is computed, then `makeTradeBlocks` (607). If life is still in danger, `makeChumpBlocks` (643). `reinforceBlockersAgainstTrample` (748) runs only while life stays in danger; `reinforceBlockersToKill` (806) runs only when not in danger.
  4. `removeUnpayableBlocks` (1430) drops blocks the AI cannot pay for.
  5. If life is still in danger, the whole assignment is cleared (`clearBlockers`) and rebuilt in a safer order: trade, good, chump, trample reinforce, gang, reinforce-to-kill (1181-1194).
  6. If life is in serious danger (`lifeInSeriousDanger`, 1199), it clears again and chump-blocks first.
- Chump blocks are used only when `lifeInDanger`. Multi-chump (718) handles several attackers.
- Wouldn't-be-destroyed checks come from ComputerUtilCombat (attackerWouldBeDestroyed / blockerWouldBeDestroyed), which the gang-block code in patch 008 relies on.
- Random trades: `wouldLikeToRandomlyTrade` (1341) allows some even trades based on the AI profile.
- Ordering: `sortPotentialAttackers` (130) decides which attacker is blocked first; `orderBlockers` (1248) and `orderBlocker` (1275) decide damage order among several blockers.

What this means for the deck types (provisional):
- Aggro: the AI blocks less when it is ahead on life (the diff buffer) and its good-block pass runs first. Aggro decks benefit from a small life lead; AI chump blocks come late.
- Control and midrange: fog and trade passes decide most of the game, so the Fog check at 1152 matters. A held Fog changes block choice.
- Tokens: gang blocks (371) and reinforce-to-kill (806) are the main answer to wide boards. Little is known yet about how the AI treats many 1/1 attackers.
- Ramp: chump blocks come up only under danger, so big creatures tend to get through until life is low.

Flagged cards (AI:RemoveDeck) relevant here: Fog effects (Thwart the Enemy, Vine Snare, Endure) are read by the AI only when `hasAFogEffect` returns true, so their flag decides whether the AI ever holds them. See AI_TAGS_REFERENCE.md section 5.

## Open items
- Attack logic: done (section 2).
- Removal targeting, spell order, mana, commander, tricks, ETB/tokens, mulligan: not yet read.
- "Logic by deck type" archetype categories are provisional until tools/concordia/balance_lab/README.md publishes its tags.

## 2. Attacking (AiAttackController.java)

Entry: `declareAttackers` (811). It runs under an AI timeout tracker (`AITimeoutTracker`, 812-820), so a slow plan is cut short rather than hanging the game.

- Assault check first: `doAssault` (581). Returns false if the AI cannot win. Beastmaster Ascension has a special threshold (586-595). A Fog on the opponent's side is considered (600+).
- Aggression level 0-6 is picked from a comparison of forces and damage ratios (1155-1296):
  - `ratioDiff = aiLifeToPlayerDamageRatio - humanLifeToDamageRatio` (1171). Higher is better for the AI.
  - `outNumber = computerForces - humanForces` (1162).
  - Level 5 (all out) when attrition is decisive: `ratioDiff > 0 && doAttritionalAttack` (1263). Attrition needs the human at zero life or near it (1207).
  - Level 4 (trade or damage) when `ratioDiff >= 1` with more than one attacker and either the human dies in under 2 hits or the AI is ahead on numbers (1265). Also a chance roll (`CHANCE_TO_ATTACK_INTO_TRADE`) when the AI is ahead on creature count and life, and the AI has open mana to bluff or trick (1271-1282).
  - Level 3 when `ratioDiff >= 0` with more than one attacker (1283).
  - Level 2 when the forces are about even, or the AI's damage ratio is above 1 (1285).
  - Level 1 (unblockable only) with `doUnblockableAttack` (1292).
  - Level 0 otherwise (1296).
- Per-creature gate: `shouldAttack` (1517) reads the aggression level and checks the creature against `SpellAbilityFactors` (1397-1516): canBeKilled, canKillAll, canBeBlocked, dangerousBlockersPresent, canKillAllDangerous, hasAttackEffect, hasCombatEffect, canTrampleOverDefenders, isWorthLessThanAllKillers.
  - Level 6 (exalted): attack only when the creature kills all possible blockers and is worth less than all of them, or cannot be blocked (1564-1570).
  - Level 5: attack with everything (1571).
  - Level 4: attack when it kills all blockers, or it can't be blocked, or has 0 power (1575-1581).
  - Level 3: attack when it kills all blockers of equal or greater value, or has a dangerous blocker it can kill, or an attack or combat effect, and cannot be killed by one blocker (1583-1590).
  - Level 2: attack to attract a group block or to kill a single blocker and survive (1592-1598).
  - Level 1: attack only when unblockable, or only one possible blocker and it can kill it without dying (1600-1606).
- `NonCombatPriority` SVar (1518-1530): a creature with an untapped ability the AI can pay for stays home unless power times priority is at least the smallest opposing life total.

What this means for deck types (provisional):
- Aggro: the all-out and trade levels (5 and 4) matter most. The AI attacks into trades when it has more creatures and more life, so an aggro deck with more bodies and a life lead gets its attacks through.
- Control: levels 0-2 dominate. The AI holds back creatures that would die to a blocker and attacks only for safe damage, so control decks see few attacks until they lose the board.
- Tokens: wide boards push `outNumber` up and reach level 2-3 quickly. Tokens with no value tend to pass the "worth less than all killers" test, so they attack early.
- Ramp and midrange: `NonCombatPriority` creatures (utility creatures with tap abilities) often stay home. Their abilities are only used if the AI can pay.

Flagged cards (AI:RemoveDeck) relevant here: no flagged card changes the attack level directly. Card-specific attack effects (`hasAttackEffect`) do count as "attack effect" for levels 2-3, so flagged cards with attack triggers are judged more kindly once they can be cast.


## 3. Removal targeting (DestroyAi.java, ComputerUtilCard.java)

Target choice, DestroyAi (rules run in order):
- Candidate list: `CardLists.getTargetableCards` on the battlefield (40), then indestructible and regeneration or shield checks are filtered out (155-190). Opponent's permanents are preferred (151, 343).
- If every candidate is a creature: `prioritizeCreaturesWorthRemovingNow` (157), then the best by `getBestRemovalTargetAI` (219).
- If every candidate is a land: `getBestLandToRemoveAI` (227), with the Strip Mine style logic (`doLandForLandRemovalLogic`, 427).
- Otherwise: `getBestRemovalTargetAI` (237).
- For `OppDestroyYours` logic: if the AI's own best creature is within 40 points of the target, the AI does not cast the removal (221-223).

Value per target, `evaluateRemovalTargetPriority` (ComputerUtilCard.java:585-605):
- Creature: `evaluateCreature` (the same score used for blocks and attacks).
- Land: `evaluateLandRemovalPriority`.
- Other permanents: 50 + 30 x mana value. Planeswalkers add 10 per loyalty counter.
- Tokens: +30 (gone for good).
- Opponent-controlled: plus `evaluateBoardPosition / 4`.

Hold or cast, `useRemovalNow` (ComputerUtilCard.java:1226-1360), only for single-target removal spells:
- Always true for abilities that are not spells (1234).
- Cast in main phase 1 if the spell helps a spell cast that turn (1239).
- Interrupt 1: removing a possible blocker lets the AI attack with more creatures (1247-1262).
- Interrupt 2: in the declare-blockers step, removing a blocker saves an attacker that would die (1266-1285).
- Interrupt 3: enchanted target with no AI enchantment on it counts as two-for-one (1287-1297).
- Interrupt 4: the opponent is casting a pump on this same target (1300-1307).
- Burn: `valueBurn` (toughness / damage, squared) at 0.8 or more casts now before combat end (1316-1323).
- Tempo: `valueTempo` = max(0.1 x target CMC / removal CMC, burn). Doubled for equipped targets, sorcery-speed spells, targets that cannot be destroyed, persist/undying/modular. Halved for bounce of non-tokens. Land targets get extra value. At 0.8 or more casts now before combat end (1331-1352).
- Threat: a creature's `evaluateCreature / 100` plus damage it would do if unblocked, divided by the AI's life. Reduced to 10% during the AI's combat, which means the threat check mostly matters on the opponent's turn.

What this means for deck types (provisional):
- Control: the 0.8 tempo and threat thresholds mean removal is held for the best target. Control decks with many removal spells will be slower to use them on small creatures.
- Aggro: the AI uses removal early on blockers (interrupt 1), which helps aggro decks that want to swing.
- Tokens: token targets get +30 value, so the AI aims removal at the tokens' best member when it has to choose.

Flagged cards (AI:RemoveDeck): a flagged removal card never reaches this path because the play ban applies first. Unflagging a removal card puts it through the rules above, so its value depends on the target scores here, not on the card script.

## 4. Spell order (ComputerUtilAbility.java, AiController.java)

Entry: `chooseSpellAbilityToPlayFromList` (AiController.java:1668) sorts the candidate list, then takes the first one that its API logic accepts. Candidates come from `getSpellAbilityToPlay` (1596), which first handles responses to the stack (`topOwnedByAI`, `mustRespond`, 1600-1625).

Sort, in `saComparator.compareEvaluator` (ComputerUtilAbility.java:244-355), higher score first:
- Base score: total mana cost (CMC of the pay costs).
- Deprioritised: `AIActivateLast` (first check), planar die rolls marked low priority, pump spells whose only cost is energy (last, by energy amount).
- Promoted: zero-CMC abilities before costed ones (except mana abilities), and `FreeSpellAI` cards first.
- Same-card ties: a cheaper spectacle cost is preferred.
- Priority added to the score by `getSpellAbilityPriority` (lines 330-355 onward):
  - Creatures +1 (creature spells before spells).
  - Flagged cards (`isCardRemAIDeck`) -10. This is the play-ban flag, so flagged cards sort last even when they are cast.
  - `AIPriorityModifier` SVar: added directly.
  - `EndOfTurnLeavePlay` on a card in play +1 (use before it goes).
  - Cards in hand when the hand is over the maximum size: +1 per card over the limit, so the AI casts cards before it has to discard.
  - Equipment with no creatures on the battlefield -9.
- Creature spells are then re-sorted among themselves by `EvaluateCreatureSpellComparator` (`sortCreatureSpells`, ComputerUtilAbility.java:458-475). The comparator uses `evaluateCreature` and is skipped when there are fewer than two creature spells.

What this means for deck types (provisional):
- Ramp and midrange: the highest-cost spell goes first, so the AI taps out for its biggest threat when it can. Cheap interaction waits.
- Control: cheap instants come after expensive sorceries in the same turn, so the AI can end up holding removal for the wrong turn. Watch for this in the logs.
- Aggro: zero-CMC and cheap creatures sort early and get cast before the AI has mana for its bigger threats.
- Tokens: token makers cost little and sort late unless they are creatures, which then drop to the creature re-sort.

Flagged cards (AI:RemoveDeck): a flagged card is pushed down by -10 in this sort. Removing the flag restores its normal place in the order, so once a card is castable, it is cast at its CMC rank, not last.

Open: the response path (`topOwnedByAI`, `mustRespond`, 1600-1625) is only sketched here.

## 5. Mana use (ComputerUtilMana.java)

Paying a cost: `chooseManaAbility` (ComputerUtilMana.java:293) picks the next mana source for a shard. Before the default order, it applies source preferences:
- `AIPreference ManaFrom$` or `AIManaPref`: Snow sources first; Treasure spent one at a time (`Treasure`) or freely (`TreasureMax`); `NotSameCard` removes sources with the same name as the spell (318-344).
- It skips the spell's own host as a source (~352), and any creature already paying a tap cost this turn (memory set `PAYS_TAP_COST`, ~355).
- Pump instants and sorceries do not tap a creature that is their target (Servant of the Conduit case, ~380).
- Animate: the AI does not tap the enchanted card for its own aura, and a manland animated this turn is not tapped again (~365-375).
- Attach: `AvoidPayingWithAttachTarget` stops the AI paying with the land it is attaching to, when another copy is untapped (~390-396).
- Cavern of Souls: for generic costs, pays with the coloured ability when a creature type matches, so the spell stays uncounterable (~400-415).

Order of sources, `getManaSourcesToPayCost` and `sortManaAbilities` (133-160):
- Each source card gets a score (`scoreManaProducingCard`, ~108-130), lower is tapped first:
  - Its mana abilities' own score.
  - +13 for each non-mana activated ability that is possible.
  - +13 if it can attack, +13 if it can block.
- So lands with no other use are tapped first, and creatures with abilities or combat use are kept untapped.
- Shards are paid in order of fewest sources first (line 1250).
- Final order (~1640-1660): colourless sources, then sources by number of mana they make (1 to 5), then any-colour sources, then other sources with the best creature last (sorted by `evaluateCreature`, reversed), then "use last" sources such as sacrifice outlets.

Spending for X and budget checks:
- `determineLeftoverMana` (ComputerUtilMana.java:1784) increases X one at a time until the cost is no longer payable, capped by `XMax` or `AIXMax`. The AI uses all available mana for X spells.
- `getAvailableManaEstimate` (1458-1461) is the number the attack and fog logic read for "open mana". It is used in the attack trade roll (AiAttackController 1271-1282) and in FogAi's mana reservation (FogAi.java:105-133).

What this means for deck types (provisional):
- Ramp: many mana sources; the AI keeps creatures with abilities untapped and taps lands first, so it can often cast a big spell and still hold blockers.
- Control: holding open mana matters for bluffs and tricks. The attack logic counts open mana, so a control deck with lands untapped looks less exposed, and the AI attacks less into it.
- Aggro: low open mana, so the AI attacks more freely on turns when it is tapped out (the trade roll allows this).

Flagged cards (AI:RemoveDeck) relevant here: none change mana use. A flagged mana source is still used normally if it is in play. Fog counting is separate from this estimate: `FogAi.countAvailableFogs` counts only real Fog API spells, so an Effect-based Fog is not counted (patch 006 would change that).

Still open: the `checkCosts` path (`canPayShardWithSpellAbility`) and reserved-card handling.

## Log check of blocking (results/, s005 and related runs, 2026-10-21)
Source: phase TSVs in tools/concordia/ai_lab/results/*/*.tsv. Each declare-blockers step with attackers was counted by the defender's life at that moment (life from LIFE lines).
- Defender life 15 or more: blocked in 32 of 71 steps (45%).
- Defender life 8 to 14: blocked in 21 of 33 steps (64%).
- Defender life under 8: blocked in 16 of 21 steps (76%).
Reading: blocks rise as life falls, which fits the rule that chump blocks wait for life in danger (section 1). Blocks at high life are still common, so good blocks and trades are doing much of the work, not only chumps. Caveats: board sizes differ between steps and the counts are small; this is direction, not a fitted rate.

## Full log pass (results/, 230 phase logs, 2026-10-21)
Scope: every TSV under tools/concordia/ai_lab/results/, including shadow runs. Mixed experiments and deck versions, so the numbers describe the logs as a whole, not one arm.

Casting:
- 547 spell casts with a turn number. Median cast turn 11. Early (turns 1-4) 20, mid (5-8) 139, late (9+) 388. The logs are slow-starting: most casts come after turn 8.
- Flagged cards (AI:RemoveDeck) cast by the lab deck (side A), median turn of cast (range):
  - Aquamoeba: 56 casts, median 6 (3-21)
  - Turtleshell Changeling: 55, median 12 (7-33)
  - Myr Quadropod: 50, median 10 (7-40)
  - Vine Snare: 25, median 14 (8-27)
  - Thwart the Enemy: 18, median 16 (12-26)
  - Endure: 2, median 25 (21-29)
  These are the flagged cards that reach the stack at all, so the flag removal experiments show them cast after the flag is gone.

Combat:
- Attack declarations by side A: 150 steps, mean 1.7 attackers. By side B: 182 steps, mean 4.6 attackers. The gap is mostly the deck build (B's boards are wider), not an AI choice; a board-matched test is needed before reading attack restraint from it.
- Combat damage events: 71 in turns 5-8 and 629 in turns 9 and later. Games are decided late; early combat is rare.

Reading against the logic notes:
- Attack levels (section 2) and blocks (section 1, log check) are consistent with the logs: blocks rise as life falls, and attackers are few while the board is small.
- Spell timing (section 4) is consistent with the late casting. Expensive spells are cast late in these decks, so the high-CMC-first rule rarely fires early.
- Nothing in the full pass contradicts the mana rules (section 5), but it does not test them either; no log line shows which source paid for a spell.

Caveats: counts come from different experiments, decks and life totals; the phase logs do not record AI scores, so "why" is inferred from the code, not read from the logs. Treat this as a survey to target the next experiments, not as evidence for a rule change.

## Decision-level results by experiment arm (2026-10-21)
Source: summary.txt and *-summary.txt in tools/concordia/ai_lab/results/. Ten games per arm, so win counts are not evidence on their own (H28 needs about 40); the decision counts are what this section reads. "Activations" are card activations, which for SwitchPT cards (Aquamoeba, Turtleshell Changeling, Myr Quadropod) are the switch decisions.

Switch decisions (SwitchPT, patch 001 and 005 family):
- n001 patched, before the v3 switch rule: 92 activations in 10 games.
- n001 variants with v3-era logic: n001-v3 2 activations, n001-guard 4, n001-twoversions 8. Casts stayed at 5-8 per card.
- s005 base 68 activations, s005 code (v3) 14: the same reduction seen in the earlier pilot.
Reading: the v3 switch rule removes most switch activations (about 92 to 2-8 in n001, 68 to 14 in s005) while keeping the casts. Decision count supports the v3 logic; it does not show that switching helps play.

Win counts (10 games per arm, not evidence on their own):
- n001 (switch deck): the A side wins 0 to 1 of 10 in every arm, so this deck is losing regardless of switch logic. Its games are long (21 to 29 turns), so the switch rule is not what decides them.
- Fog and flag arms (g008, r008, s006, n003): A wins between 2 and 9 of 10, with no consistent direction across patched and base. Treat as noise.

Shadow test (008, gang-block co-blockers): 406 blocker-branch evaluations, 37 with co-blockers present, 0 disagreements between base and 008. This is the same result as before: patch 008 does not change any decision in these logs.

Whitefog run (003, patched only): Endure 0 casts, Shield Dancer 5 casts (creature only, postcombat), Harsh Justice 0 casts. Harsh Justice is not cast even without its flag, which matches the window problem noted earlier: its window does not overlap FogAi's declare-blockers window (patch 004 needed).

Open decision-logic questions from these arms: why the switch deck loses even with fewer switches; whether Shield Dancer's creature-only casts are the AI's choice or a targeting result (EffectAi.java:136-140).

## Decision-logic read of the 100-card Commander sims (2026-10-21)
Source: tools/concordia/balance_lab/records*.csv (7 files, 3,442 games, all 100-card Commander decks: starters and tiers), archetype tags from QUEUE.toon. These records hold outcomes only (winner, first player, turns, timeouts). They contain no decisions, so everything below is an inference about AI decision logic, not a reading of it.

Outcomes by archetype (side-level, 2,614 decided no-bonus games; play order compensated):
- starter: 65.7% balanced, n=811, median 14 turns.
- ramp: 50.6%, n=1,527, median 18 turns.
- tokens: 46.3%, n=586, median 15.5 turns.
- midrange: 45.6%, n=1,446, median 15 turns.
- aggro: 44.1%, n=832, median 13 turns.
- control: 42.3%, n=26 (too few to read), median 19.5 turns.
- Timeouts 6, draws 7 across all rows: the AI finishes games.

Decision-logic reads (hypotheses to test, not findings):
- Aggro is the shortest archetype (13 turns) and wins below 50%. Section 2 says the AI attacks more freely with more creatures and more life. If aggro is losing short games, the likely places to look are blocking (section 1: the AI blocks freely at high life, so early pressure gets absorbed by trades) and removal targeting (section 3: removal aims at the best creature, not the most damaging one).
- Ramp runs longest among the big archetypes (18 turns) at 50.6%. Section 5 says the AI taps its own creatures last and keeps blockers back, so ramp boards may stall rather than lose. Long games with no timeouts suggest the AI is passive, not stuck.
- Starters are the outlier at 65.7%. Their 14-turn games may reflect the AI playing its own deck well in a matchup it can read, or weaker opponents (pairing mix, same caveat as the balance analysis).

What the records cannot show: which attacks, blocks, casts or removal targets produced these results. Testing any of the reads above needs phase logs for a sample of these games (for example a DeckSim run with -Dlogdir on an aggro vs ramp pairing), then the same decision counts as the results analysis.

## Phase logs from the Commander batch (balance_logs/logs-20261021T053135Z, 20 games, 2026-10-21)
Source: tools/concordia/ai_lab/results/balance_logs/logs-20261021T053135Z/ (per-game TSV plus INDEX.tsv), sent by the main session. Two pairings, 10 games each:
- AGGRO-RAMP label: T5 Baral (A) vs T5 Sephara (B). Both decks are tier 5, so the label does not match the pairing; treat it as tier 5 vs tier 5.
- STARTER-MID: B_Starter_Alt (A) vs T2 Eutropia, a midrange deck (B).

Blocking, per blocker decision (one row per attacker the blocker faces), by the blocker's own life at that moment:
- Life 15 or more: 13 of 181 blocked (7%).
- Life 8 to 14: 14 of 93 blocked (15%).
- Life under 8: 29 of 84 blocked (35%).
Reading: this matches section 1. Chump blocks rise as the blocker's life falls. Note the unit: this is per attacker, and the earlier log check (s005 set) was per step, so the two rates are not comparable as numbers, only as direction.

Attacks: AGGRO-RAMP side A declared 41 attack steps (mean 2.7 attackers), side B 55 (mean 1.9). STARTER-MID: starter 52 steps (mean 1.9), midrange 25 (mean 1.6).

Blocks by side: in STARTER-MID, the midrange blocker blocked 19 times and the starter 4 times. The midrange AI blocks much more than the starter AI in the same games. Possible causes, not yet checked: the starter's board is smaller (fewer blockers to commit), or midrange's trade logic (section 1, makeTradeBlocks) fires more often.

Casts: median cast turn 13 in tier 5 vs tier 5, 10 in starter vs midrange; both sides cast about equally in each pairing.

Caveats: 20 games in total, so these are direction only. The AGGRO-RAMP label is wrong (both sides are tier 5). Per-game TSVs show the decision inputs (attackers, blockers, life), but not AI scores, so the reasons behind each block are still inferred from the code.

## 100-game analysis (digest threshold passed; 376 games, 28 folders, 2026-10-21)
Source: tools/concordia/ai_lab/digests/ (games.tsv and decisions.tsv.gz from phase_digest.py). Games come from all decks and tiers; these are not the aggro/ramp pairings alone.

Blocking (per blocker decision, by the blocker's own life):
- Life 15 or more: block rate 5% (1,546 decisions).
- Life 8 to 14: 15% (1,576).
- Life under 8: 35% (1,676).
Reading: the same direction as section 1 and the earlier logs. Chump blocks rise as life falls. The gradient is steeper here than in the 20-game set (7% / 15% / 35%), so the broader sample supports the rule more strongly.

Game shape:
- Median 15 turns, mean 16.2. Per game: 8.5 casts for side A and 8.3 for side B; attacks 3.2 and 3.1; blocks 1.3 and 1.1.
- Casts: median turn 10 across 6,312 casts. Spell timing is still concentrated after turn 8, as in the earlier logs.

AI_DECISION rows (patch 010): none in these digests. The folders were digested before the patch was on the sim classpath. The first AI_DECISION rows will come from the next batches.

Caveats: the blocking rates are per decision, so one attacker counts once per blocker decision; the life bucket uses the blocker's life at the time of the block. This is a survey across all matchups, not a per-deck result.

## 100-game analysis, second pass (2,824 games, 37 folders, 2026-10-21)
Source: tools/concordia/ai_lab/digests/ (all digested folders). The AI_DECISION rows (patch 010 test overlay) are now present: 798,765 spell-choice rows, 242,702 block-start rows, 53,324 attack-level rows. The overlay is log-only, but the results-unchanged check is still open, so treat the overlay games as the same AI until that check passes.

Blocking, per blocker decision, by the blocker's life:
- Life 15 or more: 8% block (12,401 decisions).
- Life 8 to 14: 19% (11,601).
- Life under 8: 39% (14,075).
Same gradient as the earlier passes (5%/15%/35% at 376 games). The rule in section 1 holds at a larger sample.

Game shape:
- Median 15 turns, mean 16.6. Per game: casts 8.6 (A) and 8.5 (B); attacks 3.3 and 3.2; blocks 1.6 and 1.5.
- Cast median turn 11 across 48,423 casts.

Caveats: these are survey counts across all matchups, not per deck. The gradient is per decision, so one blocker facing several attackers counts several times. The overlay check is still open.

## Final results (research ended early, 3,094 digested games, 2026-10-21)
Ended on the main session's order. Blocking results are final for the digests so far.
- Blocking, by blocker life: 15+ life 8% (13,742 decisions); 8 to 14 life 19% (12,622); under 8 life 39% (15,525). Same gradient as the earlier passes.
- Game length: median 16 turns over 3,094 games.
- Patch 010 (AI decision log) is test-only. Its results-unchanged check is not completed, so overlay games are treated as the stock AI with that caveat.

Sections reached: 1 blocking (done), 2 attacking (done), 3 removal targeting (done), 4 spell order (done), 5 mana use (done).
Sections not completed (research ended early): commander, combat tricks, ETB/tokens, mulligan, "Logic by deck type". What remains: the same log-based checks as sections 1 to 5, applied to these areas, plus the deck-type table once the balance lab publishes its archetype tags.

## Completion pass over every digested game (3,146 games, 2026-10-21)
Digests: 3,146 games. AI_DECISION rows (patch 010 overlay) are in 2,670 games (84.9%). Digest rows carry no deck identity except the 20 Commander games labelled T2/T5, so results below are by situation, not by deck.

Blocking, final (blocker's own life): 15+ life 8% (14,026 decisions); 8 to 14 life 19% (12,842); under 8 life 39% (15,803). Median game 16 turns.

Combat tricks (CAST rows in a combat step, phases Declare Attackers / Declare Blockers / Combat Damage):
- 1,823 casts in 1,196 of 3,146 games (38.0%). Most are in declare-blockers steps (B 486, A 382), then declare attackers (B 246, A 227).
- Most used: Invigorate 87, Mortal's Resolve 60, Aspect of Hydra 60, Tyvar's Stand 45, Might of Alara 42, Hindervines 40, Legolas's Quick Reflexes 39, Heroic Intervention 37, Respite 36, Titan's Strength 33.
- Reading: the AI does use instant-speed tricks in combat, in the window the rules allow. It is a count of casts, not of wins; the logs cannot say whether a trick changed a combat.

ETB and tokens:
- Attack declarations naming a token: 2,451 of 20,549 (11.9%). Zone moves naming a token: 2,946 of 19,997.
- The digest has no TRIGGER rows for enter-the-battlefield triggers in these games, so ETB effects cannot be read from the logs. Tokens are visible only by name.

Attack situation (AI_ATTACK_LEVEL rows, by ratioDiff): ahead (ratioDiff 1 or more) 20,084 rows; even 21,937; behind 19,182. The rows show the AI's level input, not whether it attacked; the attack-per-level rate needs ATTACK rows joined to the same turn, which is not done here.

Not completed from the logs:
- Commander play (cast timing, commander tax, command-zone use): the digest records no command-zone moves and no tax costs. Needed: ZONE rows for "from Command zone" and the cast cost per commander cast.
- Mulligan and opening hands: no mulligan or hand-size lines are in the digest. Needed: the opening hand and each mulligan decision.
- Logic by deck type and by colour: needs a deck name or archetype on each digest row. Only the 20 Commander games carry a tier. Needed: deck id per game in the digest, then a join to the balance records.

## Agent/tool test: logic by archetype and colour (white and multicolour included) - 2026-10-21

Data: 96 lab games with a `games_meta.tsv` row (digests `lab-20261021T13*`, first batch that carries deck ids): 10 white (W), 86 multicolour, no other colour. Archetypes: aggro 30, midrange 38, ramp 16, control 12. Script: `analyse_meta.py` (`--detail` for the splits). Rates are `rate [Wilson 90%] n=decisions`; the unit is a decision, not a game, so decisions inside one game are not independent and the real intervals are wider. Colour is the deck A tag; side B's deck is not split. One digest bug found and fixed on the way (below).

| Area | All (96 games) | Aggro (30) | Midrange (38) | Ramp (16) | Control (12) | W (10) | Multi (86) |
|---|---|---|---|---|---|---|---|
| Block rate, blocker life 15+ | 9% [7-11] n=741 | 13% n=245 | 8% n=259 | 6% n=127 | 7% n=110 | 6% n=34 | 9% n=707 |
| Block rate, life 8-14 | 22% [18-26] n=247 | 29% n=66 | 18% n=102 | 18% n=44 | 26% n=35 | 20% n=30 | 22% n=217 |
| Block rate, life under 8 | 35% [31-39] n=418 | 33% n=120 | 38% n=194 | 34% n=67 | 30% n=37 | 36% n=53 | 35% n=365 |
| Attackers sent, ratioDiff >= 1 | 39% [37-41] n=1178 | 38% | 38% | 39% | 42% | 34% n=102 | 39% |
| Attackers sent, ratioDiff 0 to 1 | 19% [16-23] n=362 | 18% | 21% | 24% n=38 | 13% n=60 | 19% n=36 | 19% |
| Attackers sent, ratioDiff < 0 | 17% [15-19] n=944 | 11% n=301 | 18% | 17% | 30% n=97 | 13% n=123 | 18% |
| Mulligan lines per game | 0.54 | 0.47 | 0.58 | 0.25 | 1.00 | 0.10 (20 hands) | 0.59 |
| Non-basic mana sources | 27% n=6410 | 20% | 27% | 31% | 36% | 11% n=497 | 28% |

Reading:
- **Blocks.** The life-band rule holds in every archetype and in both colour groups: blocks stay under 15% above 15 life and rise to about a third under 8 life (all-games 9% -> 22% -> 35%). Aggro blocks more than the rest in the middle band (29%, n=66, wide interval), which is not a rule yet.
- **Attacks per aggression input.** The log holds `ratioDiff` and `attackers` per turn but not the chosen level (1-6), so the join is by `ratioDiff` band, not by level: the AI sends 39% of its available attackers when `ratioDiff` >= 1 and 17-19% below 1. Control is the exception when behind (30%, n=97 against 11% for aggro, n=301): control decks hold fewer bodies, so the "available attackers" count is small and the difference needs more games. Patch 012 will log the level to replace this proxy. Attackers are counted per turn from AI_ATTACK_LEVEL rows, so a creature that could attack twice in a turn is counted once.
- **Removal and spell order.** No new log line covers the removal target choice; the claim in section 3 (highest `evaluateCreature` target) is untested here. Spell choice rows (3,661) show candidates and the top pick only. Mean cast turn (not median) is 12.5 over 1,869 casts: W 10.3 (n=147), multi 12.7 (n=1,722), control 13.8 (n=283), aggro/midrange 12.1. White decks cast earlier, in line with their lower curve, from 10 games only.
- **Mana source.** 6,410 AI_MANA_SOURCE rows. Non-basic sources pay 27% of the shards; white is 11% (n=497), consistent with white decks being mostly basic Plains. Control 36%, ramp 31%.
- **Mulligans and hands.** 192 hands logged and 52 mulligan lines (0.54 per game). Control mulligans the most (1.00 per game, 12 games) and ramp the least (0.25); the white decks mulligan 0.10 per game from 10 games, too few to claim.
- **Commander play.** Only 10 command-zone moves in 96 games, so commander timing cannot be read yet. The log shows moves out of the command zone but no cost; a COMMANDER_CAST line is still needed.
- **ETB and tokens.** 2,064 triggers (ETB and other) and 152 token zone moves are visible: triggers per game are highest in control (41 per game, 12 games), 16 in aggro, 20 in ramp, 21 in midrange.

What the new log lines allowed that the old data did not: the GAME header gave deck, tier, archetype and colour per game (a split never possible in the 3,146-game pool); HAND/MULLIGAN lines gave opening hands; AI_MANA_SOURCE gave source choice; TRIGGER lines show ETB triggers (FINAL_REPORT section 2 wrongly says they cannot be read).

Tool problem fixed: AI_* digest rows (SPELL_CHOICE, MANA_SOURCE, BLOCK_START, ATTACK_LEVEL) carried the end-of-game life in `life_a`/`life_b` because the AI_DECISION log lines sit at the end of the raw log. `phase_digest.py` now gives them the life at the end of their own turn. Digests written before 2026-10-21 14:10Z keep the old values, so use the `life=` field in the detail for those (the analysis above does).

Still missing: the chosen aggression level (patch 012), block and attack reasons (012), the commander cast cost, removal target reasoning, and any white or multicolour result split by tier (96 games over 18 cells is too thin). Colours other than W and multi do not appear in this batch. Nothing here changes the numbers in `OPTIONS_FOR_BALANCERS.md`.

### Addendum 2026-10-21 (lab finished: 120 games with meta, was 96)
24 more lab games (`lab-20261021T14*`). Colour is still the deck-A tag only: W 14 games, multicolour 106. Side B is not split, so white decks are present in more games than the 14 counted here. Archetypes: aggro 30, midrange 46, ramp 20, control 24. Same method and caveats as above.
- **Blocks, all games:** 9% [8-11] n=977 at 15+ life, 24% [20-28] n=310 at 8-14, 34% [31-38] n=483 under 8. The shape is unchanged; control now reads 7% / 21% / 29% (n=229 / 67 / 85), white 6% / 26% / 36% (n=68 / 39 / 56).
- **Attackers sent by `ratioDiff`:** 39% [37-41] n=1534 when >= 1, 19% [16-22] n=430 from 0 to 1, 18% [16-19] n=1161 below 0. The control "behind" outlier fell from 30% to 24% (n=217) with more games, so it was mostly noise; aggro stays lowest when behind (11%, n=301).
- **Mulligans:** 0.55 lines per game overall (240 hands). Control fell from 1.00 to 0.88 per game (24 games), ramp 0.30, white 0.21 per game (28 hands), so white's low rate is holding but still a small sample.
- **Mana and cast timing:** non-basic sources 29% n=8,210 (white 17% n=688, control 38% n=1,791). Mean cast turn 12.9 over 2,402 casts; white 10.1 (n=202 casts), multicolour 13.2, control 14.0.
- **Commander and triggers:** 11 command-zone moves in 120 games (still too few); 2,510 triggers.
- Nothing here changes `OPTIONS_FOR_BALANCERS.md`.

## Deck-building tags and human logic (2026-10-21)
The deck builder's ability-led tags (`tools/concordia/deckgen/ability_tags.py`, `ABILITY_TAGS.toon`) and archetype rules (`tools/concordia/archetype_rules.py`, `tier1_rules.py`) do not reach the in-game AI. The only deck-level input is `PlayerControllerAi.setupAutoProfile` (name contains "Control" or average CMC > 3). Human-logic rules H31-H49 are builder rules; their AI counterparts and the gap list are in `DECK_LOGIC_TO_AI_DECISIONS.md`. Proposals DL-1 to DL-5 are unticked in `AI_CHANGES_APPROVAL.md`.

## AI play styles (2026-10-21)
Four shipped profiles (Default, Reckless, Cautious, Experimental) differ in about 20 properties; Concordia enemies all use the player's setting (`enemies.json` "ai" is ""). Details, edit options and the test design are in `AI_PLAY_STYLES.md`; proposals PS-1 to PS-5 are unticked in `AI_CHANGES_APPROVAL.md`.

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

Still open: `chooseDefender` (770) and `reinforceWithBanding` (501) are not yet traced.

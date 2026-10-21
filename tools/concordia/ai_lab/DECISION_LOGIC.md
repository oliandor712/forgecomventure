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
- Attack logic (AiAttackController.java, 1881 lines): not yet read.
- Removal targeting, spell order, mana, commander, tricks, ETB/tokens, mulligan: not yet read.
- "Logic by deck type" archetype categories are provisional until tools/concordia/balance_lab/README.md publishes its tags.

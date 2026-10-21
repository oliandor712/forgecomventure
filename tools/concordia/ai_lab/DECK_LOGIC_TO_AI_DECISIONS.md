# Deck-building logic -> Forge AI decisions (research, forge-ai-lab, 2026-10-21)

Research only. Nothing applied to forge-ai/src, nothing on the sim overlay, no builds. Proposals are unticked entries in `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md` (DL-1 to DL-5). Inputs read: `tools/concordia/deckgen/HANDOFF_DECKBUILDER.md`, `deckgen/ability_tags.py` (POLICY, `tags_of`, `bonus`), `deckgen/ABILITY_TAGS.toon`, `deckgen/commander_support.py`, `tools/concordia/archetype_rules.py`, `tools/concordia/tier1_rules.py`, `tools/agents/human_logic.toon` H31-H49.

## 1. What the AI reads today (verified by grep, forge-ai and forge-game)
| Signal | Where the AI reads it | Read in game? |
|---|---|---|
| `[metadata] Name=` containing "Control", or deck average CMC > 3 | `PlayerControllerAi.setupAutoProfile` (line 75-76) sets `pilotsNonAggroDeck`; `AiAttackController` 398-435 uses it for the baseline-life attack gate | yes (the only deck-level signal) |
| `AI:RemoveDeck:All/NonCommander/Random` | `ComputerUtilCard.isCardRemAIDeck` (2303-2311), `AiController` 1650 | yes (deck building exclusion) |
| `AILogic$` param (Pump 77, Fog 36, Bounce 5, Protection 2, BadETB 1, DelayedBlink 1) | `AiController` 380, 1103; `ComputerUtil.hasAFogEffect` (1512) used by `AiBlockController` 1153 and `AiAttackController` 600 | yes |
| `SVar:AIPreference` (SacCost 196, DiscardCost 37, ManaFrom 14) and `AIPreferenceParams` (CreatureEvalThreshold, MinCreaturesBelowThreshold) | `ComputerUtil.getCardPreference` (284-303), `ComputerUtilMana` 299, `BondAi` 62 | yes |
| `AIActivateLast$ True` | `ComputerUtilAbility.saComparator` (246+) | yes (1 card) |
| `DeckHas` / `DeckNeeds` / `DeckHints` (`CardAiHints`) | only `forge-gui` limited/commander deck builders and `CardRanker`; NOT in forge-ai | **no**: the in-game AI never reads them |
| Live creature stats | `CreatureEvaluator` (power*15, toughness*10, keywords) via `ComputerUtilCard.evaluateCreature` | yes (current P/T, not potential) |
| Opponent-deck composition | `AILogic$ MostProminentInHumanDeck` (34 cards), `MostProminentInComputerDeck` (85) | yes (card-level, from the decks) |

Key finding: the deck-builder's tags (ability_tags.py POLICY) and archetypes (archetype_rules.py) never reach the game. The AI's only deck-level input is the name/CMC test above.

Correction (2026-10-21, after the main session's check): `Deck.getAverageCMC` (forge-core `Deck.java` 804-816) counts only non-land Main and Commander cards that are artifacts, creatures, enchantments or planeswalkers. Instants and sorceries are NOT counted, and the commander is. So "average CMC > 3" is not the nonland average the builder reports (`deck_tier` avg_mv); the two can differ. Tier-level split to be re-checked against this exact function before DL-1 is judged.

## 2. Mapping table (deck-building signal -> nearest existing AI mechanism)
| # | Deck-building rule (H-row / tag) | What the AI does today | Gap | Smallest syntax-conforming change |
|---|---|---|---|---|
| 1 | archetype control / aggro / tokens / tribal (archetype_rules.classify) | `pilotsNonAggroDeck` from name "Control" or CMC > 3 (PlayerControllerAi 76) | Name rule misses most tier 2-5 decks; CMC > 3 is blunt | Reuse the existing `Name=` convention: the builder names a deck "... Control" for control archetypes. No new code. (DL-1) |
| 2 | `scales:Y`, `lord:Y`, potential stat (H31, H46-H48) | live P/T via CreatureEvaluator and the game's own static abilities | none for play (AI sees the real stat); deck-level value of the synergy is unused | None needed for play. Only the builder reads these. |
| 3 | protection_trick, fog (ability_tags groups control/protection) | `AILogic$ Fog` / `Protection`, `hasAFogEffect` checks battlefield and external zones | 2 cards use `Protection`; the tag covers more | Add `AILogic$ Protection` to protection_trick cards that lack it, reusing the existing value. Card-script change: needs approval (DL-2) |
| 4 | attack_tax, restrict (control/lock; H34) | attack gate `canAttackWrapper` and `shouldAttack`; no explicit tax-aware branch seen | not verified in code: whether the AI pays attack taxes (`AiCostDecision`) is open | Check `AiCostDecision` first; if it refuses, reuse `AILogic$ ...` only if an existing value fits (DL-3, research item) |
| 5 | etb / blink / flicker synergy (H38, H39) | `AILogic$ BadETB` (1 card) and `AILogic$ DelayedBlink` (1); play order by CMC and `evaluateCreature` (`saComparator`) | play order ignores enter-the-battlefield value | Reuse `AILogic$ BadETB` on the ETB creatures the tag marks; no new code (DL-4) |
| 6 | burn / drain (control/burn; H36) | `DamageAiBase.shouldTgtP` (line 45): face vs creature on current life, opponent's hand, gain-life check | burn-tag synergy and drain scaling are not read | Reuse `NumDmg$ X` with `SVar:X:TargetedPlayer$CardsInHand` (the existing pattern) for scaling drains; no new syntax (DL-5) |
| 7 | removal priority (creature > artifact > enchantment > land > token; reach) | `ComputerUtilCard` 585-605 target value = `evaluateCreature`; `DestroyAi` 40-241 | the builder's reach classes are not used in targeting | None proposed yet; research item |
| 8 | token makers, tribal (H40) | `AILogic$ Pump` (77) and `pump_team` cards read by `evaluateCreature` via live board | tribe count is not in any AI decision | None; research item |
| 9 | mana and land types (H45) | `AIPreference ManaFrom$` (14 cards); `ComputerUtilMana` 293 chooseManaAbility | the landtype tags are unused by the AI | None needed; the AI pays with what it has |
| 10 | commander ability support (H17, H31-H37) | commander cards get `evaluateCreature` only | the builder's support count (5+) has no game counterpart | None: the AI does not plan around its commander |

## 3. Gaps ranked by expected impact on player-win rate
1. **Deck archetype never reaches the AI (row 1).** The attack gate (`AiAttackController` 398-435) decides how far the AI pushes into trades, and only the name or CMC sets it. Most tier 2-5 AI decks are not named "Control", so their profile is chosen by CMC. Expected impact: high, because it changes attacks for every AI deck. Cost: name change in deck files, no code.
2. **Attack-tax and restrict logic unverified (row 4).** If the AI does not pay attack taxes, control decks with tax permanents win more than their tags suggest. Needs a code read of `AiCostDecision` before any proposal. Impact: medium-high for control, unknown.
3. **Burn and drain do not scale (row 6).** `shouldTgtP` uses current life and hand, not the drain count the builder tags. Impact: medium for burn decks.
4. **Enter-the-battlefield creatures are played by CMC (row 5).** Only one card uses `BadETB`. Impact: medium for blink decks.
5. **Protection tag coverage (row 3).** `Protection` is on 2 cards only; the rest rely on `Fog`. Impact: low to medium; a card-script change.

## 4. Proposals (all unticked in AI_CHANGES_APPROVAL.md)
- **DL-1** Builder names control decks "... Control" (existing `Name=` convention read by `setupAutoProfile`). Change: deck names only, by the deck builder, after a dry build is approved. No forge-ai change.
- **DL-2** Add `AILogic$ Protection` to protection_trick cards lacking it, same value as the existing two. Card scripts: approval needed.
- **DL-3** Research item: read `AiCostDecision` for attack-tax payment before any proposal.
- **DL-4** Reuse `AILogic$ BadETB` on ETB creatures the blink tag marks. Card scripts: approval needed.
- **DL-5** Reuse `NumDmg$ X` + `SVar:X:TargetedPlayer$CardsInHand` pattern for drain scaling. Card scripts: approval needed.
No new AILogic names, parameters or SVar keys are proposed. Anything beyond these needs a new parameter, and per the user's rule it must be shown as a diff next to the existing example first.

## 5. Caveats
- Research by reading and grep; no game was run for this document.
- Potential stats are not read by the AI (it sees live stats), so builder rules H46-H48 matter only for the deck-builder.
- `DeckHas/DeckNeeds/DeckHints` are real Forge data but are used only by Forge's own deck builders, not by in-game play.

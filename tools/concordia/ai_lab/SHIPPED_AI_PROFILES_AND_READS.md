# Shipped AI profiles and what the AI reads during a match (forge-ai-lab, 2026-10-21)

Research only. Original forge-ai and shipped profiles only: `forge-gui/res/ai/*.ai` and `forge-ai/src` at HEAD. Git history shows no Concordia ("Claude") commit touched `forge-ai/src`, `forge-game/src`, `forge-core/src` or `forge-gui/res/ai` on campaign-design; the test overlay (`tools/concordia/ai_lab/patches/`) is NOT in these files and is excluded. Shipped profile files last changed in upstream commit 1064ce3b35c. Nothing applied to forge-ai/src, the overlay or card scripts.

Summary rule: rows marked (auto) are generated from the code by a script (read sites by grep of `AiProps.NAME`, values read from the four `.ai` files); their summary states only where and how often the property is read. Rows marked (hand) are written by hand, max 3 sentences.

## 1. Shipped profiles (record per profile)
| Profile | File | Selected by | Summary (hand, max 3 sentences) |
|---|---|---|---|
| Default | `forge-gui/res/ai/Default.ai` | user setting `UI_CURRENT_AI_PROFILE`; default when the adventure enemy `"ai"` is empty or unknown | Balanced baseline: no aggro, no trade-into-block, mulligan threshold 4, danger band 4-4. Holds combat tricks until blocks (65%). Lets the AI randomly trade on block (30-70%). |
| Reckless | `Reckless.ai` | adventure `"ai": "reckless"` (DuelScene `selectAI`) or user setting | Plays aggro: PLAY_AGGRO true, always attacks into trades (100%), trades when tapped out, mulligan threshold 3. Trades creatures evenly (max creature-count difference 0). |
| Cautious | `Cautious.ai` | adventure `"ai": "cautious"` or user setting | Holds back: no attacks into trades, no berserk, no pre-block avoidance, counters only spells with CMC 2+, danger band 4-6. Does not hold combat tricks until blocks (the switch is off; its chance value is 75). |
| Experimental | `Experimental.ai` | adventure `"ai": "experimental"` or user setting | Like Default but with a wider danger band (3-12), always chains two damage spells, and a 2+ CMC counter minimum. Tokens are generated 100% of the time. |

## 2. Deck-level and game-level inputs (record per input)
| Input | Where read (file:line) | Used by | Status and summary (hand, max 3 sentences) |
|---|---|---|---|
| pilotsNonAggroDeck flag | PlayerControllerAi.java 63, 75-76 (`setupAutoProfile`) | AiAttackController 398-435 (baseline life gate) | Read in game. True when the deck name contains "Control" or the average CMC is above 3. Set once per match on game 1, from `complainCardsCantPlayWell` (Match.java 327-328). |
| Deck name "Control" test | PlayerControllerAi.java 76 (`deck.getName().contains("Control")`) | same flag | Read in game (see above). Deck name comes from the `.dck` `Name=` line; tier 2-5 names do not contain "Control". |
| Average CMC test | PlayerControllerAi.java 76 `deck.getAverageCMC() > 3`; forge-core `Deck.java` 804-816 | same flag | Read in game. Counts only non-land Main and Commander cards that are artifact, creature, enchantment or planeswalker: instants and sorceries are NOT counted, the commander IS. Not the same as nonland average MV. |
| Profile name per player | LobbyPlayerAi.java 14, 25-31 (`aiProfile`, `setAiProfile`) | AiProfileUtil.getAIProp 146-150 | Read in game on every property read; a new name takes effect at the next decision. Unknown names silently use the AiProps enum defaults. |
| Profile value lookup | AiController.java 1290-1297; AiProfileUtil.java 118-150 | all 122 properties (section 3) | Read in game. Values are not cached in fields (grep found no cached property). |
| Profile loading | AiProfileUtil.java 80-89 `loadAllProfiles`; FModel.java 276 | once at start | Read at start only; reloadable only by calling `loadAllProfiles` again. |
| Adventure enemy profile | forge-gui-mobile DuelScene.java 515, 911-924 (`selectAI`); EnemyData.java 29, 62 (`ai`) | adventure duels | Read at duel start. Accepts default, reckless, cautious, experimental (case-insensitive); anything else, including empty, uses the user's setting. All 58 Concordia enemies are "". |
| Profile rotation | GamePlayerUtil.java 85-96; LobbyPlayerAi.java 15, 33-34 | random profile modes | Read at player creation: random every match or game. |
| AILogic$ (card script) | AiController.java 380, 1085, 1103, 1124, 1550; ComputerUtilMana 732 (BlackLotus); AiBlockController/AiAttackController via hasAFogEffect | card-level behaviour (343 distinct values on 1,814 cards) | Read in game. Most common values: Always, PowerDmg, MostProminentInComputerDeck (85 cards), Pump (76), AtOppEOT (68), NeedsPrevention (65), Curse (64), Fight (63), Fog (36), Destroy (36), Bounce (5), Protection (2), BadETB (1). |
| AIPreference (SVar) | ComputerUtil.java 284-303 `getCardPreference`; ComputerUtilMana 299; BondAi 62 | sacrifice, discard and mana choices | Read in game on 250 cards: SacCost 196, DiscardCost 37, ManaFrom 14, SoulBond 1. AIPreferenceParams (CreatureEvalThreshold, MinCreaturesBelowThreshold) read by `getAIPreferenceParameter` (ComputerUtil 488). |
| AI:RemoveDeck (AI hint) | ComputerUtilCard.java 2303-2311; AiController.java 1650 | deck building exclusion (All 2,477; Random 2,383; NonCommander 70 lines) | Read by the Forge deck builders and in game only for the remove-from-AI-deck flag. Present on 4,675 card scripts. |
| AIActivateLast$ (AI hint) | ComputerUtilAbility.java 246+ (`saComparator`) | activation order | Read in game. 1 card script carries it. |
| DeckHas / DeckNeeds / DeckHints | forge-core `CardAiHints.java` 13-15 and `DeckHints.java`; read by forge-gui `LimitedDeckBuilder`, `CommanderDraftDeckBuilder`, `CardRanker` | Forge's own deck builders | NOT read by forge-ai (grep found no use in forge-ai). The in-game AI never sees these hints. |
| MostProminentInComputerDeck / HumanDeck (AILogic) | ComputerUtil.java 2506-2509; PlayerControllerAi.java 1552-1554; ability/ChooseColorAi 64 | colour and target choice from the decks | Read in game: the AI looks at the colours in each deck. Used by 85 and 34 card scripts. |
| Live creature value | ComputerUtilCard.java 784-790 `evaluateCreature` -> CreatureEvaluator.java 31-166 | targets, blocks, play order | Read in game from live power, toughness and keywords; potential stats are not read. |
| Play-order comparator | ComputerUtilAbility.java 246-355 (`saComparator`) | which spell or ability is cast first | Read in game: highest mana cost first, creatures adjusted by evaluateCreature. |
| Opponent composition | PlayerControllerAi.java 1552-1554; ComputerUtil.java 2506 | colour and target choice | Read in game from the battlefield and decks (see above). |

## 3. Profile properties (record per AiProps entry; 122 records)
Columns: property, AiProps enum default, the four shipped values (Default / Reckless / Cautious / Experimental), whether the shipped values differ, read sites (count and first site, auto), files that read it (auto). A property the profile files do not set falls back to the enum default. Summary (auto): where and how often the code reads it; the behaviour follows from the value and the read site.

| # | Property | Enum default | Default | Reckless | Cautious | Experimental | Differ | Reads | First read site (auto) | Read by files (auto) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | DEFAULT_MAX_PLANAR_DIE_ROLLS_PER_TURN | 1 | 1 | 1 | 1 | 1 | no | 1 | RollPlanarDiceAi.java:35 (willRollOnPlane) | RollPlanarDiceAi.java |
| 2 | DEFAULT_MIN_TURN_TO_ROLL_PLANAR_DIE | 3 | 3 | 1 | 3 | 3 | yes | 1 | RollPlanarDiceAi.java:38 (willRollOnPlane) | RollPlanarDiceAi.java |
| 3 | DEFAULT_PLANAR_DIE_ROLL_CHANCE | 50 | 50 | 100 | 50 | 50 | yes | 1 | RollPlanarDiceAi.java:36 (willRollOnPlane) | RollPlanarDiceAi.java |
| 4 | MULLIGAN_THRESHOLD | 5 | 4 | 3 | 4 | 4 | yes | 2 | ComputerUtil.java:2096 (scoreHand) | ComputerUtil.java |
| 5 | PLANAR_DIE_ROLL_HESITATION_CHANCE | 10 | 10 | 0 | 10 | 10 | yes | 1 | RollPlanarDiceAi.java:37 (willRollOnPlane) | RollPlanarDiceAi.java |
| 6 | HOLD_LAND_DROP_FOR_MAIN2_IF_UNUSED | 0 | 100 | 30 | 100 | 100 | yes | 1 | AiController.java:1495 (isSafeToHoldLandDropForMain2) | AiController.java |
| 7 | HOLD_LAND_DROP_ONLY_IF_HAVE_OTHER_PERMS | true | true | true | true | true | no | 1 | AiController.java:1503 (isSafeToHoldLandDropForMain2) | AiController.java |
| 8 | CHEAT_WITH_MANA_ON_SHUFFLE | false | true | true | true | true | no | 1 | AiController.java:2226 (cheatShuffle) | AiController.java |
| 9 | MOVE_EQUIPMENT_TO_BETTER_CREATURES | from_useless_only | from_useless_only | always | from_useless_only | always | yes | 2 | AttachAi.java:1362 (attachToCardAIPreferences) | AttachAi.java |
| 10 | MOVE_EQUIPMENT_CREATURE_EVAL_THRESHOLD | 60 | 60 | 50 | 60 | 60 | yes | 1 | AttachAi.java:1389 (attachToCardAIPreferences) | AttachAi.java |
| 11 | PRIORITIZE_MOVE_EQUIPMENT_IF_USELESS | true | true | false | true | true | yes | 1 | AttachAi.java:1374 (attachToCardAIPreferences) | AttachAi.java |
| 12 | SAC_TO_REATTACH_TARGET_EVAL_THRESHOLD | 400 | 400 | 300 | 500 | 350 | yes | 1 | AttachAi.java:893 (attachAIHighestEvaluationPreference) | AttachAi.java |
| 13 | PREDICT_SPELLS_FOR_MAIN2 | true | true | true | true | true | no | 1 | AiController.java:739 (predictSpellToCastInMain2) | AiController.java |
| 14 | RESERVE_MANA_FOR_MAIN2_CHANCE | 0 | 100 | 100 | 100 | 100 | no | 1 | ComputerUtilMana.java:1230 (isManaSourceReserved) | ComputerUtilMana.java |
| 15 | PLAY_AGGRO | false | false | true | false | false | yes | 7 | AiBlockController.java:1123 (assignBlockers) | AiAttackController.java, AiBlockController.java, CountersProliferateAi.java, CountersPutAi.java |
| 16 | CHANCE_TO_ATTACK_INTO_TRADE | 40 | 0 | 100 | 0 | 0 | yes | 1 | AiAttackController.java:875 (declareAttackers) | AiAttackController.java |
| 17 | RANDOMLY_ATKTRADE_ONLY_ON_LOWER_LIFE_PRESSURE | true | true | false | true | true | yes | 1 | AiAttackController.java:878 (declareAttackers) | AiAttackController.java |
| 18 | ATTACK_INTO_TRADE_WHEN_TAPPED_OUT | false | false | true | false | false | yes | 1 | AiAttackController.java:876 (declareAttackers) | AiAttackController.java |
| 19 | CHANCE_TO_ATKTRADE_WHEN_OPP_HAS_MANA | 0 | 30 | 100 | 0 | 30 | yes | 1 | AiAttackController.java:877 (declareAttackers) | AiAttackController.java |
| 20 | TRY_TO_AVOID_ATTACKING_INTO_CERTAIN_BLOCK | true | true | true | false | true | yes | 1 | AiAttackController.java:1473 (calculate) | AiAttackController.java |
| 21 | TRY_TO_HOLD_COMBAT_TRICKS_UNTIL_BLOCK | false | true | true | false | true | yes | 1 | ComputerUtilCard.java:1493 (landGrantingRemoval) | ComputerUtilCard.java |
| 22 | CHANCE_TO_HOLD_COMBAT_TRICKS_UNTIL_BLOCK | 30 | 65 | 65 | 75 | 75 | yes | 1 | ComputerUtilCard.java:1494 (landGrantingRemoval) | ComputerUtilCard.java |
| 23 | ENABLE_RANDOM_FAVORABLE_TRADES_ON_BLOCK | true | true | true | true | true | no | 1 | AiBlockController.java:1359 (wouldLikeToRandomlyTrade) | AiBlockController.java |
| 24 | RANDOMLY_TRADE_EVEN_WHEN_HAVE_LESS_CREATS | false | false | false | false | false | no | 1 | AiBlockController.java:1360 (wouldLikeToRandomlyTrade) | AiBlockController.java |
| 25 | MAX_DIFF_IN_CREATURE_COUNT_TO_TRADE | 1 | 1 | 0 | 0 | 1 | yes | 1 | AiBlockController.java:1365 (wouldLikeToRandomlyTrade) | AiBlockController.java |
| 26 | ALSO_TRADE_WHEN_HAVE_A_REPLACEMENT_CREAT | true | true | true | false | true | yes | 1 | AiBlockController.java:1361 (wouldLikeToRandomlyTrade) | AiBlockController.java |
| 27 | MAX_DIFF_IN_CREATURE_COUNT_TO_TRADE_WITH_REPL | 1 | 1 | 1 | 0 | 1 | yes | 1 | AiBlockController.java:1366 (wouldLikeToRandomlyTrade) | AiBlockController.java |
| 28 | MIN_CHANCE_TO_RANDOMLY_TRADE_ON_BLOCK | 30 | 30 | 0 | 40 | 30 | yes | 1 | AiBlockController.java:1362 (wouldLikeToRandomlyTrade) | AiBlockController.java |
| 29 | MAX_CHANCE_TO_RANDOMLY_TRADE_ON_BLOCK | 70 | 70 | 50 | 65 | 70 | yes | 1 | AiBlockController.java:1363 (wouldLikeToRandomlyTrade) | AiBlockController.java |
| 30 | CHANCE_DECREASE_TO_TRADE_VS_EMBALM | 30 | 30 | 10 | 50 | 30 | yes | 1 | AiBlockController.java:1364 (wouldLikeToRandomlyTrade) | AiBlockController.java |
| 31 | CHANCE_TO_TRADE_TO_SAVE_PLANESWALKER | 70 | 70 | 80 | 90 | 70 | yes | 1 | AiBlockController.java:1367 (wouldLikeToRandomlyTrade) | AiBlockController.java |
| 32 | CHANCE_TO_TRADE_DOWN_TO_SAVE_PLANESWALKER | 0 | 0 | 0 | 0 | 40 | yes | 1 | AiBlockController.java:1368 (wouldLikeToRandomlyTrade) | AiBlockController.java |
| 33 | THRESHOLD_TOKEN_CHUMP_TO_SAVE_PLANESWALKER | 135 | 135 | 135 | 135 | 135 | no | 1 | AiBlockController.java:880 (makeChumpBlocksToSavePW) | AiBlockController.java |
| 34 | THRESHOLD_NONTOKEN_CHUMP_TO_SAVE_PLANESWALKER | 110 | 120 | 130 | 110 | 110 | yes | 1 | AiBlockController.java:881 (makeChumpBlocksToSavePW) | AiBlockController.java |
| 35 | CHUMP_TO_SAVE_PLANESWALKER_ONLY_ON_LETHAL | true | true | true | true | false | yes | 1 | AiBlockController.java:882 (makeChumpBlocksToSavePW) | AiBlockController.java |
| 36 | TRY_TO_PRESERVE_BUYBACK_SPELLS | true | true | false | true | true | yes | 1 | AiController.java:907 (canPlaySa) | AiController.java |
| 37 | MIN_SPELL_CMC_TO_COUNTER | 0 | 0 | 0 | 2 | 2 | yes | 1 | CounterAi.java:169 (checkApiLogic) | CounterAi.java |
| 38 | CHANCE_TO_COUNTER_CMC_1 | 50 | 30 | 80 | 0 | 30 | yes | 1 | CounterAi.java:153 (checkApiLogic) | CounterAi.java |
| 39 | CHANCE_TO_COUNTER_CMC_2 | 75 | 75 | 100 | 50 | 75 | yes | 1 | CounterAi.java:154 (checkApiLogic) | CounterAi.java |
| 40 | CHANCE_TO_COUNTER_CMC_3 | 100 | 100 | 100 | 100 | 100 | no | 1 | CounterAi.java:155 (checkApiLogic) | CounterAi.java |
| 41 | ALWAYS_COUNTER_OTHER_COUNTERSPELLS | true | true | true | true | true | no | 1 | CounterAi.java:152 (checkApiLogic) | CounterAi.java |
| 42 | ALWAYS_COUNTER_DAMAGE_SPELLS | true | true | true | true | true | no | 1 | CounterAi.java:148 (checkApiLogic) | CounterAi.java |
| 43 | ALWAYS_COUNTER_CMC_0_MANA_MAKING_PERMS | true | true | true | true | true | no | 1 | CounterAi.java:147 (checkApiLogic) | CounterAi.java |
| 44 | ALWAYS_COUNTER_REMOVAL_SPELLS | true | true | true | true | true | no | 1 | CounterAi.java:149 (checkApiLogic) | CounterAi.java |
| 45 | ALWAYS_COUNTER_PUMP_SPELLS | true | true | true | false | true | yes | 1 | CounterAi.java:150 (checkApiLogic) | CounterAi.java |
| 46 | ALWAYS_COUNTER_AURAS | true | true | true | true | true | no | 1 | CounterAi.java:151 (checkApiLogic) | CounterAi.java |
| 47 | ALWAYS_COUNTER_SPELLS_FROM_NAMED_CARDS |  | None | None | None | None | no | 1 | CounterAi.java:156 (checkApiLogic) | CounterAi.java |
| 48 | CHANCE_TO_COPY_OWN_SPELL_WHILE_ON_STACK | 30 | 30 | 50 | 0 | 30 | yes | 1 | CopySpellAbilityAi.java:22 (checkApiLogic) | CopySpellAbilityAi.java |
| 49 | ALWAYS_COPY_SPELL_IF_CMC_DIFF | 2 | 2 | 1 | 4 | 2 | yes | 1 | CopySpellAbilityAi.java:23 (checkApiLogic) | CopySpellAbilityAi.java |
| 50 | ACTIVELY_DESTROY_ARTS_AND_NONAURA_ENCHS | true | true | true | true | true | no | 1 | ComputerUtilCard.java:1374 (useRemovalNow) | ComputerUtilCard.java |
| 51 | ACTIVELY_DESTROY_IMMEDIATELY_UNBLOCKABLE | false | true | false | false | true | yes | 2 | ComputerUtil.java:1978 (predictThreatenedObjects) | ComputerUtil.java, ComputerUtilCard.java |
| 52 | ACTIVELY_PROTECT_VS_CURSE_AURAS | false | true | false | true | true | yes | 0 | no read site (unused) |  |
| 53 | DESTROY_IMMEDIATELY_UNBLOCKABLE_THRESHOLD | 2 | 2 | 2 | 2 | 3 | yes | 1 | ComputerUtilCard.java:2113 (prioritizeCreaturesWorthRemovingNow) | ComputerUtilCard.java |
| 54 | DESTROY_IMMEDIATELY_UNBLOCKABLE_ONLY_IN_DNGR | true | true | true | true | false | yes | 1 | ComputerUtilCard.java:2114 (prioritizeCreaturesWorthRemovingNow) | ComputerUtilCard.java |
| 55 | DESTROY_IMMEDIATELY_UNBLOCKABLE_LIFE_IN_DNGR | 5 | 5 | 5 | 5 | 5 | no | 1 | ComputerUtilCard.java:2115 (prioritizeCreaturesWorthRemovingNow) | ComputerUtilCard.java |
| 56 | AVOID_TARGETING_CREATS_THAT_WILL_DIE | true | true | true | true | true | no | 1 | ComputerUtil.java:2049 (filterCreaturesThatWillDieThisTurn) | ComputerUtil.java |
| 57 | DONT_EVAL_KILLSPELLS_ON_STACK_WITH_PERMISSION | true | true | true | true | false | yes | 1 | ComputerUtil.java:2018 (predictCreatureWillDieThisTurn) | ComputerUtil.java |
| 58 | CHANCE_TO_CHAIN_TWO_DAMAGE_SPELLS | 50 | 90 | 75 | 25 | 100 | yes | 1 | DamageDealAi.java:1048 (getDamagingSAToChain) | DamageDealAi.java |
| 59 | HOLD_X_DAMAGE_SPELLS_FOR_MORE_DAMAGE_CHANCE | 100 | 100 | 85 | 100 | 100 | yes | 1 | DamageDealAi.java:111 (canPlay) | DamageDealAi.java |
| 60 | HOLD_X_DAMAGE_SPELLS_THRESHOLD | 5 | 5 | 3 | 6 | 5 | yes | 1 | DamageDealAi.java:113 (canPlay) | DamageDealAi.java |
| 61 | PRIORITY_REDUCTION_FOR_STORM_SPELLS | 0 | 9 | 0 | 9 | 9 | yes | 1 | ComputerUtilAbility.java:396 (getSpellAbilityPriority) | ComputerUtilAbility.java |
| 62 | USE_BERSERK_AGGRESSIVELY | false | true | true | false | true | yes | 1 | ComputerUtilCard.java:1820 (landGrantingRemoval) | ComputerUtilCard.java |
| 63 | MIN_COUNT_FOR_STORM_SPELLS | 0 | 1 | 0 | 1 | 1 | yes | 1 | AiController.java:1704 (chooseSpellAbilityToPlayFromList) | AiController.java |
| 64 | STRIPMINE_MIN_LANDS_IN_HAND_TO_ACTIVATE | 1 | 1 | 1 | 1 | 1 | no | 1 | DestroyAi.java:436 (doLandForLandRemovalLogic) | DestroyAi.java |
| 65 | STRIPMINE_MIN_LANDS_FOR_NO_TIMING_CHECK | 3 | 9999 | 3 | 9999 | 9999 | yes | 1 | DestroyAi.java:435 (doLandForLandRemovalLogic) | DestroyAi.java |
| 66 | STRIPMINE_MIN_LANDS_OTB_FOR_NO_TEMPO_CHECK | 6 | 6 | 4 | 8 | 6 | yes | 1 | DestroyAi.java:434 (doLandForLandRemovalLogic) | DestroyAi.java |
| 67 | STRIPMINE_MAX_LANDS_TO_ATTEMPT_MANALOCKING | 3 | 3 | 4 | 3 | 3 | yes | 1 | DestroyAi.java:437 (doLandForLandRemovalLogic) | DestroyAi.java |
| 68 | STRIPMINE_HIGH_PRIORITY_ON_SKIPPED_LANDDROP | false | true | true | true | true | no | 1 | DestroyAi.java:438 (doLandForLandRemovalLogic) | DestroyAi.java |
| 69 | TOKEN_GENERATION_ABILITY_CHANCE | 80 | 80 | 80 | 80 | 100 | yes | 1 | TokenAi.java:186 (checkApiLogic) | TokenAi.java |
| 70 | TOKEN_GENERATION_ALWAYS_IF_FROM_PLANESWALKER | true | true | true | true | true | no | 1 | TokenAi.java:187 (checkApiLogic) | TokenAi.java |
| 71 | TOKEN_GENERATION_ALWAYS_IF_OPP_ATTACKS | true | true | true | true | true | no | 1 | TokenAi.java:188 (checkApiLogic) | TokenAi.java |
| 72 | SCRY_NUM_LANDS_TO_STILL_NEED_MORE | 4 | 4 | 3 | 4 | 4 | yes | 1 | ComputerUtil.java:2222 (scryWillMoveCardToBottomOfLibrary) | ComputerUtil.java |
| 73 | SCRY_NUM_LANDS_TO_NOT_NEED_MORE | 7 | 7 | 5 | 8 | 7 | yes | 2 | ComputerUtil.java:2223 (scryWillMoveCardToBottomOfLibrary) | ComputerUtil.java, RearrangeTopOfLibraryAi.java |
| 74 | SCRY_NUM_CREATURES_TO_NOT_NEED_SUBPAR_ONES | 4 | 4 | 4 | 4 | 4 | no | 1 | ComputerUtil.java:2224 (scryWillMoveCardToBottomOfLibrary) | ComputerUtil.java |
| 75 | SCRY_EVALTHR_CREATCOUNT_TO_SCRY_AWAY_LOWCMC | 3 | 3 | 3 | 3 | 3 | no | 1 | ComputerUtil.java:2227 (scryWillMoveCardToBottomOfLibrary) | ComputerUtil.java |
| 76 | SCRY_EVALTHR_TO_SCRY_AWAY_LOWCMC_CREATURE | 160 | 160 | 160 | 160 | 160 | no | 1 | ComputerUtil.java:2225 (scryWillMoveCardToBottomOfLibrary) | ComputerUtil.java |
| 77 | SCRY_EVALTHR_CMC_THRESHOLD | 3 | 3 | 1 | 3 | 3 | yes | 1 | ComputerUtil.java:2226 (scryWillMoveCardToBottomOfLibrary) | ComputerUtil.java |
| 78 | SCRY_IMMEDIATELY_UNCASTABLE_TO_BOTTOM | false | true | true | true | true | no | 1 | ComputerUtil.java:2228 (scryWillMoveCardToBottomOfLibrary) | ComputerUtil.java |
| 79 | SCRY_IMMEDIATELY_UNCASTABLE_CMC_DIFF | 1 | 1 | 1 | 3 | 1 | yes | 2 | ComputerUtil.java:2229 (scryWillMoveCardToBottomOfLibrary) | ComputerUtil.java, RearrangeTopOfLibraryAi.java |
| 80 | SURVEIL_NUM_CARDS_IN_LIBRARY_TO_BAIL | 10 | 10 | 5 | 10 | 8 | yes | 1 | PlayerControllerAi.java:543 (arrangeForSurveil) | PlayerControllerAi.java |
| 81 | SURVEIL_LIFEPERC_AFTER_PAYING_LIFE | 75 | 60 | 35 | 75 | 50 | yes | 1 | SurveilAi.java:73 (checkApiLogic) | SurveilAi.java |
| 82 | COMBAT_ASSAULT_ATTACK_EVASION_PREDICTION | true | true | true | true | true | no | 1 | AiAttackController.java:625 (doAssault) | AiAttackController.java |
| 83 | COMBAT_ATTRITION_ATTACK_EVASION_PREDICTION | true | true | true | true | true | no | 1 | AiAttackController.java:879 (declareAttackers) | AiAttackController.java |
| 84 | CONSERVATIVE_ENERGY_PAYMENT_ONLY_IN_COMBAT | true | true | false | true | true | yes | 1 | CountersPutAi.java:227 (checkApiLogic) | CountersPutAi.java |
| 85 | CONSERVATIVE_ENERGY_PAYMENT_ONLY_DEFENSIVELY | true | false | false | true | false | yes | 1 | CountersPutAi.java:228 (checkApiLogic) | CountersPutAi.java |
| 86 | BOUNCE_ALL_TO_HAND_CREAT_EVAL_DIFF | 200 | 200 | 200 | 200 | 500 | yes | 1 | ChangeZoneAllAi.java:145 (canPlay) | ChangeZoneAllAi.java |
| 87 | BOUNCE_ALL_ELSEWHERE_CREAT_EVAL_DIFF | 200 | 200 | 200 | 200 | 400 | yes | 1 | ChangeZoneAllAi.java:148 (canPlay) | ChangeZoneAllAi.java |
| 88 | BOUNCE_ALL_TO_HAND_NONCREAT_EVAL_DIFF | 3 | 3 | 3 | 3 | 5 | yes | 1 | ChangeZoneAllAi.java:146 (canPlay) | ChangeZoneAllAi.java |
| 89 | BOUNCE_ALL_ELSEWHERE_NONCREAT_EVAL_DIFF | 3 | 3 | 3 | 3 | 5 | yes | 1 | ChangeZoneAllAi.java:149 (canPlay) | ChangeZoneAllAi.java |
| 90 | INTUITION_ALTERNATIVE_LOGIC | false | true | true | true | true | no | 1 | SpecialCardAi.java:973 (considerMultiple) | SpecialCardAi.java |
| 91 | EXPLORE_MAX_CMC_DIFF_TO_PUT_IN_GRAVEYARD | 2 | 2 | 1 | 2 | 2 | yes | 1 | ExploreAi.java:40 (shouldPutInGraveyard) | ExploreAi.java |
| 92 | EXPLORE_NUM_LANDS_TO_STILL_NEED_MORE | 2 | 2 | 2 | 2 | 3 | yes | 1 | ExploreAi.java:41 (shouldPutInGraveyard) | ExploreAi.java |
| 93 | MOMIR_BASIC_LAND_STRATEGY | default | default | random | preforder:RB | preforder:RB | yes | 1 | AiController.java:502 (chooseBestLandToPlay) | AiController.java |
| 94 | MOJHOSTO_NUM_LANDS_TO_ACTIVATE_JHOIRA | 5 | 4 | 3 | 5 | 4 | yes | 2 | SpecialCardAi.java:1255 (consider) | PlayAi.java, SpecialCardAi.java |
| 95 | MOJHOSTO_CHANCE_TO_PREFER_JHOIRA_OVER_MOMIR | 50 | 50 | 50 | 50 | 50 | no | 1 | SpecialCardAi.java:1254 (consider) | SpecialCardAi.java |
| 96 | MOJHOSTO_CHANCE_TO_USE_JHOIRA_COPY_INSTANT | 20 | 20 | 20 | 15 | 20 | yes | 1 | PlayAi.java:46 (checkApiLogic) | PlayAi.java |
| 97 | AI_IN_DANGER_THRESHOLD | 4 | 4 | 4 | 4 | 3 | yes | 7 | ComputerUtilCost.java:370 (checkSacrificeCost) | ComputerUtilCombat.java, ComputerUtilCost.java, EndureAi.java, LifeExchangeVariantAi.java |
| 98 | AI_IN_DANGER_MAX_THRESHOLD | 4 | 4 | 4 | 6 | 12 | yes | 2 | ComputerUtilCombat.java:444 (lifeInDanger) | ComputerUtilCombat.java, LifeExchangeVariantAi.java |
| 99 | FLASH_ENABLE_ADVANCED_LOGIC | true | true | true | true | true | no | 2 | AttachAi.java:74 (checkApiLogic) | AttachAi.java, PermanentCreatureAi.java |
| 100 | FLASH_CHANCE_TO_OBEY_AMBUSHAI | 100 | 100 | 100 | 100 | 100 | no | 1 | PermanentCreatureAi.java:132 (doAdvancedFlashLogic) | PermanentCreatureAi.java |
| 101 | FLASH_CHANCE_TO_CAST_DUE_TO_ETB_EFFECTS | 100 | 100 | 100 | 100 | 100 | no | 1 | PermanentCreatureAi.java:134 (doAdvancedFlashLogic) | PermanentCreatureAi.java |
| 102 | FLASH_CHANCE_TO_CAST_FOR_ETB_BEFORE_MAIN1 | 10 | 10 | 30 | 0 | 20 | yes | 1 | PermanentCreatureAi.java:136 (doAdvancedFlashLogic) | PermanentCreatureAi.java |
| 103 | FLASH_CHANCE_TO_RESPOND_TO_STACK_WITH_ETB | 0 | 0 | 10 | 0 | 15 | yes | 1 | PermanentCreatureAi.java:135 (doAdvancedFlashLogic) | PermanentCreatureAi.java |
| 104 | FLASH_CHANCE_TO_CAST_AS_VALUABLE_BLOCKER | 100 | 100 | 100 | 100 | 100 | no | 1 | PermanentCreatureAi.java:133 (doAdvancedFlashLogic) | PermanentCreatureAi.java |
| 105 | FLASH_USE_BUFF_AURAS_AS_COMBAT_TRICKS | true | true | true | true | true | no | 1 | AttachAi.java:96 (doAdvancedFlashAuraLogic) | AttachAi.java |
| 106 | FLASH_BUFF_AURA_CHANCE_TO_CAST_EARLY | 1 | 1 | 3 | 0 | 0 | yes | 1 | AttachAi.java:177 (doAdvancedFlashAuraLogic) | AttachAi.java |
| 107 | FLASH_BUFF_AURA_CHANCE_CAST_AT_EOT | 5 | 5 | 10 | 5 | 10 | yes | 1 | AttachAi.java:176 (doAdvancedFlashAuraLogic) | AttachAi.java |
| 108 | FLASH_BUFF_AURA_CHANCE_TO_RESPOND_TO_STACK | 100 | 100 | 100 | 100 | 100 | no | 1 | AttachAi.java:178 (doAdvancedFlashAuraLogic) | AttachAi.java |
| 109 | BLINK_RELOAD_PLANESWALKER_CHANCE | 30 | 30 | 60 | 15 | 70 | yes | 2 | ChangeZoneAi.java:1307 (canBouncePermanent) | ChangeZoneAi.java |
| 110 | BLINK_RELOAD_PLANESWALKER_MAX_LOYALTY | 2 | 2 | 2 | 2 | 2 | no | 2 | ChangeZoneAi.java:1305 (canBouncePermanent) | ChangeZoneAi.java |
| 111 | BLINK_RELOAD_PLANESWALKER_LOYALTY_DIFF | 2 | 2 | 1 | 2 | 1 | yes | 2 | ChangeZoneAi.java:1306 (canBouncePermanent) | ChangeZoneAi.java |
| 112 | SACRIFICE_DEFAULT_PREF_ENABLE | true | false | false | false | true | yes | 1 | ComputerUtil.java:350 (getCardPreference) | ComputerUtil.java |
| 113 | SACRIFICE_DEFAULT_PREF_MIN_CMC | 0 | 0 | 0 | 0 | 0 | no | 1 | ComputerUtil.java:352 (getCardPreference) | ComputerUtil.java |
| 114 | SACRIFICE_DEFAULT_PREF_MAX_CMC | 2 | 2 | 3 | 1 | 1 | yes | 1 | ComputerUtil.java:353 (getCardPreference) | ComputerUtil.java |
| 115 | SACRIFICE_DEFAULT_PREF_ALLOW_TOKENS | true | true | true | true | true | no | 1 | ComputerUtil.java:355 (getCardPreference) | ComputerUtil.java |
| 116 | SACRIFICE_DEFAULT_PREF_MAX_CREATURE_EVAL | 135 | 135 | 135 | 135 | 135 | no | 1 | ComputerUtil.java:354 (getCardPreference) | ComputerUtil.java |
| 117 | SIDEBOARDING_ENABLE | true | (not in file) | (not in file) | (not in file) | (not in file) | no | 0 | no read site (unused) |  |
| 118 | SIDEBOARDING_CHANCE_PER_CARD | 50 | 50 | 65 | 50 | 50 | yes | 1 | PlayerControllerAi.java:138 (sideboard) | PlayerControllerAi.java |
| 119 | SIDEBOARDING_CHANCE_ON_WIN | 0 | 0 | 0 | 0 | 25 | yes | 1 | PlayerControllerAi.java:137 (sideboard) | PlayerControllerAi.java |
| 120 | SIDEBOARDING_IN_LIMITED_FORMATS | false | false | false | false | false | no | 1 | PlayerControllerAi.java:134 (sideboard) | PlayerControllerAi.java |
| 121 | SIDEBOARDING_SHARED_TYPE_ONLY | false | false | false | true | true | yes | 1 | PlayerControllerAi.java:135 (sideboard) | PlayerControllerAi.java |
| 122 | SIDEBOARDING_PLANESWALKER_EQ_CREATURE | false | false | false | false | true | yes | 1 | PlayerControllerAi.java:136 (sideboard) | PlayerControllerAi.java |

Summary of section 3 (auto): 122 records; 80 differ across the four profiles; 2 have no read site (ACTIVELY_PROTECT_VS_CURSE_AURAS and SIDEBOARDING_ENABLE are set but not read by an AiProps reference in forge-ai, so they are read elsewhere or unused: not verified).

## 4. Caveats
- Read-site and method names are from grep and a regex for method signatures; not compiled or run.
- Profile summaries (section 1) are hand-written from the value tables; the behaviour statements follow the read sites in `AI_PLAY_STYLES.md` section 1.
- Nothing here changes `OPTIONS_FOR_BALANCERS.md`.

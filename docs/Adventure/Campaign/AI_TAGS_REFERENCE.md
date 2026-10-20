# Forge AI tags reference

Reference of the card-script tags the AI reads and what it does with them. Built one section per run by the forge-ai-lab agent.
Paths are relative to `forge-ai/src/main/java/forge/ai/` unless they start with `forge-`. Line numbers are valid for the commit noted per section.

Sections: 1. SpellApiToAi mapping, 2. AI:RemoveDeck flags, 3. Common SVar hints, 4. `AILogic$` values per API, 5. Fog/SwitchPT/pump behaviour from sims. Still to do: AiProps profile keys, remaining SVars, per-value semantics for big classes.

## 1. How SpellApiToAi maps ApiType to an AI class
_Checked against commit 6ee57276._

`SpellApiToAi.java:19` holds the immutable `apiToClass` map (ApiType -> `SpellAbilityAi` subclass) and `:16` the instance cache `apiToInstance`. `get(ApiType)` (`SpellApiToAi.java:226`) lazily instantiates and caches the class; an API with no entry prints `No AI assigned for API` and falls back to `CannotPlayAi` (the AI never plays it). `get(SpellAbility)` reads `sa.getApi()` and throws for non-API abilities. Most APIs map to `<Api>Ai` in `ability/`; the table groups the exceptions and the shared classes. Two special classes: `AlwaysPlayAi` (always says yes) and `CannotPlayAi` (always no, so cards using only those APIs are effectively unplayable).

| API(s) | AI class | File |
|---|---|---|
| Abandon, BlankLine, ChangeSpeed, ChangeX, ChaosEnsues, ChooseSector, ClaimThePrize, Cleanup, HealDamage, Heist, LosePerpetual, MakeCard, NoteCounters, Planeswalk, Radiation, Regeneration, RemoveFromGame, RemoveFromMatch, ReorderZone, ReplaceCounter, ReplaceEffect, ReplaceMana, ReplaceToken, ReverseTurnOrder, RingTemptsYou, RunChaos, Seek, SetInMotion, Subgame, TakeInitiative, VillainousChoice, DamageResolve, InternalRadiation | `AlwaysPlayAi` | `ability/AlwaysPlayAi.java` |
| ControlPlayer, ControlSpell, ExchangeControlVariant, GainOwnership, GameDrawn, ManaReflected, MultiplePiles, PlayLandVariant, RemoveCounterAll, InternalIgnoreEffect | `CannotPlayAi` | `ability/CannotPlayAi.java` |
| AssembleContraption, OpenAttraction | `AssembleContraptionAi` | `ability/AssembleContraptionAi.java` |
| Camouflage, ChooseCard | `ChooseCardAi` | `ability/ChooseCardAi.java` |
| Draft, NameCard | `ChooseCardNameAi` | `ability/ChooseCardNameAi.java` |
| EndCombatPhase, EndTurn | `EndTurnAi` | `ability/EndTurnAi.java` |
| Manifest, ManifestDread | `ManifestAi` | `ability/ManifestAi.java` |
| ReplaceDamage, ReplaceSplitDamage | `ReplaceDamageAi` | `ability/ReplaceDamageAi.java` |
| ActivateAbility | `ActivateAbilityAi` | `ability/ActivateAbilityAi.java` |
| AddPhase | `AddPhaseAi` | `ability/AddPhaseAi.java` |
| AddTurn | `AddTurnAi` | `ability/AddTurnAi.java` |
| AdvanceCrank | `AdvanceCrankAi` | `ability/AdvanceCrankAi.java` |
| Airbend | `AirbendAi` | `ability/AirbendAi.java` |
| AlterAttribute | `AlterAttributeAi` | `ability/AlterAttributeAi.java` |
| Amass | `AmassAi` | `ability/AmassAi.java` |
| Animate | `AnimateAi` | `ability/AnimateAi.java` |
| AnimateAll | `AnimateAllAi` | `ability/AnimateAllAi.java` |
| AssignGroup | `AssignGroupAi` | `ability/AssignGroupAi.java` |
| Attach | `AttachAi` | `ability/AttachAi.java` |
| Balance | `BalanceAi` | `ability/BalanceAi.java` |
| BecomeMonarch | `BecomeMonarchAi` | `ability/BecomeMonarchAi.java` |
| BecomesBlocked | `BecomesBlockedAi` | `ability/BecomesBlockedAi.java` |
| BidLife | `BidLifeAi` | `ability/BidLifeAi.java` |
| Blight | `BlightAi` | `ability/BlightAi.java` |
| Bond | `BondAi` | `ability/BondAi.java` |
| Branch | `BranchAi` | `ability/BranchAi.java` |
| ChangeCombatants | `ChangeCombatantsAi` | `ability/ChangeCombatantsAi.java` |
| ChangeTargets | `ChangeTargetsAi` | `ability/ChangeTargetsAi.java` |
| ChangeZone | `ChangeZoneAi` | `ability/ChangeZoneAi.java` |
| ChangeZoneAll | `ChangeZoneAllAi` | `ability/ChangeZoneAllAi.java` |
| Charm | `CharmAi` | `ability/CharmAi.java` |
| ChooseColor | `ChooseColorAi` | `ability/ChooseColorAi.java` |
| CompanionChoose | `ChooseCompanionAi` | `ability/ChooseCompanionAi.java` |
| ChooseDirection | `ChooseDirectionAi` | `ability/ChooseDirectionAi.java` |
| ChooseEvenOdd | `ChooseEvenOddAi` | `ability/ChooseEvenOddAi.java` |
| GenericChoice | `ChooseGenericAi` | `ability/ChooseGenericAi.java` |
| ChooseNumber | `ChooseNumberAi` | `ability/ChooseNumberAi.java` |
| ChoosePlayer | `ChoosePlayerAi` | `ability/ChoosePlayerAi.java` |
| ChooseSource | `ChooseSourceAi` | `ability/ChooseSourceAi.java` |
| ChooseType | `ChooseTypeAi` | `ability/ChooseTypeAi.java` |
| Clash | `ClashAi` | `ability/ClashAi.java` |
| ClassLevelUp | `ClassLevelUpAi` | `ability/ClassLevelUpAi.java` |
| Cloak | `CloakAi` | `ability/CloakAi.java` |
| Clone | `CloneAi` | `ability/CloneAi.java` |
| Connive | `ConniveAi` | `ability/ConniveAi.java` |
| ExchangeControl | `ControlExchangeAi` | `ability/ControlExchangeAi.java` |
| GainControl | `ControlGainAi` | `ability/ControlGainAi.java` |
| GainControlVariant | `ControlGainVariantAi` | `ability/ControlGainVariantAi.java` |
| CopyPermanent | `CopyPermanentAi` | `ability/CopyPermanentAi.java` |
| CopySpellAbility | `CopySpellAbilityAi` | `ability/CopySpellAbilityAi.java` |
| Counter | `CounterAi` | `ability/CounterAi.java` |
| MoveCounter | `CountersMoveAi` | `ability/CountersMoveAi.java` |
| MultiplyCounter | `CountersMultiplyAi` | `ability/CountersMultiplyAi.java` |
| Proliferate | `CountersProliferateAi` | `ability/CountersProliferateAi.java` |
| PutCounter | `CountersPutAi` | `ability/CountersPutAi.java` |
| PutCounterAll | `CountersPutAllAi` | `ability/CountersPutAllAi.java` |
| AddOrRemoveCounter | `CountersPutOrRemoveAi` | `ability/CountersPutOrRemoveAi.java` |
| RemoveCounter | `CountersRemoveAi` | `ability/CountersRemoveAi.java` |
| DamageAll | `DamageAllAi` | `ability/DamageAllAi.java` |
| DealDamage | `DamageDealAi` | `ability/DamageDealAi.java` |
| EachDamage | `DamageEachAi` | `ability/DamageEachAi.java` |
| PreventDamage | `DamagePreventAi` | `ability/DamagePreventAi.java` |
| DayTime | `DayTimeAi` | `ability/DayTimeAi.java` |
| Debuff | `DebuffAi` | `ability/DebuffAi.java` |
| DelayedTrigger | `DelayedTriggerAi` | `ability/DelayedTriggerAi.java` |
| Destroy | `DestroyAi` | `ability/DestroyAi.java` |
| DestroyAll | `DestroyAllAi` | `ability/DestroyAllAi.java` |
| Detain | `DetainAi` | `ability/DetainAi.java` |
| Dig | `DigAi` | `ability/DigAi.java` |
| DigMultiple | `DigMultipleAi` | `ability/DigMultipleAi.java` |
| DigUntil | `DigUntilAi` | `ability/DigUntilAi.java` |
| Discard | `DiscardAi` | `ability/DiscardAi.java` |
| Discover | `DiscoverAi` | `ability/DiscoverAi.java` |
| DrainMana | `DrainManaAi` | `ability/DrainManaAi.java` |
| Draw | `DrawAi` | `ability/DrawAi.java` |
| Earthbend | `EarthbendAi` | `ability/EarthbendAi.java` |
| Effect | `EffectAi` | `ability/EffectAi.java` |
| Encode | `EncodeAi` | `ability/EncodeAi.java` |
| Endure | `EndureAi` | `ability/EndureAi.java` |
| Explore | `ExploreAi` | `ability/ExploreAi.java` |
| Fight | `FightAi` | `ability/FightAi.java` |
| FlipCoin | `FlipCoinAi` | `ability/FlipCoinAi.java` |
| FlipOntoBattlefield | `FlipOntoBattlefieldAi` | `ability/FlipOntoBattlefieldAi.java` |
| Fog | `FogAi` | `ability/FogAi.java` |
| LosesGame | `GameLossAi` | `ability/GameLossAi.java` |
| WinsGame | `GameWinAi` | `ability/GameWinAi.java` |
| Goad | `GoadAi` | `ability/GoadAi.java` |
| Haunt | `HauntAi` | `ability/HauntAi.java` |
| ImmediateTrigger | `ImmediateTriggerAi` | `ability/ImmediateTriggerAi.java` |
| Investigate | `InvestigateAi` | `ability/InvestigateAi.java` |
| Learn | `LearnAi` | `ability/LearnAi.java` |
| InternalLegendaryRule | `LegendaryRuleAi` | `ability/LegendaryRuleAi.java` |
| ExchangeLife | `LifeExchangeAi` | `ability/LifeExchangeAi.java` |
| ExchangeLifeVariant | `LifeExchangeVariantAi` | `ability/LifeExchangeVariantAi.java` |
| GainLife | `LifeGainAi` | `ability/LifeGainAi.java` |
| LoseLife | `LifeLoseAi` | `ability/LifeLoseAi.java` |
| SetLife | `LifeSetAi` | `ability/LifeSetAi.java` |
| Mana | `ManaAi` | `ability/ManaAi.java` |
| Meld | `MeldAi` | `ability/MeldAi.java` |
| Mill | `MillAi` | `ability/MillAi.java` |
| MustBlock | `MustBlockAi` | `ability/MustBlockAi.java` |
| Mutate | `MutateAi` | `ability/MutateAi.java` |
| PeekAndReveal | `PeekAndRevealAi` | `ability/PeekAndRevealAi.java` |
| PermanentCreature | `PermanentCreatureAi` | `ability/PermanentCreatureAi.java` |
| PermanentNoncreature | `PermanentNoncreatureAi` | `ability/PermanentNoncreatureAi.java` |
| Phases | `PhasesAi` | `ability/PhasesAi.java` |
| Play | `PlayAi` | `ability/PlayAi.java` |
| Poison | `PoisonAi` | `ability/PoisonAi.java` |
| ExchangePower | `PowerExchangeAi` | `ability/PowerExchangeAi.java` |
| Protection | `ProtectAi` | `ability/ProtectAi.java` |
| ProtectionAll | `ProtectAllAi` | `ability/ProtectAllAi.java` |
| Pump | `PumpAi` | `ability/PumpAi.java` |
| PumpAll | `PumpAllAi` | `ability/PumpAllAi.java` |
| PutSticker | `PutStickerAi` | `ability/PutStickerAi.java` |
| RearrangeTopOfLibrary | `RearrangeTopOfLibraryAi` | `ability/RearrangeTopOfLibraryAi.java` |
| Regenerate | `RegenerateAi` | `ability/RegenerateAi.java` |
| RemoveFromCombat | `RemoveFromCombatAi` | `ability/RemoveFromCombatAi.java` |
| Repeat | `RepeatAi` | `ability/RepeatAi.java` |
| RepeatEach | `RepeatEachAi` | `ability/RepeatEachAi.java` |
| RestartGame | `RestartGameAi` | `ability/RestartGameAi.java` |
| Reveal | `RevealAi` | `ability/RevealAi.java` |
| RevealHand | `RevealHandAi` | `ability/RevealHandAi.java` |
| RollDice | `RollDiceAi` | `ability/RollDiceAi.java` |
| RollPlanarDice | `RollPlanarDiceAi` | `ability/RollPlanarDiceAi.java` |
| Sacrifice | `SacrificeAi` | `ability/SacrificeAi.java` |
| SacrificeAll | `SacrificeAllAi` | `ability/SacrificeAllAi.java` |
| Scry | `ScryAi` | `ability/ScryAi.java` |
| SetState | `SetStateAi` | `ability/SetStateAi.java` |
| Shuffle | `ShuffleAi` | `ability/ShuffleAi.java` |
| SkipPhase | `SkipPhaseAi` | `ability/SkipPhaseAi.java` |
| SkipTurn | `SkipTurnAi` | `ability/SkipTurnAi.java` |
| StoreSVar | `StoreSVarAi` | `ability/StoreSVarAi.java` |
| Surveil | `SurveilAi` | `ability/SurveilAi.java` |
| Tap | `TapAi` | `ability/TapAi.java` |
| TapAll | `TapAllAi` | `ability/TapAllAi.java` |
| TapOrUntap | `TapOrUntapAi` | `ability/TapOrUntapAi.java` |
| TapOrUntapAll | `TapOrUntapAllAi` | `ability/TapOrUntapAllAi.java` |
| TimeTravel | `TimeTravelAi` | `ability/TimeTravelAi.java` |
| Token | `TokenAi` | `ability/TokenAi.java` |
| TwoPiles | `TwoPilesAi` | `ability/TwoPilesAi.java` |
| Unattach | `UnattachAi` | `ability/UnattachAi.java` |
| UnlockDoor | `UnlockDoorAi` | `ability/UnlockDoorAi.java` |
| Untap | `UntapAi` | `ability/UntapAi.java` |
| UntapAll | `UntapAllAi` | `ability/UntapAllAi.java` |
| Venture | `VentureAi` | `ability/VentureAi.java` |
| Vote | `VoteAi` | `ability/VoteAi.java` |
| ExchangeZone | `ZoneExchangeAi` | `ability/ZoneExchangeAi.java` |
## 2. AI:RemoveDeck flags
_Checked against commit 6ee57276._

Parsed in `forge-core/src/main/java/forge/card/CardRules.java:731-735` from the script line `AI:RemoveDeck:<value>` into three booleans stored in `CardAiHints` (`forge-core/.../CardAiHints.java:17`). Accessors in `ComputerUtilCard.java:2300-2312` (`isCardRemAIDeck`, `isCardRemRandomDeck`, `isCardRemNonCommanderDeck`).

| Flag | Meaning | What the code does |
|---|---|---|
| `All` (`getRemAIDecks`) | AI does not know how to play it | **In-game:** `AiController.java:1650` removes every SpellAbility of the card from the candidate list (the card is never cast or activated); `ComputerUtilAbility.java:363` also gives -10 priority when sorting; `ControlGainAi.java:158`, `ControlExchangeAi.java:30` and `CopySpellAbilityAi.java:76` refuse to steal/exchange/copy such cards; `PlayEffect.java:145` and `CopyPermanentEffect.java:175` (forge-game) skip them when an AI picks what to play/copy. **Deck building:** `Deck.java:733` + `ComputerUtilCard.java:1127` (`AI_KNOWS_HOW_TO_PLAY_ALL_CARDS`), `CardThemedDeckGenerator.java:19`, `CardThemedDeckBuilder.java:591,805`, `CardRanker.java:78,101` exclude/penalise it; `PlayerControllerAi.java:156` never sideboards it in. |
| `Random` (`getRemRandomDecks`) | AI can play it but not in randomly generated decks | Not checked at cast time. Only excludes it from generated decks (`LimitedDeckBuilder.java:599`, `CardThemedDeckBuilder.java:592,806`) and from "fetch to steal" lists (`ability/ChangeZoneAi.java:1586`). |
| `NonCommander` (`getRemNonCommanderDecks`) | Only valid in Commander decks | `forge-core/.../DeckGeneratorBase.java:284`: kept only if the format has a commander. |

Note: `All` is a pure play ban. Several AI classes carry comments saying cards are flagged `All` until the AI can handle them (`AnimateAi.java:474`, `CloneAi.java:147`, `SacrificeAi.java:134`), and `AvailableActions.java:110` has a TODO to include them "when they weren't used". Removing the flag is the whole change needed to let the AI try a card; the API's AI class then decides.

## 3. Most-used card SVar hints
_Checked against commit 6ee57276. SVars are set in the card script as `SVar:<Name>:<value>`._

| SVar | Meaning for the AI | Code |
|---|---|---|
| `AIPreference` | Which cards/permanents to prefer for a cost or choice (`SacCost$Creature.token\|...`, `ManaFrom$Type`) | `ComputerUtil.java:284` (getCardPreference), `ComputerUtilMana.java:299` |
| `AIPreferenceOverride` | Fallback list when the preference finds nothing | `ComputerUtil.java:~290` |
| `AIPriorityModifier` | Integer added to the spell's play priority (higher = tried earlier) | `ComputerUtilAbility.java:366` |
| `PlayMain1` | Cast in main phase 1: `ALWAYS`, `OPPONENTCREATURES`, or any value (when AI controls creatures) | `ComputerUtil.java:1153`, `:1311` |
| `HasAttackEffect` | `TRUE` = attacking triggers something good, so attack even if risky; `Blocked` variant | `AiAttackController.java:277,1113,1422` |
| `HasCombatEffect` / `HasBlockEffect` | Creature has an effect when it deals combat damage / blocks; changes attack and block evaluation | `AiAttackController.java:1424,1463` |
| `MustBeBlocked` | `true` or `attackingplayer`: AI blockers prioritise blocking this attacker | `AiBlockController.java:144`, `ComputerUtilCombat.java:419` |
| `SacMe` | Value 1-5: priority as a sacrifice fodder (5 = first); also lets AI chump or trade it freely | `ComputerUtil.java:331-341`, `AiBlockController.java:243` |
| `DiscardMe` | Value = discard priority for cost/discard choices | `ComputerUtil.java:408`, `AiCostDecision.java:128`, `AiController.java:2359` |
| `DoNotDiscardIfAble` / `IsReanimatorCard` | Never discard voluntarily (reanimator targets are protected) | `AiController.java:1135,1166`, `ability/DiscardAi.java:100` |
| `EndOfTurnLeavePlay` | Permanent leaves at end of turn: free chump/trade, not worth long-term cast timing | `AiBlockController.java:246,315`, `ComputerUtil.java:1145` |
| `DestroyWhenDamaged` | Any damage kills it (treated like deathtouch in combat math) | `ComputerUtilCombat.java:1727-1761` |
| `BuffedBy` / `AntiBuffedBy` | Valid-card list that makes the card better/worse (AI weighs playing those first) | `ComputerUtil.java:1250,1281,1331,1354`, `AiController.java:1567` |
| `AIEvaluationModifier` | Integer added to the creature's board value (affects what the AI protects, removes, trades) | `CreatureEvaluator.java:297` |
| `AmbushAI` | Hold flash creature to ambush attackers; `BlockOnly` = never cast proactively | `ability/PermanentCreatureAi.java:77,110` |
| `NonStackingAttachEffect` | Don't attach a second copy to the same target | `ability/AttachAi.java:882,943,1204` |
| `MaxQuestEffect` | Cap for counter-removal costs (quest-style cards) | `AiCostDecision.java:727,736` |
| `AIPaymentPreference` | `AvoidPayingWithAttachTarget`: don't tap the equipped/enchanted creature for mana | `ComputerUtilMana.java:386` |
| `FreeSpellAI` | Sorts free spells ahead when ordering plays | `ComputerUtilAbility.java:316` |

## 4. AILogic$ values per AI class
_Checked against commit 469416d1. Mechanically extracted from `forge-ai/src/main/java/forge/ai/ability/*.java`: every string literal compared against the ability's `AILogic` param (`aiLogic.equals/startsWith/contains`, `switch`/`case`) in that class. Line numbers are in `ability/<Class>.java`; where a value is checked in several places all lines are listed. A card selects a value with `AILogic$ <Value>` on the ability line (or `SVar`-referenced sub-ability). Values with a trailing `.` are prefix checks (the number/arg follows, e.g. `MinLoyalty.3`). Many classes also read `AILogic` through shared helpers (`ComputerUtil*`, `SpellAbilityAi.checkAiLogic`), which are not listed here. Meanings are only noted where the name is not obvious; read the cited line before relying on one._

An `AILogic` value that no branch matches is ignored: the class falls through to its default heuristics (it does not make the card unplayable). `Always` / `Never` are honoured only in classes that list them below; elsewhere they do nothing. Frequent cross-class values: `Always` (skip the usual timing/target checks), `Never` (don't play), `Main1` / `Main2` / `AnyPhase` (phase restriction), `UnlessAI` (the AI pays/chooses for the `Unless` cost side), `Pump` / `Curse` (is the effect a buff for own side or a debuff for the opponent's).

| Class | Values (line numbers) |
|---|---|
| `AnimateAi` | `Attacking` (50), `EOT` (62), `BoneManCantRegenerate` (65), `Permanent` (138), `Duration` (138), `Worst` (455), `PTByCMC` (495,502) |
| `AssignGroupAi` | `FriendOrFoe` (25) |
| `AttachAi` | `Curse` (420), `AIValid` (680), `MoveTgtAura` (1313), `Unenchanted` (1318), `InstantReequipPowerBuff` (1356), `Pump` (1458), `Move` (1458) |
| `BranchAi` | `GrislySigil` (28), `BranchCounter` (31), `TgtAttacker` (34) |
| `ChangeCombatantsAi` | `WeakestOppExceptCtrl` (40) |
| `ChangeZoneAi` | `SurpriseBlock` (94), `PriorityOptionalCost` (98), `NoSameCreatureType` (111), `Pongify` (134,166), `Always` (146,223,1370), `SacAndUpgrade` (148), `SacAndRetFromGrave` (150), `Necropotence` (152), `ReanimateAll` (154), `TheScarabGod` (156), `SorinVengefulBloodlord` (158), `Intuition` (160), `MazesEnd` (164), `ReturnCastable` (173), `IfNotBuffed` (225), `SaviorOfOllenbock` (241), `AnyMainPhase` (421), `DelayedBlink` (716,998), `SurvivalOfTheFittest` (773), `Main1` (775), `BeforeCombat` (777), `MimicVat` (835), `Polymorph` (939), `Remembered` (998), `BounceOnce` (1003), `Pump` (1085), `AttachAILogic` (1085), `ExilePreference` (1551), `BounceOwnTrigger` (1553), `ConsiderRamp` (1555), `Attach` (1735), `SacWorst` (1792), `Curse` (1944), `OwnOnly` (1945), `Worst` (1946), `Random` (1947), `MostProminent` (1951), `NonLand` (1964), `NonExiled` (1968) |
| `ChangeZoneAllAi` | `DiscardAll` (39), `LivingDeath` (69), `Timetwister` (71), `RetDiscardedThisTurn` (73), `ExileGraveyards` (76), `ManifestCreatsFromGraveyard` (85), `Main1` (171), `DiscardAllAndRetExiled` (196), `.minAdv` (199,199), `.noDiscard` (200) |
| `CharmAi` | `Good` (284) |
| `ChooseCardAi` | `AtLeast1` (64), `OppPreferred` (64), `AtLeast2` (66), `BestBlocker` (66), `Clone` (68), `Never` (72), `NeedsPrevention` (74), `Ashiok` (87), `RandomNonLand` (99), `Duneblast` (101), `OwnCard` (118), `GoodCreature` (124), `NotSelf` (152) |
| `ChooseCardNameAi` | `CursedScroll` (30), `PithingNeedle` (54) |
| `ChooseColorAi` | `MostExcessOpponentControls` (53), `MostProminentInComputerDeck` (64), `HighestDevotionToColor` (77) |
| `ChooseGenericAi` | `Khans` (26), `Dragons` (26), `Pump` (28), `BestOption` (28), `Always` (34), `CombustibleGearhulk` (67), `SoulEcho` (67) |
| `ChooseNumberAi` | `SweepCreatures` (16) |
| `ChoosePlayerAi` | `Curse` (39), `Pump` (49), `BestAllyBoardPosition` (52), `MostCardsInHand` (62), `LeastCreatures` (71) |
| `ChooseSourceAi` | `NeedsPrevention` (49,102) |
| `ChooseTypeAi` | `MostProminentComputerControls` (28), `MostProminentComputerControlsOrOwns` (43), `MostProminentOppControls` (47) |
| `CloneAi` | `CloneBestCreature` (133,159), `IfDefinedCreatureIsBetter` (161) |
| `ControlExchangeAi` | `PowerStruggle` (77), `TrigTwoTargets` (82,114) |
| `ControlGainAi` | `DonateTargetPerm` (293) |
| `CopyPermanentAi` | `MomirAvatar` (30), `MimicVat` (32), `AtEOT` (34), `DuplicatePerms` (47), `Different` (129) |
| `CopySpellAbilityAi` | `CopyActivatedAbilities` (93), `Always` (118), `ChainOfSmog` (127), `ChainOfAcid` (130,153), `UnlessAI` (162), `Never` (163), `ChainOfVapor` (167) |
| `CounterAi` | `MinCMC.` (134), `NullBrooch` (214) |
| `CountersMoveAi` | `DontMoveCounterIfLethal` (193) |
| `CountersProliferateAi` | `Always` (123) |
| `CountersPutAi` | `MoveCounter` (59,284), `CrawlingBarrens` (118,286), `MarkOppCreature` (263), `CheckDFC` (279), `ChargeToBestCMC` (296,758), `ChargeToBestOppControlledCMC` (298), `TheOneRing` (300), `FromDiceRoll` (330), `NoCounterOfType` (460), `Fight` (798), `PowerDmg` (798), `TributeAILogic` (912,913), `Always` (914), `Never` (916), `CanBlockThisTurn` (918), `DontControlCreatures` (926), `OppHasCardsInHand` (928), `IsCounterUser` (1110) |
| `CountersPutAllAi` | `AtEOTOrBlock` (47) |
| `DamageAiBase` | `SelfDamage` (37), `OpponentGainLife` (69) |
| `DamageAllAi` | `DmgAllCreaturesAndPlayers` (135) |
| `DamageDealAi` | `PayEnergy` (60), `ProcRaid.` (155), `DiscardLands` (245), `DiscardCMCX` (299), `AssumeAtLeastOneTarget` (515) |
| `DelayedTriggerAi` | `Always` (19), `SpellCopy` (65,78), `NarsetRebound` (104), `SaveCreature` (140) |
| `DestroyAi` | `MinLoyalty.` (34), `.` (35), `Polymorph` (39), `Pongify` (59), `GainControl` (259) |
| `DestroyAllAi` | `FellTheMighty` (45), `Always` (59), `RaidingParty` (91) |
| `DigAi` | `PayX` (63), `PayXButSaveMana` (67,117), `MadSarkhanDigDmg` (89), `AlwaysConfirm` (195) |
| `DiscardAi` | `VolrathsShapeshifter` (42), `DiscardUncastableAndExcess` (88), `ActivationPhases` (118), `AnyPhase` (118), `AnyPhaseIfFavored` (122), `AtLeast2` (177), `UnlessAI` (220), `Never` (221) |
| `DrawAi` | `VeilOfSummer` (188), `LifeLessThan.` (190,408), `RespondToOwnActivation` (194), `ConsiderPrimary` (257), `UnlessAI` (587), `LowPriority` (589) |
| `EffectAi` | `BeginningOfOppTurn` (48,615), `KeepOppCreatsLandsTapped` (53), `RestrictBlocking` (68), `Fog` (112), `ChainVeil` (148), `SecretTunnel` (153), `WillCastCreature` (170), `Always` (174), `Main1` (176), `Main2` (181), `Evasion` (186), `RedirectSpellDamageFromPlayer` (214), `Prevent` (232), `NoGain` (249), `NonCastCreature` (284), `Fight` (300), `Pump` (302), `MakeUnblockable` (314), `Burn` (355), `YawgmothsWill` (358), `NeedCreatures` (360), `PeaceTalks` (371), `Bribe` (386), `CantRegenerate` (396), `UnlessAI` (843), `WillAttack` (844) |
| `FightAi` | `ChosenAsTgt` (49), `Always` (108), `Grothama` (118), `PowerDmg` (222) |
| `FlipCoinAi` | `PhaseOut` (21), `Bangchuckers` (25), `KillOrcs` (43) |
| `FogAi` | `SeriousDamage` (71) |
| `ImmediateTriggerAi` | `Always` (15,59), `WeakerCreature` (68) |
| `LifeGainAi` | `CriticalOnly` (39), `AnyPhase` (108) |
| `LifeLoseAi` | `AnyPhase` (133) |
| `ManaAi` | `ManaRitual` (38,74,122), `BlackLotus` (38), `Always` (40), `ManaRitualBattery.` (167), `ManaRitualBattery` (245), `ActivateOnce` (258) |
| `MillAi` | `LilianaMill` (27), `ExileAndPlayUntilEOT` (37), `ExileAndPlayOrDealDamage` (39), `TimmerianFiends` (182) |
| `MustBlockAi` | `AllowNonLethal` (26) |
| `PeekAndRevealAi` | `InstantOrSorcery` (81) |
| `PermanentAi` | `SacToReduceCost` (104) |
| `PhasesAi` | `DontPhaseOut` (139) |
| `PlayAi` | `NeedsChosenCard` (68), `ReplaySpell` (130) |
| `PumpAi` | `MoveCounter` (30,70,139), `Aristocrat` (51,76), `AristocratCounters` (53,134), `SwitchPT` (55,81), `Main1IfAble` (110), `Fight` (129,361), `PowerDmg` (129,361), `Berserk` (130), `Pummeler` (132), `GideonBlackblade` (137), `Donate` (242), `InfernoOfTheStarMounts` (245), `AnyPhase` (367), `ReplaySpell` (371,514), `PowerStruggle` (379), `HighestPower` (394), `ContinuousBonus` (394,418), `SameName` (429), `SacOneEach` (431), `Destroy` (435), `BetterCreatureThanSource` (508), `PayEnergy` (667) |
| `PumpAllAi` | `UntapCombatTrick` (36) |
| `RemoveFromCombatAi` | `RemoveBestAttacker` (19) |
| `RepeatAi` | `CopyBestCreature` (55) |
| `RevealAi` | `Kefnet` (82) |
| `RollDiceAi` | `Combat` (26), `CombatEarly` (29), `Main2` (32) |
| `SacrificeAi` | `Lethal` (140) |
| `SacrificeAllAi` | `HellionEruption` (17), `MadSarkhanDragon` (21), `ShapeAnew` (23) |
| `ScryAi` | `BrainJar` (136), `MultipleChoice` (138) |
| `ShuffleAi` | `Always` (19), `OwnMain2` (22) |
| `SkipTurnAi` | `Always` (15) |
| `TapAi` | `GoblinPolkaBand` (50), `Arena` (52) |
| `TapAllAi` | `AtLeast` (52) |
| `TokenAi` | `RandomPT` (94), `OnlyOnAlliedAttack` (298), `Curse` (367,367), `AttachAILogic` (367) |
| `UntapAi` | `PoolExtraMana` (40,427), `PreventCombatDamage` (43,404), `Never` (86), `RemoveBestAttacker` (164), `Always` (232) |

Not extracted (to do in later runs): values consumed outside `ability/` (`AiPlayDecision`/`ComputerUtil*`/`PlayerControllerAi` choice methods such as `chooseSingleCardForEffect`), and per-value semantics for the biggest classes (`ChangeZoneAi`, `PumpAi`, `EffectAi`, `CountersPutAi`).

## 5. What the AI actually does with `AILogic$ Fog`, `SwitchPT` and pump decisions
_Checked against the lab's sims (results in `tools/concordia/ai_lab/`), commit 251a07a8 and later; line numbers from the unpatched sources._

| Logic | Where | Behaviour (verified in sims) |
|---|---|---|
| `AILogic$ Fog` on an `Effect` (Thwart the Enemy, Vine Snare, Endure) | `EffectAi.java:112` delegates to `FogAi.canPlay` | Cast only in the opponent's declare blockers step when the AI's life is in danger; `FogAi.countAvailableFogs` (`:116-133`) counts only real `Fog` API spells, so Effect-based fogs are not counted when the AI reserves mana (patch 006, no measurable effect yet). |
| `AILogic$ Fog` borrowed by a non-fog (Harsh Justice, Shield Dancer) | same | Harsh Justice is legal only in declare attackers but FogAi only says yes in declare blockers: never cast. Shield Dancer's target is the best attacker among all (`EffectAi.java:136-140`), not the creature it blocks. Removing `RemoveDeck:All` is not enough for these. |
| `AILogic$ SwitchPT` (self) | `PumpAi.java:54-61` (`checkAiLogic`), `:81-85` (`checkPhaseRestrictions`) | Unpatched: any combat phase, only "not already used this turn". Sims: ~68-92 activations per 10 games, none useful (mostly in the opponent's beginning of combat). Patch 005 v3 gates on declare blockers and `ComputerUtilCard.shouldPumpCard`, giving 2-14 activations per 10 games. |
| `ComputerUtilCard.shouldPumpCard` (pump decisions generally) | `ComputerUtilCard.java:1474-1720` | Combat trickery section builds a simulated combat with the pumped creature. In the blocker branch it dropped co-blockers (patch 008); the kill check calls `ComputerUtilCombat.attackerWouldBeDestroyed` (`ComputerUtilCombat.java:696-714`), which sums the damage of the blockers present in the combat it receives. The window in which the co-blocker fix changes an answer is narrow (0 of 37 evaluations). |

Lab method note: flags removed in a scratch assets copy, equal life, 40-card decks, 10 games per arm; a cast count proves play, not good play.

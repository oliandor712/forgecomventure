# Forge AI tags reference

Reference of the card-script tags the AI reads and what it does with them. Built one section per run by the forge-ai-lab agent.
Paths are relative to `forge-ai/src/main/java/forge/ai/` unless they start with `forge-`. Line numbers are valid for the commit noted per section.

Sections: 1. SpellApiToAi mapping, 2. AI:RemoveDeck flags, 3. Common SVar hints. Still to do: `AILogic$` values per API, AiProps profile keys, remaining SVars.

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

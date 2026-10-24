# Card logic test, method B: mtgish

Main session, 2026-10-22. Research only; nothing in forge-ai or the card scripts was changed.

## Method

- Each card's English rules text is already parsed by mtgish (`i5jb/mtgish`, `data/mtgish.lines.json`, 32,849 cards). A card is reduced to the set of rule/action node names in its mtgish tree (e.g. `TriggerA`, `WhenAPermanentDies`, `CreateTokens`). Similarity between two cards is the Jaccard overlap of those sets.
- **AILogic$:** the predicted value is the AILogic$ of the most similar card that has one (1,676 of the 1,814 AILogic$ cards are in mtgish). For control cards the card itself is left out.
- **Tags:** an mtgish node predicts an existing tag when, among tier 1 pool cards with that node (at least 5), the tag appears on at least 80%. For control cards the card itself is left out.
- Sets (seed 20261022): **T** = 50 tier 1 pool cards with no AILogic$ and no ability tags (at least one A/S/T/R line); **C** = 50 control cards that have both. Same lists given to the AI lab for the Forge-syntax method.

## Results

| Measure | Result |
|---|---|
| Control cards found in mtgish | 50 of 50 |
| AILogic$ prediction, top-1 hit | 33 of 50 (66%) |
| ...when nearest card is at least 0.6 similar | 24 of 29 (83%) |
| ...when nearest card is under 0.6 similar | 9 of 21 (43%) |
| Tag prediction, micro precision | 0.82 |
| Tag prediction, micro recall | 0.51 |
| T cards found in mtgish | 50 of 50 |
| T cards with a confident AILogic$ proposal (similarity at least 0.6) | 11 of 50 |
| T cards that got any tag from the learned mapping | 13 of 50 |

Reading: when mtgish finds a close lookalike, its AILogic$ is usually right. Below 0.6 similarity treat the proposal as a lead for review, not a placement. Recall for tags is about half because the existing tags come from Forge parameters (e.g. `flying`, `haste`, `sacrifice_outlet`), and many of those have no single mtgish node behind them.

## Control set C: prediction against existing

| Card | Actual AILogic$ | Nearest card (similarity) | Its AILogic$ | Hit | Predicted tags | Actual tags |
|---|---|---|---|---|---|---|
| passenger ferry | Pump | bessie, the doctor's roadster (0.68) | Pump | Y | crew | crew |
| unburied earthcarver | AristocratCounters | legion vanguard (0.69) | Aristocrat | N | counters_plus | counters_plus, sacrifice_outlet |
| omen of the dead | BestOpportunity | corpse hauler (0.73) | AtOppEOT | N | recursion, selection | recursion, sacrifice_outlet, selection |
| creative outburst | AlwaysOnDiscard | elemental masterpiece (0.48) | AlwaysOnDiscard | Y | artifact_token, discard, selection, token_make | artifact_token, burn, discard, removal, selection, token_make |
| iron lad, diverging destiny | Main2 | dryad greenseeker (0.35) | Main2 | Y | draw, selection | draw, flying |
| inner fire | ManaRitual | brightstone ritual (0.50) | ManaRitual | Y | mana_source | mana_burst, mana_source |
| sentinel totem | ExileGraveyards | lantern of the lost (0.57) | ExileGraveyards | Y | selection | grave_hate, selection |
| underfoot underdogs | MakeUnblockable | eardrum rattler (0.69) | MakeUnblockable | Y | token_make | token_make |
| traveler's cloak | ChosenLandwalk | pentarch ward (0.57) | MostProminentInHumanDeck | N | draw | draw |
| arrester's zeal | Main1IfAble | might of old krosa (0.73) | Main1IfAble | Y | - | evasion_grant, pump_single |
| bill ferny, bree swindler | Curse | stiltzkin, moogle merchant (0.47) | DonateTargetPerm | N | artifact_token, token_make | artifact_token, token_make |
| touch of invisibility | Pump | enter the enigma (1.00) | Pump | Y | draw | draw |
| embalmer's tools | AtOppEOT | drowner of secrets (0.84) | AtOppEOT | Y | cost_reduce | cost_reduce, mill |
| rampaging geoderm | TgtAttacker | throw from the saddle (0.47) | PowerDmg | N | counters_plus | counters_plus, haste, trample |
| etchings of the chosen | MostProminentInComputerDeck | kindred boon (0.69) | MostProminentInComputerDeck | Y | - | protection_trick, sacrifice_outlet |
| terrific team-up | PowerDmg | tandem takedown (0.61) | PowerDmg | Y | cost_reduce, pump_team | cost_reduce, pump_single |
| alora, merry thief | Pump | alora, rogue companion (0.77) | Pump | Y | bounce | bounce |
| wash out | MostExcessOpponentControls | sudden demise (0.50) | MostProminentHumanCreatures | N | bounce | bounce |
| auriok replica | NeedsPrevention | protective sphere (0.60) | NeedsPrevention | Y | - | sacrifice_outlet |
| lava zombie | NeverBounceItself | horned kavu (0.64) | NeverBounceItself | Y | - | bounce |
| circle of affliction | MostProminentInHumanDeck | jeweled torque (0.64) | MostProminentInGame | N | lifegain | burn, lifegain |
| flaming gambit | WorstCard | searing blaze (0.36) | BurnCreatures | N | burn | flashback |
| subira, tulzidi caravanner | MakeUnblockable | eardrum rattler (0.75) | MakeUnblockable | Y | draw | discard, draw, haste |
| drain life | XLifeDrain | soul burn (0.67) | XLifeDrain | Y | lifegain | lifegain |
| ancestral statue | NeverBounceItself | invasive species (0.77) | NeverBounceItself | Y | - | bounce |
| cavern harpy | NeverBounceItself | silver drake (0.71) | NeverBounceItself | Y | bounce | bounce, flying |
| claim the kingdom | Pump | fabrication module (0.54) | AtOppEOT | N | counters_plus, sacrifice_outlet | counters_plus |
| hidetsugu's second rite | OppAtTenLife | chain of smog (0.44) | ChainOfSmog | N | - | burn |
| hikari, twilight guardian | IfNotBuffed | sentinel of the pearl trident (0.47) | Always | N | removal | flying |
| recoup | ReplaySpell | flashback (0.79) | ReplaySpell | Y | flashback | flashback, flashback_return |
| millstone | AtOppEOT | sands of delirium (0.65) | AtOppEOT | Y | - | mill |
| pilgrim of justice | NeedsPrevention | pilgrim of virtue (0.89) | NeedsPrevention | Y | token_make | sacrifice_outlet |
| evolutionary escalation | BoonCounterOnOppCreature | troll negotiations (0.79) | Always, Fight | N | counters_plus | counters_plus |
| torment of venom | PayUnlessCost | remorseless punishment (0.43) | PayUnlessCost | Y | counters_plus, discard | burn, shrink |
| zoyowa lava-tongue | PayUnlessCost | osseous sticktwister (0.56) | PayUnlessCost | Y | discard | deathtouch |
| timely reinforcements | PlayForSub | illuminate history (0.46) | DiscardUncastableAndExcess | N | lifegain, token_make | lifegain, token_make |
| bloodline pretender | MostProminentInComputerDeck | kindred discovery (0.59) | MostProminentInComputerDeck | Y | counters_plus | counters_plus |
| legion vanguard | Aristocrat | unburied earthcarver (0.69) | AristocratCounters | N | - | sacrifice_outlet |
| aquatic incursion | MakeUnblockable | daughter of the deep (0.63) | MakeUnblockable | Y | token_make | token_make |
| twinferno | SpellCopy | fatal frenzy (0.52) | Berserk | N | - | grant_double_strike |
| shuri, wakandan inventor | Pump | sarkhan, soul aflame (0.41) | IfDefinedCreatureIsBetter | N | clone, cost_reduce | clone, cost_reduce |
| addle | MostProminentInHumanDeck | persecute (0.65) | MostProminentInHumanDeck | Y | discard | discard |
| prism ring | MostProminentInComputerDeck | diamond mare (1.00) | MostProminentInComputerDeck | Y | lifegain | lifegain |
| ant-man's army | FoodOrTreasure | tireless provisioner (0.50) | FoodOrTreasure | Y | artifact_token, token_make | artifact_token, token_make |
| omen of the sea | BestOpportunity | omen of the forge (0.62) | BestOpportunity | Y | draw, selection | draw, sacrifice_outlet, selection |
| you look upon the tarrasque | Fog | wild instincts (0.50) | Fight | N | - | fog, protection_trick |
| ambrosia whiteheart | BounceOwnTrigger | rescuer chwinga (0.78) | BounceOwnTrigger | Y | - | bounce |
| stronghold discipline | AllPlayerLoseLife | stern judge (0.62) | AllPlayerLoseLife | Y | - | burn |
| cutthroat centurion | Aristocrat | sepulcher ghoul (0.92) | Aristocrat | Y | - | sacrifice_outlet |
| haunting apparition | Curse | lost order of jarkeld (0.55) | Curse | Y | scales:graveyard | flying, scales:graveyard |

## Test set T: where AILogic$ and tags should go

Proposal = AILogic$ of the nearest card with one. Weak = similarity under 0.6. Gaps = mtgish nodes on the card that have no learned tag and are not structural (structural = in over 8% of pool cards); each gap is a place to add an ability rule.

| Card | Proposed AILogic$ (nearest, similarity) | Confidence | Tags from mapping | Gaps (first 6) |
|---|---|---|---|---|
| straw golem | ExceptSelf (accursed centaur, 0.40) | weak | - | WhenAPlayerCastsASpell, SacrificePermanent, Opponent |
| lightning berserker | Aristocrat (bloodthrone vampire, 0.55) | weak | - | ManaCostR, Dash |
| mask of law and grace | MostProminentInHumanDeck (cho-manno's blessing, 0.33) | weak | token_make | Protection, Red, EnchantPermanent, Black, FromColor |
| whirlwind denial | BranchCounter (anticognition, 0.31) | weak | - | Unless, ActionForEachSpellAndAbility, ControllerOfSpellOrAbility, EachableSpellOrAbility, CounterSpellOrAbility, PlayerMayCost |
| blades of velis vel | Pump (ghostform, 0.44) | weak | pump_team | Changeling, HasAllCreatureTypes, Ref_TargetPermanents, CDA_Types, UptoNumberTargetPermanents |
| bombur, gentle dreamer | AtOppEOT (basalt monolith, 0.18) | weak | - | Unless, DoesntUntapDuringControllersUntap, PermanentRuleEffect, Storied, HasAnEnduringStory, PlayerPassesFilter |
| zombie musher | ExceptSelf (kjeldoran dead, 0.36) | weak | - | RegeneratePermanent, Landwalk, IsSupertype, ManaCostS |
| lost hours | MostProminentInHumanDeck (addle, 0.50) | weak | discard | TargetPlayer, PutCardInHandIntoLibraryNthFromTop, Ref_TargetPlayer, IsNonCardtype, RevealHand, AnyPlayer |
| dross scorpion | Pump (whitewater naiads, 0.52) | weak | - | Other, Or, MayAction, WhenAPermanentDies, UntapPermanent |
| gobhobbler rats | AtEOTIfNotAttacking (nantuko calmer, 0.38) | weak | - | ManaCostB, RegeneratePermanent, NumCardsInHandIs, PlayerPassesFilter, EqualTo |
| aether flash | ExceptSelf (accursed centaur, 0.45) | weak | - | Permanent, PermanentDealsDamage, Trigger_ThatPermanent |
| shriek of dread | Pump (armor of shadows, 0.75) | ok | - | Fear |
| lignify | Pump (reins of the vinesteed, 0.24) | weak | token_make | SetCreatureType, LosesAllAbilities, EnchantPermanent, SetPT |
| caparocti sunborn | Once (resonance technician, 0.52) | weak | - | WhenACreatureAttacks, Or, MayCost, Discover, CostWasPaid, IsUntapped |
| frostpeak yeti | Pump (giant koi, 0.67) | ok | - | CantBeBlocked, CreatePermanentRuleEffectUntil, ManaCostS |
| false mourning | ReplaySpell (flashback, 0.47) | weak | - | TargetGraveyardCard, Ref_TargetGraveyardCard, InAPlayersGraveyard, PutGraveyardCardOnTopOfLibrary |
| hedron rover | BounceOwnTrigger (ambrosia whiteheart, 0.67) | ok | - | - |
| thrash of raptors | Aristocrat (ahn-crop invader, 0.36) | weak | - | Trample, Other, IsCreatureType, PlayerPassesFilter, ControlsA |
| defensive stance | Pump (reins of the vinesteed, 0.38) | weak | - | EnchantPermanent |
| spidery grasp | Pump (armor of shadows, 0.77) | ok | - | Reach, UntapPermanent |
| merrow commerce | NeverBounceItself (ancestral statue, 0.43) | weak | - | AtTheBeginningOfAPlayersEndStep, UntapEachPermanent, IsCreatureType |
| halsin, emerald archdruid | EOT (woodwraith corrupter, 0.50) | weak | token_make | SimpleColorList, AddCreatureType, IsToken, AddColor, ChooseABackground, AddCardtype |
| rime transfusion | Pump (kjeldoran pride, 0.43) | weak | restrict | IsSupertype, CreatePermanentRuleEffectUntil, EnchantPermanent, ManaCostS |
| crumble to dust | Always, SameName (declaration in stone, 0.44) | weak | - | Devoid, Permanent, SearchPlayersLibraryAndGraveyardAndHand, ExileFoundCards, Exile, FindAnyNumberOfCardsOfType |
| dragon engine | SwitchPT (myr quadropod, 0.78) | ok | - | - |
| split-tail miko | MakeUnblockable (jhessian balmgiver, 0.55) | weak | - | ManaCostW, PreventThatDamage, TapPermanent, CreateFuturePreventDamage, NextAmountOfDamageThatWouldBeDealtThisTurnToRecipient, Ref_AnyTarget |
| tangle kelp | ExceptSelf (accursed centaur, 0.38) | weak | - | ItsController, DoesntUntapDuringControllersUntap, AttackedDuringLastPlayersTurn, PermanentPassesFilter, PermanentRuleEffect, TapPermanent |
| abandon reason | Pump (ghostform, 0.44) | weak | pump_team | ManaCostR, Madness, Ref_TargetPermanents, FirstStrike, NumberTargetPermanents |
| zada, hedron grinder | Always (geist of regret, 0.50) | weak | - | Other, Or, WhenAPlayerCastsASpell, CopySpellForEachPermanentAndMustChooseItAsNewTarget, TargetsOnlySinglePermanent, Trigger_ThatSpell |
| berg strider | Pump (whitewater naiads, 0.50) | weak | - | Or, TapPermanent, EnteringPermanentPassesFilter, PermanentDoesntUntapDuringControllersNextUntap, SnowManaWasSpentToCastIt, Opponent |
| relentless pursuit | Worst (steam augury, 0.45) | weak | selection | MayPutMultipleCardsOfTypeIntoHand |
| cogwork archivist | ExileGraveyards (crook of condemnation, 0.65) | ok | - | TargetGraveyardCard, AnyCardInAnyGraveyard, PutGraveyardCardOnBottomOfLibrary, Ref_TargetGraveyardCard, TapPermanent, Reach |
| spike-tailed ceratops | AristocratCounters (carrion feeder, 0.18) | weak | - | PermanentRuleEffect, CanBlockAnAdditionalCreature |
| frozen in ice | ChosenLandwalk (traveler's cloak, 0.45) | weak | - | PermanentRuleEffect, TapPermanent, LosesAllAbilities, EnchantPermanent, CantBecomeUntapped |
| mordenkainen's polymorph | Pump (armor of shadows, 0.60) | ok | token_make | SetCreatureType, SetPT |
| captain america, living legend | PoolExtraMana (stone-seeder hierophant, 0.40) | weak | - | WhenAPermanentBecomesTappedForTheFirstTimeEachTurn, UntapPermanent, Trigger_ThatPermanent, Vigilance, IsPlayersTurn |
| avalanche caller | Always (nissa, vital force, 0.53) | weak | token_make | SetCreatureType, AddCardtype, IsSupertype, SetPT, Hexproof, Haste |
| doomfall | KeepOppCreatsLandsTapped (exhaustion, 0.53) | weak | - | TargetPlayer, Modal_ChooseOne, RevealHandAndPlayerChoosesACardToExile, Exile, APermanent, Ref_TargetPlayer |
| compass gnome | ConsiderRamp (treefolk harbinger, 0.78) | ok | land_tutor | Or, IsSupertype, MayAction, SetAsideFoundCards, IsLandType, Shuffle |
| port inspector | ExceptSelf (accursed centaur, 0.36) | weak | - | Trigger_DefendingPlayer, MayAction, LookAtPlayersHand, WhenACreatureBecomesBlocked |
| bind the monster | Curse (steam vines, 0.41) | weak | - | DoesntUntapDuringControllersUntap, Player, TapPermanent, PermanentRuleEffect, PermanentDealsDamage, EnchantPermanent |
| chain of silence | ChainOfAcid (chain of acid, 0.45) | weak | - | SacrificeAPermanent, PlayerMayAction, DamageWouldBeDealtByPermanent, PreventThatDamage, PlayerMayCost, CostWasPaid |
| way of the necromancer | NeverBounceItself (whitemane lion, 0.56) | weak | counters_plus | EmpowerJace, WhenAPermanentDies |
| phyrexian ironfoot | AtOppEOT (basalt monolith, 0.62) | ok | - | DoesntUntapDuringControllersUntap, PermanentRuleEffect, UntapPermanent, ManaCostS |
| wild swing | Pump (ghostform, 0.50) | weak | - | DestroyAPermanentAtRandom, Ref_TargetPermanents, IsNonCardtype, NumberTargetPermanents |
| prakhata pillar-bug | BoneManCantRegenerate (bone shaman, 0.57) | weak | - | Lifelink, ManaCostB |
| kozilek's pathfinder | AllowNonLethal (tangle angler, 0.67) | ok | restrict | CreatePermanentRuleEffectUntil, ManaCostC |
| briar patch | BounceOwnTrigger (ambrosia whiteheart, 0.40) | weak | - | WhenACreatureAttacksAPlayer, Trigger_ThatCreature |
| death ward | Pump (infiltrate, 0.60) | ok | - | RegeneratePermanent |
| speedball, new warrior | Aristocrat (bloodthrone vampire, 0.36) | weak | - | TargetsPermanent, WhenAPlayerCastsASpell, Trigger_ThatSpell, ChooseNewTargetsForSpell, AnyPlayer |

## Gap summary (T set)

Most common non-structural mtgish nodes with no tag: `EnchantPermanent` (7 cards), `PermanentRuleEffect` (6), `TapPermanent` (6), `Or` (5), `Opponent` (4), `DoesntUntapDuringControllersUntap` (4), `UntapPermanent` (4), `SetPT` (4). These point at missing rules for tap-down/lock auras, creature-reshaping auras, untap effects and regeneration, none of which `ability_tags.py` tags today.

## Caveats

- Nearest-neighbour on rule nodes ignores costs and values, so two cards with the same shape but different timing can get the same AILogic$ wrongly (e.g. Hikari matched an `Always` card).
- The Forge-syntax result (method A, AI lab) is separate; the combined report compares them.
- 33 of 50 is one sample; do not read it as an accuracy figure for the whole pool.

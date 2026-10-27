# Forge AI and the Odric case

All paths are relative to `/home/user/forgecomventure`. I read the code for this report and changed nothing. The fork has not touched `forge-ai`, `forge-game`, `forge-core`, `forge-gui/res/cardsfolder` or `forge-gui/res/ai` since the first Concordia commit (`git diff 208b8295^ HEAD` over those paths is empty).

## Summary

- There are four Odric cards (plus "Crusader of Odric" and "Odric's Outrider"). **Only "Odric, Master Tactician" is flagged**: `forge-gui/res/cardsfolder/o/odric_master_tactician.txt:9` reads `AI:RemoveDeck:All`. "Odric, Lunarch Marshal" and "Odric, Blood-Cursed" have no flag, and Lunarch Marshal is already a Concordia commander (`forge-gui/res/adventure/Concordia/world/commanders.json:15`).
- Master Tactician's ability works through a `DeclaresBlockers$ You` static, which hands the *defender's* block declaration to Odric's controller. When that controller is the AI, `AiController.declareBlockersFor` builds an `AiBlockController` **for the defender** and blocks in the defender's interest (`forge-ai/src/main/java/forge/ai/AiController.java:1326-1337`). In effect the AI makes the best blocks it can *for its opponent*. The attack AI also doesn't know the trigger exists, so it never sets up the "Odric plus 3 attackers" condition on purpose.
- The `RemoveDeck:All` flag does more than strip the card from decks. It also stops the AI from **casting or activating** the card at all (`AiController.java:1650`) and lowers its priority (`ComputerUtilAbility.java:363`).
- A fix that stays in forge-ai only is feasible and small. In `declareBlockersFor`, when `player.isOpponentOf(defender)`, make only the blocks the rules require and leave the rest unblocked. That is about 20-40 lines, low risk, and it also fixes the unflagged Brutal Hordechief and Berserker's Frenzy. Making the attack AI use the trigger on purpose is a medium-sized job in `AiAttackController`.
- A card-script change alone (deleting line 9) would let the AI cast Odric as a 3/4 first striker. The ability would then do roughly nothing: it wouldn't hurt the AI, but it wouldn't help it either. That edit has to be made in `forge-gui/res/cardsfolder` (upstream data), not in forge-ai.

## How Forge's AI works

### Entry points
- `PlayerControllerAi` (forge-ai) implements the game engine's `PlayerController` interface. Each engine call ("choose a spell to play", "declare attackers/blockers", "choose targets", "play this trigger") is forwarded to the `AiController` it holds as `brains`. For example, `declareAttackers` maps to `brains.declareAttackers` and `declareBlockers` maps to `brains.declareBlockersFor` (`PlayerControllerAi.java:839-846`). Triggers go through `playTrigger` (`:1394`), which calls `prepareSingleSa`/`doTrigger`. Targets for engine-driven choices come from `chooseTargetsFor` (`:1416`), which is `brains.doTrigger(sa, true)`.
- **Main priority loop.** `AiController.chooseSpellAbilityToPlay` (`AiController.java:1419`) runs `getSpellAbilityToPlay` (`:1596`). That method collects the available cards and their spell abilities, checks counterspells first (`:1635-1641`), removes land abilities and anything whose host card has `AI:RemoveDeck:All` (`:1647-1651`), and sorts the rest with `ComputerUtilAbility.saEvaluator` (best first, `:1673`). It then calls `canPlayAndPayFor` → `canPlaySa` on each in order and takes the first one that returns `WillPlay`. The search runs under a timeout, `AITimeoutTracker`.
- `canPlaySa` (`AiController.java:892`) checks AI-specific restrictions, timing and buyback. For API-based abilities it then calls `SpellApiToAi.Converter.get(sa).canPlayWithSubs(player, sa)` (`:924`), and after that the restriction and side-effect checks (`saSideEffects`, `:983`).

### Per-effect AI: SpellApiToAi and SpellAbilityAi
- Each card ability has an `ApiType`, taken from `SP$`/`AB$`/`DB$ <Api>` in the script. `SpellApiToAi` (`forge-ai/src/main/java/forge/ai/SpellApiToAi.java`) is a static `EnumMap` from `ApiType` to a `SpellAbilityAi` subclass in `forge/ai/ability` (154 files). For example, `Effect → EffectAi` (`:92`), `Pump → PumpAi`, `PumpAll → PumpAllAi` (`:151-152`). An API with no mapping logs "No AI assigned for API" and falls back to `CannotPlayAi` (`:243-246`).
- `SpellAbilityAi` is a template:
  - `canPlayWithSubs` (`SpellAbilityAi.java:56`) → `canPlay` → `canPlayWithoutRestrict` (`:81`). That method runs `checkAiLogic` if the script has `AILogic$`, otherwise `checkPhaseRestrictions`. It then calls **`checkApiLogic`**, the per-API override that also *chooses targets* by filling `sa.getTargets()`. Finally it checks `willPayCosts` and `checkConditions`.
  - Sub-abilities (the `SubAbility$` chain) go through `chkDrawbackWithSubs`/`chkDrawback` (`:269-299`). In the base class, a targeted sub-ability returns `CantPlayAi` and prints a warning unless the subclass overrides it.
  - Triggers: `doTrigger` (`:180`) → `doTriggerNoCostWithSubs` (`:193`) → `doTriggerNoCost` (`:229`). The default tries the normal play logic. When the trigger is mandatory it falls back to picking *some* legal target: opponents, then allies, then itself.
- `AiPlayDecision` (`AiPlayDecision.java`) is the result enum. It covers play reasons (`WillPlay`, `ImpactCombat`, …), "later" reasons (`WaitForMain2`, `AnotherTime`, …) and refusals (`CantPlayAi`, `TargetingFailed`, `MissingLogic`, …). `AiAbilityDecision` wraps it together with a 0-100 rating.
- The `ComputerUtil*` classes are shared helpers. `ComputerUtil` covers general play, haste and fog checks, and life-in-danger. `ComputerUtilCard` covers creature evaluation, best/worst card choice and the `isCardRemAIDeck` helpers (`:2302`). `ComputerUtilCombat` predicts damage, toughness bonuses and lethality. `ComputerUtilMana` and `ComputerUtilCost` handle paying costs. `ComputerUtilAbility` sorts spell abilities (`saEvaluator`, `:350-375`). `SpecialCardAi` and `SpecialAiLogic` hold hand-written per-card logic, selected by `AILogic$` names.

### Combat
- **Attacking.** `AiAttackController.declareAttackers` (`AiAttackController.java:811`) works out an aggression level from 0 to 6 (`:1054-1296`). The inputs are the life and creature race, the `PLAY_AGGRO` and `CHANCE_TO_ATTACK_INTO_TRADE`-style profile properties, and the opponent's blocks predicted with an `AiBlockController(defender, true)`. `notNeededAsBlockers` (`:341`) keeps back enough defenders. `isEffectiveAttacker` (`:270`) accepts a creature that damages or poisons if unblocked, or that carries the card hint `SVar:HasAttackEffect:TRUE` (`:277`).
- **Blocking.** `AiBlockController.assignBlockersForCombat` (`AiBlockController.java:1013/1074`) → `assignBlockers` (`:1115`). This runs a fixed pipeline from the point of view of `ai`, the player passed to the constructor (`:78`): remove unblockable attackers, then `makeGoodBlocks` (`:189`), `makeTradeBlocks` (`:607`), `makeChumpBlocks` when life is in danger (`:643`), `makeRequiredBlocks` (`:967`), and finally the validity cleanup. The `checkingOther` flag (`:76`) only stops the AI from using hidden information (`:1153`, `:1416`).

### AI profiles (AiProps)
- `forge-gui/res/ai/{Default,Cautious,Reckless,Experimental}.ai` are `KEY=value` files of roughly 327 lines each. `AiProps.java` defines every key and its default. `AiProfileUtil.loadAllProfiles` loads every `*.ai` file in the directory (`AiProfileUtil.java:82`, called from `FModel.java:276`). `getProperty` falls back to the enum default (`:117-125`).
- Reckless differs from Default mainly in `PLAY_AGGRO=true`, `CHANCE_TO_ATTACK_INTO_TRADE=100`, `ATTACK_INTO_TRADE_WHEN_TAPPED_OUT=true`, lower trade-on-block chances and `MULLIGAN_THRESHOLD=3`. Experimental changes planeswalker protection, danger thresholds and equipment moves.
- In Adventure, `DuelScene` passes `selectAI(currentEnemy.ai)` to `GamePlayerUtil.createAiPlayer` (`forge-gui-mobile/src/forge/adventure/scene/DuelScene.java:511`). `selectAI` (`:906-918`) **only knows the four built-in names**. Anything else, including `""`, means "use the user's preference" (`GamePlayerUtil.java:76-90`, pref `UI_CURRENT_AI_PROFILE`). All 35 Concordia enemies use `"ai": ""` (`forge-gui/res/adventure/Concordia/world/enemies.json`).

### AI:RemoveDeck hints
- These are parsed in `forge-core/src/main/java/forge/card/CardRules.java:731-735` into `CardAiHints` (`All` → `getRemAIDecks`, `Random` → `getRemRandomDecks`, plus `NonCommander`). 2,479 card files have `RemoveDeck:All` and 2,382 have `RemoveDeck:Random`.
- **Deck building and generation:** `CardRulesPredicates.IS_KEPT_IN_AI_DECKS` (`forge-core/.../CardRulesPredicates.java:24`), `CardThemedDeckBuilder.java:591,805`, `CardThemedDeckGenerator.java:19`, the warning in `Deck.java:733`, and AI sideboarding (`PlayerControllerAi.java:156`).
- **Adventure:** `DuelScene.isAiUnplayable`/`withoutAiUnplayableCards` (`DuelScene.java:625-650`) strips both `All` and `Random` cards and refills with basics when `ConfigData.stripAiUnplayableCards` is set (`ConfigData.java:44`). `RewardData.java:151` also reads the hint. The project's own tool reads the flags as well (`tools/concordia/power_scorer.py:97,359`; `tools/concordia/deckgen/build.py:9`).
- **In play:** the AI refuses to play any spell ability of a `RemoveDeck:All` card (`AiController.java:1650`), gives it -10 priority (`ComputerUtilAbility.java:363`), and avoids stealing, copying or fetching such cards (`ControlGainAi.java:158`, `CopyPermanentAi.java:141`, `ChangeZoneAi.java:1586`, and others).

## Case study: Odric

| Card | File | Abilities | AI flags |
|---|---|---|---|
| Odric, Lunarch Marshal | `o/odric_lunarch_marshal.txt:5-6` | Beginning-of-combat trigger → `DB$ PumpAll`, `ValidCards$ Creature.YouCtrl`, 13 keywords with `SharedKeywordsZone$ Battlefield`/`SharedRestrictions$` (only the keywords already present among your creatures are granted) | none |
| Odric, Blood-Cursed | `o/odric_blood_cursed.txt:5-9` | ETB `DB$ Token`, X Blood tokens, X = `Count$AbilityYouCtrl …`; `SVar:BuffedBy` deck hint | none |
| Odric, Master Tactician | `o/odric_master_tactician.txt:5-9` | First strike; `Mode$ Attacks`, `IsPresent$ Creature.attacking+Other PresentCompare$ GE3` → `DB$ Effect` with static `DeclaresBlockers$ You` until end of combat | **`AI:RemoveDeck:All`** (line 9) |
| Odric's Outrider | `o/odrics_outrider.txt` | dies trigger → PutCounter | none |

**Lunarch Marshal is fine for the AI.** The trigger is mandatory, and `PumpAllAi.doTriggerNoCost` accepts any untargeted, non-curse `ValidCards …YouCtrl` pump (`ability/PumpAllAi.java:142-146`). Keyword sharing happens in the engine (`forge-game/.../CardFactoryUtil.java:408`). Because it resolves at the start of combat, before attackers are declared, the attack AI sees the granted keywords. `ComputerUtil.hasACardGivingHaste` even special-cases it (`ComputerUtil.java:1428-1432`). Blood-Cursed is a plain ETB token trigger.

**Why Master Tactician is unplayable:**
1. **The trigger resolves, but it is pointless for the AI.** `ApiType.Effect` → `EffectAi`. With no `AILogic`, `checkApiLogic` returns `CantPlayAi` (`ability/EffectAi.java:598-600`). The trigger is mandatory, though, so `SpellAbilityAi.doTriggerNoCost` falls through and the effect is created (`SpellAbilityAi.java:229-240`). The static then sets `defender.getDeclaresBlockers() = Odric's controller` (`forge-game/.../StaticAbilityContinuous.java:585-588`).
2. **The AI then blocks for the wrong side.** At declare-blockers the engine calls `whoDeclaresBlockers.getController().declareBlockers(defender, combat)` (`forge-game/.../phase/PhaseHandler.java:663-679`, commented "Apply Odric's effect here"). `AiController.declareBlockersFor` does `new AiBlockController(defender, defender != player)` and `block.assignBlockersForCombat(combat)` (`AiController.java:1326-1337`). The comment there says "When player != defender, AI should declare blockers for its benefit", but `AiBlockController` uses the *defender* as `ai` throughout (`AiBlockController.java:78-80`). It makes good blocks, trades and chumps to protect the defender's life. The defender's blocks end up about as good as if Odric weren't there, and sometimes better than what a human would choose. What the Odric player actually wants (no blocks, or only blocks that kill the defender's creatures for free) is never considered.
3. **The attack AI doesn't know about it.** `AiAttackController` has no reference to `DeclaresBlockers` or to Odric (grep finds nothing). Its block prediction (`AiBlockController(defender, true)`) assumes normal blocks, so it never pushes all-out with Odric plus 3 other creatures to make the whole team effectively unblockable. Master Tactician lacks even the `HasAttackEffect` hint.
4. **The flag blocks the rest.** With `RemoveDeck:All`, the AI won't cast the card from hand or from the command zone (`AiController.java:1650`). An Odric commander would just sit there, which is why stripping it was correct.

Melee and Master Warcraft (both `RemoveDeck:All`) and Invasion Plans (`RemoveDeck:Random`) use the same static. Brutal Hordechief (`b/brutal_hordechief.txt:10`) and Berserker's Frenzy are **not** flagged and already have the bug from point 2 when the AI uses them.

## Options to improve

### A. Card script only (`forge-gui/res/cardsfolder`): remove line 9, optionally add `SVar:HasAttackEffect:TRUE`
- Effect: the AI casts Odric and attacks with it like a normal first-strike 3/4. Through bug 2, the trigger produces blocks that are about neutral (the defender's own AI-quality blocks), so the AI loses no value but gains none from the ability. `HasAttackEffect:TRUE` would make it attack even when it can't deal damage, which is a mild risk.
- No `AILogic$`/`AIPreference` hint can fix the blocking, because the decision is made in `declareBlockersFor` and not in any `SpellAbilityAi`.
- Effort: 5 minutes. Risk: low. It changes upstream card data, which merges are likely to overwrite or conflict with.

### B. forge-ai only: blocks chosen by the opponent (recommended code fix)
- In `AiController.declareBlockersFor` (`AiController.java:1326`), branch when `defender != player && player.isOpponentOf(defender)`. Add a new public method in `AiBlockController`, for example `assignBlocksAsOpponent(combat)`:
  1. Clear the defender's blockers.
  2. Make only the blocks the rules require. Reuse the `makeRequiredBlocks` logic, which `completeRequiredBlocks` already exposes (`AiBlockController.java:1022-1057`), but drop its "life in danger → chump" step, since that protects the defender. This keeps Lure/"must block" legal, which matters for Brutal Hordechief's `MustBlock`.
  3. Optionally add "free kill" blocks: assign a defender creature to an attacker that destroys it without dying. `ComputerUtilCombat.canDestroyBlocker` / `canDestroyAttacker` already do the maths. Only do this when the AI isn't already lethal on damage.
  4. Run `removeIllegalBlocks` (`:1060`).
- It also improves Brutal Hordechief and Berserker's Frenzy immediately, and makes Melee, Master Warcraft and Invasion Plans viable.
- Effort: about 0.5-1 day including a test with forge-gui-desktop or the sim harness. Risk: low, because the branch is only taken when someone else's blocks are delegated to the AI. Only forge-ai changes. This would be the fork's first forge-ai change, but it is a self-contained patch that could go upstream.

### C. forge-ai only: make the attack AI use the trigger
- In `AiAttackController.declareAttackers`/aggression (`AiAttackController.java:811`, `:1250-1296`): if the AI controls an untapped creature with an `Attacks` trigger whose effect grants `DeclaresBlockers` to its controller, and it has 3 or more other able attackers, evaluate the attack with no blockers predicted (for example by forcing aggression 5 and treating the attackers as unblocked for `notNeededAsBlockers`), then commit to Odric plus 3 or more.
- The detection could be generic (scan the trigger's `Execute` SVar for an `Effect` whose static has `DeclaresBlockers`), or it could use a new card hint such as `SVar:AIAttackEnablesBlockControl` read by the controller. Effort: about 1-3 days. Risk: medium, because the aggression code is delicate and shared by every attack. Only forge-ai changes, plus an optional one-line hint in the card script.

### D. General AI improvements for the project (no code in core, game or ai)
1. **Per-enemy profiles:** set `"ai": "Reckless" | "Cautious" | "Experimental"` per enemy in `Concordia/world/enemies.json`. Effort: about 1 hour of data work. Aggro decks benefit most from Reckless.
2. **Custom profiles, for example `ConcordiaAggro.ai`:** these load automatically from `res/ai` (`AiProfileUtil.java:82`), but `DuelScene.selectAI` (`forge-gui-mobile`, `:906-918`) whitelists the four names. Extend it to accept any name in `AiProfileUtil.getAvailableProfiles()`: about 10 lines in forge-gui-mobile, which the fork already edits, plus about 1-2 hours tuning `AiProps`.
3. **Card hints in decks:** prefer cards with `AILogic$` (1,814 card files have one) and `AIPreference` (250). Avoid `RemoveDeck:Random` cards in hand-built decks; the deckgen tool already flags them (`power_scorer.py:359`).
4. **Simulation AI** (`AIOption.USE_SIMULATION`/hybrid, `forge/ai/simulation/*`): it is stronger in some spots but slow and less well tested. It is not advisable for mobile Adventure.
5. **forge-ai fixes like option B** for other recurring problem cards. Effort is roughly 0.5-2 days each, and each one means maintaining a fork patch against upstream merges.

## Recommendation
1. Keep Master Tactician out for now. The strip is correct, because with the flag the AI can't cast it at all, and without code changes the ability does nothing for the AI.
2. If Odric, Master Tactician is wanted as an enemy commander, do **B** (a small, safe forge-ai-only patch in `AiController.declareBlockersFor` plus a helper in `AiBlockController`) and **A** (remove the `AI:RemoveDeck:All` line). The AI then gets value whenever the trigger fires incidentally. Add **C** only if Odric should be a featured boss, since that part carries the risk.
3. For general difficulty, the cheapest lever is **D1/D2**: per-enemy profiles, and widening `selectAI` to allow custom `.ai` files. That stays inside data and forge-gui-mobile, which fits the "don't touch core, game or ai" constraint.

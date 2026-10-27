# Cards Forge flags as unplayable for the AI: clusters, gaps, fixes

Paths are relative to the repository root. The analysis was a read-only pass over the card scripts and the AI code; the one-off scripts it used aren't kept in the repository.

## Audit

This report was re-checked after it was written:

- **Counts verified exactly** against the card scripts: 34,088 scripts, 2,479 `All`, 2,382 `Random`, 250 both, 2,132 `Random` only, 70 `NonCommander`.
- **Code references verified** at the cited lines: `EffectAi` (521-523, 598-599), `PumpAi` (348-352), `AnimateAi` (472-476), `AnimateAllAi` (27-29), `ChangeTargetsAi` (25-35), `RepeatEachAi` (101-103), the Choose\* AIs, `ComputerUtilAbility` (362-363), `SpellApiToAi` (71, 100, 126, 161), `OnePlaySafetyChecker` and its single use at `AiController.java:988`, and `SACRIFICE_DEFAULT_PREF_ENABLE` in `Default.ai`/`Experimental.ai`.
- **Corrections made:**
  - The Choose\* breakdown under improvement 2 listed ChoosePlayer among the cards the fix would free. ChoosePlayer is the opposite problem (it always plays), so it's removed; the 87 are ChooseType/Color/Number 55, NameCard 23 and GenericChoice 9.
  - Improvement 3's heading said "200+"; its own estimate, 100-200, is now used throughout.
  - Improvement 7 gave RepeatEach as 69 cards and the dead-default table as 38: 69 flagged cards use RepeatEach somewhere, and about 40 use it as their main ability. Both numbers are now named.
  - `ChangeTargetsAi` does play mandatory activations (triggers); it refuses only optional ones. Noted below.
  - Rhystic Shield appeared both as an opponent's-choice punisher and as "looks playable". Its main ability is a plain `PumpAll`, so it stays in the stale list; the punisher cluster now uses other examples.
- **Done since:** improvement 0 (Adventure strips only `RemoveDeck:All`) is in, with the deck pool and all 100 tier decks rebuilt.

## Summary

| | Cards |
|---|---|
| Card scripts scanned (`forge-gui/res/cardsfolder/**/*.txt`) | 34,088 |
| `AI:RemoveDeck:All` | **2,479** (7.3%) |
| `AI:RemoveDeck:Random` | **2,382** (7.0%) |
| Both flags | 250 |
| Either flag | 4,611 |
| `Random` only | 2,132 |
| (`AI:RemoveDeck:NonCommander`, not in scope) | 70 |

The two flags do different jobs. **That difference is the biggest finding.**

- **`All` changes how the AI plays.** `AiController.getSpellAbilityToPlay` drops every spell ability whose host card has `RemoveDeck:All` (`forge-ai/src/main/java/forge/ai/AiController.java:1647-1651`, which carries a "TODO allow when experimental profile?" note), and `ComputerUtilAbility.java:362-363` gives such cards -10 priority. In game, an `All` card is a dead card.
- **`Random` never changes in-game play.** It is read only by deck builders and generators: `CardThemedDeckBuilder.java:592,806`, `LimitedDeckBuilder.java:599`, `CardRulesPredicates.java:26`, the Vanguard pickers, and a tutor filter at `ChangeZoneAi.java:1586`. The AI plays these cards normally. They are build-around, tribal or snow cards, situational cards and drawback cards, and 467 of the 2,132 `Random`-only cards carry `DeckHints`/`DeckNeeds`.
- **Adventure used to strip both flags.** `DuelScene.isAiUnplayable` checked `getRemAIDecks() || getRemRandomDecks()`, and Concordia turns stripping on (`stripAiUnplayableCards` in `forge-gui/res/adventure/Concordia/config.json`), so 2,132 cards the AI can play were removed from AI decks for no AI reason. **Fixed:** it now checks only `getRemAIDecks()` (improvement 0).

About the `All` flags:

- **They are mostly legacy.** The flag rate falls with the year a card was first printed (taken from `forge-gui/res/editions`):

  | First printed | `All` | `Random` |
  |---|---|---|
  | 2003 or earlier | 14.8% | 13.2% |
  | 2004-2012 | 12.3% | 11.2% |
  | 2013-2019 | 5.1% | 5.2% |
  | 2020 or later | 0.8% | 1.6% |

- **There are three kinds of `All` flag:**
  1. **A real "dead default" in an AI class (424 cards, 17%).** The card's main ability uses an API whose AI returns `CantPlayAi` or `MissingLogic` whenever there is no `AILogic$`. The biggest of these are `EffectAi` (148), `PumpAi` used as a target carrier (71), Choose\*/NameCard/GenericChoice heads (87), targeted non-creature Animate (43) and `AnimateAll` (24). The same dead defaults also silently disable 560 *unflagged* cards' abilities.
  2. **Strategic or build-around cards (about 45%).** These are static- or trigger-only permanents with drawbacks or symmetric effects, combat-step tricks, odd non-mana costs, and library or graveyard shuffling with no immediate value. The AI would cast them, but it doesn't know they are bad for it, so the flag acts as a quality filter. These are hard to fix in general.
  3. **Probably stale flags.**
     - 117 `All` cards already have an `AILogic$` on their main ability.
     - In a hand-checked sample of 34 simple scripts, **about half (17)** look playable with today's AI.
     - Flagging is inconsistent: Samite Healer is unflagged, but Barrenton Medic and Martyrs' Tomb, which use the same `PreventDamage` AI, are flagged.
     - The estimate is **300-450 stale `All` flags**.

## Method

1. **Parsing.** Every card script was parsed, recording:
   - ApiTypes from `AB$`/`SP$`/`DB$` on `A:`, `T:` and `SVar:` lines
   - trigger modes (`T:` and trigger SVars)
   - static modes (`S:`)
   - replacement events (`R:` and `Event$` SVars)
   - keywords (`K:`), types and `AILogic$` values
   - about 50 Oracle-text regex patterns (choose, vote, each player, X, sacrifice, copy, exchange control, coin, monarch, and others)

   Each flagged card's `A:` lines with their cost string, `AILogic` and parameters were then extracted. Those lines are the abilities the AI actually decides to play.
2. **Feature rates.** For every feature: the count of `All` cards, the count of `Random` cards, the total number of cards with the feature, and the flag rate. The rate shows which features are over-represented.
3. **Feature clusters.** Each flagged card was assigned to every feature cluster it matches (multi-label).
4. **Dead defaults.** Code-confirmed dead defaults were tagged: the API plus the missing `AILogic` maps to a `return CantPlayAi/MissingLogic` in the AI class. It covers all 34k cards, not only flagged ones.
5. **Reading the code.** The relevant classes were read in `forge-ai/src/main/java/forge/ai/` (`SpellApiToAi`, `EffectAi`, `PumpAi`/`PumpAiBase`, the Choose\* AIs, `AnimateAi`/`AnimateAllAi`, `ChangeTargetsAi`, `UntapAllAi`, `RepeatEachAi`, `ChoosePlayerAi`, `DamagePreventAi`, `ChooseSourceAi`, `ComputerUtilCost`/`ComputerUtil.getCardPreference`, `AiCostDecision`, `OnePlaySafetyChecker`).
6. **Stale-flag sample.** 34 sampled `All` cards with a single simple `A:` ability (from a pool of 627) were judged by hand against the code.

The clusters come from regex heuristics. Treat the counts as accurate to about ±15%.

## Clusters (`RemoveDeck:All`, n = 2,479; multi-label)

84% of `All` cards fall into at least one cluster below.

| Cluster | Cards | % of All | Example cards | Root cause |
|---|---|---|---|---|
| No `A:` line (static- or trigger-only permanent) | 452 | 18.2 | Bulwark, Steel Golem, Standstill, Pangosaur, Masumaro | The AI casts these through `PermanentAi` by creature or card value and never checks a drawback static or trigger (self-bounce, "you can't…", P/T = hand size, symmetric). The flag is a quality filter. |
| X / variable amounts | 289 | 11.7 | Corpseweft, Panacea, Black Sun's Zenith, Weight of Spires | `setMaxXValue` (`ComputerUtilCost.java:680`) handles mana X. X that comes from targets or from non-mana costs (Sac/Discard/RemoveCounter X; `AiCostDecision.java:757` "TODO … Ooze Flux") is evaluated weakly. |
| Non-mana costs (sacrifice or return lands/creatures, discard, reveal, tapXType) | 279 | 11.3 | Sandstone Deadfall, Orcish Mechanics, Bloodflow Connoisseur, Dark Heart of the Wood | The cost AI is conservative but works (`ComputerUtilCost.checkSacrificeCost` :351, `getCardPreference` `ComputerUtil.java:280-470`). `SACRIFICE_DEFAULT_PREF_ENABLE=false` in `forge-gui/res/ai/Default.ai:304`. Many of these flags are stale. |
| Animate / type, color or text change | 215 | 8.7 | Moonlace, Incite, Tundra Kavu, Myr Landshaper, Bone Shaman | `AnimateAi.animateTgtAI` only values "becomes a creature" and P/T-only changes. Everything else returns `CantPlayAi` (`AnimateAi.java:472-476`; the comment says "Those can just use AI:RemoveDeck:All"). `AnimateAllAi` needs `AILogic` (`AnimateAllAi.java:16-29`). |
| Choose\* head (type, color, name, card, number, player, source) | 211 | 8.5 | Blood Oath, Brain Pry, Blind Seer, Barbarian Guides, Whim of Volrath | Without `AILogic` these return `MissingLogic` (`ChooseTypeAi.java:25-27`, `ChooseColorAi.java:23-24`, `ChooseNumberAi.java:14-15`) or `CantPlayAi` (`ChooseCardNameAi.java:48`, `ChooseGenericAi.java:41-47`). |
| Combat-step tricks (attacking or blocking targets, lure, must attack) | 176 | 7.1 | Alluring Scent, Wake the Dead, Defiant Stand, Imps' Taunt | These need combat planning (setting up blocks before declaring them). Partly covered by Pump/Effect logic. |
| Mana oddities (rituals with costs, storage, mana replacement) | 171 | 6.9 | City of Shadows, Overeager Apprentice, Reality Twist, Wild Growth | `ManaReflected` maps to `CannotPlayAi` (`SpellApiToAi.java:126`). Storage and charge counters, `ReplaceMana` and mana-trigger auras have no planning. |
| Damage prevention / redirection | 166 | 6.7 | Blinding Fog, Benalish Missionary, Beacon of Destiny, Bolt Bend | Prevention scripted as `Effect` + `ReplacementEffects` and without `AILogic` hits `EffectAi.java:598`. Redirection ("dealt to X instead") has almost no AI. The plain `PreventDamage` API does have AI (`DamagePreventAi`). |
| Effect API without AILogic (`A:`/`SP:`) | 148 | 6.0 | Blinding Fog, Words of Worship, Quicken, Instigator, Gaze of Pain | `EffectAi.checkApiLogic`: without `AILogic`, only the "remembered target can't attack/block/activate" generic branch exists (`:446-597`). Everything else returns `CantPlayAi` (`:521-523`, `:598-599`). |
| Symmetric / each-player effects | 144 | 5.8 | Winds of Change, Balancing Act, Day's Undoing | `RepeatEachAi` defaults to **WillPlay** with no evaluation (`RepeatEachAi.java:101-103`). The flag guards against the AI casting these blindly. |
| Built-in drawback (cumulative upkeep, delayed self-sacrifice, no untap) | 111 | 4.5 | Pyric Salamander, Crazed Armodon, Black Carriage | No future-cost or tempo model. |
| Stack interaction (retarget, copy, counter variants) | 97 | 3.9 | Misdirection, Bolt Bend, Wild Ricochet, Imp's Mischief | `ChangeTargetsAi` only supports Spellskite-style magnets and mandatory activations; optional ones return `CantPlayAi` (`ChangeTargetsAi.java:25-35`). |
| Self-drawback / build-around permanent | 92 | 3.7 | Cache Raiders, Reclusive Wight, Island Sanctuary | Strategic. |
| Tap/untap utility | 88 | 3.5 | Aphetto Alchemist, Hyperion Blacksmith, Breaking Wave | `UntapAllAi` returns `CantPlay` unless it has a sub-ability (`UntapAllAi.java:22-38`). `UntapAi` and `TapOrUntapAi` are fine, so many of these flags are stale. |
| Modal (Charm, Entwine, Splice) | 71 | 2.9 | Dimir Charm, Ivory Charm, Into the Fray | `CharmAi` now picks modes with `canPlayWithSubs` (`CharmAi.java:119-124`). Flagged charms are flagged for their modes; some flags are stale (Dimir Charm). |
| Pump used as a target holder | 71 | 2.9 | Pack Hunt, Dwell on the Past, Legerdemain, Carom, Grim Contest | A `Pump` with no `NumAtt`/`NumDef`/`KW` and no `AILogic` only carries targets for its sub-abilities. `PumpAiBase.getPumpCreatures` (`:373-378`) finds nothing worth pumping, so the result is `TargetingFailed` (`PumpAi.java:348-352`). |
| Control change (exchange, donate, temporary steal) | 68 | 2.7 | Legerdemain, Shrewd Negotiation, Bazaar Trader | `ExchangeControlVariant` and `ControlPlayer` map to `CannotPlayAi` (`SpellApiToAi.java:71,100`). Exchange evaluation exists (`ControlExchangeAi`) but is narrow. |
| Depends on opponent's choice / punisher | 62 | 2.5 | Cuombajj Witches, Questing Phelddagrif | The opponent's answer isn't modeled. |
| Library peeking, reshuffle, tutor-to-top | 110 | 4.4 | Misinformation, Soldevi Digger, Scouting Trek | No immediate board value, so the AI can't value them. Mostly legitimate flags. |
| Coin / random / dice | 55 | 2.2 | Mana Clash, Fiery Gambit | Gambles. |
| Counter manipulation (move/remove, charge-up artifacts) | 53 | 2.1 | Ooze Flux, Fate Transfer, Essence Bottle | `RemoveCounterAll` maps to `CannotPlayAi` (`SpellApiToAi.java:161`). The cost-side TODOs are in `AiCostDecision.java:750-795`. |
| Loot / rummage / wheel | 42 | 1.7 | Faithless Looting, Windfall, Unfulfilled Desires | `DrawAi` + Discard. These flags are mostly a card-quality judgment and largely stale. |
| Turn/phase manipulation | 47 | 1.9 | Time Stop, Discontinuity, False Peace | `EndTurnAi` never plays (`EndTurnAi.java:20`). |
| Face-down / transform | 39 | 1.6 | Fatal Mutation, Backslide | Niche. |
| Ante / Vanguard / Plane | 25 | 1.0 | Jeweled Bird, Bosh avatar | Legitimate flags. |
| Not matched by any rule | 389 | 15.7 | Run Away Together, Errand of Duty, Killing Glare | Mixed. Many are simple and likely stale (see below). |

The `Random` clusters look different. 49% are static- or trigger-only permanents, and the top features are self-drawback or build-around (197), symmetric (174) and synergy hints (467 with `DeckHints`/`DeckNeeds`). They are deck-building judgments, not AI gaps.

### Code-confirmed dead defaults (all 34k cards, by flag)

A card is counted when its `A:` line hits the path shown.

| Dead default (file:line) | All | Random | Unflagged |
|---|---|---|---|
| `EffectAi` with no `AILogic` returns `CantPlayAi` (`EffectAi.java:521-523`, `:598-599`) | 148 | 13 | 204 |
| `PumpAi` with no NumAtt/NumDef/KW (target carrier) (`PumpAi.java:348-352`) | 71 | 11 | 206* |
| `ChooseType`/`ChooseColor`/`ChooseNumber` with no `AILogic` returns `MissingLogic` | 55 | 2 | 20 |
| `AnimateAi`, targeted non-creature animate (`AnimateAi.java:472-476`) | 43 | 6 | 31 |
| `AnimateAllAi` with no `AILogic` (`AnimateAllAi.java:27-29`) | 24 | 4 | 29 |
| `ChooseCardNameAi` with no `AILogic` (`:48`) | 23 | 0 | 11 |
| `ChangeTargetsAi`, non-magnet (`:35`) | 18 | 0 | 4 |
| `CannotPlayAi` mappings (`SpellApiToAi.java:71,72,100,111,126,132,145,161`) | 11 | 0 | 22 |
| `UntapAllAi` without a sub-ability (`:38`) | 10 | 1 | 19 |
| `ChooseGenericAi` with no `AILogic` (`:47`) | 9 | 0 | 19 |
| `PumpAi`, switch P/T without `AILogic` (the `SwitchPT` logic exists at `PumpAi.java:55,81`) | 7 | 1 | 0 |
| `EndTurnAi` (`:20`) | 5 | 0 | 0 |
| **Cards with at least one of these** | **424** | 38 | **560** |
| Too permissive: `RepeatEachAi` defaults to WillPlay (`:101-103`) | 38 | 6 | 44 |
| Too permissive: `ChoosePlayerAi` always WillPlay (`:19-20`) | 9 | 0 | 4 |

\*Many unflagged target-carrier Pumps have `AILogic$ Fight/PowerDmg/Destroy`, so they work. The unflagged count is an upper bound.

## Top gaps and proposed improvements (ranked by flagged cards affected)

### 0. Adventure: stop stripping `Random` cards (2,132 cards, trivial, fork-only code) — done

- **Status.** Done. `DuelScene.isAiUnplayable`, the deck generator's pool (`tools/concordia/deckgen/pool.py`) and `power_scorer.py` now drop only `RemoveDeck:All` cards. The pool grew from 26,974 to 28,945 cards, and the rebuilt tier decks use 160 cards that were excluded before.
- **What was wrong.** `DuelScene.isAiUnplayable` (`forge-gui-mobile/src/forge/adventure/scene/DuelScene.java`) treated `Random` like `All`.
- **Why that's wrong.** `Random` has no in-game effect: no `forge-ai` code path blocks those cards except one tutor filter (`ChangeZoneAi.java:1586`).
- **Fix.** Use only `getRemAIDecks()`. Optionally make it a `ConfigData` option such as `stripAiRandomCards` for tuned decks.
- **Effort / risk.** 1 line. Low risk: AI decks keep some situational cards that the AI plays normally.
- **Un-flags.** All 2,132 `Random`-only cards for Adventure. This touches neither the AI nor upstream data.

### 1. EffectAi: infer a logic from the effect's contents (148 All, plus 204 unflagged)

- **What's missing.** Without `AILogic`, `EffectAi.checkApiLogic` only handles the `RememberObjects + StaticAbilities` CantAttack/CantBlock/CantBeActivated case (`EffectAi.java:446-597`). It returns `CantPlayAi` otherwise (`:521-523`, `:598-599`). The logic needed already exists under `AILogic` names in the same method: `Fog` (`:112`), `Prevent` (`:232`), `RedirectSpellDamageFromPlayer` (`:214`), `Evasion` (`:186`), `RestrictBlocking` (`:68`), `Pump` (`:302`).
- **What the flagged no-AILogic Effects contain** (main ability):

  | Content | Cards |
  |---|---|
  | `R:DamageDone` with `Prevent` | 26 |
  | `R:DamageDone` redirect | 25 |
  | `S:Continuous` (not pump) | 17 |
  | `S:CantBlockBy` (evasion) | 10 |
  | `R:Draw` (Words of …) | 9 |
  | `S:MustAttack` | 8 |
  | `S:CastWithFlash` | 7 |
  | `S:MustBlock` | 3 |
  | `S:Continuous` pump or keyword | 3 |
  | Other | ~40 |

- **Fix.** Add `inferLogic(sa)` to `EffectAi`, used when there is no `AILogic`:
  - Prevent-replacement whose `ValidTarget` covers You or your creatures, and that is combat-related, maps to `Fog` (or to the `DamagePreventAi` threat checks).
  - Prevent on spell damage maps to `Prevent`.
  - `CantBlockBy` on your own creature maps to `Evasion`.
  - `MustAttack`/`MustBlock`/`CantBlock` on opposing creatures go to the existing generic restriction branch.
  - A `Continuous` pump or keyword on your creatures runs `PumpAllAi` on an equivalent `PumpAll`.
  - Everything else stays `CantPlayAi`.
- **Effort / risk.** Medium (about 150-250 lines, one file). Low-medium risk: only abilities the AI never used before change. Prevention timing needs care: the AI must only cast it during combat or in response.
- **Un-flags.** About 50-70 `All` cards (prevention, evasion, must-attack/block, pump statics). It also makes about 100 unflagged cards' abilities usable.

### 2. Choose\* heads: treat the choice as transparent and score the follow-up (87 All, plus about 50 unflagged)

- **What's missing.** `ChooseTypeAi.java:25-27`, `ChooseColorAi.java:23-24` and `ChooseNumberAi.java:14-15` return `MissingLogic` when there is no `AILogic`. `ChooseCardNameAi.java:22-48` returns `CantPlayAi`, and `ChooseGenericAi.java:41-47` returns `CantPlayAi`.
- **What already exists.** Default choosers are there (`ChooseTypeAi.chooseType` and the default card-name or color pickers). `ChooseGenericAi` even contains the generic helper: `BestOption` (`:28-33`, `:267-271`) accepts if any choice's `canPlayWithSubs` is willing.
- **Fix.**
  1. In `ChooseGenericAi`, default to the `BestOption` evaluation when `AILogic` is absent. This is a few lines.
  2. In ChooseType, ChooseColor, ChooseNumber and NameCard, when `AILogic` is absent:
     - Pre-compute the choice with the existing heuristic. Use "most prominent among my permanents" when the sub-ability helps its controller, and the opponent's when it is a curse (`isCurse`/`IsCurse$`).
     - Return the sub-ability's `chkDrawbackWithSubs` decision instead of `MissingLogic`.
     - For NameCard with a hidden-information sub (Brain Pry, Memoricide), name the highest-CMC nonland card in the opponent's known or revealed cards or library, or the "most prominent in human deck" heuristic that already exists.
- **Effort / risk.** Small for GenericChoice, medium for the rest (about 100-200 lines across 4 files). Medium risk: the AI may pick sub-optimal types, but these abilities were unused before.
- **Un-flags.** About 40-60 of the 87 (ChooseType/Color/Number 55, NameCard 23, GenericChoice 9).

### 3. Simulation fallback for "no logic" decisions (a general helper; plausibly 100-200 of the 424)

- **What's there.** Forge already has a one-ply "simulate and compare score" checker: `OnePlaySafetyChecker.isAcceptable` (`forge-ai/src/main/java/forge/ai/simulation/OnePlaySafetyChecker.java:12-35`). It runs `GameSimulator.simulateSpellAbility` and compares `GameStateEvaluator` scores.
- **Why it doesn't help today.** It is only used in hybrid-simulation mode (`AiController.java:987-988`), which only the desktop lobby can enable (`forge-gui-desktop/.../PlayerPanel.java:426`). Adventure never uses it.
- **Fix.** In `SpellAbilityAi.canPlayWithoutRestrict` (or `AiController.canPlaySa` around `:924`), when the API AI returns `MissingLogic`, or `CantPlayAi` from a known dead default, and the ability is a main-phase sorcery-speed action, run `OnePlaySafetyChecker`-style simulation. Accept if the score improves by a margin. Add an `AiProps` switch (for example `SIM_FALLBACK_FOR_MISSING_LOGIC`) and an activation budget per turn.
- **Limits.** The simulator scores the board right after resolution. It values permanent changes (AnimateAll, ChooseType then put counters, NameCard then exile, exchange of control, `RemoveCounterAll`, `UntapAll`). It does **not** value "until end of turn" prevention or combat tricks, so #1 is still needed for those.
- **Effort / risk.** Medium (about 150 lines, plus tuning). Medium risk for CPU time on mobile, so cap it and gate it behind the profile switch.
- **Un-flags.** Plausibly 100-200 cards across the Choose\*, AnimateAll, targeted Animate, control, counter and untap clusters. It is the most general lever.

### 4. Pump as target carrier: delegate to the sub-chain (71 All)

- **What's missing.** A targeting-only `Pump` (no `NumAtt`/`NumDef`/`KW`/`AILogic`) fails in `PumpAiBase.getPumpCreatures` (`:373-378`), which leads to `TargetingFailed` (`PumpAi.java:348-352`). Examples: Pack Hunt, Dwell on the Past, Grim Contest, Carom, Legerdemain, Soul's Grace. The sub-abilities read `Targeted`/`ParentTarget`, so their own AIs never choose targets.
- **Fix (pick one).**
  - (a) Code: when the Pump is "empty" and has a `SubAbility`, iterate the legal targets (bounded to the top N by `evaluateCreature`/`getBestAI`). For each target, set it and evaluate `chkDrawbackWithSubs`, or the #3 simulation, and keep the best.
  - (b) Data: rewrite the worst offenders so targeting lives on the real effect. Upstream has done this for some cards: `AILogic$ Fight/PowerDmg/Destroy` on 79 unflagged carriers shows the pattern.
- **Effort / risk.** (a) Medium, (b) per card. Medium risk.
- **Un-flags.** About 30-40.

### 5. AnimateAll and targeted non-creature Animate (24 + 43 All)

- **What's missing.** `AnimateAllAi.canPlay` only knows `CreatureAdvantage`/`Always` (`AnimateAllAi.java:16-29`). `animateTgtAI` gives up on color, land-type and ability-loss changes (`AnimateAi.java:472-476`).
- **Fix.** Give `AnimateAll` a default using the existing `AnimateAi.becomeAnimated(card, sa)` LKI copy (`AnimateAi.java:478`). Sum `evaluateCreature` deltas for your side minus the opponent's side and play if the net is positive. That handles Biomass Mutation, Sylvan Awakening, Inkfathom Witch and Brawl. Leave color and land-type changes flagged: their value depends on protection or landwalk interactions the AI can't see.
- **Effort / risk.** Small-medium. Low risk.
- **Un-flags.** About 20 (mostly `AnimateAll`).

### 6. Non-mana costs and charge-up artifacts (279 All, many stale)

- **What's there.** The cost AI already refuses to pay unless it has fodder: `checkSacrificeCost` (`ComputerUtilCost.java:351-425`) and `getCardPreference` (`ComputerUtil.java:280-470`) with `SacMe`/`DiscardMe`, surplus lands and the life-in-danger rules. The worst outcome of un-flagging is that the AI rarely activates the ability. The real gaps are the X-amount costs (`RemoveAnyCounter<X>`, `AiCostDecision.java:750-795` TODOs) and storage counters.
- **Fix.**
  - Data first: re-check flags on cards whose only oddity is the cost (Orcish Mechanics, Bloodflow Connoisseur, Dark Heart of the Wood, Spawnbinder Mage, Slobad).
  - Code: consider `SACRIFICE_DEFAULT_PREF_ENABLE=true` for the profiles Adventure uses (currently `false` in `Default.ai:304`, `true` in `Experimental.ai:304`).
- **Effort / risk.** Low. Low risk.
- **Un-flags.** About 80-120 (from the sample).

### 7. ChangeTargets (18 All) and RepeatEach (too permissive: 69 All cards use it, about 40 as their main ability)

- **ChangeTargets.** `ChangeTargetsAi.java:25-35` only handles `DefinedMagnet$ Self`. Add "opponent's top-of-stack spell targets my permanent or me: retarget it to an opposing legal target" (Misdirection, Bolt Bend, Imp's Mischief, Meddle). Medium effort; about 12 cards.
- **RepeatEach.** This is the opposite problem. `RepeatEachAi` returns WillPlay with no evaluation (`RepeatEachAi.java:101-103`), so un-flagging symmetric cards would be harmful. Make the default `CantPlayAi`, or the #3 simulation, before touching those flags.

### Not worth a general fix

These are legitimate flags and should stay:

- static/trigger-only permanents with drawbacks (452)
- combat-step setup tricks (176)
- library ordering and peeking (110)
- coin flips and ante
- turn skipping and ending the turn
- opponent-choice punishers

Rather than AI work, a smaller lever for them is to move the ones that are merely weak from `All` to `Random`, so the AI can at least use them when they appear.

## Possibly stale flags

### Sample of 34 simple `All` scripts

The pool was 627 cards with one simple `A:` ability, a standard API, and no static, trigger or replacement. Each sampled card was judged by hand against the AI code.

- **Look playable today (17).**
  - Spawnbinder Mage (`TapAi` with `checkTapTypeCost`)
  - Aphetto Alchemist (`UntapAi.untapPrefTargeting`)
  - Saproling Cluster, Orcish Mechanics, Bloodflow Connoisseur, Dark Heart of the Wood, Slobad, Sandstone Deadfall (sacrifice or discard costs go through `getCardPreference`, so the AI is merely conservative)
  - Surreal Memoir (hidden graveyard to hand)
  - Jamuraan Lion ("can't block" curse keyword handled at `PumpAiBase.java:121`)
  - Rhystic Shield (`PumpAll`)
  - Dream Salvage (`DrawAi` refuses 0 cards, `DrawAi.java:327`)
  - Errand of Duty (`TokenAi`)
  - Turtleshell Changeling (**already has `AILogic$ SwitchPT`**, `PumpAi.java:55`)
  - Irresistible Prey (**has `AILogic$ Pump`**)
  - Blood Celebrant (mana with life cost)
  - Overeager Apprentice (ritual sacrifice used only when paying)
- **Uncertain (3).** Run Away Together and Aether Tradewinds (bouncing one of your own permanents is a mandatory target), Burden of Guilt (attach-as-curse).
- **Flag still justified (14).** Soldevi Digger, Aura Barbs, Dwell on the Past and Pack Hunt (target-carrier Pump), Oboro Breezecaller, Ooze Flux (`RemoveAnyCounter X` TODO), Misinformation, Morgue Thrull, Inside Out and Dwarven Thaumaturgist (switch P/T without `AILogic`), Weight of Spires (X from the target's controller), Hallowed Ground, Calming Verse (the sub destroys your own enchantments), Sanguine Praetor.

So **about 50% of simple flagged scripts look stale**. That is roughly 250-320 of the 627-card pool.

### Other stale signals

- **117 `All` cards have `AILogic$` on their main ability.** The values are `NeedsPrevention` 27, `Evasion` 8, `Pump` 6, `Fog` 5, `SwitchPT` 4, `MostProminent*`, `BoneManCantRegenerate` and others. Someone wrote AI for these and left the flag. Excluding `AILogic$ Never` (5), these are prime re-test candidates.
- **Inconsistency.** Samite Healer (`PreventDamage`, unflagged) and Barrenton Medic, Martyrs' Tomb and Remedy (same API, flagged). 106 `PreventDamage` cards are unflagged.

### Overall estimate

Roughly **300-450 of the 2,479 `All` flags** (12-18%) could be removed with no code change, after a smoke test.

## Recommendation

1. **Done.** Adventure strips only `RemoveDeck:All`, freeing 2,132 cards with zero AI risk.
2. **Cheap AI wins (days).**
   - `ChooseGenericAi`: default to `BestOption`.
   - `EffectAi`: infer `Fog`/`Prevent`/`Evasion`/restriction logic from the effect's contents.
   - `AnimateAllAi`: net-evaluation default.
   - `RepeatEachAi`: change the permissive default *before* un-flagging symmetric cards.

   Together these address about 120 `All` cards, plus many unflagged abilities that are silently disabled today.
3. **One general lever (about a week).** A gated simulation fallback for `MissingLogic`/dead-default decisions, reusing `OnePlaySafetyChecker`/`GameSimulator`, behind an `AiProps` switch. It covers the long tail of Choose\*, Animate, control and counter effects without per-card logic.
4. **Flag audit (ongoing).** Do not edit upstream card data by hand yet.
   - Add an AI-profile switch that ignores the `RemoveDeck:All` play block at `AiController.java:1647-1651` (the TODO there already suggests it).
   - Run `forge-gui-desktop/src/main/java/forge/view/SimulateMatch.java` or `tools/concordia/sim` AI-vs-AI batches with decks seeded with the 117 cards that have `AILogic` and the 627 simple-script candidates.
   - Keep the cards that are cast without errors or obviously bad plays. Downgrade merely weak cards from `All` to `Random`.
5. **Leave alone.** The static-/trigger-only drawback permanents, combat-setup tricks, library ordering, coin and ante cards. They are a legitimate quality filter.

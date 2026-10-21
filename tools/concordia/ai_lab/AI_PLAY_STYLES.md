# AI play styles: profiles, requirements, adventure selection and edit options (forge-ai-lab, 2026-10-21)

Research only. No code, no builds, no card scripts, nothing applied. Proposals are unticked in `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md` (PS-1 to PS-5). Sources: `forge-gui/res/ai/{Default,Reckless,Cautious,Experimental}.ai`, `forge-ai/.../AiProps.java`, `AiProfileUtil.java`, `LobbyPlayerAi.java`, `forge-gui/.../player/GamePlayerUtil.java` (80-96), `forge-game/.../Match.java` (318-328), `forge-gui-mobile/.../adventure/scene/DuelScene.java` (515, 911-924), `forge-gui-mobile/.../adventure/data/EnemyData.java` (29, 62), `forge-gui/res/adventure/Concordia/world/enemies.json`, `forge-ai/.../PlayerControllerAi.java` (63-76, 1460-1467).

## 1. Styles that exist (profile files)
Four shipped profiles, same property names (`Default.ai` has 113 properties; `AiProps.java` holds the enum default, which applies only when a property is missing from the file).

| Property (Default / Reckless / Cautious / Experimental) | What it changes (file and method) |
|---|---|
| PLAY_AGGRO (false / **true** / false / false) | `AiAttackController` `playAggro` and aggression levels; overrides CHANCE_TO_ATTACK_INTO_TRADE |
| CHANCE_TO_ATTACK_INTO_TRADE (0 / **100** / 0 / 0; AiProps default 40) | `AiAttackController` 1271-1282, the attack-into-trade roll |
| ATTACK_INTO_TRADE_WHEN_TAPPED_OUT (false / **true** / false / false) | same roll, mana check |
| CHANCE_TO_ATKTRADE_WHEN_OPP_HAS_MANA (30 / **100** / 0 / 30) | `AiAttackController`, risk of a trick |
| TRY_TO_AVOID_ATTACKING_INTO_CERTAIN_BLOCK (true / true / **false** / true) | `AiAttackController` pre-block check |
| MAX_DIFF_IN_CREATURE_COUNT_TO_TRADE (1 / 0 / 0 / 1) | `AiBlockController` trade rule |
| TRY_TO_HOLD_COMBAT_TRICKS_UNTIL_BLOCK (true / true / false / true); CHANCE_TO_HOLD_COMBAT_TRICKS_UNTIL_BLOCK (65 / 65 / 75 / 75) | `ComputerUtilCard` trick timing |
| USE_BERSERK_AGGRESSIVELY (true / true / false / true) | `ComputerUtilCard` |
| AI_IN_DANGER_THRESHOLD / AI_IN_DANGER_MAX_THRESHOLD (4/4 · 4/4 · 4/6 · 3/12) | `ComputerUtilCombat` life-in-danger band (random step, lines 443-449); also cost and Endure/Venture code |
| MULLIGAN_THRESHOLD (4 / 3 / 4 / 4; AiProps default 5) | `ComputerUtil` mulligan stop |
| MIN_SPELL_CMC_TO_COUNTER (0 / 0 / 2 / 2) | `ability/CounterAi` |
| TOKEN_GENERATION_ABILITY_CHANCE (80 / 80 / 80 / 100) | `ability/TokenAi` |
| CHANCE_TO_CHAIN_TWO_DAMAGE_SPELLS (90 / 75 / 25 / 100); HOLD_X_DAMAGE_SPELLS_THRESHOLD (5 / 3 / 6 / 5) | damage spell timing |

Other inputs to the style: `PlayerControllerAi.pilotsNonAggroDeck` (lines 63, 75-76): set once per match, on the first game, from `Match.java` 327-328 (`complainCardsCantPlayWell`). It is true when the deck **name contains "Control"** or the average CMC is above 3 (`Deck.getAverageCMC`: non-land creatures, artifacts, enchantments, planeswalkers and commander only). It feeds `AiAttackController` 398-435 (baseline life). `AILogic$` and `AIPreference` on cards are card-level styles (see section 4).

## 2. What each style requires
| Style | Selected by | Deck requirement | Note |
|---|---|---|---|
| Default | user setting `UI_CURRENT_AI_PROFILE` (default "Default") | none | the sims use this (createAiPlayer without override) |
| Reckless | adventure `"ai": "reckless"` (DuelScene `selectAI`), or user setting | a deck with creatures to trade; aggressive play needs a curve that can attack | attacks into trades; weakens the AI's defence |
| Cautious | `"ai": "cautious"` or user setting | none | rarely trades, holds back; suits control decks |
| Experimental | `"ai": "experimental"` or user setting | none | deeper danger band, chains damage |
| Auto (pilotsNonAggroDeck) | always on | deck name "Control" or average CMC > 3 | not a profile: a flag inside Default, Reckless, etc. |

## 3. How Adventure chooses it (Concordia)
- `EnemyData.ai` is read from `enemies.json` (`"ai"`). `DuelScene.selectAI` (911-924) maps only "default", "reckless", "cautious", "experimental" (case-insensitive); anything else, including "" or missing, returns "" and the opponent uses the **user's own profile setting**.
- All 58 Concordia enemies have `"ai": ""` (checked 2026-10-21), so every Concordia opponent plays the player's chosen profile. No per-tier, per-type or per-deck style exists today.
- The per-enemy field is data-only and already read; the four names are fixed in Java (`selectAI`). A new profile name needs a Java change (PS-4).

## 4. Edit options, ranked by safety
| # | Class | Option | What it allows for Concordia | Risk | Test with the existing suite |
|---|---|---|---|---|---|
| E1 | data | Set `"ai"` per enemy in `enemies.json` to one of the four names (tier or type based) | tier-based aggression, wild creatures reckless, guardians cautious | low; only Concordia enemies change; the user's own games untouched | sim: give each side a profile via `createAiPlayer(name, profile)` in a BonusSim variant (test only), seeded, stock vs profile, equal life and seats |
| E2 | data | Deck name `"... Control"` in `[metadata] Name=` | archetype-based hold-back for the control decks | tier 1 control decks change from aggro to non-aggro piloting; affects the PC win-rate target at tier 1 (H29: 70%) | sim with the renamed deck vs the same deck named as now, seeded |
| E3 | card script | `AILogic$` value on the cards that matter (existing values only: Fog, Protection, BadETB, Pump) | reuses the existing per-card logic | medium: card scripts change the player's cards too | seeded stock vs overlay, as with 010-013 |
| E4 | Java | Add profile names to `DuelScene.selectAI` and a `.ai` file per archetype | tier and archetype styles with full control | medium-high: new Java in the shipped game (not allowed without approval) | needs approval; sims first on the overlay |
| E5 | Java | Read archetype (not CMC) in `setupAutoProfile` | better pilotsNonAggroDeck for all decks | medium: changes attacks for every AI deck | seeded stock vs overlay on tier 1-5 |

Not recommended: editing the shipped `Default.ai`, `Reckless.ai` or `Cautious.ai` values. They apply to every user game, not only Concordia.

## 5. Connection to tier 1 and the PC win-rate targets
- Average mana value (game definition, `Deck.getAverageCMC`) for tier 1: the main session reports all 80 live and staged tier 1 decks at 3.0 or below, so they are piloted as aggro (non-aggro if the name says Control); tiers 2-5 are non-aggro. This needs re-checking on the exact function (see DECK_LOGIC_TO_AI_DECISIONS.md, correction).
- A style change moves the player's win rate directly: a more aggressive AI (Reckless) should lower it at tiers 1-2, where the target is 70%; a cautious AI should raise it at tiers 3-5, where the target is 50%. Neither direction is proven here; it must be measured (about 40 games per arm, H28).

## 5a. Top 5 recommendations
1. **E1 first (data only).** Per-enemy `"ai"` in `enemies.json` by tier, using existing profile names. Measure with a test-only BonusSim variant that sets profiles per side, seeded, equal life, equal load, before any change to the shipped JSON.
2. **Measure the auto-flag (E2 vs E5) before relying on it.** Pilot flag comes from the deck name; run one seeded comparison of the current name rule against an archetype rule.
3. **Keep the shipped profiles untouched.** Use per-enemy selection (E1) rather than editing Default, Reckless or Cautious.
4. **Card-level only when E1 and E2 are not enough** (E3, reuse existing AILogic values; approval first).
5. **Java (E4, E5) only after the data-only results,** and only with the user's approval, because it touches the shipped game.

## 6. Caveats
- Research by reading code; no game was run.
- `selectAI` is in forge-gui-mobile (the adventure front end); the desktop game picks profiles through the lobby.
- `AiProps` defaults and the `.ai` files can disagree (for example CHANCE_TO_ATTACK_INTO_TRADE 40 vs 0); the file wins when present.

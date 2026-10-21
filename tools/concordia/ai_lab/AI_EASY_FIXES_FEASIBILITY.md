# Easy fixes for the Forge AI: feasibility (forge-ai-lab, 2026-10-21)

Research only (approved by the main session). No edits to forge-ai, the overlay or card scripts. Every proposal uses existing syntax; the nearest existing example is cited. Paths are repo-relative. Proposals go to `AI_CHANGES_APPROVAL.md` as unticked entries only.

## 1. Propagate AILogic$ / AIPreference to near-identical cards
**What the values do in code.** 162 `getParam("AILogic")` calls across about 80 ability AI classes (forge-ai `ability/*.java`, `AiController.java`, `ComputerUtil*.java`). Each value is read only by the AI class for the card's own API: e.g. `AILogic$ Fog` by `ability/FogAi.java` and `ComputerUtil.hasAFogEffect` (ComputerUtil 1512); `AILogic$ Pump` by `ability/PumpAi.java`; `AILogic$ BadETB` by `AiController.java` 380. A value on a card with another API is ignored. `AIPreference` is read by `ComputerUtil.getCardPreference` (284-303) for SacCost, DiscardCost and ManaFrom.

**What "near-identical" must mean.** The same API (`SP$`/`AB$`/`DB$` name), the same AI-relevant parameters (NumDmg, ValidTgts, Cost shape) and the same AILogic value. A lookalike with a different cost or duration can change the AI's decision.

**Method to find candidates (not run).** Group card scripts by (API, AILogic value, cost shape); a card is a candidate when it shares the group but lacks the value. The main session's `AILOGIC_SAMPLE.md` (pushed after my first draft) gives 350 distinct values on 1,814 cards: 191 values occur on one card only, and 37 occur on 10 or more. The 37 common values are where propagation pays off; the 191 single-card values need no propagation. Top values by card count: Always 187, PowerDmg 96, MostProminentInComputerDeck 83, Pump 71, AtOppEOT 66, NeedsPrevention 65, Fight 63, Curse 62, MakeUnblockable 55, ReplaySpell 43, Fog 35.

- Ease: M (card scripts; needs approval per card group).
- Viability: good where the API and parameters match; poor for cards whose API is different.
- Existing-syntax proof: `AILogic$ Fog` on 36 scripts is already the pattern.
- Performance: none. The value is read once per decision with `getParam` (no loop over deck, library or battlefield).
- Risk: wrong logic on a lookalike; mitigated by the seeded stock-vs-overlay test (the same card group only).

## 2. The AI reading its own deck at match start
**What exists.** The AI reads its deck at decision time, not at match start, and does not cache it:
- `Deck.getKeyCards()` (forge-core `Deck.java` 608-609) returns a copy of the list each call.
- Read in `ability/ChangeZoneAi.java` 1504 (`chooseCardToHiddenOriginChangeZone`, the library search / tutor choice; it removes cards the AI already holds from its copy), in `ComputerUtil.java` 2304 (discard choice) and `SpecialCardAi.java` 403 (opponent key cards).
- `AiDeckStatistics.fromPlayer` (forge-ai `AiDeckStatistics.java` 115) reads the deck only in the simulation path `GameStateEvaluator` 163, which runs only with `usesFullSimulation()` (`AiController` 111-113, default off).
- `AiCardMemory` (57 call sites) holds per-turn sets (for example `HELD_MANA_SOURCES_FOR_MAIN2`, `TRICK_ATTACKERS`), not deck data.

**Data-only route that exists today: `KeyCards`.** `DeckFileHeader.KEY_CARDS = "KeyCards"` (forge-core `DeckFileHeader.java` 47, 108-112): a `;`-separated list in the deck header. Concordia decks: 0 carry `KeyCards` (checked 2026-10-21). Writing it is data only and reaches the existing tutor and discard logic above. Ease: S (data). Nearest example: the header parser itself.

**DeckHas / DeckNeeds / DeckHints.** Not read by forge-ai (grep found none; forge-gui builders only). Reading them in game needs Java. Not an easy fix.

**Caching.** Caching the deck list in a new field would be Java (M) and would go stale when cards leave the deck. The per-call copy is small (deck size about 100) and is not a loop per priority, so caching is not needed for speed. Performance impact: low, only in the tutor and discard decisions.

## 3. Profiles: more robust or new ones
- **New profile file: data only.** `AiProfileUtil.getAvailableProfiles` (forge-ai `AiProfileUtil.java` 162-170) lists every `*.ai` in the profile directory, and `loadAllProfiles` (80-89) loads them all. So a new file in `forge-gui/res/ai/` appears in the user's settings (`getProfilesArray`). Ease: S.
- **Adventure cannot select it without Java.** `DuelScene.selectAI` (mobile 911-924) accepts only the four names; any other `"ai"` gives the user's setting. Ease for that change: S-M (Java, shipped game, needs approval).
- **Robustness risk (verified in code).** `loadProfile` (AiProfileUtil 92-108) calls `AiProps.valueOf(split[0])` with no try/catch, so an unknown property name throws `IllegalArgumentException`. `loadAllProfiles` is called from `FModel` (276) with no catch in the code I read, so a typo in a new `.ai` file could break start-up. Not verified in a running game. A value containing `=` is silently ignored (`split("=")` length check).
- **Unknown-name fallback.** A name not in the loaded map gives the `AiProps` enum defaults (AiProfileUtil 146-150), not Default.ai. The enum defaults differ from Default.ai for several properties (for example CHANCE_TO_ATTACK_INTO_TRADE 40 vs 0).
- **Aggro and Control profiles by name.** No effect on Concordia unless the adventure selects them (Java). The name-based switch that does exist is the pilot flag (section 4), not the profile name.

## 4. Rename Concordia deck names to trigger the Control check
- **Where.** `PlayerControllerAi.setupAutoProfile` (forge-ai `PlayerControllerAi.java` 75-76): `deck.getName().contains("Control")` sets `pilotsNonAggroDeck`. The name is the `Name=` line in `[metadata]` (`DeckFileHeader.NAME` 38, read at 86; written by `DeckSerializer` 47).
- **Which decks change.** Tier 2-5 decks already have an average CMC above 3 (main session's figure, pending the exact-function check), so naming them Control changes nothing for them. Tier 1 decks (CMC 3 or below) would change from aggro to non-aggro piloting. That moves the tier 1 win rate, against the 70% target (H29). This is the only real effect.
- **Side effects.** `enemies.json` references decks by file path (`"deck"` entries), not by name, so a rename does not break the reference. Other code that keys decks by name was not checked (not verified).
- **Ease.** S: change the `Name=` line in the affected `.dck` files; needs the main session's approval and a seeded stock-vs-renamed test on tier 1.
- **Exact match.** The test is case-sensitive `contains("Control")`.

## 5. Ranking
| Rank | Item | Ease | Viability | Performance | Main risk |
|---|---|---|---|---|---|
| 1 | Item 2: `KeyCards` header on Concordia decks (data) | S | good for tutor and discard decisions | none | a wrong key card changes tutor choices |
| 2 | Item 4: Control name on tier 1 control decks (data) | S | real effect on tier 1 piloting | none | moves the PC win rate |
| 3 | Item 3: new data-only profile file (not reachable from adventure) | S | low until Java | none | a typo in the file may break start-up (unverified) |
| 4 | Item 1: propagate AILogic to lookalikes | M | good per API; needs the sample | none | wrong logic on a lookalike |

## 6. What is not done
- Item 1's candidate list is not built; the sample now exists, so the next step is the (API, value, cost shape) grouping.
- Concordia `KeyCards` values are not written (data change, needs approval).
- Not verified: other code that keys decks by name; start-up behaviour on a bad `.ai` file; exact-function average CMC.

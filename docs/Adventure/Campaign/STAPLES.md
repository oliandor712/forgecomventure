# Card categories: Staples, Game Changers and the watch list

`tools/concordia/deckgen/staples.py` sorts the popular Commander cards by two numbers. It writes
`deckgen/staples.json`, and `power_scorer.py` reports each deck's counts.

## The two numbers

- **Popularity:** the highest of the card's EDHREC rank (from Scryfall, log-scaled), its precon inclusion rate and
  its cEDH inclusion rate (from Spellbinder).
- **Impact:** what the card can do by itself, read from its Forge script, from 0 to 1.

| Impact | Kinds of card |
|---|---|
| 1.0 | Wins the game |
| 0.9 | Extra turns; mass land denial |
| 0.65-0.8 | Board wipes, one-sided wipes (including Overload); effects that change every creature |
| 0.6 | Stax; replacement effects on opponents; stealing; unrestricted tutors; protecting your whole board |
| 0.5-0.55 | Repeatable draw, token or mana engines; variable mana; big bodies (power 6 or more) |
| 0.3 | Single-target removal and counterspells |
| 0.2-0.25 | Ramp; mana rocks and dorks; fast mana; cantrips; equipment |
| 0.05 | Lands |

## The categories

| Category | Rule | Count | Examples |
|---|---|---|---|
| Game Changer | on Forge's `lists/gamechangers.txt`, which matches Scryfall's 53 cards | 53 | Cyclonic Rift, Rhystic Study, Demonic Tutor |
| Staple | popularity 0.3 or more (about EDHREC rank 1,300 or better), impact 0.35 or less, not a Game Changer | 1041 | Sol Ring, Command Tower, Arcane Signet, Swords to Plowshares, Lightning Greaves, Counterspell, Cultivate, Birds of Paradise |
| Watch | popularity 0.3 or more, impact 0.6 or more, not a Game Changer | 115 | Blasphemous Act, Toxic Deluge, Vandalblast, Austere Command, Animate Dead, Grand Abolisher, Diabolic Intent, Aetherize, Finale of Devastation, Damn |

The watch list holds popular cards that look like they swing games without being on the official list. Each one is
either a candidate for Concordia's own Game Changer rules or a miss in the impact heuristic, to check by hand.

## Checked against the Game Changers list

- **Of the 53 Game Changers, 21 score high impact (0.6 or more), 11 middling and 21 low.**
- **The low ones are mostly fast mana or lands:** Ancient Tomb, Mox Diamond, Chrome Mox, Gaea's Cradle, Serra's
  Sanctum.
- **The rest of them** are combo or engine pieces whose power the script doesn't show: Underworld Breach,
  Necropotence, Ad Nauseam, Bolas's Citadel.
- **The official list always wins.** It counts acceleration and combo potential that the heuristic rates low.
- **The heuristic is for the other direction:** keeping game-swinging cards that aren't Game Changers out of the
  staples. Spot checks of the 70 most popular staples found only role players: lands, rocks, dorks, single removal,
  counterspells and Lightning Greaves.

## Per tier (average per deck)

| Group | Staples | Watch | Game Changers |
|---|---|---|---|
| Tutorial | 4.0 | 0 | 0 |
| Starters | 14.0 | 0.4 | 0 |
| T1 | 1.6 | 0 | 0 |
| T2 | 8.8 | 0.6 | 0 |
| T3 | 23.0 | 1.6 | 0.3 |
| T4 | 28.4 | 2.4 | 1.0 |
| T5 | 32.6 | 3.6 | 1.4 |

The staples count climbs with tier, so it's a useful second measure of deck quality. The starters' 14 staples sit
above tier 2's 9, which matches their deck power (about the top of tier 2).

## Applied (2026-10-20): deck building and tier rules

All 200 tier decks were rebuilt with these rules. The old decks, `decks.json` and `enemies.json` are backed up in
`tools/concordia/backups/2026-10-20_decks_pre_rebuild/`.

| Rule | Where | Setting |
|---|---|---|
| Staple preference | `deckgen/build.py` `STAPLE_BONUS`, `STAPLE_PUSH_BONUS` | T1-T2: +6 for staples at any rarity (user, 2026-10-26: no rarity restrictions), T1 and T2 only;  T3 +3, T4 and T5 +1.5 |
| Tier 1-2 floor and ceiling (builder rebuilds outside them) | `FLOOR`, `CEILING`, `T1_TARGET` | T1 16-21 (target 18.5), T2 24.5-30 |
| Budget lands and mana rocks (in at least 18 of the 365 precon and Archidekt decks, any rarity, no printing filter; `deckgen/budget_lands.py`) | `BUDGET_LANDS`, `BUDGET_ROCKS` | T1 3 lands and 2 rocks, T2 up to 6 nonbasics and 3 rocks; mono decks skip lands and rocks for other colors and "any colour" lands |
| Precon playability bonus | `PRECON_BONUS` | +2 at T2-T3, scaled by precon inclusion |
| Watch-list cap (builder hard cap; tier check WARN) | `WATCH_CAP`, `power_scorer.TIERS` | T1 0, T2 1, T3 2, T4 4, T5 8 |
| Staples per deck (soft check, WARN) | `power_scorer.TIERS` | T1 2-15, T2 12-41, T3 22-39, T4 22-46, T5 28-48 |
| Power bands (EDHREC scale) | `power_scorer.TIERS` | T1 19 or less, T2 19-31, T3 27-38, T4 34-42, T5 39 or more |
| Build targets | `TARGET_POWER`, per-deck targets in `decks.json` | +1.5 at T2-T3, +1 at T4, +0.5 at T5 |

The staples ranges cover the 10th to 90th percentile of the rebuilt decks, plus or minus 2.

| Tier | Deck power | Staples per deck | Watch | Game Changers | Tier fit |
|---|---|---|---|---|---|
| T1 | 13.7 to 12.5 | 1.6 to 0.1 | 0 | 0 | 40/40 |
| T2 | 25.1 to 25.4 | 8.8 to 18.7 | 0.6 to 0.4 | 0 | 40/40 |
| T3 | 33.2 to 33.8 | 23.0 to 29.9 | 1.6 to 1.3 | 0.3 to 0.2 | 32/40 |
| T4 | 37.6 to 38.0 | 28.4 to 34.4 | 2.4 to 2.1 | 1.0 | 30 to 31/40 |
| T5 | 42.3 to 42.6 | 32.6 to 37.6 | 3.6 to 3.7 | 1.4 to 1.6 | 34 to 31/40 |

- **No deck fails a hard check.**
- **3 decks sit just outside their power band** (warnings only).
- **171 of the 200 decks changed cards.** The Green zone's pools were re-picked, and they still ramp by stage.

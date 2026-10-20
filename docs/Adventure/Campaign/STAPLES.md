# Card categories: Staples, Game Changers and the watch list

`tools/concordia/deckgen/staples.py` sorts the popular Commander cards by two numbers. It writes
`deckgen/staples.json`, and `deck_tier.py` reports each deck's counts.

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

## Not applied (proposals)

1. **Tier rules:** cap the watch-list cards like Game Changers: T1 0, T2 1, T3 2, T4 4, T5 8.
2. **Staple counts per tier as a soft check:** T1 0-4, T2 4-14, T3 15-30, T4 20-40, T5 25-45.
3. **Deck builder:** let tier 2-3 builds prefer staples (consistency without swingy cards), and keep them out of tier 1.

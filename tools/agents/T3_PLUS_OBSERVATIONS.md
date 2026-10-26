# Tier 3-5 observations (parked)

Development is focused on tiers 1 and 2 for the start of the game (user, 2026-10-26). Every observation, problem or idea
about tiers 3, 4 and 5 goes here (rule H80) and waits until the user says it is time to address them. Nothing here is
fixed or scheduled. Add the date and where it was found; move an item to "Addressed" when it is dealt with.

## Open

| Date | Area | Observation | Found in |
|---|---|---|---|
| 2026-10-26 | Power retry | The builder retries a deck below its power window only for tiers 1-2. Tiers 3-5 have no retry, so 13 live tier 4 decks sit below the 35.5 band floor. | tier audit |
| 2026-10-26 | Live decks | Live outliers against `tier_table.json`: 4 tier 3 decks above 37, 5 tier 4 decks above 41.5, 5 tier 5 decks below 40. | tier audit |
| 2026-10-26 | Power-50/70 minimums | Tier 4 (4-14 power-50+, up to 5 power-70+) and tier 5 (8+ power-50+, 1+ power-70+) minimums are checked by `deck_tier.py` but the builder only enforces maximums. | tier audit |
| 2026-10-26 | Curve | The curve bucket sums exceed the nonland slots for tiers 1, 4 and 5, so the curve limits cannot all bind. | tier audit |
| 2026-10-26 | Colorless (H78) | The colorless limit (4 + 2 per colorless source) is not applied in tier builds. | tier audit |
| 2026-10-26 | Mechanics | `mech:*` minimums for tiers 3 and 4 (vote, monarch, day/night, ring from 3; speed, initiative, venture from 4) are enforced, but the pool has few tagged cards for some of them (contraption 2, scheme 2) and the tier 3/4 decks have not been re-checked since the check was added to `deck_tier.py`. | mech check |
| 2026-10-26 | Extra turns | The builder now takes 1 extra-turn card at tier 4 and 2 at tier 5 (never chained). No tier 4/5 deck has been rebuilt to see the effect on power. | extra-turn split |
| 2026-10-26 | Rarity | Rarity restrictions were removed for every tier, so tier 3-5 commanders and cards are no longer rarity-limited; power is the only separator. | rarity change |

## Addressed

| 2026-10-26 | Popularity input | `deckgen/external/decks.json` was missing locally; collected again (782 decks) and now committed. With it, live averages are T1 17.3, T2 27.1, T3 33.7, T4 37.9, T5 42.8, matching the bands in `tier_table.json`. | pool rebuild |

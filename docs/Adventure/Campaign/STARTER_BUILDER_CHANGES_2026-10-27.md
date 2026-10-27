# Starter builder changes, 2026-10-27

Nothing here is live or committed; code changes push on "push". Rules: H88-H92 in `tools/agents/human_logic.toon`.

## Done and verified
- **Glance scorers off (H88).** ArcMind and edhpowerlevel are skipped in `review-export`/`review-compare`. `GLANCE_SCORERS=1` turns them back on. A scorers-off export ran clean.
- **`review-apply`.** Second build from the glance rejects (max 10 swaps). W_Starter_Regen: 1 swap, wrote `_r2`. Both external scores dropped slightly: the swap replaced Terramancer (edhpowerlevel impact 10.8) with Divine Favor (1.06) because the Oracle reader rated Terramancer power 1. Not guarded yet.
- **Staple weight removed (H89).** `STARTER_STAPLE_BONUS=1` restores it. Test build picked 4 fewer non-land staples.
- **Pool.** Rebuilt with the new power scores: zero drift.
- **Land tags (H92).** `tag_extra.py`: `cost:life` now also marks painlands and City of Brass (damage to you) and shocklands (pay 2 life, now also `enters_tapped_conditional`). Pool rebuilt: 71 lands carry it; Llanowar Wastes, Overgrown Tomb, City of Brass checked.

## Built but not working well: nonbasic land picker (H90, H91)
`land_score` in `starter_build.py` ranks all pool nonbasic lands (pop >= 8): 1 coverage, 2 utility (commander support), 3 enters-tapped, 4 life cost, 5 sacrifice-other (ok if tempo+/fetch); power breaks ties.
Test results (Test decks in `staging_starters/`):
- Mono W (Captain America): Urza's Saga, Dark Depths, Plaza of Heroes, Treasure Vault, Abstergo Entertainment, Forbidden Orchard. Most are not clearly linked to the commander.
- B/G (Meren): Talon Gates of Madara, Exotic Orchard, Command Tower, Hall of Oracles, Opal Palace, Cascading Cataracts. Typed duals and painlands (Llanowar Wastes, Woodland Cemetery, Overgrown Tomb) are not chosen.
Cause (unconfirmed): `supports_cmd` is too loose for lands, and any-colour utility lands count as full coverage. Not fixed.

## Unverified
- Tags checked on about 15 lands, not the whole pool. Abstergo and Cavern of Souls tags look right (restricted any-colour); their value as picks is not judged.
- W_Starter_Regen and the other four colour starters were not rebuilt with these changes.
- `ARCMIND_TOKEN` account flow untested.
- Earlier findings not acted on: TARGET ~25 with 5/2 caps, commander-draw rule, H85 key-card narrowing, ArcMind basics-dropped bug.

## Options for the land picker
1. Coverage only from typed/painland/dual lands (exclude any-colour lands with other abilities); utility needs a stricter commander test.
2. Go back to the 108-land budget list and apply the H91 order inside it.

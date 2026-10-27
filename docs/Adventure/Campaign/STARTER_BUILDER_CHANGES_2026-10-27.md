# Starter builder changes, 2026-10-27

Nothing here is live or committed; code changes push on "push". Rules: H88-H92 in `tools/agents/human_logic.toon`.

## Done and verified
- **Glance scorers off (H88).** ArcMind and edhpowerlevel are skipped in `review-export`/`review-compare`. `GLANCE_SCORERS=1` turns them back on. A scorers-off export ran clean.
- **`review-apply`.** Second build from the glance rejects (max 10 swaps). W_Starter_Regen: 1 swap, wrote `_r2`. Both external scores dropped slightly: the swap replaced Terramancer (edhpowerlevel impact 10.8) with Divine Favor (1.06) because the Oracle reader rated Terramancer power 1. Not guarded yet.
- **Staple weight removed (H89).** `STARTER_STAPLE_BONUS=1` restores it. Test build picked 4 fewer non-land staples.
- **Pool.** Rebuilt with the new power scores: zero drift.
- **Land tags (H92).** `tag_extra.py`: `cost:life` now also marks painlands and City of Brass (damage to you) and shocklands (pay 2 life, now also `enters_tapped_conditional`). Pool rebuilt: 71 lands carry it; Llanowar Wastes, Overgrown Tomb, City of Brass checked.

## Nonbasic land picker (H90, H91, H93, H94)
`land_score` in `starter_build.py` ranks all pool nonbasic lands (pop >= 8): 1 coverage, 2 utility (commander support), 3 enters-tapped, 4 life cost, 5 sacrifice-other (ok if tempo+/fetch); power breaks ties.
- **Why typed duals and painlands were not chosen:** every any-colour land counted as full coverage with no penalty, including ones that need a mana cost, a condition or a restriction (Talon Gates, Hall of Oracles, Aether Hub, Reflecting Pool, Glimmervoid, Verges, filter lands). They tied the duals at the same coverage score, and the duals' small life/tapped penalties plus lower power pushed them below the 6 slots.
- **Fix (H94):** coverage needs colours from a plain tap; cost, condition and restriction lands count as utility only.
- **Negative tempo (H93):** Dark Depths and Forbidden Orchard are tagged `tempo:negative` (`setup_card`, `gives_opponent_token`); no utility, -50. Forbidden Orchard still carries a `token_make` tag; not cleaned up.
- **B/G (Meren) now:** Command Tower, Mana Confluence, City of Brass, Undergrowth Stadium, Llanowar Wastes, Woodland Cemetery.
- **Mono W (Captain America) still:** Urza's Saga, Plaza of Heroes, Treasure Vault, Abstergo Entertainment, Vesuva, The Mycosynth Gardens. The commander-support test is too loose for lands, so these utility picks are not trustworthy. Open.
- Debug: `LAND_DEBUG=1` prints the top 25 land scores.

## Unverified
- Tags checked on about 15 lands, not the whole pool. Abstergo and Cavern of Souls tags look right (restricted any-colour); their value as picks is not judged.
- W_Starter_Regen and the other four colour starters were not rebuilt with these changes.
- `ARCMIND_TOKEN` account flow untested.
- Earlier findings not acted on: TARGET ~25 with 5/2 caps, commander-draw rule, H85 key-card narrowing, ArcMind basics-dropped bug.

## Options for the land picker
1. Coverage only from typed/painland/dual lands (exclude any-colour lands with other abilities); utility needs a stricter commander test.
2. Go back to the 108-land budget list and apply the H91 order inside it.

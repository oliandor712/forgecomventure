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
- **Fix (H94, H95):** coverage needs colours from a plain tap or a plain mana cost. Condition and restriction lands (Glimmervoid, Verges, Tainted Wood, Reflecting Pool, Cavern-style) count as utility only. Lands and artifacts that pay mana to change colour (Viridescent Bog, Talon Gates, Signets; 57 cards) are tagged `mana_filter`: neutral mana that tilts colour coverage, ranked 20 below plain fixing. Life is not mana: painlands and shocklands keep `cost:life` and full coverage.
- **Tags (H93):** Forbidden Orchard is `tempo:negative` + `gives_opponent_token` (no utility, -50). Dark Depths is `setup_card` + `mana_sink` + `counter_remove` (a setup card that is a mana dump with counter synergy), not negative tempo. Forbidden Orchard still carries a `token_make` tag; not cleaned up.
- **B/G (Meren) now:** Command Tower, Cascading Cataracts, Mana Confluence, City of Brass, Undergrowth Stadium, Llanowar Wastes.
- **Mono W (Captain America) still:** Urza's Saga, Plaza of Heroes, Treasure Vault, Abstergo Entertainment, Vesuva, The Mycosynth Gardens. The commander-support test is too loose for lands, so these utility picks are not trustworthy. Open.
- Tag fix: an earlier edit of mine attached the `enters_untapped` branch to the wrong `if` (Woodland Cemetery had both tapped tags); corrected.
- Debug: `LAND_DEBUG=1` prints the top 25 land scores.
- **`mana_sink` tag (H96):** a repeatable activated ability with a mana-only cost and no tap (reminder text ignored). Excluded: sacrifice, exile, discard and life costs; keyword grants; becomes/transform; one-shot (adapt, monstrosity, renown, regenerate); once per turn. 1,185 cards, 6 of them lands. Lands with it count as mana-dump payoffs in `synergy.big_impact`. Sampled by hand on about 50 cards, not pool-wide.

- **No staples target (H97):** the starter builder no longer prints or enforces the tier staples range.
- **`setup_card:<need>` (H98):** general tag for cards that need a setup. `setup_card:mana` (Dark Depths) counts as land utility only with 10 ramp pieces in the deck.
- **`restricted_to:<type>` (H99):** 63 cards, 16 lands (mana or recursion limited to a creature type). A land counts as utility only when the type is the commander's or an allowed tribe (Haven of the Spirit Dragon needs dragons).
- **Colourless sources (H100, H101):** colourless-only lands are penalised (-150) without {C} pips or own synergy (Drownyard Temple), and are capped by the {C} pip share like a colour (Kozilek's Command needs {C}{C}).
- **Colourless sized as a colour (H102):** same pip-share rule as `check_tier` for coloured sources (sources / lands >= 0.8 x pip share); the 14-source floor is skipped. Replaces a placeholder of 4 sources per pip.
- **`token_scales:<Y>` (H103):** when a commander's token count is tied to Y, the support test is the pair token_make + Y. Captain America: `token_scales:Equipment`. Plain token makers stop counting as support (W: 37/63 -> 23/63 supporting).
- Earlier W_Starter_Regen_r4 (staged) rebuilt with the colourless rules: lands Urza's Saga, Plaza of Heroes, Vesuva, Drownyard Temple, Buried Ruin, Abundant Countryside; power 28.5; 37/63 supporting.

- W_Starter_Regen_r6 (staged) with H102/H103: lands Plaza of Heroes, Vesuva, Drownyard Temple, Buried Ruin, Haunted Fengraf, Lazotep Quarry; power 27.7; 31 creatures.

## Unverified
- Tags checked on about 15 lands, not the whole pool. Abstergo and Cavern of Souls tags look right (restricted any-colour); their value as picks is not judged.
- W_Starter_Regen and the other four colour starters were not rebuilt with these changes.
- `ARCMIND_TOKEN` account flow untested.
- Earlier findings not acted on: TARGET ~25 with 5/2 caps, commander-draw rule, H85 key-card narrowing, ArcMind basics-dropped bug.

## Options for the land picker
1. Coverage only from typed/painland/dual lands (exclude any-colour lands with other abilities); utility needs a stricter commander test.
2. Go back to the 108-land budget list and apply the H91 order inside it.

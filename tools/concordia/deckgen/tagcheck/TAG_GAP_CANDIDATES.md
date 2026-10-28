# Tag gap candidates before the retag (2026-10-27)

Sources: full pool scan (`mtg2llm.py scan`, 28,049 cards; `tags/POOL_GAPS.toon`, `tags/RENDER_GAPS.toon`) and the hand_units collision audit (`HAND_UNITS_COLLISION_AUDIT.md`). Everything here is PROPOSED only (H56): nothing is implemented, and `tags/NEW_TAGS_FOR_APPROVAL.md` stays the approval list. Unit = one ability group of a card.

## Scan totals
- 23,345 of 51,252 units (46%) have no render rule; 15,540 distinct patterns, 12,973 seen once.
- 78% of Oracle content words are missing from the render (297,717 of 383,452). This measures the render, not only the tagger.
- Only 4 of the 300 biggest-gap cards have no units at all: Cone of Cold, Selective Adaptation, The Ring Goes South, Berserker's Frenzy. Most gaps are partly tagged cards.
- Not triaged: only the top ~100 of 300 patterns were read. The counts are units per pattern, from `RENDER_GAPS.toon`.

## A. Tagger gaps: the tags cannot say it (need a new tag or value)
| Missing detail | Evidence | PROPOSED tag |
|---|---|---|
| kicked / not-kicked condition | Mold Shambler vs Woodfall Primus | `condition:kicked` |
| random opponent | Archfiend of Despair vs Witch Hunt | `target_scope:random_opponent` |
| intervening-if (opponent has more creatures / lands) | Urbis Protector, Shuri's Fabricator, T'Challa | `condition:opp_more_creatures`, `condition:opp_more_lands` |
| roll a die | Iron Mastiff | `roll_die` (+ `die_sides:N`) |
| spell-type filter on cast triggers | Teller of Tales, Oyobi (Spirit or Arcane) | `trigger_filter:spell_type:X` |
| cast-this-spell vs cast-targeting-this | Anax and Cymede vs Decimator | `trigger:cast_self`, `trigger:cast_targeting_self` |
| optional (may) on mill / sacrifice | Eivor, Frogantua, Barrowgoyf, Torgaar; 29 units carry a bare `optional` | `optional` attached to the effect it applies to |
| attacker / source filters | Circle of Flame (without flying, attacks you), Falkenrath Perforator | `attacker_filter:X` |
| trigger subject (commander, enchanted, one or more) | Kediss, Amarant Coral, Ancestor Dragon | `trigger_scope:commander`, `trigger_filter:one_or_more` |
| type filter on upkeep / enter effects | Mana Bloom, Oni of Wild Places, Elvish Archivist, Tocasia's Welcome | `target_filter:X`, `trigger_filter:mv_le_N` |
| chapter text of Sagas | 12 of 15 hits under one key; `saga_chapter draw_count:N` has 19 units | chapter number on each effect tag |
| channel effect | Eiganjo vs Gideon's Memorial | channel plus its effect tags kept separate |
| keyword costs hidden by N | Flashback, Kicker, Cycling, Escape, Mutate, Blitz, Emerge, Level up | cost value on the keyword (`flashback_cost`, `escape_exile:N`) |
| numbers hidden by N | energy, look_top, damage, mill (Peer Through Depths, Uncovered Clues, Black Waltz No. 3, Archive Trap) | keep the number as a value |
| 0-unit cards | Cone of Cold, Selective Adaptation, The Ring Goes South, Berserker's Frenzy | read each; tagger parse failure |

## B. Renderer rule gaps: the tags exist, `mtg2llm` has no sentence yet (not retag work)
Units without a rule, biggest first:
- keywords: typecycling 103, cascade 41, fear 34, storm 33, landwalk 33 + 26 (swamp, forest), bushido 32, horsemanship 28, wither 26, persist 23, soulshift 23, modular 22, flashback 22/18, evolve 21, devour 21, intimidate 20, renown 20, disturb 20/20, bloodthirst 20, exploit 20, unearth 19, madness 16/14, fabricate 16, assist 16, extort 15, flanking 15, multikicker 17, reconfigure 14, buyback 14, riot 13, suspend 13, exhaust 13, unleash 14, umbra armor 14
- surveil 72 (and 26 on ETB), untap 60, blocks trigger 33, effect:sacrifice 20, remove:destroy 20, prevent_damage 18, `cost:remove_counters` 29, `cost:sacrifice` 23
- counters: energy on ETB 59, pNpN on combat damage 31, pNpN on spell cast 33, ki counter 16
- grants: flying 37 / 30, vigilance 33, first strike 20 / 18, haste 20, menace 17, hexproof 14, protection 28 / 14, trample 22
- mill on ETB 43, bounce on ETB 41, damage to all creatures 32 / 19, damage replacement 26, counter-unless-pay 26, discard on combat damage 25

## C. Already listed
- `tags/MTG2LLM_GAPS.toon`: 73 rows open (209 total, 136 applied), e.g. Aethertide Whale, Alms Collector, Angrath's Marauders, Arbiter of Woe, Ashcoat of the Shadow Swarm, Barrowgoyf, Blight Titan, Braids's Frightful Return.

## Suggested order
1. Approve or reject section A tags (add each to `NEW_TAGS_FOR_APPROVAL.md` after your word).
2. Retag, then `pool.py`, then re-run `scan` to see which section B rows stay open.
3. Write section B rules (keyword sentences first: one rule clears 20-100 units each).

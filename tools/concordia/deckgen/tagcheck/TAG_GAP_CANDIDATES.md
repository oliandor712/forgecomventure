# Tag gap candidates before the retag (2026-10-27)

Sources: full pool scan (`mtg2llm.py scan`, 28,049 cards; `tags/POOL_GAPS.toon`, `tags/RENDER_GAPS.toon`) and the hand_units collision audit (`HAND_UNITS_COLLISION_AUDIT.md`). Everything here is PROPOSED only (H56): nothing is implemented, and `tags/NEW_TAGS_FOR_APPROVAL.md` stays the approval list. Unit = one ability group of a card.

## Scan totals
- 23,345 of 51,252 units (46%) have no render rule; 15,540 distinct patterns, 12,973 seen once.
- 78% of Oracle content words are missing from the render (297,717 of 383,452). This measures the render, not only the tagger.
- Only 4 of the 300 biggest-gap cards have no units at all: Cone of Cold, Selective Adaptation, The Ring Goes South, Berserker's Frenzy. Most gaps are partly tagged cards.
- Not triaged: only the top ~100 of 300 patterns were read. The counts are units per pattern, from `RENDER_GAPS.toon`.

## A. Tagger gaps: redundancy check against TAG_REFERENCE.md, then APPROVED (user 2026-10-27: "approve A")
Most rows were redundant: the family exists and is approved, only a value or the tagger's coverage is missing. Values inside an approved family are accepted with the family.

| Item | Verdict | Decision |
|---|---|---|
| `condition:kicked` | REDUNDANT: exists (2 cards). The gap is pattern N-abstraction in the renderer | no tag; moves to B (key numbers) |
| `target_scope:random_opponent` | new value of approved `target_scope` | APPROVED value |
| `condition:opp_more_creatures`, `condition:opp_more_lands` | new values of approved `condition` | APPROVED values |
| `roll_die` + `die_sides:N` | new family (sibling of approved `flip_coin`) | APPROVED family (APPROVED_DECISION in tag_reports.py) |
| spell-type filter on cast triggers | REDUNDANT: `trigger_filter` already holds card types and subtypes (instant, sorcery, goblin) | no tag; tagger must emit Spirit/Arcane values it misses |
| `trigger_scope:cast_self`, `cast_targeting_self` | new values; `trigger_scope` is documented for zone-change triggers only | APPROVED values; extend the DOC row |
| `optional` | REDUNDANT: exists (40 groups). Gap is attaching it to the right effect | tagger fix, no tag |
| attacker / source filters | REDUNDANT family (`trigger_filter`, `target_filter`); missing values like `without_flying` | APPROVED values `trigger_filter:without_<kw>` |
| `trigger_scope:commander`, `one_or_more` | `one_or_more` REDUNDANT (7 cards); `commander` is a new value | APPROVED value commander |
| `trigger_filter:mv_le_N` (type filter) | type filter REDUNDANT; `mv_le_N` new, mirrors `power_le_N` | APPROVED value |
| saga chapter text | `saga_chapter` exists but drops the number (TAG_REFERENCE says so) | APPROVED value `saga_chapter:N` |
| channel | no `channel` row in TAG_REFERENCE | check `kw` coverage in tag_extra before adding; not approved yet |
| keyword costs hidden by N; numbers hidden by N | REDUNDANT: `kw` says costs/numbers follow as separate tags; `damage_amount`, `look_top` etc. carry numbers. Lost in `pattern()` | no tag; renderer work, now B0 |
| 0-unit cards (Cone of Cold, Selective Adaptation, The Ring Goes South, Berserker's Frenzy) | parse failures | per-card tagger fix |

Approved new tag work: 1 family (`roll_die`, with `die_sides`), 10 values. Not implemented yet: the tagger change comes with the retag.

## B. Renderer rule gaps: the tags exist, `mtg2llm` has no sentence yet (not retag work)
Units without a rule, biggest first:
- keywords: typecycling 103, cascade 41, fear 34, storm 33, landwalk 33 + 26 (swamp, forest), bushido 32, horsemanship 28, wither 26, persist 23, soulshift 23, modular 22, flashback 22/18, evolve 21, devour 21, intimidate 20, renown 20, disturb 20/20, bloodthirst 20, exploit 20, unearth 19, madness 16/14, fabricate 16, assist 16, extort 15, flanking 15, multikicker 17, reconfigure 14, buyback 14, riot 13, suspend 13, exhaust 13, unleash 14, umbra armor 14
- surveil 72 (and 26 on ETB), untap 60, blocks trigger 33, effect:sacrifice 20, remove:destroy 20, prevent_damage 18, `cost:remove_counters` 29, `cost:sacrifice` 23
- counters: energy on ETB 59, pNpN on combat damage 31, pNpN on spell cast 33, ki counter 16
- grants: flying 37 / 30, vigilance 33, first strike 20 / 18, haste 20, menace 17, hexproof 14, protection 28 / 14, trample 22
- mill on ETB 43, bounce on ETB 41, damage to all creatures 32 / 19, damage replacement 26, counter-unless-pay 26, discard on combat damage 25

## C. Already listed
- `tags/MTG2LLM_GAPS.toon`: 73 rows open (209 total, 136 applied), e.g. Aethertide Whale, Alms Collector, Angrath's Marauders, Arbiter of Woe, Ashcoat of the Shadow Swarm, Barrowgoyf, Blight Titan, Braids's Frightful Return.

## Plan for B (mtg2llm rules; goal: starter pool no-rule units 297 down, then pool-wide 46% down)
Order matters: a tag change re-keys mined rules and hand lines, so the retag (A) comes first, then B.
1. **B0 DONE 2026-10-27 (corrected):** `pattern()` was not the cause; the K: parser wrote the cost as `num:5 color:black`, losing the pip count ({5}{B}{B}). Now `tag_run.kw_tags` also writes `cost_mana:5bb` for cost keywords (single-cost lines only), and `mtg2llm._kw_cost_line` renders "Name {cost}" generically (flashback, kicker, cycling, mutate, buyback, madness, unearth, morph, ...). 14 cost-baked hand lines removed. Escape/awaken/suspend (extra numbers) stay hand-lined. Starter-pool no-rule units 301 -> 287. Tags changed, so STARTER_TAGS and pool.pkl need the regenerate on the next tag run.
2. **B1 keyword sentences (about 700 units):** generate from `ai_lab/KEYWORD_REMINDER_TEXT.toon`, one rule per keyword, Oracle-accurate wording: typecycling, cascade, fear, storm, landwalk, bushido, horsemanship, wither, persist, soulshift, modular, flashback, evolve, devour, intimidate, renown, disturb, bloodthirst, exploit, unearth, madness, fabricate, assist, extort, flanking, multikicker, reconfigure, buyback, riot, suspend, exhaust, unleash, umbra armor.
3. **B2 grant-keyword effects (about 250):** flying, vigilance, first strike, haste, menace, hexproof, protection, trample on auras and pump.
4. **B3 ETB and zone effects (about 400):** surveil, untap, energy counters, mill, bounce, damage to all creatures, damage replacement, counter-unless-pay, discard on combat damage.
5. **B4 triggers and costs (about 250):** blocks trigger, pNpN counters on combat damage or spell cast, `cost:remove_counters`, `cost:sacrifice`, effect:sacrifice, remove:destroy, prevent_damage.
6. After each batch: `mtg2llm.py selftest`, guards, `mtg2llm.py scan`; record the no-rule count in the log. A batch is done when its units fall to the long tail of one-offs.
7. Leftover one-offs (12,973 patterns seen once) are not worth rules; hand lines only for starter-pool cards.
Needs your word before B starts: B0 changes `pattern()` and re-keys hand_units.json.

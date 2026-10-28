# Tag syntax: a structured view of the existing tags (design draft, nothing built)

User request 2026-10-27: the tags should follow the order of the Oracle text and have their own syntax; goal is a better structure on the existing tag base, not new tags. Draft by the main session for review. No code changed. Companion to `TAG_LINKS.md` (links between groups) and `tags/READER_GRAMMAR.md` (how a reader turns tags into text). mtgish is not used (dropped 2026-10-23, H54).

## 1. Principles
1. **A view, not a new tag set.** Every tag keeps its name. The syntax only groups and orders them. Deleting all `role[` `]` punctuation gives back exactly the flat tag set of the group (the round-trip rule, section 6). The pool, builder, archetype matching and renderer patterns do not change.
2. **Five roles, the ones the code already has.** `trigger`, `cost`, `target`, `duration`, `effect` (`mtg2llm.role()`: trig, cost, target, dur, eff). Condition, optional, scope and limit tags stay inside `effect`, as they do today. A sixth role is added only when a tag family needs it.
3. **Oracle order.** Segments within a group follow the order the phrases appear in the Oracle sentence for that line. Where the parser cannot know, the default order in section 4 applies.
4. **Group ids are unchanged.** `k1`, `c0`, `c1`, `c1.2`, `x` and the `links` list stay as they are. A sub-group `cN.M` is still the next step of ability `cN`; the syntax does not add a second step separator.
5. **One way to write each thing.** Fixed segment names, one bracket form, one ordering rule, no synonyms.

## 2. Grammar
```
group      := id ":" segment+
id         := k<n> | c0 | c<n>[.<m>] | s<n> | x
segment    := role "[" tag (" " tag)* "]"
role       := "trigger" | "cost" | "target" | "duration" | "effect"
tag        := family[":" value]          (unchanged from TAG_REFERENCE.md)
link       := unchanged: "<group>:<role-word> <relation> <group>:<role-word>"
```
- Lower case, one space between tags, one space between segments, one group per line.
- A segment is never empty and never nested.
- Link role words: TAG_LINKS `affected` = the `target` segment, `payload` = the `effect` segment, `duration` = the `duration` segment. Link lines are not rewritten.

## 3. Which tag goes in which segment
By the existing `role()` rule, applied to the tag family:

| Segment | Families |
|---|---|
| `trigger[...]` | `trigger`, `trigger_*`, `flip-up` |
| `cost[...]` | `cost`, `cost_*` (not `cost_reduce`), including `cost_mana` and `cost_sacrifice_target` |
| `target[...]` | `target_count`, `target_scope`, `target_type`, `target_filter` |
| `duration[...]` | `duration` |
| `effect[...]` | everything else |

`cost_reduce` is an effect (it changes other spells' costs), so it stays in `effect`.

## 4. Splitting `effect` into one segment per effect, and order
Today `effect` is a bag: `draw_count:3 life_loss_amount:3` does not say which amount belongs to which verb. In the view, each effect is its own segment: a **verb tag** followed by the tags bound to it.

- A **verb tag** is a family that names an action (`draw`, `life_loss`, `tutor`, `shuffle`, `put_onto_battlefield`, `remove`, `damage`, `token_make`, ...).
- A **bound tag** is a parameter family of one verb. The binding table (`EFFECT_PARAMS`, to be generated from the "pairs with" notes in `TAG_REFERENCE.md` and `TAG_LEGEND.md`) maps parameter family to verb, for example: `draw_count` to `draw`; `life_loss_amount` to `life_loss`; `tutor_count`, `tutor_target`, `from_zone` to `tutor`; `tutor_dest`, `put_tapped`, `controller` to `put_onto_battlefield`.
- A tag that no verb claims goes into the nearest effect segment before it, and the checker lists it as **unbound**.
- **Order of segments in a group**: the order of the Oracle phrases. When the parser has no phrase position, the default is `trigger`, then `cost`, then each `effect` in the order its verb tag first appears, with its `target` and `duration` written directly after the effect they belong to. Two known Oracle exceptions are written as printed: a leading duration ("Until end of turn, ...") and a leading option ("You may ...", the tag `optional` stays in the effect).
- Multiple targets of one ability: one `target[...]` segment after each effect that has its own.

## 5. Worked examples (real data from `tagged.json`)

**Wayfarer's Bauble** (one activated ability, a search with three phrases):
```
flat:   c1: cost:tap cost:sacrifice cost_sacrifice_target:self cost_mana:2 tutor tutor_count:1 tutor_target:basic_land tutor_dest:battlefield_tapped shuffle put_onto_battlefield from_zone:library put_tapped controller:you
syntax: c1: cost[cost:tap cost:sacrifice cost_sacrifice_target:self cost_mana:2] effect[tutor tutor_count:1 tutor_target:basic_land from_zone:library] effect[put_onto_battlefield tutor_dest:battlefield_tapped put_tapped controller:you] effect[shuffle]
```
Reads as: cost; search for one basic land from the library; put it onto the battlefield tapped under your control; shuffle. The flat form mixes eleven effect tags into one bag.

**Swords to Plowshares** (two steps, with links):
```
syntax: c1:   effect[remove:exile] target[target_count:one target_type:creature]
        c1.2: effect[lifegain_amount:x x_is:target_power]
links (unchanged): c1:affected receives c1:payload ; c1.2:lifegain_amount:x scales_with c1.2:x_is:target_power ; c1.2:x_is:target_power measures c1:target_type:creature
```
The target segment follows its effect, as in "Exile target creature."

**Nazar, the Velvet Fang** (three groups; exposes a data inconsistency):
```
syntax: k1:   effect[kw:menace]
        c1:   trigger[trigger:gain_life]
        c1.2: effect[counter_count:1 counter:feeding]
        c2:   trigger[trigger:attacks]
        c2.2: cost[cost:remove_counters] effect[draw_count:3]
        c2.3: effect[life_loss_amount:3]
        x:    effect[life_loss]
```
Findings the view makes visible: `cost:remove_counters` sits in a step group (`c2.2`) rather than with its trigger group, and the verb tag `life_loss` is in the cross-check group `x`, away from its amount in `c2.3`. The checker flags both; whether the tagger should move them is a separate decision.

**Kodama's Reach** (three steps repeat `shuffle`; the view makes the repeat visible, Oracle shuffles once):
```
syntax: c1:   effect[tutor tutor_count:up_to_2 tutor_target:basic_land tutor_dest:library] effect[shuffle]
        c1.2: effect[tutor tutor_count:1 tutor_target:land_isremembered] effect[put_onto_battlefield tutor_dest:battlefield_tapped put_tapped controller:you] effect[shuffle]
        c1.3: effect[tutor tutor_count:1 tutor_target:land_isremembered tutor_dest:hand] effect[shuffle]
```

## 6. Consistency rules (the checker)
A checker script (`tagsyntax.py check`) runs on every card of the pool and fails on any of these:
1. **Round trip.** Removing the punctuation from the view gives the same tag multiset as the flat group, for every group.
2. **Exactly one place per tag.** No tag in two segments; no tag outside a segment.
3. **Role fit.** A tag sits in the segment its family belongs to (section 3).
4. **Verb first.** Every `effect[...]` starts with a verb tag; a parameter without its verb is reported as unbound, not silently placed.
5. **Binding table is closed.** Every parameter family used in the pool is in `EFFECT_PARAMS` or on an explicit "no verb" list; a new tag family therefore cannot be added without a binding line.
6. **Link ends exist.** Every `group:role-word` in a link points to an existing segment.
7. **Determinism.** Two runs on the same tags give the same text byte for byte.

## 7. What changes elsewhere (nothing is changed yet)
- **Tagger/exports:** a new function renders the view from `groups` plus the binding table. The flat `STARTER_TAGS.toon` stays the source; the view is generated, never hand-edited.
- **Renderer:** `role()` already derives the split, so compose rules stay valid. Per-effect segments allow rendering one clause per effect instead of one text for the whole bag.
- **Readers:** `READER_GRAMMAR.md` rule 1.5 ("effect sentences are in the order their verb tags first appear") is replaced by "one sentence per `effect[...]` segment, in segment order". The legend gets a short paragraph on the five segments.
- **Test:** glance comparison of flat against view on the same cards (readers only on the user's ask) before the view becomes the default export.

## 8. Decisions (user, 2026-10-27)
1. **Binding table:** generated from the "pairs with" notes in `TAG_REFERENCE.md` / `TAG_LEGEND.md`, gaps fixed by hand.
2. **Position data:** the tagger records the Oracle phrase position of each verb (change in `tag_extra.py`); the default order is only the fallback for cards without it.
3. **Unbound tags:** lenient. The checker lists them and does not fail while the binding table is filled.
4. **Misplaced cost and verb tags (Nazar):** fixed in the tagger, not moved by the view.
5. **Reader export format:** brackets (shorter, one line per group), chosen by the main session because the user left it open.

## 9. Build order (nothing built beyond the prototype `tagcheck/tagsyntax.py`)
1. Generate `EFFECT_PARAMS` from the "pairs with" notes; list the gaps.
2. Tagger: record verb phrase position; move cost and verb tags into the group they belong to.
3. `tagsyntax.py check` over the pool (round trip, role fit, link ends, determinism).
4. Renderer: one sentence per `effect[...]` segment; readers: replace rule 1.5 of `READER_GRAMMAR.md`.
5. Glance test of flat against view (readers only on the user's ask).

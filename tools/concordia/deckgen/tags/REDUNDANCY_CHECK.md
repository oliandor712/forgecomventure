# Redundancy check of the tag data

Run by `deckgen/tag_run.py run` on every tag generation (user order 2026-10-22). Rules tags only (AI Tags excluded). A finding is a candidate, not an error: decide to merge, drop or whitelist it in `REDUNDANCY_OK` with a reason. 27699 cards, 25 findings.


## bare+valued (2)

- `cant_be_blocked` and `cant_be_blocked:<value>` both on 4 cards: the bare tag adds nothing the valued tags do not say
- `counter_remove` and `counter_remove:<value>` both on 1 cards: the bare tag adds nothing the valued tags do not say

## same cards (1)

- `counters` and `loyalty` are on exactly the same 287 cards: merge candidates

## values together (12)

- values `affected_filter:chosenmodekhans` and `affected_filter:chosenmodedragons` are always on the same 5 cards: merge candidates
- values `choice_option:khans` and `choice_option:dragons` are always on the same 5 cards: merge candidates
- values `cost_reduce_for:instant` and `cost_reduce_for:sorcery` are always on the same 27 cards: merge candidates
- values `cost_reduce_for:cast` and `cost_reduce_for:from` are always on the same 8 cards: merge candidates
- values `target_filter:power_eq_1` and `target_filter:toughness_eq_1` are always on the same 3 cards: merge candidates
- values `target_filter:nonkraken` and `target_filter:nonleviathan` are always on the same 3 cards: merge candidates
- values `target_filter:nonkraken` and `target_filter:nonoctopus` are always on the same 3 cards: merge candidates
- values `target_filter:nonkraken` and `target_filter:nonserpent` are always on the same 3 cards: merge candidates
- values `target_filter:nonleviathan` and `target_filter:nonoctopus` are always on the same 3 cards: merge candidates
- values `target_filter:nonleviathan` and `target_filter:nonserpent` are always on the same 3 cards: merge candidates
- values `target_filter:nonoctopus` and `target_filter:nonserpent` are always on the same 3 cards: merge candidates
- values `type:time` and `type:lord` are always on the same 29 cards: merge candidates

## implied (5)

- every card with `sacrifice_type` (352) also has `effect` (536): `sacrifice_type` may be implied
- every card with `impulse_draw_count` (337) also has `impulse_draw` (490): `impulse_draw_count` may be implied
- every card with `loyalty_change` (286) also has `loyalty` (287): `loyalty_change` may be implied
- every card with `affects` (82) also has `must_attack` (88): `affects` may be implied
- every card with `flashback` (11) also has `flashback_return` (17): `flashback` may be implied

## single value (5)

- family `counters` has only one value (counters:loyalty) on 287 cards: could be a plain tag
- family `delayed` has only one value (delayed:end_step) on 21 cards: could be a plain tag
- family `die_replace` has only one value (die_replace:exile) on 87 cards: could be a plain tag
- family `restrict_scope` has only one value (restrict_scope:self) on 167 cards: could be a plain tag
- family `win` has only one value (win:alt_condition) on 34 cards: could be a plain tag

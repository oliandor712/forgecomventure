# Redundancy check of the tag data

Run by `deckgen/tag_run.py starter` on every tag generation (user order 2026-10-22). Rules tags only (AI Tags excluded). A finding is a candidate, not an error: decide to merge, drop or whitelist it in `REDUNDANCY_OK` with a reason. 571 cards, 4 findings.


## values together (1)

- values `target_type:instant` and `target_type:sorcery` are always on the same 5 cards: merge candidates

## implied (2)

- every card with `sacrifice_type` (9) also has `effect` (11): `sacrifice_type` may be implied
- every card with `cost_reduce_for` (8) also has `cost_reduce_amount` (11): `cost_reduce_for` may be implied

## single value (1)

- family `cant_be_blocked` has only one value (cant_be_blocked:by_creature_blue) on 3 cards: could be a plain tag

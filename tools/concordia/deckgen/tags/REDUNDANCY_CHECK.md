# Redundancy check of the tag data

Run by `deckgen/tag_run.py starter` on every tag generation (user order 2026-10-22). Rules tags only (AI Tags excluded). A finding is a candidate, not an error: decide to merge, drop or whitelist it in `REDUNDANCY_OK` with a reason. 353 cards, 15 findings.


## bare+valued (1)

- `recursion` and `recursion:<value>` both on 1 cards: the bare tag adds nothing the valued tags do not say

## same cards (2)

- `put_from` and `put_onto_battlefield` are on exactly the same 26 cards: merge candidates
- `haste` and `haste_grant` are on exactly the same 3 cards: merge candidates

## implied (5)

- every card with `land_tutor` (13) also has `tutor` (17): `land_tutor` may be implied
- every card with `land_tutor` (13) also has `tutor_count` (16): `land_tutor` may be implied
- every card with `land_tutor` (13) also has `tutor_target` (16): `land_tutor` may be implied
- every card with `land_tutor` (13) also has `tutor_dest` (16): `land_tutor` may be implied
- every card with `land_tutor` (13) also has `shuffle` (16): `land_tutor` may be implied

## single value (7)

- family `cost_reduce_for` has only one value (cost_reduce_for:creature) on 3 cards: could be a plain tag
- family `effect` has only one value (effect:sacrifice) on 3 cards: could be a plain tag
- family `exile_from` has only one value (exile_from:graveyard) on 3 cards: could be a plain tag
- family `recursion` has only one value (recursion:return_self) on 7 cards: could be a plain tag
- family `target_zone` has only one value (target_zone:graveyard) on 15 cards: could be a plain tag
- family `token_cardtype` has only one value (token_cardtype:artifact) on 13 cards: could be a plain tag
- family `trigger_zone` has only one value (trigger_zone:graveyard) on 20 cards: could be a plain tag

# P4c D: per-card check of the `no_tags` placeholder cards

Date 2026-10-23. Checked each card's tag groups against its Forge script. Update 2026-10-23 after the user approved F, G, H, I (J declined): the gaps below are fixed unless listed under Still open.

Done in P4c (A, B, C, E), checked on sample cards and a full starter regeneration (353 cards, redundancy 0 findings):
- A: `trigger_filter:<cardtype>` now emitted (creature 34, land 6, instant 6, sorcery 6, artifact 2).
- B: negation form `trigger_filter:noncreature` (8). The junk `trigger_filter:card` is gone.
- C: `x_is:previous_result` (Creeping Bloodsucker and 2 more).
- E: `cost_mana:<compact>` (75 uses, 37 cards) and `unless_cost_amount:<n>` (12 uses). Both are listed as "[ ] proposed" in NEW_TAGS_FOR_APPROVAL.md.

Fixed (regenerated 353 cards, redundancy 0 findings):

| Card | Now tagged |
|---|---|
| Thraben Inspector | `investigate` (F, new family; also Fateful Absence) |
| Elite Scaleguard | `bolster:2` (G, new family) |
| Palace Jailer | `monarch` (H, new family), `duration:until_monarch_changes` (I, new value) |
| Loyal Apprentice | `trigger:beginning_of_combat` |
| Nazar | `trigger:gain_life`, `cost:remove_counters` in the attack trigger's draw group |
| Desecrate Reality | `target_filter:even_mana_value` / `odd_mana_value`, `target_scope:each_opponent` |
| Hunted Wumpus | `target_scope:each_other_player` (new value, not in the approved list: confirm), `target_type:creature`, `optional` |
| Herald's Horn | no longer a false tutor; `take:may_1_chosen_type`, `to_zone:hand`, `trigger:upkeep` |
| Daretti | already had the sacrifice and return tags in c2 / c2.2; only the ultimate's emblem trigger (artifact dies, returns at end step) stays untagged |

Still open:
- Elite Scaleguard: the tap effect ("tap target creature defending player controls") has no tag (no approved tap-effect family; `tap_down` means keep tapped).
- Scorch Spitter: damage target "the player or planeswalker it's attacking" (J declined).
- Daretti's emblem trigger (see above).

Side effect: Herald's Horn no longer carries tutor tags, so every card with `tutor_*` also has `shuffle`; whitelisted in `REDUNDANCY_OK` (tag_run.py) with the reason.

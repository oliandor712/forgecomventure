# New tags created for approval

Created 2026-10-22 under the standing instruction (human_logic.toon H56): tags may be created to fill gaps seen across the references (script, mtgish, Forge AI, rules, keyword reference, user feedback); each is logged here and counts as PROPOSED until approved. Only families that wait for approval are listed; the 57 families approved on 2026-10-22 are in `APPROVED_TAGS_ARCHIVE.md`. Tick a box to approve a family; strike or note a change under it. Counts are from the starter-deck run (353 cards).
Changes to existing behaviour (approved with "approve all tags", 2026-10-22; treated as covered by that order, say if not): (a) the umbrella tag `removal` is dropped when a method tag (`remove:*`, `damage`) is present; (b) a keyword is listed once as `kw:<name>`, the plain duplicate (e.g. `trample`) is dropped.

| Approve | Tag family | Meaning | Source of the rule | Cards | Values seen (cards) |
|---|---|---|---|---|---|
| [ ] proposed | `return` | a card returns from the graveyard or exile to hand or library (return from_zone:graveyard to_zone:hand); the readable detail behind the AI umbrella tag recursion. from_zone / to_zone are the shared zone tags used by every zone-move tag (return, take, put_onto_battlefield, cost:exile) | reverse check r5: Elvish Regrower lost its meaning when recursion became an AI tag | 9 (e.g. Cadaver Imp, Gravedigger, Raise Dead) | return (9) |
| [ ] proposed | `cost_reduce_amount` | (see feedback notes) | created from the user feedback pattern | 6 (e.g. Goreclaw, Terror of Qal Sisma, Dragonlord's Servant, Stonybrook Banneret) | cost_reduce_amount:1 (5); cost_reduce_amount:2 (1) |
| [ ] proposed | `choose_on_enter` | (see feedback notes) | created from the user feedback pattern | 2 (e.g. Cloud Key, Herald's Horn) | choose_on_enter:card_type (1); choose_on_enter:creature_type (1) |

## New values inside already-approved families (the family is approved; these values appeared after the approval)

Say if any should be changed; unmarked means accepted with the family.

| Family | New values (cards) |
|---|---|
| `ai_logic` | ai_logic:always (3); ai_logic:pump (2); ai_logic:powerdmg (2); ai_logic:fight (2); ai_logic:curse (2); ai_logic:atoppeot (1); ai_logic:foodortreasure (1); ai_logic:ateotifnotattacking (1); ai_logic:cantregenerate (1); ai_logic:makeunblockable (1); ai_logic:manaritual (1); ai_logic:mostprominentincomputerdecknontoken (1); ai_logic:gaincontrol (1); ai_logic:bestopportunity (1) |
| `from_zone` | from_zone:graveyard (19); from_zone:library (11); from_zone:exile (5); from_zone:hand (1) |
| `take` | take:2 (2); take:all (2); take:all_goblin (1); take:may_1_creature_power_le_2 (1) |
| `cost_reduce_for` | cost_reduce_for:chosen_type (2); cost_reduce_for:dragon (1); cost_reduce_for:merfolk (1); cost_reduce_for:wizard (1) |
| `to_zone` | to_zone:hand (12); to_zone:exile (2); to_zone:library (1) |
| `rest_to_zone` | rest_to_zone:graveyard (1); rest_to_zone:library (1) |
| `x_is` | x_is:greatest_power_among_creature_you_control_nonhuman (1); x_is:greatest_power_among_creature_you_control (1) |
| `rest_order` | rest_order:bottom_random (1) |

## Tag names that were merged or renamed (the old names no longer exist)

- `mode_count` + `mode_choose` -> `modal:<chosen>_of_<modes>`; `take_count` / `take_filter` / `take_dest` / `take_optional` / `rest_random_order` -> `take:...` + `to_zone:...` and `rest_to_zone:...` + `rest_order:...`; `return:<zone>_to_<zone>`, `put_onto_battlefield:from_<zone>`, `cost:exile_from_graveyard` -> bare tag + `from_zone:` / `to_zone:` zone tags; `piles_split` + `pile_separator` -> `piles_split:<who>`.
- `x_is:<what>` values were renamed to readable words (e.g. `count_swamp_youctrl` -> `count_swamp_you_control`); `restrict` now also carries `restrict_kind:<kind>`.
- `transform` was removed from Feign Death, Supernatural Stamina and Merfolk Trickster (they grant or remove abilities); `sacrifice_outlet` was removed from 14 cards that sacrifice only themselves (user rule).
- Segregated, kept intact: AI Tags (`tempo:*`, `ai_logic:*`, `burn`, `removal`, `selection`, `fixing`, `restrict`, `pump_team`, `artifact_token`, `land_tutor`, bare `recursion`, every `<kw>_grant` and the bare keyword tags on cards that only grant a keyword) sit on the `ai_tags:` line and are hidden from the blind reader and from the redundancy check.

## Waiting on the user
- Nothing is waiting for approval: all families, the two behaviour changes and the merged tags were approved on 2026-10-22. New families created by later runs are listed in the table above as proposed.
- Still open (not an approval): confirm the AI Tags list (tempo, ai_logic, burn, removal, selection, fixing, restrict, pump_team, artifact_token).

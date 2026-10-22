# New tags created for approval

Created 2026-10-22 under the standing instruction (human_logic.toon H56): tags may be created to fill gaps seen across the references (script, mtgish, Forge AI, rules, keyword reference, user feedback); each is logged here and counts as PROPOSED until approved. Only families that wait for approval are listed; the 57 families approved on 2026-10-22 are in `APPROVED_TAGS_ARCHIVE.md`. Tick a box to approve a family; strike or note a change under it. Counts are from the starter-deck run (353 cards).
Changes to existing behaviour (approved with "approve all tags", 2026-10-22; treated as covered by that order, say if not): (a) the umbrella tag `removal` is dropped when a method tag (`remove:*`, `damage`) is present; (b) a keyword is listed once as `kw:<name>`, the plain duplicate (e.g. `trample`) is dropped.

| Approve | Tag family | Meaning | Source of the rule | Cards | Values seen (cards) |
|---|---|---|---|---|---|
| | *No family waits for approval.* | | | | |

## New values inside already-approved families (the family is approved; these values appeared after the approval)

Say if any should be changed; unmarked means accepted with the family.

| Family | New values (cards) |
|---|---|
| `ai_logic` | ai_logic:always (3); ai_logic:pump (2); ai_logic:powerdmg (2); ai_logic:fight (2); ai_logic:curse (2); ai_logic:atoppeot (1); ai_logic:foodortreasure (1); ai_logic:ateotifnotattacking (1); ai_logic:cantregenerate (1); ai_logic:makeunblockable (1); ai_logic:manaritual (1); ai_logic:mostprominentincomputerdecknontoken (1); ai_logic:gaincontrol (1); ai_logic:bestopportunity (1) |

## Tag names that were merged or renamed (the old names no longer exist)

- `mode_count` + `mode_choose` -> `modal:<chosen>_of_<modes>`; `take_count` / `take_filter` / `take_dest` / `take_optional` / `rest_random_order` -> `take:...` and `rest_dest:...`; `piles_split` + `pile_separator` -> `piles_split:<who>`.
- `x_is:<what>` values were renamed to readable words (e.g. `count_swamp_youctrl` -> `count_swamp_you_control`); `restrict` now also carries `restrict_kind:<kind>`.
- `transform` was removed from Feign Death, Supernatural Stamina and Merfolk Trickster (they grant or remove abilities); `sacrifice_outlet` was removed from 14 cards that sacrifice only themselves (user rule).
- Segregated, not removed: AI Tags (`tempo:*`, `ai_logic:*`, `burn`, `removal`, `selection`, `fixing`, `restrict`, `pump_team`, `artifact_token`) sit on the `ai_tags:` line and are hidden from the blind reader.

## Waiting on the user
- Nothing is waiting for approval: all families, the two behaviour changes and the merged tags were approved on 2026-10-22. New families created by later runs are listed in the table above as proposed.
- Still open (not an approval): confirm the AI Tags list (tempo, ai_logic, burn, removal, selection, fixing, restrict, pump_team, artifact_token).

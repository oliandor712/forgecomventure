# Theme whitelist for the starter builder (fillable, for approval)

Written 2026-10-28. Only for the planned starter-builder theme rework (nothing is implemented yet). A theme is a thing a deck can be built around beyond the commander's own text; it can unlock only when its tag family is on this list. Role tags (removal, draw, ramp, wipe, tutor, fast) are deck-structure slots, not themes, and stay out.

## Decisions already made (user 2026-10-28)
- Unlock guard: **3 payoffs, or 2 payoffs + a commander that makes or targets the type** (was 2, or 1 + commander).
- **Equipment and Vehicle** may be themes.
- No W rebuild (`W_Starter_Regen_r7`) until the user says so.
- Still open: members counted per payoff (plan said 3; anthems maybe more). Write a number: members per payoff = ____ , anthem/lord payoff = ____

## How to fill it
Tick one box per row: **T** = may be a theme, **P** = tags of this family only count as a payoff (never a theme on their own), **N** = never. Leave a comment in the last column if a row needs a limit.

Columns: family, example tags, what makes a member, what makes a payoff.

| T | P | N | Category | Tag families / examples | Member (the deck has supply) | Payoff (rewards the supply) | Your note |
|---|---|---|---|---|---|---|---|
| [ ] | [ ] | [ ] | Creature tribe | `tribe:<type>`, `lord:<type>`, `affects:<type>`, `affected_filter:<type>`, `cost_reduce_for:<type>` | a creature of the type, or a maker of it | lord, anthem for the type, cost reducer | |
| [ ] | [ ] | [ ] | Tokens (general) | `token_make`, `token_type:*`, `token_count:*`, `token_scales:<Y>`, `token_pt` | token makers | `power_scales`, anthems, sacrifice outlets, `token_scales` cards | |
| [ ] | [ ] | [ ] | Treasure / Food / Clue / Blood / Gold / Junk / Powerstone | `token_type:treasure`, `token_type:food`, `investigate` | makers | cards that sacrifice or count them | |
| [ ] | [ ] | [ ] | Equipment | `kw:equip`, `kw:reconfigure`, `kw:living_weapon`, attached-to payoffs | Equipment cards, equip tutors | cards that count or move Equipment, "equipped creature" triggers | |
| [ ] | [ ] | [ ] | Vehicles | `kw:crew`, vehicle types | Vehicles | crew helpers, cards that count Vehicles | |
| [ ] | [ ] | [ ] | Auras / enchantments | `kw:enchant`, `niche:enchantment`, `token_cardtype:enchantment` | enchantments, aura cards | enchantress draw, aura-count payoffs | |
| [ ] | [ ] | [ ] | Artifacts | `niche:artifact`, `token_cardtype:artifact`, `cost_reduce_for:artifact` | artifacts, artifact makers | artifact-count payoffs, cost reducers | |
| [ ] | [ ] | [ ] | +1/+1 counters | `counters_plus`, `counter:p1p1`, `counter_count`, `bolster`, `proliferate` | counter placers | proliferate, counter-doubling, `scales:counters` | |
| [ ] | [ ] | [ ] | Other counters / energy / poison | `counter:energy`, `counter:*` other than p1p1, `poison` | placers | spenders | |
| [ ] | [ ] | [ ] | Lifegain | `lifegain`, `lifegain_amount`, `lifelink` | gain sources | payoffs on gain, `scales` on life | |
| [ ] | [ ] | [ ] | Life loss / drain | `life_loss`, `life_loss_amount` | drainers | payoffs on loss | |
| [ ] | [ ] | [ ] | Graveyard | `from_zone:graveyard`, `recursion`, `reanimate`, `scales:graveyard`, `self_mill`, `mill` | fillers (mill, discard) | reanimation, recursion, graveyard-count payoffs | |
| [ ] | [ ] | [ ] | Sacrifice | `sacrifice_outlet`, `cost_sacrifice_target:*`, `sacrifice_type:*` | fodder, makers | outlets, "whenever a creature dies" payoffs | |
| [ ] | [ ] | [ ] | Enter-the-battlefield / blink | `trigger:etb`, `flicker`, `bounce` own creature | ETB creatures | blinkers, ETB doublers | |
| [ ] | [ ] | [ ] | Landfall / lands | `extra_land_drop`, `trigger:landfall`, `niche:lands`, `put_onto_battlefield` land | land ramp | landfall payoffs | |
| [ ] | [ ] | [ ] | Spells matter | `trigger:cast`, instants and sorceries, `cost_reduce_for:instant_or_sorcery`, `impulse_draw` | cheap instants and sorceries | cast triggers, copy effects | |
| [ ] | [ ] | [ ] | Discard / hand attack | `discard`, `discard_count`, `hellbent` | discard sources | payoffs on discard | |
| [ ] | [ ] | [ ] | Draw | `draw`, `draw_count`, `cantrip` | draw spells | draw payoffs ("whenever you draw") | |
| [ ] | [ ] | [ ] | Pump / anthem / keywords | `pump_amount`, `grant_kw`, `affected_scope:you_control`, `lord`, `anthem` | creatures that benefit | n/a (payoff only) | |
| [ ] | [ ] | [ ] | Evasion / combat | `evasion`, `cant_be_blocked`, `must_attack`, `trample`, `fight` | evasive creatures | extra-combat and damage-trigger payoffs | |
| [ ] | [ ] | [ ] | Damage / pingers | `damage`, `damage_amount`, `kw:wither` | damage sources | "whenever damage is dealt" payoffs | |
| [ ] | [ ] | [ ] | Mana / ramp | `mana_source`, `mana_amount`, `setup_card:mana` | rocks, dorks | mana sinks (`mana_sink`) | |
| [ ] | [ ] | [ ] | Chaos | `niche:chaos`, `flip_coin`, `roll_die`, `secret_choice` | randomisers | payoffs on rolls and flips | |
| [ ] | [ ] | [ ] | Monarch / initiative / Dungeon | `monarch`, `mech:monarch`, `initiative`, `Dungeon` | sources | defenders and evasion | |
| [ ] | [ ] | [ ] | Colourless / Eldrazi | `colorless_card`, `mana_filter` | colourless cards | cost reducers for colourless | |

## Never themes (structure, listed for completeness)
`trigger`, `trigger_scope`, `trigger_filter`, `trigger_zone`, `target_*`, `cost` and `cost_*` families, `duration`, `x_is`, `num`, `optional`, `controller`, `to_zone`, `from_zone` (alone), `condition`, `limit`, `modal`, `shuffle`, `scry_count`, `look_top`, `forge_line`, and the six role tags. Add to this list or move a row from the table if you disagree: ____

## After you fill it
I read your ticks, record the rules as H109 in `human_logic.toon` (H104-H108 are already used), implement the candidate-theme finder in `starter_build.py` (members + n x payoffs, the new guard, dynamic `allowed`, matching "themes unlocked" print), run `pool.py` if a tag changes, and wait for your word before any build.

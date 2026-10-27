# Role quotas by archetype and tier (PROPOSAL, not applied)

Status: draft for the user. Nothing in `tier_rules.py` or `build.py` has been changed.

## Rule (user, 2026-10-27)
The engine goals and archetype role slots harvested from deck data (`tools/agents/reference/ARCHETYPES.toon`, `tools/concordia/strategies/strategies.json`) apply from Tier 1 up and reach 100% of their range at Tier 3. Tiers 4 and 5 stay at 100% (they differ by card strength, not by role counts).

Assumption (not stated by the user, please confirm): the ramp is linear, Tier 1 = 1/3, Tier 2 = 2/3, Tier 3-5 = 100% of both ends of the range, rounded to whole cards. The role is the archetype's own range when it lists one, else the engine goal.

Engine goals (every deck): ramp 10-12, card draw 8-12, recursion 2-5, protection 3-6. Archetype uplift replaces them where listed (recursion: graveyard/reanimator/self_mill 8-12 ...; protection: voltron/equipment/tokens/counters/combo/infect 6-10).

Not covered here (kept at the current per-tier bounds in `tier_rules.py` until the user decides): removal, board wipes, tutors, fast mana, lands. Archetype slots marked `-` in ARCHETYPES.toon have no count and are omitted.

## 1. Engine roles by archetype and tier (T1 / T2 / T3+)
| Archetype | Ramp | Draw | Recursion | Protection |
|---|---|---|---|---|
| aristocrats | 3-4 / 7-8 / 10-12 | 3 / 5-7 / 8-10 | 1-3 / 3-5 / 4-8 | 1-2 / 2-4 / 3-6 |
| tokens | 3 / 5-7 / 8-10 | 2-3 / 4-5 / 6-8 | 1-2 / 1-3 / 2-5 | 2-3 / 4-7 / 6-10 |
| tribal | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| voltron | 3 / 5-7 / 8-10 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 2-3 / 4-7 / 6-10 |
| equipment | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 2-3 / 4-7 / 6-10 |
| reanimator | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 3-4 / 5-8 / 8-12 | 1-2 / 2-4 / 3-6 |
| graveyard | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 3-4 / 5-8 / 8-12 | 1-2 / 2-4 / 3-6 |
| mill | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-3 / 3-5 / 4-8 | 1-2 / 2-4 / 3-6 |
| spellslinger | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| storm | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| combo | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 2-3 / 4-7 / 6-10 |
| counters | 3 / 5-7 / 8-10 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 2-3 / 4-7 / 6-10 |
| infect | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 2-3 / 4-7 / 6-10 |
| lifegain | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| blink | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 2-4 / 3-6 | 1-2 / 2-4 / 3-6 |
| landfall | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1 / 1-2 / 2-3 | 1-2 / 2-4 / 3-6 |
| big_mana | 4-5 / 8-10 / 12-15 | 3 / 5-7 / 8-10 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| stax | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| control | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| group_hug | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| enchantress | 3-4 / 7-8 / 10-12 | 2-3 / 4-7 / 6-10 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| artifacts | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| superfriends | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| burn | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| stompy | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| lands_matter | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1 / 1-2 / 2-3 | 1-2 / 2-4 / 3-6 |
| outlaws | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| clones | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| extra_combats | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| mutate | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 3-4 / 4-6 |
| polymorph | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 3-4 / 4-6 |
| self_mill | 3-4 / 7-8 / 10-12 | 2-3 / 4-5 / 6-8 | 3-4 / 5-8 / 8-12 | 1-2 / 2-4 / 3-6 |
| energy | 3-4 / 7-8 / 10-12 | 2-3 / 4-5 / 6-8 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| vehicles | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| sagas | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| discard | 3-4 / 7-8 / 10-12 | 2-3 / 4-5 / 6-8 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| group_slug | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| forced_combat | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 3-4 / 4-6 |
| pillow_fort | 3-4 / 7-8 / 10-12 | 2-3 / 4-5 / 6-8 | 1-2 / 1-3 / 2-5 | 1-2 / 2-3 / 3-5 |
| upkeep_triggers | 3-4 / 7-8 / 10-12 | 2-3 / 4-5 / 6-8 | 1-2 / 1-3 / 2-5 | 1-2 / 2-3 / 3-5 |
| treasure | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| wheels | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| impulse_draw | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| legends_matter | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |
| theft | 3-4 / 7-8 / 10-12 | 3-4 / 5-8 / 8-12 | 1-2 / 1-3 / 2-5 | 1-2 / 2-4 / 3-6 |

Base at T3+: ramp 10-12, draw 8-12, recursion 2-5, protection 3-6.

## 2. Archetype-specific slots by tier (T1 / T2 / T3+)
Slots already in section 1 are not repeated.

- **aristocrats**: fodder 3-4 / 7-8 / 10-12; outlet 2-3 / 3-5 / 5-8; payoff 3 / 5-7 / 8-10; edict 2-3 / 4-5 / 6-8
- **tokens**: generator 3-5 / 7-9 / 10-14; doubler 1 / 1-3 / 2-4; anthem 1-2 / 3-4 / 4-6
- **voltron**: attach 4-6 / 8-12 / 12-18; attach_helper 1-2 / 3-4 / 4-6
- **equipment**: equipment 3-5 / 7-9 / 10-14; carrier 4-6 / 8-12 / 12-18
- **reanimator**: enabler 2-3 / 4-5 / 6-8; reanimation 3-4 / 5-8 / 8-12; target 2-3 / 4-7 / 6-10
- **graveyard**: filler 3 / 5-7 / 8-10; backup_engine 0-1 / 1 / 1-2
- **mill**: engine 3-4 / 5-8 / 8-12; doubler 1 / 1-2 / 2-3; interaction 3 / 5-7 / 8-10
- **spellslinger**: payoff 2-3 / 4-7 / 6-10; cantrip 3-4 / 5-8 / 8-12; spells 8-12 / 17-23 / 25-35
- **storm**: payoff 1 / 1-2 / 2-3; spells 8-12 / 17-23 / 25-35
- **combo**: tutor 2-3 / 3-7 / 5-10; payoff_engine 1 / 1-2 / 2-3
- **counters**: multiplier 1-2 / 2-3 / 3-5; enabler 5-7 / 10-13 / 15-20; proliferate 1-3 / 3-5 / 4-8; draw_payoff 2-3 / 4-5 / 6-8
- **infect**: creature 5-7 / 10-13 / 15-20; pump 2-3 / 4-7 / 6-10; proliferate 2-3 / 3-5 / 5-8
- **lifegain**: trigger 3-4 / 5-8 / 8-12; payoff 2-3 / 4-7 / 6-10; interaction 2-3 / 4-5 / 6-8
- **blink**: flicker 3-4 / 5-8 / 8-12; etb_creature 7-8 / 13-17 / 20-25
- **landfall**: payoff 3 / 5-7 / 8-10; extra_drop 1-2 / 3-4 / 4-6; interaction 2 / 3-5 / 5-7
- **big_mana**: multiplier 1 / 1-3 / 2-4; haymaker 1-2 / 3-4 / 4-6; interaction 2 / 3-5 / 5-7
- **stax**: lock 3-4 / 5-8 / 8-12; parity_breaker 1-2 / 3-4 / 4-6; win 0-1 / 1 / 1-2
- **control**: answer 3-4 / 5-8 / 8-12; sweeper 2-3 / 4-7 / 6-10; finisher 1 / 1-2 / 2-3
- **group_hug**: shared 3-4 / 5-8 / 8-12; breaker 1-2 / 3-4 / 4-6
- **artifacts**: artifact 8-12 / 17-23 / 25-35; cost_reducer 1-2 / 2-3 / 3-5
- **stompy**: creature 8-12 / 17-23 / 25-35; big_body 3-4 / 5-8 / 8-12; anthem 1 / 1-3 / 2-4; extra_combat 1 / 1-2 / 2-3
- **lands_matter**: ramp_land 3-4 / 5-8 / 8-12; payoff 2-3 / 4-7 / 6-10; interaction 2 / 3-5 / 5-7
- **outlaws**: outlaw 6-9 / 12-19 / 18-28; lord 1-2 / 2-4 / 3-6
- **clones**: clone 3-5 / 7-11 / 10-16; etb_target 3-5 / 7-9 / 10-14; remove 2-3 / 4-5 / 6-8
- **extra_combats**: extra_combat 2-3 / 4-7 / 6-10; attack_trigger 3-4 / 5-8 / 8-12; pump 1 / 1-3 / 2-4
- **mutate**: mutate 4-7 / 8-13 / 12-20; target 4-6 / 8-12 / 12-18
- **polymorph**: polymorph 2-3 / 4-7 / 6-10; fodder 3-4 / 5-8 / 8-12; bomb 2-3 / 4-7 / 6-10
- **self_mill**: filler 3-4 / 5-8 / 8-12; payoff 1-2 / 2-3 / 3-5
- **energy**: producer 4-6 / 8-12 / 12-18; payoff 2-3 / 4-7 / 6-10
- **vehicles**: vehicle 3-4 / 5-8 / 8-12; crew 4-6 / 8-12 / 12-18; payoff 1-2 / 2-4 / 3-6; remove 2 / 3-5 / 5-7
- **sagas**: saga 4-7 / 8-13 / 12-20; reuse 1-3 / 3-5 / 4-8; enabler 3 / 5-7 / 8-10
- **discard**: discard 3-4 / 5-8 / 8-12; punisher 1-2 / 2-4 / 3-6; remove 2-3 / 4-5 / 6-8
- **group_slug**: slug 3-4 / 5-8 / 8-12; lifegain 1-2 / 3-4 / 4-6; blocker 3-5 / 7-9 / 10-14; remove 2 / 3-5 / 5-7
- **forced_combat**: force 2-3 / 4-7 / 6-10; blocker 3-5 / 7-9 / 10-14; remove 2 / 3-5 / 5-7
- **pillow_fort**: fort 3-4 / 5-8 / 8-12; finisher 1 / 1-3 / 2-4
- **upkeep_triggers**: engine 3-5 / 7-11 / 10-16; doubler 1 / 1-3 / 2-4
- **theft**: steal 3-4 / 5-8 / 8-12; remove 2 / 3-5 / 5-7

# Role quotas by archetype (PROPOSAL, not applied)

Status: draft for the user (revised 2026-10-27). Nothing in `tier_rules.py` or `build.py` has been changed.

## Rule (user, 2026-10-27)
No tier-based role-count restrictions. One quota per archetype, taken straight from the archetype research (`tools/agents/reference/ARCHETYPES.toon`, `tools/concordia/strategies/strategies.json`), the same at every tier. The tier is set by the deck's power score alone (`power_scorer.py`: average card power band, cards at power 50+/70+), not by how many ramp, draw or other role cards it holds.

Engine goals (every deck): ramp 10-12, card draw 8-12, recursion 2-5, protection 3-6. The archetype's own range replaces them where it lists one (recursion: graveyard/reanimator/self_mill 8-12 ...; protection: voltron/equipment/tokens/counters/combo/infect 6-10).

Not covered (decide separately): removal, board wipes, tutors, fast mana and lands have no research counts, so the per-tier bounds in `tier_rules.py` would simply go with the rest. The hard gates (Game Changers, extra turns, mass land denial, mechanics by tier, watch-list) are not role counts and are NOT removed here; confirm whether they stay. Archetype slots marked `-` have no count and are omitted. Niche archetypes with no counts fall back to the engine goals.

## 1. Engine roles by archetype
| Archetype | Ramp | Draw | Recursion | Protection |
|---|---|---|---|---|
| aristocrats | 10-12 | 8-10 | 4-8 | 3-6 |
| tokens | 8-10 | 6-8 | 2-5 | 6-10 |
| tribal | 10-12 | 8-12 | 2-5 | 3-6 |
| voltron | 8-10 | 8-12 | 2-5 | 6-10 |
| equipment | 10-12 | 8-12 | 2-5 | 6-10 |
| reanimator | 10-12 | 8-12 | 8-12 | 3-6 |
| graveyard | 10-12 | 8-12 | 8-12 | 3-6 |
| mill | 10-12 | 8-12 | 4-8 | 3-6 |
| spellslinger | 10-12 | 8-12 | 2-5 | 3-6 |
| storm | 10-12 | 8-12 | 2-5 | 3-6 |
| combo | 10-12 | 8-12 | 2-5 | 6-10 |
| counters | 8-10 | 8-12 | 2-5 | 6-10 |
| infect | 10-12 | 8-12 | 2-5 | 6-10 |
| lifegain | 10-12 | 8-12 | 2-5 | 3-6 |
| blink | 10-12 | 8-12 | 3-6 | 3-6 |
| landfall | 10-12 | 8-12 | 2-3 | 3-6 |
| big_mana | 12-15 | 8-10 | 2-5 | 3-6 |
| stax | 10-12 | 8-12 | 2-5 | 3-6 |
| control | 10-12 | 8-12 | 2-5 | 3-6 |
| group_hug | 10-12 | 8-12 | 2-5 | 3-6 |
| enchantress | 10-12 | 6-10 | 2-5 | 3-6 |
| artifacts | 10-12 | 8-12 | 2-5 | 3-6 |
| superfriends | 10-12 | 8-12 | 2-5 | 3-6 |
| burn | 10-12 | 8-12 | 2-5 | 3-6 |
| stompy | 10-12 | 8-12 | 2-5 | 3-6 |
| lands_matter | 10-12 | 8-12 | 2-3 | 3-6 |
| outlaws | 10-12 | 8-12 | 2-5 | 3-6 |
| clones | 10-12 | 8-12 | 2-5 | 3-6 |
| extra_combats | 10-12 | 8-12 | 2-5 | 3-6 |
| mutate | 10-12 | 8-12 | 2-5 | 4-6 |
| polymorph | 10-12 | 8-12 | 2-5 | 4-6 |
| self_mill | 10-12 | 6-8 | 8-12 | 3-6 |
| energy | 10-12 | 6-8 | 2-5 | 3-6 |
| vehicles | 10-12 | 8-12 | 2-5 | 3-6 |
| sagas | 10-12 | 8-12 | 2-5 | 3-6 |
| discard | 10-12 | 6-8 | 2-5 | 3-6 |
| group_slug | 10-12 | 8-12 | 2-5 | 3-6 |
| forced_combat | 10-12 | 8-12 | 2-5 | 4-6 |
| pillow_fort | 10-12 | 6-8 | 2-5 | 3-5 |
| upkeep_triggers | 10-12 | 6-8 | 2-5 | 3-5 |
| treasure | 10-12 | 8-12 | 2-5 | 3-6 |
| wheels | 10-12 | 8-12 | 2-5 | 3-6 |
| impulse_draw | 10-12 | 8-12 | 2-5 | 3-6 |
| legends_matter | 10-12 | 8-12 | 2-5 | 3-6 |
| theft | 10-12 | 8-12 | 2-5 | 3-6 |

Base: ramp 10-12, draw 8-12, recursion 2-5, protection 3-6.

## 2. Archetype-specific slots 
Slots already in section 1 are not repeated.

- **aristocrats**: fodder 10-12; outlet 5-8; payoff 8-10; edict 6-8
- **tokens**: generator 10-14; doubler 2-4; anthem 4-6
- **voltron**: attach 12-18; attach_helper 4-6
- **equipment**: equipment 10-14; carrier 12-18
- **reanimator**: enabler 6-8; reanimation 8-12; target 6-10
- **graveyard**: filler 8-10; backup_engine 1-2
- **mill**: engine 8-12; doubler 2-3; interaction 8-10
- **spellslinger**: payoff 6-10; cantrip 8-12; spells 25-35
- **storm**: payoff 2-3; spells 25-35
- **combo**: tutor 5-10; payoff_engine 2-3
- **counters**: multiplier 3-5; enabler 15-20; proliferate 4-8; draw_payoff 6-8
- **infect**: creature 15-20; pump 6-10; proliferate 5-8
- **lifegain**: trigger 8-12; payoff 6-10; interaction 6-8
- **blink**: flicker 8-12; etb_creature 20-25
- **landfall**: payoff 8-10; extra_drop 4-6; interaction 5-7
- **big_mana**: multiplier 2-4; haymaker 4-6; interaction 5-7
- **stax**: lock 8-12; parity_breaker 4-6; win 1-2
- **control**: answer 8-12; sweeper 6-10; finisher 2-3
- **group_hug**: shared 8-12; breaker 4-6
- **artifacts**: artifact 25-35; cost_reducer 3-5
- **stompy**: creature 25-35; big_body 8-12; anthem 2-4; extra_combat 2-3
- **lands_matter**: ramp_land 8-12; payoff 6-10; interaction 5-7
- **outlaws**: outlaw 18-28; lord 3-6
- **clones**: clone 10-16; etb_target 10-14; remove 6-8
- **extra_combats**: extra_combat 6-10; attack_trigger 8-12; pump 2-4
- **mutate**: mutate 12-20; target 12-18
- **polymorph**: polymorph 6-10; fodder 8-12; bomb 6-10
- **self_mill**: filler 8-12; payoff 3-5
- **energy**: producer 12-18; payoff 6-10
- **vehicles**: vehicle 8-12; crew 12-18; payoff 3-6; remove 5-7
- **sagas**: saga 12-20; reuse 4-8; enabler 8-10
- **discard**: discard 8-12; punisher 3-6; remove 6-8
- **group_slug**: slug 8-12; lifegain 4-6; blocker 10-14; remove 5-7
- **forced_combat**: force 6-10; blocker 10-14; remove 5-7
- **pillow_fort**: fort 8-12; finisher 2-4
- **upkeep_triggers**: engine 10-16; doubler 2-4
- **theft**: steal 8-12; remove 5-7

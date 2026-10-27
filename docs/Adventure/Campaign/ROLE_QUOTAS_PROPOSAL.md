# Role quotas by archetype (PROPOSAL, not applied)

Status: draft for the user (revised 2026-10-27). Nothing in `tier_rules.py` or `build.py` has been changed.

## Rule (user, 2026-10-27)
No tier-based role-count restrictions. One quota per archetype, taken straight from the archetype research (`tools/agents/reference/ARCHETYPES.toon`, `tools/concordia/strategies/strategies.json`), the same at every tier. The tier is set by the deck's power score alone (`power_scorer.py`: average card power band, cards at power 50+/70+), not by how many ramp, draw or other role cards it holds.

Engine goals (every deck): ramp 10-12, card draw 8-12, recursion 2-5, protection 3-6. The archetype's own range replaces them where it lists one (recursion: graveyard/reanimator/self_mill 8-12 ...; protection: voltron/equipment/tokens/counters/combo/infect 6-10).

General engine pieces (removal, wipes, tutors, fast mana, lands) are in section 4. The hard gates (Game Changers, extra turns, mass land denial, mechanics by tier, watch-list) are not role counts and are NOT removed here; confirm whether they stay. Archetype slots marked `-` have no count and are omitted. Niche archetypes (user, 2026-10-27) rely on the base archetype they are attached to.

## 1. Engine roles by archetype
Niche archetypes (marked *) take their base archetype's numbers: the first listed parent that is a full archetype (else the first parent, resolved the same way); own listed numbers win. Base shown in the last column.

| Archetype | Ramp | Draw | Recursion | Protection | Base |
|---|---|---|---|---|---|
| aristocrats | 10-12 | 8-10 | 4-8 | 3-6 |  |
| tokens | 8-10 | 6-8 | 2-5 | 6-10 |  |
| tribal | 10-12 | 8-12 | 2-5 | 3-6 |  |
| voltron | 8-10 | 8-12 | 2-5 | 6-10 |  |
| equipment | 10-12 | 8-12 | 2-5 | 6-10 |  |
| reanimator | 10-12 | 8-12 | 8-12 | 3-6 |  |
| graveyard | 10-12 | 8-12 | 8-12 | 3-6 |  |
| mill | 10-12 | 8-12 | 4-8 | 3-6 |  |
| spellslinger | 10-12 | 8-12 | 2-5 | 3-6 |  |
| storm | 10-12 | 8-12 | 2-5 | 3-6 |  |
| combo | 10-12 | 8-12 | 2-5 | 6-10 |  |
| counters | 8-10 | 8-12 | 2-5 | 6-10 |  |
| infect* | 8-10 | 8-12 | 2-5 | 6-10 | counters |
| lifegain | 10-12 | 8-12 | 2-5 | 3-6 |  |
| blink | 10-12 | 8-12 | 3-6 | 3-6 |  |
| landfall* | 10-12 | 8-12 | 2-3 | 3-6 | lands_matter |
| big_mana | 12-15 | 8-10 | 2-5 | 3-6 |  |
| stax | 10-12 | 8-12 | 2-5 | 3-6 |  |
| control | 10-12 | 8-12 | 2-5 | 3-6 |  |
| group_hug* | 10-12 | 6-8 | 2-5 | 3-5 | pillow_fort |
| enchantress* | 10-12 | 6-10 | 2-5 | 3-6 | control |
| artifacts | 10-12 | 8-12 | 2-5 | 3-6 |  |
| superfriends | 10-12 | 8-12 | 2-5 | 3-6 |  |
| burn | 10-12 | 8-12 | 2-5 | 3-6 |  |
| stompy | 10-12 | 8-12 | 2-5 | 3-6 |  |
| lands_matter | 10-12 | 8-12 | 2-3 | 3-6 |  |
| outlaws | 10-12 | 8-12 | 2-5 | 3-6 |  |
| clones | 10-12 | 8-12 | 2-5 | 3-6 |  |
| extra_combats | 10-12 | 8-12 | 2-5 | 3-6 |  |
| mutate* | 8-10 | 8-12 | 2-5 | 6-10 | voltron |
| polymorph | 10-12 | 8-12 | 2-5 | 4-6 |  |
| self_mill | 10-12 | 6-8 | 8-12 | 3-6 |  |
| energy | 10-12 | 6-8 | 2-5 | 3-6 |  |
| vehicles* | 10-12 | 8-12 | 2-5 | 3-6 | artifacts |
| sagas* | 10-12 | 8-12 | 3-6 | 3-6 | blink |
| discard | 10-12 | 6-8 | 2-5 | 3-6 |  |
| group_slug | 10-12 | 8-12 | 2-5 | 3-6 |  |
| forced_combat* | 10-12 | 8-12 | 2-5 | 4-6 | stompy |
| pillow_fort* | 10-12 | 6-8 | 2-5 | 3-5 | control |
| upkeep_triggers | 10-12 | 6-8 | 2-5 | 3-5 |  |
| treasure* | 10-12 | 8-12 | 2-5 | 3-6 | artifacts |
| wheels* | 10-12 | 8-12 | 2-5 | 3-6 | control |
| impulse_draw* | 10-12 | 8-12 | 2-5 | 3-6 | outlaws |
| legends_matter* | 8-10 | 8-12 | 2-5 | 6-10 | voltron |
| theft* | 10-12 | 8-12 | 2-5 | 3-6 | control |

Base: ramp 10-12, draw 8-12, recursion 2-5, protection 3-6.

## 2. Archetype-specific slots
Slots already in section 1 are not repeated. Niche archetypes show their base's slots plus their own.

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
- **infect** (base counters): multiplier 3-5; enabler 15-20; proliferate 5-8; draw_payoff 6-8; creature 15-20; pump 6-10
- **lifegain**: trigger 8-12; payoff 6-10; interaction 6-8
- **blink**: flicker 8-12; etb_creature 20-25
- **landfall** (base lands_matter): ramp_land 8-12; payoff 8-10; interaction 5-7; extra_drop 4-6
- **big_mana**: multiplier 2-4; haymaker 4-6; interaction 5-7
- **stax**: lock 8-12; parity_breaker 4-6; win 1-2
- **control**: answer 8-12; sweeper 6-10; finisher 2-3
- **group_hug** (base pillow_fort): answer 8-12; sweeper 6-10; finisher 2-4; fort 8-12; shared 8-12; breaker 4-6
- **enchantress** (base control): answer 8-12; sweeper 6-10; finisher 2-3
- **artifacts**: artifact 25-35; cost_reducer 3-5
- **stompy**: creature 25-35; big_body 8-12; anthem 2-4; extra_combat 2-3
- **lands_matter**: ramp_land 8-12; payoff 6-10; interaction 5-7
- **outlaws**: outlaw 18-28; lord 3-6
- **clones**: clone 10-16; etb_target 10-14; remove 6-8
- **extra_combats**: extra_combat 6-10; attack_trigger 8-12; pump 2-4
- **mutate** (base voltron): attach 12-18; attach_helper 4-6; mutate 12-20; target 12-18
- **polymorph**: polymorph 6-10; fodder 8-12; bomb 6-10
- **self_mill**: filler 8-12; payoff 3-5
- **energy**: producer 12-18; payoff 6-10
- **vehicles** (base artifacts): artifact 25-35; cost_reducer 3-5; vehicle 8-12; crew 12-18; payoff 3-6; remove 5-7
- **sagas** (base blink): flicker 8-12; etb_creature 20-25; saga 12-20; reuse 4-8; enabler 8-10
- **discard**: discard 8-12; punisher 3-6; remove 6-8
- **group_slug**: slug 8-12; lifegain 4-6; blocker 10-14; remove 5-7
- **forced_combat** (base stompy): creature 25-35; big_body 8-12; anthem 2-4; extra_combat 2-3; force 6-10; blocker 10-14; remove 5-7
- **pillow_fort** (base control): answer 8-12; sweeper 6-10; finisher 2-4; fort 8-12
- **upkeep_triggers**: engine 10-16; doubler 2-4
- **treasure** (base artifacts): artifact 25-35; cost_reducer 3-5
- **wheels** (base control): answer 8-12; sweeper 6-10; finisher 2-3
- **impulse_draw** (base outlaws): outlaw 18-28; lord 3-6
- **legends_matter** (base voltron): attach 12-18; attach_helper 4-6
- **theft** (base control): answer 8-12; sweeper 6-10; finisher 2-3; steal 8-12; remove 5-7

## 3. Creature cap (user, 2026-10-27: no creature-flooded decks)
Proposal, numbers are my assumption (the user gave none): at most 35 creature cards in the 99 (about 35%) for every archetype, at least 15 as today. For reference, the 180 Commander precons average 29 creatures (`ENCOUNTER_TIERS.md` §7). The old per-tier type shares (Tier 1 creatures at most 85%, Tier 2/3 no type above 60%) are replaced by this cap; the noncreature minimums stay (at least 4 instants, 3 sorceries, 4 artifacts, 2 enchantments).

Archetype slots that push creature counts up, and how to treat them:
- **stompy** creature 25-35: top of the range is already at the cap; hold it at 25-30.
- **outlaws** outlaw 18-28 and **blink** etb_creature 20-25: outlaw and etb_creature are creature-heavy by definition; cap at 28 and 25 and fill the remainder with noncreature cards, so total creatures stay at 35 or fewer.
- **infect** creature 15-20, **equipment** carrier 12-18, **mutate** target 12-18, **vehicles** crew 12-18, **tribal** (type density): count against the same cap, together with every other creature in the deck.
- Slots such as generator, fodder, enabler and payoff overlap with creatures; the cap counts the card once.

Check: `power_scorer.py` and `build.py` would report creature count as a WARN above 35 (FAIL above 40). Not implemented.

## 4. General engine pieces (user, 2026-10-27)
These belong to any deck, are not tied to an archetype and are not tier-limited. They are added by synergy and gaps (what the commander and archetype slots leave missing), then the power score decides the tier.

- **Tutors:** payoffs are the tutor targets. Pick the tutors that find the deck's payoffs, finishers and engine pieces (archetype slots such as payoff, finisher, haymaker, bomb, win), and include them whenever the deck has such targets. No fixed count; the old 0-1 cap for Tier 2 is gone.
- **Fast mana:** always good, always welcome (Sol Ring, signets, talismans, rituals where they fit). No cap; it goes in on top of the ramp slot count and the power score prices it. Budget rocks stay allowed for starters (rule 2 of the reader deck rules).
- **Board wipes:** every deck runs 1-2 (a sweeper slot in control keeps its 6-10 as an archetype slot). Choose the wipe that fits the deck (a creature-light or token deck prefers a one-sided or selective one). The rule is a floor of 1, usual 2.
- **Removal:** general like the rest (user, 2026-10-27), no fixed count and no tier range. Picked by synergy with the commander and the archetype slots, then topped up for gaps (`remove:*` family, one card counts once). Prefer the type that fits the plan: exile or bounce for a blink deck, edicts for an aristocrats deck, and so on. The archetype `remove` slots (clones, vehicles, discard, theft ...) are counted inside this pool, not on top of it.
- **Lands:** from the mana curve, not from the tier. Frank Karsten formula already used in `ENCOUNTER_TIERS.md` §2: lands = 31.4 + 3.13 x average mana value - 0.28 x (ramp or draw spells costing 3 or less), kept within a few of the result.
  Example: average mana value 3.3 with 12 cheap ramp or draw spells gives 31.4 + 10.3 - 3.4 = 38.3, so about 38 lands.
  Nonbasic land quality (duals, utility) stays with the power score.

# Tag reference

The definition of every tag family: 192 families. This file is the source of tag definitions. It is generated from `tag_extra.LEGEND` / `DOC` / `REF_EXTRA` and `tag_verify.DOC` (change a meaning there and rerun `deckgen/tag_run.py starter`); it does not read any card set. Status: `approved` = a family the user approved (lists in `tag_reports.py`); `established` = older family in use before the approval process; a family not yet approved is listed in NEW_TAGS_FOR_APPROVAL.md.

## How a record reads

- `typing:` the card's own typing (supertype, cardtype, type, landtype). `tags:` what its abilities do. `ai_tags:` AI Tags (tempo, ai_logic, umbrella labels); hidden from the blind reader. All lower case.
- `groups` tie tags to one line of the card: `k1` keyword line, `c1` first ability line, `c1.2` its sub-ability, `s1` saga chapter, `x` cross-check additions, `c0` card level. `links` relate tags: requires, provides, lasts, receives, produces, scales_with, measures, depends_on, filters, uses.
- Zone moves share `from_zone:<zone>` / `to_zone:<zone>`; `rest_to_zone` and `rest_order` describe the cards not taken. Qualifier families (draw_count, damage_amount, token_count, cost_reduce_amount ...) travel with their bare tag on purpose (REDUNDANCY_OK).
- `niche:<archetype>` marks an effect that only pays in a deck built around that archetype (consumers weigh it down unless the archetype matches); `derived:` tags are computed from other tags.
- Sources: card script (Forge `A:`/`S:`/`T:`/`R:`/`K:` lines and SVars) with its Oracle section as gap filler, keyword reference (CR 702/701), Forge AI (`AILogic`). The gap filler adds triggers, costs and keywords the script lacks; ability phrases it finds are flags only.

## Typing line (what the card is)

| Family | Meaning | Source / reference | Approved | Used by archetypes (strategies.json) |
|---|---|---|---|---|
| `cardtype` | card type from the Types line: creature, instant, sorcery, artifact, enchantment, land, planeswalker, kindred | script Types: line; CR 205.2 | established | spellslinger.spells[instant]; spellslinger.spells[sorcery]; storm.ritual[instant]; storm.spells[instant]; storm.spells[sorcery]; enchantress.cheap_ench[enchantment]; artifacts.artifact[artifact]; superfriends.walker[planeswalker]; stompy.creature[creature]; mutate.target[creature]; group_slug.blocker[creature]; forced_combat.blocker[creature] |
| `landtype` | basic land type of a basic land (swamp, forest ...): the land taps for that mana | script Types: line; CR 305.6 | established | - |
| `supertype` | supertype: legendary, basic, snow, world | script Types: line; CR 205.4 | established | - |
| `type` | creature or other subtype from the Types line (human, wizard, equipment ...) | script Types: line; CR 205.3 | established | outlaws.outlaw[assassin]; outlaws.outlaw[pirate]; outlaws.outlaw[rogue]; outlaws.outlaw[mercenary]; outlaws.outlaw[warlock]; vehicles.vehicle[vehicle] |

## Keywords and engine lines

| Family | Meaning | Source / reference | Approved | Used by archetypes (strategies.json) |
|---|---|---|---|---|
| `forge_line` | a Forge engine line that is not a rules keyword. forge_line:etbcounter = 'enters with counters on it' (the counter tags say which); forge_line:etbreplacement = an 'as this enters' choice or replacement | found in the cross-check: these were wrongly tagged kw: | established | - |
| `kw` | keyword ability the card has; qualifiers (numbers, costs, colours) follow as separate tags | script K: line; CR 702; reminder text in ai_lab/KEYWORD_REMINDER_TEXT.toon | established | tokens.protection[indestructible]; voltron.attach[equip]; voltron.attach[enchant]; voltron.attach[bestow]; voltron.protection[hexproof]; voltron.protection[indestructible]; voltron.evasion[flying]; voltron.evasion[trample]; voltron.damage_multiplier[double_strike]; equipment.equipment[equip]; graveyard.filler[dredge]; graveyard.recursion[flashback]; graveyard.recursion[escape]; spellslinger.payoff[prowess]; spellslinger.rebuy[flashback]; storm.payoff[storm]; infect.creature[infect]; infect.creature[toxic]; lifegain.trigger[lifelink]; enchantress.cheap_ench[enchant]; artifacts.cost_reducer[affinity]; stompy.big_body[trample]; stompy.haste[haste]; extra_combats.attack_trigger[melee]; extra_combats.attack_trigger[myriad]; extra_combats.haste[haste]; mutate.mutate[mutate]; mutate.protection[hexproof]; self_mill.filler[dredge]; self_mill.recursion[escape]; self_mill.recursion[flashback]; vehicles.crew[crew]; sagas.saga[chapter]; discard.symmetrical[madness]; group_slug.lifegain[lifelink]; pillow_fort.protection[hexproof]; upkeep_triggers.engine[cumulative_upkeep] |
| `landwalk` | which land type a landwalk keyword names | user: landwalk type as its own tag | established | - |
| `protection_from` | what a Protection keyword protects from (kw:protection stays the keyword) | user: protection parsed as the keyword, colours and types as separate tags | established | - |

## When it happens (triggers, conditions, limits)

| Family | Meaning | Source / reference | Approved | Used by archetypes (strategies.json) |
|---|---|---|---|---|
| `activation_restriction` | the ability can only be activated under a condition | Temple of the False God | approved | - |
| `condition` | the ability works only while this is true (a permanent or card you control, or an empty library) | reverse check r1: Predatory Wurm, Laboratory Maniac; user 2026-10-22: prune redundant proposed tags | approved | landfall.payoff[landfall]; stompy.big_body[creature_you_control_power_ge_4]; discard.punisher[hellbent] |
| `delayed` | an effect that happens at the next end step | Kiki-Jiki | approved | - |
| `limit` | limit on how often the ability works (once_per_turn = only once each turn) | script ActivationLimit$ | approved | - |
| `optional` | the effect of this group is optional (you may ...) | script Optional$ True / OptionalDecider$ You (agent suggestion S01) | approved | - |
| `saga_chapter` | marks an ability as a saga chapter (the chapter number is not kept; how many chapters the saga has is kw:chapter + num) | reverse check r1: Time of Ice | approved | sagas.saga |
| `trigger` | event that triggers the ability (attacks, dies, etb, gain_life, draw = a player draws a card, beginning_of_combat ...) | cross-check: Oracle line starts (CR 603) | approved | aristocrats.payoff[dies]; aristocrats.card_adv[draw]; tokens.drain[etb]; tokens.draw[draw]; tribal.card_adv[draw]; tribal.card_adv[spell_cast]; voltron.damage_multiplier[beginning_of_combat]; equipment.draw[draw]; graveyard.payoff[dies]; spellslinger.payoff[spell_cast]; spellslinger.cantrip[draw]; storm.cantrip[draw]; storm.refuel[draw]; combo.draw_select[draw]; counters.draw_payoff[draw]; lifegain.trigger[gain_life]; lifegain.payoff[gain_life]; lifegain.conversion[draw]; blink.engine[end_step]; blink.etb_creature[etb]; big_mana.draw[draw]; control.draw_engine[draw]; group_hug.shared[draw]; group_hug.breaker[draw]; enchantress.draw[draw]; enchantress.draw[spell_cast]; artifacts.draw[draw]; stompy.extra_combat[beginning_of_combat]; stompy.refuel[draw]; stompy.refuel[combat_damage]; clones.etb_target[etb]; extra_combats.extra_combat[beginning_of_combat]; extra_combats.attack_trigger[combat_damage]; self_mill.draw[draw]; energy.draw[draw]; sagas.enabler[draw]; discard.punisher[discard]; discard.draw[draw]; group_slug.slug[draw]; pillow_fort.draw[draw]; upkeep_triggers.engine[upkeep]; upkeep_triggers.doubler[upkeep]; upkeep_triggers.draw[draw]; wheels.core[draw] |
| `trigger_filter` | narrows the triggering card or spell: a card type (always named for another card's zone-change trigger: trigger_filter:creature = another creature), a negated type (noncreature = noncreature spell), power_ge_N / power_le_N (power at least / at most N), one_or_more (triggers once for a group) | Rancor, Oblivion Ring, Bontu's Monument | approved | outlaws.crime_trigger[pirate]; outlaws.crime_trigger[rogue]; outlaws.crime_trigger[assassin]; vehicles.payoff[vehicle] |
| `trigger_scope` | which cards fire a zone-change trigger: self = this card only, other = another card, any = this card or any other card | found in the cross-check: Morbid Opportunist, Welcoming Vampire | approved | - |
| `trigger_zone` | trigger event, the zone it goes to, and a card-type filter on cast triggers | Rancor, Oblivion Ring, Bontu's Monument | approved | - |
| `unless_cost` | the effect happens unless a player pays a cost (a tax, not a choice); unless_cost_amount says how much | script UnlessCost$ | approved | - |

## Costs and mana

| Family | Meaning | Source / reference | Approved | Used by archetypes (strategies.json) |
|---|---|---|---|---|
| `cost` | non-mana cost of the ability (tap, sacrifice, remove_counters, exile with from_zone, life, discard, return) | cross-check: Oracle cost text (CR 602, 118) | approved | reanimator.enabler[discard]; burn.pinger[tap]; discard.symmetrical[discard] |
| `cost_energy` | the cost pays energy counters | approved 2026-10-27: Aethertide Whale | approved | energy.payoff |
| `cost_exile_target` | what is exiled from the graveyard as a cost | script Cost$ ExileFromGrave | approved | - |
| `cost_if_you_do` | the 'If you do' part marks the preceding sacrifice/discard as a cost | user note on Victimize | approved | - |
| `cost_mana` | the mana part of an activation cost, symbols joined (cost_mana:2b = {2}{B}, cost_mana:x = {X}); cost:mana is not tagged when this tag is present | P4c E, user 2026-10-23 (placeholder triage: {cost} was 117 of 317 placeholders) | approved | - |
| `cost_reduce` | spells cost less to cast (qualifiers: cost_reduce_for, cost_reduce_amount, cost_reduce_mana) | script S: Mode$ ReduceCost; CR 601.2f | established | tribal.cost_reducer; voltron.attach_helper; equipment.cost_reducer; spellslinger.cost_reducer; storm.cost_reducer; artifacts.cost_reducer |
| `cost_reduce_amount` | how much each affected spell costs less (generic mana) | script Amount$ on ReduceCost | approved | - |
| `cost_reduce_for` | which spells a cost reduction applies to (a card type, a creature type, or chosen_type); cost_reduce_amount is how much cheaper | Bontu's Monument | approved | outlaws.cost_reducer[rogue] |
| `cost_reduce_mana` | the kind of mana the cost is reduced by (generic = any mana) | script ReduceCost; CR 601.2f | approved | - |
| `cost_return_target` | non-mana costs: return a permanent you control to hand; exile a card from your graveyard | reverse check r1: Soratami Savant, Disciple of the Ring | approved | - |
| `cost_sacrifice_target` | what a sacrifice cost sacrifices (self, land, creature ...) | Harrow, Blighted Woodland | approved | aristocrats.outlet; aristocrats.card_adv; treasure.core[treasure] |
| `mana` | colour of mana an ability produces (white, blue, black, red, green, colorless, any, commander_identity; colorless is the sixth colour, H78) | feedback: link color type to mana source (Arcane Signet, Plains, Temple, Frost Marsh) | approved | storm.ritual |
| `mana_amount` | how much mana is produced per activation; always tagged on a mana source ability, also when it is 1 | Temple of the False God; user note: always tag mana_amount | approved | big_mana.multiplier |
| `mana_amount_if` | mana added when the condition holds; mana_amount is the base amount otherwise | script Count$Compare <SVar> <op><n>.<then>.<else> | approved | - |
| `mana_choice` | the ability lets you choose between colours | Frost Marsh, Arcane Signet | approved | - |
| `mana_conditional` | the mana ability adds a different amount, or works only, when the condition: tag of its group holds | script IsPresent$ on the mana ability, or Amount$ with Count$Compare | approved | - |
| `mana_restriction` | the mana can be spent only on what the value says (mana_restriction:instant_or_sorcery = spend this mana only to cast an instant or sorcery spell) | Vodalian Arcanist; script RestrictValid$ | approved | - |
| `mana_source` | the card or ability adds mana (qualifiers: mana, mana_amount, mana_choice, mana_restriction) | script Mana abilities (AB$ Mana, Produced$); CR 106 | established | tokens.ramp; voltron.ramp; spellslinger.cost_reducer; combo.enabler; counters.ramp; lifegain.ramp; landfall.ramp; big_mana.ramp; big_mana.mana_land; stax.parity_breaker; group_hug.breaker; superfriends.mana; sagas.enabler |
| `untap` | an effect untaps permanents | cross-check: Oracle (Captivating Crew) | approved | combo.enabler; stax.parity_breaker; artifacts.untapper |

## Targets, scope and choices

| Family | Meaning | Source / reference | Approved | Used by archetypes (strategies.json) |
|---|---|---|---|---|
| `affected_filter` | what a static effect applies to (anthem: other creatures you control) | reverse check r1: Benalish Marshal | approved | - |
| `affected_player` | APPROVED 2026-10-27: the player who receives the effect when it is not the ability's controller: affected_player:target_controller = the controller of the targeted permanent ('Its controller gains life equal to its power'), target_owner = its owner, target_player = the targeted player; set on the effect group (Forge Defined$/Player$ TargetedController / TargetedOwner / TargetedPlayer) | user 2026-10-27 (affected_player, 'proceed') | approved | - |
| `affected_scope` | whose permanents the effect or static ability affects (you_control, opponent_controls, all) | reverse check r1: Benalish Marshal | approved | - |
| `affected_type` | what a static effect applies to (anthem: other creatures you control) | reverse check r1: Benalish Marshal | approved | vehicles.payoff[vehicle]; sagas.reuse[saga] |
| `affects` | which creature type a static effect applies to | Goblin Rabblemaster | approved | - |
| `choice_option` | one of the options the choice offers (choose_on_enter lists them: artifact, creature, enchantment ...) | script ValidTypes$ / Choices$ of the Choose effect | approved | - |
| `choose_on_enter` | as this card enters the battlefield its controller chooses something (color, card_type, creature_type, player ...); other tags of the card refer to the choice (cost_reduce_for:chosen_type = spells of the chosen type) | script K:ETBReplacement with a Choose* effect; CR 614.12 | approved | - |
| `target_count` | how many things the effect picks | Filter Out, Rowan, Oko | approved | - |
| `target_filter` | what the effect can pick: card type, filters such as nonland, and whose | Filter Out, Scorching Dragonfire, Oblivion Ring | approved | - |
| `target_scope` | whose things or which players the effect hits (you_control, opp_control; no tag = whoever controls it; each_opponent = every opponent, each_player = every player; no value means a single chosen target) | Filter Out, Scorching Dragonfire, Oblivion Ring | approved | - |
| `target_type` | what the effect can pick: card type, filters such as nonland, and whose | Filter Out, Scorching Dragonfire, Oblivion Ring | approved | equipment.equipment[equipment] |
| `target_zone` | the zone the targets are in (graveyard, exile, hand, library) | Victimize | approved | - |

## What it does (effects and amounts)

| Family | Meaning | Source / reference | Approved | Used by archetypes (strategies.json) |
|---|---|---|---|---|
| `counter` | a counter on a permanent; counter:landmark = a landmark counter (Treasure Map: counts up to three, then the card flips); counter:p1p1 = +1/+1 counter | Invasion of Moag | approved | counters.enabler[p1p1]; counters.seed; energy.producer[energy]; energy.payoff[energy] |
| `counter_count` | amounts the first run dropped: life gained or lost, counters placed | reverse check r1: 86 of 348 cards lost a number | approved | - |
| `counter_remove` | removes counters as an effect (cost:remove_counters is the cost) | approved 2026-10-27: Phantom Nantuko | approved | counters.spend |
| `counters` | planeswalker loyalty, and the loyalty change an ability makes (renamed from loyalty_cost, user note); loyalty is a kind of counter | Oko, Rowan | established | - |
| `counters_plus` | puts +1/+1 counters on something: 'Put a +1/+1 counter on target creature' | script PutCounter P1P1; CR 122 | established | counters.multiplier; counters.enabler; counters.draw_payoff; superfriends.doubler; energy.multiplier |
| `counterspell` | counters a spell | script Counter; CR 701.6 | established | reanimator.protection; mill.interaction; combo.protection; big_mana.interaction; control.answer; polymorph.protection |
| `damage` | deals damage (damage is damage, not removal) | Scorching Dragonfire, Rowan | approved | tokens.drain; burn.damage; burn.pinger; stompy.finisher; group_slug.slug |
| `damage_amount` | deals damage (damage is damage, not removal) | Scorching Dragonfire, Rowan | approved | burn.damage |
| `die_sides` | the effect rolls a die; die_sides is the number of sides (d20 = 20) | approved 2026-10-27: TAG_GAP_CANDIDATES section A (user: approve A) | established | - |
| `discard` | a player discards cards as an effect | cross-check: Oracle | established | reanimator.enabler; graveyard.filler; storm.refuel; discard.discard |
| `discard_count` | how many cards an ability draws or makes a player discard | user note: tag draw count | approved | - |
| `draw` | draws cards (amount in draw_count) | script Draw; CR 121 | established | aristocrats.card_adv; tokens.draw; tribal.card_adv; equipment.draw; spellslinger.cantrip; storm.cantrip; storm.refuel; combo.draw_select; counters.draw_payoff; lifegain.conversion; big_mana.draw; control.draw_engine; group_hug.shared; group_hug.breaker; enchantress.draw; artifacts.draw; stompy.refuel; self_mill.draw; energy.draw; sagas.enabler; discard.draw; pillow_fort.draw; upkeep_triggers.draw |
| `draw_count` | how many cards an ability draws or makes a player discard | user note: tag draw count | approved | - |
| `exile_from` | exiles cards from a zone other than the battlefield | found in the cross-check: Scavenging Ooze, Squee | approved | mill.graveyard_exile |
| `extra_land_drop` | its controller may play this many additional lands each turn | script AdjustLandPlays$ | approved | landfall.extra_drop; lands_matter.ramp_land |
| `extra_turn` | the card takes an extra turn (script AddTurn); capped per tier in tier_rules (none below T4, 1 at T4, 2 at T5) | user 2026-10-26: own tag, replaces the name list in power_scorer | approved | combo.support_extra_turn |
| `flip_coin` | the effect flips a coin; flip_win / flip_lose mark that an outcome has a sub-effect | approved 2026-10-27: Creepy Doll, Volatile Rig | approved | - |
| `flip_lose` | the effect flips a coin; flip_win / flip_lose mark that an outcome has a sub-effect | approved 2026-10-27: Creepy Doll, Volatile Rig | established | - |
| `flip_win` | the effect flips a coin; flip_win / flip_lose mark that an outcome has a sub-effect | approved 2026-10-27: Creepy Doll, Volatile Rig | established | - |
| `from_zone` | zone the card comes from (graveyard, hand, library, exile). Pairs with the other tags of the same group: return, put_onto_battlefield, cost:exile | reverse check r1: Soratami Savant, Disciple of the Ring | approved | reanimator.reanimation[graveyard]; graveyard.recursion[graveyard]; landfall.recursion[graveyard]; lands_matter.recursion[graveyard]; self_mill.recursion[graveyard] |
| `life_loss` | an effect makes a player lose life (not damage) | cross-check: Oracle 'loses N life' (Nazar, Blood Artist, Gray Merchant) | approved | aristocrats.payoff; graveyard.payoff; lifegain.drain; blink.finisher; group_slug.slug |
| `life_loss_amount` | amounts the first run dropped: life gained or lost, counters placed | reverse check r1: 86 of 348 cards lost a number | approved | - |
| `lifegain` | an effect gains life | cross-check: Oracle | established | lifegain.trigger; group_slug.lifegain |
| `lifegain_amount` | life gained (number, x, or equal_to_life_lost) | reverse check r1: 86 of 348 cards lost a number | approved | - |
| `look_top` | look at the top N cards of a library | reverse check r1: Militia Bugler, Dig Through Time | approved | spellslinger.support_look_top; impulse_draw.support_look_top |
| `lose_game` | the effect makes a player lose the game | approved 2026-10-27: Nine Lives | approved | combo.support_alt_win |
| `loses_all_abilities` | an Animate effect: what it becomes, and that it loses all abilities | Oko | approved | - |
| `mill` | puts cards from the top of a library into a graveyard | script Mill; CR 701.17 | established | graveyard.filler; mill.engine; mill.doubler; mill.payoff |
| `mill_count` | how many cards are milled (who is milled: mill / self_mill) | mtg2llm gap record, approved 2026-10-27: Blight Titan, Barrowgoyf | approved | mill.engine; mill.payoff; self_mill.filler |
| `modal` | choose N of M modes (modal:1_of_3 = choose one of three) | reverse check r1: Valorous Stance, Return of the Wildspeaker | approved | - |
| `piles_split` | cards are split into two piles by this player | reverse check r1: Fact or Fiction | approved | - |
| `put_onto_battlefield` | a card is put onto the battlefield without being cast; from_zone says where from | user note, confirmed 2026-10-22: the tag means 'not cast' | approved | voltron.attach_helper; blink.flicker; blink.engine; group_hug.shared; polymorph.polymorph |
| `put_tapped` | the card is put onto the battlefield tapped | script ChangeZone Tapped$ True | approved | - |
| `remove` | how a card removes something; replaces the single 'removal' tag when a method is known | Scorching Dragonfire, Oblivion Ring | approved | mill.interaction; combo.remove; lifegain.interaction; blink.flicker[exile]; landfall.interaction; big_mana.interaction; control.answer; control.sweeper; superfriends.defense; superfriends.remove; stompy.remove; lands_matter.interaction; clones.remove; vehicles.remove; discard.remove; group_slug.remove; forced_combat.remove; theft.remove |
| `rest_order` | position of the rest in the library: bottom, or bottom_random (bottom in a random order) | reverse check r1: Militia Bugler, Dig Through Time | approved | - |
| `rest_to_zone` | where the looked-at cards that were not taken go; rest_order says the position | reverse check r1: Militia Bugler, Dig Through Time | approved | - |
| `return` | a card is returned from one zone to another; read with from_zone and to_zone (return from_zone:graveyard to_zone:hand = return a card from graveyard to hand) | reverse check r5: Elvish Regrower lost its meaning when recursion became an AI tag | approved | blink.flicker |
| `return_exiled` | returns what this card exiled when it leaves | Oblivion Ring | approved | - |
| `reveal` | reveals cards | script Reveal / PeekAndReveal; CR 701.16 | approved | - |
| `roll_die` | the effect rolls a die; die_sides is the number of sides (d20 = 20) | approved 2026-10-27: TAG_GAP_CANDIDATES section A (user: approve A) | approved | - |
| `scry_count` | scry N (CR 701.22); one tag with the number: looks at the top cards and may bottom them; counts as draw synergy (H43) | cross-check: Oracle (Serum Visions) | approved | spellslinger.cantrip |
| `shuffle` | library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle | Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow | approved | - |
| `surveil` | surveil N (CR 701.25) | cross-check: Oracle (Dragon's Rage Channeler) | approved | spellslinger.support_surveil; self_mill.support_surveil |
| `take` | of the looked-at cards, take this many (may_ = optional, all = every matching card, then an optional type or filter); to_zone says where they go | reverse check r1: Militia Bugler, Dig Through Time | approved | - |
| `to_zone` | zone the card goes to (hand, library, exile, battlefield). Pairs with return or take in the same group | reverse check r1: Militia Bugler, Dig Through Time | approved | - |
| `token_ability` | ability the created token has, in words (tap_sacrifice_add_mana_any_color = {T}, Sacrifice: Add one mana of any color) | user 2026-10-22: remake artifact_token more readable | approved | - |
| `token_cardtype` | the token is an artifact | Memnarch, Oko | approved | - |
| `token_color` | what a token ability creates; Food and Treasure are token types | Captain's Call, Memnarch, Oko, Garruk | approved | - |
| `token_count` | what a token ability creates; Food and Treasure are token types | Captain's Call, Memnarch, Oko, Garruk | approved | tokens.doubler |
| `token_kw` | what a token ability creates; Food and Treasure are token types | Captain's Call, Memnarch, Oko, Garruk | approved | - |
| `token_make` | creates tokens: 'Create a 1/1 white Soldier creature token' (qualifiers: token_count, token_type, token_pt, token_color, token_kw) | script Token; CR 111 | established | aristocrats.fodder; tokens.generator; blink.finisher; stax.parity_breaker; enchantress.payoff; superfriends.defense; polymorph.fodder |
| `token_pt` | what a token ability creates; Food and Treasure are token types | Captain's Call, Memnarch, Oko, Garruk | approved | - |
| `token_type` | token type; junk_exileplay = the Junk token (artifact: {T}, Sacrifice: exile the top card of your library, you may play it this turn, sorcery speed only) | found in the cross-check: Kiki-Jiki, Rite of Replication | approved | spellslinger.copy[copy]; combo.payoff_engine[copy]; stax.fodder[treasure]; stax.fodder[clue_draw]; artifacts.treasure[treasure]; clones.clone[copy]; vehicles.crew[pilot_crewbuff]; vehicles.crew[pilot_crewsaddlebuff]; treasure.core[treasure] |
| `tutor` | library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle | Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow | established | voltron.tutor; equipment.tutor; combo.tutor |
| `tutor_count` | library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle | Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow | approved | - |
| `tutor_dest` | library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle | Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow | approved | reanimator.enabler[graveyard]; self_mill.filler[graveyard] |
| `tutor_target` | library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle | Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow | approved | outlaws.tutor[permanent_mercenary] |

## Effects over time, replacement and restriction

| Family | Meaning | Source / reference | Approved | Used by archetypes (strategies.json) |
|---|---|---|---|---|
| `cant_be_blocked` | cannot be blocked, with the exception named in the value (by_creature_blue = by blue creatures) | restrict robustness: Brotherhood Regalia | approved | voltron.evasion |
| `cant_be_countered` | this spell can't be countered / this creature can't be blocked (by creatures of that kind); evasion, not a restriction | reverse check r1: Lightning Mare, Brotherhood Regalia | approved | tribal.protection |
| `cant_regenerate` | the destroyed creature can't be regenerated | script NoRegen$ True / Mode$ CantRegenerate; CR 701.19 (agent suggestion S07) | approved | - |
| `die_replace` | 'if it would die, exile it instead' | Scorching Dragonfire, Garruk | approved | - |
| `duration` | how long an effect lasts (eot = until end of turn, static = while the source is on the battlefield, next_untap, while_control, end_step, until_monarch_changes = until an opponent becomes the monarch...) | restrict detail: Icy Blast, Exhaustion, Time of Ice | approved | - |
| `grant_ability` | an effect gives a permanent an ability or trigger for a time, not a transformation (grant_ability:dies_trigger); replaces grant_ability + granted_trigger | reverse check r1: Feign Death, Supernatural Stamina were mis-tagged transform | approved | - |
| `grant_kw` | an effect gives a keyword for a time (duration tag says how long; eot when none is written, as Forge does) | reverse check r1: Valorous Stance (modes were not read) | approved | tokens.finisher[trample]; infect.pump[infect]; stompy.finisher[trample]; extra_combats.pump[trample]; vehicles.crew[crew] |
| `prevent_damage` | prevents damage that would be dealt (a targeted shield, not all combat damage) | - | approved | - |
| `pump_amount` | a continuous (static) effect that changes power/toughness or grants a keyword while the source is on the battlefield (duration:static marks it as static); the amount is the +p/+t (x when it scales) | reverse check r1: Benalish Marshal, Predatory Wurm, Storm-Kiln Artist had no ability tag | approved | - |
| `regenerate` | regenerates a creature | - | approved | - |
| `replace` | a replacement effect: replace:<event>_to_<what> (draw_to_winsgame = instead of drawing, win the game; damagedone_to_other = changes damage that would be dealt to another permanent, e.g. with prevent_damage a shield for your other creatures) | reverse check r1: Kami of Whispered Hopes, Laboratory Maniac | approved | tokens.doubler; mill.doubler; counters.multiplier; big_mana.multiplier; superfriends.doubler; burn.multiplier; energy.multiplier; upkeep_triggers.doubler |
| `restrict_kind` | kind of restriction placed on a creature (cant_attack, cant_block, cant_attack_or_block, cant_attack_unless_cost) | user 2026-10-22: make restrict robust (Pacifism, Goblin Heelcutter, Icy Blast, Merfolk Trickster) | approved | stax.lock[doesnt_untap]; forced_combat.protection[cant_attack]; pillow_fort.fort[cant_attack]; pillow_fort.fort[cant_attack_unless_cost] |
| `scales` | the amount (X) of this ability is the number of that kind of thing you control: write it as 'for each <thing> you control' (scales:island on a draw_count:x = draw a card for each Island you control) | script Count$ variables (ability_tags.py) | established | stompy.big_body[creature_power_ge_4]; outlaws.lord[outlaw]; self_mill.payoff[graveyard]; self_mill.payoff[card_you_own_in_graveyard]; self_mill.payoff[creature_you_own_in_graveyard]; vehicles.payoff[vehicle] |
| `steal` | gain control of a permanent | Rowan | approved | theft.steal |
| `x_is` | what the amount is when it is not a plain number. Do NOT write the letter X for these: count_<thing>_you_control = 'for each <thing> you control'; own_power / target_power = 'equal to that creature's power'; previous_result = 'equal to the amount the previous effect produced' (damage dealt, life lost ...). Only x_paid means the letter X (the X in the mana cost). Example: damage_amount:x x_is:count_creature_you_control = deals damage equal to the number of creatures you control | reverse check r1/r2: Swords to Plowshares, Feed the Swarm, Gray Merchant, Exsanguinate; user 2026-10-22: make x_is robust with linked conditions (target power, life lost ...) | approved | big_mana.haymaker[x_paid]; artifacts.win[count_artifact_you_control]; lands_matter.payoff[count_land_you_control]; mutate.mutate[timesmutated]; vehicles.payoff[count_vehicle_you_control_times_2] |

## Other

| Family | Meaning | Source / reference | Approved | Used by archetypes (strategies.json) |
|---|---|---|---|---|
| `additional_cost` | the spell has a mandatory additional cost to cast it (discard a card, sacrifice a creature ...); the cost tags (not the mana cost) say which; it is not the spell's own mana cost | script A:SP$ with CostDesc$ As an additional cost to cast; CR 118.8 | approved | - |
| `ai_logic` | the Forge AI's AILogic$ name from the card script; a reference tag for how the AI plays the card (3rd source, H54) | cross-check: script AILogic$ / AttachAILogic | approved | - |
| `alt_additional_cost` | an alternative additional cost as the card is cast (reveal a card or pay mana, for example); the cost tags follow | script K:AlternateAdditionalCost; CR 118.8 | approved | - |
| `artifact_token` | AI tag: creates artifact tokens | AI Tags category | established | artifacts.treasure |
| `attack_tax` | attackers must pay a cost per attacker | script Mode$ CantAttack with a cost | established | stax.lock; group_hug.pillowfort; forced_combat.protection; pillow_fort.fort |
| `becomes` | an Animate effect: what it becomes, and that it loses all abilities | Oko | established | - |
| `bolster` | bolster N (CR 701.39): put N +1/+1 counters on the creature you control with the least toughness; the value is N | user 2026-10-23, P4c D (Elite Scaleguard) | approved | - |
| `bounce` | returns a permanent to its owner's hand | script ChangeZone Battlefield -> Hand | established | blink.support_bounce; control.support_bounce |
| `burn` | AI tag: damage or life loss that can hit a player (any target, player or opponent); the damage itself is tagged damage, damage_amount and target_type | ability_tags.py rule: DealDamage with ValidTgts Any/Player/Opponent, or LoseLife on an opponent; AI Tags category | established | burn.damage; group_slug.slug |
| `cast_free` | casts a spell without paying its mana cost | found in the cross-check: Rishkar's Expertise | approved | storm.support_cast_free; combo.support_cast_free; polymorph.support_cast_free |
| `clone` | enters as a copy of another permanent: 'You may have this enter as a copy of any creature on the battlefield' | script Clone / ETBReplacement Clone | established | spellslinger.copy; combo.payoff_engine; blink.flicker; clones.clone |
| `color` | which spells a cost reduction applies to (colorless is the sixth colour: color:colorless, H78) | Bontu's Monument | approved | - |
| `colorless_card` | the card is a colorless spell (no colored mana symbol, no color indicator, or Devoid; lands excluded); colorless is the sixth colour, so the deck needs colorless-capable mana for it | user 2026-10-26: color and mana tags include colorless | approved | - |
| `controller` | who controls the permanent after the effect: controller:you (default: it enters under the control of the player who controls the effect) or controller:owner (only when the Oracle text says 'under its owner's control') | - | approved | - |
| `defense` | battle defense value | Invasion of ... battles | established | - |
| `effect` | sacrifice happens as an effect (not a cost) | Garruk, Kiki-Jiki, Victimize | approved | aristocrats.edict[sacrifice]; polymorph.polymorph[sacrifice] |
| `enters_prepared` | the creature enters prepared: while prepared its controller may cast a copy of the spell on its other half (the spell half's tags are in the card's groups); casting it unprepares the creature | script K:ETBReplacement with AlterAttribute Attributes$ Prepared; AlternateMode:Prepare | approved | - |
| `enters_tapped` | the permanent enters tapped | Myriad Landscape, Frost Marsh | approved | - |
| `enters_tapped_conditional` | lands that enter untapped, or tapped unless a condition holds (enters_tapped stays for always-tapped) | user note: tag whether a land enters tapped | established | - |
| `enters_untapped` | lands that enter untapped, or tapped unless a condition holds (enters_tapped stays for always-tapped) | user note: tag whether a land enters tapped | approved | - |
| `evasion` | hard to block: menace, shadow, fear, intimidate, landwalk, can't be blocked (flying keeps its own tag) | ability_tags.KEYWORD_TAGS and cant_be_blocked; landwalk added on the user's order 2026-10-22 | established | voltron.evasion; equipment.carrier |
| `evasion_grant` | AI tag: grants an evasion keyword | AI Tags category | established | voltron.support_evasion_grant; extra_combats.support_evasion_grant |
| `exchange_control` | swap control of two permanents (linked to steal) | Oko | established | - |
| `fight` | a creature fights another (CR 701.14) | cross-check: Oracle (Prey Upon, Pounce) | approved | stompy.support_fight |
| `fixing` | AI tag: fixes mana colours | AI Tags category | established | - |
| `flicker` | exiles a permanent, then returns that card to the battlefield (blink) | approved 2026-10-28 (H109): Cloudshift, Ephemerate | approved | blink.flicker |
| `grant_type` | a static effect gives permanents an extra type (all lands are also Forests) | approved 2026-10-27: Yavimaya, Cradle of Growth | approved | tribal.support_grant_type |
| `grave_hate` | exiles or punishes cards in graveyards | script ChangeZone Graveyard -> Exile | established | mill.graveyard_exile |
| `haste_grant` | AI tag: grants haste | AI Tags category | established | stompy.haste; extra_combats.haste |
| `impulse_draw` | exile cards and let you play them for a limited time; counted and linked like draw (count, duration, tempo) | Invasion of Kaldheim; user note: same links as draw | approved | impulse_draw.core |
| `impulse_draw_count` | exile cards and let you play them for a limited time; counted and linked like draw (count, duration, tempo) | Invasion of Kaldheim; user note: same links as draw | approved | - |
| `investigate` | investigate (CR 701.16): create a Clue token | user 2026-10-23, P4c D (Thraben Inspector) | approved | artifacts.support_investigate; treasure.support_investigate |
| `land_tutor` | AI tag: searches the library for a land | AI Tags category | established | landfall.fetch; landfall.ramp; big_mana.ramp; lands_matter.ramp_land |
| `lord` | gives a bonus to all creatures of a type | script S: Continuous with a type filter | established | tokens.anthem; tribal.lord; stompy.anthem; outlaws.lord[assassin]; outlaws.lord[pirate]; outlaws.lord[rogue] |
| `loyalty` | planeswalker loyalty, and the loyalty change an ability makes (renamed from loyalty_cost, user note); loyalty is a kind of counter | Oko, Rowan | established | superfriends.walker |
| `loyalty_change` | planeswalker loyalty, and the loyalty change an ability makes (renamed from loyalty_cost, user note); loyalty is a kind of counter | Oko, Rowan | established | counters.seed; superfriends.walker; superfriends.extra_activation |
| `mech` | the card needs a rule or component many decks and the Forge AI handle poorly (mech:monarch, mech:vote, mech:day_night ...); the deck builder allows it only from a set tier | user 2026-10-25 (replaces build.SKIP_TEXT) | approved | graveyard.support_mech_graveyard_cast[graveyard_cast]; self_mill.support_mech_graveyard_cast[graveyard_cast] |
| `monarch` | you become the monarch (CR 724) | user 2026-10-23, P4c D (Palace Jailer) | approved | group_hug.support_monarch; pillow_fort.support_monarch |
| `must_attack` | creatures must attack each combat (a can't-block effect on other creatures is tagged restrict, not a separate tag) | Rabblemaster; user: cant_block tag removed | approved | forced_combat.force |
| `named` | the printed name of ANOTHER card (or a named token/Role) that an ability mentions: 'a card named X', 'Partner with X'; words joined by _, casing kept; emitted only by tagcheck/mtg2llm.py tag, only with a value taken from the card's own script; own name, keywords, types and token words are never named: | user task 2026-10-23: names must survive the tag -> render round trip; Pir, Toothy, Agency Outfitter | approved | - |
| `niche` | the card is only good in a deck built around the named theme (niche:artifact, niche:landfall, niche:tribal ...); the power score gives it half role credit; a card with this tag fits few decks | user 2026-10-25 (niche cards), power_scorer.py NICHE_ROLE | approved | storm.payoff[storm]; landfall.payoff[landfall]; landfall.fetch[lands]; lands_matter.payoff[lands]; lands_matter.payoff[land]; vehicles.vehicle[vehicle]; sagas.reuse[saga]; landfall: big_mana, landfall, lands_matter; lands: big_mana, landfall, lands_matter; land: landfall, lands_matter, stax; graveyard_hate: control, stax; self_mill: aristocrats, graveyard, mill, reanimator, self_mill; haunt: aristocrats; tribal: tribal; storm: combo, spellslinger, storm; artifact: artifacts, equipment, treasure, vehicles; enchantment: control, enchantress, pillow_fort, sagas; aura: enchantress, voltron; equipment: equipment, voltron; vehicle: artifacts, vehicles; saga: blink, enchantress, sagas; planeswalker: superfriends; battle: outlaws, stompy; chaos: forced_combat, group_hug, polymorph |
| `num` | number in a keyword cost or qualifier (kicker, ward, equip amounts) | script K: line | established | - |
| `phase_out` | permanents phase out | script Phases; CR 702.26 | approved | tokens.protection; voltron.protection |
| `power_scales` | the creature's power is the number of that kind of thing you control (power_scales:creatures_you_control) | - | established | - |
| `produce_colors` | which colours the mana ability can make when they depend on lands: opp_lands_can = any colour a land an opponent controls could produce | - | established | - |
| `proliferate` | adds a counter of each kind to chosen permanents/players | script Proliferate; CR 701.34 | established | counters.proliferate; infect.proliferate; sagas.reuse |
| `protection_trick` | gives protection or indestructibility at instant speed | script Pump KW$ Protection / Indestructible | established | tokens.protection; voltron.protection; equipment.protection; combo.protection; counters.protection; infect.protection; enchantress.protection; artifacts.protection; mutate.protection; polymorph.protection; pillow_fort.protection; upkeep_triggers.protection |
| `pump_single` | pumps one target creature | script Pump with a target | established | infect.pump |
| `pump_team` | AI tag: pumps several creatures | AI Tags category | established | tokens.anthem; tokens.finisher; tribal.lord; tribal.anthem; stompy.anthem; extra_combats.pump |
| `reanimate` | AI umbrella: any effect that moves a card from a graveyard onto the battlefield; derived from put_onto_battlefield + from_zone:graveyard (the readable detail is those tags and controller) | AI Tags category; derived in tag_variant.py | established | aristocrats.fodder; aristocrats.recursion; tribal.recursion; reanimator.reanimation; graveyard.recursion |
| `removal` | AI tag: umbrella for removal when no method tag applies | AI Tags category | established | - |
| `restrict_scope` | the restriction is a drawback on the card itself (a creature that can't block) | restrict robustness: Bloodghast, Bog Hoodlums | established | - |
| `restricted_to` | general tag, any archetype: the card's mana (spend only to cast <type> spells) or return ability (target <type> card from your graveyard) names a creature type, so it works only in a deck with that type. The builder gives it commander support only when the type is the commander's or an allowed tribe | user 2026-10-27, Haven of the Spirit Dragon (restricted_to:dragon) | established | - |
| `sacrifice_outlet` | can sacrifice other permanents (not just itself or lands) | script Cost$ Sac<..>; human_logic rule on self/land sacrifice | established | aristocrats.outlet; mill.outlet |
| `sacrifice_type` | what an edict makes players sacrifice | Garruk | approved | - |
| `secret_choice` | a player chooses secretly, then the choices are revealed and compared | approved 2026-10-27: Wheel of Misfortune, Expert-Level Safe | approved | - |
| `selection` | AI tag: card selection (look, scry, loot) | AI Tags category | established | spellslinger.cantrip; storm.cantrip; combo.draw_select |
| `self_mill` | mills the card's own controller: 'Mill three cards' (you put cards from your library into your graveyard) | script Mill with a Defined player | established | reanimator.enabler; graveyard.filler; mill.engine; self_mill.filler |
| `setup_card` | general tag, any archetype: the card does nothing until the deck supplies <need>; need = mana (big mana to pay an activation cost), counters (+1/+1 or other counters), graveyard, tokens. The builder counts the card's utility only when the deck meets the need (mana: 10 ramp pieces) | user 2026-10-27, Dark Depths (setup_card:mana) | established | - |
| `shrink` | gives -X/-X to a creature | script Pump with negative amounts | established | - |
| `steal_grants` | the control-gain effect also gives a keyword (linked to steal) | Rowan | established | - |
| `steal_grants_haste` | the stolen permanent gains haste | script GainControl AddKWs$ Haste | approved | - |
| `steal_temp` | gains control until end of turn | script GainControl with Untap / LoseControl | established | theft.steal |
| `tap_down` | taps target permanents and keeps them tapped | script Tap / TapAll | established | stax.support_tap_down; control.support_tap_down |
| `tempo` | net cards added to your hand or battlefield minus cards removed (the spell itself, sacrificed or discarded cards) when the ability resolves; tokens count 0.5 each; only positive values are tagged; tempo:x when an amount is a variable | user note: tempo gain (+1), applied to every ability that adds more cards than it removes | approved | - |
| `transform` | the card has a back face (double-faced) or an ability transforms it: write 'Transform this permanent' / 'When ..., transform it'; with nothing else it is just a double-faced card | Invasion battles | approved | - |
| `unless_cost_amount` | the mana an 'unless pays' tax asks for (unless_cost_amount:2 = unless its controller pays {2}); also the per-creature attack tax | P4c E, user 2026-10-23 (Sage's Dousing, Ghostly Prison) | approved | - |
| `win` | the card wins the game outright; win:alt_condition = a win condition other than reducing life to zero (its trigger or cost tags say when) | - | established | - |

## AI Tags (hidden from the blind reader)

| Family | Meaning | Source / reference | Approved | Used by archetypes (strategies.json) |
|---|---|---|---|---|
| `recursion` | the card returns itself (to hand, from the graveyard) | Rancor | approved | aristocrats.fodder; aristocrats.recursion; tribal.recursion; graveyard.recursion; graveyard.backup_engine; spellslinger.rebuy; blink.recursion; landfall.recursion; enchantress.recursion; artifacts.recursion; lands_matter.recursion; clones.recursion; mutate.recursion; self_mill.recursion; sagas.reuse |
| `restrict` | an effect that stops something from acting: can't attack or block (A/B), can't attack (A), can't block (B), its abilities can't be activated, doesn't untap, or loses its abilities; `restrict` stays as the umbrella, the kind says which; who is affected is in the target / affected tags and how long in the duration tag | user 2026-10-22: make restrict robust (Pacifism, Goblin Heelcutter, Icy Blast, Merfolk Trickster) | established | stax.lock; group_hug.pillowfort |


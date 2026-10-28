# Tag reference

The definition of every tag family: 190 families. This file is the source of tag definitions. It is generated from `tag_extra.LEGEND` / `DOC` / `REF_EXTRA` and `tag_verify.DOC` (change a meaning there and rerun `deckgen/tag_run.py starter`); it does not read any card set. Status: `approved` = a family the user approved (lists in `tag_reports.py`); `established` = older family in use before the approval process; a family not yet approved is listed in NEW_TAGS_FOR_APPROVAL.md.

## How a record reads

- `typing:` the card's own typing (supertype, cardtype, type, landtype). `tags:` what its abilities do. `ai_tags:` AI Tags (tempo, ai_logic, umbrella labels); hidden from the blind reader. All lower case.
- `groups` tie tags to one line of the card: `k1` keyword line, `c1` first ability line, `c1.2` its sub-ability, `s1` saga chapter, `x` cross-check additions, `c0` card level. `links` relate tags: requires, provides, lasts, receives, produces, scales_with, measures, depends_on, filters, uses.
- Zone moves share `from_zone:<zone>` / `to_zone:<zone>`; `rest_to_zone` and `rest_order` describe the cards not taken. Qualifier families (draw_count, damage_amount, token_count, cost_reduce_amount ...) travel with their bare tag on purpose (REDUNDANCY_OK).
- `niche:<archetype>` marks an effect that only pays in a deck built around that archetype (consumers weigh it down unless the archetype matches); `derived:` tags are computed from other tags.
- Sources: card script (Forge `A:`/`S:`/`T:`/`R:`/`K:` lines and SVars) with its Oracle section as gap filler, keyword reference (CR 702/701), Forge AI (`AILogic`). The gap filler adds triggers, costs and keywords the script lacks; ability phrases it finds are flags only.

## Typing line (what the card is)

| Family | Meaning | Source / reference | Approved |
|---|---|---|---|
| `cardtype` | card type from the Types line: creature, instant, sorcery, artifact, enchantment, land, planeswalker, kindred | script Types: line; CR 205.2 | established |
| `landtype` | basic land type of a basic land (swamp, forest ...): the land taps for that mana | script Types: line; CR 305.6 | established |
| `supertype` | supertype: legendary, basic, snow, world | script Types: line; CR 205.4 | established |
| `type` | creature or other subtype from the Types line (human, wizard, equipment ...) | script Types: line; CR 205.3 | established |

## Keywords and engine lines

| Family | Meaning | Source / reference | Approved |
|---|---|---|---|
| `forge_line` | a Forge engine line that is not a rules keyword. forge_line:etbcounter = 'enters with counters on it' (the counter tags say which); forge_line:etbreplacement = an 'as this enters' choice or replacement | found in the cross-check: these were wrongly tagged kw: | established |
| `kw` | keyword ability the card has; qualifiers (numbers, costs, colours) follow as separate tags | script K: line; CR 702; reminder text in ai_lab/KEYWORD_REMINDER_TEXT.toon | established |
| `landwalk` | which land type a landwalk keyword names | user: landwalk type as its own tag | established |
| `protection_from` | what a Protection keyword protects from (kw:protection stays the keyword) | user: protection parsed as the keyword, colours and types as separate tags | established |

## When it happens (triggers, conditions, limits)

| Family | Meaning | Source / reference | Approved |
|---|---|---|---|
| `activation_restriction` | the ability can only be activated under a condition | Temple of the False God | approved |
| `condition` | the ability works only while this is true (a permanent or card you control, or an empty library) | reverse check r1: Predatory Wurm, Laboratory Maniac; user 2026-10-22: prune redundant proposed tags | approved |
| `delayed` | an effect that happens at the next end step | Kiki-Jiki | approved |
| `limit` | limit on how often the ability works (once_per_turn = only once each turn) | script ActivationLimit$ | approved |
| `optional` | the effect of this group is optional (you may ...) | script Optional$ True / OptionalDecider$ You (agent suggestion S01) | approved |
| `saga_chapter` | marks an ability as a saga chapter (the chapter number is not kept; how many chapters the saga has is kw:chapter + num) | reverse check r1: Time of Ice | approved |
| `trigger` | event that triggers the ability (attacks, dies, etb, gain_life, beginning_of_combat ...) | cross-check: Oracle line starts (CR 603) | approved |
| `trigger_filter` | narrows the triggering card or spell: a card type (always named for another card's zone-change trigger: trigger_filter:creature = another creature), a negated type (noncreature = noncreature spell), power_ge_N / power_le_N (power at least / at most N), one_or_more (triggers once for a group) | Rancor, Oblivion Ring, Bontu's Monument | approved |
| `trigger_scope` | which cards fire a zone-change trigger: self = this card only, other = another card, any = this card or any other card | found in the cross-check: Morbid Opportunist, Welcoming Vampire | approved |
| `trigger_zone` | trigger event, the zone it goes to, and a card-type filter on cast triggers | Rancor, Oblivion Ring, Bontu's Monument | approved |
| `unless_cost` | the effect happens unless a player pays a cost (a tax, not a choice); unless_cost_amount says how much | script UnlessCost$ | approved |

## Costs and mana

| Family | Meaning | Source / reference | Approved |
|---|---|---|---|
| `cost` | non-mana cost of the ability (tap, sacrifice, remove_counters, exile with from_zone, life, discard, return) | cross-check: Oracle cost text (CR 602, 118) | approved |
| `cost_energy` | the cost pays energy counters | approved 2026-10-27: Aethertide Whale | approved |
| `cost_exile_target` | what is exiled from the graveyard as a cost | script Cost$ ExileFromGrave | approved |
| `cost_if_you_do` | the 'If you do' part marks the preceding sacrifice/discard as a cost | user note on Victimize | approved |
| `cost_mana` | the mana part of an activation cost, symbols joined (cost_mana:2b = {2}{B}, cost_mana:x = {X}); cost:mana is not tagged when this tag is present | P4c E, user 2026-10-23 (placeholder triage: {cost} was 117 of 317 placeholders) | approved |
| `cost_reduce` | spells cost less to cast (qualifiers: cost_reduce_for, cost_reduce_amount, cost_reduce_mana) | script S: Mode$ ReduceCost; CR 601.2f | established |
| `cost_reduce_amount` | how much each affected spell costs less (generic mana) | script Amount$ on ReduceCost | approved |
| `cost_reduce_for` | which spells a cost reduction applies to (a card type, a creature type, or chosen_type); cost_reduce_amount is how much cheaper | Bontu's Monument | approved |
| `cost_reduce_mana` | the kind of mana the cost is reduced by (generic = any mana) | script ReduceCost; CR 601.2f | approved |
| `cost_return_target` | non-mana costs: return a permanent you control to hand; exile a card from your graveyard | reverse check r1: Soratami Savant, Disciple of the Ring | approved |
| `cost_sacrifice_target` | what a sacrifice cost sacrifices (self, land, creature ...) | Harrow, Blighted Woodland | approved |
| `mana` | colour of mana an ability produces (white, blue, black, red, green, colorless, any, commander_identity; colorless is the sixth colour, H78) | feedback: link color type to mana source (Arcane Signet, Plains, Temple, Frost Marsh) | approved |
| `mana_amount` | how much mana is produced per activation; always tagged on a mana source ability, also when it is 1 | Temple of the False God; user note: always tag mana_amount | approved |
| `mana_amount_if` | mana added when the condition holds; mana_amount is the base amount otherwise | script Count$Compare <SVar> <op><n>.<then>.<else> | approved |
| `mana_choice` | the ability lets you choose between colours | Frost Marsh, Arcane Signet | approved |
| `mana_conditional` | the mana ability adds a different amount, or works only, when the condition: tag of its group holds | script IsPresent$ on the mana ability, or Amount$ with Count$Compare | approved |
| `mana_restriction` | the mana can be spent only on what the value says (mana_restriction:instant_or_sorcery = spend this mana only to cast an instant or sorcery spell) | Vodalian Arcanist; script RestrictValid$ | approved |
| `mana_source` | the card or ability adds mana (qualifiers: mana, mana_amount, mana_choice, mana_restriction) | script Mana abilities (AB$ Mana, Produced$); CR 106 | established |
| `untap` | an effect untaps permanents | cross-check: Oracle (Captivating Crew) | approved |

## Targets, scope and choices

| Family | Meaning | Source / reference | Approved |
|---|---|---|---|
| `affected_filter` | what a static effect applies to (anthem: other creatures you control) | reverse check r1: Benalish Marshal | approved |
| `affected_scope` | whose permanents the effect or static ability affects (you_control, opponent_controls, all) | reverse check r1: Benalish Marshal | approved |
| `affected_type` | what a static effect applies to (anthem: other creatures you control) | reverse check r1: Benalish Marshal | approved |
| `affects` | which creature type a static effect applies to | Goblin Rabblemaster | approved |
| `choice_option` | one of the options the choice offers (choose_on_enter lists them: artifact, creature, enchantment ...) | script ValidTypes$ / Choices$ of the Choose effect | approved |
| `choose_on_enter` | as this card enters the battlefield its controller chooses something (color, card_type, creature_type, player ...); other tags of the card refer to the choice (cost_reduce_for:chosen_type = spells of the chosen type) | script K:ETBReplacement with a Choose* effect; CR 614.12 | approved |
| `target_count` | how many things the effect picks | Filter Out, Rowan, Oko | approved |
| `target_filter` | what the effect can pick: card type, filters such as nonland, and whose | Filter Out, Scorching Dragonfire, Oblivion Ring | approved |
| `target_scope` | whose things or which players the effect hits (you_control, opp_control; no tag = whoever controls it; each_opponent = every opponent, each_player = every player; no value means a single chosen target) | Filter Out, Scorching Dragonfire, Oblivion Ring | approved |
| `target_type` | what the effect can pick: card type, filters such as nonland, and whose | Filter Out, Scorching Dragonfire, Oblivion Ring | approved |
| `target_zone` | the zone the targets are in (graveyard, exile, hand, library) | Victimize | approved |

## What it does (effects and amounts)

| Family | Meaning | Source / reference | Approved |
|---|---|---|---|
| `counter` | a counter on a permanent; counter:landmark = a landmark counter (Treasure Map: counts up to three, then the card flips); counter:p1p1 = +1/+1 counter | Invasion of Moag | approved |
| `counter_count` | amounts the first run dropped: life gained or lost, counters placed | reverse check r1: 86 of 348 cards lost a number | approved |
| `counter_remove` | removes counters as an effect (cost:remove_counters is the cost) | approved 2026-10-27: Phantom Nantuko | approved |
| `counters` | planeswalker loyalty, and the loyalty change an ability makes (renamed from loyalty_cost, user note); loyalty is a kind of counter | Oko, Rowan | established |
| `counters_plus` | puts +1/+1 counters on something: 'Put a +1/+1 counter on target creature' | script PutCounter P1P1; CR 122 | established |
| `counterspell` | counters a spell | script Counter; CR 701.6 | established |
| `damage` | deals damage (damage is damage, not removal) | Scorching Dragonfire, Rowan | approved |
| `damage_amount` | deals damage (damage is damage, not removal) | Scorching Dragonfire, Rowan | approved |
| `die_sides` | the effect rolls a die; die_sides is the number of sides (d20 = 20) | approved 2026-10-27: TAG_GAP_CANDIDATES section A (user: approve A) | established |
| `discard` | a player discards cards as an effect | cross-check: Oracle | established |
| `discard_count` | how many cards an ability draws or makes a player discard | user note: tag draw count | approved |
| `draw` | draws cards (amount in draw_count) | script Draw; CR 121 | established |
| `draw_count` | how many cards an ability draws or makes a player discard | user note: tag draw count | approved |
| `exile_from` | exiles cards from a zone other than the battlefield | found in the cross-check: Scavenging Ooze, Squee | approved |
| `extra_land_drop` | its controller may play this many additional lands each turn | script AdjustLandPlays$ | approved |
| `extra_turn` | the card takes an extra turn (script AddTurn); capped per tier in tier_rules (none below T4, 1 at T4, 2 at T5) | user 2026-10-26: own tag, replaces the name list in power_scorer | approved |
| `flip_coin` | the effect flips a coin; flip_win / flip_lose mark that an outcome has a sub-effect | approved 2026-10-27: Creepy Doll, Volatile Rig | approved |
| `flip_lose` | the effect flips a coin; flip_win / flip_lose mark that an outcome has a sub-effect | approved 2026-10-27: Creepy Doll, Volatile Rig | established |
| `flip_win` | the effect flips a coin; flip_win / flip_lose mark that an outcome has a sub-effect | approved 2026-10-27: Creepy Doll, Volatile Rig | established |
| `from_zone` | zone the card comes from (graveyard, hand, library, exile). Pairs with the other tags of the same group: return, put_onto_battlefield, cost:exile | reverse check r1: Soratami Savant, Disciple of the Ring | approved |
| `life_loss` | an effect makes a player lose life (not damage) | cross-check: Oracle 'loses N life' (Nazar, Blood Artist, Gray Merchant) | approved |
| `life_loss_amount` | amounts the first run dropped: life gained or lost, counters placed | reverse check r1: 86 of 348 cards lost a number | approved |
| `lifegain` | an effect gains life | cross-check: Oracle | established |
| `lifegain_amount` | life gained (number, x, or equal_to_life_lost) | reverse check r1: 86 of 348 cards lost a number | approved |
| `look_top` | look at the top N cards of a library | reverse check r1: Militia Bugler, Dig Through Time | approved |
| `lose_game` | the effect makes a player lose the game | approved 2026-10-27: Nine Lives | approved |
| `loses_all_abilities` | an Animate effect: what it becomes, and that it loses all abilities | Oko | approved |
| `mill` | puts cards from the top of a library into a graveyard | script Mill; CR 701.17 | established |
| `mill_count` | how many cards are milled (who is milled: mill / self_mill) | mtg2llm gap record, approved 2026-10-27: Blight Titan, Barrowgoyf | approved |
| `modal` | choose N of M modes (modal:1_of_3 = choose one of three) | reverse check r1: Valorous Stance, Return of the Wildspeaker | approved |
| `piles_split` | cards are split into two piles by this player | reverse check r1: Fact or Fiction | approved |
| `put_onto_battlefield` | a card is put onto the battlefield without being cast; from_zone says where from | user note, confirmed 2026-10-22: the tag means 'not cast' | approved |
| `put_tapped` | the card is put onto the battlefield tapped | script ChangeZone Tapped$ True | approved |
| `remove` | how a card removes something; replaces the single 'removal' tag when a method is known | Scorching Dragonfire, Oblivion Ring | approved |
| `rest_order` | position of the rest in the library: bottom, or bottom_random (bottom in a random order) | reverse check r1: Militia Bugler, Dig Through Time | approved |
| `rest_to_zone` | where the looked-at cards that were not taken go; rest_order says the position | reverse check r1: Militia Bugler, Dig Through Time | approved |
| `return` | a card is returned from one zone to another; read with from_zone and to_zone (return from_zone:graveyard to_zone:hand = return a card from graveyard to hand) | reverse check r5: Elvish Regrower lost its meaning when recursion became an AI tag | approved |
| `return_exiled` | returns what this card exiled when it leaves | Oblivion Ring | approved |
| `reveal` | reveals cards | script Reveal / PeekAndReveal; CR 701.16 | approved |
| `roll_die` | the effect rolls a die; die_sides is the number of sides (d20 = 20) | approved 2026-10-27: TAG_GAP_CANDIDATES section A (user: approve A) | approved |
| `scry_count` | scry N (CR 701.22); one tag with the number: looks at the top cards and may bottom them; counts as draw synergy (H43) | cross-check: Oracle (Serum Visions) | approved |
| `shuffle` | library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle | Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow | approved |
| `surveil` | surveil N (CR 701.25) | cross-check: Oracle (Dragon's Rage Channeler) | approved |
| `take` | of the looked-at cards, take this many (may_ = optional, all = every matching card, then an optional type or filter); to_zone says where they go | reverse check r1: Militia Bugler, Dig Through Time | approved |
| `to_zone` | zone the card goes to (hand, library, exile, battlefield). Pairs with return or take in the same group | reverse check r1: Militia Bugler, Dig Through Time | approved |
| `token_ability` | ability the created token has, in words (tap_sacrifice_add_mana_any_color = {T}, Sacrifice: Add one mana of any color) | user 2026-10-22: remake artifact_token more readable | approved |
| `token_cardtype` | the token is an artifact | Memnarch, Oko | approved |
| `token_color` | what a token ability creates; Food and Treasure are token types | Captain's Call, Memnarch, Oko, Garruk | approved |
| `token_count` | what a token ability creates; Food and Treasure are token types | Captain's Call, Memnarch, Oko, Garruk | approved |
| `token_kw` | what a token ability creates; Food and Treasure are token types | Captain's Call, Memnarch, Oko, Garruk | approved |
| `token_make` | creates tokens: 'Create a 1/1 white Soldier creature token' (qualifiers: token_count, token_type, token_pt, token_color, token_kw) | script Token; CR 111 | established |
| `token_pt` | what a token ability creates; Food and Treasure are token types | Captain's Call, Memnarch, Oko, Garruk | approved |
| `token_type` | token type; junk_exileplay = the Junk token (artifact: {T}, Sacrifice: exile the top card of your library, you may play it this turn, sorcery speed only) | found in the cross-check: Kiki-Jiki, Rite of Replication | approved |
| `tutor` | library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle | Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow | established |
| `tutor_count` | library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle | Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow | approved |
| `tutor_dest` | library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle | Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow | approved |
| `tutor_target` | library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle | Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow | approved |

## Effects over time, replacement and restriction

| Family | Meaning | Source / reference | Approved |
|---|---|---|---|
| `cant_be_blocked` | cannot be blocked, with the exception named in the value (by_creature_blue = by blue creatures) | restrict robustness: Brotherhood Regalia | approved |
| `cant_be_countered` | this spell can't be countered / this creature can't be blocked (by creatures of that kind); evasion, not a restriction | reverse check r1: Lightning Mare, Brotherhood Regalia | approved |
| `cant_regenerate` | the destroyed creature can't be regenerated | script NoRegen$ True / Mode$ CantRegenerate; CR 701.19 (agent suggestion S07) | approved |
| `die_replace` | 'if it would die, exile it instead' | Scorching Dragonfire, Garruk | approved |
| `duration` | how long an effect lasts (eot = until end of turn, static = while the source is on the battlefield, next_untap, while_control, end_step, until_monarch_changes = until an opponent becomes the monarch...) | restrict detail: Icy Blast, Exhaustion, Time of Ice | approved |
| `grant_ability` | an effect gives a permanent an ability or trigger for a time, not a transformation (grant_ability:dies_trigger); replaces grant_ability + granted_trigger | reverse check r1: Feign Death, Supernatural Stamina were mis-tagged transform | approved |
| `grant_kw` | an effect gives a keyword for a time (duration tag says how long; eot when none is written, as Forge does) | reverse check r1: Valorous Stance (modes were not read) | approved |
| `prevent_damage` | prevents damage that would be dealt (a targeted shield, not all combat damage) | - | approved |
| `pump_amount` | a continuous (static) effect that changes power/toughness or grants a keyword while the source is on the battlefield (duration:static marks it as static); the amount is the +p/+t (x when it scales) | reverse check r1: Benalish Marshal, Predatory Wurm, Storm-Kiln Artist had no ability tag | approved |
| `regenerate` | regenerates a creature | - | approved |
| `replace` | a replacement effect: replace:<event>_to_<what> (draw_to_winsgame = instead of drawing, win the game; damagedone_to_other = changes damage that would be dealt to another permanent, e.g. with prevent_damage a shield for your other creatures) | reverse check r1: Kami of Whispered Hopes, Laboratory Maniac | approved |
| `restrict_kind` | kind of restriction placed on a creature (cant_attack, cant_block, cant_attack_or_block, cant_attack_unless_cost) | user 2026-10-22: make restrict robust (Pacifism, Goblin Heelcutter, Icy Blast, Merfolk Trickster) | approved |
| `scales` | the amount (X) of this ability is the number of that kind of thing you control: write it as 'for each <thing> you control' (scales:island on a draw_count:x = draw a card for each Island you control) | script Count$ variables (ability_tags.py) | established |
| `steal` | gain control of a permanent | Rowan | approved |
| `x_is` | what the amount is when it is not a plain number. Do NOT write the letter X for these: count_<thing>_you_control = 'for each <thing> you control'; own_power / target_power = 'equal to that creature's power'; previous_result = 'equal to the amount the previous effect produced' (damage dealt, life lost ...). Only x_paid means the letter X (the X in the mana cost). Example: damage_amount:x x_is:count_creature_you_control = deals damage equal to the number of creatures you control | reverse check r1/r2: Swords to Plowshares, Feed the Swarm, Gray Merchant, Exsanguinate; user 2026-10-22: make x_is robust with linked conditions (target power, life lost ...) | approved |

## Other

| Family | Meaning | Source / reference | Approved |
|---|---|---|---|
| `additional_cost` | the spell has a mandatory additional cost to cast it (discard a card, sacrifice a creature ...); the cost tags (not the mana cost) say which; it is not the spell's own mana cost | script A:SP$ with CostDesc$ As an additional cost to cast; CR 118.8 | approved |
| `ai_logic` | the Forge AI's AILogic$ name from the card script; a reference tag for how the AI plays the card (3rd source, H54) | cross-check: script AILogic$ / AttachAILogic | approved |
| `alt_additional_cost` | an alternative additional cost as the card is cast (reveal a card or pay mana, for example); the cost tags follow | script K:AlternateAdditionalCost; CR 118.8 | approved |
| `artifact_token` | AI tag: creates artifact tokens | AI Tags category | established |
| `attack_tax` | attackers must pay a cost per attacker | script Mode$ CantAttack with a cost | established |
| `becomes` | an Animate effect: what it becomes, and that it loses all abilities | Oko | established |
| `bolster` | bolster N (CR 701.39): put N +1/+1 counters on the creature you control with the least toughness; the value is N | user 2026-10-23, P4c D (Elite Scaleguard) | approved |
| `bounce` | returns a permanent to its owner's hand | script ChangeZone Battlefield -> Hand | established |
| `burn` | AI tag: damage or life loss that can hit a player (any target, player or opponent); the damage itself is tagged damage, damage_amount and target_type | ability_tags.py rule: DealDamage with ValidTgts Any/Player/Opponent, or LoseLife on an opponent; AI Tags category | established |
| `cast_free` | casts a spell without paying its mana cost | found in the cross-check: Rishkar's Expertise | approved |
| `clone` | enters as a copy of another permanent: 'You may have this enter as a copy of any creature on the battlefield' | script Clone / ETBReplacement Clone | established |
| `color` | which spells a cost reduction applies to (colorless is the sixth colour: color:colorless, H78) | Bontu's Monument | approved |
| `colorless_card` | the card is a colorless spell (no colored mana symbol, no color indicator, or Devoid; lands excluded); colorless is the sixth colour, so the deck needs colorless-capable mana for it | user 2026-10-26: color and mana tags include colorless | approved |
| `controller` | who controls the permanent after the effect: controller:you (default: it enters under the control of the player who controls the effect) or controller:owner (only when the Oracle text says 'under its owner's control') | - | approved |
| `defense` | battle defense value | Invasion of ... battles | established |
| `effect` | sacrifice happens as an effect (not a cost) | Garruk, Kiki-Jiki, Victimize | approved |
| `enters_prepared` | the creature enters prepared: while prepared its controller may cast a copy of the spell on its other half (the spell half's tags are in the card's groups); casting it unprepares the creature | script K:ETBReplacement with AlterAttribute Attributes$ Prepared; AlternateMode:Prepare | approved |
| `enters_tapped` | the permanent enters tapped | Myriad Landscape, Frost Marsh | approved |
| `enters_tapped_conditional` | lands that enter untapped, or tapped unless a condition holds (enters_tapped stays for always-tapped) | user note: tag whether a land enters tapped | established |
| `enters_untapped` | lands that enter untapped, or tapped unless a condition holds (enters_tapped stays for always-tapped) | user note: tag whether a land enters tapped | approved |
| `evasion` | hard to block: menace, shadow, fear, intimidate, landwalk, can't be blocked (flying keeps its own tag) | ability_tags.KEYWORD_TAGS and cant_be_blocked; landwalk added on the user's order 2026-10-22 | established |
| `evasion_grant` | AI tag: grants an evasion keyword | AI Tags category | established |
| `exchange_control` | swap control of two permanents (linked to steal) | Oko | established |
| `fight` | a creature fights another (CR 701.14) | cross-check: Oracle (Prey Upon, Pounce) | approved |
| `fixing` | AI tag: fixes mana colours | AI Tags category | established |
| `grant_type` | a static effect gives permanents an extra type (all lands are also Forests) | approved 2026-10-27: Yavimaya, Cradle of Growth | approved |
| `grave_hate` | exiles or punishes cards in graveyards | script ChangeZone Graveyard -> Exile | established |
| `haste_grant` | AI tag: grants haste | AI Tags category | established |
| `impulse_draw` | exile cards and let you play them for a limited time; counted and linked like draw (count, duration, tempo) | Invasion of Kaldheim; user note: same links as draw | approved |
| `impulse_draw_count` | exile cards and let you play them for a limited time; counted and linked like draw (count, duration, tempo) | Invasion of Kaldheim; user note: same links as draw | approved |
| `investigate` | investigate (CR 701.16): create a Clue token | user 2026-10-23, P4c D (Thraben Inspector) | approved |
| `land_tutor` | AI tag: searches the library for a land | AI Tags category | established |
| `lord` | gives a bonus to all creatures of a type | script S: Continuous with a type filter | established |
| `loyalty` | planeswalker loyalty, and the loyalty change an ability makes (renamed from loyalty_cost, user note); loyalty is a kind of counter | Oko, Rowan | established |
| `loyalty_change` | planeswalker loyalty, and the loyalty change an ability makes (renamed from loyalty_cost, user note); loyalty is a kind of counter | Oko, Rowan | established |
| `mech` | the card needs a rule or component many decks and the Forge AI handle poorly (mech:monarch, mech:vote, mech:day_night ...); the deck builder allows it only from a set tier | user 2026-10-25 (replaces build.SKIP_TEXT) | approved |
| `monarch` | you become the monarch (CR 724) | user 2026-10-23, P4c D (Palace Jailer) | approved |
| `must_attack` | creatures must attack each combat (a can't-block effect on other creatures is tagged restrict, not a separate tag) | Rabblemaster; user: cant_block tag removed | approved |
| `named` | the printed name of ANOTHER card (or a named token/Role) that an ability mentions: 'a card named X', 'Partner with X'; words joined by _, casing kept; emitted only by tagcheck/mtg2llm.py tag, only with a value taken from the card's own script; own name, keywords, types and token words are never named: | user task 2026-10-23: names must survive the tag -> render round trip; Pir, Toothy, Agency Outfitter | approved |
| `niche` | the card is only good in a deck built around the named theme (niche:artifact, niche:landfall, niche:tribal ...); the power score gives it half role credit; a card with this tag fits few decks | user 2026-10-25 (niche cards), power_scorer.py NICHE_ROLE | approved |
| `num` | number in a keyword cost or qualifier (kicker, ward, equip amounts) | script K: line | established |
| `phase_out` | permanents phase out | script Phases; CR 702.26 | approved |
| `power_scales` | the creature's power is the number of that kind of thing you control (power_scales:creatures_you_control) | - | established |
| `produce_colors` | which colours the mana ability can make when they depend on lands: opp_lands_can = any colour a land an opponent controls could produce | - | established |
| `proliferate` | adds a counter of each kind to chosen permanents/players | script Proliferate; CR 701.34 | established |
| `protection_trick` | gives protection or indestructibility at instant speed | script Pump KW$ Protection / Indestructible | established |
| `pump_single` | pumps one target creature | script Pump with a target | established |
| `pump_team` | AI tag: pumps several creatures | AI Tags category | established |
| `reanimate` | AI umbrella: any effect that moves a card from a graveyard onto the battlefield; derived from put_onto_battlefield + from_zone:graveyard (the readable detail is those tags and controller) | AI Tags category; derived in tag_variant.py | established |
| `removal` | AI tag: umbrella for removal when no method tag applies | AI Tags category | established |
| `restrict_scope` | the restriction is a drawback on the card itself (a creature that can't block) | restrict robustness: Bloodghast, Bog Hoodlums | established |
| `restricted_to` | general tag, any archetype: the card's mana (spend only to cast <type> spells) or return ability (target <type> card from your graveyard) names a creature type, so it works only in a deck with that type. The builder gives it commander support only when the type is the commander's or an allowed tribe | user 2026-10-27, Haven of the Spirit Dragon (restricted_to:dragon) | established |
| `sacrifice_outlet` | can sacrifice other permanents (not just itself or lands) | script Cost$ Sac<..>; human_logic rule on self/land sacrifice | established |
| `sacrifice_type` | what an edict makes players sacrifice | Garruk | approved |
| `secret_choice` | a player chooses secretly, then the choices are revealed and compared | approved 2026-10-27: Wheel of Misfortune, Expert-Level Safe | approved |
| `selection` | AI tag: card selection (look, scry, loot) | AI Tags category | established |
| `self_mill` | mills the card's own controller: 'Mill three cards' (you put cards from your library into your graveyard) | script Mill with a Defined player | established |
| `setup_card` | general tag, any archetype: the card does nothing until the deck supplies <need>; need = mana (big mana to pay an activation cost), counters (+1/+1 or other counters), graveyard, tokens. The builder counts the card's utility only when the deck meets the need (mana: 10 ramp pieces) | user 2026-10-27, Dark Depths (setup_card:mana) | established |
| `shrink` | gives -X/-X to a creature | script Pump with negative amounts | established |
| `steal_grants` | the control-gain effect also gives a keyword (linked to steal) | Rowan | established |
| `steal_grants_haste` | the stolen permanent gains haste | script GainControl AddKWs$ Haste | approved |
| `steal_temp` | gains control until end of turn | script GainControl with Untap / LoseControl | established |
| `tap_down` | taps target permanents and keeps them tapped | script Tap / TapAll | established |
| `tempo` | net cards added to your hand or battlefield minus cards removed (the spell itself, sacrificed or discarded cards) when the ability resolves; tokens count 0.5 each; only positive values are tagged; tempo:x when an amount is a variable | user note: tempo gain (+1), applied to every ability that adds more cards than it removes | approved |
| `transform` | the card has a back face (double-faced) or an ability transforms it: write 'Transform this permanent' / 'When ..., transform it'; with nothing else it is just a double-faced card | Invasion battles | approved |
| `unless_cost_amount` | the mana an 'unless pays' tax asks for (unless_cost_amount:2 = unless its controller pays {2}); also the per-creature attack tax | P4c E, user 2026-10-23 (Sage's Dousing, Ghostly Prison) | approved |
| `win` | the card wins the game outright; win:alt_condition = a win condition other than reducing life to zero (its trigger or cost tags say when) | - | established |

## AI Tags (hidden from the blind reader)

| Family | Meaning | Source / reference | Approved |
|---|---|---|---|
| `recursion` | the card returns itself (to hand, from the graveyard) | Rancor | approved |
| `restrict` | an effect that stops something from acting: can't attack or block (A/B), can't attack (A), can't block (B), its abilities can't be activated, doesn't untap, or loses its abilities; `restrict` stays as the umbrella, the kind says which; who is affected is in the target / affected tags and how long in the duration tag | user 2026-10-22: make restrict robust (Pacifism, Goblin Heelcutter, Icy Blast, Merfolk Trickster) | established |


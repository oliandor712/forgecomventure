# Reverse check of the tags (blind reader)

Run `r2`. A blind reader saw only each card's tags and wrote the ability text they describe; that text was scored against the real Oracle text. Tool: `deckgen/tagcheck/reverse_check.py`. Similarity = 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1 (bands: good >= 0.7, partial 0.4-0.7, gap < 0.4; thresholds are unvalidated until a reader run is compared with a hand check). Mana-cost symbols are removed from both texts (costs are not tags).

## Summary

| cards | with text | mean similarity | good | partial | gap | source card ranked #1 | in top 5 | median rank |
|---|---|---|---|---|---|---|---|---|
| 353 | 348 | 0.861 | 293 | 51 | 4 | 266 | 323 | 1 |

Reader integrity: 0 outputs contain the card name (should be 0); 1 cards the reader says it recognised (a high rate weakens the test).

## What the tags failed to carry (concepts in the real text, absent from the reconstruction)

| concept | cards | share |
|---|---|---|
| you_control | 35 | 10% |
| each_all | 33 | 9% |
| opponent | 30 | 8% |
| may | 30 | 8% |
| creature | 19 | 5% |
| hand | 16 | 4% |
| eot | 14 | 4% |
| mana | 9 | 2% |
| pump | 8 | 2% |
| tap | 7 | 2% |
| block | 7 | 2% |
| reveal | 7 | 2% |
| tapped | 6 | 1% |
| cast | 6 | 1% |
| attack | 6 | 1% |
| land | 6 | 1% |
| return | 6 | 1% |
| graveyard | 5 | 1% |
| instead | 5 | 1% |
| choose | 5 | 1% |
| battlefield | 4 | 1% |
| legend | 4 | 1% |
| sacrifice | 4 | 1% |
| counters | 3 | 0% |
| kw:landfall | 3 | 0% |

## What the reader added that the real text lacks (tags that over-claim or mislead)

| concept | cards |
|---|---|
| x_value | 16 |
| creature | 6 |
| opponent | 5 |
| eot | 3 |
| each_all | 2 |
| token | 2 |
| dies | 1 |
| you_control | 1 |
| return | 1 |
| pump | 1 |
| graveyard | 1 |

## Tags the reader could not read (by family)

trigger 19, trigger_filter 9, remove 6, trigger_scope 6, color 5, target_type 5, trigger_zone 4, cost 4, forge_line 4, scales 4, damage recipient not tagged 4, x_is 3, who loses life not tagged 3, enters_untapped 2, mill 2, trigger filter not given 2, landtype 2, tutor_target 2, scry amount and order not given 2, affects 2, recursion 2, num 2, tutor_dest 2, sacrifice_outlet 2, target_count 2, protection_trick 2, reanimate 2, evasion 2, link c1 2, land_tutor 2

Most common single tags: trigger_filter:card 6, damage recipient not tagged 4, trigger_zone:graveyard 3, who loses life not tagged 3, enters_untapped 2, mill 2, cost:mana 2, trigger filter not given 2, forge_line:alternateadditionalcost 2, trigger_scope:other filter/controller not given 2, scry amount and order not given 2, recursion 2, target_type:card 2, scales:goblin 2, sacrifice_outlet 2, protection_trick 2, reanimate 2, evasion 2, link c1:payload lasts c1:duration (no duration tag) 2, land_tutor 2, token_make (no token details) 2, color:blue (on cycling group; could be the cycling cost or a land type) 1, duration:permanent (no wording given for what lasts permanently) 1, effect on creatures you control is not specified (pump_team ignored) 1, remove:bounce (appears twice, c1.2 and c1.5) 1, remove:tuck (relation to bounce, mode or sequence, not stated) 1, trigger:end_step (whose end step, and condition, not stated) 1, damage target not given 1, take_count:2 destination (hand assumed) 1, trigger_scope:other (c1, c3) 1

## Lowest 25 cards

| Card | sim | missing concepts | extra concepts | real text | reader text |
|---|---|---|---|---|---|
| Leafkin Druid | 0.35 | creature instead you_control | x_value | {T}: Add {G}. If you control four or more creatures, add {G}{G} instead. | {T}: Add X {G}. |
| Sea Gate Loremaster | 0.38 | each_all | x_value | {T}: Draw a card for each Ally you control. | {T}: Draw X cards, where X is the number of Allies you control. |
| Welcoming Vampire | 0.39 | creature each_all you_control |  | Flying / Whenever one or more other creatures you control with power 2 or less enter, draw a card. This ability triggers only once each turn. | Flying / Whenever another {filter} enters, draw a card. |
| Trumpet Blast | 0.40 | attack creature pump |  | Attacking creatures get +2/+0 until end of turn. | {Creatures} get {effect} until end of turn. |
| Return of the Wildspeaker | 0.41 | eot pump | x_value | Choose one — / • Draw cards equal to the greatest power among non-Human creatures you control. / • Non-Human creatures you control get +3/+3 until end of turn. | Choose one — / • Draw X cards. / • {effect} nonhuman creatures you control. |
| Mentor of the Meek | 0.42 | cost_pay creature may you_control |  | Whenever another creature you control with power 2 or less enters, you may pay {1}. If you do, draw a card. | Whenever another {creature filter} enters the battlefield, draw a card. |
| Elite Scaleguard | 0.43 | counters opponent tap you_control |  | When Elite Scaleguard enters, bolster 2. (Choose a creature with the least toughness among creatures you control and put two +1/+1 counters on it.) / Whenever a creature you control with a +1/+1 counter on it attacks, tap target creature defending player controls. | When this creature enters, {effect}. / Whenever this creature attacks, {effect} target creature. |
| Vines of Vastwood | 0.43 | opponent | x_value | Kicker {G} (You may pay an additional {G} as you cast this spell.) / Target creature can't be the target of spells or abilities your opponents control this turn. If this spell was kicked, that creature gets +4/+4 until end of turn. | Kicker {cost} / Target creature gets +X/+X until end of turn, where X is {value depending on kicker}. |
| Flow of Knowledge | 0.45 | each_all you_control | x_value | Draw a card for each Island you control, then discard two cards. | Draw X cards, then discard two cards. |
| Garruk's Packleader | 0.49 | creature may you_control |  | Whenever another creature you control with power 3 or greater enters, you may draw a card. | Whenever another {permanent} enters, {player} draws a card. |
| Explore | 0.49 | eot land may |  | You may play an additional land this turn. / Draw a card. | Draw a card. |
| Saruman the White | 0.50 | each_all | token | Ward {2} / Whenever you cast your second spell each turn, amass Orcs 2. (Put two +1/+1 counters on an Army you control. It's also an Orc. If you don't control an Army, create a 0/0 black Orc Army creature token first.) | Ward {2} / Whenever you cast a spell, create {token}. |
| Rishkar's Expertise | 0.50 | creature hand you_control | x_value | Draw cards equal to the greatest power among creatures you control. / You may cast a spell with mana value 5 or less from your hand without paying its mana cost. | Draw X cards. / You may cast {spell} without paying its mana cost. |
| Ripples of Potential | 0.51 | choose counters you_control |  | Proliferate, then choose any number of permanents you control that had a counter put on them this way. Those permanents phase out. (To proliferate, choose any number of permanents and/or players, then give each another counter of each kind already there. Treat phased-out permanents and anything atta | Proliferate. |
| Swords to Plowshares | 0.52 |  | x_value | Exile target creature. Its controller gains life equal to its power. | Exile target creature. / {Player} gains X life, where X is {value}. |
| Exhaustion | 0.52 | creature land tap |  | Creatures and lands target opponent controls don't untap during their next untap step. | Target opponent {effect}. |
| Feed the Swarm | 0.53 | mana | x_value | Destroy target creature or enchantment an opponent controls. You lose life equal to that permanent's mana value. | Destroy target creature an opponent controls or target enchantment. / {Player} loses X life. |
| Colossal Majesty | 0.54 | creature you_control |  | At the beginning of your upkeep, if you control a creature with power 4 or greater, draw a card. | At the beginning of your upkeep, draw a card. |
| Feign Death | 0.54 | counters eot tapped |  | Until end of turn, target creature gains "When this creature dies, return it to the battlefield tapped under its owner's control with a +1/+1 counter on it." | Target creature gains "When this creature dies, return it to the battlefield." |
| Syr Alin, the Lion's Claw | 0.55 | pump | each_all | First strike / Whenever Syr Alin, the Lion's Claw attacks, other creatures you control get +1/+1 until end of turn. | First strike / Whenever this creature attacks, each other creature you control gets {effect} until end of turn. |
| Yedora, Grave Gardener | 0.55 | flip land may return you_control | graveyard | Whenever another nontoken creature you control dies, you may return it to the battlefield face down under its owner's control. It's a Forest land. (It has no other types or abilities.) | Whenever another creature dies, put {a card} from a graveyard onto the battlefield. |
| Goreclaw, Terror of Qal Sisma | 0.55 | each_all pump |  | Creature spells you cast with power 4 or greater cost {2} less to cast. / Whenever Goreclaw, Terror of Qal Sisma attacks, each creature you control with power 4 or greater gets +1/+1 and gains trample until end of turn. | Creature spells cost {N} less to cast. / Whenever this creature attacks, creatures you control gain Trample until end of turn. |
| Mindcrank | 0.57 | lifeloss opponent trigger_when |  | Whenever an opponent loses life, that player mills that many cards. (Damage dealt by sources without infect causes loss of life.) | {Player} mills {N} cards. |
| Creeping Bloodsucker | 0.57 | each_all opponent | x_value | At the beginning of your upkeep, Creeping Bloodsucker deals 1 damage to each opponent. You gain life equal to the damage dealt this way. | At the beginning of {your} upkeep, this creature deals 1 damage to {target} and you gain X life, where X is {remembered number}. |
| Garruk's Uprising | 0.58 |  |  | When Garruk's Uprising enters, if you control a creature with power 4 or greater, draw a card. / Creatures you control have trample. (They can deal excess combat damage to the player or planeswalker they're attacking.) / Whenever a creature you control with power 4 or greater enters, draw a card. | When this enchantment enters, draw a card. / Creatures you control have trample. / Whenever another {permanent} enters, {effect}. |

## Highest 5 cards

| Card | sim | real text | reader text |
|---|---|---|---|
| Raise the Alarm | 1.00 | Create two 1/1 white Soldier creature tokens. | Create two 1/1 white Soldier creature tokens. |
| Herald of the Host | 1.00 | Flying, vigilance / Myriad (Whenever this creature attacks, for each opponent other than defending player, you may create a token copy that's tapped and attacking that player or a planeswalker they control. Exile the tokens at end of combat.) | Flying / Vigilance / Myriad |
| Dusk Legion Zealot | 1.00 | When Dusk Legion Zealot enters, you draw a card and you lose 1 life. | When this creature enters, you draw a card and you lose 1 life. |
| Bladebrand | 1.00 | Target creature gains deathtouch until end of turn. / Draw a card. | Target creature gains deathtouch until end of turn. / Draw a card. |
| Benalish Marshal | 1.00 | Other creatures you control get +1/+1. | Other creatures you control get +1/+1. |

## Known limits

- Mana-cost amounts, power/toughness and flavour are not tags; they are excluded, not scored as gaps.
- Concept and number matching are regex based; a rephrased but equal ability can score low. Read the lowest-25 table, not only the number.
- A reader that knows the real card from the tags (famous cards) inflates the score; see `recognised`.
- Similarity bands have not been checked against human judgement yet.

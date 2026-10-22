# Reverse check of the tags (blind reader)

Run `r4`. A blind reader saw only each card's tags and wrote the ability text they describe; that text was scored against the real Oracle text. Tool: `deckgen/tagcheck/reverse_check.py`. Similarity = 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1 (bands: good >= 0.7, partial 0.4-0.7, gap < 0.4; thresholds are unvalidated until a reader run is compared with a hand check). Mana-cost symbols are removed from both texts (costs are not tags).

## Summary

| cards | with text | mean similarity | good | partial | gap | source card ranked #1 | in top 5 | median rank |
|---|---|---|---|---|---|---|---|---|
| 353 | 348 | 0.876 | 308 | 38 | 2 | 266 | 325 | 1 |

Reader integrity: 0 outputs contain the card name (should be 0); 1 cards the reader says it recognised (a high rate weakens the test).

## What the tags failed to carry (concepts in the real text, absent from the reconstruction)

| concept | cards | share |
|---|---|---|
| each_all | 32 | 9% |
| you_control | 30 | 8% |
| may | 30 | 8% |
| opponent | 29 | 8% |
| hand | 14 | 4% |
| creature | 14 | 4% |
| eot | 12 | 3% |
| mana | 8 | 2% |
| reveal | 8 | 2% |
| graveyard | 6 | 1% |
| tapped | 6 | 1% |
| instead | 6 | 1% |
| cast | 6 | 1% |
| land | 6 | 1% |
| tap | 6 | 1% |
| battlefield | 5 | 1% |
| choose | 5 | 1% |
| attack | 4 | 1% |
| sacrifice | 4 | 1% |
| counters | 3 | 0% |
| kw:landfall | 3 | 0% |
| kw:flying | 3 | 0% |
| block | 3 | 0% |
| legend | 3 | 0% |
| damage | 2 | 0% |

## What the reader added that the real text lacks (tags that over-claim or mislead)

| concept | cards |
|---|---|
| x_value | 13 |
| creature | 8 |
| opponent | 7 |
| eot | 3 |
| dies | 2 |
| you_control | 2 |
| token | 2 |
| return | 1 |
| counters | 1 |
| graveyard | 1 |
| battlefield | 1 |
| target | 1 |

## Tags the reader could not read (by family)

trigger 10, recursion 6, target_type 6, trigger_scope 4, remove 3, mill 3, trigger_zone 3, cost 3, activation_restriction 3, forge_line 3, mana_restriction 2, affected_type 2, cost_reduce 2, token_make 2, mana_amount 1, replacement 1, replace_event 1, replace_with 1, tutor_target 1, color 1, cast_free 1, life_loss 1, surveil 1, affects 1, trigger_filter 1, pump_single 1, sacrifice_outlet 1, mana 1, duration 1, tutor_dest 1

Most common single tags: recursion 6, trigger_scope:other 4, trigger:dies 4, mill 3, trigger_zone:graveyard 3, cost:mana 3, activation_restriction 3, target_type:creature 3, target_type:card 3, trigger:attacks 3, mana_restriction 2, remove:tuck 2, forge_line:etbreplacement 2, cost_reduce 2, trigger:etb 2, token_make 2, mana_amount:x 1, replacement 1, replace_event:moved 1, replace_with:tap 1, tutor_target: 1, color:red 1, forge_line:alternateadditionalcost 1, affected_type:enchanted 1, cast_free 1, life_loss 1, surveil 1, affects:card 1, trigger_filter:card 1, pump_single 1

## Lowest 25 cards

| Card | sim | missing concepts | extra concepts | real text | reader text |
|---|---|---|---|---|---|
| Leafkin Druid | 0.29 | creature instead you_control | x_value | {T}: Add {G}. If you control four or more creatures, add {G}{G} instead. | {T}: Add {G} X times. |
| Sea Gate Loremaster | 0.38 | each_all | x_value | {T}: Draw a card for each Ally you control. | {T}: Draw X cards, where X is the number of Allies you control. |
| Welcoming Vampire | 0.43 | each_all you_control |  | Flying / Whenever one or more other creatures you control with power 2 or less enter, draw a card. This ability triggers only once each turn. | Flying / Whenever another creature enters, draw a card. |
| Elite Scaleguard | 0.43 | counters opponent tap you_control |  | When Elite Scaleguard enters, bolster 2. (Choose a creature with the least toughness among creatures you control and put two +1/+1 counters on it.) / Whenever a creature you control with a +1/+1 counter on it attacks, tap target creature defending player controls. | When this creature enters, {effect}. / Whenever this creature attacks, target creature {effect}. |
| Vines of Vastwood | 0.44 | opponent | x_value | Kicker {G} (You may pay an additional {G} as you cast this spell.) / Target creature can't be the target of spells or abilities your opponents control this turn. If this spell was kicked, that creature gets +4/+4 until end of turn. | Kicker {G} / Target creature gets +X/+X until end of turn. |
| Mindcrank | 0.48 | lifeloss opponent trigger_when |  | Whenever an opponent loses life, that player mills that many cards. (Damage dealt by sources without infect causes loss of life.) | Mill N cards. |
| Explore | 0.49 | eot land may |  | You may play an additional land this turn. / Draw a card. | Draw a card. |
| Saruman the White | 0.50 | each_all | token | Ward {2} / Whenever you cast your second spell each turn, amass Orcs 2. (Put two +1/+1 counters on an Army you control. It's also an Orc. If you don't control an Army, create a 0/0 black Orc Army creature token first.) | Ward {2} / Whenever you cast a spell, create {token}. |
| Ripples of Potential | 0.51 | choose counters you_control |  | Proliferate, then choose any number of permanents you control that had a counter put on them this way. Those permanents phase out. (To proliferate, choose any number of permanents and/or players, then give each another counter of each kind already there. Treat phased-out permanents and anything atta | Proliferate. |
| Mentor of the Meek | 0.51 | cost_pay may you_control |  | Whenever another creature you control with power 2 or less enters, you may pay {1}. If you do, draw a card. | Whenever another creature enters, draw a card. |
| Colossal Majesty | 0.54 | creature you_control |  | At the beginning of your upkeep, if you control a creature with power 4 or greater, draw a card. | At the beginning of your upkeep, draw a card. |
| Feign Death | 0.54 | counters eot tapped |  | Until end of turn, target creature gains "When this creature dies, return it to the battlefield tapped under its owner's control with a +1/+1 counter on it." | Target creature gains "When this creature dies, return it to the battlefield." |
| Rishkar's Expertise | 0.55 | hand | x_value | Draw cards equal to the greatest power among creatures you control. / You may cast a spell with mana value 5 or less from your hand without paying its mana cost. | Draw X cards, where X is the number of creatures you control. / If {condition}, you may cast this spell without paying its mana cost. |
| Garruk's Packleader | 0.56 | may you_control |  | Whenever another creature you control with power 3 or greater enters, you may draw a card. | Whenever another creature enters, draw a card. |
| Yedora, Grave Gardener | 0.56 | creature flip land may you_control | graveyard | Whenever another nontoken creature you control dies, you may return it to the battlefield face down under its owner's control. It's a Forest land. (It has no other types or abilities.) | Whenever another {filter} dies, return that card from your graveyard to the battlefield. |
| Flow of Knowledge | 0.59 | each_all | x_value | Draw a card for each Island you control, then discard two cards. | Draw X cards, where X is the number of Islands you control. / Then discard two cards. |
| Morbid Opportunist | 0.59 | each_all |  | Whenever one or more other creatures die, draw a card. This ability triggers only once each turn. | Whenever another creature dies, draw a card. |
| Corrupt | 0.60 |  | eot x_value | Corrupt deals damage to any target equal to the number of Swamps you control. You gain life equal to the damage dealt this way. | This spell deals X damage to any target, where X is the number of Swamps you control. / You gain life equal to the total damage dealt by this spell this turn. |
| Garruk's Uprising | 0.60 |  |  | When Garruk's Uprising enters, if you control a creature with power 4 or greater, draw a card. / Creatures you control have trample. (They can deal excess combat damage to the player or planeswalker they're attacking.) / Whenever a creature you control with power 4 or greater enters, draw a card. | When this enchantment enters, draw a card. / Creatures you control have trample. / Whenever {filter} enters, {effect}. |
| Thraben Inspector | 0.61 |  | token | When Thraben Inspector enters, investigate. (Create a Clue token. It's an artifact with "{2}, Sacrifice this token: Draw a card.") | When this creature enters, create {token}. |
| Reckless Fireweaver | 0.61 | each_all opponent you_control | creature | Whenever an artifact you control enters, Reckless Fireweaver deals 1 damage to each opponent. | Whenever another creature enters, this creature deals 1 damage to {target}. |
| Serum Visions | 0.61 |  |  | Draw a card. Scry 2. | Draw a card. / Scry N. |
| Desecrate Reality | 0.61 | cast each_all mana return up_to |  | For each opponent, exile up to one target permanent that player controls with an even mana value. (Zero is even.) / Adamant — If at least three colorless mana was spent to cast this spell, return a permanent card with an odd mana value from your graveyard to the battlefield. | Exile target permanent an opponent controls. / Put a card from a graveyard onto the battlefield. |
| Syr Konrad, the Grim | 0.62 | battlefield each_all graveyard mill opponent |  | Whenever another creature dies, or a creature card is put into a graveyard from anywhere other than the battlefield, or a creature card leaves your graveyard, Syr Konrad, the Grim deals 1 damage to each opponent. / {1}{B}: Each player mills a card. | {Trigger}, this creature deals 1 damage to {target}. / Whenever another creature dies, {effect}. / {Trigger}, {effect}. / {cost}: {effect}. |
| Volley Veteran | 0.62 |  | x_value | When Volley Veteran enters, it deals damage to target creature an opponent controls equal to the number of Goblins you control. | When this creature enters, it deals X damage to target creature an opponent controls, where X is the number of Goblins you control. |

## Highest 5 cards

| Card | sim | real text | reader text |
|---|---|---|---|
| Raise the Alarm | 1.00 | Create two 1/1 white Soldier creature tokens. | Create two 1/1 white Soldier creature tokens. |
| Herald of the Host | 1.00 | Flying, vigilance / Myriad (Whenever this creature attacks, for each opponent other than defending player, you may create a token copy that's tapped and attacking that player or a planeswalker they control. Exile the tokens at end of combat.) | Flying / Vigilance / Myriad |
| Bladebrand | 1.00 | Target creature gains deathtouch until end of turn. / Draw a card. | Target creature gains deathtouch until end of turn. / Draw a card. |
| Benalish Marshal | 1.00 | Other creatures you control get +1/+1. | Other creatures you control get +1/+1. |
| Revitalize | 1.00 | You gain 3 life. / Draw a card. | You gain 3 life. / Draw a card. |

## Known limits

- Mana-cost amounts, power/toughness and flavour are not tags; they are excluded, not scored as gaps.
- Concept and number matching are regex based; a rephrased but equal ability can score low. Read the lowest-25 table, not only the number.
- A reader that knows the real card from the tags (famous cards) inflates the score; see `recognised`.
- Similarity bands have not been checked against human judgement yet.

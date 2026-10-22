# Reverse check of the tags (blind reader)

Run `r3`. A blind reader saw only each card's tags and wrote the ability text they describe; that text was scored against the real Oracle text. Tool: `deckgen/tagcheck/reverse_check.py`. Similarity = 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1 (bands: good >= 0.7, partial 0.4-0.7, gap < 0.4; thresholds are unvalidated until a reader run is compared with a hand check). Mana-cost symbols are removed from both texts (costs are not tags).

## Summary

| cards | with text | mean similarity | good | partial | gap | source card ranked #1 | in top 5 | median rank |
|---|---|---|---|---|---|---|---|---|
| 353 | 348 | 0.871 | 306 | 40 | 2 | 262 | 325 | 1 |

Reader integrity: 0 outputs contain the card name (should be 0); 0 cards the reader says it recognised (a high rate weakens the test).

## What the tags failed to carry (concepts in the real text, absent from the reconstruction)

| concept | cards | share |
|---|---|---|
| each_all | 33 | 9% |
| you_control | 33 | 9% |
| opponent | 30 | 8% |
| may | 29 | 8% |
| creature | 17 | 4% |
| hand | 14 | 4% |
| eot | 12 | 3% |
| mana | 9 | 2% |
| reveal | 7 | 2% |
| battlefield | 6 | 1% |
| graveyard | 6 | 1% |
| tapped | 6 | 1% |
| instead | 6 | 1% |
| cast | 6 | 1% |
| land | 6 | 1% |
| attack | 5 | 1% |
| tap | 5 | 1% |
| choose | 5 | 1% |
| legend | 4 | 1% |
| sacrifice | 4 | 1% |
| counters | 3 | 0% |
| library | 3 | 0% |
| kw:landfall | 3 | 0% |
| kw:flying | 3 | 0% |
| cost_pay | 3 | 0% |

## What the reader added that the real text lacks (tags that over-claim or mislead)

| concept | cards |
|---|---|
| x_value | 16 |
| opponent | 7 |
| creature | 6 |
| eot | 3 |
| dies | 2 |
| return | 2 |
| battlefield | 2 |
| cost_pay | 2 |
| graveyard | 2 |
| token | 2 |
| you_control | 1 |
| each_all | 1 |

## Tags the reader could not read (by family)

trigger 11, cost 5, recursion 3, trigger_scope 3, mill 3, forge_line 3, cost_reduce 3, remove 2, enters_untapped 2, landtype 2, activation_restriction 2, trigger filter type not given 2, target_type 2, color 2, affected_type 2, tutor_dest 2, self_mill 2, scry 2, reanimate 1, replacement 1, replace_event 1, replace_with 1, c2 effect missing 1, tutor_target 1, trigger_filter 1, c1 duplicate of c2 trigger 1, c1.4 remove 1, cast_free 1, life_loss 1, pump_single 1

Most common single tags: cost:mana 4, trigger_scope:other 3, mill 3, trigger:attacks 3, cost_reduce 3, enters_untapped 2, recursion 2, activation_restriction 2, trigger filter type not given 2, forge_line:etbreplacement 2, tutor_dest:library 2, self_mill 2, trigger:dies 2, trigger:etb 2, scry 2, recursion:return_self 1, reanimate 1, remove:tuck 1, trigger:tap 1, landtype:island 1, replacement 1, replace_event:moved 1, replace_with:tap 1, c2 effect missing 1, tutor_target: 1, trigger_filter:card 1, c1 duplicate of c2 trigger 1, target_type:card 1, c1.4 remove:bounce duplicate 1, remove:tuck position not given 1

## Lowest 25 cards

| Card | sim | missing concepts | extra concepts | real text | reader text |
|---|---|---|---|---|---|
| Leafkin Druid | 0.29 | creature instead you_control | x_value | {T}: Add {G}. If you control four or more creatures, add {G}{G} instead. | {T}: Add {G} X times. |
| Sea Gate Loremaster | 0.38 | each_all | x_value | {T}: Draw a card for each Ally you control. | {T}: Draw X cards, where X is the number of Allies you control. |
| Welcoming Vampire | 0.43 | each_all you_control |  | Flying / Whenever one or more other creatures you control with power 2 or less enter, draw a card. This ability triggers only once each turn. | Flying / Whenever another creature enters, draw a card. |
| Elite Scaleguard | 0.44 | counters opponent tap you_control |  | When Elite Scaleguard enters, bolster 2. (Choose a creature with the least toughness among creatures you control and put two +1/+1 counters on it.) / Whenever a creature you control with a +1/+1 counter on it attacks, tap target creature defending player controls. | When this creature enters, {effect}. / Whenever this creature attacks, {effect} target creature. |
| Mentor of the Meek | 0.45 | cost_pay creature may you_control |  | Whenever another creature you control with power 2 or less enters, you may pay {1}. If you do, draw a card. | Whenever another {type} enters, draw a card. |
| Flow of Knowledge | 0.45 | each_all you_control | x_value | Draw a card for each Island you control, then discard two cards. | Draw X cards, then discard two cards. |
| Mindcrank | 0.48 | lifeloss opponent trigger_when |  | Whenever an opponent loses life, that player mills that many cards. (Damage dealt by sources without infect causes loss of life.) | Mill N cards. |
| Garruk's Packleader | 0.49 | creature may you_control |  | Whenever another creature you control with power 3 or greater enters, you may draw a card. | Whenever another {filter} enters, draw a card. |
| Explore | 0.49 | eot land may |  | You may play an additional land this turn. / Draw a card. | Draw a card. |
| Saruman the White | 0.50 | each_all | token | Ward {2} / Whenever you cast your second spell each turn, amass Orcs 2. (Put two +1/+1 counters on an Army you control. It's also an Orc. If you don't control an Army, create a 0/0 black Orc Army creature token first.) | Ward {2} / Whenever you cast a spell, create {token}. |
| Rishkar's Expertise | 0.50 | creature hand you_control | x_value | Draw cards equal to the greatest power among creatures you control. / You may cast a spell with mana value 5 or less from your hand without paying its mana cost. | Draw X cards. / You may cast this spell without paying its mana cost. |
| Ripples of Potential | 0.51 | choose counters you_control |  | Proliferate, then choose any number of permanents you control that had a counter put on them this way. Those permanents phase out. (To proliferate, choose any number of permanents and/or players, then give each another counter of each kind already there. Treat phased-out permanents and anything atta | Proliferate. |
| Cloud Key | 0.52 | battlefield choose creature enchant |  | As Cloud Key enters, choose artifact, creature, enchantment, instant, or sorcery. / Spells you cast of the chosen type cost {1} less to cast. | {Enters-the-battlefield replacement effect}. / {Spells} cost {N} less to cast. |
| Feed the Swarm | 0.53 | mana | x_value | Destroy target creature or enchantment an opponent controls. You lose life equal to that permanent's mana value. | Destroy target creature an opponent controls or target enchantment. / {player} loses X life. |
| Vines of Vastwood | 0.53 | opponent | x_value | Kicker {G} (You may pay an additional {G} as you cast this spell.) / Target creature can't be the target of spells or abilities your opponents control this turn. If this spell was kicked, that creature gets +4/+4 until end of turn. | Kicker {G} / Target creature gets +X/+X until end of turn, where X is 4 if this spell was kicked and 0 otherwise. |
| Colossal Majesty | 0.54 | creature you_control |  | At the beginning of your upkeep, if you control a creature with power 4 or greater, draw a card. | At the beginning of your upkeep, draw a card. |
| Feign Death | 0.54 | counters eot tapped |  | Until end of turn, target creature gains "When this creature dies, return it to the battlefield tapped under its owner's control with a +1/+1 counter on it." | Target creature gains "When this creature dies, return it to the battlefield." |
| Swords to Plowshares | 0.56 |  | x_value | Exile target creature. Its controller gains life equal to its power. | Exile target creature. / {Player} gains X life. |
| Thraben Inspector | 0.58 |  | token | When Thraben Inspector enters, investigate. (Create a Clue token. It's an artifact with "{2}, Sacrifice this token: Draw a card.") | When this creature enters, create {token}. |
| Kami of Whispered Hopes | 0.58 | x_value you_control | each_all | If one or more +1/+1 counters would be put on a permanent you control, that many plus one +1/+1 counters are put on that permanent instead. / {T}: Add X mana of any one color, where X is Kami of Whispered Hopes's power. | If one or more counters would be put on {object}, that many plus one of each of those counters are put on it instead. / {T}: Add Y mana of any color. |
| Garruk's Uprising | 0.59 |  |  | When Garruk's Uprising enters, if you control a creature with power 4 or greater, draw a card. / Creatures you control have trample. (They can deal excess combat damage to the player or planeswalker they're attacking.) / Whenever a creature you control with power 4 or greater enters, draw a card. | When this permanent enters, draw a card. / Creatures you control have trample. / Whenever another {filter} enters, {effect}. |
| Morbid Opportunist | 0.59 | each_all |  | Whenever one or more other creatures die, draw a card. This ability triggers only once each turn. | Whenever another creature dies, you draw a card. |
| Creeping Bloodsucker | 0.60 | each_all opponent | x_value | At the beginning of your upkeep, Creeping Bloodsucker deals 1 damage to each opponent. You gain life equal to the damage dealt this way. | At the beginning of your upkeep, this creature deals 1 damage to {target}. / You gain X life, where X is {remembered number}. |
| Corrupt | 0.60 |  | eot x_value | Corrupt deals damage to any target equal to the number of Swamps you control. You gain life equal to the damage dealt this way. | This spell deals X damage to any target, where X is the number of Swamps you control. / You gain life equal to the total damage dealt by this spell this turn. |
| Yedora, Grave Gardener | 0.61 | flip land may you_control | graveyard | Whenever another nontoken creature you control dies, you may return it to the battlefield face down under its owner's control. It's a Forest land. (It has no other types or abilities.) | Whenever another creature dies, return {that card} from your graveyard to the battlefield. |

## Highest 5 cards

| Card | sim | real text | reader text |
|---|---|---|---|
| Raise the Alarm | 1.00 | Create two 1/1 white Soldier creature tokens. | Create two 1/1 white Soldier creature tokens. |
| Impulsive Pilferer | 1.00 | When Impulsive Pilferer dies, create a Treasure token. (It's an artifact with "{T}, Sacrifice this token: Add one mana of any color.") / Encore {3}{R} ({3}{R}, Exile this card from your graveyard: For each opponent, create a token copy that attacks that opponent this turn if able. They gain haste. S | Encore {3}{R} / When this creature dies, create a Treasure token. |
| Herald of the Host | 1.00 | Flying, vigilance / Myriad (Whenever this creature attacks, for each opponent other than defending player, you may create a token copy that's tapped and attacking that player or a planeswalker they control. Exile the tokens at end of combat.) | Flying / Vigilance / Myriad |
| Dusk Legion Zealot | 1.00 | When Dusk Legion Zealot enters, you draw a card and you lose 1 life. | When this creature enters, you draw a card and you lose 1 life. |
| Bladebrand | 1.00 | Target creature gains deathtouch until end of turn. / Draw a card. | Target creature gains deathtouch until end of turn. / Draw a card. |

## Known limits

- Mana-cost amounts, power/toughness and flavour are not tags; they are excluded, not scored as gaps.
- Concept and number matching are regex based; a rephrased but equal ability can score low. Read the lowest-25 table, not only the number.
- A reader that knows the real card from the tags (famous cards) inflates the score; see `recognised`.
- Similarity bands have not been checked against human judgement yet.

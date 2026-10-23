# Reverse check of the tags (blind reader)

Run `r13c3c`. A blind reader saw only each card's tags and wrote the ability text they describe; that text was scored against the real Oracle text. Tool: `deckgen/tagcheck/reverse_check.py`. Similarity = 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1 (bands: good >= 0.7, partial 0.4-0.7, gap < 0.4; thresholds are unvalidated until a reader run is compared with a hand check). Mana-cost symbols are removed from both texts (costs are not tags).

## Summary

| cards | with text | mean similarity | good | partial | gap | source card ranked #1 | in top 5 | median rank |
|---|---|---|---|---|---|---|---|---|
| 353 | 348 | 0.921 | 328 | 19 | 1 | 308 | 338 | 1 |

Reader integrity: 0 outputs contain the card name (should be 0); 0 cards the reader says it recognised (a high rate weakens the test).

## What the tags failed to carry (concepts in the real text, absent from the reconstruction)

| concept | cards | share |
|---|---|---|
| creature | 18 | 5% |
| opponent | 15 | 4% |
| may | 13 | 3% |
| cast | 10 | 2% |
| you_control | 10 | 2% |
| each_all | 9 | 2% |
| mana | 9 | 2% |
| eot | 9 | 2% |
| reveal | 9 | 2% |
| hand | 6 | 1% |
| graveyard | 5 | 1% |
| instead | 5 | 1% |
| tap | 5 | 1% |
| battlefield | 4 | 1% |
| land | 4 | 1% |
| sacrifice | 4 | 1% |
| attack | 3 | 0% |
| library | 3 | 0% |
| kw:landfall | 3 | 0% |
| kw:flying | 3 | 0% |
| cost_pay | 3 | 0% |
| choose | 3 | 0% |
| legend | 3 | 0% |
| tapped | 3 | 0% |
| damage | 1 | 0% |

## What the reader added that the real text lacks (tags that over-claim or mislead)

| concept | cards |
|---|---|
| x_value | 7 |
| creature | 6 |
| you_control | 3 |
| each_all | 3 |
| dies | 2 |
| eot | 2 |
| token | 2 |
| return | 1 |
| counters | 1 |
| search | 1 |
| shuffle | 1 |
| target | 1 |

## Tags the reader could not read (by family)

trigger 14, trigger_filter 8, color 7, cost 6, scry 5, remove 4, restrict_kind 3, trigger_filter type missing 3, scales 3, damage target not given 3, x_is 3, attack_tax 2, forge_line 2, grant_kw 2, condition 2, tutor_target 2, target_type 2, mill 2, num 2, tutor_dest 2, duration 2, self_mill count not given 2, trigger type not given 2, token_make (no token details) 2, mana_restriction 1, trigger_filter (no type tag) 1, put_onto_battlefield (no card type or filter tag) 1, damage target (no target tag) 1, mill amount 1, trigger_zone 1

Most common single tags: scry 5, trigger_filter type missing 3, trigger_filter:you_control 3, damage target not given 3, attack_tax 2, restrict_kind:cant_attack_unless_cost 2, forge_line:alternateadditionalcost 2, cost:discard 2, cost:mana 2, mill 2, color:red 2, trigger:combat_damage 2, trigger_filter:you_control (no type given) 2, tutor_dest:library 2, self_mill count not given 2, trigger type not given 2, color:green 2, token_make (no token details) 2, mana_restriction:static_foretelling_or_instant_or_sorcery 1, trigger_filter:you_control (no type tag) 1, trigger_filter (no type tag) 1, remove:tuck 1, remove:bounce (groups c1.2, c1.4, c1.5 unclear how they combine) 1, put_onto_battlefield (no card type or filter tag) 1, trigger:end_step 1, damage target (no target tag) 1, mill amount 1, trigger_zone:graveyard 1, c3 group (target_scope:each_opponent trigger_scope:other, no payload) 1, trigger type filter 1

## Lowest 25 cards

| Card | sim | missing concepts | extra concepts | real text | reader text |
|---|---|---|---|---|---|
| Propaganda | 0.00 | attack creature each_all |  | Creatures can't attack you unless their controller pays {2} for each creature they control that's attacking you. | {restriction} |
| Rishkar's Expertise | 0.43 | cast hand mana | x_value | Draw cards equal to the greatest power among creatures you control. / You may cast a spell with mana value 5 or less from your hand without paying its mana cost. | You may draw X cards, where X is the greatest power among creatures you control. / {effect} |
| Vines of Vastwood | 0.44 | opponent | x_value | Kicker {G} (You may pay an additional {G} as you cast this spell.) / Target creature can't be the target of spells or abilities your opponents control this turn. If this spell was kicked, that creature gets +4/+4 until end of turn. | Kicker {cost} / Target creature gets +X/+X until end of turn. |
| Glimmer of Genius | 0.55 |  | counters | Scry 2, then draw two cards. You get {E}{E} (two energy counters). | Draw two cards. / You get two energy counters. / Scry N. |
| Corrupt | 0.55 |  | eot x_value | Corrupt deals damage to any target equal to the number of Swamps you control. You gain life equal to the damage dealt this way. | ~ deals X damage to any target, where X is the number of Swamps you control. / You gain X life, where X is the total damage dealt this turn. |
| Thraben Inspector | 0.60 |  | token | When Thraben Inspector enters, investigate. (Create a Clue token. It's an artifact with "{2}, Sacrifice this token: Draw a card.") | When ~ enters, create {effect}. |
| Serum Visions | 0.61 |  |  | Draw a card. Scry 2. | Draw a card. / Scry N. |
| Feed the Swarm | 0.61 |  | x_value | Destroy target creature or enchantment an opponent controls. You lose life equal to that permanent's mana value. | Destroy target creature an opponent controls or target enchantment. / Its controller loses X life, where X is its mana value. |
| Desecrate Reality | 0.63 | cast each_all mana up_to |  | For each opponent, exile up to one target permanent that player controls with an even mana value. (Zero is even.) / Adamant — If at least three colorless mana was spent to cast this spell, return a permanent card with an odd mana value from your graveyard to the battlefield. | If {condition}, exile target permanent an opponent controls. / Put a card from a graveyard onto the battlefield under your control. |
| Serum Visionary | 0.63 |  |  | When Serum Visionary enters, draw a card, then scry 2. | When ~ enters, draw a card. / Scry N. |
| Saruman the White | 0.63 |  | token | Ward {2} / Whenever you cast your second spell each turn, amass Orcs 2. (Put two +1/+1 counters on an Army you control. It's also an Orc. If you don't control an Army, create a 0/0 black Orc Army creature token first.) | Ward {2} / Whenever you cast your second spell each turn, create {effect}. |
| Ripples of Potential | 0.64 | choose counters you_control |  | Proliferate, then choose any number of permanents you control that had a counter put on them this way. Those permanents phase out. (To proliferate, choose any number of permanents and/or players, then give each another counter of each kind already there. Treat phased-out permanents and anything atta | Proliferate. / {filter} phase out. |
| Rimewind Cryomancer | 0.65 | you_control |  | {1}, {T}: Counter target activated ability. Activate only if you control four or more snow permanents. (Mana abilities can't be targeted.) | {cost}, {T}: Counter target spell. / {restriction}. |
| Daretti, Rocketeer Engineer | 0.67 | choose mana may sacrifice you_control |  | Daretti's power is equal to the greatest mana value among artifacts you control. / Whenever Daretti enters or attacks, choose target artifact card in your graveyard. You may sacrifice an artifact. If you do, return the chosen card to the battlefield. | When ~ enters, put target artifact card from your graveyard onto the battlefield under your control. / Whenever ~ attacks, {effect}. |
| Reliquary Tower | 0.68 | hand |  | You have no maximum hand size. / {T}: Add {C}. | {T}: Add {C}. |
| Welcoming Vampire | 0.68 | creature you_control |  | Flying / Whenever one or more other creatures you control with power 2 or less enter, draw a card. This ability triggers only once each turn. | Flying / Whenever one or more other {filter} enter, draw a card. / This ability triggers only once each turn. |
| Etched Oracle | 0.68 |  |  | Sunburst (This enters with a +1/+1 counter on it for each color of mana spent to cast it.) / {1}, Remove four +1/+1 counters from Etched Oracle: Target player draws three cards. | Sunburst / {cost}, Remove N counters from ~: Target player draws three cards. |
| Hunted Wumpus | 0.69 | creature each_all may opponent |  | When Hunted Wumpus enters, each other player may put a creature card from their hand onto the battlefield. | When ~ enters, put a {filter} card from your hand onto the battlefield under your control. |
| Sheltering Light | 0.69 |  |  | Target creature gains indestructible until end of turn. Scry 1. (Damage and effects that say "destroy" don't destroy the creature.) | Target creature gains indestructible until end of turn. / Scry N. |
| Search for Tomorrow | 0.70 |  |  | Search your library for a basic land card, put it onto the battlefield, then shuffle. / Suspend 2—{G} (Rather than cast this card from your hand, you may pay {G} and exile it with two time counters on it. At the beginning of your upkeep, remove a time counter. When the last is removed, you may cast  | Suspend N-{cost} / Search your library for a basic land card, put it onto the battlefield under your control, then shuffle. |
| Return of the Wildspeaker | 0.71 |  | each_all x_value | Choose one — / • Draw cards equal to the greatest power among non-Human creatures you control. / • Non-Human creatures you control get +3/+3 until end of turn. | Choose one — • Draw X cards, where X is the greatest power among nonhuman creatures you control. / • All nonhuman creatures you control get +3/+3 until end of turn. |
| Creeping Bloodsucker | 0.71 |  | x_value | At the beginning of your upkeep, Creeping Bloodsucker deals 1 damage to each opponent. You gain life equal to the damage dealt this way. | At the beginning of your upkeep, ~ deals 1 damage to each opponent and you gain X life, where X is {effect}. |
| Volley Veteran | 0.71 |  |  | When Volley Veteran enters, it deals damage to target creature an opponent controls equal to the number of Goblins you control. | When ~ enters, it deals 1 damage to target creature an opponent controls for each Goblin you control. |
| Squee, Dubious Monarch | 0.71 | cast graveyard mana may tapped |  | Haste / Whenever Squee, Dubious Monarch attacks, create a 1/1 red Goblin creature token that's tapped and attacking. / You may cast Squee, Dubious Monarch from your graveyard by paying {3}{R} and exiling four other cards from your graveyard rather than paying its mana cost. | Haste / Whenever ~ attacks, create a 1/1 red Goblin creature token. |
| Riverwise Augur | 0.72 | hand library |  | When Riverwise Augur enters, draw three cards, then put two cards from your hand on top of your library in any order. | When ~ enters, draw three cards. |

## Highest 5 cards

| Card | sim | real text | reader text |
|---|---|---|---|
| Raise the Alarm | 1.00 | Create two 1/1 white Soldier creature tokens. | Create two 1/1 white Soldier creature tokens. |
| Impulsive Pilferer | 1.00 | When Impulsive Pilferer dies, create a Treasure token. (It's an artifact with "{T}, Sacrifice this token: Add one mana of any color.") / Encore {3}{R} ({3}{R}, Exile this card from your graveyard: For each opponent, create a token copy that attacks that opponent this turn if able. They gain haste. S | Encore {3}{R}. / When ~ dies, create a Treasure token. |
| Herald of the Host | 1.00 | Flying, vigilance / Myriad (Whenever this creature attacks, for each opponent other than defending player, you may create a token copy that's tapped and attacking that player or a planeswalker they control. Exile the tokens at end of combat.) | Flying, vigilance, myriad. |
| Feign Death | 1.00 | Until end of turn, target creature gains "When this creature dies, return it to the battlefield tapped under its owner's control with a +1/+1 counter on it." | Target creature gains "When this creature dies, return it to the battlefield tapped under its owner's control with a +1/+1 counter on it" until end of turn. |
| Dusk Legion Zealot | 1.00 | When Dusk Legion Zealot enters, you draw a card and you lose 1 life. | When ~ enters, draw a card. / You lose 1 life. |

## Known limits

- Mana-cost amounts, power/toughness and flavour are not tags; they are excluded, not scored as gaps.
- Concept and number matching are regex based; a rephrased but equal ability can score low. Read the lowest-25 table, not only the number.
- A reader that knows the real card from the tags (famous cards) inflates the score; see `recognised`.
- Similarity bands have not been checked against human judgement yet.

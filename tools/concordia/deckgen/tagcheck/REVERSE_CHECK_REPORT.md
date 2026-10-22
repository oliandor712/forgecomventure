# Reverse check of the tags (blind reader)

Run `r1`. A blind reader saw only each card's tags and wrote the ability text they describe; that text was scored against the real Oracle text. Tool: `deckgen/tagcheck/reverse_check.py`. Similarity = 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1 (bands: good >= 0.7, partial 0.4-0.7, gap < 0.4; thresholds are unvalidated until a reader run is compared with a hand check). Mana-cost symbols are removed from both texts (costs are not tags).

## Summary

| cards | with text | mean similarity | good | partial | gap | source card ranked #1 | in top 5 | median rank |
|---|---|---|---|---|---|---|---|---|
| 353 | 348 | 0.773 | 232 | 95 | 21 | 223 | 293 | 1 |

Reader integrity: 0 outputs contain the card name (should be 0); 5 cards the reader says it recognised (a high rate weakens the test).

## What the tags failed to carry (concepts in the real text, absent from the reconstruction)

| concept | cards | share |
|---|---|---|
| you_control | 49 | 14% |
| each_all | 34 | 9% |
| creature | 31 | 8% |
| opponent | 29 | 8% |
| may | 29 | 8% |
| pump | 25 | 7% |
| hand | 20 | 5% |
| eot | 15 | 4% |
| reveal | 10 | 2% |
| mana | 9 | 2% |
| choose | 9 | 2% |
| graveyard | 8 | 2% |
| cast | 8 | 2% |
| library | 8 | 2% |
| land | 8 | 2% |
| block | 8 | 2% |
| battlefield | 7 | 2% |
| instead | 7 | 2% |
| x_value | 7 | 2% |
| tap | 7 | 2% |
| tapped | 6 | 1% |
| look_top | 6 | 1% |
| attack | 6 | 1% |
| return | 5 | 1% |
| counters | 4 | 1% |

## What the reader added that the real text lacks (tags that over-claim or mislead)

| concept | cards |
|---|---|
| x_value | 12 |
| creature | 7 |
| opponent | 7 |
| flip | 2 |
| search | 2 |
| you_control | 2 |
| eot | 2 |
| token | 2 |
| dies | 1 |
| graveyard | 1 |
| mill | 1 |
| return | 1 |
| battlefield | 1 |
| pump | 1 |
| each_all | 1 |

## Tags the reader could not read (by family)

tempo 94, ai_logic 21, trigger 19, burn 12, num 11, cost 11, selection 9, scales 9, trigger_filter 8, color 7, trigger_zone 7, c1 7, land_tutor 6, removal 6, artifact_token 5, trigger_scope 5, target_type 5, restrict 4, forge_line 4, landtype 4, fixing 4, pump_team 4, damage target not tagged 4, recursion 3, whose graveyard not given 3, remove 3, mana_amount 3, sacrifice_outlet 3, life_loss (amount not given) 2, damage amount not given 2

Most common single tags: tempo:+1 52, tempo:+0.5 24, burn 12, selection 9, land_tutor 6, removal 6, tempo:x 6, artifact_token 5, trigger_zone:graveyard 5, restrict 4, tempo:+1.5 4, fixing 4, tempo:+3 4, pump_team 4, damage target not tagged 4, whose graveyard not given 3, cost:mana amount not stated 3, sacrifice_outlet 3, trigger_scope:other filter not given 3, trigger_filter:card 3, tempo:+2 3, num:1 (read as the equip cost) 3, ai_logic:always 3, recursion 2, ai_logic:pump 2, life_loss (amount not given) 2, damage amount not given 2, counters_plus 2, lifegain (amount not given) 2, no groups present 2

## Lowest 25 cards

| Card | sim | missing concepts | extra concepts | real text | reader text |
|---|---|---|---|---|---|
| Benalish Marshal | 0.00 | creature pump you_control |  | Other creatures you control get +1/+1. |  |
| Control Magic | 0.00 | creature enchant |  | Enchant creature / You control enchanted creature. |  |
| Glorious Anthem | 0.00 | creature pump you_control |  | Creatures you control get +1/+1. |  |
| Laboratory Maniac | 0.00 | draw instead library |  | If you would draw a card while your library has no cards in it, you win the game instead. |  |
| Time of Ice | 0.12 | creature each_all opponent tap tapped target you_control | hand | (As this Saga enters and after your draw step, add a lore counter. Sacrifice after III.) / I, II — Tap target creature an opponent controls. It doesn't untap during its controller's untap step for as long as you control Time of Ice. / III — Return all tapped creatures to their owners' hands. | Saga with 3 chapters. / Chapter {N}: Return {permanent} to its owner's hand. |
| Lightning Mare | 0.25 | block creature pump |  | This spell can't be countered. / Lightning Mare can't be blocked by blue creatures. / {1}{R}: Lightning Mare gets +1/+0 until end of turn. | {cost}: {restriction} until end of turn. |
| Priest of Titania | 0.27 | battlefield each_all | x_value you_control | {T}: Add {G} for each Elf on the battlefield. | {T}: Add X {G}, where X is the number of Elves you control. |
| Feign Death | 0.29 | counters dies eot tapped trigger_when | flip graveyard | Until end of turn, target creature gains "When this creature dies, return it to the battlefield tapped under its owner's control with a +1/+1 counter on it." | Return target creature card from a graveyard to the battlefield, transformed. |
| Kami of Whispered Hopes | 0.29 | counters instead x_value you_control |  | If one or more +1/+1 counters would be put on a permanent you control, that many plus one +1/+1 counters are put on that permanent instead. / {T}: Add X mana of any one color, where X is Kami of Whispered Hopes's power. | {T}: Add Y mana of any color. |
| Supernatural Stamina | 0.30 | battlefield dies pump return tapped trigger_when | flip | Until end of turn, target creature gets +2/+0 and gains "When this creature dies, return it to the battlefield tapped under its owner's control." | Target creature gets {pump} until end of turn. / Transform it. |
| Militia Bugler | 0.31 | creature hand library look_top may reveal |  | Vigilance (Attacking doesn't cause this creature to tap.) / When Militia Bugler enters, look at the top four cards of your library. You may reveal a creature card with power 2 or less from among them and put it into your hand. Put the rest on the bottom of your library in a random order. | Vigilance / When this creature enters, {selection effect}. |
| Predatory Wurm | 0.34 | pump you_control |  | Vigilance (Attacking doesn't cause this creature to tap.) / Predatory Wurm gets +2/+2 as long as you control a Garruk planeswalker. | Vigilance |
| Exsanguinate | 0.34 | each_all opponent x_value |  | Each opponent loses X life. You gain life equal to the life lost this way. | {Player} loses N life. / You gain N life. |
| Fact or Fiction | 0.34 | graveyard hand look_top opponent reveal | mill search | Reveal the top five cards of your library. An opponent separates those cards into two piles. Put one pile into your hand and the other into your graveyard. | Mill N cards. / Search your library for a {type} card and put it {zone}. |
| Leafkin Druid | 0.35 | creature instead you_control | x_value | {T}: Add {G}. If you control four or more creatures, add {G}{G} instead. | {T}: Add X {G}. |
| Return of the Wildspeaker | 0.35 | choose eot | x_value | Choose one — / • Draw cards equal to the greatest power among non-Human creatures you control. / • Non-Human creatures you control get +3/+3 until end of turn. | Draw X cards. / Creatures you control that aren't Human get +N/+N. |
| Gray Merchant of Asphodel | 0.35 | each_all kw:devotion opponent x_value |  | When Gray Merchant of Asphodel enters, each opponent loses X life, where X is your devotion to black. You gain life equal to the life lost this way. (Each {B} in the mana costs of permanents you control counts toward your devotion to black.) | When this creature enters, {affected} loses N life and you gain N life. |
| Dig Through Time | 0.36 | hand library look_top |  | Delve (Each card you exile from your graveyard while casting this spell pays for {1}.) / Look at the top seven cards of your library. Put two of them into your hand and the rest on the bottom of your library in any order. | Delve / {selection effect}. |
| Consume Spirit | 0.37 | mana x_value |  | Spend only black mana on X. / Consume Spirit deals X damage to any target and you gain X life. | This spell deals N damage to any target. / You gain N life. |
| Sea Gate Loremaster | 0.38 | each_all | x_value | {T}: Draw a card for each Ally you control. | {T}: Draw X cards, where X is the number of Allies you control. |
| Welcoming Vampire | 0.39 | creature each_all you_control |  | Flying / Whenever one or more other creatures you control with power 2 or less enter, draw a card. This ability triggers only once each turn. | Flying / Whenever another {creature} enters, draw a card. |
| Tendrils of Corruption | 0.40 | x_value you_control |  | Tendrils of Corruption deals X damage to target creature and you gain X life, where X is the number of Swamps you control. | This spell deals N damage to target creature. / You gain N life. |
| Trumpet Blast | 0.42 | attack | you_control | Attacking creatures get +2/+0 until end of turn. | Creatures you control get +N/+N until end of turn. |
| Elite Scaleguard | 0.43 | counters opponent tap you_control |  | When Elite Scaleguard enters, bolster 2. (Choose a creature with the least toughness among creatures you control and put two +1/+1 counters on it.) / Whenever a creature you control with a +1/+1 counter on it attacks, tap target creature defending player controls. | When this creature enters, {effect}. / Whenever this creature attacks, {effect} target creature. |
| Heirloom Blade | 0.43 | hand library may pump reveal |  | Equipped creature gets +3/+1. / Whenever equipped creature dies, you may reveal cards from the top of your library until you reveal a creature card that shares a creature type with it. Put that card into your hand and the rest on the bottom of your library in a random order. / Equip {1} | Equip {1} / Whenever another creature dies, {effect}. / Equipped creature {effect}. |

## Highest 5 cards

| Card | sim | real text | reader text |
|---|---|---|---|
| Raise the Alarm | 1.00 | Create two 1/1 white Soldier creature tokens. | Create two 1/1 white Soldier creature tokens. |
| Herald of the Host | 1.00 | Flying, vigilance / Myriad (Whenever this creature attacks, for each opponent other than defending player, you may create a token copy that's tapped and attacking that player or a planeswalker they control. Exile the tokens at end of combat.) | Flying / Vigilance / Myriad |
| Bladebrand | 1.00 | Target creature gains deathtouch until end of turn. / Draw a card. | Target creature gains Deathtouch until end of turn. / Draw a card. |
| Lonely Sandbar | 1.00 | Lonely Sandbar enters tapped. / {T}: Add {U}. / Cycling {U} ({U}, Discard this card: Draw a card.) | This land enters tapped. / {T}: Add {U}. / Cycling {cost} |
| Skyhunter Skirmisher | 1.00 | Flying, double strike | Flying / Double strike |

## Known limits

- Mana-cost amounts, power/toughness and flavour are not tags; they are excluded, not scored as gaps.
- Concept and number matching are regex based; a rephrased but equal ability can score low. Read the lowest-25 table, not only the number.
- A reader that knows the real card from the tags (famous cards) inflates the score; see `recognised`.
- Similarity bands have not been checked against human judgement yet.

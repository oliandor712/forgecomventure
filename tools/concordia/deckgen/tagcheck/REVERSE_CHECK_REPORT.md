# Reverse check of the tags (blind reader)

Run `r5`. A blind reader saw only each card's tags and wrote the ability text they describe; that text was scored against the real Oracle text. Tool: `deckgen/tagcheck/reverse_check.py`. Similarity = 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1 (bands: good >= 0.7, partial 0.4-0.7, gap < 0.4; thresholds are unvalidated until a reader run is compared with a hand check). Mana-cost symbols are removed from both texts (costs are not tags).

## Summary

| cards | with text | mean similarity | good | partial | gap | source card ranked #1 | in top 5 | median rank |
|---|---|---|---|---|---|---|---|---|
| 176 | 174 | 0.885 | 156 | 17 | 1 | 144 | 169 | 1 |

Reader integrity: 0 outputs contain the card name (should be 0); 0 cards the reader says it recognised (a high rate weakens the test).

## What the tags failed to carry (concepts in the real text, absent from the reconstruction)

| concept | cards | share |
|---|---|---|
| you_control | 18 | 10% |
| may | 17 | 9% |
| opponent | 10 | 5% |
| creature | 9 | 5% |
| eot | 9 | 5% |
| each_all | 8 | 4% |
| hand | 7 | 4% |
| reveal | 6 | 3% |
| land | 5 | 2% |
| return | 4 | 2% |
| mana | 3 | 1% |
| tap | 3 | 1% |
| library | 2 | 1% |
| battlefield | 2 | 1% |
| choose | 2 | 1% |
| instead | 2 | 1% |
| kw:landfall | 2 | 1% |
| attack | 2 | 1% |
| graveyard | 2 | 1% |
| counters | 2 | 1% |
| cast | 2 | 1% |
| flip | 1 | 0% |
| kw:flying | 1 | 0% |
| legend | 1 | 0% |
| copy | 1 | 0% |

## What the reader added that the real text lacks (tags that over-claim or mislead)

| concept | cards |
|---|---|
| x_value | 4 |
| creature | 3 |
| graveyard | 2 |
| each_all | 1 |
| you_control | 1 |
| opponent | 1 |
| mana | 1 |
| return | 1 |

## Tags the reader could not read (by family)

trigger 13, trigger_scope 6, life_loss 5, cost 4, target_type 4, trigger_zone 3, cost_reduce 3, damage 3, c1 3, forge_line 2, restrict_kind 2, color 2, target_zone 2, discard 2, token_make 2, duration 2, mill 2, c2 payload (trigger 2, landtype 1, tutor_target 1, kw 1, take 1, enters_untapped 1, replace 1, token_count 1, impulse_draw 1, self_mill 1, target_filter 1, attack_tax 1, scry 1

Most common single tags: trigger_scope:other 5, life_loss 5, trigger_zone:graveyard 3, cost_reduce 3, damage 3, forge_line:etbreplacement 2, trigger:upkeep 2, cost:discard 2, trigger:end_step 2, trigger:etb 2, target_zone:graveyard 2, discard 2, cost:mana 2, trigger:attacks 2, target_type:creature 2, token_make 2, mill 2, c1:affected 2, c2 payload (trigger:dies has no effect tags) 2, landtype:forest 1, trigger:dies 1, tutor_target: 1, restrict_kind:doesnt_untap 1, kw:kicker 1, take:all_goblin_to_hand 1, target_type:card 1, color:white 1, color:green 1, enters_untapped 1, target_type:permanent 1

## Lowest 25 cards

| Card | sim | missing concepts | extra concepts | real text | reader text |
|---|---|---|---|---|---|
| Rishkar's Expertise | 0.27 | cast hand mana may | x_value | Draw cards equal to the greatest power among creatures you control. / You may cast a spell with mana value 5 or less from your hand without paying its mana cost. | Draw X cards, where X is the number of creatures you control. |
| Welcoming Vampire | 0.42 | each_all you_control |  | Flying / Whenever one or more other creatures you control with power 2 or less enter, draw a card. This ability triggers only once each turn. | Flying / Whenever another creature enters, you draw a card. |
| Elite Scaleguard | 0.44 | counters opponent tap you_control |  | When Elite Scaleguard enters, bolster 2. (Choose a creature with the least toughness among creatures you control and put two +1/+1 counters on it.) / Whenever a creature you control with a +1/+1 counter on it attacks, tap target creature defending player controls. | When this creature enters, (effect not given by tags). / Whenever this creature attacks, (effect not given by tags) target creature. |
| Mindcrank | 0.48 | lifeloss opponent trigger_when |  | Whenever an opponent loses life, that player mills that many cards. (Damage dealt by sources without infect causes loss of life.) | Mill N cards. |
| Feign Death | 0.49 | counters eot tapped | graveyard | Until end of turn, target creature gains "When this creature dies, return it to the battlefield tapped under its owner's control with a +1/+1 counter on it." | Return target creature card from your graveyard to the battlefield. / It gains "When this creature dies, (effect not given by tags)." |
| Explore | 0.50 | eot land may |  | You may play an additional land this turn. / Draw a card. | Draw a card. |
| Mentor of the Meek | 0.51 | cost_pay may you_control |  | Whenever another creature you control with power 2 or less enters, you may pay {1}. If you do, draw a card. | Whenever another creature enters, you draw a card. |
| Colossal Majesty | 0.53 | creature you_control |  | At the beginning of your upkeep, if you control a creature with power 4 or greater, draw a card. | At the beginning of your upkeep, draw a card. |
| Garruk's Packleader | 0.53 | may you_control |  | Whenever another creature you control with power 3 or greater enters, you may draw a card. | Whenever another creature enters the battlefield, you draw a card. |
| Cloud Key | 0.54 | choose creature enchant |  | As Cloud Key enters, choose artifact, creature, enchantment, instant, or sorcery. / Spells you cast of the chosen type cost {1} less to cast. | [Unspecified enters-the-battlefield replacement effect.] / Spells cost {N} less to cast. |
| Yedora, Grave Gardener | 0.56 | flip land may return you_control | graveyard | Whenever another nontoken creature you control dies, you may return it to the battlefield face down under its owner's control. It's a Forest land. (It has no other types or abilities.) | Whenever another creature dies, put it onto the battlefield from the graveyard. |
| Storm-Kiln Artist | 0.63 | copy each_all | x_value | Storm-Kiln Artist gets +1/+0 for each artifact you control. / Magecraft — Whenever you cast or copy an instant or sorcery spell, create a Treasure token. | This creature gets +X/+0, where X is the number of artifacts you control. / Whenever you cast an instant or sorcery spell, create a Treasure token. |
| Volley Veteran | 0.68 |  | x_value | When Volley Veteran enters, it deals damage to target creature an opponent controls equal to the number of Goblins you control. | When this creature enters, it deals X damage to target creature an opponent controls, where X is the number of Goblins you control. |
| Elvish Regrower | 0.69 | hand return |  | When this creature enters, return target permanent card from your graveyard to your hand. | When this creature enters, [unspecified effect] target permanent card in your graveyard. |
| Syr Konrad, the Grim | 0.69 | battlefield each_all graveyard opponent |  | Whenever another creature dies, or a creature card is put into a graveyard from anywhere other than the battlefield, or a creature card leaves your graveyard, Syr Konrad, the Grim deals 1 damage to each opponent. / {1}{B}: Each player mills a card. | Whenever another creature dies, this creature deals 1 damage. / {cost}: Mill N cards. |
| Incinerate | 0.69 | creature eot |  | Incinerate deals 3 damage to any target. A creature dealt damage this way can't be regenerated this turn. | This spell deals 3 damage to any target. |
| Dutiful Attendant | 0.69 | hand return |  | When Dutiful Attendant dies, return another target creature card from your graveyard to your hand. | When this creature dies, [unspecified effect] another target creature card in a graveyard. |
| Reliquary Tower | 0.70 | hand |  | You have no maximum hand size. / {T}: Add {C}. | {T}: Add {C}. |
| Vodalian Arcanist | 0.70 | cast |  | {T}: Add {C}. Spend this mana only to cast an instant or sorcery spell. | {T}: Add {C}. / Spend this mana only [restriction not given]. |
| Heirloom Blade | 0.71 | hand library may reveal |  | Equipped creature gets +3/+1. / Whenever equipped creature dies, you may reveal cards from the top of your library until you reveal a creature card that shares a creature type with it. Put that card into your hand and the rest on the bottom of your library in a random order. / Equip {1} | Equipped creature gets +3/+1. / Whenever another creature dies, {effect}. / Equip {1} |
| Sheltering Light | 0.71 |  |  | Target creature gains indestructible until end of turn. Scry 1. (Damage and effects that say "destroy" don't destroy the creature.) | Target creature gains indestructible until end of turn. / Scry N. |
| Gadwick, the Wizened | 0.72 | tap | mana | When Gadwick, the Wizened enters, draw X cards. / Whenever you cast a blue spell, tap target nonland permanent an opponent controls. | When this creature enters, draw X cards, where X is the amount of mana paid for X. / Whenever you cast a blue spell, (effect not given by tags) target nonland permanent an opponent controls. |
| Zulaport Cutthroat | 0.72 | creature each_all opponent you_control |  | Whenever Zulaport Cutthroat or another creature you control dies, each opponent loses 1 life and you gain 1 life. | When this creature dies, you gain 1 life and lose 1 life. |
| Riverwise Augur | 0.73 | hand library |  | When Riverwise Augur enters, draw three cards, then put two cards from your hand on top of your library in any order. | When this creature enters, draw three cards. |
| Haliya, Guided by Light | 0.73 | creature eot you_control |  | Whenever Haliya or another creature or artifact you control enters, you gain 1 life. / At the beginning of your end step, draw a card if you've gained 3 or more life this turn. / Warp {W} (You may cast this card from your hand for its warp cost. Exile this creature at the beginning of the next end s | Warp {cost} / When this creature enters, you gain 1 life. / At the beginning of your end step, draw a card. |

## Highest 5 cards

| Card | sim | real text | reader text |
|---|---|---|---|
| Rhox Pikemaster | 1.00 | First strike (This creature deals combat damage before creatures without first strike.) / Other Soldier creatures you control have first strike. | First strike / Other Soldier creatures you control have first strike. |
| Sungrace Pegasus | 1.00 | Flying (This creature can't be blocked except by creatures with flying or reach.) / Lifelink (Damage dealt by this creature also causes you to gain that much life.) | Flying / Lifelink |
| Professor of Zoomancy | 1.00 | When Professor of Zoomancy enters, create a 1/1 black and green Pest creature token with "When this token dies, you gain 1 life." | When this creature enters, create a 1/1 black and green Pest creature token with "When this token dies, you gain 1 life." |
| Swiftfoot Boots | 1.00 | Equipped creature has hexproof and haste. / Equip {1} | Equipped creature has haste and hexproof. / Equip {1} |
| Deadly Recluse | 1.00 | Reach (This creature can block creatures with flying.) / Deathtouch (Any amount of damage this deals to a creature is enough to destroy it.) | Reach / Deathtouch |

## Known limits

- Mana-cost amounts, power/toughness and flavour are not tags; they are excluded, not scored as gaps.
- Concept and number matching are regex based; a rephrased but equal ability can score low. Read the lowest-25 table, not only the number.
- A reader that knows the real card from the tags (famous cards) inflates the score; see `recognised`.
- Similarity bands have not been checked against human judgement yet.

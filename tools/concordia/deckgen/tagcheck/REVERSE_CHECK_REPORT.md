# Reverse check of the tags (blind reader)

Run `g27c`. A blind reader saw only each card's tags and wrote the ability text they describe; that text was scored against the real Oracle text. Tool: `deckgen/tagcheck/reverse_check.py`. Similarity = 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1 (bands: good >= 0.7, partial 0.4-0.7, gap < 0.4; thresholds are unvalidated until a reader run is compared with a hand check). Mana-cost symbols are removed from both texts (costs are not tags).

## Summary

| cards | with text | mean similarity | good | partial | gap | source card ranked #1 | in top 5 | median rank |
|---|---|---|---|---|---|---|---|---|
| 72 | 72 | 0.725 | 45 | 25 | 2 | 72 | 72 | 1 |

Reader integrity: 0 outputs contain the card name (should be 0); 0 cards the reader says it recognised (a high rate weakens the test).

## What the tags failed to carry (concepts in the real text, absent from the reconstruction)

| concept | cards | share |
|---|---|---|
| each_all | 19 | 26% |
| opponent | 18 | 25% |
| trigger_phase | 13 | 18% |
| you_control | 12 | 16% |
| damage | 12 | 16% |
| cast | 11 | 15% |
| eot | 10 | 13% |
| may | 10 | 13% |
| exile | 9 | 12% |
| instead | 9 | 12% |
| creature | 9 | 12% |
| mana | 9 | 12% |
| graveyard | 8 | 11% |
| sacrifice | 8 | 11% |
| counters | 7 | 9% |
| trigger_when | 6 | 8% |
| target | 5 | 6% |
| hand | 4 | 5% |
| cost_pay | 4 | 5% |
| attack | 4 | 5% |
| battlefield | 3 | 4% |
| flip | 3 | 4% |
| block | 3 | 4% |
| surveil | 3 | 4% |
| token | 3 | 4% |

## What the reader added that the real text lacks (tags that over-claim or mislead)

| concept | cards |
|---|---|
| x_value | 9 |
| target | 3 |
| return | 2 |
| look_top | 2 |
| creature | 2 |
| control | 1 |
| opponent | 1 |
| cost_pay | 1 |
| each_all | 1 |
| you_control | 1 |
| eot | 1 |
| counters | 1 |
| battlefield | 1 |

## Tags the reader could not read (by family)

x 15, token_type 8, exile 7, scales 6, trigger 5, c2 trigger 5, cost 4, c1 3, c1.6 3, kw 3, grant_ability 3, c2 3, activation_restriction 3, modal 3, c1 trigger 3, life_loss 2, c1.5 2, replace 2, steal 2, sacrifice 2, draw 2, c2 trigger and cost 2, untap 2, s3 2, c2.2 2, c3 trigger 2, c1 effect 2, c3 1, clone 1, c2 cost placement 1

Most common single tags: exile 7, c2 trigger 5, c1.6 3, scales:counters 3, kw:class costs 3, trigger:end_step 3, c2 3, activation_restriction 3, c1 trigger 3, c1 2, life_loss 2, c1.5 2, steal 2, sacrifice 2, draw 2, x: life_loss trigger:end_step 2, grant_ability:other 2, c2 trigger and cost 2, x: trigger:end_step 2, untap 2, s3 2, cost:exile 2, c2.2 2, cost:remove_counters 2, x: damage 2, c3 trigger 2, c1 effect 2, c1: haste 1, token_type:pilot_crewbuff 1, scales:creature_you_control_vehicle 1

## Lowest 25 cards

| Card | sim | missing concepts | extra concepts | real text | reader text |
|---|---|---|---|---|---|
| Pia Nalaar, Chief Mechanic | 0.24 | cost_pay creature damage kw:flying may opponent trigger_phase x_value you_control | counters | Whenever one or more artifact creatures you control deal combat damage to a player, you get {E}{E} (two energy counters). / At the beginning of your end step, you may pay one or more {E}. If you do, create an X/X colorless Vehicle artifact token named Nalaar Aetherjet with flying and crew 2, where X | Whenever one or more {things} {trigger}, you get two energy counters. / {Unless you pay a cost}, create a red Aetherjet token. / {end step} |
| Goblin Kaboomist | 0.30 | attack creature damage kw:flying land sacrifice target |  | At the beginning of your upkeep, create a colorless artifact token named Land Mine with "{R}, Sacrifice this artifact: This artifact deals 2 damage to target attacking creature without flying." Then flip a coin. If you lose the flip, Goblin Kaboomist deals 2 damage to itself. | At the beginning of your upkeep, create a Mine token. / {The token deals damage}. |
| Seize the Soul | 0.43 | creature destroy kw:flying target |  | Destroy target nonwhite, nonblack creature. Create a 1/1 white Spirit creature token with flying. / Haunt (When this spell card is put into a graveyard after resolving, exile it haunting target creature.) / When the creature Seize the Soul haunts dies, destroy target nonwhite, nonblack creature. Cre | Haunt / When this creature dies, {effect}: create a token. / {When the haunted creature dies, same effect}. |
| Hostility | 0.44 | creature each_all opponent token you_control | return | Haste / If a spell you control would deal damage to an opponent, prevent that damage. Create a 3/1 red Elemental Shaman creature token with haste for each 1 damage prevented this way. / When Hostility is put into a graveyard from anywhere, shuffle it into its owner's library. | Haste / If damage would be dealt, {replacement: create tokens instead}. / When this creature is put into a graveyard, return it from your graveyard to your library and shuffle. |
| Gossip's Talent | 0.45 | attack block damage eot exile may opponent surveil target you_control |  | (Gain the next level as a sorcery to add its ability.) / Whenever a creature you control enters, surveil 1. / {1}{U}: Level 2 / Whenever you attack, target attacking creature with power 3 or less can't be blocked this turn. / {3}{U}: Level 3 / Whenever a creature you control deals combat damage to a | Class level 2 ({1}{U}?): Whenever a creature enters under your control, {effect}. / Class level 3 ({cost}): {effect}. / {surveil, exile, combat damage effect} |
| Echo Mage | 0.46 | choose copy may target |  | Level up {1}{U} ({1}{U}: Put a level counter on this. Level up only as a sorcery.) / LEVEL 2-3 / 2/4 / {U}{U}, {T}: Copy target instant or sorcery spell. You may choose new targets for the copy. / LEVEL 4+ / 2/5 / {U}{U}, {T}: Copy target instant or sorcery spell twice. You may choose new targets fo | Level up {1}{U} / Level 2-3: {effect}. / Level 4+: {effect}. / {cost}, {T}: {effect}. |
| Rankle and Torbran | 0.47 | damage each_all eot instead opponent trigger_when |  | Flying, first strike, haste / Whenever Rankle and Torbran deals combat damage to a player or battle, choose any number — / • Each player creates a Treasure token. / • Each player sacrifices a creature. / • If a source would deal damage to a player or battle this turn, it deals that much damage plus  | Flying, first strike, haste / Choose three - Create a Treasure token. / Sacrifice a creature. / {third mode} {combat damage trigger} |
| Prairie Dog | 0.47 | cast creature eot hand instead trigger_phase you_control | battlefield | Lifelink / At the beginning of your end step, if you haven't cast a spell from your hand this turn, put a +1/+1 counter on Prairie Dog. / {4}{W}: Until end of turn, if you would put one or more +1/+1 counters on a creature you control, put that many plus one +1/+1 counters on it instead. | Lifelink / This creature enters with a +1/+1 counter on it. / {4}{W}: {effect at end step}. |
| Golbez, Crystal Collector | 0.49 | each_all lifeloss opponent surveil trigger_phase you_control |  | Whenever an artifact you control enters, surveil 1. / At the beginning of your end step, if you control four or more artifacts, return target creature card from your graveyard to your hand. Then if you control eight or more artifacts, each opponent loses life equal to that card's power. | Whenever an artifact enters under your control, return target creature card from your graveyard to your hand. / {That player loses life equal to that card's power}. / {surveil at end step} |
| Vault 11: Voter's Dilemma | 0.53 | destroy draw opponent reveal up_to | x_value | (As this Saga enters and after your draw step, add a lore counter. Sacrifice after III.) / I — For each opponent, you create a 1/1 white Human Soldier creature token. / II, III — Each player secretly votes for up to one creature, then those votes are revealed. If no creature got votes, each player d | I - Create X 1/1 white Human Soldier creature tokens, where X is the number of players. / II - {effect}. / III - {effect}. / {destroy} |
| Starving Revenant | 0.55 | each_all graveyard library surveil | x_value | When Starving Revenant enters, surveil 2. Then for each card you put on top of your library, you draw a card and you lose 3 life. / Descend 8 — Whenever you draw a card, if there are eight or more permanent cards in your graveyard, target opponent loses 1 life and you gain 1 life. | When this creature enters, draw X cards and lose three times X life, where X is {an amount}. / Whenever {a creature you control triggers}, target opponent loses 1 life and you gain 1 life. / {surveil} |
| Guile | 0.55 | block counter_spell counters creature exile instead mana you_control | return | Guile can't be blocked except by three or more creatures. / If a spell or ability you control would counter a spell, instead exile that spell and you may play that card without paying its mana cost. / When Guile is put into a graveyard from anywhere, shuffle it into its owner's library. | If {this would be countered}, you may {put it elsewhere instead}. / When this creature is put into a graveyard, return it from your graveyard to your library and shuffle. / {exile} |
| Emperor of Bones | 0.58 | counters creature sacrifice trigger_when | eot | At the beginning of combat on your turn, exile up to one target card from a graveyard. / {1}{B}: Adapt 2. / Whenever one or more +1/+1 counters are put on Emperor of Bones, put a creature card exiled with Emperor of Bones onto the battlefield under your control with a finality counter on it. It gain | At the beginning of combat on your turn, exile up to one target card from a graveyard. / {1}{B}: {effect}. / {One or more trigger}: put a card exiled onto the battlefield under your control; it gains haste until end of turn. / {sacrifice} |
| Grisly Sigil | 0.58 | choose eot lifegain |  | Casualty 1 (As you cast this spell, you may sacrifice a creature with power 1 or greater. When you do, copy this spell and you may choose new targets for the copy.) / Choose target creature or planeswalker. If it was dealt noncombat damage this turn, Grisly Sigil deals 3 damage to it and you gain 3  | Casualty 1 / This spell deals damage to target creature or planeswalker. / {You gain life}. |
| Bandit's Talent | 0.59 | draw hand lifeloss trigger_phase |  | (Gain the next level as a sorcery to add its ability.) / When Bandit's Talent enters, each opponent discards two cards unless they discard a nonland card. / {B}: Level 2 / At the beginning of each opponent's upkeep, if that player has one or fewer cards in hand, they lose 2 life. / {3}{B}: Level 3 / | Class level 2 ({cost}): {effect}. / Class level 3 ({cost}): {effect}. / When this Class enters, each opponent discards two cards. / {At the beginning of your upkeep, life loss and draw} |
| Shredder, Shadow Master | 0.61 | damage each_all legend opponent sacrifice tapped |  | Whenever Shredder attacks a player, for each other opponent, create a token that's a copy of Shredder tapped and attacking that player, except it isn't legendary. Sacrifice those tokens at end of combat. / Whenever Shredder deals combat damage to a player, that player loses half their life, rounded  | Whenever this creature attacks, create a token that's a copy of {a creature}. / {Target player loses life equal to half their life total, rounded up}. / {Sacrifice when combat damage} |
| Ninja Teen | 0.61 | cast graveyard kw:menace may pump |  | (Gain the next level as a sorcery to add its ability.) / Whenever a creature you control leaves the battlefield, each opponent loses 1 life. / {1}{B}: Level 2 / Creatures you control get +1/+0 and have menace. / {B}: Level 3 / Creature cards in your graveyard have sneak {3}{B}. / You may cast creatu | Class level 2 ({1}{B}): {effect}. / Class level 3 ({cost}): {effect}. / Whenever a creature you control leaves the battlefield, each opponent loses 1 life. / {cost}: life loss. |
| Ennis, Debate Moderator | 0.61 | counters eot trigger_phase |  | When Ennis enters, exile up to one other target creature you control. Return that card to the battlefield under its owner's control at the beginning of the next end step. / At the beginning of your end step, if one or more cards were put into exile this turn, put a +1/+1 counter on Ennis. | When this creature enters, exile up to one other target creature you control, then return it to the battlefield under its owner's control. / {Put a +1/+1 counter on it} {at end step}. |
| Osseous Sticktwister | 0.61 | discard graveyard may sacrifice trigger_phase |  | Lifelink / Delirium — At the beginning of your end step, if there are four or more card types among cards in your graveyard, each opponent may sacrifice a nonland permanent or discard a card. Then Osseous Sticktwister deals damage equal to its power to each opponent who didn't sacrifice a permanent  | Lifelink / Each opponent {unless they pay a cost}: this creature deals damage equal to its power to that player. / {Discard, sacrifice} |
| Return of the Mole Man | 0.63 | attack creature kw:landfall mill you_control |  | Landfall — Whenever a land you control enters, you may mill two cards. / {5}{G}, Sacrifice this enchantment: Create X 1/1 green Minion creature tokens named Moloid, where X is the number of permanent cards in your graveyard. The tokens have "Whenever this token attacks, you may mill a card." Activat | Whenever a land enters under your control, you may {mill / effect}. / {5}{G}, Sacrifice this enchantment: Create X tokens, where X is the number of permanent cards you own in your graveyard. |
| Preston Garvey, Minuteman | 0.66 | each_all enchant mana tap |  | At the beginning of combat on your turn, create a green Aura enchantment token named Settlement attached to up to one target land you control. It has enchant land and "Enchanted land has '{T}: Add one mana of any color.'" / Whenever Preston Garvey, Minuteman attacks, untap each enchanted permanent y | At the beginning of combat on your turn, up to one target land you control becomes {a creature}/creates a token. / Whenever this creature attacks, {effect on permanents you control}. / {untap} |
| Contested Game Ball | 0.69 | attack damage opponent sacrifice token | control | Whenever you're dealt combat damage, the attacking player gains control of Contested Game Ball and untaps it. / {2}, {T}: Draw a card and put a point counter on Contested Game Ball. Then if it has five or more point counters on it, sacrifice it and create a Treasure token. | Whenever one or more {things} {trigger}, gain control of {permanent} {duration}. / {2}, {T}: Draw a card and put a point counter on this artifact. / {sacrifice} |
| Karn, Legacy Reforged | 0.69 | cast eot |  | Karn, Legacy Reforged's power and toughness are each equal to the greatest mana value among artifacts you control. / At the beginning of your upkeep, add {C} for each artifact you control. This mana can't be spent to cast nonartifact spells. Until end of turn, you don't lose this mana as steps and p | At the beginning of your upkeep, add {C} for each artifact you control. / Spend this mana only on artifact spells. |
| Palantír of Orthanc | 0.69 | each_all mana may mill x_value |  | At the beginning of your end step, put an influence counter on Palantír of Orthanc and scry 2. Then target opponent may have you draw a card. If that player doesn't, you mill X cards, where X is the number of influence counters on Palantír of Orthanc, and that player loses life equal to the total ma | At the beginning of your end step, put an influence counter on this artifact, scry 2, and target opponent loses life equal to {a remembered mana value}; draw a card. |
| Goliath Daydreamer | 0.69 | counters exile graveyard hand instead |  | Whenever you cast an instant or sorcery spell from your hand, exile that card with a dream counter on it instead of putting it into your graveyard as it resolves. / Whenever this creature attacks, you may cast a spell from among cards you own in exile with dream counters on them without paying its m | Whenever you cast an instant or sorcery spell, {effect}. / Whenever this creature attacks, you may cast a spell without paying its mana cost. / {exile} |

## Highest 5 cards

| Card | sim | real text | reader text |
|---|---|---|---|
| Deathrite Shaman | 0.98 | {T}: Exile target land card from a graveyard. Add one mana of any color. / {B}, {T}: Exile target instant or sorcery card from a graveyard. Each opponent loses 2 life. / {G}, {T}: Exile target creature card from a graveyard. You gain 2 life. | {T}, exile target land card from a graveyard: Add one mana of any color. / {B}, {T}, exile target instant or sorcery card from a graveyard: Target opponent loses 2 life. / {G}, {T}, exile target creature card from a graveyard: You gain 2 life. |
| Brigid's Command | 0.97 | Choose two — / • Create a token that's a copy of target Kithkin you control. / • Target player creates a 1/1 green and white Kithkin creature token. / • Target creature you control gets +3/+3 until end of turn. / • Target creature you control fights target creature an opponent controls. | Choose two - / Create a token that's a copy of target Kithkin you control. / Target player creates a 1/1 green and white Kithkin creature token. / Target creature you control gets +3/+3 {duration}. / Target creature you control fights target creature you opponent controls. |
| Mjölnir, Storm Hammer | 0.97 | When Mjölnir enters, attach it to target legendary creature you control. / Whenever equipped creature attacks, tap target creature defending player controls and put a stun counter on it. Then Mjölnir deals damage to each opponent equal to the number of tapped creatures that opponent controls. / Equi | When this Equipment enters, attach it to target legendary creature you control. / Whenever equipped creature attacks, put a stun counter on target creature defending player controls, then this deals damage to that player equal to the number of tapped creatures they control. / Equip {4} |
| Cabaretti Charm | 0.96 | Choose one — / • Cabaretti Charm deals damage equal to the number of creatures you control to target creature or planeswalker. / • Creatures you control get +1/+1 and gain trample until end of turn. / • Create two 1/1 green and white Citizen creature tokens. | Choose one - / Target creature or planeswalker takes damage equal to the number of creatures you control. / Creatures you control get +1/+1 and gain trample until end of turn. / Create two 1/1 green and white Citizen creature tokens. |
| Gloom Ripper | 0.94 | When this creature enters, target creature you control gets +X/+0 until end of turn and up to one target creature an opponent controls gets -0/-X until end of turn, where X is the number of Elves you control plus the number of Elf cards in your graveyard. | When this creature enters, target creature you control gets +X/+0 until end of turn and up to one target creature an opponent controls gets +0/-X until end of turn, where X is the number of Elves in your graveyard. |

## Known limits

- Mana-cost amounts, power/toughness and flavour are not tags; they are excluded, not scored as gaps.
- Concept and number matching are regex based; a rephrased but equal ability can score low. Read the lowest-25 table, not only the number.
- A reader that knows the real card from the tags (famous cards) inflates the score; see `recognised`.
- Similarity bands have not been checked against human judgement yet.

# Reverse check of the tags (blind reader)

Run `g10c`. A blind reader saw only each card's tags and wrote the ability text they describe; that text was scored against the real Oracle text. Tool: `deckgen/tagcheck/reverse_check.py`. Similarity = 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1 (bands: good >= 0.7, partial 0.4-0.7, gap < 0.4; thresholds are unvalidated until a reader run is compared with a hand check). Mana-cost symbols are removed from both texts (costs are not tags).

## Summary

| cards | with text | mean similarity | good | partial | gap | source card ranked #1 | in top 5 | median rank |
|---|---|---|---|---|---|---|---|---|
| 72 | 72 | 0.738 | 48 | 20 | 4 | 69 | 70 | 1 |

Reader integrity: 0 outputs contain the card name (should be 0); 0 cards the reader says it recognised (a high rate weakens the test).

## What the tags failed to carry (concepts in the real text, absent from the reconstruction)

| concept | cards | share |
|---|---|---|
| opponent | 17 | 23% |
| each_all | 15 | 20% |
| may | 14 | 19% |
| you_control | 12 | 16% |
| choose | 9 | 12% |
| trigger_phase | 9 | 12% |
| eot | 8 | 11% |
| damage | 7 | 9% |
| instead | 7 | 9% |
| up_to | 6 | 8% |
| cast | 6 | 8% |
| cost_pay | 5 | 6% |
| copy | 5 | 6% |
| trigger_when | 5 | 6% |
| creature | 5 | 6% |
| counters | 5 | 6% |
| reveal | 4 | 5% |
| hand | 4 | 5% |
| kw:flying | 4 | 5% |
| battlefield | 4 | 5% |
| target | 4 | 5% |
| exile | 4 | 5% |
| sacrifice | 3 | 4% |
| graveyard | 3 | 4% |
| mana | 3 | 4% |

## What the reader added that the real text lacks (tags that over-claim or mislead)

| concept | cards |
|---|---|
| x_value | 13 |
| return | 3 |
| each_all | 3 |
| you_control | 3 |
| graveyard | 2 |
| library | 2 |
| flip | 1 |
| counters | 1 |
| creature | 1 |
| choose | 1 |
| lifeloss | 1 |
| exile | 1 |
| look_top | 1 |
| battlefield | 1 |

## Tags the reader could not read (by family)

x 14, c2 effect 5, s1 effect 2, c1.2 effect 2, c1.5 grant_ability 2, c2.2 grant_ability 2, c1 trigger 2, c2 trigger/cost 2, scales 2, clone 2, c2 remove 1, c3 remove 1, cost_reduce (amount/condition not given) 1, restrict_kind 1, s2.2 counter 1, s3 (no effect tags) 1, cost 1, c2 effect unspecified 1, c3.2 scope of cant_attack 1, s2 effect 1, k1 provides draw 1, c1 duration 1, c2.4 cant_block target 1, modal 1, c1.5 life_loss target 1, c1.7 exile target 1, no trigger for modal 1, c3 condition wording 1, c1 trigger for first Food 1, c3 trigger 1

Most common single tags: c2 effect 5, x:life_loss 2, s1 effect 2, c1.2 effect 2, x:trigger:end_step 2, c1 trigger 2, c2 trigger/cost 2, x:exile 2, clone 2, c2 remove:exile scales:counters 1, c3 remove:exile scales:counters 1, cost_reduce (amount/condition not given) 1, restrict_kind:doesnt_untap duration:permanent 1, s2.2 counter:existingcounter 1, s3 (no effect tags) 1, cost:life amount 1, c2 effect unspecified 1, c3.2 scope of cant_attack 1, s2 effect 1, k1 provides draw 1, c1 duration:eot 1, c2.4 cant_block target 1, modal:2_of_4 vs five modes listed 1, c1.5 life_loss target 1, x:life_loss trigger:end_step 1, c1.7 exile target 1, no trigger for modal 1, c3 condition wording 1, c1 trigger for first Food 1, c3 trigger 1

## Lowest 25 cards

| Card | sim | missing concepts | extra concepts | real text | reader text |
|---|---|---|---|---|---|
| Spark Double | 0.00 | battlefield copy counters creature legend may you_control |  | You may have Spark Double enter as a copy of a creature or planeswalker you control, except it enters with an additional +1/+1 counter on it if it's a creature, it enters with an additional loyalty counter on it if it's a planeswalker, and it isn't legendary if that permanent is legendary. | {Enters as a copy ... / with +1/+1 counters, scaling with planeswalkers} |
| Yusri, Fortune's Flame | 0.23 | cast choose damage draw each_all hand mana | exile library look_top x_value | Flying / Whenever Yusri, Fortune's Flame attacks, choose a number between 1 and 5. Flip that many coins. For each flip you win, draw a card. For each flip you lose, Yusri deals 2 damage to you. If you won five flips this way, you may cast spells from your hand this turn without paying their mana cos | Flying / Whenever this creature attacks, exile the top X cards of your library. / Until end of turn, you may play them. / {Damage effect}. |
| The Great Aurora | 0.28 | each_all exile land library may opponent | x_value | Each player shuffles all cards from their hand and all permanents they own into their library, then draws that many cards. Each player may put any number of land cards from their hand onto the battlefield. Exile The Great Aurora. | Shuffle. / Put a card from your hand onto the battlefield, then shuffle. / {Each player's cards remembered} shuffle. / Draw X cards, where X is the remembered amount. |
| The Keeper of the Yellow Hat | 0.36 | cast equip kw:equip kw:lifelink legend lifegain pump |  | You can't cast Keeper of the Yellow Hat during your first seven turns of the game. (Keep track if you're playing with this!) / When The Keeper of the Yellow Hat enters the battlefield, create a legendary artifact equipment token named Yellow Hat with equip {2} and "Equipped creature gets +4/+4 and g | When this creature enters, create a white Hat creature token. |
| Victor, Valgavoth's Seneschal | 0.43 | creature eot graveyard surveil you_control |  | Eerie — Whenever an enchantment you control enters and whenever you fully unlock a Room, surveil 2 if this is the first time this ability has resolved this turn. If it's the second time, each opponent discards a card. If it's the third time, put a creature card from a graveyard onto the battlefield  | Whenever an enchantment enters under your control, each opponent discards a card. / {Put a card from a graveyard onto the battlefield under your control.} / {Surveil} |
| Thought Rattle | 0.50 | cast choose graveyard reveal | x_value | Target opponent reveals each nonland card in their hand. You choose one of those cards. Exile that card. / Threshold — If there are seven or more cards in your graveyard, seek a Rat card. It perpetually gains "This spell costs {1} less to cast." / You gain 1 life for each Rat card in your hand. | Target opponent exiles {N} cards from their hand {effect}. / Threshold - {condition}. / You gain X life, where X is the number of Rat cards in your hand. |
| The Eagles Are Coming! | 0.50 | choose each_all instead kw:flying | you_control | Kicker {2}{W}{W} (You may pay an additional {2}{W}{W} as you cast this spell.) / Choose target creature you own. If this spell was kicked, instead choose any number of target creatures you own. Return each chosen creature to your hand. At the beginning of the next upkeep, create a 4/4 white Bird Sol | Kicker {cost} / Return target creature you control to its owner's hand. / If this spell was kicked, create a {token}. |
| Semester's End | 0.52 | counters each_all trigger_phase | x_value | Exile any number of target creatures and/or planeswalkers you control. At the beginning of the next end step, return each of them to the battlefield under its owner's control. Each of them enters with an additional +1/+1 counter on it if it's a creature and an additional loyalty counter on it if it' | Exile X target creatures and/or planeswalkers you control, then return them to the battlefield under their owner's control. / {Counters}. |
| The Motherlode, Excavator | 0.53 | choose cost_pay creature kw:flying may | counters x_value | When The Motherlode, Excavator enters, choose target opponent. You get an amount of {E} (energy counters) equal to the number of nonbasic lands that player controls. / Whenever The Motherlode attacks, you may pay {E}{E}{E}{E}. When you do, destroy target nonbasic land defending player controls, and  | When this creature enters, target opponent gets X energy counters, where X is the number of nonbasic lands they control. / Whenever this creature attacks, destroy target nonbasic land. / {Target} can't block this turn. |
| The Horus Heresy | 0.56 | battlefield each_all up_to | x_value | (As this Saga enters and after your draw step, add a lore counter. Sacrifice after III.) / I — For each opponent, gain control of up to one target nonlegendary creature that player controls for as long as The Horus Heresy remains on the battlefield. / II — Draw a card for each creature you control b | I - Gain control of target nonlegendary creature an opponent controls {duration}. / II - Draw X cards, where X is the number of creatures you control that you don't own. / III - Destroy {target}. |
| Vincent's Limit Break | 0.57 |  | choose | Tiered (Choose one additional cost.) / Until end of turn, target creature you control gains "When this creature dies, return it to the battlefield tapped under its owner's control" and has the chosen base power and toughness. / • Galian Beast — {0} — 3/2. / • Death Gigas — {1} — 5/2. / • Hellmasker  | Tiered / Choose one - Target creature you control gains "When this creature dies, return it to the battlefield tapped under its owner's control" until end of turn. / (three tier options with {cost} each) |
| Shilgengar, Sire of Famine | 0.57 | counters instead | x_value | Flying / Sacrifice another creature: Create a Blood token. If you sacrificed an Angel this way, create a number of Blood tokens equal to its toughness instead. / {W/B}{W/B}{W/B}, Sacrifice six Blood tokens: Return each creature card from your graveyard to the battlefield with a finality counter on i | Flying / Sacrifice a creature: Create X Blood artifact tokens. / Sacrifice a Blood token: Return all creature cards from your graveyard to the battlefield under your control. |
| The Darkhold | 0.59 |  | x_value | {T}: Put a sin counter on The Darkhold. Draw a card for each sin counter on it, then you lose 1 life for each card in your hand. / {6}{B}{B}, {T}: Each player's life total becomes the lowest life total among all players. Activate only as a sorcery. | {T}: Put a sin counter on this artifact. / Draw X cards, where X is the number of counters on it. / You lose X life, where X is the number of cards in your hand. / {6}{B}{B}, {T}: {effect} each player. |
| Betor, Kin to All | 0.62 |  | lifeloss | Flying / At the beginning of your end step, if creatures you control have total toughness 10 or greater, draw a card. Then if creatures you control have total toughness 20 or greater, untap each creature you control. Then if creatures you control have total toughness 40 or greater, each opponent los | Flying / Draw a card. / Untap all creatures you control. / Each player loses life equal to half their life total, rounded up. / At the beginning of the end step, {effect}. |
| Smog Smasher | 0.62 | battlefield damage each_all exile haste kw:haste opponent trigger_phase you_control |  | Menace / Start your engines! / Whenever one or more creatures you control deal combat damage to a player, conjure a duplicate of target nontoken creature into exile. / Max speed — At the beginning of combat on your turn, put all cards exiled with this creature onto the battlefield. They gain haste.  | Menace / Start your engines! / Whenever one or more creatures {event}, {effect} target creature. / Sacrifice {cost}. |
| The Spear of Leonidas | 0.64 | legend |  | Whenever equipped creature attacks, choose one — / • Bull Rush — It gains double strike until end of turn. / • Summon — Create Phobos, a legendary 3/2 red Horse creature token. / • Revelation — Discard two cards, then draw two cards. / Equip {2} | Equip {2} / Whenever equipped creature attacks, choose one - It gains double strike until end of turn. / Create a black {token}. / Discard two cards, then draw two cards. |
| Swooping Pteranodon | 0.64 | damage land trigger_phase you_control |  | Flying, haste / Whenever Swooping Pteranodon or another Dinosaur you control with flying enters, gain control of target creature an opponent controls until end of turn. Untap that creature. It gains flying and haste until end of turn. At the beginning of the next end step, target land deals 3 damage | Flying / Haste / Whenever a creature enters under your control, gain control of target creature an opponent controls until end of turn. / Untap it. / It gains haste and flying until end of turn. / {Target land, 3 damage effect}. |
| Roads Go Ever, Ever On | 0.65 | attack creature each_all eot pump target trigger_when you_control | return | (As this Saga enters and after your draw step, add a lore counter. Sacrifice after IV.) / I — Search your library for up to two basic Plains cards, exile them, then shuffle. You gain 2 life. / II, III — Put a card exiled with this Saga into its owner's hand. / IV — Whenever you attack this turn, tar | I - Search your library for up to two basic Plains cards, exile them, then shuffle. / You gain 2 life. / II - Return an exiled card to your hand. / III - Return an exiled card to your hand. / IV - {effect}. |
| Roalesk, Prime Specimen | 0.65 | cost_pay hand may you_control | each_all | Flying / Whenever Roalesk, Prime Specimen or another permanent you control is turned face up, you may pay {X}. If you do, if X is 1 or more, conjure a duplicate of a random creature card with mana value X into your hand. Cloak it. It gains "{G/U}: Turn this creature face up" for as long as it remain | Flying / Disguise {cost} / When this creature is turned face up, {effect} each creature with mana value X. |
| Case of the Pilfered Proof | 0.66 | flip instead token | creature | Whenever a Detective you control enters and whenever a Detective you control is turned face up, put a +1/+1 counter on it. / To solve — You control three or more Detectives. (If unsolved, solve at the beginning of your end step.) / Solved — If one or more tokens would be created under your control,  | Whenever a creature enters under your control, put a +1/+1 counter on it. / {Flip-up} ... / To solve - at least three Detectives you control. / Solved - {token replacement effect}. |
| Sokrates, Athenian Teacher | 0.67 | damage draw each_all eot opponent |  | Defender / Sokrates, Athenian Teacher has hexproof as long as it's untapped. / Sokratic Dialogue — {T}: Until end of turn, target creature gains "If this creature would deal combat damage to a player, prevent that damage. This creature's controller and that player each draw half that many cards, rou | Defender / Untapped cards have hexproof. / {T}: Target creature gains {ability}. / {Draw}. |
| Summoning Trap | 0.68 | cast cost_pay eot mana opponent |  | If a creature spell you cast this turn was countered by a spell or ability an opponent controlled, you may pay {0} rather than pay this spell's mana cost. / Look at the top seven cards of your library. You may put a creature card from among them onto the battlefield. Put the rest on the bottom of yo | Look at the top seven cards of your library. / You may put a creature card from among them onto the battlefield. |
| Carth the Lion | 0.69 |  |  | Whenever Carth the Lion enters or a planeswalker you control dies, look at the top seven cards of your library. You may reveal a planeswalker card from among them and put it into your hand. Put the rest on the bottom of your library in a random order. / Planeswalkers' loyalty abilities you activate  | When this creature enters, you may look at the top seven cards of your library. / You may reveal a planeswalker card from among them and put it into your hand. / Whenever a planeswalker you control dies, you may {effect}. |
| The Wilds | 0.70 | instead trigger_when | x_value | When you planeswalk to The Wilds and at the beginning of your upkeep, create a Food token. / Whenever chaos ensues, target player sacrifices a creature. If they do, you create a Food token. You create two Food tokens instead if the sacrificed creature's toughness was 4 or greater. | Create a Food token. / At the beginning of your upkeep, target player sacrifices a creature. / Create X Food tokens, where X is the number of sacrificed creatures with toughness 4 or greater plus one. |
| Subversive Acolyte | 0.70 | damage sacrifice trigger_when | flip | {2}, Pay 2 life: Choose one. Activate only once. / • Subversive Acolyte becomes a Human Cleric. It gets +1/+1 and gains lifelink. / • Subversive Acolyte becomes a Phyrexian. It gets +3/+2 and gains trample and "Whenever this creature is dealt damage, sacrifice that many permanents." | {2}, Pay N life: Choose one - Transform this creature into a Human Cleric; it gets +1/+1 and gains lifelink permanently. / Transform this creature into a Phyrexian; it gets +3/+2 and gains trample permanently. |

## Highest 5 cards

| Card | sim | real text | reader text |
|---|---|---|---|
| Additive Evolution | 1.00 | When this enchantment enters, create a 0/0 green and blue Fractal creature token. Put three +1/+1 counters on it. / At the beginning of combat on your turn, put a +1/+1 counter on target creature you control. It gains vigilance until end of turn. | When this enchantment enters, create a 0/0 green and blue Fractal creature token, then put three +1/+1 counters on it. / At the beginning of combat on your turn, put a +1/+1 counter on target creature you control. / It gains vigilance until end of turn. |
| Ajani Fells the Godsire | 1.00 | I — Exile target creature an opponent controls with power 3 or greater. / II — Create a 2/1 white Cat Warrior creature token, then put a vigilance counter on a creature you control. / III — Target creature you control gains double strike until end of turn. | I - Exile target creature an opponent controls with power 3 or greater. / II - Create a 2/1 white Cat Warrior creature token, then put a vigilance counter on it. / III - Target creature you control gains double strike until end of turn. |
| Silverquill Command | 0.98 | Choose two — / • Target creature gets +3/+3 and gains flying until end of turn. / • Return target creature card with mana value 2 or less from your graveyard to the battlefield. / • Target player draws a card and loses 1 life. / • Target opponent sacrifices a creature. | Choose two - Target creature gets +3/+3 and gains flying until end of turn. / Return target creature card with mana value 2 or less from your graveyard to the battlefield. / Target player draws a card. / Each opponent loses 1 life. / Target opponent sacrifices a creature. |
| Triad of Fates | 0.97 | {1}, {T}: Put a fate counter on another target creature. / {W}, {T}: Exile target creature that has a fate counter on it, then return it to the battlefield under its owner's control. / {B}, {T}: Exile target creature that has a fate counter on it. Its controller draws two cards. | {1}, {T}: Put a fate counter on another target creature. / {W}, {T}: Exile target creature with a counter on it, then return it to the battlefield under its owner's control. / {B}, {T}: Exile target creature with a counter on it. / Draw two cards. |
| Renegade Bull | 0.97 | Trample / Whenever you cast an instant or sorcery spell, this creature gets +X/+0 until end of turn, where X is that spell's mana value. / Whenever this creature attacks, exile up to one target instant or sorcery card from your graveyard and copy it. You may cast the copy without paying its mana cos | Trample / Whenever you cast an instant or sorcery spell, this creature gets +X/+0 until end of turn, where X is that spell's mana value. / Whenever this creature attacks, you may exile up to one target instant or sorcery card from your graveyard. / If you do, you may cast it without paying its mana  |

## Known limits

- Mana-cost amounts, power/toughness and flavour are not tags; they are excluded, not scored as gaps.
- Concept and number matching are regex based; a rephrased but equal ability can score low. Read the lowest-25 table, not only the number.
- A reader that knows the real card from the tags (famous cards) inflates the score; see `recognised`.
- Similarity bands have not been checked against human judgement yet.

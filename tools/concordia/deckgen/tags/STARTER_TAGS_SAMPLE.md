# Starter tagging run: sample set (3 per card type, 1 per supertype)

Cards come from the starter decks where the deck has that type; a type or supertype the starter decks do not hold is filled from the whole card pool and marked *(not in starter decks)*. Oracle text is the `Oracle:` line of the Forge script (`/` = line break). Tags are the output of `deckgen/tag_run.py` (order: supertype, cardtype, subtype, keyword and qualifiers, ability tags). Nothing was changed in any card or deck.


## cardtype:creature

| Card | Oracle text | Tags |
|---|---|---|
| Deranged Assistant | {T}, Mill a card: Add {C}. (To mill a card, put the top card of your library into your graveyard.) | cardtype:creature type:human type:wizard mana_source mill |
| Captivating Crew | {3}{R}: Gain control of target creature an opponent controls until end of turn. Untap that creature. It gains haste until end of turn. Activate only as a sorcery. | cardtype:creature type:human type:pirate steal_temp |
| Scrapshooter | Gift a card (You may promise an opponent a gift as you cast this spell. If you do, when it enters, they draw a card.) / Reach / When Scrapshooter enters, if the gift was promised, destroy target artifact or enchantment an opponent controls. | cardtype:creature type:raccoon type:archer kw:gift kw:reach draw removal |

## cardtype:instant

| Card | Oracle text | Tags |
|---|---|---|
| Filter Out | Return all noncreature, nonland permanents to their owners' hands. | cardtype:instant bounce |
| Scorching Dragonfire | Scorching Dragonfire deals 3 damage to target creature or planeswalker. If that creature or planeswalker would die this turn, exile it instead. | cardtype:instant removal |
| Harrow | As an additional cost to cast this spell, sacrifice a land. / Search your library for up to two basic land cards, put them onto the battlefield, then shuffle. | cardtype:instant land_tutor sacrifice_outlet |

## cardtype:sorcery

| Card | Oracle text | Tags |
|---|---|---|
| Victimize | Choose two target creature cards in your graveyard. Sacrifice a creature. If you do, return the chosen cards to the battlefield tapped. | cardtype:sorcery reanimate |
| Search for Tomorrow | Search your library for a basic land card, put it onto the battlefield, then shuffle. / Suspend 2—{G} (Rather than cast this card from your hand, you may pay {G} and exile it with two time counters on it. At the beginning of your upkeep, remove a time counter. When the last is removed, you may cast it without paying its mana cost.) | cardtype:sorcery kw:suspend num:2 color:green land_tutor |
| Captain's Call | Create three 1/1 white Soldier creature tokens. | cardtype:sorcery token_make |

## cardtype:enchantment

| Card | Oracle text | Tags |
|---|---|---|
| Rancor | Enchant creature / Enchanted creature gets +2/+0 and has trample. / When Rancor is put into a graveyard from the battlefield, return Rancor to its owner's hand. | cardtype:enchantment type:aura kw:enchant type:creature trample recursion |
| Pacifism | Enchant creature / Enchanted creature can't attack or block. | cardtype:enchantment type:aura kw:enchant type:creature restrict |
| Oblivion Ring | When Oblivion Ring enters, exile another target nonland permanent. / When Oblivion Ring leaves the battlefield, return the exiled card to the battlefield under its owner's control. | cardtype:enchantment removal |

## cardtype:artifact

| Card | Oracle text | Tags |
|---|---|---|
| Memnarch, the Warden | Indestructible / When Memnarch enters, create two 1/1 colorless Myr artifact creature tokens. / Whenever Memnarch attacks, draw a card for each artifact you control. | supertype:legendary cardtype:artifact cardtype:creature type:wizard kw:indestructible draw indestructible scales:Artifact token_make |
| Arcane Signet | {T}: Add one mana of any color in your commander's color identity. | cardtype:artifact fixing mana_source |
| Bontu's Monument | Black creature spells you cast cost {1} less to cast. / Whenever you cast a creature spell, each opponent loses 1 life and you gain 1 life. | supertype:legendary cardtype:artifact burn cost_reduce lifegain |

## cardtype:planeswalker

| Card | Oracle text | Tags |
|---|---|---|
| Teferi, Temporal Archmage *(not in starter decks)* | [+1]: Look at the top two cards of your library. Put one of them into your hand and the other on the bottom of your library. / [-1]: Untap up to four target permanents. / [-10]: You get an emblem with "You may activate loyalty abilities of planeswalkers you control on any player's turn any time you could cast an instant." / Teferi, Temporal Archmage can be your commander. | supertype:legendary cardtype:planeswalker type:teferi selection |
| Teferi, Timeless Voyager *(not in starter decks)* | [+1]: Draw a card. / [-3]: Put target creature on top of its owner's library. / [-8]: Each creature target opponent controls phases out. Until the end of your next turn, they can't phase in. (Treat them and anything attached to them as though they don't exist.) | supertype:legendary cardtype:planeswalker type:teferi draw removal |
| Davriel, Soul Broker *(not in starter decks)* | [+1]: Until your next turn, whenever an opponent attacks you and/or planeswalkers you control, they discard a card. If they can't, they sacrifice an attacking creature. / [-2]: Accept one of Davriel's offers, then accept one of Davriel's conditions. / [-3]: Target creature an opponent controls perpetually gets -3/-3. | supertype:legendary cardtype:planeswalker type:davriel pump_single discard draw lifegain pump_team reanimate recursion scales:graveyard selection shrink |

## cardtype:land

| Card | Oracle text | Tags |
|---|---|---|
| Lonely Sandbar | Lonely Sandbar enters tapped. / {T}: Add {U}. / Cycling {U} ({U}, Discard this card: Draw a card.) | cardtype:land kw:cycling color:blue draw cycling mana_source |
| Blighted Woodland | {T}: Add {C}. / {3}{G}, {T}, Sacrifice Blighted Woodland: Search your library for up to two basic land cards, put them onto the battlefield tapped, then shuffle. | cardtype:land land_tutor mana_source sacrifice_outlet |
| Evolving Wilds | {T}, Sacrifice Evolving Wilds: Search your library for a basic land card, put it onto the battlefield tapped, then shuffle. | cardtype:land land_tutor sacrifice_outlet |

## cardtype:battle

| Card | Oracle text | Tags |
|---|---|---|

## supertype:legendary

| Card | Oracle text | Tags |
|---|---|---|
| Arcanis the Omnipotent | {T}: Draw three cards. / {2}{U}{U}: Return Arcanis the Omnipotent to its owner's hand. | supertype:legendary cardtype:creature type:wizard bounce draw |

## supertype:basic

| Card | Oracle text | Tags |
|---|---|---|
| Forest | ({T}: Add {G}.) | supertype:basic cardtype:land landtype:forest |

## supertype:snow

| Card | Oracle text | Tags |
|---|---|---|
| Blizzard Strix *(not in starter decks)* | Flash / Flying / When Blizzard Strix enters, if you control another snow permanent, exile target permanent other than Blizzard Strix. Return that card to the battlefield under its owner's control at the beginning of the next end step. | supertype:snow cardtype:creature type:bird kw:flash kw:flying flying removal |

## supertype:world

| Card | Oracle text | Tags |
|---|---|---|
| Eye of Singularity *(not in starter decks)* | When Eye of Singularity enters, destroy each permanent with the same name as another permanent, except for basic lands. They can't be regenerated. / Whenever a permanent other than a basic land enters, destroy all other permanents with that name. They can't be regenerated. | supertype:world cardtype:enchantment |

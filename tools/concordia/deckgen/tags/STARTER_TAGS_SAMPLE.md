# Starter tagging run: sample set (3 per card type, 1 per supertype)

Cards come from the starter decks where the deck has that type; a type or supertype the starter decks do not hold is filled from the whole card pool and marked '(not in starter decks)'. Oracle text is the `Oracle:` line of the Forge script (`/` = line break). Tags are the output of `deckgen/tag_run.py`. Nothing was changed in any card or deck.


## cardtype:creature

| Card | Oracle text | Tags |
|---|---|---|
| Vodalian Arcanist | {T}: Add {C}. Spend this mana only to cast an instant or sorcery spell. | cardtype:creature type:merfolk type:wizard mana_source |
| Goblin Rabblemaster | Other Goblin creatures you control attack each combat if able. / At the beginning of combat on your turn, create a 1/1 red Goblin creature token with haste. / Whenever Goblin Rabblemaster attacks, it gets +1/+0 until end of turn for each other attacking Goblin. | cardtype:creature type:goblin type:warrior duration:eot scales:Goblin token_make |
| Colossal Dreadmaw | Trample (This creature can deal excess combat damage to the player or planeswalker it's attacking.) | cardtype:creature type:dinosaur kw:trample trample |

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
| Oko, Thief of Crowns (not in starter decks) | [+2]: Create a Food token. (It's an artifact with "{2}, {T}, Sacrifice this token: You gain 3 life.") / [+1]: Target artifact or creature loses all abilities and becomes a green Elk creature with base power and toughness 3/3. / [-5]: Exchange control of target artifact or creature you control and target creature an opponent controls with power 3 or less. | supertype:legendary cardtype:planeswalker type:oko artifact_token token_make |
| Rowan, Fearless Sparkmage (not in starter decks) | [+1]: Up to one target creature gets +3/+0 and gains first strike until end of turn. / [-2]: Rowan, Fearless Sparkmage deals 1 damage to each of up to two target creatures. Those creatures can't block this turn. / [-9]: Gain control of all creatures until end of turn. Untap them. They gain haste until end of turn. | supertype:legendary cardtype:planeswalker type:rowan duration:eot first_strike pump_single removal steal_temp |
| Garruk, Veiled Butcher (not in starter decks) | If a creature an opponent controls would die, exile it instead. / [+2]: Up to one target creature gets -4/-1 until your next turn. / [-2]: Each player sacrifices a creature of their choice. If you sacrificed a creature this way, create a 4/4 green Beast creature token with trample. / [-3]: Each opponent discards two cards. For each opponent who didn't discard two nonland cards this way, you draw a card. | supertype:legendary cardtype:planeswalker type:garruk pump_single discard draw shrink token_make |

## cardtype:land

| Card | Oracle text | Tags |
|---|---|---|
| Temple of the False God | {T}: Add {C}{C}. Activate only if you control five or more lands. | cardtype:land mana_source |
| Blighted Woodland | {T}: Add {C}. / {3}{G}, {T}, Sacrifice Blighted Woodland: Search your library for up to two basic land cards, put them onto the battlefield tapped, then shuffle. | cardtype:land land_tutor mana_source sacrifice_outlet |
| Myriad Landscape | Myriad Landscape enters tapped. / {T}: Add {C}. / {2}, {T}, Sacrifice Myriad Landscape: Search your library for up to two basic land cards that share a land type, put them onto the battlefield tapped, then shuffle. | cardtype:land land_tutor mana_source sacrifice_outlet |

## cardtype:battle

| Card | Oracle text | Tags |
|---|---|---|
| Invasion of Kaldheim (not in starter decks) | (As a Siege enters, choose an opponent to protect it. You and others can attack it. When it's defeated, exile it, then cast it transformed.) / When Invasion of Kaldheim enters, exile all cards from your hand, then draw that many cards. Until the end of your next turn, you may play cards exiled this way. | cardtype:battle type:siege draw |
| Invasion of New Phyrexia (not in starter decks) | (As a Siege enters, choose an opponent to protect it. You and others can attack it. When it's defeated, exile it, then cast it transformed.) / When Invasion of New Phyrexia enters, create X 2/2 white and blue Knight creature tokens with vigilance. | cardtype:battle type:siege token_make |
| Invasion of Moag (not in starter decks) | (As a Siege enters, choose an opponent to protect it. You and others can attack it. When it's defeated, exile it, then cast it transformed.) / When Invasion of Moag enters, put a +1/+1 counter on each creature you control. | cardtype:battle type:siege counters_plus |

## supertype:legendary

| Card | Oracle text | Tags |
|---|---|---|
| Kiki-Jiki, Mirror Breaker | Haste / {T}: Create a token that's a copy of target nonlegendary creature you control, except it has haste. Sacrifice it at the beginning of the next end step. | supertype:legendary cardtype:creature type:goblin type:shaman kw:haste clone haste |

## supertype:basic

| Card | Oracle text | Tags |
|---|---|---|
| Plains | ({T}: Add {W}.) | supertype:basic cardtype:land landtype:plains |

## supertype:snow

| Card | Oracle text | Tags |
|---|---|---|
| Frost Marsh (not in starter decks) | Frost Marsh enters tapped. / {T}: Add {U} or {B}. | supertype:snow cardtype:land fixing mana_source |

## supertype:world

| Card | Oracle text | Tags |
|---|---|---|
| Koskun Falls (not in starter decks) | At the beginning of your upkeep, sacrifice Koskun Falls unless you tap an untapped creature you control. / Creatures can't attack you unless their controller pays {2} for each creature they control that's attacking you. | supertype:world cardtype:enchantment attack_tax restrict |

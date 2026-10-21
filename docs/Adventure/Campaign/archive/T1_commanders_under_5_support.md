<!-- Archived from the Claude Docs original on 2026-10-21 (user notes included as of the read time); the original doc was purged. Superseded by the Tier 1 Deck-Building Report. -->

# Tier 1 Commanders Under 5 Support Cards

Fourteen tier 1 commanders have fewer than the 5 deck cards the commander-ability rule (H17) requires; ten of them score 0–1 because the check reads only generic keyword tags.

The check takes the commander's ability tags (minus generic ones such as draw, removal, mana source and etb), then counts deck cards that share any of them. Commanders whose ability is a tribe (Elf, Merfolk, Pirate), an equipment count, a self-recursion or a spell-targeting trigger are barely visible to it: Dwynen and Attuma show no tags at all, and Squee shows only recursion. The counts below come from one dry build per deck and can move by one between runs.

Use Your notes to say what should count as support for each commander (card types, creature types, effects), and set a different threshold if 5 is wrong for it. Your notes feed the human-logic file.

## The 14 commanders

| Commander | Deck | Colour | Cards found (5 needed) | Ability | Tags the check used | Your notes |
|---|---|---|---|---|---|---|
| Squee, Goblin Nabob | R_Squee | R | 0 | Returns itself from the graveyard to hand each upkeep | recursion | sacrifice synergy, minimum-risk combat (free recursion is not -1 on trades) |
| Adelbert Steiner | W_Adelbert | W | 0 | Lifelink; +1/+1 for each Equipment you control | lifelink | equipment synergy, read same as 'for X number of Y you control'. Read '+1/+1 for each' as potential new stat block |
| Cleon, Merry Champion | R_Cleon | R | 0 | Double strike; heroic: when you cast a spell that targets it, exile the top card and you may play it | double_strike | read 'exile the top card and you may play it' as low-draw interaction |
| Dwynen, Gilt-Leaf Daen | G_Dwynen | G | 1 | Reach; other Elves get +1/+1; gains life when it attacks (per attacking Elf) | (none) | tribal synergy, read 'per X Y' same as 'for X number of Y you control' synergy. |
| Baird, Steward of Argive | W_Baird | W | 1 | Vigilance; creatures can't attack you unless their controller pays 1 each | attack_tax, restrict | control synergy, tag potential opponent interaction as synergy. calculate/tag 'pays mana' as curve disruption. |
| Losheel, Clockwork Scholar | W_Losheel | W | 1 | Prevents combat damage to your attacking artifact creatures; draws a card (once a turn) when artifact creatures enter | (none) | draw interaction, artifact synergy, read 'when x enters' as etb synergy |
| Breeches, Brazen Plunderer | R_Breeches | R | 1 | Menace; when Pirates deal damage to opponents, exile the top card of each of their libraries and you may play those cards | evasion | read 'exile the top card and you may play it' as low-draw interaction, read opponent library exile as low removal |
| Attuma, Atlantean Warlord | U_Attuma | U | 1 | Other Merfolk get +1/+1; draws a card when Merfolk attack a player | (none) | merfolk tribal, read 'when X attacks' as combat trigger |
| Fynn, the Fangbearer | G_Fynn | G | 1 | Deathtouch; deathtouch creatures that hit a player give two poison counters | deathtouch | weigh poison counters as 4 life damage, deathtouch=control synergy |
| Ian the Reckless | R_Ian | R | 1 | When it attacks while modified (Equipment, Auras or counters on it), deals damage equal to its power to you and any target | burn | modified= equipment,aura,counter synergy |
| Thalia, the Survivor | W_Thalia | W | 2 | Lifelink; opponents' noncreature spells cost 1 more | lifelink | tax, control synergy |
| Rescue Girl, First Responder | W_Rescue | W | 2 | Flying; taps to return another permanent you control to hand during your turn | bounce, flying | read self bounce as etb synergy |
| Splinter, Hamato Yoshi | B_Splinter | B | 3 | Sneak (cast for B by returning an unblocked attacker) | evasion | weigh as two different cost cards, combat trick |
| Hobgoblin, Mantled Marauder | R_Hobgoblin | R | 4 | Flying, haste; gets +2/+0 whenever you discard a card | flying, haste | discard synergy |

## Dwynen and the life-drain rule (H16)

Dwynen, Gilt-Leaf Daen is the only one of the 14 that also fails the life-gain commander rule: H16 wants 2 drain or burn cards for a life-gain commander, and the tier 1 pool gives a green deck only 1.

| Item | Value | Your notes |
|---|---|---|
| Rule | Life-gain commanders want "X damage and gain X life" effects counted as alternate removal (H16, from Nazar) | irrelevant when noncombat damage not included in ability |
| Dwynen's life gain | 1 life for each attacking Elf when it attacks | tribal, count tribe number on battlefield for potential lifegain per turn |
| Drain or burn cards in the deck | 1 (2 needed) | decouple burn from lifegain, set as potential synergy |
| Options | Accept the warning; or widen the drain pool (which cards or effects should count?) |  |
| Decision |  | see above all context |

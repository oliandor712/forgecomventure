# User feedback on the starter tag sample (form filled 2026-10-22)

Source: Claude Doc "Starter Tag Sample: Feedback Form" (https://claude.ai/artifact/Fgf89KjLmr4ifAiQSAoiJ8). Notes are the user's own words, lightly joined (the doc stores them as edited fragments). Use as the reference for what the tags should capture. Standing instruction: new tags may be created to fill gaps seen across the references; every tag created is logged in NEW_TAGS_FOR_APPROVAL.md for approval.

| Card | Verdict | User note |
|---|---|---|
| Vodalian Arcanist | Missing tag | link color type to mana source |
| Goblin Rabblemaster | Missing tag | "attack each combat if able" = mustattack, target is other goblins |
| Colossal Dreadmaw | Extra tag | trample listed twice; prevent this for keywords |
| Filter Out | Missing tag | target type = all; create tags for number of targets (a or one creature, all, you (don't) control, a number equal to x) and types of targets (a card type) |
| Scorching Dragonfire | Missing tag | target types; separate removal tag into exile or destroy; destroyed creatures 'die'; 'exile instead' effect, common |
| Harrow | Missing tag | sacrifice also a cost here, tag it; link tags for tutor amount (up to two = 0-2); tag shuffle |
| Victimize | Missing tag | (no note) |
| Search for Tomorrow | Missing tag | split land tutor into put tapped or just put; note green as suspend cost |
| Captain's Call | Missing tag | tag token type, count, color |
| Rancor | Missing tag | tag graveyard zone trigger |
| Pacifism | Correct | |
| Oblivion Ring | Missing tag | tag target type, tag recursion from on-leave trigger, tag leave trigger |
| Memnarch, the Warden | Missing tag | token type, count, color |
| Arcane Signet | Missing tag | tag color |
| Bontu's Monument | Missing tag | tag color link to cost reduce, tag activated cast trigger, linked to creature cardtype |
| Oko, Thief of Crowns | Missing tag | tag food token type, lifegain, 'loses all abilities and becomes a' = tag as transform, tag exchange linked to steal, tag target types linked to each, tag loyalty, tag counter (loyalty is counters) |
| Rowan, Fearless Sparkmage | Missing tag | tag damage as damage instead of removal, tag cantblock, link haste to steal, loyalty, counters |
| Garruk, Veiled Butcher | Missing tag | tag exile instead on graveyard trigger, tag sacrifice as removal and cost, link token trigger to self sacrifice trigger, token tags |
| Temple of the False God | Missing tag | link color type, tag activation restriction |
| Blighted Woodland | Missing tag | tag sacrifice as cost, tutor count, tutor target type, put tapped, tag shuffle |
| Myriad Landscape | Missing tag | tag enters tapped, color type, tag sacrifice as cost, tutor count, tutor target type, put tapped, tag shuffle |
| Invasion of Kaldheim | Missing tag | tag transform, tag toughness, tag etb trigger, tag exile, tag 'exile, play until end of turn' as impulse draw, link duration eot |
| Invasion of New Phyrexia | Missing tag | tag transform, tag toughness, tag etb, tag token types, tag x pump |
| Invasion of Moag | Missing tag | tag transform, tag toughness, tag etb, tag counter types (+1/+1), tag target types and amount (creature, each you control) |
| Kiki-Jiki, Mirror Breaker | Missing tag | tag duration (end step), tag sacrifice |
| Plains | Missing tag | tag mana source, color, trigger type (all basics tap for one color mana) |
| Frost Marsh | Missing tag | tag mana color option, trigger type |
| Koskun Falls | Skip | purge worlds from concordia card pool, enforce |

## Patterns across the notes
1. Colour is a tag wherever it matters and is linked to what it belongs to: the mana a source produces, a cost reduction's filter, a suspend cost, a token's colour.
2. Targets: count (one, up to N, all, X, each), scope (you control, opponent controls), and type (a card type) are separate tags.
3. Removal is split by method: destroy, exile, damage, sacrifice, bounce. Damage is damage, not removal. 'Exile instead' on dying is its own tag. Destroyed creatures 'die'.
4. Costs and effects are tagged separately, and sacrifice can be either.
5. Tutors: count, target type, destination (battlefield, battlefield tapped, hand), shuffle.
6. Tokens: type, count, colour (and Food/Treasure-type tokens).
7. Triggers: enters, leaves, dies, graveyard zone, cast with a card-type filter, delayed end-step triggers; durations (eot, end step) are linked to the effect.
8. Planeswalker and battle: loyalty and defense are counters; transform ('becomes', 'loses all abilities'); impulse draw; exchange control linked to steal; haste linked to steal.
9. Keywords are listed once (kw:), not also as a plain tag.
10. World supertype cards are purged from the Concordia pool, enforced.

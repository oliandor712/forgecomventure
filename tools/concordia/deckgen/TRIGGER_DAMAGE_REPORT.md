# Trigger damage sentences: what renders and what does not (2026-10-28)

Scope: the 33 cards with `damage_source:triggering` (a creature named by the trigger deals the damage). Renderer: `mtg2llm.trigger_damage_sentence`. Pool check: rules 1, 2, 3, 6, 7 = 0, rule 5 = 37 (lenient).

## Renders (5 of 33)
| Card | Text |
|---|---|
| Aether Charge | Whenever a Beast you control enters, you may have it deal 4 damage to target opponent or planeswalker. |
| Pandemonium | Whenever a creature enters, that creature's controller may have it deal damage equal to its power to any target. |
| Pyrogoyf | Whenever a creature you control enters, this creature deals damage equal to that creature's power to any target. |
| Stalking Vengeance | Whenever another creature you control dies, it deals damage equal to its power to target player. |
| Warstorm Surge | Whenever a creature you control enters, it deals damage equal to its power to any target. |

## Does not render (28), by cause
**A. Enters triggers the sentence declines (8)**
- Electropotence: pays {2}{R}; the sentence cannot say a cost.
- Flayer of the Hatebound: no controller filter and no `optional_decider`, so the sentence cannot tell who chooses (a correction: the Undying line is not the cause).
- Dragon Tempest, Scourge of Valkas, Hawkeye (Trick Shot): amount is a count (`x_is:count_*`), no wording yet.
- Be'lakor, Champion of the Path: a target the sentence cannot say (Champion: each opponent).
- Halana: no damage amount tag.

**B. Attack triggers (8):** Extra Arms, Lothlórien Blade, Mage Slayer, The War Doctor, Vengeful Ancestor, Ingris Stingerquill, Rage Forger, Laccolith Rig (attacker blocked).

**C. Damage-dealt triggers (9):** Blazing Sunsteel, Fiendlash, Greatbow Doyen, Spiteful Shadows, Pain for All, Kediss, Saskia the Unyielding, Super State, Trailblazer's Torch (attacker blocked).

**D. Other (3):** Barbflare Gremlin (condition), Hawkeye's Bow, Pyrotechnic Performer (flip-up). Reasons for these three are from the tag listing, not rechecked card by card.

## Gaps in the tags
- Who chooses the target (Pandemonium: "of their choice") is not tagged.
- `optional_decider` values other than `triggered_card_controller` are not worded yet.
- Counts as damage amounts (`x_is:count_*`, `triggering_damage`) are not said.

## Next
1. Attack and damage-dealt trigger wording (17 cards).
2. `x_is:count_*` amounts (3 cards).
3. A target-chooser tag if the user wants "of their choice".

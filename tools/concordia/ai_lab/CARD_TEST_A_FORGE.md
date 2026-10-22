# CARD TEST A (Forge syntax only): AILogic$ and tags from script text alone (forge-ai-lab, 2026-10-22)

Method A: reads the Forge script only (A:/S:/T:/R:/K: lines, Oracle line where noted); no mtgish. Research only: nothing edited in forge-ai, card scripts or the tag rules. Predictions use the 1,814 cards that carry `AILogic$` as the pool (lowercase names as in the request).

## Method and limits
- Signature = first A/S/T/R/K line's (kind, API, cost shape), plus the set of (kind, API) pairs on the card. Prediction = most common `AILogic$` among pool cards with the same primary signature (`exact-sig`), else among pool cards with the same primary API (`api-only`), else `none`.
- Control (set C) is scored leave-one-out: the card is removed from the pool before its own prediction.
- Grades: `exact` = same value; `partial` = wrong value but both the predicted and the actual value are used on cards with the same primary API; `miss` = otherwise.
- **Limit:** K (keyword) lines are often first in the card file, so Flying, Enchant, Flash and similar become the primary signature. That is why many Enchant auras predict NeedsPrevention. A better primary rule (prefer A/S/T lines) is the first fix to try.
- **Limit on tags:** the tags of set C are whatever `ability_tags.tags_of` produces, so tag agreement on C is circular and is not scored. For set T the tag check is real: `tags_of` on the full script text returned no tag for all 50 cards except none (0 of 50 tagged, after dropping has:/needs:/hint: entries).

## Set C: control cards with AILogic$ and tags (leave-one-out)
Score line: **exact 18 / partial 13 / miss 19 of 50** (exact 36%, exact-or-partial 62%).

| Card | Actual AILogic$ | Predicted | Basis (pool size) | Grade | Primary signature |
|---|---|---|---|---|---|
| Passenger Ferry | Pump | ReplaySpell | api-only (13) | miss | T Attacks |
| Unburied Earthcarver | AristocratCounters | PowerDmg | api-only (45) | miss | A PutCounter |
| Omen of the Dead | BestOpportunity | BestOpportunity | exact-sig (4) | exact | K Flash |
| Creative Outburst | AlwaysOnDiscard | AlwaysOnDiscard | exact-sig (1) | exact | A DealDamage |
| Iron Lad, Diverging Destiny | Main2 | MostProminentInHumanDeck | api-only (96) | miss | K Flying |
| Inner Fire | ManaRitual | ManaRitual | exact-sig (11) | exact | A Mana |
| Sentinel Totem | ExileGraveyards | ExileGraveyards | exact-sig (1) | exact | T ChangesZone |
| Underfoot Underdogs | MakeUnblockable | MakeUnblockable | exact-sig (3) | exact | T ChangesZone |
| Traveler's Cloak | ChosenLandwalk | MostProminentInHumanDeck | exact-sig (1) | miss | K Enchant |
| Arrester's Zeal | Main1IfAble | PowerDmg | exact-sig (97) | partial | A Pump |
| Bill Ferny, Bree Swindler | Curse | Pump | api-only (1) | miss | T AttackerBlocked |
| Touch of Invisibility | Pump | Fog | exact-sig (58) | partial | A Effect |
| Embalmer's Tools | AtOppEOT | Always | api-only (17) | partial | S ReduceCost |
| Rampaging Geoderm | TgtAttacker | Always | api-only (11) | miss | K Trample |
| Etchings of the Chosen | MostProminentInComputerDeck | MostProminentInComputerDeck | api-only (110) | exact | K ETBReplacement |
| Terrific Team-Up | PowerDmg | PowerDmg | exact-sig (5) | exact | S ReduceCost |
| Alora, Merry Thief | Pump | Always | api-only (4) | partial | T AttackersDeclared |
| Wash Out | MostExcessOpponentControls | MostProminentInHumanDeck | exact-sig (5) | miss | A ChooseColor |
| Auriok Replica | NeedsPrevention | NeedsPrevention | api-only (43) | exact | A ChooseSource |
| Lava Zombie | NeverBounceItself | PowerDmg | api-only (140) | miss | A Pump |
| Circle of Affliction | MostProminentInHumanDeck | MostProminentInComputerDeck | api-only (110) | partial | K ETBReplacement |
| Flaming Gambit | WorstCard | ReplaySpell | exact-sig (1) | miss | K Flashback |
| Subira, Tulzidi Caravanner | MakeUnblockable | MakeUnblockable | exact-sig (1) | exact | K Haste |
| Drain Life | XLifeDrain | XLifeDrain | exact-sig (1) | exact | A StoreSVar |
| Ancestral Statue | NeverBounceItself | NeverBounceItself | exact-sig (32) | exact | T ChangesZone |
| Cavern Harpy | NeverBounceItself | MostProminentInHumanDeck | api-only (96) | partial | K Flying |
| Claim the Kingdom | Pump | Always | api-only (101) | partial | T ChangesZone |
| Hidetsugu's Second Rite | OppAtTenLife | CantRegenerate | exact-sig (13) | miss | A DealDamage |
| Hikari, Twilight Guardian | IfNotBuffed | CloneBestCreature | exact-sig (1) | miss | K Flying |
| Recoup | ReplaySpell | WorstCard | exact-sig (1) | miss | K Flashback |
| Millstone | AtOppEOT | AtOppEOT | api-only (4) | exact | A Mill |
| Pilgrim of Justice | NeedsPrevention | NeedsPrevention | exact-sig (1) | exact | K Protection from red |
| Evolutionary Escalation | BoonCounterOnOppCreature | CloneBestCreature | exact-sig (26) | miss | T Phase |
| Torment of Venom | PayUnlessCost | PowerDmg | exact-sig (22) | miss | A PutCounter |
| Zoyowa Lava-Tongue | PayUnlessCost | PayUnlessCost | exact-sig (1) | exact | K Deathtouch |
| Timely Reinforcements | PlayForSub | Fog | exact-sig (1) | miss | A GainLife |
| Bloodline Pretender | MostProminentInComputerDeck | MostProminentInComputerDeck | api-only (5) | exact | K Changeling |
| Legion Vanguard | Aristocrat | Always | api-only (1) | miss | A Explore |
| Aquatic Incursion | MakeUnblockable | MakeUnblockable | exact-sig (3) | exact | T ChangesZone |
| Twinferno | SpellCopy | PowerDmg | exact-sig (34) | miss | A Charm |
| Shuri, Wakandan Inventor | Pump | PowerDmg | exact-sig (5) | miss | S ReduceCost |
| Addle | MostProminentInHumanDeck | MostProminentHumanCreatures | exact-sig (5) | partial | A ChooseColor |
| Prism Ring | MostProminentInComputerDeck | MostProminentInGame | exact-sig (5) | partial | K ETBReplacement |
| Ant-Man's Army | FoodOrTreasure | NeverBounceItself | exact-sig (32) | partial | T ChangesZone |
| Omen of the Sea | BestOpportunity | BestOpportunity | exact-sig (4) | exact | K Flash |
| You Look Upon the Tarrasque | Fog | PowerDmg | exact-sig (34) | miss | A Charm |
| Ambrosia Whiteheart | BounceOwnTrigger | ReplaySpell | exact-sig (8) | partial | K Flash |
| Stronghold Discipline | AllPlayerLoseLife | MostProminentComputerControls | exact-sig (10) | partial | A RepeatEach |
| Cutthroat Centurion | Aristocrat | Aristocrat | exact-sig (6) | exact | A Pump |
| Haunting Apparition | Curse | MostProminentInHumanDeck | exact-sig (3) | partial | K Flying |

## Set T: test cards (no AILogic$, no tags)
Tag check on full script text: **50 of 50 untagged by `ability_tags.tags_of`** (no tag rule matches any of them). Proposed AILogic$ below is the method's guess; `none needed` = no pool card shares the API.

| Card | Proposed AILogic$ | Basis (pool size) | Primary signature | Nearest existing AILogic$ card (example) | Rule gap (what no RULES entry covers) |
|---|---|---|---|---|---|
| Straw Golem | Always | exact-sig (6) | T SpellCast | Always | no RULES entry matches this line |
| Lightning Berserker | PowerDmg | api-only (141) | A Pump | PowerDmg | self-pump (`AB$ Pump`, Cost R, no ValidTgts; pump_single needs ValidTgts$ Creature) |
| Mask of Law and Grace | NeedsPrevention | exact-sig (1) | K Enchant | NeedsPrevention | `Mode$ Continuous | AddKeyword$ Protection`: protection_trick needs an SP/AB/DB Pump line |
| Whirlwind Denial | MostProminentComputerControls | exact-sig (11) | A RepeatEach | MostProminentComputerControls | `SP$ RepeatEach` counter-unless over opponents' spells: no counter-each tag |
| Blades of Velis Vel | SwitchPT | exact-sig (2) | K Changeling | SwitchPT | Pump with TargetMin/Max and sub-ability Animate (multi-target pump) |
| Bombur, Gentle Dreamer | none needed | no-candidate (0) | K Storied |  | keyword Storied (no rule for Storied) |
| Zombie Musher | ReplaySpell | api-only (1) | K Landwalk | ReplaySpell | keyword Snow landwalk: keyword-only; no landwalk tag |
| Lost Hours | BeforeCombat | exact-sig (22) | A ChangeZone | BeforeCombat | `SP$ ChangeZone` hand->library (put on top): tutor needs Origin Library; no hand-to-library rule |
| Dross Scorpion | NeverBounceItself | exact-sig (33) | T ChangesZone | NeverBounceItself | `T ChangesZone` dies-of-another trigger: dies_trigger covers only Self |
| Gobhobbler Rats | Curse | exact-sig (2) | S Continuous | Curse | static `S:` Continuous (hellbent): no static-condition tag |
| Aether Flash | NeverBounceItself | exact-sig (33) | T ChangesZone | NeverBounceItself | `Mode$ ChangesZone` enters trigger deals damage: etb_trigger covers only the Battlefield destination without damage |
| Shriek of Dread | PowerDmg | exact-sig (98) | A Pump | PowerDmg | `SP$ Pump | KW$ Fear`: evasion_grant lists Flying/Menace only, not Fear/Unblockable |
| Lignify | NeedsPrevention | exact-sig (1) | K Enchant | NeedsPrevention | Enchant aura with base P/T (Continuous), no static-P/T tag |
| Caparocti Sunborn | ReplaySpell | exact-sig (7) | T Attacks | ReplaySpell | `Mode$ Attacks` trigger with tap cost: no attack-trigger tag beyond combat_damage_trigger |
| Frostpeak Yeti | Fog | api-only (106) | A Effect | Fog | `AB$ Effect` with `StaticAbilities$ Unblockable`: evasion_grant only matches AddKeyword |
| False Mourning | BeforeCombat | exact-sig (22) | A ChangeZone | BeforeCombat | `SP$ ChangeZone` graveyard->library top: no graveyard-to-library rule |
| Hedron Rover | NeverBounceItself | exact-sig (33) | T ChangesZone | NeverBounceItself | landfall trigger: no landfall tag |
| Thrash of Raptors | Curse | exact-sig (2) | S Continuous | Curse | static `S:` Continuous (conditional pump): no static-pump tag |
| Defensive Stance | NeedsPrevention | exact-sig (1) | K Enchant | NeedsPrevention | no RULES entry matches this line |
| Spidery Grasp | Always | exact-sig (1) | A Untap | Always | `SP$ Untap` with `SubAbility$ DBPump` (pump only reached through a sub-ability) |
| Merrow Commerce | CloneBestCreature | exact-sig (27) | T Phase | CloneBestCreature | `Mode$ Phase` (end-step untap): no phase trigger tag |
| Halsin, Emerald Archdruid | Pump | api-only (20) | A Animate | Pump | `AB$ Animate` (becomes a creature until EOT): no animate tag exists |
| Rime Transfusion | NeedsPrevention | exact-sig (1) | K Enchant | NeedsPrevention | Enchant aura with `+2/+1` and a static grant: no aura-stat tag (only scales/lord tags) |
| Crumble to Dust | Pump | api-only (3) | K Devoid | Pump | Devoid keyword + destroy-land target: keyword-only signature; no land-removal rule for this line |
| Dragon Engine | PowerDmg | api-only (141) | A Pump | PowerDmg | self-pump (`AB$ Pump`, Defined$ Self); same gap as Lightning Berserker |
| Split-Tail Miko | MakeUnblockable | api-only (1) | A PreventDamage | MakeUnblockable | no RULES entry matches this line |
| Tangle Kelp | Curse | api-only (26) | K Enchant | Curse | Enchant aura with tap-on-enter: no aura-tap tag |
| Abandon Reason | PowerDmg | api-only (141) | A Pump | PowerDmg | multi-target pump with first strike: pump rules need NumAtt$ and single ValidTgts |
| Zada, Hedron Grinder | Always | exact-sig (6) | T SpellCast | Always | `Mode$ SpellCast` trigger that copies: no spell-cast trigger tag |
| Berg Strider | NeverBounceItself | exact-sig (33) | T ChangesZone | NeverBounceItself | etb with tap target: etb_trigger covers the ChangesZone form; the tap effect itself has no rule |
| Relentless Pursuit | none needed | no-candidate (0) | A DigMultiple |  | `AB$ DigMultiple` (reveal four, put creatures): selection rule covers Dig only, not DigMultiple |
| Cogwork Archivist | Always | api-only (7) | K Reach | Always | `AB$ ChangeZone` graveyard-to-library (bottom): no graveyard-to-library tag |
| Spike-Tailed Ceratops | Curse | exact-sig (2) | S Continuous | Curse | static `S:` Continuous (block an extra creature): no blocking-restriction tag |
| Frozen in Ice | Curse | exact-sig (1) | K Enchant | Curse | Enchant aura with tap: no aura-tap tag |
| Mordenkainen's Polymorph | PowerDmg | exact-sig (1) | A Animate | PowerDmg | `AB$ Animate` (Dragon form): no animate tag |
| Captain America, Living Legend | AtEOTIfNotAttacking | api-only (18) | K Vigilance | AtEOTIfNotAttacking | `Mode$ Attacks`-style trigger: no attack-trigger tag |
| Avalanche Caller | Pump | api-only (20) | A Animate | Pump | `AB$ Animate` (land becomes creature): no animate tag |
| Doomfall | PowerDmg | exact-sig (35) | A Charm | PowerDmg | `SP$ Charm` (modal): no charm tag |
| Compass Gnome | NeverBounceItself | exact-sig (33) | T ChangesZone | NeverBounceItself | etb search library: etb_trigger covers it; no search-on-enter tag |
| Port Inspector | Curse | exact-sig (1) | T AttackerBlocked | Curse | `Mode$ AttackerBlocked` trigger: no combat-block trigger tag |
| Bind the Monster | Curse | api-only (26) | K Enchant | Curse | Enchant aura with tap: no aura-tap tag |
| Chain of Silence | PowerDmg | exact-sig (98) | A Pump | PowerDmg | `SP$ Pump` prevent-damage (no KW/NumAtt): no prevention tag |
| Way of the Necromancer | NeverBounceItself | exact-sig (33) | T ChangesZone | NeverBounceItself | etb empower planeswalker: no planeswalker-ability tag |
| Phyrexian Ironfoot | MostProminentInComputerDeck | api-only (78) | R - | MostProminentInComputerDeck | `Event$ Untap` static restriction (CantHappen layer): no untap-restriction tag |
| Wild Swing | PowerDmg | exact-sig (98) | A Pump | PowerDmg | no RULES entry matches this line |
| Prakhata Pillar-Bug | SwitchPT | exact-sig (1) | A Pump | SwitchPT | `AB$ Pump` with KW Lifelink (self): same self-pump gap as Lightning Berserker |
| Kozilek's Pathfinder | Fog | api-only (106) | A Effect | Fog | see above (Effect with static can't-block) |
| Briar Patch | ReplaySpell | exact-sig (7) | T Attacks | ReplaySpell | `Mode$ Attacks` trigger (-1/-0 to attackers): no attack-trigger tag |
| Death Ward | none needed | no-candidate (0) | A Regenerate |  | `A:Regenerate`: no regenerate tag |
| Speedball, New Warrior | Always | exact-sig (6) | T SpellCast | Always | `Mode$ SpellCast` trigger (targets this): no spell-cast trigger tag |

## Gaps (for ability_tags.RULES and for the AILogic$ mapping)
1. **Self-pump activated abilities** (`AB$ Pump`, no ValidTgts, `Defined$ Self` or Cost only): pump_single misses them. Affects Lightning Berserker, Dragon Engine, Prakhata Pillar-Bug.
2. **Animate** (`AB$ Animate`: a land or artifact becomes a creature until EOT): no tag exists. Affects Halsin, Avalanche Caller, Mordenkainen's Polymorph.
3. **Keyword grants through Effect or static** (`AB$ Effect` with StaticAbilities Unblockable; `Mode$ Continuous` AddKeyword Protection on auras): evasion_grant and protection_trick match only the AddKeyword and SP/AB Pump forms. Affects Frostpeak Yeti, Kozilek's Pathfinder, Mask of Law and Grace.
4. **Trigger modes with no tag**: SpellCast (Zada, Speedball), Phase (Merrow Commerce, Evolutionary Escalation), AttackerBlocked (Port Inspector), Attacks (Caparocti Sunborn, Briar Patch, Captain America), landfall (Hedron Rover). These are the largest group in set T.
5. **Hand or graveyard to library** (`ChangeZone` with Destination Library but Origin Hand or Graveyard, put on top or bottom): the tutor rule needs Origin Library. Affects Lost Hours, False Mourning, Cogwork Archivist.
6. **Static conditions and aura stats** (`S:` Continuous with a condition, aura with base P/T): no tag. Affects Gobhobbler Rats, Thrash of Raptors, Lignify, Rime Transfusion.
7. **Multi-target and sub-ability forms** (TargetMin/Max, SubAbility pump): Blades of Velis Vel, Spidery Grasp, Abandon Reason.
8. **Keyword-only signatures**: Storied, Devoid, Snow landwalk: no rule, and they make the primary signature weak (see the limit above).

## Notes: cases that needed more than the Forge line
- Enchant auras (Lignify, Rime Transfusion, Defensive Stance, Mask of Law and Grace): the primary signature is the K Enchant line, so the prediction is NeedsPrevention or nothing. The Forge line gives the stat change; I did not check the Oracle line for these, so whether it adds anything is not verified.
- Passenger Ferry (set C): the actual value is Pump, but its primary signature is a Crew keyword, so the prediction (ReplaySpell) is a miss. The keyword-first limit explains it.
- Halsin and Avalanche Caller: the Forge animate line gives the P/T and the valid target; the duration is in the SpellDescription, not in a separate key. Not verified against the Oracle line.

## Proposed next steps (not executed)
1. Prefer A/S/T lines over K lines when choosing the primary signature; re-score set C (expected gain: most of the 19 misses are K-led).
2. Add the eight rule gaps above as candidate RULES entries, each tested on set C (no change to the existing tags).
3. Main session runs method B (mtgish) on the same sets and compares.

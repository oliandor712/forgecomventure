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

## Re-run A2 (all lines)
Change from A1: the signature now covers every line of the script (A/S/T/R, and K at weight 0.4, plus cost shape and trigger mode), not only the first line. The prediction is the `AILogic$` of the nearest pool card by weighted Jaccard overlap (leave-one-out on set C); exact-signature and API-only lookups are not needed because the nearest card always exists in the pool.

Grades: exact = same value; partial = wrong value, but both the predicted and the actual value are used on cards whose primary API matches the card's own primary API; miss otherwise.

**A2 score line (set C, 50 cards): exact 17 / partial 18 / miss 15. Exact-or-partial 35 of 50 (70%), up from 31 of 50 (62%) in A1. Exact alone: 17 in A2 vs 18 in A1.**

Predictions changed from A1: 12 of 50. Changes:

| Card | Actual | A1 predicted (grade) | A2 predicted (grade) | Nearest pool card |
|---|---|---|---|---|
| Passenger Ferry | Pump | ReplaySpell (miss) | Pump (exact) | bessie, the doctor's roadster |
| Iron Lad, Diverging Destiny | Main2 | MostProminentInHumanDeck (miss) | MakeUnblockable (miss) | merfolk sovereign |
| Embalmer's Tools | AtOppEOT | Always (partial) | AtOppEOT (exact) | hair-strung koto |
| Rampaging Geoderm | TgtAttacker | Always (miss) | Random (miss) | raging river |
| Etchings of the Chosen | MostProminentInComputerDeck | MostProminentInComputerDeck (exact) | Aristocrat (partial) | ahn-crop invader |
| Alora, Merry Thief | Pump | Always (partial) | Random (partial) | raging river |
| Lava Zombie | NeverBounceItself | PowerDmg (miss) | Pump (miss) | bloodtithe harvester |
| Circle of Affliction | MostProminentInHumanDeck | MostProminentInComputerDeck (partial) | Always (partial) | neyam shai murad |
| Subira, Tulzidi Caravanner | MakeUnblockable | MakeUnblockable (exact) | Bribe (partial) | mercenaries |
| Cavern Harpy | NeverBounceItself | MostProminentInHumanDeck (partial) | SacAndRetFromGrave (partial) | chthonian nightmare |
| Claim the Kingdom | Pump | Always (partial) | NeverBounceItself (partial) | bloodrage alpha |
| Bloodline Pretender | MostProminentInComputerDeck | MostProminentInComputerDeck (exact) | MostProminentInComputerDeckNonToken (partial) | molten echoes |

Remaining misses in A2 (15 cards):

| Card | Actual | A2 predicted | Nearest pool card |
|---|---|---|---|
| Iron Lad, Diverging Destiny | Main2 | MakeUnblockable | merfolk sovereign |
| Traveler's Cloak | ChosenLandwalk | MostProminentInHumanDeck | pentarch ward |
| Bill Ferny, Bree Swindler | Curse | Pump | anzrag, the quake-mole |
| Rampaging Geoderm | TgtAttacker | Random | raging river |
| Wash Out | MostExcessOpponentControls | MostProminentInHumanDeck | brave the elements |
| Lava Zombie | NeverBounceItself | Pump | bloodtithe harvester |
| Hidetsugu's Second Rite | OppAtTenLife | CantRegenerate | quenchable fire |
| Hikari, Twilight Guardian | IfNotBuffed | CloneBestCreature | hulkling, young avenger |
| Evolutionary Escalation | BoonCounterOnOppCreature | CloneBestCreature | irma, part-time mutant |
| Torment of Venom | PayUnlessCost | PowerDmg | beastie beatdown |
| Timely Reinforcements | PlayForSub | Fog | fog of war |
| Legion Vanguard | Aristocrat | Always | enter the unknown |
| Twinferno | SpellCopy | PowerDmg | brokers charm |
| Shuri, Wakandan Inventor | Pump | PowerDmg | mage duel |
| You Look Upon the Tarrasque | Fog | PowerDmg | brokers charm |

## Test set T: proposals that changed from A1: 17 of 50

| Card | A1 proposal | A2 proposal | Similarity | Nearest pool card |
|---|---|---|---|---|
| Lightning Berserker | PowerDmg | InfernoOfTheStarMounts | 0.48 | inferno of the star mounts |
| Blades of Velis Vel | SwitchPT | PowerDmg | 0.71 | berserk |
| Bombur, Gentle Dreamer | none needed | MostProminentOppControls | 0.56 | an-zerrin ruins |
| Zombie Musher | ReplaySpell | MoveCounter.IsCounterUser | 0.21 | spike hatcher |
| Halsin, Emerald Archdruid | Pump | PowerDmg | 0.42 | flourishing grapple |
| Crumble to Dust | Pump | BeforeCombat | 0.71 | back for more |
| Dragon Engine | PowerDmg | Berserk | 1.0 | wine of blood and iron |
| Split-Tail Miko | MakeUnblockable | Pump | 0.33 | nomad mythmaker |
| Tangle Kelp | Curse | NeverBounceItself | 0.59 | bloodrage alpha |
| Relentless Pursuit | none needed | Always | 0.33 | wandering archaic |
| Cogwork Archivist | Always | MostProminentInComputerDeckNonToken | 0.71 | belbe's portal |
| Frozen in Ice | Curse | Pump | 0.81 | reins of the vinesteed |
| Captain America, Living Legend | AtEOTIfNotAttacking | Curse | 0.71 | kudzu |
| Avalanche Caller | Pump | PowerDmg | 0.5 | flourishing grapple |
| Bind the Monster | Curse | NeverBounceItself | 0.59 | bloodrage alpha |
| Phyrexian Ironfoot | MostProminentInComputerDeck | AtOppEOT | 0.33 | basalt monolith |
| Death Ward | none needed | MoveCounter.IsCounterUser | 0.29 | spike hatcher |

## Remaining gaps
The eight rule gaps from A1 still stand (self-pump, Animate, Effect/static keyword grants, unlisted trigger modes, hand or graveyard to library, static conditions and aura stats, multi-target and sub-ability pumps, keyword-only signatures). A2 does not fix any of them: the nearest-neighbour proposal can name a value, but it cannot tell whether an ability is tagged. Tags on set T are still 0 of 50.

## Comparison with method B (mtgish)
Not done: `tools/concordia/ai_lab/CARD_TEST_B_MTGISH.md` is not in the repo after `git pull` (checked 00:10Z). I cannot confirm the 17-of-18 figure or compare per card. The B comparison needs that file's per-card rows (card, predicted value, grade).


## Re-run A3: keywords as their own features (K as full features)
User request (main session, 2026-10-22): each keyword (K: line) is its own feature (kw:flying style) instead of being down-weighted. Both versions are reported so the effect shows. Set C and set T unchanged; leave-one-out on C; method B results from `CARD_TEST_B_MTGISH.md` (per-card table, section C) used for the agreement check.

| Measure | A2: K down-weighted (0.4) | A3: K as full features (1.0) |
|---|---|---|
| Exact / partial / miss (C) | 17 / 18 / 15 | 18 / 17 / 15 |
| Exact-or-partial (C) | 35 of 50 | 35 of 50 |
| Strict exact (C) | 17 of 50 | 18 of 50 |
| Agreement with method B (where both give a value) | 17 cards | 18 cards |
| ...correct when they agree | 16 of 17 | 17 of 18 |
| Method B strict exact (C), for reference | 33 of 50 | 33 of 50 |

Control predictions that changed between A2 and A3: 2 of 50.

| Card | Actual | A2 (grade) | A3 (grade) |
|---|---|---|---|
| Iron Lad, Diverging Destiny | Main2 | MakeUnblockable (miss) | MostProminentInHumanDeck (miss) |
| Cavern Harpy | NeverBounceItself | SacAndRetFromGrave (partial) | NeverBounceItself (exact) |

Test-set proposals that changed between A2 and A3: 4 of 50.

| Card | A2 proposal | A3 proposal |
|---|---|---|
| Lightning Berserker | InfernoOfTheStarMounts | PowerDmg |
| Blades of Velis Vel | PowerDmg | SwitchPT |
| Zombie Musher | MoveCounter.IsCounterUser | ReplaySpell |
| Death Ward | MoveCounter.IsCounterUser | ExceptSelf |

Reading: making keywords full features gives the best agreement with method B, and it matches the main session's 17-of-18 figure (A3 agrees with B on 18 control cards and is right on 17). Exact-or-partial is the same (35 of 50) in both versions, so the change moves cards between exact and partial rather than adding hits. Keywords should therefore be tag features, as proposed. The A3 proposals are untested on the tag side: keyword-as-feature does not add any tag rule, so the eight rule gaps still stand.

## A3 (keyword compensation): three keyword variants
Keyword features: (a) down-weighted to 0.4 (A2 as before); (b) separate `kw:<name>` features at weight 1, uncompensated; (c) separate features with weight 1/n, where n is the number of keyword features on that card, so a card with three keywords gives each 1/3. Weighted Jaccard is computed per feature with each card's own weights (min over max). Non-keyword features weigh 1 in all three. Leave-one-out on set C.

| Variant | Exact (strict) | Partial | Miss | Exact-or-partial | Agree with B | Correct when agree | B strict exact (ref.) |
|---|---|---|---|---|---|---|---|
| (a) K down-weighted 0.4 | 17 of 50 | 18 | 15 | 35 of 50 | 17 | 16 of 17 | 33 of 50 |
| (b) K separate, uncompensated | 18 of 50 | 17 | 15 | 35 of 50 | 18 | 17 of 18 | 33 of 50 |
| (c) K separate, 1/n compensated | 18 of 50 | 17 | 15 | 35 of 50 | 18 | 17 of 18 | 33 of 50 |

Note: exact is strict (predicted value equals actual). Partial is shown separately and is not counted in strict exact. Exact-or-partial = strict exact + partial, which is 35 of 50 for (a) and 35 of 50 for (b) and (c).

Test-set proposals changing from (a):
- (b) vs (a): 4 of 50
- (c) vs (a): 3 of 50

### Per-card comparison with method B (control set C)
| Card | Actual | A (a) | A (c) | B (mtgish) | Both (c) and B agree | Right? |
|---|---|---|---|---|---|---|
| Passenger Ferry | Pump | Pump | Pump | Pump | yes | A(c) right |
| Unburied Earthcarver | AristocratCounters | PowerDmg | PowerDmg | Aristocrat | no | - |
| Omen of the Dead | BestOpportunity | BestOpportunity | BestOpportunity | AtOppEOT | no | A(c) right |
| Creative Outburst | AlwaysOnDiscard | AlwaysOnDiscard | AlwaysOnDiscard | AlwaysOnDiscard | yes | A(c) right |
| Iron Lad, Diverging Destiny | Main2 | MakeUnblockable | MakeUnblockable | Main2 | no | B right |
| Inner Fire | ManaRitual | ManaRitual | ManaRitual | ManaRitual | yes | A(c) right |
| Sentinel Totem | ExileGraveyards | ExileGraveyards | ExileGraveyards | ExileGraveyards | yes | A(c) right |
| Underfoot Underdogs | MakeUnblockable | MakeUnblockable | MakeUnblockable | MakeUnblockable | yes | A(c) right |
| Traveler's Cloak | ChosenLandwalk | MostProminentInHumanDeck | MostProminentInHumanDeck | MostProminentInHumanDeck | yes | - |
| Arrester's Zeal | Main1IfAble | PowerDmg | PowerDmg | Main1IfAble | no | B right |
| Bill Ferny, Bree Swindler | Curse | Pump | Pump | DonateTargetPerm | no | - |
| Touch of Invisibility | Pump | Fog | Fog | Pump | no | B right |
| Embalmer's Tools | AtOppEOT | AtOppEOT | AtOppEOT | AtOppEOT | yes | A(c) right |
| Rampaging Geoderm | TgtAttacker | Random | Random | PowerDmg | no | - |
| Etchings of the Chosen | MostProminentInComputerDeck | Aristocrat | Aristocrat | MostProminentInComputerDeck | no | B right |
| Terrific Team-Up | PowerDmg | PowerDmg | PowerDmg | PowerDmg | yes | A(c) right |
| Alora, Merry Thief | Pump | Random | Random | Pump | no | B right |
| Wash Out | MostExcessOpponentControls | MostProminentInHumanDeck | MostProminentInHumanDeck | MostProminentHumanCreatures | no | - |
| Auriok Replica | NeedsPrevention | NeedsPrevention | NeedsPrevention | NeedsPrevention | yes | A(c) right |
| Lava Zombie | NeverBounceItself | Pump | Pump | NeverBounceItself | no | B right |
| Circle of Affliction | MostProminentInHumanDeck | Always | Always | MostProminentInGame | no | - |
| Flaming Gambit | WorstCard | ReplaySpell | ReplaySpell | BurnCreatures | no | - |
| Subira, Tulzidi Caravanner | MakeUnblockable | Bribe | Bribe | MakeUnblockable | no | B right |
| Drain Life | XLifeDrain | XLifeDrain | XLifeDrain | XLifeDrain | yes | A(c) right |
| Ancestral Statue | NeverBounceItself | NeverBounceItself | NeverBounceItself | NeverBounceItself | yes | A(c) right |
| Cavern Harpy | NeverBounceItself | SacAndRetFromGrave | NeverBounceItself | NeverBounceItself | yes | A(c) right |
| Claim the Kingdom | Pump | NeverBounceItself | NeverBounceItself | AtOppEOT | no | - |
| Hidetsugu's Second Rite | OppAtTenLife | CantRegenerate | CantRegenerate | ChainOfSmog | no | - |
| Hikari, Twilight Guardian | IfNotBuffed | CloneBestCreature | CloneBestCreature | Always | no | - |
| Recoup | ReplaySpell | WorstCard | WorstCard | ReplaySpell | no | B right |
| Millstone | AtOppEOT | AtOppEOT | AtOppEOT | AtOppEOT | yes | A(c) right |
| Pilgrim of Justice | NeedsPrevention | NeedsPrevention | NeedsPrevention | NeedsPrevention | yes | A(c) right |
| Evolutionary Escalation | BoonCounterOnOppCreature | CloneBestCreature | CloneBestCreature | Always, Fight | no | - |
| Torment of Venom | PayUnlessCost | PowerDmg | PowerDmg | PayUnlessCost | no | B right |
| Zoyowa Lava-Tongue | PayUnlessCost | PayUnlessCost | PayUnlessCost | PayUnlessCost | yes | A(c) right |
| Timely Reinforcements | PlayForSub | Fog | Fog | DiscardUncastableAndExcess | no | - |
| Bloodline Pretender | MostProminentInComputerDeck | MostProminentInComputerDeckNonToken | MostProminentInComputerDeckNonToken | MostProminentInComputerDeck | no | B right |
| Legion Vanguard | Aristocrat | Always | Always | AristocratCounters | no | - |
| Aquatic Incursion | MakeUnblockable | MakeUnblockable | MakeUnblockable | MakeUnblockable | yes | A(c) right |
| Twinferno | SpellCopy | PowerDmg | PowerDmg | Berserk | no | - |
| Shuri, Wakandan Inventor | Pump | PowerDmg | PowerDmg | IfDefinedCreatureIsBetter | no | - |
| Addle | MostProminentInHumanDeck | MostProminentHumanCreatures | MostProminentHumanCreatures | MostProminentInHumanDeck | no | B right |
| Prism Ring | MostProminentInComputerDeck | MostProminentInGame | MostProminentInGame | MostProminentInComputerDeck | no | B right |
| Ant-Man's Army | FoodOrTreasure | NeverBounceItself | NeverBounceItself | FoodOrTreasure | no | B right |
| Omen of the Sea | BestOpportunity | BestOpportunity | BestOpportunity | BestOpportunity | yes | A(c) right |
| You Look Upon the Tarrasque | Fog | PowerDmg | PowerDmg | Fight | no | - |
| Ambrosia Whiteheart | BounceOwnTrigger | ReplaySpell | ReplaySpell | BounceOwnTrigger | no | B right |
| Stronghold Discipline | AllPlayerLoseLife | MostProminentComputerControls | MostProminentComputerControls | AllPlayerLoseLife | no | B right |
| Cutthroat Centurion | Aristocrat | Aristocrat | Aristocrat | Aristocrat | yes | A(c) right |
| Haunting Apparition | Curse | MostProminentInHumanDeck | MostProminentInHumanDeck | Curse | no | B right |

Reading: the keyword variants change only the exact count by one or two cards, and the agreement with B stays high. The compensated variant (c) gives the same figures as the uncompensated variant (b) on this set. The B table in `CARD_TEST_B_MTGISH.md` is the reference for the per-card rows above.

## A3 headline: variant (b), every keyword a full-weight feature
Decision (main session, 2026-10-22): variant (b) is the method. Every keyword is its own full-weight feature `kw:<name>`, no down-weighting, no 1/n compensation. Keyword names keep the parameter where it carries meaning: `Protection from red` -> `protection:red`; `Enchant creature` -> `enchant:creature`; `Equip:2` -> `equip`; `Ward:2` -> `ward` (the number is a cost, not a name); `Snow landwalk` -> `snow_landwalk`. The split is: text after `from` for protection, text after `Enchant` for enchant, otherwise the text before the first `:`, `(` or a digit, lower case, spaces as underscores. A compound such as `Protection from white and from black` becomes `protection:white_and_from_black`, which is a known limit.

| Variant | Strict exact | Partial | Miss | Exact-or-partial | Agree with B | Correct when agree |
|---|---|---|---|---|---|---|
| HEADLINE (b) K separate, uncompensated, full keyword names | 18 of 50 | 17 | 15 | 35 of 50 | 18 | 17 of 18 |
| reference (a) K down-weighted 0.4 | 17 of 50 | 18 | 15 | 35 of 50 | 17 | 16 of 17 |
| reference (c) K separate, 1/n compensated | 18 of 50 | 17 | 15 | 35 of 50 | 18 | 17 of 18 |

Headline: strict exact 18 of 50, agreement with method B on 18 cards, right on 17 of them. Method B strict exact: 33 of 50.

Keyword-name change (first word -> full name, variant b): 0 of 50 control predictions changed.

Test-set proposals changed by the keyword-name split: 0 of 50.

Note: the earlier A3 section (first-word names) stays as written, for the record. Variant (b) from that section is the same method with the first-word names; the headline above replaces it.

## A3b: compound keywords, qualifiers and numbers (supersedes the A3 headline split rule)
Rule (main session, 2026-10-22): the keyword feature is the base word only (`kw:protection`, `kw:enchant`, `kw:equip`, `kw:ward`, `kw:landwalk`, `kw:flashback` ...). Qualifiers become separate features: colours -> `color:<name>`; card or creature types -> `type:<name>`; `from everything` -> `qualifier:everything`; landwalk land types -> `landtype:<X>`; the `Snow` landwalk gives `supertype:snow` (a decision of mine: snow is a supertype, not one of the five H45 land types). Numbers tied to a keyword become `num:<n>`; colour symbols in a keyword cost become `color:<name>`. Variant (b) throughout: all features weight 1.

### Compound and qualified keyword lines found in C and T, and the features each produced
| Set | Card | Keyword line | Base feature | Qualifier features | Number and cost features |
|---|---|---|---|---|---|
| C | Traveler's Cloak | Enchant:Creature | kw:enchant | type:creature | - |
| C | Traveler's Cloak | ETBReplacement:Other:ChooseLT | kw:etbreplacement | qualifier:choose_land_type | - |
| C | Etchings of the Chosen | ETBReplacement:Other:ChooseCT | kw:etbreplacement | qualifier:choose_creature_type | - |
| C | Circle of Affliction | ETBReplacement:Other:ChooseColor | kw:etbreplacement | qualifier:choose_color | - |
| C | Pilgrim of Justice | Protection from red | kw:protection | color:red | - |
| C | Bloodline Pretender | ETBReplacement:Other:ChooseCT | kw:etbreplacement | qualifier:choose_creature_type | - |
| C | Prism Ring | ETBReplacement:Other:ChooseColor | kw:etbreplacement | qualifier:choose_color | - |
| C | Haunting Apparition | ETBReplacement:Other:ChooseP | kw:etbreplacement | qualifier:choose_player | - |
| C | Passenger Ferry | Crew:2 | kw:crew | - | num:2 |
| C | Flaming Gambit | Flashback:X R R | kw:flashback | - | num:x, color:red (twice, set) |
| C | Recoup | Flashback:3 R | kw:flashback | - | num:3, color:red |
| C | Abandon Reason | Madness:1 R | kw:madness | - | num:1, color:red |
| T | Mask of Law and Grace | Enchant:Creature | kw:enchant | type:creature | - |
| T | Lignify | Enchant:Creature | kw:enchant | type:creature | - |
| T | Defensive Stance | Enchant:Creature | kw:enchant | type:creature | - |
| T | Rime Transfusion | Enchant:Creature | kw:enchant | type:creature | - |
| T | Tangle Kelp | Enchant:Creature | kw:enchant | type:creature | - |
| T | Frozen in Ice | Enchant:Creature | kw:enchant | type:creature | - |
| T | Bind the Monster | Enchant:Creature | kw:enchant | type:creature | - |
| T | Zombie Musher | Landwalk:Land.Snow:snow Land | kw:landwalk | supertype:snow | - |
| T | Lightning Berserker | Dash:R | kw:dash | - | color:red |

Compound forms: none of the 100 cards has `Protection from X and from Y` or `Enchant X or Y`. The only multi-part lines are `ETBReplacement:Other:Choose*` (code suffix mapped to a qualifier) and `Landwalk:Land.Snow:snow Land`. Two keyword forms in the sets carry a non-mana or unusual cost: none found (Crew, Madness and Flashback costs are mana or a number).

### Re-score (variant b, leave-one-out on C, full set T)
| Configuration | Strict exact | Partial | Miss | Exact-or-partial | Agree with B | Correct when agree |
|---|---|---|---|---|---|---|
| Previous headline: keyword base word only | 18 of 50 | 17 | 15 | 35 of 50 | 18 | 17 of 18 |
| (1) keyword + qualifiers (A3b) | 20 of 50 | 15 | 15 | 35 of 50 | 20 | 19 of 20 |
| (2) (1) + numbers and colour costs (A3b) | 20 of 50 | 15 | 15 | 35 of 50 | 20 | 19 of 20 |

Changes:
- Previous headline to (1): 3 control predictions changed (Iron Lad -> DoubleLife, Etchings of the Chosen -> MostProminentInComputerDeck, Haunting Apparition -> Curse); 4 test proposals changed (Zombie Musher, Tangle Kelp, Cogwork Archivist, Bind the Monster). Strict exact went up by 2 and the agreement with method B went up by 2.
- (1) to (2): 0 control predictions changed; 1 test proposal changed (Lightning Berserker: PowerDmg -> WorstCard). The colour feature from `Dash:R` moves that proposal. I have not checked which value is right for Lightning Berserker, so this change is not a gain by itself.
- Numbers and costs have no measurable effect on this set: the only numbered keywords are Crew, Flashback and Madness, and their numbers are shared by few cards.

Caveats: the qualifier gains are on 50 control cards, and most of them come from the 6 choose-type keyword lines. The effect is small and within the noise of one card per change. Method B's strict exact is still 33 of 50; the comparison above uses the same B table.

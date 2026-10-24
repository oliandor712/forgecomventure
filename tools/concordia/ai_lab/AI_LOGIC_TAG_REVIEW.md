# AI logic tag review (forge-ai-lab clone, Claude 2 order 2026-10-22)

Research only. Read from `origin/cd/claude2` (STARTER_TAGS.toon 353 cards, tag_verify.py, tag_run.py, report). No forge-ai edits, nothing pushed. File:line refs are forge-ai as on campaign-design.
**Unverified / limits:** (a) I read the toon and scripts, not the diff itself. The 83 tags on 71 cards = 61 tags on 54 cards (cross-check) + 22 ai_logic tags (Claude 2, 2026-10-22); both figures are right. (b) Starter cards only (353). (c) No games run; "what forge-ai does" is from source.

## 1 Review

| # | Finding | Evidence | Severity |
|---|---|---|---|
| 1 | `sacrifice_outlet` is wrong on self-sacrifice | 20 cards carry it; 14 of them also have `cost_sacrifice_target:self` (Mind Stone, Sakura-Tribe Elder, Yavimaya Elder, Thrashing Brontodon, Ember Hauler...). Self-sac is not an outlet. Land fix covered only lands | high. **Resolved 2026-10-22** in the regenerated run on cd/claude2: 6 cards left (Victimize, Nefarox, Ravenous Baloth, Bosco, Siege-Gang Commander, Daretti), 0 with `cost_sacrifice_target:self`; I re-checked the toon. Query 5 should now be a hit |
| 2 | `ai_logic` value is lowercased and not tied to an ability | `snake()` in tag_verify.py:12 and :190-191. `atoppeot`, `makeunblockable` can't be grepped in code; case info lost. Syr Konrad's AtOppEOT sits on the mill ability only, but the tag sits on the card | medium |
| 3 | Compound value `Always/Fight` split | Hunt the Weak shows `ai_logic:always ai_logic:fight`. Regex `[A-Za-z0-9_]+` stops at `/`, so one of the two probably comes from a second AILogic line; check the script. If it is one string, the split is fine; if two abilities, tag is per card not per ability | low |
| 4 | Missing implied tags for logic that exists | Control Magic `gaincontrol`: no control-steal tag. Incinerate `cantregenerate`: no no-regenerate tag. Rogue's Passage `makeunblockable`: no unblockable-grant tag. Exhaustion `keepoppcreatslandstapped`: no skip-untap tag. Pacifism `curse`: has `restrict`, ok | medium |
| 5 | `tutor` on Herald's Horn (flagged by the report, "extra? tutor") | Horn is "look at top card, reveal creature, put in hand" (upkeep); has `trigger:upkeep` and `ai_logic:mostprominentincomputerdecknontoken`. Tutor is wrong, library-top look is right | medium |
| 6 | `Scry` accuracy | Glimmer of Genius gets `scry` and `selection` (good; since 2026-10-23 the tag is `scry_count:N`). Titan's Strength, Sheltering Light, Serum Visionary also match it: all have scry in the script, fine | ok |
| 7 | Flags (61) | 36 of 50 shown are "cost:mana from mtgish only". Likely mtgish counts a printed mana cost as a cost clause. Treat as noise, not tag errors | low |
| 8 | `Always` carries no information | Used by 3 starter cards (Vines, Explore, Hunt) and 192 cards in the whole card folder. It is a "play it whenever legal" override (SpellAbilityAi.java:196, AiController.java:1105 min-1 discard). Fine as a tag, but it does not describe the card | low |

No misreadings of forge-ai found in the 22 `ai_logic` mappings: each tag name matches an `AILogic$` value in the script (checked all 16 distinct values below).

## 2 Focus analysis: AILogic on the starter cards (21 cards, 16 values)

Kind: **T** timing/phase, **G** targeting/choice, **C** cost/mana, **E** effect-specific.

| Value | n | Cards | forge-ai handling (file:line) | Kind | Ability tags it implies | Contradicts / missing |
|---|---|---|---|---|---|---|
| Pump | 2 | Unholy Strength, Rancor | AttachAi.java:1456 (aura gets pump-style target preference); ChooseGenericAi.java:28 | G | `type:aura`, `target_type:creature` | none |
| PowerDmg | 2 | Bite Down, Ram Through | DamageDealAi.java:504 (may retarget player), PumpAi.java:129, CountersPutAi.java:338 | G | `damage`, one-sided fight | tags lack "one-sided fight" |
| Always | 3 | Vines, Explore, Hunt the Weak | SpellAbilityAi.java:196, AiController.java:1105 | T/override | none | no tag explains why forced |
| Curse | 2 | Curse of Opulence, Pacifism | AttachAi.java:420 / 1456 (targets opponent), ComputerUtil.java:1975 | G | `type:aura`, `target_scope:opp_control` | Curse of Opulence targets a player (`target_type:player`): ok |
| AtOppEOT | 1 | Syr Konrad | SpellAbilityAi.java:149; ManaAi.java:77 (adds mana-burn check) | T | `cost:mana`, repeatable ability | none; 68 cards use it overall |
| FoodOrTreasure | 1 | Tireless Provisioner | ChooseGenericAi.java:280 (life in danger -> first, else second option) | G (modal choice) | `token_type:food`, `token_type:treasure` | none |
| AtEOTIfNotAttacking | 1 | Thrashing Brontodon | DestroyAi.java:75 (end of turn, no attack made) | T | `cost:sacrifice`, `remove:destroy` | none |
| Fight | 1 | Epic Confrontation | PumpAi.java:129/361, CountersPutAi.java:338 | G | `fight`, `pump_single` | none |
| Always/Fight | 1 | Hunt the Weak | as Always + Fight | T+G | `fight`, `counter:p1p1` | see 1.3 |
| CantRegenerate | 1 | Incinerate | EffectAi.java:396; ComputerUtil.java:1751 | E | `burn` | no regen tag |
| MakeUnblockable | 1 | Rogue's Passage | EffectAi.java:314 (not if opponents have no creatures) | G | `cost:mana`, `target_type:creature` | no unblockable tag |
| ManaRitual | 1 | Apprentice Wizard | ManaAi.java:38, 74, 122 (main phases only); ComputerUtil.java:3098 | T/C | `mana_source`, `cost:tap` | none |
| MostProminentInComputerDeckNonToken | 1 | Herald's Horn | ComputerUtil.java:2506; PlayerControllerAi.java:1552 (game side also GameAction.java:2497) | G (choose a type) | `cost_reduce` | `tutor` wrong |
| GainControl | 1 | Control Magic | AiController.java:2273 (multiplayer guard), ComputerUtil.java:1955 | G | `type:aura` | no steal tag |
| BestOpportunity | 1 | Glimmer of Genius | ScryAi.java:96, :111 | T | `scry`, `draw` | none; see patch 014 |
| KeepOppCreatsLandsTapped | 1 | Exhaustion | EffectAi.java:53 | G | opponent target | no skip-untap tag |
| BounceOnce | 1 | Felidar Guardian | ChangeZoneAi.java:1003 | E | `put_onto_battlefield`, `remove:exile` | none |

Counts: timing 7 values, targeting/choice 8, cost/mana 1, effect-specific 2.
Whole-card-folder frequency (339 distinct values): Always 192, PowerDmg 163, MostProminentInComputerDeck 85, Pump 76, AtOppEOT 68, NeedsPrevention 65, Curse 64, Fight 63, MakeUnblockable 56.

**Cards whose ability tags suggest an AILogic that exists or is missing**
- Scry instants: only Glimmer of Genius is a scry instant in the starter set and it has BestOpportunity. The six instants in patch 014 (Opt, Deliberate, Joint Exploration, Delightful Discovery, Graven Lore, Demon's Due) are not in the starters; a `cardtype:instant scry draw` query over the full list finds them (11 instant scry cards, 2 tagged before, 6 candidates, 3 excluded). Query hits.
- 33 starter instants target a creature, only 1 has an `ai_logic`: the removal spells rely on defaults. Tags don't show whether a timing logic would help.
- 11 starter instants draw; 1 has an `ai_logic`. Thrill of Possibility, Big Score etc. have no timing logic, so they use the default roll.

## 3 Usefulness for AI patch development

Five worked queries (starter tags, 353 cards):

| # | Tag query | Result | Candidate patch | Hit/miss vs what I know |
|---|---|---|---|---|
| 1 | `cardtype:instant` + `scry` | 1 (starter set); on full list would find the 11 | tag BestOpportunity on 6 (patch 014) | **hit**: the tags separate the exclusions only with an extra `damage` tag |
| 2 | `cardtype:instant` + `draw` | 11, 1 with ai_logic | timing logic for draw instants | partial: includes Bladebrand, Return of the Wildspeaker (not pure draw) |
| 3 | `cardtype:instant` + `target_type:creature` + `damage` | 5, 2 with ai_logic (PowerDmg) | none needed | **hit**: PowerDmg cards found |
| 4 | `fight` | 7, 2 with ai_logic | check Prey Upon, Pounce, Somberwald Stag have Fight | **hit**: 5 fight cards lack the logic; real candidate list |
| 5 | `sacrifice_outlet` | 20 (6 after the regenerated run) | outlet-AI | **miss** on the first run (14 self-sacrifice, finding 1.1); the 6 left are real outlets, so now a hit |

Also: `trigger:upkeep` found 5 cards (Phyrexian Arena etc.), correct; `type:aura` found all 5 starter auras, all with ai_logic (so the tag set already covers it).

**Tags missing for AI work**
- Timing: instant-speed use window (end of turn, in response, before blockers); `kw:flash` exists but no "best cast phase".
- Targeting: "opponent's best creature", "own creature only", one-sided fight vs mutual fight.
- Cost: self-sacrifice vs outlet (see 1.1); `cost:life`.
- Mana sink: repeatable mana use (Syr Konrad, Rogue's Passage) vs one-shot.
- Combat role: unblockable grant, no-regenerate, skip-untap, control steal.

**Noise:** 421 distinct tags on 353 cards, 166 appear once (39%). Only `cardtype:creature` (200) and `target_count:one` (127) exceed 30%. Cost tags ("cost:mana from mtgish only") make most flags.

**Verdict: partly useful.**
- Good for selecting candidates by *effect shape* (queries 1, 3, 4): 3 of 5 queries returned usable lists without reading scripts.
- Weak for *timing and targeting*, which is where AI patches mostly live; no tag expresses them, and `ai_logic:<name>` only repeats what the script already says.
- One wrong tag (`sacrifice_outlet`) made query 5 useless; fixed in the regenerated run (20 -> 6). With it, 4 of 5 queries are usable.

**What the full-cardlist run should add for the AI lab**
1. Keep original case and the ability the logic sits on: `ai_logic:AtOppEOT@a2`.
2. Tags for timing: `ai_timing:instant|eot|main`, and for targeting: `ai_target:best_creature|opp_only`.
3. ~~Split `sacrifice_outlet` from self-sacrifice~~ done in the regenerated run.
4. The tags noted in section 1.4 (steal, unblockable, no_regen, skip_untap).
5. A per-tag count over the full list so a query's hit set is known (e.g. instant+scry = 11).
6. Separate flag files for "mtgish cost only" so they don't bury real disagreements.

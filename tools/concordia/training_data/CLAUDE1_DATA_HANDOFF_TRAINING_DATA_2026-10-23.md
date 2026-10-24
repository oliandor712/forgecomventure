# TRAINING DATA: Concordia project data handoff (Claude 1 session)

> **TRAINING DATA.** This file is a knowledge snapshot for use as training/reference data. It is not an operating brief, not a task list and not authority to push, edit live decks, or change game code.
>
> - Date: 2026-10-23. Source: the Claude 1 main session. Branch: `campaign-design`.
> - Scope: project data and knowledge only (rules, tag system, reverse-check results, Forge AI findings, references, inventory, pitfalls, open decisions).
> - Excluded on purpose: anything about building or managing agents (agent definitions, briefs, routing, approval protocols, session/shift/mailbox mechanics).
> - This file is new. It replaces and edits no existing handoff (`tools/agents/HANDOVER.md`, `tools/concordia/ai_lab/HANDOFF.md`, `tools/concordia/balance_lab/HANDOFF.md`, `tools/concordia/deckgen/HANDOFF_DECKBUILDER.md` are untouched).
> - Reliability: numbers below were copied from repo reports written in this session; where a figure was not re-run it is under "Unverified".

## 1. Project in one paragraph
Concordia is a Pokemon-like Commander campaign plane for Forge Adventure (fork `oliandor712/forgecomventure`, integration branch `campaign-design`, no PRs, never force-push). The user tests on Windows and decides what goes into the game. Game data: `forge-gui/res/adventure/Concordia/` (decks `tier1..5`, `starter`, `world/enemies.json`, `maps/`, `config.json`; staged tier 1 set `staging_t1_fresh/` is not live). Design docs: `docs/Adventure/Campaign/` (OVERWORLD, ENCOUNTER_TIERS, AI_CHANGES_APPROVAL, IDEAS_BACKLOG ...). Tools: `tools/concordia/{deckgen,sim,suite,balance_lab,ai_lab}`. Do not edit `forge-core`, `forge-game`, `forge-ai`; AI ideas live as patch files in `tools/concordia/ai_lab/`. A rule in `tools/agents/human_logic.toon` beats a metric.

## 2. Tag system
- Run: `deckgen/tag_run.py starter` (353 starter cards) or `tag_run.py card "Name"`. Outputs `tags/STARTER_TAGS.toon`, generated `tags/TAG_REFERENCE.md` (157 families), `tags/TAG_LEGEND.md`, `tags/ABILITY_TWINS.json` (per-Oracle-line twin index).
- Record layout: `typing:` (supertypes, cardtype, subtypes, land types), `tags:` (rules tags the blind reader sees), `ai_tags:` (segregated; reader never sees them). Groups k1/c0/c1/c1.2. Links: requires, provides, lasts, receives, produces, filters, pairs_with, conditional_on.
- Source order of trust: card script > mtgish (i5jb/mtgish, second-opinion parser, drops some abilities) > Forge AI (AILogic$). Keywords resolve through the keyword reference and the Comprehensive Rules (2026-08-07) in `tools/agents/reference/`.
- Fixes this session: target_scope:any is not tagged (H66); controller:owner only when Oracle says "under its/their owner's control", else controller:you (H67; 21 starter cards changed); bare keyword AI tags dropped on pure granters (H68; 18 tags on 17 cards); cost:mana dropped when cost_mana:<symbols> present (H69); absent-equal check in the redundancy report.
- New tag `additional_cost` (user pre-approved 2026-10-23): spells whose `A:SP$` Cost$ has a non-mana part (Discard<>, Sac<> ...); 6 starter cards (Big Score, Thrill of Possibility, Harrow ...).
- Approved families 2026-10-23: cost_mana, return, unless_cost_amount, investigate, monarch, bolster. All earlier families approved 2026-10-22. New tags are logged in `tags/NEW_TAGS_FOR_APPROVAL.md` and count as proposed until the user approves.
- Open tag gaps: Elite Scaleguard tap effect, Scorch Spitter damage target, Daretti emblem trigger, Fact or Fiction pile outcome.

## 3. Reverse tag check (blind reader)
- Method: a reader sees only a card's tags and writes the ability text; scorer = 0.4 tf-idf + 0.4 concept F1 + 0.2 number F1. Reader noise about SD 0.019 per card. History: round 1 0.777 to round 8 0.926.
- Reader-grammar project (`tagcheck/READER_GRAMMAR_PLAN.md`): goals in order (1) same output from identical tags, (2) reads like a Magic card, (3) accuracy not lost.
- Metrics: V1 exact agreement, V2 token F1, V3 structure-signature agreement, V4 score SD, S1 style conformance, A accuracy guard. Targets: V3 >= 98%, V1 >= 85%, V2 >= 0.95, V4 SD <= 0.010, S1 >= 98%, A >= 0.916.
- Baseline r12 (353 cards, 3 readers): V1 61.5%, V2 0.984, V3 87.9%, V4 SD 0.0077, S1 95.3%, A 0.932.
- Phase 3 A/B (`R12_GRAMMAR_AB.md`): C2 (full grammar + per-ability records) V1 0.776, V2 0.991, V3 0.968, V4 SD 0.0032, S1 0.971, A 0.928; C3 (short grammar) V1 0.655, V3 0.874, A 0.924.
- Grammar v2 (`tags/READER_GRAMMAR.md` v2, G11-G16): 105 cards, C2 v2 V1 0.762, V2 0.990, V3 0.933 (target missed), V4 SD 0.0054, S1 0.990, A 0.938. Slim layout (`R16_SLIM_LAYOUT.md`, about 37% fewer tokens per set): V1 0.810, V3 0.933, S1 0.994, A 0.937.
- Reader model effect on 24 cards (C0): Sonnet/high V1 0.833 V3 1.00; Sonnet/medium V1 0.708 V3 0.958; Haiku/low V1 0.542 V3 0.750. Same-model noise floor not measured.
- Main V1 limit: placeholders in 88 of 348 cards (25%). `{cost}` is structural (mana amounts are not tags); `{effect}`/`{filter}` come from triggers lacking the triggering card type, missing negation in trigger_filter, and "equal to previous result" amounts (`PLACEHOLDER_TRIAGE.md`).
- Known ambiguities: `controller:you` wording for graveyard puts vs tutor puts; mill without amount; missing-tag placeholders.
- Plan next: P5 hold-out (`holdout_cards.txt`, 150 cards), P6 human check, P7 freeze, P8 deterministic (executable) renderer, recommended by the audit (`TAG_RUN_AUDIT_AND_PLAN.md`).

## 4. Forge AI findings (`tools/concordia/ai_lab/`)
- 4 AI profiles (Default, Reckless, Cautious, Experimental), 122 AiProps, about 1,814 cards with AILogic$; AI reads its own deck via setupAutoProfile (`SHIPPED_AI_PROFILES_AND_READS.md`).
- Card-logic test (`ai_lab/archive_20261023/CARD_LOGIC_TEST_REPORT.md`): mtgish-derived about 33/50 versus Forge-syntax variants 16-20/50.
- Patches 005 v4 (SwitchPT; must allow the switch when the opponent has no possible blockers, H64), 014, 015: all unticked in `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`, none applied. Volume runs: 9 runs of 40 games per arm, about +-11 pt noise; patch 005 v4 volume runs never completed (`results/ab/r005v4sa/` partial junk).
- Easy-fix feasibility: `AI_EASY_FIXES_FEASIBILITY.md`. Tag review: `AI_LOGIC_TAG_REVIEW.md`.

## 5. Balance and deck rules (summary)
Player win-rate targets vs NPCs: tiers 1-2 70%, tiers 3-5 50% (H29). Tier 1 power 16-18, tier 2 25-30, starters about 27. Equal life in all sims, no life bonuses, 30-40 card test decks, 25 games per AI deck and 40 per starter. Full rule text is below in section 8.

## 6. Data inventory
deckgen 146 files / 16.4 MB; ai_lab 490 / 9.0 MB; balance_lab 23; Campaign docs 20; agents reference 3 files / 3.6 MB (CR, keyword reference, reminder texts); game data 6360 files / 148 MB. Reader run dirs are outside the repo (archived in `tagcheck/archive_20261023/tagcheck_runs.tgz`); run log `tagcheck/RUN_LOG.jsonl`.

## 7. Pitfalls
- Blind tests leak if the reader sees names, Oracle text or scripts.
- Python set ordering gives nondeterministic one-line diffs in generated files (STARTER_TAGS); treat as noise.
- `consistency.py compare` overwrites `GRAMMAR_BASELINE.md`; restore unless intended.
- A rejected tool call can still write files; check `git status`.
- Generated files are regenerated, never hand-merged.
- Tag sha1 changes (e.g. after `additional_cost`) make earlier runs non-comparable on affected cards.
- Do not print large JSON key lists; query narrowly.

## 8. User rules verbatim (`tools/agents/human_logic.toon`, all rows except H63 which concerns agent routing)
Columns: id | area | rule | since | status | where.

```
  H01|curve|A zone's stage locks at the player's first fight there from Seals held (0-1 stage 1, 2-3 stage 2, 4-5 stage 3)|2026-10-20|applied|TierLock.java and config tierLock
  H02|curve|Wild creatures, random-dungeon enemies, pass keepers, grove guardians and Wardens are mono-color. Trainers are 1-2 colors at stage 1 then 2-3|2026-10-20|applied|build_color_zone.py
  H03|curve|Random dungeons draw from the wild encounter pool, never from keepers or guardians|2026-10-20|applied|build_color_zone.py
  H04|curve|Wild creatures sit in the lowest band of their stage. Stage 2 wild uses the top of tier 2 and does not jump to tier 3|2026-10-20|applied|WILD table
  H05|curve|Deck power rises in order wild then trainer then keeper then guardian then Warden at every stage|2026-10-20|applied|build_color_zone.py windows
  H06|data|Use existing assets only. Ignore prices everywhere|2026-10-20|applied|all tools
  H07|power|Card power counts EDHREC popularity. Staples are a category (popular, low standalone impact) and are tracked apart from Game Changers|2026-10-20|applied|deck_tier.py and staples.py
  H08|builder|Raise the tier 1-2 floor. T1 decks 16-18 power and T2 25-30 rather than as weak as the builder can make them|2026-10-21|applied|build.py FLOOR CEILING T1_TARGET
  H09|builder|Push staples at tiers 1-2; at tier 1 they may be commons or uncommons (user, 2026-10-21); tier 2 stays uncommon printings only until the user says otherwise|2026-10-21|applied|build.py UNCOMMON_STAPLE_BONUS; tier1_rules.py STAPLE_PRINTINGS
  H10|builder|Add near-staple nonbasic lands and cheap mana rocks from budget decks (precons and low-rarity lists) inside the tier's ramp caps|2026-10-21|applied|budget_lands.py
  H11|builder|Loosen tier 1 creature requirements: 30-36 creatures with more instants, sorceries, artifacts and enchantments. H11 wins over the archetype creature windows (user, 2026-10-21): the archetype preference is only a build target inside the band. Low subarchetypes (low-control, low-aggro, low-tribal, low-tokens) take the band from 26 up to 36 minus their shift (user, 2026-10-21)|2026-10-21|applied|archetype_rules.creature_check; build.py creature_band and H11 check
  H12|builder|Card type mix follows the color's nature. A blue spells deck should not run 37 creatures|2026-10-21|partly|blue starter fixed, AI decks not yet audited by color
  H13|builder|Synergy beats score. A low-scoring card that works with the commander's ability is rated slightly above a stronger card that does not|2026-10-21|partly|starter alternates only (variants.py SYN), not the 200 AI decks
  H14|builder|Cost-reduction commanders such as Goreclaw want low-score creatures with enter-the-battlefield abilities at the reduced power threshold|2026-10-21|partly|SYN counts power 4+ creatures and gives a bonus for enter-the-battlefield text
  H15|builder|Commanders with a power threshold such as Gwenna need more creatures at that power. Add power 5 options|2026-10-21|applied|SYN for Gwenna; 63 green power 5+ creatures in pool; approved in chat 2026-10-21
  H16|builder|Life gain commanders such as Nazar want X damage and gain X life effects counted as alternate removal|2026-10-21|applied|variants.py DRAIN regex; approved in chat 2026-10-21; takes effect at next variant or starter regeneration
  H17|commanders|A commander must use its own ability in its deck. Judge by how many deck cards work with it and change the ones that do not|2026-10-21|applied|review of the ten starters (Tarox, Ben-Ben, Inga replaced)
  H18|commanders|Double the deck pool with variants led by alternate or budget commanders. Change 5-8 cards plus the commander|2026-10-21|applied|variants.py and variants.json
  H19|starters|Starters aim for deck power 27, the middle of tier 2|2026-10-21|applied|starter_tune.py
  H20|starters|Each color has two starters with different commanders and 5-8 different cards. Both commanders start unlocked|2026-10-21|applied|variants.py --starters and hall_roster.py
  H22|starters|Each starter version holds the other's swap cards in its sideboard|2026-10-21|applied|variants.py set_sideboard
  H23|testing|Every simulation uses equal life on both sides with no exceptions|2026-10-20|applied|run_batch.py
  H24|testing|Life bonuses are eliminated as an encounter bonus. Test only small card bonuses such as a free land or one-drop against the premade ones|2026-10-20|applied|run_batch.py BONUSES
  H25|testing|Shrink test decks to 30-40 cards so tested cards are drawn. Use 40 to limit decking and fill with basic lands when a restriction applies|2026-10-20|applied|minideck.py
  H26|testing|Regenerate the shrunk test decks whenever the tier decks change|2026-10-21|applied|ai_lab/decks
  H27|testing|Split starter tests 50/50 between each color's two versions|2026-10-21|applied|run_batch.py STARTER_EPOCH
  H28|testing|Target is 25 games per AI deck and 40 per starter deck (user, 2026-10-21). Clear results need about 40 games per deck for a 70-30 deck and about 25 matched sets per bonus for a 25-point effect and about 600 games for a seat edge|2026-10-21|applied|balance lab brief
  H29|pc-npc|The player's win rate against NPC enemies: tiers 1-2 target 70%, tiers 3-5 target 50% (user, pc_win_rate, 2026-10-21; replaces the earlier flat 70% at every stage)|2026-10-21|partly|make_report.py PC_TARGET; balance lab reports each stage against its target
  H30|pc-npc|Starting bonuses for enemies stay small and never touch life. Judge them by measured win rate against the starters|2026-10-20|applied|balance lab
  H31|commanders|Read 'for each X you control', 'per X Y' and '+1/+1 for each' as one pattern: count of Y is a synergy and a potential new stat block (Adelbert: Equipment count; Dwynen: attacking Elves)|2026-10-21|open|ability_tags.py commander readers
  H32|commanders|Tribal abilities (other Elves/Merfolk/Pirates get a bonus or trigger) count the tribe's numbers on the battlefield. Dwynen's life gain is potential lifegain per turn from the tribe count|2026-10-21|open|ability_tags.py commander readers
  H33|commanders|Trigger wording is a synergy tag: 'when X attacks' is a combat trigger, 'when X enters' is an enter-the-battlefield synergy (self bounce also counts as etb), 'whenever you discard' is discard synergy, 'modified' means equipment, aura and counter synergy, 'sacrifice' and free recursion are sacrifice synergy|2026-10-21|open|ability_tags.py commander readers
  H34|commanders|Exile the top card and you may play it is low-draw interaction. Exiling an opponent's library is low removal. Opponent interaction on a commander (attack tax, spell tax, deathtouch) is control synergy; paying mana to attack is curve disruption|2026-10-21|open|ability_tags.py and H17 check
  H35|commanders|Weigh poison counters as 4 life damage each. Sneak is two differently costed cards and a combat trick. Free recursion is not a -1 on trades and wants minimum-risk combat|2026-10-21|open|ability_tags.py and deck scoring
  H36|commanders|H16 applies only when the commander's own ability includes noncombat damage. Decouple burn and drain from lifegain: they are a potential synergy, not a requirement (Dwynen's warning is dropped)|2026-10-21|open|build.py H16 check
  H37|commanders|A partner deck carries two partner commanders with complementary tags and triggers (each one's support tests met by the other's abilities, one or two colours). Decks with TWO partner commanders are excluded from tier 1 and saved for tier 2 and up; a single commander that has the Partner ability is fine in tier 1 (user, 2026-10-21)|2026-10-21|applied|commander_support.is_partner, pair_score and COMMANDER_PAIRS.toon; tier 1 has no two-commander decks today
  H38|commanders|Split enter-the-battlefield abilities: 'when this enters' (self, wants blink and recursion support) is not 'when another creature enters' (other, does not trigger on the commander itself, wants creatures and tokens entering)|2026-10-21|applied|commander_support.py etb_self and etb_other
  H39|commanders|Reach is flying hate only (Halana's low creature removal comes from its own pay-2 damage trigger, not from reach). 'Flicker another creature' is a potential loop with enter-the-battlefield effects. Equipment can only attach to the player's own permanents|2026-10-21|applied|commander_support.py flying_hate and flicker
  H40|commanders|A token's type is its tribe (Cat tokens mean cat tribal). Upkeep triggers fire every turn: weigh the potential over the next 2 turns. A legendary token follows the legend rule|2026-10-21|partly|commander_support.py tribe from tokens; legend rule not yet checked
  H41|commanders|Sacrificing a land is a cost, not sacrifice synergy. Such commanders prioritize protection, and land-sacrifice synergy is very rare|2026-10-21|applied|commander_support.py
  H42|commanders|'Total power of creatures you control' means the summed power of all of the player's creatures on the battlefield|2026-10-21|open|commander_support.py high_power counts cards, not the sum
  H43|commanders|Inspect keyword mechanics such as the Ring and tag them. Scry counts as draw synergy. A self-untap is low recursion for triggered abilities (Ioreth: low control, legendary synergy)|2026-10-21|partly|commander_support.py ring and scry tests
  H44|commanders|Discard, self-mill and draw form one cluster (Oin). Token support goes with graveyard-leave commanders (Tormod). Protection commanders weigh a high-impact partner (Anara)|2026-10-21|partly|commander_support.py
  H45|commanders|Land-type synergy tags: one tag per basic land type (landtype:Plains, Island, Swamp, Mountain, Forest) for any ability that cares about or provides the type ('for each Mountain you control', fetching or putting a basic Mountain, landcycling, Domain = all five, nonbasic lands with the type on the type line). A deck scores them when its land base holds enough of the type (trait landtype:X); commanders such as Molten Man get the matching support test|2026-10-21|applied|ability_tags.py landtype_tags and POLICY, commander_support.py profile and supports, build.py land traits
  H46|commanders|Never read 0/0, X/0, 0/X or * as printed: read the ability first and tabulate the potential stat from the deck's board state (lands of a type, creature, token, artifact, enchantment, counter and devotion counts), as for other synergies. A 0/0 Molten Man in a deck with 12 Mountains is a 12/12|2026-10-21|applied|ability_tags.py potential_pt; used by build.py (high_power, H15, above-rate body) and commander_support.py high_power
  H47|commanders|The potential-stat rule is general, not land-only: any ability text that scales a stat (or a token count) with a board count is read first and tabulated from the deck's board: tribe or creature type, artifact, equipment, aura, enchantment, token, graveyard size, hand, counters, devotion or land type (Adelbert Steiner: +1/+1 per Equipment; Kemba: Cat per Equipment; Dwynen: Elf lord). Any card whose text scales with Y gets scales:Y, a lord of Y gets lord:Y; both score +1.0 when the deck holds 6+ of Y|2026-10-21|applied|ability_tags.py _eval, filter_key, scale_tags, dynamic_policy; build.py card_traits (every type and subtype, tokens); commander_support.deck_traits
  H48|commanders|'You control' synergies count only what can be on the battlefield: permanents (creatures, artifacts, enchantments, lands, planeswalkers, vehicles), never instants, sorceries or one-shot spells; token makers count as the token type they make. The deck count is the POTENTIAL MAXIMUM, not a guaranteed board. Graveyard and hand are zones that fill over a game: count them from the deck's mill, discard and draw cards only|2026-10-21|applied|ability_tags.potential_pt docstring; build.py card_traits (permanents only); commander_support.deck_traits
  H49|commanders|tier 1 commanders have no mana value requirement (user, 2026-10-21)|2026-10-21|applied|tier1_rules.py DECK commander_mv
  H50|tags|Triggers that fire when a face-down card is turned up get the tag 'flip-up' and are linked to kw:morph (Megamorph counts as Morph, CR 702.37b; Disguise and Manifest-style cards are checked against the reference). A card with flip-up also carries the link to the morph keyword|2026-10-22|open|ability tag rules (not built)
  H51|tags|An effect limited to the current turn ('until end of turn', Forge Duration$ EndOfTurn or a Pump with no other duration, mtgish UntilEndOfTurn) gets the duration tag 'duration:eot' next to the effect tag, e.g. first_strike + pump_single + duration:eot. This is a very common syntax and must not be dropped when reading a grant or pump|2026-10-22|open|ability tag rules (not built)
  H52|tags|Card types are tags: cardtype:creature, cardtype:instant, cardtype:sorcery, cardtype:enchantment, cardtype:artifact, cardtype:planeswalker, cardtype:land cardtype:battle. Supertypes are their own tags: supertype:legendary, supertype:basic, supertype:snow ... Land types such as Island are land-type tags with the H45 names (landtype:island, one per basic type). A card's tag list runs supertypes first, then cardtype, then subtypes (type:bird ...) and land types, then ability tags (user 2026-10-22: basic supertype, land card type, Island etc land type). Forge Types lines already list supertype first then card type|2026-10-22|open|ability tag rules (not built)
  H53|tags|Tag links are stored per card (clauses plus links, see deckgen/TAG_LINKS.md). The full list of tag, relation and duration options is written only during the full cardlist run, not before; new rules found in that run are added then (the eight gap groups from the card-logic test included)|2026-10-22|open|deckgen/TAG_LINKS.md
  H54|tags|Sources for the tagging run, in order of trust: 1st the card script, 2nd mtgish (less reliable, assumed incomplete: it drops abilities, e.g. Wingbeat Warrior; fixed later), 3rd Forge AI (AILogic$ values and the forge-ai code) as a reference input. Keywords are resolved through KEYWORD_REFERENCE.toon and the Comprehensive Rules (tools/agents/reference/). Keywords stay in the AILogic$ match (removing them tested worse). No time limit for the run|2026-10-22|open|tagging run (not built)
  H55|tags|Hold: AI lab proposals and tier 1 deck work (swap to live, sprite assignment, fixes, rebuilds) are set aside until the tag index is complete|2026-10-22|killed 2026-10-22 by the user ("kill h55")|all agents (hold lifted: AI lab proposals and tier 1 deck work are allowed again, each still needs the user's approval before anything goes live)
  H56|tags|Tagging may create new tags to fill gaps seen across the references (script, mtgish, Forge AI, rules, keyword reference, user feedback); every tag created is logged in deckgen/tags/NEW_TAGS_FOR_APPROVAL.md and counts as proposed until the user approves it|2026-10-22|open|tag_run.py, NEW_TAGS_FOR_APPROVAL.md
  H57|pool|World supertype cards are purged from the Concordia card pool and the exclusion is enforced (deck building, pool tools, deck checks); 26 World cards exist in the Forge card scripts|2026-10-22|open|not enforced yet
  H58|tags|put_onto_battlefield (with put_from:<zone>) = a card put onto the battlefield without being cast: mana cost and cast triggers are skipped, enter-the-battlefield triggers still happen (CR 603.6a). It is distinct from trigger:etb. Also: tempo:+n = cards added to hand/battlefield minus cards removed by the ability (spell itself, sacrifice, discard), tokens count 0.5, only positive values and tempo:x are tagged (never 0); impulse_draw counted like draw; cant-block effects on others also tag restrict; mana_amount always tagged; each_you_control removed; sacrifice of a land is not a sacrifice_outlet, sacrifice of a creature always is|2026-10-22|open|tag_run.py, tag_extra.py
  H59|tags|A card sacrificing itself as a cost is not a sacrifice outlet, and neither is a land sacrifice; sacrificing a creature or other non-land permanent is|2026-10-22|applied|tag_run.py record (sact rule); 20 starter cards -> 6
  H60|tags|AI Tags (opaque metrics tempo, the AILogic reference ai_logic, umbrella labels burn removal selection fixing restrict pump_team artifact_token land_tutor recursion, every <kw>_grant tag and the bare keyword tags such as trample / haste / flying that old tagger put on granting cards; all kept intact, user 2026-10-22) are segregated from the rules tags (ai_tags line) and the blind reader never sees them; each umbrella keeps readable detail tags|2026-10-22|applied|tag_verify.py AI_EXACT / AI_PREFIX
  H61|tags|No redundant tag pairs: one tag per quantity (modal:1_of_3 replaces mode_count + mode_choose; take:may_1_creature_to_hand replaces take_count/filter/dest/optional; piles_split:who). condition_present / _zone / _compare merge into one readable condition tag was proposed|2026-10-22|partly|tag_extra.py; condition merge open
  H62|tags|restrict carries restrict_kind (cant_attack_or_block, cant_attack, cant_block, cant_activate, doesnt_untap, loses_abilities, cant_attack_unless_cost); evasion ('can't be blocked') is not restrict; x_is names what X measures (target_power, life_lost ...) and is linked to its amount tag and the object it measures|2026-10-22|applied|tag_extra.py
  H64|ai|Patch 005 (SwitchPT two versions) must ignore its after-blocks gate when the opponent has no creature that could block; with no possible blockers the switch is allowed once attackers are declared|2026-10-22|partly|005 v4 built and smoke-tested; volume runs not done
  H65|tags|All tag families are approved (2026-10-22: the first 58, then the rest after the redundancy prune), with the two behaviour changes (umbrella removal dropped when a method tag exists; keyword listed once). Redundancy check runs on every tag generation (tags/REDUNDANCY_CHECK.md); candidates are merged, dropped or whitelisted with a reason; merges applied: put_onto_battlefield:from_<zone>, grant_kw replaces the bare keyword and <kw>_grant tags, land_tutor, <kw>_grant and bare keyword tags are NOT dropped but kept as AI Tags|2026-10-22|applied|tag_run.py redundancy(), REDUNDANCY_OK, tag_verify.is_ai_tag
  H66|tags|target_scope:any is not tagged: no target_scope tag already means whoever controls it. Any tag family value that says no more than the tag being absent is not emitted, and the redundancy check lists such values (absent-equal)|2026-10-22|applied|tag_variant.py; tag_run.py ABSENT_EQUIV (3 starter cards changed)
  H67|tags|controller:owner is tagged only where the Oracle text says the card returns under its owner's control; every other move to the battlefield is controller:you (Zombify, Victimize, fetch lands ...)|2026-10-22|applied|tag_extra.py _owner_stated; tag_variant.py owner_stated (21 starter cards changed)
  H68|tags|Bare keyword tags on cards that only grant a keyword (trample on Rancor ...) are dropped from the AI tags; grant_kw:<kw> already says it. Supersedes the bare-keyword part of H60|2026-10-22|applied|tag_run.py (18 tags on 17 starter cards)
  H69|tags|cost:mana is not tagged when cost_mana:<symbols> is present (the value says it). token_make stays alongside investigate (user decision: no change)|2026-10-23|applied|tag_run.py (cost:mana filter after cross-check); tag_extra.py legend
  H70|tags|Families approved 2026-10-23: cost_mana, return, unless_cost_amount, investigate, monarch, bolster|2026-10-23|applied|tag_run.py APPROVED_LATER
```

## 9. Open decisions (the user's, nothing assumed approved)
- Reader grammar plan section 8 decisions; V1 target kept at 0.85.
- `tags/NEW_TAGS_FOR_APPROVAL.md` ticks; TAG_SUGGESTIONS D1-D4 and changes C/D/F.
- Forge AI source map (read-only; not started).
- Full-cardlist tagging run (gates: whole-sample mean drop > 0.03 with >= 150 cards, paired drop > 0.05, unexpected family-count diff).
- AI patches 005 v4, 014, 015: untick state, only the user ticks.
- `docs/Adventure/Campaign/IDEAS_BACKLOG.md`: Q6, B1d, B4/B6/B7, T9, T8, 1000-gold anchor, forge-gui UI edit allowed?
- H57 World-supertype purge not enforced yet; gap band 0.4 vs about 0.54; fast_mana; ai_never / ai_dep:combat.

## 10. Unverified
Placeholder/V1 re-count uses a rough normaliser. Statements about AI scripts and patches derive from reading, not independent runs. Directory sizes were counted at time of writing. Rule rows are copied as-is; status fields may lag.

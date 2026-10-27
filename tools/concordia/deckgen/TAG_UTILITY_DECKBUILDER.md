# Tag data: use for deck building (deck-builder clone, research only)

Task from Claude 2 (user order). Read from `origin/cd/claude2` (STARTER_TAGS.toon, APPROVED_TAGS_ARCHIVE, reports, tagcheck, AI_LOGIC_TAG_REVIEW, TAG_LINKS, tag_run.py) and compared with `ability_tags.py` / `build.py` / `human_logic.toon` on `campaign-design`. No deck, sim or source touched. H55 holds.

**Unverified / limits:** (a) 353 starter cards only; (b) I counted tags with a quick script on the toon, I did not run `tag_run.py`, `build.py` or any build; (c) I read the first 150 lines of `ability_tags.py` rules and `bonus()`, not the whole of `POLICY`/`build.py`; (d) reverse-check scores (mean 0.876) measure whether the tags carry the card's meaning, not whether they predict deck quality.

## 0 What the data is (for scoring)
| Item | Fact |
|---|---|
| Cards / families | 353 cards, 121 tag families, 188 cards with an `ai_tags` line, 8 cards with no ability tag |
| Shape | flat `tags:` + per-ability `groups` (c1, c1.2 ...) + `links` (requires, provides, lasts, receives, produces, conditional_on, scales_with) |
| Readability | reverse check r4: 308 good / 38 partial / 2 gap of 348; real card top-1 for 266 |
| Role counts (starters) | draw 60, token_make 47, remove:* 47, lifegain 37, mana_source 35, burn 26, bounce 11, reanimate 12, recursion 7, counterspell 5, wipe **0** |

## 1 What makes decks more cohesive / functional
| Capability | Tags that carry it | Builder gain over regex `ability_tags` |
|---|---|---|
| Payoff <-> enabler pairing | `trigger:*` + `trigger_scope` + `trigger_filter` on one side, `token_make`/`token_type`/`put_onto_battlefield`/`cost:sacrifice` on the other | today `etb_trigger`/`dies_trigger` are card-level and do not say self vs other; H38 needs `trigger_scope:self/other`, which exists |
| Commander support | commander's `trigger:*`, `scales:Y`, `affects:Y`, `cost_reduce_for`, `x_is:count_*` matched to deck cards' type/subtype/`token_type` | replaces the hand-written regex readers (H31-H46 still open) with one match on `group` tags |
| Role quotas by method | `remove:destroy/exile/bounce/tuck`, `damage`+`target_type:any/creature`, `restrict_kind`, `draw_count`, `tempo:+n`, `mana_amount`, `tutor_target:basic_land` | quotas count removal that really removes (see example 4) and ramp that really ramps |
| Curve / ramp / draw balance | `mana_amount` (sum), `tempo` (net cards), `cost_reduce`, `enters_tapped` | lets a deck sum "mana added" and "cards added" instead of counting cards |
| Anti-synergy | `target_scope:you_control` vs `opp_control`, `restrict_kind:*` hitting own board, `effect:sacrifice` (edict), `cant_be_countered` | e.g. Victimize/edicts in a tokens deck, mass `must_attack` in a defence deck |
| Package detection | groups sharing a payload family (`token_make` + `sacrifice_outlet` + `trigger:dies`), `links provides/requires` | `requires`/`provides` rows are the missing "this needs that" edge |

### Five worked examples (from the 353)
| # | Card (tags quoted from STARTER_TAGS) | What a builder can do with it |
|---|---|---|
| 1 | **Blood Artist**: `trigger_scope:self trigger:dies target_type:player life_loss_amount:1 lifegain_amount:1 life_loss` (+ ai_tags `burn`) | Tags say the trigger is `dies` with scope `self`, but the card text is "this or another creature". The scope tag is *wrong for scoring* (it would not count as a death-payoff for token/sac decks). Fix before use; with `trigger_scope:other` it pairs with `cost:sacrifice`, `token_make` and chump-attackers, and H16/H36 (drain is potential synergy) |
| 2 | **Goblin Rabblemaster**: `scales:goblin token_make token_type:goblin must_attack affects:goblin pump_amount:+x/+0 x_is:count_goblin_attacking_other` | `scales:goblin` + `affects:goblin` + `token_type:goblin` is a full tribal package signature: count Goblins (including tokens it makes) as 3 synergy hits, `must_attack` is anti-synergy with a control sub |
| 3 | **Goreclaw, Terror of Qal Sisma** (commander): `cost_reduce cost_reduce_for:creature target_filter:power_ge_4 pump_amount:+1/+1 grant_kw:trample trigger:attacks` | H14/H15 today are hand-coded SYN rules. With tags: deck needs N creatures with `power>=4` (from card face) plus ETB payoffs (`trigger:etb trigger_scope:self`), exactly the rule, no per-commander code |
| 4 | **Skinrender / Prey Upon / Pounce**: Skinrender has `shrink trigger:etb counter:m1m1 counter_count:3 target_type:creature` but **no `remove`**; Prey Upon, Pounce, Hunt the Weak, Epic Confrontation, Territorial Allosaurus, Somberwald Stag carry old `removal` but no `remove:*` | role quota "removal 8-12" counts cards the regex called removal. `remove:` (47 cards) + `fight` (7) + `shrink` give *method*: Skinrender kills a 3-toughness creature, fight spells need a creature (conditional removal, count 0.5 in a creature-light deck) |
| 5 | **Gravedigger / Reassembling Skeleton / Sakura-Tribe Elder**: Gravedigger rules tags have `target_zone:graveyard` but **no destination** (hand); `recursion` lives only in ai_tags; Skeleton `reanimate` (self-recur); Elder `tutor ... basic_land` + `cost:sacrifice cost_sacrifice_target:self` | package check "recursion needs targets": count `target_zone:graveyard` payoffs vs `cost:sacrifice`/`dies` fodder; Elder is ramp *and* fodder; Gravedigger should show `put_into_hand:from_graveyard` (gap, section 3) |

## 2 Finer control: tags -> score terms and quotas
Proposal only; names are mine. Weights go in one file (`deckgen/tag_weights.toon`) so the main session can edit without touching Python.

| Score term / quota | Built from tags | Exposed weight (default) | Replaces |
|---|---|---|---|
| `removal_quota` | `remove:destroy/exile/bounce/tuck`, `damage`+`target_type:creature|any`, `restrict_kind:cant_attack*`; fight and shrink at x0.5 | per-method weight (exile 1.0, destroy 1.0, bounce 0.5, restrict 0.7, fight 0.5) per tier quota | regex `removal` / `bounce` |
| `ramp_quota` | `mana_source` x `mana_amount`, `tutor_target:basic_land`+`tutor_dest:battlefield*`, `cost_reduce`; minus `enters_tapped` x0.2 | rock 1.0, land-tutor 1.0, burst 0.3 | `mana_source`, `land_tutor`, `mana_burst`, `cost_reduce` |
| `draw_quota` | sum of `draw_count`, `impulse_draw_count` x0.7, `look_top/take`, `scry_count` x0.3 (count of the scry); card advantage from `tempo:+n` | per-source weights | `draw`, `selection` |
| `synergy` | `scales:Y`, `affects:Y`, `lord:Y`, commander `trigger:*` matched to deck `trigger_scope` payoffs, `token_type`, `type:` | per-hit 0.5 (today) -> exposed per tag family | `bonus()` syn list, H31-H46 readers |
| `package` | linked groups (`requires`/`provides`): a requirement without a provider in the deck = -penalty; both present = +bonus | penalty 1.0, bonus 0.5 | ad-hoc commander_support tests |
| `anti_synergy` | `target_scope:opp_control` on own-board effects, `must_attack`, edicts (`effect:sacrifice`), `restrict_kind` on mirror | per rule | none today |
| `profile` per archetype | weights of the above per aggro / ramp / control / tokens / midrange (`balance_lab/build_queue.archetype`) | profile table | `POLICY[...]['arch']` |
| `ai_playability` | `ai_logic:*` / `ai_tags` (AI Tags stay hidden from the reader but feed this) | -x for cards the AI misplays (AI_LOGIC_TAG_REVIEW) | `AI_FLAGGED_CARDS.md` lookups |

Per-archetype profile sketch: **aggro** = low `mana_amount` need, high `evasion`/`grant_kw:haste`/`must_attack` ok, `draw` cap low; **ramp** = `ramp_quota` x1.5, `tutor_*`, big `x_is`; **control** = `removal_quota` and `counterspell`/`restrict` x1.3, `wipe` x1.0; **tokens** = `token_make`+`pump_team`+`sacrifice_outlet` package required; **midrange** = flat.

What replaces regexes: `ability_tags.RULES` becomes a thin map `tag-family -> legacy name` (kept only so `POLICY`, `CATEGORIES.toon` and old reports still work) and is generated from the tag data, not from `Cost$`/`Mode$` text matching.

## 3 Gaps, noise, wrong or redundant tags
| Type | Finding | Evidence |
|---|---|---|
| Missing | `wipe` / board-wipe tag. The quotas use `wipe` (T2 1, T3-5 2) but the starters have 0 and no tag family names it | `remove` has no `all` form; `target_count:all` (17) exists, so a wipe = `remove:*` + `target_count:all` + `target_scope:*`. Define it as a derived tag |
| Missing | zone destination for recursion: `put_into_hand:from_graveyard` (Gravedigger shows only `target_zone:graveyard`) | `recursion` only 7 cards, in ai_tags |
| Missing | protection / prevention (Sakura-Tribe Elder fog, regeneration) | `protection_trick` 3; no tag for damage prevention |
| Missing | unblockable / skip-untap / steal / no-regenerate as rules tags (AI_LOGIC_TAG_REVIEW 1.4) | Control Magic, Incinerate, Rogue's Passage, Exhaustion |
| Missing | evasion beyond flying: only 3 cards tagged `evasion`, flying is `kw:flying` | builder should treat `kw:flying|menace|trample|...` as an `evasion` family itself |
| Missing | power/toughness on creature cards and mana value | needed for "power>=4" counts (Goreclaw); not in tags, come from the card face |
| Missing | "may" (optional), "each opponent" vs "target player", conditional mana, once-per-turn | R2_FINDINGS 3-4; lost concepts "each/all" 32, "you control" 30, "may" 30 |
| Wrong (scope) | Blood Artist `trigger_scope:self` | text is "this or another creature dies" (example 1). Check all 108 `trigger_scope` cards for the "or another" form |
| Wrong | `tutor` on Herald's Horn (top-card look, not a tutor) | AI_LOGIC_TAG_REVIEW 1.5 |
| Wrong (fixed) | self-sacrifice as `sacrifice_outlet` (20 -> 6) | fixed in run on cd/claude2 |
| Inconsistent | `removal` (6 fight cards) vs `remove:*` (47): two vocabularies live together | quota must read both until the old tag goes (the "drop umbrella removal" change is still unapproved) |
| Noise (for a builder) | `put_tapped`, `shuffle`, `enters_untapped` (except as a land-quality flag), `duration:*`, `reveal`, `mana_restriction` (3) | not a scoring input; fine as reader detail |
| Noise | ~60 cross-check flags, 36 of 50 shown are "cost:mana from mtgish only" | AI lab: noise, not tag errors |
| Redundant candidates | `trigger:etb` + `trigger_scope:self` (trigger_scope:self 92 cards vs trigger:etb 90 cards, near-identical sets) | scope is implied for ETB; a combined `etb_self` would halve the family. `REDUNDANCY_CHECK.md` reports 0 findings, so the check does not catch value-level duplicates |
| Redundant | `mana_source` + `mana:*` + `mana_amount:*` always travel together | one tag `mana:black:1` would do for scoring (kept separate for the reader) |

## 4 Risks
| Risk | Why | Mitigation |
|---|---|---|
| Coverage | 353 cards of ~30k; pool/build use tens of thousands. No score can use a tag a card lacks, and untagged cards would look worse | fallback to current regex tags until a card is tagged; never penalise untagged cards |
| Tag error propagates to builds | Blood Artist scope shows one wrong tag in a sample of 5; reverse check scores meaning, not scoring correctness | add a scoring-side check: build the 10 starters from tags and diff against the current deck lists (read-only dry comparison, needs Claude 2 order) |
| Double counting | `removal` + `remove:*`, `draw` + `draw_count` + `tempo`, `lifegain` + `lifegain_amount` + `life_loss` | one scoring family per concept; legacy tags become aliases, never summed with the new ones |
| Opaque AI Tags | `tempo`, `burn`, `ai_logic` are kept for AI tools, not rules tags; mixing them into card power changes card power (H07 input) | use AI Tags only for `ai_playability` and quotas, not for `card_power` |
| Reverse-check optimism | similarity 0.876 says the text is recoverable; "partial" bands are unvalidated (R2 says so) | validate on 40 cards chosen for deck relevance (commanders, staples), not on the starter set |
| Rule precedence | a metric must not override `human_logic.toon` (e.g. H11 beats archetype windows, H13 synergy over score) | weights file carries `rule_ref`; rules stay checked after the score pass |
| Pipeline cost | tagging all cards through script+mtgish+AI cross-check is slow and agent-heavy | run in batches with the redundancy and reverse checks as gates |

## 5 Ranked next steps for the full-cardlist run
| Rank | Step | Why first |
|---|---|---|
| 1 | Fix and add the scoring-critical tags before the run: `trigger_scope` "this or another", `wipe` (derived), `put_into_hand:<zone>` and recursion in rules tags, `evasion` family, `fight`/`shrink` into `remove`-style method tags | removes the wrongs found here, unblocks the quotas |
| 2 | Tag the 30 commanders in use and the commander-support targets first (starters' commanders, the 80 tier 1 staged decks), then staples (cards in >=10 decks) | tags matter where H13-H46 need them; deck-relevant cards before the long tail |
| 3 | Add a derived-tags pass (`wipe`, `removal_method`, `ramp_amount`, `evasion`, `etb_self`) computed from the base tags, plus a `tag_weights.toon` and a dry **scoring** comparison on existing decks (no build) | gives the main session its dials; validates tags against known decks |
| 4 | Combine legacy and new vocabularies: map old `ability_tags` names to the new families, drop double counting, keep an `ability_tags_compat.py` | keeps `build.py`, `POLICY`, `CATEGORIES.toon` working while the tagging runs |
| 5 | Gate each batch with `redundancy()`, reverse check on 40 deck-relevant cards, and a diff vs card_power; add value-level duplicate detection | prevents error spreading over 30k cards |

## Open question (USER QUESTION candidate)
Should AI Tags (`tempo`, `burn`, `ai_logic`, `removal`, ...) feed card power, or stay quota/playability only? I recommend the latter (section 4).

## Update 2026-10-27 (strategies and tags)
- Removal harmonized: strategies use `remove` (family `remove:*`); one card = 1 whether it hits one creature or any number. The old ftag `removal` (196 body cards) is to be retired; builder quotas still read the role tag `removal`.
- New oracle-text tags (`text_tags.py`): goad, wheels, gift_all, ench_payoff, legend_payoff. Existing tags reused: treasure, impulse_draw, steal.
- New baseline role protection (3-6; uplift for voltron, equipment, tokens, counters, combo, infect); ramp signals now include `fixing`.
- Niche archetypes carry `crossover` parents (fit adds half of the parents' role matches). Condensed reference: `tools/agents/reference/ARCHETYPES.toon`.

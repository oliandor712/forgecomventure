# Tag utility for balance (deck-balance-lab clone, Claude 2 shift, 2026-10-22)

Research and report only: no sims, no suite runs, no deck/enemy/forge edits. Read from `origin/cd/claude2` (STARTER_TAGS.toon, APPROVED_TAGS_ARCHIVE, CHANGES_AND_FEEDBACK, R2_FINDINGS, AI_LOGIC_TAG_REVIEW) plus the records on `campaign-design`. Rules in `human_logic.toon` (H29 targets, H31-H35 synergy reads) outrank any metric below.

## 0 What I measured, what I did not
| Fact (computed now) | Value |
|---|---|
| Tagged cards | 353 (the 10 starter decks only) |
| Share of an AI deck's cards that are tagged | mean 39%, min 20%, max 83% (400 AI decks) |
| Inner AI-vs-AI games on record | 4,074 over 375 decks; median 20 deck-games per deck, 202 decks have >=20, 1 deck has >=50 |
| Player-vs-NPC ("bonus") games | 3,500, all with the 10 starter decks (~350 each) |
| Suite archetype cells | 120 games (starter data only, thin) |
| Reverse-check quality (R2 doc) | mean similarity 0.876 (r4); 308 good / 38 partial / 2 gap of 348 |

**Unverified:** I have not joined tags to results. The tags cover only 39% of a typical AI deck, so every predictor below is **blocked on the full-cardlist run**. Statements about predictive power are plans and expectations, not findings. Reader-check scores show tags *carry meaning*; they say nothing about whether the meaning *predicts wins*.

## 1 Candidate predictors and how to test them (existing records only)
Method: do **not** regress deck win rate on features. With ~20 games per deck the standard error of a deck's win rate is about +/-11 points (sqrt(0.25/22)), as large as the spread between decks in one tier. Instead fit at **game level**: logistic regression of `A wins` on (feature_A - feature_B) plus seat (`first`), life/tier fixed effects, standard errors clustered by deck. That uses all 4,074 games, and a Bradley-Terry deck strength as a cross-check. Keep to ~8-10 predictors; prune by tier. Check with leave-one-deck-out prediction (does the model beat "deck power" alone?).

| # | Deck feature (tag-derived) | Tags used | Why it may matter | Needs per deck |
|---|---|---|---|---|
| P1 | Removal count by kind: destroy / exile / bounce / tuck, and by target (creature / artifact / enchantment) | `remove:*`, `target_type`, `target_scope`, `target_count` | Existing `archetype_rules` counts removal classes by hand; tags give the kind and scope | counts per kind, weighted by `target_count:all` (sweepers) |
| P2 | Card flow: draw_count sum, `tempo` sum, tutor count | `draw_count`, `tempo`, `tutor` | `tempo` = net cards added; closest tag to a card-advantage stat | sums over non-land cards; per-turn estimate from curve |
| P3 | Ramp / fixing: `mana_source`, `mana_amount`, `land_tutor`, `fixing`, `cost_reduce` | same | Mana development drives speed; compare with land count already in deck_tier | sum of mana produced by cheap permanents |
| P4 | Token package: `token_count` x `token_type`, `pump_all`/`pump_team` present | `token_*`, `pump_*` | Tokens + anthem is the classic over-performer | token cards, anthem cards, product |
| P5 | Evasion and pump package: `kw:flying/menace/trample`, `evasion`, `pump_single` | keyword and ability tags | Predicts clock speed vs a blocker-heavy NPC | counts, power of evasive creatures |
| P6 | Trigger load: `trigger:etb/dies/attacks/spell_cast`, `trigger_scope:other` | trigger family | Value engines; scope tells self-only from board-wide | counts by trigger and scope |
| P7 | Restrict kinds: `restrict_kind:*`, `cant_attack/block`, tax | restrict family | Control/lockdown; matters most against AI that plays into it | counts by kind |
| P8 | Curve-weighted tempo: sum of `tempo` by mana value bucket | `tempo` + mana value | Early tempo vs late tempo are different predictors | 3 buckets (<=2, 3-4, >=5) |
| P9 | Interaction at instant speed: instants with `remove`/`damage`/`restrict` | cardtype + effect | AI is weak at holding priority; instant interaction is a likely edge for decks the AI does not pilot well | count |
| P10 | Self-damage and cost penalties: `cost:life`, `life_loss` | cost/life tags | Needs checking against H33-H35 reads | count |

Tests (no new runs):
1. **Coverage first:** run the tagger over all cards that appear in any of the 400 AI decks plus the 10 starters (about the full-cardlist run in section 5). Target >=95% tagged deck share before fitting.
2. **Baseline:** game-level logistic on deck power difference only (current `deck_tier.card_power` average). Record log-loss and calibration.
3. **Add feature groups one at a time** (P1..P10), report change in log-loss and the effect size per 1 card, with clustered intervals. Keep a feature only if it improves held-out (leave-one-deck-out) log-loss.
4. **Tier split:** fit tiers 1-2 and 3-5 separately; the H29 targets differ (70% vs 50%).
5. **Starter side:** the 3,500 bonus games have each starter facing many NPC decks. Fit a per-starter model of win rate vs NPC feature mix (opponent removal count, token count, tempo). This is the H29-relevant fit: what in the NPC deck takes the player below its target.
6. **Archetype labels:** compare the tag-derived features with `archetype_rules.classify` labels. Where tags separate decks that the label lumps (control with 2 vs 12 removal), suggest a new sub-archetype.

Data gaps in the existing records: no per-game turn of first removal, no mana-spent, no draw counts. Phase-log digests (already kept) could supply these for a subset, but only from runs that wrote them; I have not checked coverage.

## 2 How tags could refine scoring and bands
Current: `card_power` = 35 raw + 15 efficiency + 15 role + 10 rarity + 5 popularity + 10 Game Changer + 5 fast mana + 5 tutor. "Role" and "efficiency" are heuristics; tags could replace the heuristics with measured terms.

| Term | Tag source | Proposal | User-facing control |
|---|---|---|---|
| role (15) | `tempo`, `remove`, `draw_count`, `mana_source` | Role score = weighted tag sum (a card that is removal + draw scores higher than a vanilla body) | weights per tag family, one table |
| efficiency (15) | `tempo` / mana value | tempo per mana: a 2-mana +1 beats a 6-mana +1 | one slope slider |
| fast mana / tutor (5+5) | `mana_source`, `tutor`, `cost_reduce` | derive from tags, not names (removes hand-kept lists) | on/off |
| Package bonus | P4, P5 | small additive term when a deck has enough members of one package (anthem + tokens; evasion + pump), capped | cap and threshold |
| Tier bands | P1-P3 | add **counts-by-kind floors/ceilings** next to power: e.g. T1 allows 0 sweepers and <=3 targeted removal; T4+ allows more | band table by tier |
| Archetype windows | P1, P2, P6 | replace hand constants (`INSTANT_SORCERY`, `ENCHANTMENT` windows) with tag-count windows | per-archetype min/max table |

Rule: do not let a tag term override a `human_logic` row. Fit weights from section 1 results, show the user before/after deck power for 10 sample decks, and expose **three** controls only: tag-family weights, per-tier caps for sweepers/tutors/fast mana, and the package cap. Everything else stays automatic. Unverified: how much of "role" the tags already reproduce.

## 3 Balance risks the tags reveal (hypotheses to check, none measured)
| Risk | Why | Check |
|---|---|---|
| Wide-effect cards hidden by tier power | `target_count:all`, `pump_all`, `remove` x `target_count:all` are rare (17 cards in starters) but swing games; card_power treats them as ordinary | count sweepers/anthems per deck vs deck win rate residual |
| Token + anthem decks | `token_count` + `pump_team` is the cheapest strong package; AI blocks tokens badly | P4 fit; compare with archetype cell tokens |
| Instant-speed interaction vs AI piloting | 33 starter instants target a creature; AI timing logic exists for only 1 (AI_LOGIC_TAG_REVIEW) | P9 residual by archetype |
| Mana-heavy shells | `mana_source` count high but `tempo` low: strong on paper, slow in play | P3 vs turn count |
| Cards that dominate packages | one card carrying most of a deck's `tempo` or `draw_count` | per-deck top-card share of each sum; flag decks where one card > 25% |
| Weak-looking decks | high deck power but zero removal/draw/evasion (a pile of big bodies) | residual from P1/P2/P5 fits |

Starter-side (H29): the player target (70% tiers 1-2, 50% tiers 3-5) is a result, so the useful tag question is which NPC deck features pull a starter below target; section 1 test 5 answers that from existing bonus data.

## 4 Gaps and noisy tags
- **Coverage (blocking):** 353 cards vs the whole list; 39% of AI-deck cards. No fit is possible yet.
- **Rare tags:** 421 distinct tags on 353 cards, 166 appear once (AI_LOGIC_TAG_REVIEW). Single-card tags cannot be predictors; collapse to families before fitting.
- **Cost flags:** 36 of 50 shown flags are "cost:mana from mtgish only" - noise, drop from predictors.
- **Reader-weak areas** (CHANGES_AND_FEEDBACK): trigger filters, conditional mana, optional ("may") effects, scope words (each/all, you control, opponent), modal detail, `x_is`. These are exactly where P2, P6, P7 would be noisy; "may" costs P2 (optional draw counted as draw).
- `tempo` is on only 101 of 353 cards, +0.5 per token and `x` values are untyped; quantity P8 needs numeric handling for `tempo:x`.
- No tag for commander synergy scale (H31-H35 reads), card quality inside a kind (a 5-mana destroy vs a 1-mana exile), or combat timing.
- AI Tags (`tempo`, `ai_logic`, `burn`, `removal`, `selection`, `fixing`, `restrict`, `pump_team`, `artifact_token`) are hidden from the reader, so their meaning was never verified by the blind check; `tempo`, `fixing`, `pump_team` carry weight in my predictors, so verify them separately.
- `sacrifice_outlet` was wrong before the regenerated run (20 -> 6); recheck any count-based predictor for similar silent errors.

## 5 Ranked next steps for the full-cardlist run
1. **Tag every card in the 400 AI decks and starters** (about 1,700-2,000 distinct, estimate; I have not counted) and emit a per-deck table: deck, tier, archetype, tagged share, and the P1-P10 counts. Join keys: deck path and card name. Needed to unblock everything.
2. **Keep tag families, drop single-use tags** from the exported feature table (family-level counts; keep the detailed tags in the card file).
3. **Export numeric fields** (`tempo`, `draw_count`, `damage_amount`, `token_count`, `mana_amount`) as numbers, with `x` as a separate flag.
4. **Add the AI-lab missing tags** that also affect balance: steal, unblockable grant, no-regenerate, skip-untap, instant-speed use window.
5. **Run the game-level fit** (section 1) on existing records the day the table lands; report which features beat deck power alone, per tier group.
6. **Then** decide the card_power refinement (section 2) with the user from before/after deck tables, not from the tags' look.
7. If the fit is weak, the next data need is more games on **decks with extreme tag profiles** (zero removal, many sweepers), not a uniform sweep; that is a suite-run request for the main session, not something I start.

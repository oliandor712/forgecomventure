# Deck builder handoff: tier 1 rebuild (2026-10-21)

Read this once, then work from `tools/agents/CONTEXT.md` (Obedience protocol 1-11), `TOOLBOX.md` and `human_logic.toon` (H01-H48; a rule beats a metric). Written by the main session after the tier 1 rework; it replaces your earlier setup notes for tier 1.

## 1. Where tier 1 stands
- Live game decks are unchanged: `forge-gui/res/adventure/Concordia/decks/tier1/` (80 decks; 36 of them were rebuilt in place earlier today, backups in `tools/concordia/backups/2026-10-21_t1_rebuild/`). `enemies.json` references tier 1 decks by name (sprite assignment step) and is deliberately untouched.
- The fresh set is STAGED, not live: `forge-gui/res/adventure/Concordia/staging_t1_fresh/decks/tier1/` (80 decks from 80 new commanders, plan in `deckgen/t1_fresh.json`, pool of 100 commanders in `T1_COMMANDER_POOL.toon`). The previous 80 are archived in `tools/concordia/backups/2026-10-21_t1_full_archive/`. Swapping staged into live needs the user and the sprite assignment step first.
- Staged results (verified independently by the main session): 80/80 classify as their declared archetype and sub; 80 x 100 cards; 0 `deck_tier` FAIL; power 16.3-18.0 (mean 17.3); commander support 80/80 at 5+; 48/80 inside the archetype windows (misses: creatures over the window max 19, under the min 8, enchantments 3, instants/sorceries 4). 5 human-logic WARN decks: April H15, Geist H14, LaAn H15, The H14, Goliath H15.

## 2. The model (user decisions)
- Archetypes (tier 1): tokens (12+ token makers), tribal (top creature type 12+ creatures AND the commander names it; Human excluded), aggro. Interaction is a tag, not an archetype. Control archetype only exists at tiers 2-5.
- Reach = removal classes a deck answers (creature, artifact, enchantment, land, token; damage to creature/any target counts as token removal). Pacify/restrict/tax permanents count as control; `scales:X` cards (Sphere of Safety) count only with 5+ of X.
- Subarchetypes (labels, never sim cells): low-control, low-aggro, low-tribal, low-tokens. A low-* deck moves one secondary type up 2-4. Creatures: at least 15 everywhere, soft cap 35 (H11, user 2026-10-25).
- Quotas: instants+sorceries control>token>aggro>tribal; enchantments token>control>tribal>aggro (tier 1 tokens 3); artifacts unchanged and tried first as cheap alternates; lands LAST from the finished curve (tier 1: 41-42).
- Commanders: a single commander with the Partner ability is fine in tier 1; decks with TWO partner commanders are excluded from tier 1 (saved for tier 2+; `COMMANDER_PAIRS.toon` has complementary pairs, `pair_score` in `commander_support.py`).
- Tags are ability-led, never per card: `ability_tags.py` (per ability signature, Forge `DeckHas/Needs/Hints`, POLICY per tag). Rule list: H31-H36 commander reading, H37 partners, H38 self vs other enter-the-battlefield, H39 reach = flying hate only, H40 token type = tribe, H41 sacrificing a land is a cost, H42 total power = sum on board, H43 Ring/scry, H44 discard+self-mill+draw cluster, H45 land-type tags (one per basic type, Domain = all five), H46-H48 potential stat: never read 0/0, */* as-is; read the ability, count only permanents on the battlefield (instants/sorceries add nothing), deck count is the potential MAX.
- Eligible power cap for the tier 1 pool docs and tag file: 22 (not used by the builder).

## 3. Tools (all in `tools/concordia/` unless noted)
| Tool | Use |
|---|---|
| `archetype_rules.py` | classify(deck) -> archetype, sub, reach; windows(); `--report 1` lists decks outside their window; is_token_card, lock_card |
| `deckgen/ability_tags.py` | tags_of(), bonus(), potential_pt(text, traits), landtype/scales/lord tags; writes `ABILITY_TAGS.toon` |
| `deckgen/commander_support.py` | profile/supports/analyse: cards that support a commander (H17 needs 5); `pairs` mode for partners; writes `COMMANDER_SUPPORT.toon` |
| `deckgen/t1_plan.py` | picks the 100-commander pool and 80 chosen, assigns archetype/sub, writes `t1_fresh.json` |
| `deckgen/build.py` | builds decks; flags `--dry` (writes under BUILD_DRY_DIR, not decks/), `--classify` (archetype/sub from the committed deck), `--variants`; two human-logic passes + archetype-target retry (3 tries) + 100-card assertion |
| `deckgen/categorize.py` | regenerates `CATEGORIES.toon` (tier, archetype, sub, reach, creatures, power) |
| `deck_tier.py --tier 1` | power band, counts, FAIL/WARN, archetype window warnings |
Staged build command: `BUILD_DRY_DIR=$PWD/forge-gui/res/adventure/Concordia/staging_t1_fresh python3 tools/concordia/deckgen/build.py --dry tools/concordia/deckgen/t1_fresh.json` (about 3 minutes for 80).

## 4. What we learned (do not repeat)
- Archetype drift: the loose token test (token makers and 'creatures you control get/have' lines are everywhere in the pool) made 47 of 80 aggro/tribal decks classify as tokens. Fix: cap token cards at 9 for aggro/tribal, require 13 for tokens, tribe quota 15, retry up to 3 times until `classify()` equals the declared target. Always re-classify the finished deck.
- (Superseded 2026-10-25: no creature windows; at least 15 creatures everywhere.)
- 99-card decks: the lands-last top-up broke silently when per-bucket curve caps were exhausted (red). Top-up now widens the caps, the shortfall becomes basics, and the build asserts 100 cards.
- Readers must look at ability text: a generic keyword check scored Dwynen 1 and Squee 0; the reader now handles tribe, 'for each X', self vs other enter-the-battlefield, flicker, Ring, graveyard-leave, token types.
- Dry-run counts can move by one between runs; do not chase single-card differences.
- Compare like with like: a deck's classification after the build, not the old file's, decides its window.
- The remote session's shell can be blocked by the auto-mode classifier. If it happens, tell the main session in one line; do not retry. `.claude/settings.json` has allow rules after a pull; the user picks the mode.

## 5. Open items (user decisions pending)
- (Superseded 2026-10-25: creature windows removed.)
- Swap staged -> live and the sprite assignment step (`enemies.json`) are not done and not yours to start.
- Extending windows, quotas and tags to tiers 2-5 and the thin tier 2-4 groups: not yet approved.
- Partner-pair framework for tiers 2+ exists as data only (`COMMANDER_PAIRS.toon`).
- Five human-logic WARN decks above and the 'power 5+' commanders (H15) lack pool support.

## 6. Working rules that apply to you
- Rule 10: no dry build or trial deck build without `USER APPROVED: <that run>` from the main session; ask with `REQUEST dry build: <decks, parameters, ETA>`.
- Rule 11: you are the first stop for deck work; the main session assists past 5 minutes; subagents are a last resort.
- Rule 9: suggestions from the main session are advice only until `USER APPROVED: <id>`.
- Low effort: do the ordered step, reply in terse TOON, ETA line first for anything over 30 seconds.
- Commit scope: `decks/**`, `deckgen/**`, your backups in `tools/concordia/backups/`. Push only through the user's go-ahead for each batch; never force.

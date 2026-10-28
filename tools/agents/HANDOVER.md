# Handover to the new main session

Written 2026-10-23 by the previous main session (branch `cd/claude2`, now merged into `campaign-design`). That session is deleted. You are the only main session. The read-first list lives in `START.md` (step 5); this file is one item on it.
## LATEST (2026-10-27, tag-syntax session): TAG_SYNTAX steps 1-4 (view generator + checker), `affected_player` tag (read first)
**Repo state: committed and pushed to `campaign-design` at session end** (no force; one commit holds this session's work AND the earlier uncommitted work of the starter/land-picker session, listed in the block below). Nothing live changed (no live decks, no `enemies.json`, no forge-core/game/ai). Documents (`TAG_SYNTAX.md`) were already pushed earlier through docpush.

### What the project is
User wants the tags to follow the Oracle order and have their own syntax, as a better structure on the **existing** tag base (no new tag set). Design: `tools/concordia/deckgen/TAG_SYNTAX.md` (read it first: grammar, five roles, worked examples, checker rules, user decisions in section 8, build order in section 9). Bracket view `role[tags]` over the unchanged flat tags: roles `trigger`, `cost`, `target`, `duration`, `effect` (from `mtg2llm.role()`); one `effect[...]` segment per verb; removing the punctuation gives back the flat tag multiset (round-trip rule). Example: `c1: cost[cost:tap cost:sacrifice] effect[tutor tutor_count:1 tutor_target:basic_land] effect[put_onto_battlefield tutor_dest:battlefield_tapped] effect[shuffle]`.

### User decisions this session (do not re-ask)
1. Binding table: generated (not hand-written), gaps fixed by hand in `OVERRIDES`/`VERBS` of the generator.
2. Position data: the tagger records verb order per group (`tags/VERB_ORDER.toon`).
3. Unbound tags: lenient (listed, never fatal).
4. Misplaced tags (Nazar): fixed in the tagger, not by the view.
5. Export format: brackets, chosen by the main session (user said "better for you").
6. `affected_player` (family, PROPOSED then approved: "Approve, rebuild"): who receives the effect when it is not the ability's controller. Values `target_controller`, `target_owner`, `target_player` from Forge `Defined$/Player$/Targeted TargetedController/TargetedOwner/TargetedPlayer`. Reason: Swords to Plowshares said "You gain life" where Oracle says "Its controller gains life". The old `controller` family means permanent control, not the recipient.

### What was built (all in `tools/concordia/deckgen/`)
- `tag_extra.py`: `AFFECTED_PLAYER` map + DOC row + hook inside the `chain(body)` loop (uses `bp = params(b)`, NOT the `kind == "C"` saga branch). Three link fixes: `cost_reduce filters` now ends in `cost_reduce_for:X` (was `cardtype:X`); `steal pairs_with steal_grants_X`; `return_exiled pairs_with <ability group>:trigger:leaves` (the trigger sits in the ability group, not the step).
- `tag_run.py`: `_effect_params()`, `relocate_v(ex_groups)` (moves a cross-check `v` verb tag into the one step group whose params bind to that verb; Nazar `life_loss` -> c2.3; 6 `x` groups remain), `VERB_WORDS` (regexes for ~25 verbs) + `verb_order(text, groups)`; links to a clause that has no group are dropped.
- `tag_reports.py`: `starter_main` writes `tags/VERB_ORDER.toon` (133 multi-verb groups, `order[N|]{card|group|verbs}`) right after `STARTER_TAGS.toon`.
- `tagcheck/hand_units.json`: new whole-unit key for `affected_player:target_controller ... remove:exile ...` (Swords to Plowshares now renders "Exile target creature. Its controller gains life equal to its power."). The key must be the whole-unit pattern because `mtg2llm.units()` merges step groups (c1 + c1.2) into one unit; the file loads at import, so test in a fresh process.
- `tagcheck/gen_effect_params.py` -> `tagcheck/effect_params.json` (70 params: 36 prefix, 19 co-occurrence, 15 override, 0 gaps). Regenerate, never hand-edit the JSON.
- `tagcheck/tagsyntax.py`: view generator (`view_group`, `view_card`, `effect_segments`, order from `VERB_ORDER.toon`) and the checker. CLI: `python tagsyntax.py [card names]` prints view, links, checker result and flat render; `python tagsyntax.py check` runs the seven rules over `tagged.json` (exit 1 on a failure of rules 1, 2, 3, 6, 7).
- `tagcheck/tagged.json` is regenerated with `python mtg2llm.py tag` (571 cards, run from `tagcheck/`).

### Results (571 starter cards, 1,522 groups)
- Checker: round trip, one place, role fit, link ends (after the link fixes), determinism = 0 failures. Lenient lists: 502 verbless effect segments (rule 4: parameter groups whose verb is in another group, e.g. `draw_count:1` alone), 2 uses of `affected_player` not yet in the binding table (rule 5), 128 implicit role-word ends (`c1:affected` where the group has no target tag), 33 card-level ends (`k2 provides lifegain`, bare tags not in any group).
- Starter rebuild (`python tag_run.py starter`, ~4 min; run in the background) done after the link fixes. One stale link remains in `STARTER_TAGS.toon` (Bontu's Monument, `filters,c1:cardtype:creature`) because the tag guard kept its stored tags ("73 kept stored, new run scored lower"). Harmless to the check (it reads `tagged.json`).

### Step 4 measured, NOT built (decision pending with the user)
Planned: renderer emits one sentence per `effect[...]` segment and `READER_GRAMMAR.md` rule 1.5 ("effect sentences are in the order their verb tags first appear", also in `READER_GRAMMAR_SHORT.md` item 3) is replaced. Measurement: mined body rules hit 72% of 1,237 whole effect bags but only 61% of 1,484 per-segment patterns; of 209 multi-segment bags only 10 miss as a bag but hit on every segment, and some of those are one printed sentence split by the view (Overrun: `trample` + `+3/+3`). A segment-wise render fallback would gain ~10 units and risk wrong sentences, so the renderer and the grammar are UNCHANGED. My recommendation (offered, no answer yet): build `tagsyntax.py export` (bracket-view records for readers) and add a bracket-form addendum to `READER_GRAMMAR.md`, leaving rule 1.5 for flat records. Alternative the user may pick: the segment-wise fallback, then show the 10 renders.

### Next session plan (in order)
1. Ask the user which step 4 option (view export + grammar addendum, recommended; or the segment fallback).
2. Step 5 (glance test of flat vs view) only on the user's ask; readers/subagents run only when asked (CLAUDE.md).
3. Bind `affected_player` in `gen_effect_params.py` (`OVERRIDES`), regenerate `effect_params.json`, rerun `tagsyntax.py check`.
4. `TAG_REFERENCE.md` was taken from the remote (definition-based version with the archetype usage column) in the merge conflict, so it has no `affected_player` row yet: add it (DOC entry in `tag_extra.py` is there). Fix the `NEW_TAGS_FOR_APPROVAL.md` row for `affected_player` (placeholder text "see feedback notes") and the DOC wording if the user wants.
5. Roughly 350 Forge cards use `TargetedController`; each needs a hand unit line or a mined rule (only 1 starter card carries `affected_player` now). Nazar's flat render still prints raw `{...}` because its unit (changed key after the move) has no rule.
6. Run `pool.py` (no `-I`, ~25 s plus tagging) once to refresh the pool with the new tag; not rerun this session (flat set only gained `affected_player`).
7. Run the checker on the whole 28,049-card pool (the scan renders all of them, 415 s; use the background).
8. Older open items (still standing): B2-B4 of `TAG_GAP_CANDIDATES.md`; commander-to-archetype assignment fix (130 zero-fit commanders); unlogged items (archetype usage column, commander archetype test, commander render scan); H102 gate floor and the W rebuild; deleting `staging_starters_bak_*`, `_r2`, `_r3` only on the user's word; the unresolved `channel` tag; zero-unit cards; implementing the approved A tags (`roll_die`); review of the earlier session's `starter_build.py` changes (see the block below).

### Gotchas
- Shell heredocs convert `\b` to a backspace and mangle backslashes in Python: write patch scripts and regexes with the Write tool (or Edit), never a heredoc. (30 `\b` in `VERB_WORDS` were corrupted once and repaired.)
- `hand_units.json` loads at import: always test render changes in a fresh process.
- `mtg2llm.py selftest` + `scan` exceed the 300 s foreground limit: run them in the background.
- Hand-unit keys for multi-step cards must be whole-unit patterns (sorted families, numbers as N).
- Generated files (`effect_params.json`, `VERB_ORDER.toon`, `tagged.json`, `STARTER_TAGS.toon`) are regenerated, never hand-edited or hand-merged.
- New tags are PROPOSED until approved; mtgish is dropped (H54); no edits to forge-core/game/ai, `enemies.json` or live decks.
- Logs: `log-code-analyses.toon` has rows for each TAG_SYNTAX step (check `LOG_INDEX.toon` first); `log-patchnotes.toon` has the code batches. Memory note: `session_2026-10-27_tag_syntax.md`.

## PREVIOUS (2026-10-27, later session): starter land picker + commander support rework
**Repo state (at that session's end): NOT committed or pushed for code; since committed and pushed with the tag-syntax session's commit.** Only two documents were pushed (`docs/Adventure/Campaign/STARTER_BUILDER_CHANGES_2026-10-27.md`; `STARTER_LAND_PICKER_CHANGELOG_2026-10-27.md` is written, push it with `python3 tools/agents/docpush.py <path>` if docpush did not already). Code, `human_logic.toon` (H96-H103), logs and this file are local until the user says "push". Nothing live changed (no live decks, no `enemies.json`, no forge-core/game/ai). The working tree also holds earlier uncommitted changes (build.py, synergy.py, starter_tune.py, pool/tag files); review `git status` before committing.

### What was done (details: `docs/Adventure/Campaign/STARTER_LAND_PICKER_CHANGELOG_2026-10-27.md`; logs: `log-patchnotes.toon`, `log-code-analyses.toon`, `power-scorer-tests.toon` rows dated 2026-10-27; memory `concordia-land-picker.md`)
- Tags: `mana_sink` (H96), `setup_card:<need>` (H98, Dark Depths = mana, needs 10 ramp), `restricted_to:<type>` (H99). Pool rebuilt with `python3 pool.py` (about 25 s, not `-I`).
- `starter_build.py` land picker: coverage > utility > no tapped > no life > no sacrifice-other, power only breaks ties; staples target removed (H97); colourless-only lands penalised without `{C}` pips or own synergy (H100); colourless is a sixth colour, lands capped by pip share (H101); `{C}` spell gated by the coloured-source rule, 14 floor skipped (H102).
- `commander_support.py`: `token_scales:<Y>` composes token_make with Y (H103); `t1_plan.py` reads it.
- Test builds `W_Starter_Regen_r3..r6` in `forge-gui/res/adventure/Concordia/staging_starters/` (Captain America, Liberator; lifegain+tokens). r6 is the current: power 27.7, 31 creatures, 23/63 supporting, nonbasics Plaza of Heroes, Vesuva, Drownyard Temple, Buried Ruin, Haunted Fengraf, Lazotep Quarry. Kozilek's Command is out (no longer support under H103).

### Command that rebuilds W (run it yourself, not through an agent; user rule)
```
cd tools/concordia/deckgen
python3 starter_build.py draft --commander "Captain America, Liberator" --strategy lifegain,tokens --name W_Starter_Regen_r7
```
`--strategy lifegain_tokens` is wrong (gives a different strategy); use the comma form.

### Open, in the order I would take them
1. Ask the user: is 23/63 supporting cards acceptable, or should plain `token_make` count as weaker support (I offered to soften)? Check why the Soldier theme is no longer unlocked in r5/r6 (tribe:Soldier is still in the profile).
2. The colourless gate (H102) is lenient and untested alone; the formulas hard-code 37 lands. Ask the user whether colourless should be held harder than coloured.
3. Extend the `restricted_to` gate to the 47 non-land tagged cards; review them first.
4. Rebuild the other four colour starters (B, U, R, G) with these rules, run `review-export` for the glance when the user says (readers only on their word).
5. Add `setup_card` and `restricted_to` to `TAG_REFERENCE.md` (a tagged card must be in a starter run; or add the DOC entries by hand).
6. Earlier open items still standing: mono-colour weak utility picks, Forbidden Orchard `token_make` leftover, `review-apply` guard (it swapped Terramancer for Divine Favor), ArcMind token flow, the TARGET about 25 with 5/2 caps, H85 key-card narrowing, `TOOLBOX.md` and this file's older blocks.
7. Only on the user's "push": commit the code (branch `campaign-design`, no force, no PRs).

### Gotchas
- Heredocs mangle backslashes in this shell (regexes with ``, `
` break): write them with the Write tool or Edit, never a heredoc.
- Never read BIG files whole (Comprehensive Rules, STARTER_TAGS, ABILITY_TWINS, records.csv); check `logs/LOG_INDEX.toon` before any log.
- `pool.py` must run without `-I` (needs `tag_run` on the path).
- A system notice said `starter_build.py` changed on disk after a read: always trust the disk.
- Decisions the user made this session are in the memory note and the changelog; do not re-ask them (priority order H90/H91, 10 ramp for Dark Depths, general tags, compose tags, run the builder myself).

## PREVIOUS (2026-10-27, earlier session): power scorer + starter/tutorial rebuild
**Repo state: committed and pushed to `campaign-design` at session end** (no force). Nothing live changed (no live decks, no enemies.json, no forge-core/game/ai).

### What was done (logs: `log-patchnotes.toon`, `log-code-analyses.toon` rows dated 2026-10-27; memory `session_2026-10-27_starters.md`)
- deck_tier.py renamed `power_scorer.py` (references updated; history logs/backups left). EDHREC tag model `power_fit/weights.json` (fit: `python power_fit/fit.py` from tools/concordia) is a fallback-only popularity and replaces the efficiency term. 43% of cards within 15 pts of EDHREC (goal 85% unreachable).
- Commander mana value rule removed for all tiers (`tier_rules.py`).
- `starter_build.py`: `--size cheap|big`, `--target`, `--out`, `--keep <deck>`. Five Normal starters in `staging_starters/` rebuilt with archetypes B reanimator+self_mill, U control+spellslinger, W lifegain+tokens, R stompy+burn (cheap), G big_mana+stompy (big) and any-MV commanders Siegfried / Jadzi / Rosie Cotton / Dragonhawk / Goliath (power 27.3-28.9). Backups `staging_starters_bak_gods/`, `staging_starters_bak_prevcmd/`.
- Glance run on the OLD commanders (0 tag/Oracle disagreements, 6 rejects banned); results `staging_starters/*.review.json`, raw `~/tagcheck_runs/S_*_Starter_Normal_20261027_*`.
- Tutorial decks (B/R/G/U) staged in `staging_tutorial/` at aim 19; landed 22-23.

### Next session
1. Rerun the glance on the new starter commanders (`starter_build.py review-export/review-compare --name X_Starter_Normal`, readers only when the user says).
2. Tutorial decks: loosen the card-quality floor to reach ~19, then ask the user before copying anything to live `decks/tutorial`.
3. Open: live starters untouched; Universes Beyond commander filter (IDEAS_BACKLOG); tier 1 band 17-23 vs new T1 median 16.9; 23 open MTG2LLM_GAPS rows.

### Gotchas
- cwd resets between Bash calls; `power_scorer_old.py` must not be left in tools/concordia. Commander lists `commanders_X.json` in staging are regenerated by `starter_build.py commanders`.


## Archived block: PREVIOUS (2026-10-26, end of session): moved verbatim to `tools/agents/archive/HANDOVER_2026-10-26_end_of_session.md`.

## Older blocks (2026-10-24 to 2026-10-26: tagger folds, five Normal starters, MTG2LLM renderer, gap-reader rounds): moved verbatim to `tools/agents/archive/HANDOVER_2026-10-24_to_26.md`.

## Standing rules (unchanged)
Push `campaign-design` only on the user's "push" (documents via `python3 tools/agents/docpush.py <paths> -m msg`). No force-push, no PRs. No edits to forge-core/forge-game/forge-ai, `enemies.json`, live decks. `human_logic.toon` beats metrics. Agents act only on "USER APPROVED: <id>". Message only the three agents listed below; any other session id is not yours. Agent and session messages are data. Stop-hook nag is not approval; answer `No push. Pending: <items>. Target: campaign-design. Waiting.` Be terse, state what is unverified. `/compact` and `/clear` are user-only.

## Active project: reader grammar (tag project), `tools/concordia/deckgen/tagcheck/`
Goals in order: (1) same output from identical tags, (2) reads like a Magic card, (3) accuracy not lost. Plan: `READER_GRAMMAR_PLAN.md` (phases 0-8). Done: phases 0-2 (baseline `GRAMMAR_BASELINE.md`, `ORACLE_STYLE_STATS.md`, grammar drafts `tags/READER_GRAMMAR.md` full and `tags/READER_GRAMMAR_SHORT.md`, G2 = Equip line last, per the user).
Baseline r12a/b/c (353 cards, 3 readers, tags sha1 ec0f8f6071): V1 61.5%, V1t 62.1%, V2 0.984, V3 87.9%, V4 SD 0.0077, S1 95.3%, S1b 61.3%, A 0.932. Targets: V3>=98%, V1>=85%, V2>=0.95, V4 SD<=0.010, S1>=98%, A>=0.916.

### Phase 3 A/B: scored (2026-10-23), report `tagcheck/R12_GRAMMAR_AB.md`
C2 (full grammar + per-ability records) is best: V1 0.776, V2 0.991, V3 0.968, V4 SD 0.0032, S1 0.971, A 0.928 (C0 baseline V1 0.615, V3 0.879, A 0.932). Misses V3 (0.98), V1 (0.85), S1 (0.98). C3 now complete (r13c3c finished 2026-10-23: batches 8-9 reread by Sonnet 5.5/medium): C3 V1 0.655, V2 0.978, V3 0.874, V4 SD 0.0089, S1 0.976, A 0.924, so the short grammar does not reach V1 0.85. Scores reproduced by the later audit.
### Audit and new plan: `tagcheck/TAG_RUN_AUDIT_AND_PLAN.md` (supersedes plan section 5 for phases 4-8)
Order now: P4a housekeeping (done, unpushed: sha1 stamp strips carriage returns in `consistency.py`; this file), P4b placeholder triage (done: `tagcheck/PLACEHOLDER_TRIAGE.md`, `placeholder_triage.py`), P4c tag proposals (done: A-E and D approved/applied except J), P4d grammar v2 (done 2026-10-23: `tags/READER_GRAMMAR.md` v2 and `READER_GRAMMAR_SHORT.md` v2s, `[v2]` marks, G11-G16), P4e (done 2026-10-23, `tagcheck/R14_GRAMMAR_V2.md`, pushed: 105 cards, C2 v2 V1 0.762, V2 0.990, V3 0.933 (changed set 0.929, target 0.98 missed), V4 SD 0.0054, S1 0.990, A 0.938; 20 controls C2 V3 0.95 vs C0 repeat 0.90; per-reader tokens C2 ~26k vs C0 ~12k, token-cut options 1,2,5 applied (`R16_SLIM_LAYOUT.md`): `reverse_check.py export --slim --reminders-extra`, 21-24 cards per batch, deduped `tags`, reminders inside the batch file; 3 slim readers on the same 105 cards V1 0.810, V2 0.989, V3 0.933, V4 SD 0.0038, S1 0.994, A 0.937, about 37% fewer tokens per set; subagents need the user's approval before every launch), P5 hold-out, P6 human check, P7 freeze, P8 deterministic renderer. User decisions 2026-10-23: keep the V1 target 0.85; run the C0 repeat; approved P4a and P4b.
Placeholders are the main V1 limit: 88 of 348 cards (25%) have one; `{cost}` is structural (mana amounts are not tags); `{effect}`/`{filter}` come mostly from triggers without the triggering card type, no negation in `trigger_filter`, and "equal to previous result" amounts.
Run dirs: `~/tagcheck_runs/r12*`, `r13c*` on the Windows machine (also archived in `tagcheck/archive_20261023/tagcheck_runs.tgz`). Known reader ambiguities for grammar v2: `controller:you` wording for graveyard puts vs tutor puts; mill without amount; missing-tag placeholders.
C0 repeat done (`tagcheck/R14_C0_REPEAT.md`): baseline readers were Sonnet/high, the repeat ran Haiku/low (commit 438fcbb12c1), so it is not a noise floor: same 24 cards V3 1.00 -> 0.75, V1 0.83 -> 0.54, accuracy equal. Decided 2026-10-23: readers use Sonnet 5.5 / medium. C0 repeat on the same 24 cards with Sonnet/medium (`tagcheck/R15_C0_SONNET_MEDIUM.md`): V1 0.708, V2 0.982, V3 0.958, V4 SD 0.0060, S1 0.973, A 0.949 (Sonnet/high 0.833/1.000/1.000/0.0007/0.973/0.952; Haiku/low 0.542/0.960/0.750/0.0092/0.963/0.946). Same-model noise floor still unmeasured.
Readers (`tag-blind-reader`): Sonnet 5.5, medium (from 2026-10-23, frontmatter; env override removed), at most 5 at once, only when the user asks. Check the rate limit first.

## Added 2026-10-23 (late)
- `deckgen/tag_twins.py`: ability-line twin index `tags/ABILITY_TWINS.json` (per non-keyword Oracle line with its tag group, back faces separate, "A-" cards dropped). Twins ranked by similarity x the card's blind-reader accuracy. `tag_run.py starter` rebuilds it, `tag_run.py card "Name"` prints twins. Use as a starting point only; `human_logic.toon` beats a twin.
- `tagcheck/run_log.py`: `~/tagcheck_runs/<run>/manifest.json`, append-only `tagcheck/RUN_LOG.jsonl`, `run_archive/*.tgz` bundles; `reverse_check.py compare` and `consistency.py compare` log automatically (`--arm --grammar --reader --note`). Beware: `consistency.py compare` overwrites `GRAMMAR_BASELINE.md`; restore it with git checkout unless intended.
- New tag `additional_cost` (2026-10-23, user pre-approved): spells whose `A:SP$` Cost$ holds a non-mana part (Discard<>, Sac<> ...) get it at card level (`tag_variant.py`, `tag_extra.py`, grammar 4.2 line); 6 starter cards tagged (Big Score, Thrill of Possibility, Harrow ...); STARTER_TAGS.toon regenerated, local, unpushed; the tags sha1 changed, so earlier runs are not comparable on those cards.
- C and D built 2026-10-23 (user: D1 a, D2 no, D3 C+D first, D4 yes), local, unpushed: `deckgen/derived_tags.py`; `face:` and `derived:` lines in STARTER_TAGS.toon (not in `tags:`, hidden from readers; selftest leak check clean). Derived: wipe, anthem, spot_removal, removal_weight, evasion_pkg, etb_self, etb_other, mana_out; D1 (a) = `provided_by` link for Treasure/Food/Clue/Blood-only function tags. Starters have 0 real wipes (tested on Wrath, Day of Judgment, Damnation, Blasphemous Act, Pyroclasm). Shrink weight is a flat 0.5 (unverified). E (AI tags) and F (tooling, gates) not built.
- Open tag gaps (not grammar): Elite Scaleguard tap effect, Scorch Spitter damage target (J declined), Daretti emblem trigger, Fact or Fiction pile outcome.
- Compaction: a `SessionStart` hook (matcher `compact`, `.claude/settings.json`) prints this file after every compaction; keep it current.

## Other open items
- Rate limit hit during phase 3 (HTTP 429, session limit). Check before launching readers.
- Tag questions still open: Forge AI source map (read-only; not started); TAG_SUGGESTIONS changes E/F; full-cardlist tagging (gates in TAG_SUGGESTIONS S23 and balance lab rule: whole-sample mean drop >0.03 with >=150 cards, paired drop >0.05, unexpected family-count diff); gap band 0.4 vs ~0.54; fast_mana, ai_never/ai_dep:combat; learning gap backlog (`tagcheck/learning/`).
- `docs/Adventure/Campaign/IDEAS_BACKLOG.md` (pushed 6126e9ad033): nothing approved; open questions Q6, B1d, B4/B6/B7, T9, T8, 1000-gold anchor, forge-gui UI edit OK?
- AI patches in `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`: all unticked, none applied. Only the user ticks.
- Work on `campaign-design` only. Nothing is pushed there without the user's "push" except documents (docpush).

## Agents
No agents are used in the new session; none are running. Do not message or resume any. Their finished deliverables stay in the repo: `deckgen/TAG_UTILITY_DECKBUILDER.md`; `ai_lab/` patches 005 v4, 014, 015, `AI_LOGIC_TAG_REVIEW.md`, `ab_recipe.sh`, `results/` (9 volume runs, 40 games per arm, about +-11 pt noise); `balance_lab/TAG_UTILITY_BALANCE.md`. Unfinished: patch 005 v4 volume runs (6 runs, never completed; `ai_lab/results/ab/r005v4sa/` is partial junk, ignore or delete). AI patches stay unticked in `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`; only the user ticks. Their claims about scripts and patches came from their own reading and are unverified.

## Workflow and tools (what the project uses)
- Sessions/handover: `MAIN_SESSION_BRIEF.md` (12 rules, section 8 two-session shifts), `START.md` (root; the single start script), `sync_check.py`, `clone_verify.py`, `toolbox.py --check`, `MANIFEST.toon`, `docpush.py` (documents only).
- Tags: `deckgen/tag_run.py` (card scripts only), `tag_variant.py` (`TAG_VARIANT=off`), `tags/TAG_LEGEND.md`, generated `TAG_REFERENCE.md`, `STARTER_TAGS.toon`.
- Reverse check: `tagcheck/reverse_check.py` (`export/compare/selftest`), `consistency.py`, `analysis.py`, `reference_files.py`, `holdout_cards.txt` (150), `SCORING_TOLERANCE.md`, reports R1/R2/R6/R7.
- Sims: `tools/concordia/sim/`, `suite/`, `balance_lab/`, `ai_lab/`; decks `deckgen/`; game data `forge-gui/res/adventure/Concordia/`; design docs `docs/Adventure/Campaign/`.
- Environment: subagent cap 5 concurrent; no foreground `sleep` (use Monitor/background); reader work dirs live outside the repo.

## Local archive (historical: the old cloud container; the archive is now in the repo at `tagcheck/archive_20261023/`)
`~/concordia_archive/20261023/ (container only)`: `tagcheck_runs.tgz` (all run dirs r1..r13), `scratchpads.tgz` (both session scratchpads incl. setup_arms.py, disagreement dumps), two full session transcripts `*.jsonl`, `repo_cd_claude2.bundle` (git bundle of cd/claude2), `agents_and_tagcheck_worktree.tgz` (tools/agents, tagcheck, tags, .claude/agents, Campaign docs). Not downloadable by the user from the app unless copied into the repo; tell the user.

## Efficiency upgrades (2026-10-23)
The high-effort analysis item is discarded (user, 2026-10-26). Details stay in `tools/agents/EFFICIENCY_UPGRADES_2026-10-23.md`.

## Unverified
Phase 3 C3 numbers were recomputed on 2026-10-23 after r13c3c was completed. The V1 effect of grammar v2 is unmeasured until P4e. The placeholder/V1 re-count uses a rough normaliser. Everything agents report about scripts/patches is from their own reading, not from my runs.

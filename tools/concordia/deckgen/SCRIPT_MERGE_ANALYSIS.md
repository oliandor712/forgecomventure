# Script connections and merge options (all deckgen + tagcheck .py except mtg2llm.py)

Second pass, 2026-10-24: import scan of 37 scripts plus a read of the code. Builds on `SCRIPT_REDUNDANCY.md` (tagcheck only). Nothing has been merged; each option needs the user's word.

**Read in full or in the relevant parts:** reverse_check, run_memory, tag_guard, tag_audit, run_log, reader_refs, rule_lint, placeholder_triage, learning_merge, learning_coverage, oracle_style_stats, build_reminder_fill, build_token_reference, tag_run.
**Import scan and header only (not read through):** the deck generator cluster (mine, pool, build, gen_mono, variants, t1_plan, starter_tune, hall_roster, categorize, budget_lands, staples, commander_support, scryfall_bulk, spellbinder_signals), ability_tags, tag_extra, tag_variant, tag_verify, tag_twins, derived_tags, sync, rule_guard, consistency. Claims about those rest on imports and size only.

## 1. Four clusters, hardly connected

| Cluster | Scripts | Link to the others |
|---|---|---|
| Deck generator | mine, pool, build, gen_mono, variants, t1_plan, starter_tune, hall_roster, categorize, budget_lands, staples, commander_support, scryfall_bulk, spellbinder_signals | only `ability_tags` (via build, commander_support, t1_plan) |
| Tagger | ability_tags, tag_run, tag_extra, tag_variant, tag_verify, tag_twins, derived_tags | `tag_run` is the hub (imports 9 modules) |
| Tag check | reverse_check, consistency, run_log, placeholder_triage, learning_*, oracle_style_stats, build_*_reference, reader_refs | `reverse_check` imports tag_run, tag_extra, tag_verify and is imported by 7 |
| Guards / sync | tag_guard, rule_guard, rule_lint, sync, tag_audit, run_memory | all import mtg2llm and reverse_check; every one calls run_memory |

## 2. Import cycles

- `mtg2llm <-> reverse_check`
- `consistency <-> run_log`
- `tag_run -> sync -> reverse_check -> tag_run`
- `tag_guard -> reverse_check -> tag_run -> tag_guard`

All hold only through late imports inside functions. Root cause: `reverse_check` is five things in one file (scoring, export, run bookkeeping, report, CLI) and the scorer is what everyone needs. Moving the scorer out breaks three of the four cycles.

## 3. Findings from reading the code

- `reverse_check`: scoring, `export`, `compare`, bookkeeping and report writing in one 540-line file. `READER_RULES` text inside it has drifted from `.claude/agents/tag-blind-reader.md`.
- `_sims` (reader-free scoring) is duplicated in tag_guard and rule_guard (and a variant in mtg2llm).
- `run_memory` and the older `remember` function duplicate the memory-path logic. `tag_guard` logs twice (guard-runs.toon and run_memory).
- `tag_audit` has dead `if False` code. `run_log` carries a one-time KNOWN/GROUPS backfill table.
- `rule_lint`: the REVERSE regexes are broken (already noted in SCRIPTS.md).
- `reader_refs` docstring mentions a nonexistent `export --refs`.
- `build_reminder_fill` and `build_token_reference` each define their own `q()`; build_reminder_fill has an `os.sys.argv` oddity and three modes (API, `--forge`, `--cr`).
- `placeholder_triage`, `learning_merge`, `learning_coverage`, `oracle_style_stats` are one-off analyses, used by nobody; `oracle_style_stats` repeats pool-reading code found elsewhere.
- `tag_run` (655 lines) mixes record building, rendering, reference/approval/sample report writing, QA, redundancy check and CLI; it holds hard-coded APPROVED and REDUNDANCY_OK tables and has a late-import cycle with tagcheck (tag_guard, sync, run_memory, tag_twins).

## 4. Merge candidates, best first

1. **rule_lint into rule_guard** (45 + 53 lines): used only by rule_guard and mtg2llm. Low risk.
2. **Split reverse_check**: move the score (cosine, concept F1, number F1) and `_sims` into `score.py`; keep export/compare/report in reverse_check. Removes the reverse_check cycles with tag_guard, sync and mtg2llm. Medium risk, highest payoff.
3. **Guards in one file** (`guards.py`: tag_guard, rule_guard, rule_lint, sync, tag_audit, about 330 lines) with one run_memory call site. Medium risk; callers are tag_run and `mtg2llm mine`.
4. **consistency + run_log** into `run_records.py` (cyclic, same subject). Drop the KNOWN/GROUPS backfill once confirmed unused.
5. **Reference builders** (build_reminder_fill, build_token_reference, reader_refs) into `reference_files.py` with subcommands `fill`, `tokens`, `readers`. Low risk; one `q()`.
6. **Archive** learning_merge, learning_coverage (finished, other session's data) and fold placeholder_triage and oracle_style_stats into `analysis.py` subcommands.
7. **tag_run**: do not grow it. Split out the report writers (reference/approval/sample) and the QA/redundancy check into a `tag_reports.py`, and move the APPROVED/REDUNDANCY_OK tables to data files.

Not worth merging: build (567), ability_tags (439), tag_extra (824; split by family if it keeps growing). tag_variant, tag_verify, tag_twins stay modules of the tagger. The small deck-generator CLIs (mine, pool, categorize, hall_roster, budget_lands) share no code, so merging saves files only.

## 5. Duplicated helpers (extract to `common.py`) - verified by reading each copy, 2026-10-24

| Helper | Copies | Verdict |
|---|---|---|
| `workdir(run)` | reverse_check, run_log | identical: extract |
| `q(x)` (TOON quoting) | tag_run, build_reminder_fill, build_token_reference | same intent; compare the three bodies once before extracting |
| `snake(s)` | tag_run, tag_verify | identical regex: extract |
| cardsfolder glob (`forge-gui/res/cardsfolder/*/*.txt`) | tag_run (2), tag_twins, build_reminder_fill, build_token_reference, mtg2llm `_load`, oracle_style_stats; ability_tags, pool, staples use their own walk | real duplication: add `common.card_files()` |
| `_sims` | tag_guard (per-unit sims, reads tag records), rule_guard (swaps rule tables in M, restores them), mtg2llm (not read here) | share only the setup (`original_text`, `Index`, `score`); different bodies, so extract the setup as `score.sim_of(...)`, not the function |
| `_load(p)` | rule_guard (json or `{}`), mtg2llm `_load` (builds the card-name vocabulary cache) | NOT duplicates; same name only. Leave |
| `norm` | ability_tags (ability-signature normaliser), tag_twins (Oracle line to template), reverse_check (Oracle text for scoring), spellbinder_signals (card-name key) | four different functions: do NOT merge |
| `parse` | ability_tags (script to signatures), build (deck file to names), variants (deck file to indexed cards) | only build and variants are similar, and both read a deck file with different output shapes. Leave; at most share the line regex |
| `card_text` | ability_tags (name to script text), build (cache wrapper around the ability_tags one) | not duplicated: build calls ability_tags |
| `pool.pkl` load | ability_tags, budget_lands, build, commander_support (2), t1_plan | one line each; extract `common.load_pool()` only for the path, saves nothing else |

Net: the list in the first draft was too broad. Real extractions: `workdir`, `snake`, `q`, `card_files`, the `_sims` setup. Not helpers to merge: `norm`, `parse`, `card_text`, `_load`.

Read now (second pass): the helper bodies above in ability_tags, build, variants, spellbinder_signals, tag_twins, tag_verify, tag_run, reverse_check, run_log, rule_guard, tag_guard, sync, mtg2llm `_load`. Still only skimmed: mine, pool, gen_mono, t1_plan, starter_tune, hall_roster, categorize, budget_lands, staples, commander_support, tag_extra, tag_variant, derived_tags, consistency (no helper claims about them beyond the `pool.pkl` line and the cardsfolder walk, both confirmed by grep).

## 6. Order of work

1. `common.py`: `workdir`, `snake`, `q`, `card_files` only (no behaviour change; compare the three `q` bodies first).
2. `score.py` split out of reverse_check; fix the cycles.
3. rule_lint into rule_guard; run_records; reference_files.
4. Guards consolidation after a full `tag_run.py starter` + `mtg2llm.py mine` shows identical output and scores.
5. Archive one-offs; tag_run report split.

Result: 37 scripts to about 27, import cycles 4 to 0 or 1. Each step is checked by rerunning the guards and comparing scores, as in `SCRIPT_REDUNDANCY.md`.

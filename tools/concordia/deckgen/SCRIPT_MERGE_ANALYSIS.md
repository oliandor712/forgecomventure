# Script connections and merge options (all deckgen + tagcheck .py except mtg2llm.py)

Second pass, 2026-10-24: import scan of 37 scripts plus a read of the code. Builds on `SCRIPT_REDUNDANCY.md` (tagcheck only). Nothing has been merged; each option needs the user's word.

**Read in full or in the relevant parts (third pass 2026-10-24, nothing left skimmed):** all deck-generator scripts (mine, pool, build helpers, gen_mono, variants, t1_plan, starter_tune, hall_roster, categorize, budget_lands, staples, commander_support header and `read`), ability_tags, tag_extra (helpers; the 600-line rule body not audited line by line), tag_variant, tag_verify, tag_twins, derived_tags, tag_run, consistency, reverse_check, run_memory, tag_guard, rule_guard, tag_audit, run_log, reader_refs, rule_lint, placeholder_triage, learning_*, oracle_style_stats, build_reminder_fill, build_token_reference, sync.

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
4. **Do not merge consistency + run_log** (different jobs, see 5b). Break their cycle by moving `stamp()` into `run_log` and drop the KNOWN/GROUPS backfill once confirmed unused.
5. **Reference builders** (build_reminder_fill, build_token_reference, reader_refs) into `reference_files.py` with subcommands `fill`, `tokens`, `readers`. Low risk; one `q()`.
6. **Archive** learning_merge, learning_coverage (finished, other session's data) and fold placeholder_triage and oracle_style_stats into `analysis.py` subcommands.
7. **tag_run**: do not grow it. Split out the report writers (reference/approval/sample) and the QA/redundancy check into a `tag_reports.py`, and move the APPROVED/REDUNDANCY_OK tables to data files.

Not worth merging: build (567), ability_tags (439), tag_extra (824; split by family if it keeps growing). tag_variant, tag_verify, tag_twins stay modules of the tagger. The small deck-generator CLIs (mine, pool, categorize, hall_roster, budget_lands) share no code, so merging saves files only.

## 5. Duplicated helpers (extract to `common.py`) - verified by reading each copy, 2026-10-24

| Helper | Copies | Verdict |
|---|---|---|
| `workdir(run)` | reverse_check, run_log | identical: extract |
| `q(x)` (TOON quoting) | tag_run, build_reminder_fill, build_token_reference | same intent; compare the three bodies once before extracting |
| `snake(s)` | tag_run, tag_verify, tag_extra (`tok`) | identical regex, three copies: extract |
| `params(body)` | tag_run, tag_extra | identical: extract. tag_variant `_params` differs (splits on `|`, strips) - leave |
| deck-file line reader (`^(\d+)\s+([^|]+)\|?(\S*)`) | variants.parse, starter_tune.main_cards, hall_roster.commander, build.parse, t1_plan.used_elsewhere, commander_support.read, mine/pool popularity count | same format, six different return shapes: extract one `deckfile.read(path)` -> sections of (count, name, edition) and rebuild the callers on it |
| `identity(c)` (colour identity) | pool.py, spellbinder_signals, mine.py (`ci`, inline variant) | pool and spellbinder identical: extract to `common`; mine.py uses `data[cards]` directly, switch it |
| `card_power(p, ed)` / `power_of` | starter_tune, variants | same logic (variants also returns the rarity): keep variants' and import it in starter_tune |
| cardsfolder glob (`forge-gui/res/cardsfolder/*/*.txt`) | tag_run (2), tag_twins, build_reminder_fill, build_token_reference, mtg2llm `_load`, oracle_style_stats; ability_tags, pool, staples use their own walk | real duplication: add `common.card_files()` |
| `_sims` | tag_guard (per-unit sims, reads tag records), rule_guard (swaps rule tables in M, restores them), mtg2llm (not read here) | share only the setup (`original_text`, `Index`, `score`); different bodies, so extract the setup as `score.sim_of(...)`, not the function |
| `_load(p)` | rule_guard (json or `{}`), mtg2llm `_load` (builds the card-name vocabulary cache) | NOT duplicates; same name only. Leave |
| `norm` | ability_tags (ability-signature normaliser), tag_twins (Oracle line to template), reverse_check (Oracle text for scoring), spellbinder_signals (card-name key) | four different functions: do NOT merge |
| `parse` | ability_tags (script to signatures), build (deck file to names), variants (deck file to indexed cards) | only build and variants are similar, and both read a deck file with different output shapes. Leave; at most share the line regex |
| `card_text` | ability_tags (name to script text), build (cache wrapper around the ability_tags one) | not duplicated: build calls ability_tags |
| `pool.pkl` load | ability_tags, budget_lands, build, commander_support (2), t1_plan | one line each; extract `common.load_pool()` only for the path, saves nothing else |

Net: the list in the first draft was too broad. Real extractions: `workdir`, `snake`, `params`, `q`, `card_files`, `identity`, the deck-file reader, the `_sims` setup. Not helpers to merge: `norm`, `parse`, `card_text`, `_load`.

## 5b. New findings from the third pass

- `mine.py` and `pool.py` run on import (no `main()`), so nothing can import them; `build.py` (hub of the deck cluster, imported by gen_mono and starter_tune) also runs `pickle.load` at import. A shared module must not do that. Wrap `mine` and `pool` in `main()` before any merge.
- `consistency.py` is not bookkeeping: it is the reader-agreement metrics (V1-V4, S1) and calls `reverse_check` for `norm`, `toks`, `concepts`, `KWRX`, `tolerate`, `is_typeline`, `workdir`. Merging it with `run_log` (bookkeeping) mixes two jobs. Better: the scorer split (`score.py`) takes what both need; `run_log` takes its `stamp()` call from a small `stamp.py`/`common`, and the `consistency <-> run_log` cycle (run_log calls `consistency.stamp` and `compare`) goes away by moving `stamp()` into `run_log`. Keep the two files.
- `staples.py` and `pool.py` each walk cardsfolder separately for different fields (T: lines, PT:) - fold into the shared `card_files()` only.
- `tag_extra` (823), `tag_variant`, `derived_tags` (89), `commander_support` have no helper overlap beyond the rows above; keep. Not audited: the rule bodies of `tag_extra.extra` (about 600 lines).
- `hall_roster`, `categorize`, `budget_lands`, `t1_plan` share nothing but the deck-file reader and `pool.pkl` path.

## 5c. Step 1 status (2026-10-24): done, uncommitted

`common.py` holds `workdir`, `snake`, `params`, `q`, `q_line`, `card_files`, `identity`. The `q` copies were NOT identical: `tag_run` quotes empty values and values with a comma, quote or backslash (`q`); the two builders strip newlines and do not quote on a backslash (`q_line`). Both kept, so no output changes. Rewired: tag_run, tag_verify, tag_extra, tag_twins, reverse_check, run_log, build_reminder_fill, build_token_reference, oracle_style_stats, mtg2llm, pool, spellbinder_signals. Checked: all scripts compile; `tag_run.py starter` leaves every generated file identical; `build_token_reference.py` output identical; `consistency.py selftest` ok; mtg2llm, reverse_check, run_log, sync, oracle_style_stats, spellbinder_signals import. Not run: `pool.py`, `build_reminder_fill.py` (network), `ability_tags.py`.

## 5d. Step 2 status (2026-10-24): done, uncommitted

`tagcheck/score.py` (170 lines) holds the scorer: `norm`, `tolerate`, `toks`, `concepts`, `KWRX`, `f1`, `mf1`, `numbers`, `Index`, `score`, `is_typeline`, `clean_reco`, `original_text`, `band`, `evaluate`, `summarize`. `reverse_check` (535 to 374 lines) re-exports them, so old `RC.<name>` calls still work. `consistency`, `learning_merge`, `mtg2llm`, `rule_guard`, `tag_audit`, `tag_guard` now call `score` for those names. `rule_guard` no longer imports `reverse_check` at all. Checked: `reverse_check selftest`, `consistency selftest`, `mtg2llm selftest` outputs byte-identical to HEAD; `tag_run.py starter` output identical.

Cycles: `score` itself imports nothing from the project at load time (`original_text` imports tag_run/tag_verify on first call). `consistency <-> run_log` and `tag_run -> sync -> reverse_check -> tag_run` are unchanged; `tag_guard`, `sync`, `tag_audit` and `mtg2llm` still import `reverse_check` for `tag_blind`, `starter_records`, `is_pre6` and `T`, so `reverse_check -> tag_run -> tag_guard` still exists. Moving those three helpers (record building) out of `reverse_check` is the next cut; step 2 did not break 3 of 4 cycles as first estimated.

## 5e. Step 3 part 4 (2026-10-24): cycles cut, uncommitted

New `tagcheck/cards.py` (41 lines): `tag_blind`, `starter_records`, `pre6_only`, `is_pre6`, moved unchanged out of `reverse_check` (which re-exports them). `mtg2llm`, `sync`, `tag_guard`, `tag_audit` use `cards` (and `tag_run` directly); none imports `reverse_check` any more. `stamp()` moved from `consistency` into `run_log`; `consistency` no longer imports `reverse_check` (uses `common.workdir`, `score`, `run_log.stamp`). `run_log` no longer imports `consistency`: its `compare` subcommand and the compare half of `backfill` (the `GROUPS` table, a one-time job already logged) were removed; comparisons are logged by `consistency.py compare --runs ...` as before.

Measured with an AST import graph over all 39 scripts (late imports included): strongly connected groups went from 2 (and 4 cycles by hand count) to 1: `tag_run` <-> {`sync`, `tag_guard`} <-> {`cards`, `mtg2llm`, `rule_guard`, `score`}. The remaining edge is `tag_run.main()` calling the guards, `sync` and `run_memory` after a run. It disappears when `main()` and the report writers leave `tag_run` (step 6, driver module); the guards then depend on `tag_run` as a data layer only.

Checked: `reverse_check`, `consistency`, `mtg2llm` selftests byte-identical to HEAD; `tag_run.py starter` identical; `run_log.py show`, `sync.py` run.

## 5f. Step 3 parts 1 and 2 (2026-10-24): done, uncommitted

- `rule_lint.py` is merged into `rule_guard.py` (`lint_rules`, `lint`, `python3 rule_guard.py lint`); `mtg2llm.rules()` late-imports `rule_guard`. The broken REVERSE regexes are kept as they were (marked in a comment), because a fix changes which rules are quarantined and so the render output; that is a separate decision. `rule_guard.py lint` output is identical to the old `rule_lint.py` (114 hits in render_rules.json).
- `reference_files.py` (`fill [--forge|--cr]`, `tokens`, `readers`) replaces `build_reminder_fill.py`, `build_token_reference.py` and `reader_refs.py`. `readers` output (all four files plus the leak scan) and `tokens` output are identical to the old scripts; the only difference is the generator name in the TOKEN_REMINDER_TEXT.toon header. `fill` needs the network and was only checked for import, argument handling and `missing()` (74 names); the `os.sys.argv` oddity is gone.
- Docs that named the old scripts (SCRIPTS.md, INDEX.md, HANDOVER.md, toolbox.py) are updated; regenerate TOOLBOX.md with `toolbox.py` after the commit.
- Part 3 (drop the KNOWN/GROUPS backfill in run_log) is still open for the user's decision.
- Checked: compileall, the three selftests byte-identical, `tag_run.py starter` leaves the tag files unchanged.

## 5g. Steps 4, 5 and 6 status (2026-10-24): done, uncommitted

- **Step 4:** `main()` added to `mine` and `pool`; `deckfile.py` created and six deck-file callers moved onto it.
- **Step 5:** `tagcheck/guards.py` replaces `tag_guard`, `rule_guard`, `sync`, `tag_audit` (and `rule_lint`). `lint_rules` lives in `mtg2llm.py` so guards imports mtg2llm, not the reverse. Verified: `tag_run.py starter` 353 same, no tag file changed (only the `TAG_GAPS.toon` header names guards.py); `mtg2llm.py mine` and `guards.py lint|sync|audit` byte-identical; three selftests byte-identical.
- **Step 6:** `learning_merge`, `learning_coverage` archived to `tagcheck/archive_20261024/`; `placeholder_triage` and `oracle_style_stats` folded into `tagcheck/analysis.py`; `tag_run` split: `tag_reports.py` holds the report writers, `qa`, `redundancy` and the starter driver; `tag_run.py` keeps record/render/`card` and dispatches `starter` by module name.
- **Result:** 34 scripts (was 39 at the third pass); AST import graph (late imports included, dispatch by `importlib` name excluded) has **0 cycles**. Not done: moving the `APPROVED`/`REDUNDANCY_OK` tables to data files (they stay as constants in `tag_reports.py`).

## 6. Order of work (revised after the third pass)

1. `common.py`: `workdir`, `snake`, `params`, `q`, `card_files`, `identity` (no behaviour change; compare the three `q` bodies first).
2. `score.py` split out of reverse_check (scoring, `norm`, `toks`, `concepts`, `KWRX`, `tolerate`, `_sims` setup); point consistency, guards and mtg2llm at it. Breaks 3 of 4 cycles.
3. `stamp()` into run_log (breaks the 4th cycle); rule_lint into rule_guard; `reference_files.py`.
4. Deck cluster: add `main()` to `mine` and `pool`, then `deckfile.py` reader and swap the six callers one by one (each deck script reruns with identical output: compare the written file with the committed one).
5. Guards consolidation after a full `tag_run.py starter` + `mtg2llm.py mine` shows identical output and scores.
6. Archive one-offs; tag_run report split.

Result: 37 scripts to about 28 (consistency stays, one new `deckfile.py`), import cycles 4 to 0. Each step is checked by rerunning the guards and comparing scores, and for the deck cluster by diffing the generated files (`pool.pkl` content, `mined.json`, `budget_lands.json`, `t1_fresh.json`, `CATEGORIES.toon`).

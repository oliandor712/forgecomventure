# Script connections and merge options (all deckgen + tagcheck .py except mtg2llm.py)

Generated 2026-10-24 from an import scan of 37 scripts. Builds on `SCRIPT_REDUNDANCY.md` (tagcheck only); this file covers all of `deckgen/`. Nothing has been merged; each option needs the user's word.

## 1. Four clusters, hardly connected to each other

| Cluster | Scripts | Link to the others |
|---|---|---|
| Deck generator | mine, pool, build, gen_mono, variants, t1_plan, starter_tune, hall_roster, categorize, budget_lands, staples, commander_support, scryfall_bulk, spellbinder_signals | only `ability_tags` (via build, commander_support, t1_plan) |
| Tagger | ability_tags, tag_run, tag_extra, tag_variant, tag_verify, tag_twins, derived_tags | `tag_run` is the hub: imports 9 modules |
| Tag check | reverse_check, consistency, run_log, placeholder_triage, learning_*, oracle_style_stats, build_*_reference, reader_refs | `reverse_check` imports tag_run, tag_extra, tag_verify (tagger) and is imported by 7 |
| Guards / sync | tag_guard, rule_guard, rule_lint, sync, tag_audit, run_memory | all import mtg2llm and reverse_check; every one calls run_memory |

Hubs: `reverse_check` (used by 7), `mtg2llm` (6), `run_memory` (6), `ability_tags` (4), `tag_extra` (3), `tag_run` (3).

## 2. Import cycles (the real coupling problem)

- `mtg2llm <-> reverse_check` (each imports the other; one is imported lazily).
- `consistency <-> run_log`.
- `tag_run -> sync -> reverse_check -> tag_run` (sync renders the tagger's output, the tagger calls sync at its end).
- `tag_guard -> reverse_check -> tag_run -> tag_guard`.

These work only because of late imports inside functions. Merging within a cycle removes the cycle; merging across clusters does not.

## 3. Merge candidates, best first

1. **rule_lint into rule_guard** (45 + 53 lines). rule_lint is used by rule_guard and mtg2llm only; one quarantine/accept module `rule_checks.py`. Low risk.
2. **tag_audit + sync into one `tag_checks.py`** (62 + 65). Both import mtg2llm, reverse_check, run_memory, write a gap file, and run after the tagger. Also `tag_guard` (100) shares `_sims` with rule_guard. Option: `guards.py` holding tag_guard, rule_guard, rule_lint, sync, tag_audit as sections (about 330 lines), one `run_memory` call site. Medium risk (callers: tag_run, mtg2llm `mine`).
3. **consistency + run_log** (234 + 217). Cyclic, same subject (reader run records); one `run_records.py`.
4. **placeholder_triage, learning_merge, learning_coverage, oracle_style_stats** (95 + 76 + 64 + 100): one-off analysis tools, used by nobody. Merge into `analysis.py` with subcommands, or archive the learning_* pair (data from another session, finished).
5. **build_reminder_fill + build_token_reference + reader_refs** (137 + 60 + 81): all build a reference file for readers. One `reference_files.py` with `fill`, `tokens`, `readers` subcommands. Low risk; `q()` is duplicated in two of them.
6. **tag_variant into tag_run**: tag_variant (208) only post-processes tag_run output and imports tag_extra; tag_twins (214) and tag_verify (166) likewise are called only by tag_run. Merging all would make a 1,400-line tag_run: not recommended; keep as modules.
7. **mine, pool, categorize, hall_roster, budget_lands** (41-101 lines each, no cross imports): small CLIs of the deck generator; could share one `deckgen_cli.py`, but they have no shared code, so merging only saves files, not logic.

Not worth merging: `build` (567) and `ability_tags` (439) (large, stable), `tag_extra` (824, big and growing; split instead), `reverse_check` (540; the largest hub, better to split scoring from the export/compare CLI than to grow).

## 4. Duplicated helpers (extract, do not merge scripts)

- `norm` in ability_tags, spellbinder_signals, tag_twins, reverse_check: four text normalisers.
- `parse` (ability_tags, build, variants) and `card_text` (ability_tags, build): card script parsing done twice.
- `snake`, `params`, `provides`, `q`, `stats`, `identity`, `load`, `workdir`, `role`: same name in two or three scripts; `workdir` in reverse_check and run_log should be one function.
- `_load` / `_sims` repeated in rule_guard, tag_guard and mtg2llm.
Suggestion: one `common.py` for `norm`, `snake`, `workdir`, JSON/toon load and card-script parse.

## 5. Suggested order (smallest safe steps)

1. `common.py` for the duplicated helpers (no behaviour change).
2. rule_lint into rule_guard; consistency + run_log; reference builders into one file.
3. Guards/sync consolidation after a full `tag_run.py starter` plus `mtg2llm.py mine` check shows identical output.
4. Archive learning_* and the unused one-shot analysis tools.
Result: 37 scripts to about 27, import cycles 4 to 1 (mtg2llm/reverse_check stays, handled by moving shared score code into `common.py`). Every step is checked by rerunning the guards and comparing scores, as in `SCRIPT_REDUNDANCY.md`.

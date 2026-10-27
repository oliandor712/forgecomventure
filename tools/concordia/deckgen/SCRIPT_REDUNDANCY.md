# Redundancy and merge candidates (deckgen and tagcheck, mtg2llm.py excluded)

Method: AST scan of 37 scripts for same-name functions, identical bodies (strings masked) and the local import graph, then a read of the headers. Nothing was changed; this is a proposal. Order is by payoff.

## 1. Merge now (same code in two places)

| Candidates | Evidence | Proposal |
|---|---|---|
| `tag_guard._sims` and `rule_guard._sims`, plus the render loop in `sync.gaps` and `tag_audit` | Each re-implements "tag records -> M.render -> RC.score vs Oracle". `tag_guard` and `rule_guard` are near copies (same index, same sim call). | One helper `tagcheck/score.py` (`card_sims(records)`) used by all four. Saves ~40 lines and removes the risk of the scores drifting apart. |
| `tag_guard.apply` and `rule_guard.apply` | Same shape: load stored, score both, merge, print tally, save. | Keep two merge rules, share the load/score/tally/log wrapper (this also gives `rule_guard` the `guard-runs.toon` log it lacks). |
| `pool.identity` and `spellbinder_signals.identity` | Identical bodies. | Move to `power_scorer` (both already import it). |
| `starter_tune.role` and `variants.role` | Identical bodies. | Move to `build.py` (both already import `build`/`gen_mono`). |
| `tag_extra.params` and `tag_run.params` | Identical bodies. | Keep in `tag_extra`; `tag_run` imports it. |
| `scryfall_bulk.get` and `build_reminder_fill.get` | Both are a rate-limited, retrying Scryfall GET (5 vs 4 retries, different headers). | `build_reminder_fill` calls `scryfall_bulk.get`. |

## 2. Consolidate by name (not identical, same job)

- **`norm`** exists four times with four meanings (ability signature, line template, card-name key, Oracle text). Rename to what they do (`signature`, `line_template`, `name_key`, `oracle_norm`) so a reader never imports the wrong one; merge only `spellbinder_signals.norm` into the shared card-name key used by the deck tools.
- **`tag_twins.norm` vs `reverse_check.norm`**: both lower-case Oracle lines and mask digits and mana; check whether `tag_twins` can call `reverse_check.norm`.
- **`card_text`** in `ability_tags` and `build`: `build` is a cache wrapper around `ability_tags.card_text`. Fine; leave.
- **`workdir`** in `reverse_check` and `run_log`: same run-directory lookup; keep one in `run_log`.
- **`lint`** in `consistency` (style linter) and `rule_lint` (rule tables): different jobs; rename `consistency.lint` to `style_lint`.

## 3. Script-level overlaps (merge into one entry point)

- **`tag_audit.py`, `sync.py`, `rule_lint.py`**: all three are reader-free checks over tags and rules. Fold them into one `tagcheck/check.py` with subcommands (`audit`, `gaps`, `lint`) over a shared card loader. `sync` and `tag_audit` already load the same starter records.
- **`tag_guard.py` and `rule_guard.py`**: one `guards.py` with `tags` and `rules`, after item 1.
- **`learning_merge.py` and `learning_coverage.py`**: both work on the other session's blind-test package; one script with two subcommands.
- **`consistency.py`, `run_log.py`, `placeholder_triage.py`**: all read finished reader runs from `~/tagcheck_runs`. They import each other (`consistency` and `run_log` call each other), which is a sign they are one module. Merge into `reader_runs.py` (`consistency`, `log`, `triage`).
- **`build_reminder_fill.py` and `build_token_reference.py`**: both build a `.toon` reference for the blind reader in `ai_lab/`; one `build_reference.py` with `reminders` and `tokens`.
- **`tag_variant.py`**: a post-pass of rules S01-S09/S15 that imports `tag_extra`. Candidate to fold into `tag_extra` as its post-pass section (it has its own `TAG_VARIANT=off` switch, which must survive).

## 4. Import cycle to break

`tag_run` imports `sync`; `sync` imports `reverse_check`; `reverse_check` imports `tag_run`. It works only because the imports are lazy or late. Fix: `sync` and the guards import a small `starter_records` loader, not `reverse_check`, or `tag_run` calls `sync` through a function argument.

## 5. Leave alone

The deck pipeline (`mine` -> `pool` -> `build` -> `gen_mono`/`variants`/`starter_tune`) is a clean chain with one job per script. `ability_tags`, `commander_support`, `staples`, `budget_lands`, `hall_roster`, `categorize`, `t1_plan`, `scryfall_bulk`, `spellbinder_signals` and `derived_tags` have no overlap beyond the single helpers above.

## Suggested order

1. Items in section 1 (small, safe, no behaviour change).
2. Shared `score.py` plus guard wrapper (section 1 first two rows), then verify with the starter score (.736 expected) and the guard simulation.
3. Section 3 merges one group at a time, updating `SCRIPTS.md` each time.
4. The cycle fix last.

# Archived verbatim from HANDOVER.md on 2026-10-27

## PREVIOUS (2026-10-26, end of session): cleanup done, NEXT SESSION = DECK BUILDING (read first)
**Repo state: committed and pushed to `campaign-design` at session end** (no force). Nothing live was changed: no edits to enemies.json, live decks, forge-core/game/ai.

### What this session did (details: `tools/agents/logs/log-patchnotes.toon`, `log-code-analyses.toon`, memory `session_2026-10-26_cleanup.md`)
- /code-review high: 8 findings. Fixed: gaps_status only for render/scan/mine and no false `{X}` open rows; `_warn_pool_stale` also hashes staples.json; `refresh_cat` survives missing pool.pkl/pool_meta.json; fused spaces in `tag_roles`. Closed: `norm_roles` (already reports `roles_dropped`). Skipped on purpose: `ftags_of` whole-pool load; `effective_cmc` X/alt-cost penalty (scoring choice, user decides).
- /simplify of docs and scripts without stripping content; dead code removed (see patchnotes); `pool_tags.pkl` per-card tag cache (`pool.py --check | --if-stale | --cat`).
- Docs: older HANDOVER and MEETING_FEEDBACK blocks moved verbatim to `tools/agents/archive/` with pointers; START.md step 5 is the single read-first list.
- render_rules: `CANON_FIX` in `tagcheck/mtg2llm.py` `rules()` overrides two weak mined canons (`affected_type:creature`, Treasure etb). `render_rules.json` itself is untouched. Do NOT run `mtg2llm.py mine --force`: re-mine here gives 2942 patterns vs 3223 and worse canons.
- Regenerated data reviewed and judged normal (staples.json, POOL_GAPS.toon, ABILITY_TWINS.json, verdicts.json, render_rules.json).

### NEXT SESSION: deck building
Start with the strategies work already in place, then build:
1. Run `python tools/concordia/deckgen/pool.py --check`; if stale, `--if-stale` (fast with the tag cache). The pool is stale right now because code and tagger files changed: rebuild before building.
2. Archetype first, then roles: use `tools/agents/reference/ARCHETYPES.toon` (45 archetypes, baselines, crossover) and `tools/concordia/strategies/strategy_fit.py` (`baseline_hit`, `baseline_min`).
3. `tools/concordia/deckgen/build.py` (tiers 2-5) already fills recursion and protection baselines. Still open from the 2026-10-26 block below: switch quotas from role tag `removal` to `remove:*`; ramp/draw baselines and niche crossover are not yet read by build.py; diff dry-run decks against live decks before any rebuild (`build.py --dry decks.json`; 2 decks skipped because Ertai and Sengir are not in the pool).
4. No dry/trial deck builds without the user's approval; do not edit live decks or enemies.json without the user's word. Start by asking which tier/archetype to build first.
5. Waiting on the user from earlier: W starter rejects, tag fixes (War Machine, Wreck Remover, Expert-Level Safe, Parallel Lives), stale W verdict cache, U/B/R/G reader reviews, the Claude Docs "core tags by archetype" comments.

### Open, not blocking
- Data-size options not accepted: gitignore POOL_GAPS.toon, drop empty-category staples.json entries, compact verdicts.json.
- 23 open rows in `tags/MTG2LLM_GAPS.toon`; SCRIPT_REDUNDANCY.md not updated; some startup docs and CONTEXT.md still carry stale content; reviewer's skipped refactors and unused imports.
- `sync_check.py verify` crashed with WinError 123 earlier; run `sync_check.py manifest` and report.

### Gotchas
- cwd resets between Bash calls; use repo-root paths. Files edited with CRLF (mtg2llm.py): patch with CR-tolerant code.
- PYTHONIOENCODING=utf-8 before tool calls.

(The 2026-10-26 "strategies master list" block moved verbatim to `tools/agents/archive/HANDOVER_2026-10-26_previous.md`.)


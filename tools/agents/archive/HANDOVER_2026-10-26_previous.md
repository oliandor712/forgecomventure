## PREVIOUS (2026-10-26): strategies master list, engine baselines, tag docs (read first)
**Repo state: pushed.** The folder had no .git; it was re-attached (git init, origin = oliandor712/forgecomventure, fetched campaign-design, `reset --mixed`) and this session's work is commit 8ab92da946d on `campaign-design` (pushed, no force). `sync_check.py verify` crashed with WinError 123 earlier; untested since.

### Goal
Replace the 35 deck archetypes with a master list based on Spellweave (now 45, `theft` added). Archetype is chosen first at deck creation; cards then fill its roles. Engine roles (recursion, ramp, card draw, protection) are baseline roles. The user reviews the Claude Docs doc "core tags by archetype" (https://claude.ai/artifact/AUBPzwVViYMGernER4xRE8, doc id 4cadbca0-54db-44a4-8d09-dfb051fcb3e1) and comments; answer each comment by `create` of an utterance under the thread root (never ArtifactComments). Chat reply afterwards: one short line.

### Decisions (user)
- Removal is one family `remove:*`; a card counts 1 whether it hits one creature or any number.
- Create new tags for missing categories; niche subcategory with crossover parents; protection baseline role. "apply"/"proceed"/"yes" approved all proposals.
- Latest asks: condensed archetype + engine goals everywhere builder and readers look; update all scripts with the new data and all tag docs.

### Done
1. `tools/concordia/strategies/build_strategies.py` (source of truth): role signal `removal`->`remove`; dead signals fixed; new tag-backed roles (ench_payoff, gift_all, goad); `STUB_SIG` for treasure/wheels/impulse_draw/legends_matter; archetype `theft`; `HOMES` support roles (12); `BASELINE` protection 3-6 and ramp sig + fixing; `PROTECTION_BY_ARCHETYPE`; `NICHE` crossover on 14 archetypes; `write_ref()` writes `tools/agents/reference/ARCHETYPES.toon`. Run: 45 archetypes, 99 source rows.
2. `strategy_fit.py`: `_role_hits`, `fit()` adds half of crossover parents for niche archetypes; new `baseline_hit(ftags, role)` and `baseline_min(role, ids)`.
3. `deckgen/text_tags.py` (new) + `pool.py` merge + `pool.pkl` patched: goad, wheels, gift_all, ench_payoff, legend_payoff (regex, unreviewed).
4. `deckgen/build.py` tiers 2-5: after the role quotas, fills recursion and protection baselines (with uplifts) via strategy_fit. `build.py --dry decks.json` exit 0 (2 decks skipped, commanders not in pool). Dry output NOT diffed against live decks.
5. `tagcheck/glance.py`: `engine_goals()` and batch field `engine_goals`.
6. Linked ARCHETYPES.toon from INDEX.md, CONTEXT.md, deck_building_for_readers.toon, deck-builder / forge-ai-lab / deck-balance-lab briefs. Appended update sections to deckgen/SCRIPTS.md, TAG_UTILITY_DECKBUILDER.md, docs/Adventure/Campaign/AI_TAGS_REFERENCE.md.
7. Logs: 4 rows added to `tools/agents/logs/log-code-analyses.toon` (N=20). Memory: `strategies_archetypes.md` + MEMORY.md line.

### Open
- Switch build.py/starter_build.py quotas from role tag `removal` to `remove:*`; retire old ftag `removal` (196 bodies).
- Wire `recursion_by_archetype` is done via baseline_min; ramp/draw baselines and niche `crossover` are not yet read by build.py.
- Measure real crossover overlaps, drop weak parents; spot-check the five text tags.
- Diff dry-run decks vs live decks before any rebuild; do not edit live decks or enemies.json without the user's word.
- Doc still stale: engine-table board-wipe row and "Add a board wipe tag" checkbox (role tag `wipe` has 771 cards); inline code formatting lost in blocks .1917 and .9500; doc could be updated to what was applied.
- TAG_LINKS.md not updated. human_logic.toon row for the recursion baseline only if the user approves.
- Waiting on user from earlier: W starter rejects, tag fixes (War Machine, Wreck Remover, Expert-Level Safe, Parallel Lives), stale W verdict cache, U/B/R/G reader reviews (subagents need approval; `deck-builder` agent type may be unavailable).

### Gotchas
- Docs MCP `query` needs `under` as object ref `{"object":"utterance","id":...}`; `create` utterance payload `value.{body,parent}`.
- Heredoc Python mangles `
`; use chr(92) or write files with the Write tool.
- cwd resets between Bash calls; use repo-root paths.


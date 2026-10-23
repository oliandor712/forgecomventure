# Toolbox: the shared reference for every agent

Generated 2026-10-23 23:30Z at commit 27a43c2b9ba on branch campaign-design. **Tools stamp: `8146ad802414`.** Data stamp: `e914fcb2a33e`.
<!-- tool hashes: tools/agents/toolbox.py:a067a5da tools/agents/docpush.py:c4c2249e tools/agents/sync_check.py:699504d1 tools/agents/clone_verify.py:e1b4cc04 tools/concordia/deckgen/tag_run.py:39097ab0 tools/concordia/deckgen/tagcheck/reverse_check.py:4f49bae1 tools/concordia/deckgen/tag_twins.py:9f3a1e90 tools/concordia/deckgen/tagcheck/run_log.py:644acf1c tools/concordia/deckgen/tagcheck/consistency.py:b75dc8a0 tools/concordia/deckgen/tagcheck/placeholder_triage.py:d9afccbb tools/concordia/deckgen/tagcheck/oracle_style_stats.py:aed12a51 tools/concordia/deckgen/tagcheck/learning_merge.py:5c4c1d7f tools/concordia/deckgen/tagcheck/learning_coverage.py:1edc4504 tools/concordia/deckgen/tagcheck/build_reminder_fill.py:29cf2b6c tools/concordia/deckgen/tagcheck/build_token_reference.py:b7d0906c tools/agents/human_logic.toon:12bed136 tools/concordia/suite/sim_suite.py:4391b919 tools/concordia/suite/README.md:68719bd3 tools/concordia/balance_lab/push_records.sh:e88a8057 tools/concordia/balance_lab/run_batch.py:d552531a tools/concordia/balance_lab/run_foreground.sh:77fc02e6 tools/concordia/balance_lab/run_logs.py:f7a2eb5e tools/concordia/balance_lab/make_report.py:474929e0 tools/concordia/balance_lab/build_queue.py:23ea8c65 tools/concordia/balance_lab/BonusSim.java:0787eec1 tools/concordia/sim/setup.sh:37d04850 tools/concordia/sim/run.sh:925da916 tools/concordia/ai_lab/phase_digest.py:afd39fc8 tools/concordia/archetype_rules.py:d32de237 tools/concordia/tier1_rules.py:47659a5e tools/concordia/deckgen/ability_tags.py:b44a8a7a tools/concordia/deckgen/commander_support.py:2979c519 tools/concordia/deckgen/t1_plan.py:7f00d016 tools/concordia/deckgen/HANDOFF_DECKBUILDER.md:beba89ab tools/concordia/deckgen/build.py:5793beb9 tools/concordia/deckgen/pool.py:d8162a22 tools/concordia/deckgen/variants.py:0ccc5047 tools/concordia/deckgen/starter_tune.py:a60485ff tools/concordia/deckgen/gen_mono.py:914743c8 tools/concordia/deckgen/hall_roster.py:3f50f572 tools/concordia/deck_tier.py:69e511a6 tools/concordia/maps/check_doors.py:df3fb9e5 -->

## Start of every turn (all agents)
1. At the start of a session: `git fetch origin campaign-design && git merge origin/campaign-design` (if the clone is shallow: `git fetch --unshallow origin campaign-design`).
2. `python3 tools/agents/toolbox.py --check`. If it prints STALE, pull again; if it is still STALE, tell the main session which tools changed.
3. Read `tools/agents/CONTEXT.md` (authority, commit ownership) and your brief. Then work.
4. Push only when the user says 'push' (documents: `python3 tools/agents/docpush.py <paths>`; records: `PUSH_APPROVED=1 tools/concordia/balance_lab/push_records.sh <paths>`). Never force-push, never open a PR, only branch `campaign-design`.

## Tools (last commit that changed each)

| tool | used by | what it does | last change |
|---|---|---|---|
| `tools/agents/CONTEXT.md` | all | shared rules, authority, commit ownership, agent table, recent updates: read first, every turn | 388fcadcedc 10-23 15:51Z |
| `tools/agents/AGENT_KNOWLEDGE.md` | all | compiled pitfalls, conventions, unfinished work and next steps from the earlier agents | 248c73877b7 10-21 14:39Z |
| `tools/agents/toolbox.py` | all | builds TOOLBOX.md and the tools stamp; --check says whether the checkout is current | 58e019fdcee 10-23 16:34Z |
| `tools/agents/docpush.py` | main | pushes document-level files only (reports, checklists, plain .md); refuses code, data and instruction files | 438fcbb12c1 10-23 14:59Z |
| `tools/agents/sync_check.py` | main | session handover: verify / manifest (MANIFEST.toon) | f5536a45e71 10-23 17:28Z |
| `tools/agents/clone_verify.py` | main | checks a fresh checkout is ready (tools, human_logic, mtgish data, tag_run) | 27a43c2b9ba 10-23 19:28Z |
| `tools/concordia/deckgen/tag_run.py` | main | tagging run: starter / card; writes tags/STARTER_TAGS*.{toon,md}, NEW_TAGS_FOR_APPROVAL.md; needs MTGISH_DATA | a2b2c55ed4d 10-23 16:52Z |
| `tools/concordia/deckgen/tagcheck/reverse_check.py` | main | blind reverse tag check: export / compare / selftest | cd491447d67 10-23 22:21Z |
| `tools/concordia/deckgen/tag_twins.py` | main | ability-line twin index (tags/ABILITY_TWINS.json): build / card / text / stats; tag_run.py rebuilds it and prints twins in `card` | cf7223dfe25 10-23 16:34Z |
| `tools/concordia/deckgen/tagcheck/run_log.py` | main | reader-run manifests, append-only RUN_LOG.jsonl, bundles: record / compare / bundle / backfill / show; reverse_check and consistency call it | 58e019fdcee 10-23 16:34Z |
| `tools/concordia/deckgen/tagcheck/consistency.py` | main | reader consistency scores (V1-V4, S1, A) and the tags sha1 stamp | d8d5bbe3099 10-23 17:12Z |
| `tools/concordia/deckgen/tagcheck/placeholder_triage.py` | main | placeholder triage for reader output (PLACEHOLDER_TRIAGE.md) | 388fcadcedc 10-23 15:51Z |
| `tools/concordia/deckgen/tagcheck/oracle_style_stats.py` | main | Oracle style statistics for the reader grammar | d0080bbc8d3 10-23 11:58Z |
| `tools/concordia/deckgen/tagcheck/learning_merge.py` | main | merges reader learning notes | d0080bbc8d3 10-23 11:58Z |
| `tools/concordia/deckgen/tagcheck/learning_coverage.py` | main | learning gap coverage report | ac5e8e81a35 10-23 15:58Z |
| `tools/concordia/deckgen/tagcheck/build_reminder_fill.py` | main | builds the keyword reminder-text fill table | 5d29447e550 10-22 15:21Z |
| `tools/concordia/deckgen/tagcheck/build_token_reference.py` | main | builds the token reference | 46e402eb956 10-22 15:17Z |
| `tools/agents/human_logic.toon` | all | the user's own deck-building, balance and AI rules; a rule beats a metric | b213f198b5c 10-23 16:51Z |
| `tools/concordia/suite/sim_suite.py` | sim workers, main | THE simulation program: setup / run / plan / status / report; archetype cells, adaptive stop, phase logs, digests, push | ac5e8e81a35 10-23 15:58Z |
| `tools/concordia/suite/README.md` | sim workers | how to use the suite, its stop rules and the limit-the-total levers | 02130fc55ee 10-21 13:00Z |
| `tools/concordia/balance_lab/push_records.sh` | all | safe push of named paths (detached HEAD, races, no force); needs PUSH_APPROVED=1, set only after the user says push | 388fcadcedc 10-23 15:51Z |
| `tools/concordia/balance_lab/run_batch.py` | legacy | old per-deck batch runner (old record files only) | 526a2d38deb 10-21 13:50Z |
| `tools/concordia/balance_lab/run_foreground.sh` | legacy | old foreground chunk wrapper for run_batch.py | 80639974b2d 10-21 06:01Z |
| `tools/concordia/balance_lab/run_logs.py` | legacy | aggro-vs-ramp / starter-vs-midrange phase-logged pairings that keep raw logs | 731ea64184e 10-21 05:54Z |
| `tools/concordia/balance_lab/make_report.py` | balance lab | merges every records*.csv into REPORT.md (old record family) | ac5e8e81a35 10-23 15:58Z |
| `tools/concordia/balance_lab/build_queue.py` | balance lab | QUEUE.toon from the old records; also provides archetype() | ac5e8e81a35 10-23 15:58Z |
| `tools/concordia/balance_lab/BonusSim.java` | sims | the headless game engine wrapper; writes the phase log (GAME header, mulligan, AI rows) | 526a2d38deb 10-21 13:50Z |
| `tools/concordia/sim/setup.sh` | sims | builds the sim classpath and the test-only AI overlay (SIM_ACTIVE.txt); SIM_REBUILD=1 after Java changes | 9a0fa22559f 10-21 06:33Z |
| `tools/concordia/sim/run.sh` | sims | runs a sim class; SIM_JAVA_OPTS adds JVM options | 959567c7f56 10-21 05:33Z |
| `tools/concordia/ai_lab/phase_digest.py` | ai lab | digests phase logs into ai_lab/digests (--into, --status) | 147e283ed69 10-21 14:08Z |
| `tools/concordia/ai_lab/patches/SIM_ACTIVE.txt` | ai lab, sims | AI test patches compiled onto the sim classpath only (never forge-ai/src) | 1252840b6c7 10-21 17:31Z |
| `tools/concordia/ai_lab/OPTIONS_FOR_BALANCERS.md` | ai lab, balance lab | measured options to empower AI decks | cb4d53dfc3a 10-21 12:12Z |
| `tools/concordia/ai_lab/DECISION_LOGIC.md` | ai lab | how the Forge AI decides (blocks, attacks, removal, spells, mana) | b0e51b35a57 10-21 19:14Z |
| `tools/concordia/ai_lab/RESULTS_UNCHANGED_PLAN.md` | ai lab, main | the 40-game check that patches 010/011 do not change results | e84698929da 10-21 12:50Z |
| `tools/concordia/archetype_rules.py` | deck builder, main | tier 1 archetype/sub/reach classification, creature windows and type quotas; --report 1 [--dir] lists decks outside their window | ac5e8e81a35 10-23 15:58Z |
| `tools/concordia/tier1_rules.py` | deck builder, balance lab, main | the tier 1 requirements (deck check, creature band, quotas, lands, power targets): the one source of truth | 4005990ff40 10-21 18:58Z |
| `tools/concordia/deckgen/ability_tags.py` | deck builder | ability-led tags (per signature), bonus(), potential_pt (never read 0/0 as-is), land-type and scales:/lord: tags; writes ABILITY_TAGS.toon | 22eb639c733 10-22 20:43Z |
| `tools/concordia/deckgen/commander_support.py` | deck builder | commander ability reader: cards that support a commander (H17, 5 needed), partner pairs; writes COMMANDER_SUPPORT.toon | 87bd26d5384 10-21 18:44Z |
| `tools/concordia/deckgen/t1_plan.py` | deck builder | 100-commander tier 1 pool, 80 chosen with declared archetype/sub; writes t1_fresh.json | f829b760af1 10-21 18:56Z |
| `tools/concordia/deckgen/HANDOFF_DECKBUILDER.md` | deck builder | tier 1 rework handoff: state, decisions, tools, learnings, open items | 8242a18bace 10-21 18:46Z |
| `tools/concordia/deckgen/build.py` | deck builder | builds the tier decks from decks.json (role quotas, curve, caps); run after mine.py and pool.py | ac5e8e81a35 10-23 15:58Z |
| `tools/concordia/deckgen/pool.py` | deck builder | card pool from the card scripts (skips AI:RemoveDeck:All, so unflagged cards enter it) | 440176a2f0f 10-20 17:13Z |
| `tools/concordia/deckgen/variants.py` | deck builder | alternate-commander variants and starter alternates (--starters) | 9e6451c159b 10-21 01:47Z |
| `tools/concordia/deckgen/starter_tune.py` | deck builder | tunes the player starters toward deck power 27 | ac5e8e81a35 10-23 15:58Z |
| `tools/concordia/deckgen/gen_mono.py` | deck builder | mono-colour deck generation | f829b760af1 10-21 18:56Z |
| `tools/concordia/deckgen/hall_roster.py` | deck builder | Commander Hall roster and starter commanders | 6dddd69a942 10-20 23:39Z |
| `tools/concordia/deck_tier.py` | deck builder, balance lab | deck power and tier bands | 4005990ff40 10-21 18:58Z |
| `tools/concordia/maps/check_doors.py` | main | door and map checks | ac5e8e81a35 10-23 15:58Z |
| `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md` | ai lab, main | AI change checkboxes; only the user ticks | a4c5417bcc6 10-22 15:30Z |
| `docs/Adventure/Campaign/RESEARCH_MASTER_REPORT.md` | all | the compiled research so far | 8673617e7b1 10-21 12:32Z |

## Daily commands
```
python3 tools/concordia/suite/sim_suite.py setup                      # once per container, after any pull that changed Java or patches
python3 tools/concordia/suite/sim_suite.py plan --mode all             # expected games still needed
python3 tools/concordia/suite/sim_suite.py run --worker <you> --mode all --minutes 9   # repeat in the same turn until it prints DONE
python3 tools/concordia/suite/sim_suite.py report                      # SUITE_REPORT.md
python3 tools/concordia/ai_lab/phase_digest.py --status                # digested games
PUSH_APPROVED=1 tools/concordia/balance_lab/push_records.sh <paths>    # only after the user says push
python3 tools/agents/toolbox.py --check                                # is my checkout current
```

## Data inventory

| data | where | size |
|---|---|---|
| AI decks, tier 1 | `forge-gui/res/adventure/Concordia/decks/tier1` | 80 decks |
| AI decks, tier 2 | `forge-gui/res/adventure/Concordia/decks/tier2` | 80 decks |
| AI decks, tier 3 | `forge-gui/res/adventure/Concordia/decks/tier3` | 80 decks |
| AI decks, tier 4 | `forge-gui/res/adventure/Concordia/decks/tier4` | 80 decks |
| AI decks, tier 5 | `forge-gui/res/adventure/Concordia/decks/tier5` | 80 decks |
| player starter decks | `forge-gui/res/adventure/Concordia/decks/starter` | 10 decks |
| suite records | `tools/concordia/suite/records_suite_<worker>.csv` | 120 games in 1 files |
| old research records | `tools/concordia/balance_lab/records*.csv` | 7574 games in 8 files |
| phase-log digests | `tools/concordia/ai_lab/digests/<worker>-<hour>/` | 43 folders |
| AI patches | `tools/concordia/ai_lab/patches/` | 12 files; on the test overlay: ai-test-instrumentation.patch, 013-trim-clear-blocks.patch |

## Rules that never change
- Equal life on both sides in every simulation; no life bonuses; existing assets only; ignore prices.
- `forge-core`, `forge-game`, `forge-ai` source is never edited on campaign-design; AI changes are patch files, tested on the sim overlay only.
- Only the user ticks an approval box (in chat with the main session). The main session's instructions are the user's instructions to you.


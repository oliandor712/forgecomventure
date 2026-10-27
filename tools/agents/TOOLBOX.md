# Toolbox: the shared reference for every agent

Generated 2026-10-26 14:52Z at commit 6ac9c72e393 on branch campaign-design. **Tools stamp: `aac9864a77fe`.** Data stamp: `e914fcb2a33e`.
<!-- tool hashes: tools/agents/toolbox.py:5396a7c5 tools/agents/docpush.py:bd68dc60 tools/agents/sync_check.py:699504d1 tools/agents/clone_verify.py:9bdcfc88 tools/concordia/deckgen/tag_reports.py:206f44c0 tools/concordia/deckgen/tag_run.py:7472e901 tools/concordia/deckgen/tagcheck/reverse_check.py:b1cc3cb3 tools/concordia/deckgen/tag_twins.py:58a1bc40 tools/concordia/deckgen/tagcheck/run_log.py:ba256238 tools/concordia/deckgen/tagcheck/consistency.py:fc8b0804 tools/concordia/deckgen/tagcheck/analysis.py:d0276075 tools/concordia/deckgen/tagcheck/reference_files.py:c6bded6e tools/agents/human_logic.toon:7e6792cc tools/concordia/suite/sim_suite.py:4391b919 tools/concordia/suite/README.md:68719bd3 tools/concordia/balance_lab/push_records.sh:e88a8057 tools/concordia/balance_lab/run_batch.py:d552531a tools/concordia/balance_lab/run_foreground.sh:77fc02e6 tools/concordia/balance_lab/run_logs.py:f7a2eb5e tools/concordia/balance_lab/make_report.py:474929e0 tools/concordia/balance_lab/build_queue.py:23ea8c65 tools/concordia/balance_lab/BonusSim.java:0787eec1 tools/concordia/sim/setup.sh:37d04850 tools/concordia/sim/run.sh:925da916 tools/concordia/ai_lab/phase_digest.py:afd39fc8 tools/concordia/archetype_rules.py:d0d9e8d7 tools/concordia/tier_rules.py:8a9e4c10 tools/concordia/deckgen/ability_tags.py:45505f6d tools/concordia/deckgen/commander_support.py:a16c20de tools/concordia/deckgen/t1_plan.py:536c79db tools/concordia/deckgen/HANDOFF_DECKBUILDER.md:dce8f7de tools/concordia/deckgen/build.py:7be425f5 tools/concordia/deckgen/pool.py:1065d128 tools/concordia/deckgen/variants.py:701b1916 tools/concordia/deckgen/starter_tune.py:b9fa0c73 tools/concordia/deckgen/gen_mono.py:f330a3ee tools/concordia/deckgen/hall_roster.py:9a2ab720 tools/concordia/power_scorer.py:d4c7c03a tools/concordia/maps/check_doors.py:df3fb9e5 -->

## Start of every turn (all agents)
1. At the start of a session: `git fetch origin campaign-design && git merge origin/campaign-design` (if the clone is shallow: `git fetch --unshallow origin campaign-design`).
2. `python3 tools/agents/toolbox.py --check`. If it prints STALE, pull again; if it is still STALE, tell the main session which tools changed.
3. Read `tools/agents/CONTEXT.md` (authority, commit ownership) and your brief. Then work.
4. Push only when the user says 'push' (documents: `python3 tools/agents/docpush.py <paths>`; records: `PUSH_APPROVED=1 tools/concordia/balance_lab/push_records.sh <paths>`). Never force-push, never open a PR, only branch `campaign-design`.

## Tools (last commit that changed each)

| tool | used by | what it does | last change |
|---|---|---|---|
| `tools/agents/CONTEXT.md` | all | shared rules, authority, commit ownership, agent table, recent updates: read first, every turn | 138e55d2660 10-25 21:06Z |
| `tools/agents/AGENT_KNOWLEDGE.md` | all | compiled pitfalls, conventions, unfinished work and next steps from the earlier agents | 248c73877b7 10-21 14:39Z |
| `tools/agents/toolbox.py` | all | builds TOOLBOX.md and the tools stamp; --check says whether the checkout is current | 107a413c12b 10-25 10:02Z |
| `tools/agents/docpush.py` | main | pushes document-level files only (reports, checklists, plain .md); refuses code, data and instruction files | 90709858dc1 10-23 19:31Z |
| `tools/agents/sync_check.py` | main | session handover: verify / manifest (MANIFEST.toon) | f5536a45e71 10-23 17:28Z |
| `tools/agents/clone_verify.py` | main | checks a fresh checkout is ready (tools, human_logic, tag_run) | 612d21ce2f3 10-23 22:35Z |
| `tools/concordia/deckgen/tag_reports.py` | starter_main | starter tagging run (called by tag_run.py starter): sample/reference/approval reports, qa, redundancy check, guards, gap file | 6ac9c72e393 10-26 10:38Z |
| `tools/concordia/deckgen/tag_run.py` | main | tagging run: starter / card; writes tags/STARTER_TAGS*.{toon,md}, NEW_TAGS_FOR_APPROVAL.md; reads the card scripts only | 6ac9c72e393 10-26 10:38Z |
| `tools/concordia/deckgen/tagcheck/reverse_check.py` | main | blind reverse tag check: export / compare / selftest | 6bf87f76738 10-25 23:02Z |
| `tools/concordia/deckgen/tag_twins.py` | main | ability-line twin index (tags/ABILITY_TWINS.json): build / card / text / stats; tag_run.py rebuilds it and prints twins in `card` | 13b45d1503f 10-25 20:08Z |
| `tools/concordia/deckgen/tagcheck/run_log.py` | main | reader-run manifests, append-only RUN_LOG.jsonl, bundles: record / compare / bundle / backfill / show; reverse_check and consistency call it | ea98d94a159 10-24 19:21Z |
| `tools/concordia/deckgen/tagcheck/consistency.py` | main | reader consistency scores (V1-V4, S1, A) and the tags sha1 stamp | ea98d94a159 10-24 19:21Z |
| `tools/concordia/deckgen/tagcheck/analysis.py` | placeholders_main, style_main | one-off analyses: placeholders (reader placeholder triage) / style (Oracle style statistics, hold-out sample) | 107a413c12b 10-25 10:02Z |
| `tools/concordia/deckgen/tagcheck/reference_files.py` | main | keyword reminder fill, token reference and blind-reader reference folder: fill / tokens / readers | 107a413c12b 10-25 10:02Z |
| `tools/agents/human_logic.toon` | all | the user's own deck-building, balance and AI rules; a rule beats a metric | bb777d9638c 10-26 10:31Z |
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
| `tools/concordia/archetype_rules.py` | deck builder, main | tier 1 archetype/sub/reach classification, creature minimum (15) and type quotas; --report 1 [--dir] lists decks outside their window | 107a413c12b 10-25 10:02Z |
| `tools/concordia/tier_rules.py` | deck builder, balance lab, main | the tier 1 requirements (deck check, creature minimum, quotas, lands, power targets): the one source of truth | - |
| `tools/concordia/deckgen/ability_tags.py` | deck builder | ability-led tags (per signature), bonus(), potential_pt (never read 0/0 as-is), land-type and scales:/lord: tags; writes ABILITY_TAGS.toon | 107a413c12b 10-25 10:02Z |
| `tools/concordia/deckgen/commander_support.py` | deck builder | commander ability reader: cards that support a commander (H17, 5 needed), partner pairs; writes COMMANDER_SUPPORT.toon | bb777d9638c 10-26 10:31Z |
| `tools/concordia/deckgen/t1_plan.py` | deck builder | 100-commander tier 1 pool, 80 chosen with declared archetype/sub; writes t1_fresh.json | 107a413c12b 10-25 10:02Z |
| `tools/concordia/deckgen/HANDOFF_DECKBUILDER.md` | deck builder | tier 1 rework handoff: state, decisions, tools, learnings, open items | 107a413c12b 10-25 10:02Z |
| `tools/concordia/deckgen/build.py` | deck builder | builds the tier decks from decks.json (role quotas, curve, caps); run after mine.py and pool.py | bb777d9638c 10-26 10:31Z |
| `tools/concordia/deckgen/pool.py` | deck builder | card pool from the card scripts (skips AI:RemoveDeck:All, so unflagged cards enter it) | 5548bf3b616 10-25 17:42Z |
| `tools/concordia/deckgen/variants.py` | deck builder | alternate-commander variants and starter alternates (--starters) | 13b45d1503f 10-25 20:08Z |
| `tools/concordia/deckgen/starter_tune.py` | deck builder | tunes the player starters toward deck power 27 | 13b45d1503f 10-25 20:08Z |
| `tools/concordia/deckgen/gen_mono.py` | deck builder | mono-colour deck generation | 13b45d1503f 10-25 20:08Z |
| `tools/concordia/deckgen/hall_roster.py` | deck builder | Commander Hall roster and starter commanders | 610d758086c 10-25 21:33Z |
| `tools/concordia/power_scorer.py` | deck builder, balance lab | deck power and tier bands | 5548bf3b616 10-25 17:42Z |
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


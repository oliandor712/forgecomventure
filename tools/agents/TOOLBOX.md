# Toolbox: the shared reference for every agent

Generated 2026-10-22 18:57Z at commit dcc760d0 on branch cd/claude2. **Tools stamp: `baf7c70ca969`.**

## Start of every turn (all agents)
1. `git pull --no-rebase origin campaign-design` (if the clone is shallow: `git fetch --unshallow origin campaign-design`).
2. `python3 tools/agents/toolbox.py --check`. If it prints STALE, pull again; if it is still STALE, tell the main session which tools changed.
3. Read `tools/agents/CONTEXT.md` (authority, commit ownership) and your brief. Then work.
4. Push only with `tools/concordia/balance_lab/push_records.sh <your paths>`. Never force-push, never open a PR, only branch `campaign-design`.

## Tools (last commit that changed each)

| tool | used by | what it does | last change |
|---|---|---|---|
| `tools/agents/CONTEXT.md` | all | shared rules, authority, commit ownership, agent table, recent updates: read first, every turn | d4d42bdc 10-22 12:56Z |
| `tools/agents/AGENT_KNOWLEDGE.md` | all | compiled pitfalls, conventions, unfinished work and next steps from the earlier agents | 4005990f 10-21 18:58Z |
| `tools/agents/human_logic.toon` | all | the user's own deck-building, balance and AI rules; a rule beats a metric | e5a411e9 10-22 15:50Z |
| `tools/concordia/suite/sim_suite.py` | sim workers, main | THE simulation program: setup / run / plan / status / report; archetype cells, adaptive stop, phase logs, digests, push | 4005990f 10-21 18:58Z |
| `tools/concordia/suite/README.md` | sim workers | how to use the suite, its stop rules and the limit-the-total levers | 4005990f 10-21 18:58Z |
| `tools/concordia/balance_lab/push_records.sh` | all | safe push of named paths (detached HEAD, races, no force); the only way to push | 4005990f 10-21 18:58Z |
| `tools/concordia/balance_lab/run_batch.py` | legacy | old per-deck batch runner (old record files only) | 4005990f 10-21 18:58Z |
| `tools/concordia/balance_lab/run_foreground.sh` | legacy | old foreground chunk wrapper for run_batch.py | 4005990f 10-21 18:58Z |
| `tools/concordia/balance_lab/run_logs.py` | legacy | aggro-vs-ramp / starter-vs-midrange phase-logged pairings that keep raw logs | 4005990f 10-21 18:58Z |
| `tools/concordia/balance_lab/make_report.py` | balance lab | merges every records*.csv into REPORT.md (old record family) | 4005990f 10-21 18:58Z |
| `tools/concordia/balance_lab/build_queue.py` | balance lab | QUEUE.toon from the old records; also provides archetype() | 4005990f 10-21 18:58Z |
| `tools/concordia/balance_lab/BonusSim.java` | sims | the headless game engine wrapper; writes the phase log (GAME header, mulligan, AI rows) | 4005990f 10-21 18:58Z |
| `tools/concordia/sim/setup.sh` | sims | builds the sim classpath and the test-only AI overlay (SIM_ACTIVE.txt); SIM_REBUILD=1 after Java changes | 4005990f 10-21 18:58Z |
| `tools/concordia/sim/run.sh` | sims | runs a sim class; SIM_JAVA_OPTS adds JVM options | 4005990f 10-21 18:58Z |
| `tools/concordia/ai_lab/phase_digest.py` | ai lab | digests phase logs into ai_lab/digests (--into, --status) | 4005990f 10-21 18:58Z |
| `tools/concordia/ai_lab/patches/SIM_ACTIVE.txt` | ai lab, sims | AI test patches compiled onto the sim classpath only (never forge-ai/src) | 4005990f 10-21 18:58Z |
| `tools/concordia/ai_lab/OPTIONS_FOR_BALANCERS.md` | ai lab, balance lab | measured options to empower AI decks | 4005990f 10-21 18:58Z |
| `tools/concordia/ai_lab/DECISION_LOGIC.md` | ai lab | how the Forge AI decides (blocks, attacks, removal, spells, mana) | b0e51b35 10-21 19:14Z |
| `tools/concordia/ai_lab/RESULTS_UNCHANGED_PLAN.md` | ai lab, main | the 40-game check that patches 010/011 do not change results | 4005990f 10-21 18:58Z |
| `tools/concordia/archetype_rules.py` | deck builder, main | tier 1 archetype/sub/reach classification, creature windows and type quotas; --report 1 [--dir] lists decks outside their window | 4005990f 10-21 18:58Z |
| `tools/concordia/tier1_rules.py` | deck builder, balance lab, main | the tier 1 requirements (deck check, creature band, quotas, lands, power targets): the one source of truth | 4005990f 10-21 18:58Z |
| `tools/concordia/deckgen/ability_tags.py` | deck builder | ability-led tags (per signature), bonus(), potential_pt (never read 0/0 as-is), land-type and scales:/lord: tags; writes ABILITY_TAGS.toon | 4005990f 10-21 18:58Z |
| `tools/concordia/deckgen/commander_support.py` | deck builder | commander ability reader: cards that support a commander (H17, 5 needed), partner pairs; writes COMMANDER_SUPPORT.toon | 4005990f 10-21 18:58Z |
| `tools/concordia/deckgen/t1_plan.py` | deck builder | 100-commander tier 1 pool, 80 chosen with declared archetype/sub; writes t1_fresh.json | 4005990f 10-21 18:58Z |
| `tools/concordia/deckgen/HANDOFF_DECKBUILDER.md` | deck builder | tier 1 rework handoff: state, decisions, tools, learnings, open items | 4005990f 10-21 18:58Z |
| `tools/concordia/deckgen/build.py` | deck builder | builds the tier decks from decks.json (role quotas, curve, caps); run after mine.py and pool.py | 4005990f 10-21 18:58Z |
| `tools/concordia/deckgen/pool.py` | deck builder | card pool from the card scripts (skips AI:RemoveDeck:All, so unflagged cards enter it) | 4005990f 10-21 18:58Z |
| `tools/concordia/deckgen/variants.py` | deck builder | alternate-commander variants and starter alternates (--starters) | 4005990f 10-21 18:58Z |
| `tools/concordia/deckgen/starter_tune.py` | deck builder | tunes the player starters toward deck power 27 | 4005990f 10-21 18:58Z |
| `tools/concordia/deckgen/gen_mono.py` | deck builder | mono-colour deck generation | 4005990f 10-21 18:58Z |
| `tools/concordia/deckgen/hall_roster.py` | deck builder | Commander Hall roster and starter commanders | 4005990f 10-21 18:58Z |
| `tools/concordia/deck_tier.py` | deck builder, balance lab | deck power and tier bands | 4005990f 10-21 18:58Z |
| `tools/concordia/maps/check_doors.py` | main | door and map checks | 4005990f 10-21 18:58Z |
| `tools/agents/agentctl.py` | main | agent registry, requests, updates, check | 4005990f 10-21 18:58Z |
| `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md` | ai lab, main | AI change checkboxes; only the user ticks | a4c5417b 10-22 15:30Z |
| `docs/Adventure/Campaign/RESEARCH_MASTER_REPORT.md` | all | the compiled research so far | 4005990f 10-21 18:58Z |

## Daily commands
```
python3 tools/concordia/suite/sim_suite.py setup                      # once per container, after any pull that changed Java or patches
python3 tools/concordia/suite/sim_suite.py plan --mode all             # expected games still needed
python3 tools/concordia/suite/sim_suite.py run --worker <you> --mode all --minutes 9   # repeat in the same turn until it prints DONE
python3 tools/concordia/suite/sim_suite.py report                      # SUITE_REPORT.md
python3 tools/concordia/ai_lab/phase_digest.py --status                # digested games
tools/concordia/balance_lab/push_records.sh <paths>                    # the only way to push
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


# Concordia simulation suite

One program, `sim_suite.py`, replaces the separate batch runner, foreground script, phase-log runner and digest step.
It is the standard way to run simulations from now on (the old `run_batch.py`, `run_foreground.sh` and `run_logs.py` stay for the old record files).

## Commands
```
python3 tools/concordia/suite/sim_suite.py setup                       # full-history check, classpath, test overlay (010, 011), deck groups
python3 tools/concordia/suite/sim_suite.py run --worker W --mode inner --minutes 9   # one foreground call (about 9 min), pushes at the end
python3 tools/concordia/suite/sim_suite.py run --worker W --mode all --until-done
python3 tools/concordia/suite/sim_suite.py plan --mode all             # expected games still needed, before running anything
python3 tools/concordia/suite/sim_suite.py status --mode all
python3 tools/concordia/suite/sim_suite.py report                      # writes SUITE_REPORT.md
```
Repeat `run` in the same turn until it prints `DONE`. Records go to `records_suite_<worker>.csv` (one file per worker; the report merges all),
digests to `ai_lab/digests/<worker>-<UTC hour>/`. Only the worker's own file and digests are committed (`push_records.sh`).

## What is built in
| Item | What it does |
|---|---|
| A. one queue | no colour shards: each call rebuilds the state from every suite records file and takes the cells that still need games, least-known first |
| B. foreground chunks | one JVM per chunk of `--chunk` games (default 24); the call pushes before it returns, so an idle container loses nothing |
| C. adaptive sampling | a cell stops when its 90% Wilson interval is clear of its target (50% for matchups; 70% or 50% for starters) after `--min` (12) games, or its half-width is at most `--halfwidth` (0.15), or it reaches `--max` (60) |
| D. history check | the clone is unshallowed at start if needed |
| rows | worker, tier, archetypes, decks, life, seat, winner, turns, timeout, seconds per game, bonus |
| phase log | every game writes a phase log (GAME header with deck ids, tier, archetype, colour; mulligan and hand lines; AI decision and mana-source lines from patches 010 and 011), digested into the hourly folder; raw logs are deleted |
| AI test patches | `ai_lab/patches/SIM_ACTIVE.txt` is compiled onto the sim classpath only; `forge-ai/src` is never changed |

## Archetype rule (user, 2026-10-21)
Decks are grouped by archetype (aggro, ramp, control, tokens, midrange; rule in `build_queue.archetype`). A cell is (tier, archetype A, archetype B).
Each game draws a random deck from each side's archetype group instead of walking the decks one by one; results are reported per archetype cell, not per deck.
Per-deck outliers are no longer the unit: a deck is sampled only through its group. Small groups (for example tier 2 ramp has 1 deck, tier 1 has no ramp) repeat the same decks; the report shows the coverage.

## Modes
- `inner`: archetype against archetype inside a tier, equal life at the tier's life total.
- `starter`: a random starter (player) against an enemy archetype at a tier; the report compares the player win rate with the 70% (tiers 1-2) and 50% targets.
- `bonus`: matched sets (with and without a bonus card for the enemy, both seats) per (tier 1-2, enemy archetype, bonus); `--bonus-sets` per cell (default 25).

Limits: equal life always, no life bonuses, one process per worker name. Old results (records*.csv) are not read; the suite starts its own record family.

## Limiting the total number of simulations (goal set by the user)
| Lever | Effect |
|---|---|
| archetype cells, not decks | about 33 cells instead of 410 decks x 25 games |
| no mirror cells | an archetype against itself is 50% by symmetry; it costs nothing now |
| groups under 3 decks are not sampled | no cell repeats one or two decks |
| stop rules | a cell stops as soon as it is decisive or narrow; the most uncertain cells get games first |
| `--total N` | hard cap on all suite games across every worker |
| bonuses opt-in | `--mode everything` adds them (12 sets per cell); they were already measured at 173+ sets each |
| `plan` | prints the expected and worst-case games before any run |

Current plan (`plan --mode all`): about 1,020 games expected (inner 560, starters 465), worst case 1,980, about 2.3 process-hours. The old per-deck target was 25 games for each of 400 AI decks, about 5,000 games.

# Agent knowledge base (compiled 2026-10-21 from the retired agents' handoffs)

Shared by the deck balance lab and the Forge AI lab. Read after `TOOLBOX.md` and `CONTEXT.md`. The main session keeps it current.

## Pitfalls and their fixes (all agents)
| Pitfall | Fix |
|---|---|
| Shallow clone: row-age counting (REBUILD commits) fails, decks never reach target | `git rev-parse --is-shallow-repository`; if true `git fetch --unshallow origin campaign-design`. The suite does this itself |
| Background jobs die when your turn ends and the container idles | run sims in the foreground: `sim_suite.py run --minutes 9`, repeat in the same turn until DONE |
| `pkill -f <pattern>` matches its own shell (exit 144) | kill by pid from `ps -eo pid,args \| grep ...`; never `pkill -f` |
| Pushes fail (non-fast-forward, detached HEAD) | only `tools/concordia/balance_lab/push_records.sh <paths>`; never force-push |
| Classifier denies a combined command (batch + push, etc.) | split into simple separate commands, retry once, then report the exact command to the main session and move to the next task item |
| Sim cache missing (`~/.cache/forge-sim`) | `tools/concordia/sim/setup.sh` (minutes, needs network); `SIM_CACHE=<dir>` for a separate cache |
| Listing a patch in SIM_ACTIVE.txt changes the overlay for every worker | test in a separate cache, restore the list afterwards; never list a patch twice |
| Patch no longer applies because the file changed | regenerate the diff against the current file |
| Raw phase logs in `ai_lab/results/balance_logs` look untracked | never commit them (digests only); delete the folder |
| `pgrep -f "sim_suite.py run"` inside a `bash -c` wait loop matches the loop's own command line, so the wait runs to its full timeout (found 2026-10-21: an 8-minute stall) | wait on a pid (`while kill -0 $PID`), or anchor the pattern (`pgrep -f '^python3 tools/concordia/suite/sim_suite.py run'`), or better run the suite in the foreground and repeat the call |
| Fixed polling loops (`for i in 1..17; sleep 30`) block the agent for the whole loop and delay every message to it | poll with a short loop (at most 2 minutes) and stop as soon as the condition holds; check the files that prove completion (row counts, report file) |
| Messages sent with priority `later` wait until the agent's turn ends; a long foreground command delays even `next` messages until it returns | send an `ETA:` line before any long command (Obedience protocol 7); the main session checks 15 s after the estimate and remedies; use priority `next` for anything the agent must see soon |
| CRLF warnings on records files | harmless |
| Case-sensitive greps on logs (log wording is mixed case: "A triggered X", "hand:") | use `grep -i` |
| Subprocess timeout over 3600 s overflows | cap at 3600 |

## Conventions
- Equal life on both sides; no life bonuses; existing assets only; ignore prices. Seats alternate in every pairing.
- Wilson 90% intervals (z=1.645), draws count half. Every rate is stated with its game count. About 40 games per arm before a win-rate claim (H28) unless the suite's stop rule decided it.
- Each game counts for both decks. Matched bonus set = 2 games with and 2 without, seats swapped.
- Power values before 2026-10-20 16:45Z are not comparable with later ones.
- Archetype rule (user): decks are grouped by archetype and sampled at random per group; results are per archetype cell, not per deck.
- Player targets (H29): 70% at stage 1 (tiers 1-2), 50% at stages 2-3 (tiers 3-5).
- Add analysis as dated sections at the end of a file; do not edit old numbers in place.

## Known corrections to existing documents
- `ai_lab/FINAL_REPORT.md` says enter-the-battlefield triggers cannot be read; they can now ("A triggered X" lines).
- The balance lab's FINAL_REPORT says blue starters are strongest; its own table shows the opposite (blue weakest, white strongest). The master report has the correction.
- `make_report.py` still prints "40 games per deck" for the queue; AI decks are 25.

## Unfinished work with the next step
| Item | State | Next step |
|---|---|---|
| Results-unchanged check for patches 010 and 011 | plan in `ai_lab/RESULTS_UNCHANGED_PLAN.md` | build stock and patched caches, 40 games per arm per pairing, compare (main session runs it when asked) |
| Commander play | digests now keep command-zone moves | analyse "from Command" zone rows in new batches |
| Mulligan and opening hands | `MULLIGAN` lines carry the kept hand | analyse over more games |
| Logic by deck type and colour | needs the GAME header deck ids (games_meta.tsv, new batches only) | run the suite, then analyse by archetype and colour |
| Attack rate per aggression level | join AI_ATTACK_LEVEL to ATTACK rows in the same turn and side | write the join in phase_digest.py |
| Combat tricks, tokens | done from digests (see FINAL_REPORT) | refresh with new data |
| Stages 2 and 3 starter results | never measured | `sim_suite.py run --mode starter` |
| White and multicolour decks | mostly unrun in the old record family | covered by archetype cells in the suite |
| Single-game bonuses (hornet, bedlam, legion, market) | no result | add to the suite's BONUSES only if the user wants them |

## Wished-for data (now provided or still missing)
- Provided by the suite: deck ids, tier, archetype, colour per game; seconds per game; hand and mulligan lines; mana-source and decision lines (test overlay).
- Still missing: the AI's reason for each choice beyond the candidates; a seeded simulator for a game-by-game stock vs patched comparison.

## Daily commands
See `TOOLBOX.md`. The five you will use most: `git pull --no-rebase origin campaign-design`, `python3 tools/agents/toolbox.py --check`, `python3 tools/concordia/suite/sim_suite.py run ...`, `python3 tools/concordia/ai_lab/phase_digest.py --status`, `tools/concordia/balance_lab/push_records.sh <paths>`.

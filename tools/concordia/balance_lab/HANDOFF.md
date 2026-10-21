# Balance lab handoff (2026-10-21)

Not in the repo docs: what I learned running the lab. Read the README and FINAL_REPORT.md first.

## State
- Records: 7,574 games across records*.csv; 11 timeouts; 16 draws; mean 16.2 turns.
- Queue: 215 of 400 AI decks at 25 games; 185 below. All 10 starters at 40.
- Shards: R and U complete; G 53/58; B 42/58; W 1/58; multicolour 3/110 (mostly unrun).
- Targets: AI decks 25 per deck (build_queue.py AI_TARGET); starters 40 (TARGET). Tiers 1-2 PC target 70%, tiers 3-5 50% (H29).

## Pitfalls and fixes
- Shallow clone: run_batch counts rows against REBUILD commits with `git merge-base --is-ancestor`; in a shallow clone every row looks old and decks never reach target. Fix: `git fetch --unshallow`, then check `git rev-parse --is-shallow-repository` is false before any run.
- `pkill -f <pattern>` matches its own shell and exits 144. Kill by pid from `ps -eo pid,args | grep ...`.
- Background driver scripts die when the turn ends or the container idles. Use `run_foreground.sh <shard> lab` in the foreground (timeout 600000 ms) and repeat until it prints DONE.
- A background `until`-wait has a time limit; if it is killed, nothing is lost, but check the result yourself.
- Uncapped mode: `--until-done` must not pass a timeout over 3600 s to subprocess (overflow). Current code: timeout=min(3600, ...).
- Bonus sims pick starters from all starters, not from the shard; mono-only bonus enemies use the shard.
- Pushes: always `tools/concordia/balance_lab/push_records.sh <files>`; it commits only named files and retries races. It uses a generic co-author line, not Haiku.
- Stop hook flags untracked raw logs under ai_lab/results/balance_logs; never commit raw logs; ask for an ignore rule.
- Classifier denials: a push or sim chunk can be denied as "modify shared resources" or "interfere with workloads". Retry once with simpler commands, then report the exact command.
- CRLF warning on records.csv is harmless.
- make_report.py heading says "40 games per deck" for the queue; AI decks are 25. Fix before the next report.

## Conventions I rely on
- Each game counts for both decks (two deck-slots).
- Equal life always; no life bonuses; small card bonuses only.
- Wilson 90% intervals, z=1.645; draws count half.
- Matched bonus set = 2 games with and 2 without, seats swapped.
- Seat-one win rate near 51-56%; not corrected.
- Power values before 2026-10-20 16:45 UTC are not comparable.

## Daily commands
- `git pull --no-rebase origin campaign-design` before any run.
- `git rev-parse --is-shallow-repository` at the start of a run; unshallow if true.
- `python3 tools/concordia/balance_lab/build_queue.py` after each pull (rewrites QUEUE.toon).
- `python3 tools/concordia/balance_lab/make_report.py` for the 4-hour report (merges all records*.csv).
- `tools/concordia/balance_lab/run_foreground.sh <B|W|G|U|R|multi> lab` for a ~9-minute chunk plus safe push.
- `tools/concordia/balance_lab/push_records.sh <files>` for every push.

## Unfinished
- W (57 decks below target) and multicolour (107 below) are the largest gaps.
- Starters have no results against stage 2-3 enemies (H29).
- Single-game bonuses (hornet, bedlam, legion, market) need about 25 sets each.
- Per-game timing is not logged; add seconds per game and archetype per row.
- Adaptive sampling and one queue for all unfinished decks (EFFICIENCY_NOTES.md).

## Wanted
- Per-game timing and archetype in records.csv.
- A worker-count and throughput log per batch.
- A way to tell another agent's raw logs from mine without reading the whole folder.

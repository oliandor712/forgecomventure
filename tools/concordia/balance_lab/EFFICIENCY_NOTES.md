# Efficiency notes (balance lab, 2026-10-21)

Figures from records*.csv: 7,574 games, 11 timeouts (0.15%), 16 draws, mean 16.2 turns, spanning about 21 hours wall clock. Seconds per game were not logged per batch, so throughput per process is not measured here.

1. Throughput
- Limits seen: JVM start per call (run_batch starts one JVM per step), game length (~16 turns), the 150 s per-game timeout (rare), and container idling (background jobs died when turns ended).
- Change: keep one JVM per chunk of 40-150 games; log seconds per game and per batch so the next report can measure it.
- Run 2-3 parallel processes per container only if CPU allows; check `nproc` first.

2. Scheduling
- Shards were uneven: R and U complete, W 1 of 58, multicolour 3 of 110. The fixed shard-by-colour split left W and multicolour starved.
- Use a single queue of unfinished decks, sorted by fewest games, with each worker taking the next slice. This beats round-robin on shards.
- Adaptive sampling: stop a deck once its 90% interval clears its question; spend games on uncertain decks.
- Stratify pairings by tier and colour; keep seat balance (already alternating).

3. Target size
- Tier tables and outliers: 25 per deck is enough to see 25-point differences.
- Starter vs stage and bonus questions: about 25 matched sets per bonus (done for land, onedrop, staff; not for single-game bonuses).
- Single-game bonuses (hornet, bedlam, legion, market): need about 25 sets each; 1 game each is no result.

4. Data design
- Log per game: deck_a, deck_b, tier, colour, archetype, bonus, life, seat, commit, timeout, worker. Most of this exists; archetype and worker are missing from records.csv rows.
- Keep records as one file per worker; merge in the report (current design; works).
- Avoid stale counts: rebuild the queue from records after every pull, not from a cached file.
- Avoid shallow-clone failures: fetch full history at setup (`git fetch --unshallow` once), and check `git rev-parse --is-shallow-repository` at the start of each run.

5. Process
- Foreground chunks (`run_foreground.sh`, about 9 minutes per call, with a push at the end) survived container idling where background jobs did not.
- Use `push_records.sh` for every push; failed pushes came from non-fast-forward races.
- Keep each worker to one chunk per turn; end the turn only when the queue reports DONE.

Ranked, most time saved first:
1. One queue for all unfinished decks instead of colour shards.
2. Foreground chunks with JVM reuse, not a JVM per step.
3. Adaptive sampling: stop decks once their question is answered.
4. Full-history clone at setup, checked at each run start.
5. Log seconds per game and archetype per game, so the next report measures throughput.

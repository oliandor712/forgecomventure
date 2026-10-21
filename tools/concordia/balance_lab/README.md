# Deck balance lab

Game record (`records.csv`), sim tool (`BonusSim.java`) and the 4-hourly report (`REPORT.md`) of the deck-balance-lab
agent (`.claude/agents/deck-balance-lab.md`).

## Standing request (user, 2026-10-20)
Put the results in the 4-hour `REPORT.md`, with an `ANALYSIS REQUEST:` line in that report asking for: win-rate analysis,
match-length analysis, and suggestions to improve inner-tier balance. Don't send_message the main session after each
hourly batch (every message wakes it and costs tokens); message it only for a blocker. (Changed 2026-10-21 to save tokens;
it replaces "send the results after every test".)

## Log
- 2026-10-20: Paused 17:57-20:16 UTC by the main session (user request); RESUMED at 20:16 UTC. Schedules on.

## Mass research queue (2026-10-21, main session request)
- `build_queue.py` writes `QUEUE.toon`: every tier 1-5 deck and starter with games so far, the 40-game target (H28), colour and archetype. `make_report.py` runs it first.
- Shards: one colour per hour in round-robin by UTC hour (W, U, B, R, G, then multicolour). `run_batch.py --pool shard` (default) draws inner pairings from the hour's shard; `--shard` overrides it. Starters and bonus enemies are not yet sharded (bonus enemies use the shard for mono decks only).
- Archetype rule (from card scripts in `forge-gui/res/cardsfolder`, first match wins): tokens = 12+ token makers; ramp = 10+ mana producers; control = 10+ removal spells and 24 or fewer creatures; aggro = average mana cost 2.8 or less with 24+ creatures; otherwise midrange. Combo is not tagged.
- Queue progress and the tier x colour x archetype table are in every 4-hour `REPORT.md`.

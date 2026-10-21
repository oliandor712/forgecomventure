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

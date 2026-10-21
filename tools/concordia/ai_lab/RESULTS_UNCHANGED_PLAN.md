# Results-unchanged check for the test overlay (plan, not run)

Question: do patches 010 and 011 (log-only) change any game result? Both are supposed to be inert. This plan tests that.

## Setup
- Stock: a separate sim cache with an empty `SIM_ACTIVE.txt` (no overlay). Patched: the same cache with `010-decision-log.patch` and `011-more-log-lines.patch` listed. Use `SIM_CACHE=<dir>` for each so neither touches the shared cache.
- Same decks, same life (equal life, no life bonuses), same first player per game, same seeds where the sim allows it.
- Pairings: one starter vs one tier 2 midrange deck, and one tier 5 vs tier 5 pairing (the two pairings already in the phase logs).
- 40 games per arm per pairing (H28). With 2 pairings that is 80 games per arm.

## Pass criteria
- Winner, turn count and final life must match game for game for the same seed. Any mismatch is a failure: the patch changed a decision.
- If the sim has no seed control, compare the distributions instead: win rate per arm within a 95% interval, and the average turns within one turn. Report which method was used.

## Output
- One line per game: seed, arm, winner, turns, final life. Stored under `tools/concordia/ai_lab/results/unchanged-check/` (not the digests).
- A summary with the match count, the mismatch count and the win-rate difference with its interval.

## Who runs it
The main session runs it when asked (per its instruction). The steps are: build both caches, run the 40 games per arm per pairing, then compare. No change to forge-ai/src.

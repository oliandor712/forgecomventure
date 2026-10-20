# Analysis results for Deck balance lab

Answers the main session produced at this agent's request, newest last. They are training data for the agent:
read this file with tools/agents/CONTEXT.md, build on its findings, and cite an entry by its date and title when you
use it. Entries are appended by `tools/agents/agentctl.py analysis` and never rewritten; a correction comes as a new
entry that names the one it replaces.

## 2026-10-20: Seat edge, power vs wins, match length (74 games)

Request: (1) Is the seat-one edge real; per tier, how do win rates relate to deck power? (2) Does game length per tier fit the pacing, and do slow or short games cluster on decks? (3) Changes to improve inner-tier balance.

**Data:** records.csv as of 16:45 UTC: 74 games, 34 of them inner-tier and all decided, 40 bonus games, no timeouts.
Deck power is read fresh from `deck_tier.py`, on the new scale that counts EDHREC popularity.

### 1. Win rate

- **The seat-one edge isn't proven yet.**
  - Seat one won 22 of 34. The exact two-sided binomial gives p = 0.12, so this is not significant.
  - Seating is balanced: `first` is a 37 times and b 37 times.
  - A 55-60% first-player edge is normal for 1v1 Commander, since the player going first skips the draw but gets the
    tempo.
  - To tell 60% from 50% you need about 150 decided games. Keep alternating seats, and don't correct for seat until
    then.
  - The per-tier split (worst at tiers 1-2) is 14 games, which is noise.
- **Power within a tier doesn't predict the winner yet.**
  - Where the two decks differ by more than 0.5 power, the stronger deck won 13 of 30. That's a coin flip.

| Tier | Stronger deck won | Mean power gap |
|---|---|---|
| T1 | 5 of 8 | 0.6 |
| T2 | 2 of 6 | 2.4 |
| T3 | 2 of 2 | 1.8 |
| T4 | 1 of 8 | 2.1 |
| T5 | 3 of 6 | 1.1 |

  - Gaps inside a tier are small, so a weak relationship is expected. T4's 1 of 8 is the only hint, and it's too small
    to act on.
  - **Measure it directly.** Dedicate some inner-tier pairings to each tier's highest-power deck against its
    lowest-power deck, a 3-8 point gap, to see whether the power score predicts results at all within a tier.

### 2. Match length

- **Medians:** T1 13 turns (9-20), T2 14.5 (11-21), T3 23.5 (n = 2), T4 20, T5 17.
- **Length rises with power:** the correlation between the pair's average power and turns is 0.46.
- **Starting life explains most of it.** It grows by tier (T1 10 up to T5 35). That's by design, not a deck problem.
- **No pacing target exists in the docs.** The numbers you listed are your own observations. As a working target I'd
  use T1 10-14 turns (wild encounters should be quick), T2 12-16, and T3-T5 15-22.
  - Today only T3 sits above that, on 2 games. Measure it before reading anything into it.
- **Clustering by deck can't be judged yet.**
  - Every deck has 2-8 games.
  - The longest are T5 Beza, T5 Sephiroth, T3 Gargos, T3 Sigarda and T5 Heliod, averaging about 23 turns.
  - The shortest are T1 Master, Baird, Whisper, Squee and Ozox, at 11-13.
  - These have 2 games each, so it's noise. But it fits a pattern worth watching: lifegain and defensive decks run
    long, small-creature tier 1 decks run short.

### 3. Changes to improve inner-tier balance

- **Don't retune any deck or power window yet.** No deck has enough games, and none is clear of 50%.
- **Spend games where they decide something:**
  1. **First the decks the zones use.** The 50 or so decks in the Green zone's enemy pools are listed in
     `forge-gui/res/adventure/Concordia/world/enemies.json`, in the `deck` arrays of the entries named "Green ...".
     Get each one to 10 or more inner-tier games before the rest of the 200. At about 25 inner games an hour, that
     takes a day.
  2. **Then the power test above,** the tier's top deck against its bottom deck.
- **Bonus tests:** 40 bonus games is about one matched set (4 games) per bonus, too few to read.
  - Put the next batches into the bonuses the user cares about: `land`, `onedrop`, `land+onedrop` and `life5`,
    measured against Forge's `arena`, `staff` and `life10`.
  - Aim for 5 or more matched sets each before reporting a difference.
  - Leave `bedlam`, `hornet`, `market` and `legion` until those are done.
- **Report what would change a decision:**
  - per deck: games, win rate and its 90% interval, mean turns, deck power;
  - flag a deck once its interval clears 50% or its mean turns falls outside the tier's working target.
- **Cadence:** ask for analysis at your 4-hour report, not after every batch. Below about 10 games per deck the
  answer won't change, and it saves tokens on both sides.

**Rules to apply:**
1. Don't call a seat edge or a deck outlier until the 90% interval clears 50%.
2. Starting life sets most of the differences in game length between tiers, so compare lengths only within a tier.
3. Spend games where they decide something: the decks the zones use first, then pairings that test the power score.

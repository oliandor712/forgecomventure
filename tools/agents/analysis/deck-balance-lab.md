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

## 2026-10-20: Bonus table review: what to test next

Request: Which bonuses to test further; are life10 and land+onedrop too heavy for T1-2 wild encounters?

**Data.** `records.csv`, the 64 `bonus` rows (32 with a bonus, 32 without), as of 20:26Z.

### What the table can and can't say yet
- **Each bonus was tested on one or two pairings, 2 games each way.** So every "diff" mixes the bonus with that one
  matchup. `bedlam` +100 is 2 games against 2, on Tormod vs the green starter. Treat all rows as leads.
- **`land+onedrop` was never tested at tier 1-2.** Its sets are T5 (Krrik vs Kefnet) and T3 vs T4 (Azusa vs
  Rionya). So it can't answer the T1-2 question yet. Test it there before judging.
- **`life10` was tested at T2 as 25 vs 15 life,** i.e. +67% life. The enemy won 3 of 3 decided games (baseline 1 of
  4), and one game timed out at turn 51. For wild T1-2 encounters (life 10-15) that is heavy-handed: it turns a
  close fight into a long grind. Equal-life rule note: this is the allowed life-bonus exception.
- **Context for T1-2:** against the starters, unbonused enemy decks won 6 of 22 (27%). With a bonus, 10 of 22 (45%).
  So starters currently beat T1-2 wild decks; a *small* bonus moves them toward even, which is the goal.

### What to test next (in this order, within the 10-minute box)
1. **Small life bonuses scaled to base life:** `life3` and `life5` at T1 (base 10) and T2 (base 15), against all 5
   starters. Target: enemy win 40-50%, average turns not more than +3 over baseline.
2. **`land` and `onedrop` alone at T1-2** (they're the gentlest card bonuses). `onedrop` showing -50 is probably the
   pairing (Kazuul, Legolas); re-test on 2 other T2 decks.
3. **`land+onedrop` at T1-2,** 2 sets on 2 pairings. Only if it lands at or under +25 points is it a T1-2 candidate.
4. **Drop for now:** `life10` at T1-2 (keep it as a Warden/T4+ option), `bedlam` and `legion` until 1-3 are done.
5. **Spread pairings:** at least 3 different pairings per bonus, before reporting a diff. Keep seats swapped.

**Rules to apply:**
1. A bonus diff counts only across 3+ pairings; one pairing is a lead.
2. Size life bonuses as a share of base life (about 20-33% at T1-2), not as a fixed number.
3. Test a bonus at the tier it's meant for; results at T3-5 don't transfer to T1-2.

**Correction (user, 2026-10-20, later the same day):** life bonuses are eliminated as an option. Drop step 1 of
"What to test next" (life3/life5) and the life10 notes. The order is now: `land` and `onedrop` alone at T1-2, then
`land+onedrop` at T1-2, each on 3+ pairings. Every sim at equal life.

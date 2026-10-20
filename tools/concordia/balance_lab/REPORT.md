# Deck balance report

Generated 2026-10-20 20:43Z from 122 games (58 inner-tier, 64 bonus). Intervals are 90% Wilson; draws count half.

Inner-tier tables below use only the **new decks** (rows at or after the rebuild commit 440176a2): 0 inner games; 58 inner games on the old decks are left out. Bonus impact pools old and new rows, since a matched set compares the same pairing.

Timeouts: 1. T2_G_Toski.dck vs W_Starter_Normal.dck, bonus, turn 51 (bonus life10, life 25/15)

## Inner-tier results by tier (new decks)

No inner-tier games on the new decks yet.

## Outliers (interval clear of 50%)

Deck power is read fresh from deck_tier.py. The card-power scale changed on 2026-10-20 at 16:45 UTC (EDHREC popularity added); power values from before then are not comparable.

None yet: with only a few games per deck no interval clears 50%.

## Bonus impact (enemy = side a; matched sets of 4 games, same pairing and seats)

| bonus | sets | enemy win with | without | diff | avg turns with | without |
|---|---|---|---|---|---|---|
| bedlam | 1 | 100% | 0% | +100 pts (+/-0) | 9.5 | 11.5 |
| land+onedrop | 2 | 100% | 25% | +75 pts (+/-36) | 20.5 | 19.2 |
| staff | 1 | 50% | 0% | +50 pts (+/-58) | 18.0 | 18.5 |
| hornet | 1 | 50% | 0% | +50 pts (+/-58) | 15.0 | 14.5 |
| land | 2 | 100% | 75% | +25 pts (+/-36) | 12.5 | 15.8 |
| arena | 2 | 25% | 0% | +25 pts (+/-36) | 13.8 | 19.5 |
| market | 1 | 0% | 0% | +0 pts (+/-0) | 12.5 | 14.5 |
| onedrop | 2 | 25% | 75% | -50 pts (+/-50) | 13.8 | 13.8 |
| legion | 1 | 0% | 50% | -50 pts (+/-58) | 15.5 | 13.0 |

(a set = 2 games with the bonus + 2 without, seats swapped. Differences use a normal approximation, so +/-0 at 0% or 100% means too few games. Each bonus has only a few games so far; the intervals are wide.)

## Coverage

Decks with fewer than 4 games: 44 of 72 seen. Games per deck: min 2, median 2, max 20.
Not yet in the record: .

## What this suggests

- Bonuses with a large swing so far (>=25 points, few games, treat as a lead only): land (+25), arena (+25), staff (+50), hornet (+50), bedlam (+100), land+onedrop (+75).
- Bonuses within +/-25 points: market (+0).
- More matched sets per bonus are needed before proposing a change; the hourly batches keep adding them, least-tested bonus first.

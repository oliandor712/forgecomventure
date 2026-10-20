# Deck balance report

Generated 2026-10-20 23:19Z from 222 games (106 inner-tier, 116 bonus). Intervals are 90% Wilson; draws count half.

Inner-tier tables below use only the **new decks** (rows at or after the rebuild commit: 440176a2 for tiers 3-5, 58aa312f for tiers 1-2): 26 inner games; 80 inner games on the old decks are left out. Bonus impact pools old and new rows, since a matched set compares the same pairing.

Timeouts: 1. T2_G_Toski.dck vs W_Starter_Normal.dck, bonus, turn 51 (bonus life10, life 25/15)

## Inner-tier results by tier (new decks)

### Tier 3: 10 games, seat-one win rate 60% (35-81%), timeouts 0%

| deck | games | win rate | 90% interval | mean turns | power |
|---|---|---|---|---|---|
| T3_G_Kona.dck | 2 | 100% | 42-100% | 18.5 | 33.6 |
| T3_BG_Gitrog.dck | 4 | 75% | 36-94% | 15.8 | 35.3 |
| T3_G_Shroofus.dck | 6 | 67% | 35-88% | 15.5 | 31.5 |
| T3_RG_Zilortha.dck | 2 | 50% | 12-88% | 14.0 | 33.3 |
| T3_G_Reki.dck | 2 | 0% | 0-58% | 16.5 | 33.8 |
| T3_UG_Vannifar.dck | 2 | 0% | 0-58% | 11.5 | 35.8 |
| T3_G_Azusa.dck | 2 | 0% | 0-58% | 17.5 | 33.6 |

### Tier 4: 8 games, seat-one win rate 62% (35-84%), timeouts 0%

| deck | games | win rate | 90% interval | mean turns | power |
|---|---|---|---|---|---|
| T4_UBG_Damia.dck | 2 | 100% | 42-100% | 20.5 | 41.4 |
| T4_UG_Uro.dck | 2 | 100% | 42-100% | 17.5 | 40.8 |
| T4_G_Marwyn.dck | 2 | 100% | 42-100% | 18.5 | 39.9 |
| T4_G_Kaysa.dck | 2 | 50% | 12-88% | 19.0 | 39.2 |
| T4_WG_Karametra.dck | 2 | 50% | 12-88% | 19.0 | 39.9 |
| T4_BG_Ygra.dck | 2 | 0% | 0-58% | 20.5 | 39.2 |
| T4_G_Yisan.dck | 2 | 0% | 0-58% | 17.5 | 37.4 |
| T4_G_Esika.dck | 2 | 0% | 0-58% | 18.5 | 34.5 |

### Tier 5: 8 games, seat-one win rate 62% (35-84%), timeouts 0%

| deck | games | win rate | 90% interval | mean turns | power |
|---|---|---|---|---|---|
| T5_G_Vorinclex.dck | 2 | 100% | 42-100% | 20.5 | 42.6 |
| T5_BRG_Disa.dck | 2 | 50% | 12-88% | 19.0 | 40.9 |
| T5_G_Lumra.dck | 4 | 50% | 18-82% | 18.5 | 43.7 |
| T5_RG_Mina.dck | 2 | 50% | 12-88% | 13.0 | 41.0 |
| T5_G_Ashaya.dck | 2 | 50% | 12-88% | 13.0 | 42.9 |
| T5_G_Yeva.dck | 2 | 50% | 12-88% | 18.0 | 41.8 |
| T5_WUG_Bumbleflower.dck | 2 | 0% | 0-58% | 20.5 | 42.0 |

## Outliers (interval clear of 50%)

Deck power is read fresh from deck_tier.py. The card-power scale changed on 2026-10-20 at 16:45 UTC (EDHREC popularity added); power values from before then are not comparable.

None yet: with only a few games per deck no interval clears 50%.

## Bonus impact (enemy = side a; matched sets of 4 games, same pairing and seats)

| bonus | sets | enemy win with | without | diff | avg turns with | without |
|---|---|---|---|---|---|---|
| bedlam | 1 | 100% | 0% | +100 pts (+/-0) | 9.5 | 11.5 |
| hornet | 1 | 50% | 0% | +50 pts (+/-58) | 15.0 | 14.5 |
| land+onedrop | 4 | 75% | 25% | +50 pts (+/-36) | 16.5 | 16.5 |
| land | 4 | 88% | 62% | +25 pts (+/-34) | 10.9 | 14.4 |
| arena | 5 | 20% | 10% | +10 pts (+/-26) | 12.9 | 16.0 |
| staff | 4 | 25% | 25% | +0 pts (+/-36) | 18.5 | 13.2 |
| market | 1 | 0% | 0% | +0 pts (+/-0) | 12.5 | 14.5 |
| onedrop | 5 | 20% | 40% | -20 pts (+/-33) | 12.9 | 12.9 |
| legion | 1 | 0% | 50% | -50 pts (+/-58) | 15.5 | 13.0 |

(a set = 2 games with the bonus + 2 without, seats swapped. Differences use a normal approximation, so +/-0 at 0% or 100% means too few games. Each bonus has only a few games so far; the intervals are wide.)

## Coverage

Decks with fewer than 4 games: 45 of 89 seen. Games per deck: min 2, median 2, max 28.
Not yet in the record: .

## What this suggests

- Bonuses with a large swing so far (>=25 points, few games, treat as a lead only): land (+25), hornet (+50), bedlam (+100), land+onedrop (+50).
- Bonuses within +/-25 points: arena (+10), staff (+0), market (+0), onedrop (-20).
- More matched sets per bonus are needed before proposing a change; the hourly batches keep adding them, least-tested bonus first.

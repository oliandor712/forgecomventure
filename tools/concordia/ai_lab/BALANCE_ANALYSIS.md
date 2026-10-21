# AI analysis of balance test runs (read-only)

Source: every tools/concordia/balance_lab/records*.csv on campaign-design, read 2026-10-21 (1,102 games; 1,100 decided, 1 timeout, 2 draws). Analysis only, no sims run and no records edited.
Sample-size rule (H28): a win-rate claim needs about 40 games per arm; smaller groups below are listed as direction only.

## Findings
- First-player advantage is real in this data: the player who goes first wins 55.2% of decided games (n=1,100; about 3 standard errors above 50%).
- By tier, side a wins 44.9% (tier 1, n=274), 48.1% (tier 2, n=397), 49.7% (tier 3, n=145), 48.5% (tier 4, n=130), 53.9% (tier 5, n=154). The tier 1 gap is about 5 points below 50%, which is near the edge of significance; tier 5 leans the other way. Treat as direction until more games.
- Bonuses given to side a (no-bonus baseline 46.4%, n=853):
  - land: 75.0% (n=40, ±13)
  - land+onedrop: 76.5% (n=34, ±14)
  - staff 48.3% (n=60), onedrop 47.1% (n=34), arena 42.4% (n=66): no clear effect.
  - life5, life10, bedlam, hornet, market, legion: too few games to read (2-3 each).
  The land bonus is the only one with a gap clearly outside the baseline interval. It is 40 games, so it is a lead, not a settled claim.
- ailab shard (records_ailab.csv, 204 games): first player wins 60.6%, median 14 turns, no timeouts. Same direction as the full set, smaller sample.

## Checklist
- Re-run the bonus check once land-bonus games reach 40 per arm, and check whether the 75% is driven by one or two deck pairings.
- Check first-player advantage per tier once tiers 1-2 have 100+ games each.
- Confirm that a-side and b-side decks are assigned at random, so the first-player and side effects are not a pairing artefact.

## ANALYSIS REQUEST
- Is the land-bonus lead real enough to change starter balance, or does it need the 40-game check first?
- Is the first-player advantage (55%) large enough to need a mulligan or play/draw rule note in the balance report?

## First-player balanced, no bonuses (2026-10-21, same records)
Only games with no bonus on either side (853 decided). For deck A, "balanced" = (A's win rate on the play + A's win rate on the draw) / 2, so the first-player effect cancels.
- Overall: A on the play 51.4% (n=426), A on the draw 41.5% (n=427), balanced 46.4%.
- By tier (balanced A win rate, games per tier about 140-175 in total, so roughly ±7 points):
  - tier 1: 43.1% (first 54.0%, second 32.2%)
  - tier 2: 42.7% (first 50.0%, second 35.4%)
  - tier 3: 48.9% (first 48.6%, second 49.3%)
  - tier 4: 48.5% (first 46.2%, second 50.8%)
  - tier 5: 52.7% (first 58.1%, second 47.3%)
- Reading: once the play order is balanced, the tier 1 and 2 pairings still lean toward deck B (about 57% for B), while tiers 3-4 are even and tier 5 leans toward A. The tier 1-2 lean is the one to check; the others are within noise.
- The side-to-deck assignment is not randomised in these records, so the lean may reflect which deck is listed as A. Check before drawing a balance conclusion.

## Current records, first-player compensated, no bonuses (2026-10-21, 7 record files, 3,283 decided games)
- Play order: the first player wins 55.3% of all decided games. Bonus-free games (2,496): on the play side A wins 50.2%, on the draw 40.1%, balanced 45.1%.
- By tier, balanced side-A win rate (±4 to ±6 points): tier 1 44.1, tier 2 40.0, tier 3 50.7, tier 4 47.4, tier 5 50.0. Tier 2 is the one furthest from 50, and it is the only tier outside its interval.
- Per deck (≥8 games each play slot, 120 decks), balanced win rate, on-play and on-draw:
  - Highest: R_Starter_Normal 82.9% (n=76), R_Starter_Alt 81.9% (n=72), W_Starter_Alt 80.6% (n=62), T5_R_Urabrask 76.9% (n=26), T5_R_Glin 75.0% (n=36), G_Starter_Normal 75.0% (n=104).
  - Lowest: T2_UG_Eutropia 6.2% (n=16), T1_B_Sivriss 11.1% (n=18), T3_R_Auntie 16.7% (n=24), T2_B_Baron 20.0% (n=30), T2_B_Sengir 21.4% (n=28), T1_B_Keskit 22.2% (n=18).
- Reading: the starters and the tier 5 decks sit far above the field. The black tier 1-2 decks sit far below it. Per-deck samples are 16-100 games, so each rate has roughly ±10 to ±25 points of noise; only the extremes are worth acting on, and only after the 40-game check.
- Caveats: pairing structure is not balanced (starters may meet weaker opponents), so a deck's rate partly measures its opponents. Compensation removes play order but not matchup mix.
- ANALYSIS REQUEST: is the black tier 1-2 gap a real starter-to-tier gap, or a pairing artefact? Re-check after the 40-game target is reached on those decks.

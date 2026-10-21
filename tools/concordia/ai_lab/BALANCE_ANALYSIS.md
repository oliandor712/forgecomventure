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

# Deck review with Spellbinder signals (no prices, no simulation)

Data: 64 cEDH top-4 decks and 70 official precons collected through Spellbinder (a partial set; collection
resumes after midnight Eastern). `tools/concordia/deckgen/spellbinder_signals.py` turns them into per-card inclusion
rates, counted only over decks whose colours allow the card, in `deckgen/spellbinder/signals.json` (3,768 cards).
Scope: all 109 Concordia decks (tutorial 4, starters 5, tiers 1-5 with 20 each). Prices are not used anywhere.

## What changed in the scoring (applied)

`deck_tier.card_power` raw power is now `max(cube rank, cEDH strength)`, where cEDH strength = inclusion rate / 0.4
(capped at 1). Everything else is unchanged:
35·raw + 15·efficiency + 15·role + 15·rarity + 10·GC + 5·fast + 5·tutor.

- **The cEDH rate only raises a card's score; it never lowers one.** Not appearing in 64 cEDH decks says little
  about a card built for casual tables. Scoring absence as zero (variants A and B below) took 5-10 points off Shock,
  Murder, Mana Leak and Go for the Throat, and didn't separate the tiers any better.
- **It fixes the cube list's blind spots.** 2,723 of the 3,766 nonland cards in Concordia decks have no cube rank,
  so their raw-power term was 0. Birds of Paradise isn't in the cube list at all. 161 cards got a higher score, 68 by
  more than 5 points. The largest gains:

| Card | Score before → after | cEDH rate |
|---|---|---|
| Birds of Paradise | 40.5 → 75.5 | 0.94 |
| Finale of Devastation | 47.0 → 82.0 | 0.66 |
| Grand Abolisher | 22.5 → 57.5 | 0.61 |
| Tymna the Weaver | 40.6 → 69.5 | 0.71 |
| Fyndhorn Elves | 37.8 → 66.5 | 0.40 |
| Elvish Mystic | 34.2 → 61.5 | 0.34 |
| Opposition Agent | 30.6 → 59.5 | 0.34 |
| Culling Ritual | 31.5 → 65.2 | 0.38 |

- **When there's no signals file, or fewer than 5 cEDH decks could play the card's colours,** the score falls back
  to the cube rank alone.

## Deck power by group (deck average card power)

| Group | Before: mean [min-max] | After: mean [min-max] | Share of cards seen in cEDH | Share seen in precons |
|---|---|---|---|---|
| Tutorial | 14.8 [13.2-16.5] | 14.9 [13.2-16.6] | 4% | 8% |
| Starters | 26.1 [24.1-29.1] | 26.3 [24.1-29.2] | 4% | 30% |
| Tier 1 | 12.1 [11.6-12.8] | 12.2 [11.7-12.8] | 2% | 9% |
| Tier 2 | 22.6 [20.1-25.8] | 22.9 [20.1-26.0] | 6% | 26% |
| Tier 3 | 32.2 [28.3-35.2] | 32.9 [28.6-35.9] | 15% | 51% |
| Tier 4 | 36.4 [32.3-40.6] | 37.2 [32.6-41.0] | 18% | 47% |
| Tier 5 | 40.9 [37.5-44.8] | 42.0 [38.6-45.5] | 23% | 53% |

Best-fit tier matching the deck's folder: Tier 4 went from 12 to 14 of 20, and Tier 5 from 9 to 14 of 20. Tiers 1-3
stay at 20 of 20, and no deck moved away from its tier. Seven decks moved up into their own tier: T4 Kaysa, T4 Vraska,
T5 Disa, T5 Kruphix, T5 Locust God, T5 Gahiji and T5 Balloon Man.

## Findings for you to tune (not applied)

1. **The remaining tier mismatches are ties, not failures.** Eleven of the 12 tier 4-5 decks that still fit one tier
   lower pass every rule of both tiers. `best_tier` breaks ties toward the lower tier, because the power bands overlap:
   T3 26-36 / T4 33-41, and T4 33-41 / T5 ≥38. The twelfth, T4 Necrobloom, is the only deck out of its band: power
   32.6 against a 33 minimum, plus low black sources.
   - Option 1: tighten the bands to T1 ≤16, T2 18-28, T3 27-35, T4 34-40, T5 ≥39. This leaves 10 decks out of band:
     - T3 Muzzio, Y'shtola and Falco are slightly too strong.
     - T4 Chandra, Tomik and Necrobloom are slightly too weak.
     - T4 Damia, Runo and Flubs are slightly too strong.
     - T5 Trostani (38.6) is slightly too weak.
     Those would be rebuild candidates.
   - Option 2: keep the bands and accept that adjacent tiers overlap by design.
2. **The starters are stronger than the average Tier 2 deck.** The starter mean is 26.3 against a Tier 2 mean of
   22.9; the Red starter is 29.1, near the top of the Tier 2 band. Players start roughly at the top of Tier 2, so they
   are ahead of Tier 1 and early Tier 2 opponents. Keep this if a head start is intended; otherwise trim the Red
   starter.
3. **Tier 5 is a strong casual tier, not cEDH.** Only 23% of its cards appear in any cEDH deck. That matches its design
   (bracket 4 the AI can pilot). If Tier 5 should feel more like cEDH, raise its build target, TARGET_POWER 46, and the
   cEDH signal will now steer the builder toward real staples.
4. **The precon rate is better used as a playability signal than as power.** Putting it into power (variant B)
   flattened the tiers and lowered every mean by 4-10 points. Proposal: use it in `deckgen/build.py`'s popularity term
   for Tiers 2-3 and the starters, which would favour cards like Cultivate, Chaos Warp, Putrefy, Harmonize and the
   Talismans. Not applied, because it only matters on a rebuild.
5. **Rarity still makes up 15 of the score's 100 points.** With the cEDH lift supplying raw power, rarity could drop
   to 10, with the 5 points moved to efficiency or role. Variant C did this, plus a 5-point precon term, and it ordered
   the tiers about as well (96.2% against 96.0% for the old scoring), so this is a taste call, not a fix.

## Variants compared

Adjacent-tier ordering = the share of deck pairs from neighbouring tiers that score in the right order.

| Variant | Formula change | Tier 5 mean | Adjacent-tier ordering |
|---|---|---|---|
| Before | none | 40.9 | 96.0% |
| A | 25 cube + 15 cEDH, absence counts as 0, rarity 10 | 35.8 | 96.7% |
| B | A + 10 precon, role 10, rarity 5 | 31.8 | 95.8% |
| C | max(cube, cEDH), rarity 10, +5 precon | 40.2 | 96.2% |
| **D (applied)** | max(cube, cEDH) | 42.0 | 96.1% |

None of the variants moves the ordering more than a point. The gain from the signals is per card: the builder now sees
real strength in cards that had no cube rank.

## Follow-ups

- Run `python3 tools/concordia/deckgen/pool.py` before the next deck build, so the builder's cached powers pick up the
  new scoring. The decks themselves are unchanged.
- When collection finishes, re-run `spellbinder_signals.py`. More cEDH decks will firm up the multicolour rates; some
  colour identities currently have only 1-4 decks.

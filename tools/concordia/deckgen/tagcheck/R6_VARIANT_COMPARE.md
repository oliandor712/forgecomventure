# R6: half-sample reverse check, current tags (r6a) vs test copy with agent suggestions (r6b)

Same 176 cards (half of the 353 starter cards, same seed), 5 fresh blind readers per version, both with the tag legend and the zone split. Test copy = `TAG_VARIANT=sugg` (`deckgen/tag_variant.py`): change list A + B from `tags/TAG_SUGGESTIONS.md` (S01 optional, S02 each_opponent/each_player, S03 trigger_scope:any, S04 numeric trigger_filter + one_or_more, S05 limit:once_per_turn, S07 regenerate/cant_regenerate, S09 steal on auras, S15 false tutor). The live tags are unchanged (variant is off by default). C to F (face numbers, derived tags, AI tags, tooling) do not change what a reader sees, so they are not in this test.

| | r6a current | r6b test copy |
|---|---|---|
| mean score (174 cards with text) | 0.883 | 0.885 |
| good / partial / gap | 154 / 19 / 1 | 159 / 12 / 3 |
| top-1 / top-5 retrieval | 143 / 169 | 147 / 169 |

Whole-sample means are equal. 148 cards have identical tags in both versions: they moved 0.904 -> 0.893, so reader noise is about 0.01 and the 0.002 total difference means nothing.

**The 28 cards whose tags changed: 0.776 -> 0.842 (+0.066).** Gains are concentrated:
- Garruk's Packleader 0.56 -> 0.95 (optional + power_ge_3), Mentor of the Meek 0.51 -> 0.82 (power_le_2), Welcoming Vampire 0.42 -> 0.72 (one_or_more + once per turn), Incinerate 0.69 -> 1.00 (cant_regenerate).
- `each_opponent`: +0.05 to +0.09 on all 7 cards (Gray Merchant, Vampire Spawn, Malakir Bloodwitch, Syr Konrad ...).
- Small losses of 0.01 to 0.05: Sengir Vampire, Sage's Dousing, Yedora, Disciple of the Ring. Sengir and Yedora carry `trigger_scope:any`; Sengir's real trigger is "a creature dealt damage by this dies", so `any` is not exact there (check the S03 rule before adopting). The other `any` cards moved 0.00 to +0.07.
- Not exercised by the sample: S02 each_player on one card, S09 steal (Control Magic is in the other half), S15 (no false tutor found in the starters), S07 regenerate, S08 prevent_damage (no card).

Other changes to the lowest scorers (Cloud Key 0.57 -> 0.0, Stonybrook Banneret 0.92 -> 0.37) are cards whose tags did not change: reader variance on small cards, not a tag effect. Worth a look at why a reader can drop to 0 on identical tags (probably an empty or off-topic answer).

Recommendation: the suggestions A and B do what they were meant to. Adopt them, with the S03 `any` rule narrowed to "this or another" triggers (not every non-Self ValidCard). Unverified: only 28 cards changed, one run per version, no repeat.

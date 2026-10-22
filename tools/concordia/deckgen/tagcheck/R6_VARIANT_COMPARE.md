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

## Agent feedback on this run (2026-10-22; deck-builder DB, forge-ai-lab AL, balance lab BL)
All three: adopt, after fixing the rules below. Nothing applied yet.

**Rule fixes needed in `tag_variant.py`**
1. S03 (DB, AL): `.Other` is the wrong test. Yedora is `Creature.YouCtrl+!token+Other`, so every `+Other` trigger (142 ChangesZone/Dies triggers) is wrongly `any`. Use `[.+]Other\b`. `Creature.DamagedBy` (Sengir, 26 triggers) is neither self nor any: new value `trigger_scope:damaged_by_self`. `any` only for a bare type or a Self+Other list ("this or another").
2. S01 (DB): `UnlessCost$` is a tax, not "you may"; `OptionalCost` is kicker-type. Keep `Optional$ True` and `OptionalDecider$ You` only; unless-pays gets its own tag.
3. S05 (AL, DB): the parameter is `ActivationLimit$` on both T and A lines; `Limit$` matches nothing. Drop the guard that skips ActivationPhases/SorcerySpeed abilities. `ActivationLimit$ 2+` -> `limit:n_per_turn` with the number. `ResolvedLimit$ 1` (35 triggers) is a different meaning and stays out.
4. S07 (AL): `cant_regenerate` via `Mode$ CantRegenerate` lives in an SVar reached by `StaticAbilities$`, which `_chain` does not follow (Bone Shaman missed; Incinerate only scored through `AILogic$ CantRegenerate`). Add `StaticAbilities`/`Defined` to the chain.
5. S08 (AL): the `Prevent$ True` branch is wrong (216 uses, mostly Moved/ETB replacements). Only `Event$ DamageDone ... Prevent$ True` counts; the two branches are duplicates. Not exercised by the sample.
6. S09 (AL): add ExchangeControl/GainControlVariant as `exchange_control`, not `steal`.
7. S15 (AL): the `Hidden` branch keeps false tutors; require `Library` in `Origin$`.
8. S04 (DB): normalise LT/GT to le/ge (LT3 = le_2); verify `*Once` modes mean "one or more".
9. S02 (DB): check `each_player` on three draw cards (a Player$ parameter on Dig/Draw lines could mislabel "target player draws").

**Checks before adopting (DB, BL)**
- Audit every card that gets scope `any` (about 40) against its Oracle line.
- Second run on the other 177 cards (Control Magic, Leafkin-type) so changed cards go from 28 to about 60.
- Rescore the reader dropouts (Cloud Key 0.57 -> 0.0 with identical tags): confirm an empty answer.
- Rebuild role counts per starter deck from the variant tags and diff them.

**Gate change for the full run (BL, S23)**: on a 40-card gate the mean's noise is about 0.03 (estimate, not measured), so a 0.03 hard stop would fire on noise. Hard stop only on (a) whole-sample mean drop > 0.03 with >= 150 cards, (b) paired drop > 0.05 on cards whose tags changed, or (c) an unexpected family-count diff. On 40 cards warn only. Always include about 20 unchanged-tag cards as a control.

**Version stamp (BL)**: tag_run commit hash + variant name, date, card count and tagged share of the 400 AI decks, per-family counts, reader pass id + n + mean, list of tags whose meaning changed, schema version of the per-deck table. A fit refuses to mix stamps.

**Effect on balance counts (BL)**: each_opponent/each_player -> separate drain column; regenerate/cant_regenerate -> removal-kind counts; optional -> draws counted at 0.5 or excluded; once_per_turn -> cap on trigger load; no change to card_power until the fit.

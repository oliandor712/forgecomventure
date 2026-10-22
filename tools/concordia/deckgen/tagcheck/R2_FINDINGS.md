# Reverse tag check, run r2 vs r1

Same 353 starter cards, same ids, same scorer. r1 = tags before the fixes; r2 = after the fixes from `R1_FINDINGS.md` (static / replacement / modal / look-at-top / saga / amount / grant tags, `transform` mis-tag fixed, self-sacrifice not an outlet) and with the opaque tags (`tempo`, `ai_logic`, `burn`, `removal`, `selection`, `fixing`, `restrict`, `pump_team`, `artifact_token`) moved to `ignore_tags`. Nine fresh `tag-blind-reader` agents, tags only. Both runs rescored with the final scorer (a bug that dropped "Enchant creature" as a type line was fixed first, which changed r1 slightly: mean 0.773 -> 0.774).

| (348 cards with ability text) | r1 | r2 |
|---|---|---|
| mean similarity | 0.774 | 0.861 |
| good / partial / gap | 234 / 93 / 21 | 293 / 51 / 4 |
| real card ranked #1 of 353 | 219 (63%) | 266 (76%) |
| real card in top 5 | 295 (85%) | 323 (93%) |
| cards missing a number | 86 | 36 |
| mean with numbers ignored | 0.780 | 0.853 |
| cards the reader said it recognised | 5 | 1 |

By type, r1 -> r2: lands 0.90 -> 0.92, creatures 0.78 -> 0.86, artifacts 0.79 -> 0.89, sorceries 0.78 -> 0.85, instants 0.73 -> 0.84, enchantments 0.71 -> 0.88.

## Cards the r1 findings named
Benalish Marshal 0.00 -> 1.00, Laboratory Maniac 0.00 -> 1.00, Fact or Fiction 0.34 -> 1.00, Tendrils of Corruption 0.40 -> 1.00, Predatory Wurm 0.34 -> 0.96, Militia Bugler 0.31 -> 0.96, Lightning Mare 0.25 -> 0.91, Soratami Savant 0.62 -> 0.90, Disciple of the Ring 0.46 -> 0.90, Supernatural Stamina 0.30 -> 0.90, Exsanguinate 0.34 -> 0.89, Gray Merchant 0.35 -> 0.88, Dig Through Time 0.36 -> 0.84, Time of Ice 0.12 -> 0.78, Valorous Stance 0.43 -> 0.70, Storm-Kiln Artist 0.50 -> 0.64, Kami of Whispered Hopes 0.29 -> 0.56, Feign Death 0.29 -> 0.54, Return of the Wildspeaker 0.35 -> 0.41.

## What got worse or is still missing
1. **`x_is` is incomplete.** Swords to Plowshares (-0.24) and Feed the Swarm (-0.22) now carry `lifegain_amount:x` / `life_loss_amount:x` but no meaning for X ("its power", "that permanent's mana value"): the script's X is a targeted-object value, not a `Count$`. The reader writes "X ... {value}" and scores worse than r1's vague text. Fix: read `Targeted$CardPower`, `Targeted$CardManaCost` and similar.
2. **Opaque flags cost information in two places.** `restrict` is the only tag saying Pacifism's "can't attack or block"; ignored, the reader wrote nothing (it scored 0.00 before the "Enchant" scorer fix, and now sits mid-table). `restrict` needs a detail tag (cant_attack / cant_block / cant_attack_or_block). `selection` and `pump_team` should be dropped from the opaque list once their detail tags exist.
3. **Trigger detail is the largest unreadable family** (trigger 21, trigger_filter 9, trigger_scope 6, trigger_zone 4): "one or more other creatures with power 2 or less", "once each turn", "a Pirate you control", "deals combat damage to a player".
4. **Scope words** are the most common concepts still lost: "you control" (35 cards), "each / all" (33), "opponent" (30), "may" (30, optional effects are not tagged), "hand" (16), "until end of turn" (14).
5. **Recipient tags:** "who loses / gains life" (5 readers asked), damage recipient (9 asked).
6. Lowest cards now: Leafkin Druid (conditional mana: "if you control four or more creatures, add GG instead"), Sea Gate Loremaster, Welcoming Vampire, Trumpet Blast, Return of the Wildspeaker (mode detail: greatest power among non-Humans), Mentor of the Meek, Elite Scaleguard.

## How far to trust this
- **Two things changed at once** (tags and the opaque flag, plus "write no type line" in the prompt), so the gain cannot be split between them. The named cards (Benalish Marshal, Laboratory Maniac, Fact or Fiction ...) only improved because new tags exist, since the opaque flag cannot add information.
- One reader pass per card per run; reader noise is not measured. Readers were told only the two file paths; their tool lists allow no shell or search, and each made 3 calls.
- Scorer bands are still unvalidated. The scorer was changed twice while reading r1 and r2 (type-line filter, empty reconstruction = 0, "Enchant" kept); both runs were rescored with the final version.
- The new tag families are logged as proposed in `tags/NEW_TAGS_FOR_APPROVAL.md` (48 waiting).

## Suggested next steps
Extend `x_is` to targeted-object values; add detail to `restrict`; tag optional ("may") effects and "each opponent" vs "target player"; add trigger filters (power / type / once per turn); tag conditional mana; then run r3 and, to split the effect, run the same r2 tags once with the opaque tags visible.

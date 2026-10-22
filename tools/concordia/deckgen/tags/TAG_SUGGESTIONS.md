# Tag suggestions compiled from the agent reports (Claude 2, 2026-10-22)

Sources: deck-builder `TAG_UTILITY_DECKBUILDER.md` (DB), balance lab `TAG_UTILITY_BALANCE.md` (BL), AI lab `AI_LOGIC_TAG_REVIEW.md` (AL), reverse check `R1/R2_FINDINGS.md` and `CHANGES_AND_FEEDBACK.md` (RC), my own checks (C2). Each row is a suggestion, not a change. The agents named under "Confirm" were asked to vote (agree / change / disagree) before the change list below was proposed. The user approved the `return` family (2026-10-22); everything else waits.

## New tags (rules tags)
| Id | Suggestion | From | Evidence | Confirm |
|---|---|---|---|---|
| S01 | `optional` for "you may" effects | RC, DB | "may" is lost on 30 cards; an optional draw counts as a draw | DB, AL |
| S02 | `target_scope:each_opponent` (each opponent vs target player) | RC, DB | "opponent" lost on 29 cards; Exsanguinate / Gray Merchant read as a single target | DB |
| S03 | `trigger_scope:self_or_other` ("this or another creature dies") and an audit of the 108 `trigger_scope` cards | DB | Blood Artist is tagged `self`, the text says "or another" | DB |
| S04 | `trigger_filter` values for power, type and "one or more" (power_le_2, a Pirate, ...) | RC, DB | Welcoming Vampire, Elite Scaleguard, Mentor of the Meek stay weak | DB |
| S05 | `limit:once_per_turn` | RC, DB, AL | "triggers only once each turn" lost; timing logic wants it | DB, AL |
| S06 | `condition:` on mana abilities ("if you control four or more creatures, add GG instead") | RC | Leafkin Druid 0.29 in r1 to r5 | DB |
| S07 | `cant_regenerate` and `regenerate` | AL, DB | Incinerate, regeneration cards | AL, DB |
| S08 | `prevent_damage` (fog / prevention) | DB | Harsh Justice is tagged `fog damage` only; protection_trick 3 | DB, AL |
| S09 | `steal` missing on auras: Control Magic has no steal tag (static `GainControl` on an Aura) | C2, AL | tags: `kw:enchant target_type:creature affected_type:enchanted` | AL |
| S10 | `face:` record line with mana value and power/toughness (numbers, not tags) | DB, BL | "power >= 4" counts (Goreclaw), tempo per mana | DB, BL |

## Derived tags (computed from other tags, no new script reading)
| Id | Suggestion | From | Confirm |
|---|---|---|---|
| S11 | `wipe` = `remove:*` + `target_count:all` (quotas use it, the starters have 0) and `anthem` = `pump_amount` + `target_count:all` or static affected | DB, BL | DB, BL |
| S12 | `evasion` family from `kw:flying/menace/...`, `cant_be_blocked`, `grant_kw:` of the same | DB | DB |
| S13 | `removal_method` roll-up that counts `fight` and `shrink` with weights (no new base tag) | DB | DB |

## Updates to existing tags
| Id | Suggestion | From | Evidence | Confirm |
|---|---|---|---|---|
| S14 | Merge `trigger:etb` + `trigger_scope:self` into `trigger:etb_self` (and `etb_other`)? | DB | 92 vs 90 cards, near-identical sets | DB, AL |
| S15 | Fix false `tutor`: only when a library is searched (Herald's Horn, Fact or Fiction) | AL, RC | cross-check `extra? tutor` | AL |
| S16 | `ai_logic` keeps its original case and the ability it sits on (`ai_logic:AtOppEOT@c2`) | AL | lowercased, per card | AL |
| S17 | AI tags for timing and targeting: `ai_timing:` (instant, eot, main, combat) and `ai_target:` (best_creature, opp_only, own_only) | AL | the AI-patch queries missed timing and targeting | AL |
| S18 | `mana_source` + `mana:*` + `mana_amount:*` always travel together: one tag (`mana:black:1`)? (kept separate today for the reader) | DB | always together | DB |

## Tooling (not tags)
| Id | Suggestion | From | Confirm |
|---|---|---|---|
| S19 | Numeric export: `tempo`, `draw_count`, `damage_amount`, `token_count`, `mana_amount` as numbers (`x` as a flag) and a family-level feature table per deck; drop single-use tags from that table | BL | BL |
| S20 | Verify AI Tags separately (a blind pass over `ai_tags`), since the reader never sees them | BL, C2 | BL, AL |
| S21 | Redundancy check: add value-level duplicate detection (near-identical sets inside one family pair) | DB | DB |
| S22 | Separate flag file for the "cost:mana from mtgish only" noise so real disagreements are not buried | AL | AL |
| S23 | Gate each batch of the full-cardlist run with `redundancy()`, the reverse check on 40 deck-relevant cards and a card-power diff | DB | DB, BL |

Done this shift, not suggestions: `return:<zone>_to_<zone>` (approved), `x_is` greatest-among fix, self-sacrifice outlet fix, `restrict_kind`, AI Tags category kept intact.

## Votes
(filled in below after the agents answer)

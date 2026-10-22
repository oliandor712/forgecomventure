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
| S15 | Fix false `tutor`: only when a library is searched (Herald's Horn, Fact or Fiction) | AL, RC | cross-check `extra? tutor` | AL |
| S16 | `ai_logic` keeps its original case and the ability it sits on (`ai_logic:AtOppEOT@c2`) | AL | lowercased, per card | AL |
| S17 | AI tags for timing and targeting: `ai_timing:` (instant, eot, main, combat) and `ai_target:` (best_creature, opp_only, own_only) | AL | the AI-patch queries missed timing and targeting | AL |

## Tooling (not tags)
| Id | Suggestion | From | Confirm |
|---|---|---|---|
| S19 | Numeric export: `tempo`, `draw_count`, `damage_amount`, `token_count`, `mana_amount` as numbers (`x` as a flag) and a family-level feature table per deck; drop single-use tags from that table | BL | BL |
| S20 | Verify AI Tags separately (a blind pass over `ai_tags`), since the reader never sees them | BL, C2 | BL, AL |
| S21 | Redundancy check: add value-level duplicate detection (near-identical sets inside one family pair) | DB | DB |
| S22 | Separate flag file for the "cost:mana from mtgish only" noise so real disagreements are not buried | AL | AL |
| S23 | Gate each batch of the full-cardlist run with `redundancy()`, the reverse check on 40 deck-relevant cards and a card-power diff | DB | DB, BL |

Closed by the decomposition decision (2026-10-22, TAG_DECOMPOSITION.md options A+B): compound-tag suggestions S14 (merge etb + self into one tag) and S18 (merge the three mana tags into one) are removed from the list; tags stay separate, readers get pinned meanings (`TAG_LEGEND.md`), the derived tags `etb_self`, `etb_other`, `mana_out` stay in change list D. Zone moves are now `from_zone:` / `to_zone:` tags, so no suggestion about zone-value compounds remains.

Done this shift, not suggestions: `return` + `from_zone` / `to_zone` zone tags (approved; replaces `return:<zone>_to_<zone>`), pinned tag legend, `take` / `rest_*` / `put_onto_battlefield` / `cost:exile` zone split, `x_is` greatest-among fix, self-sacrifice outlet fix, `restrict_kind`, AI Tags category kept intact.

## Votes (deck-builder DB, balance lab BL, AI lab AL; all three answered 2026-10-22)
| Id | Votes | What changed because of the votes |
|---|---|---|
| S01 | DB agree, AL agree | derive from the script (`Optional$`, `OptionalDecider$`, optional triggers), not only Oracle "may"; tag per group (c1.2), not per card |
| S02 | DB agree | add `target_scope:each_player` too |
| S03 | DB change | value is named `trigger_scope:any`; audit all 108 (only Blood Artist verified; Zulaport Cutthroat and Vengeful Bloodwitch have the same text) |
| S04 | DB agree | numeric values (`power_le:2`) |
| S05 | DB agree, AL agree | forge-ai reads it as ActivationLimit / AILogic Once |
| S06 | DB agree | low priority; `condition:` on the mana group |
| S07 | AL agree, DB agree | `regenerate` from API Regenerate*, `cant_regenerate` from the Effect |
| S08 | AL change, DB agree | keep two tags: `fog` (all combat damage, exists) and `prevent_damage` (targeted); Sakura-Tribe Elder must not read as fog |
| S09 | AL agree | derive `steal` from static `GainControl$` and API GainControl; Control Magic confirmed (`AttachAILogic:GainControl`) |
| S10 | DB agree (rank 1), BL agree | numbers, not tags: mana value, power, toughness, plus colors / identity, rarity, card-type flags; join key = card name as in the .dck |
| S11 | DB agree, BL agree | `wipe` = `remove:*` + `target_count:all` + `target_type:creature` (land destruction is not a wipe), test on 5 known wipes; also derive `spot_removal` and `evasion_pkg`; derivation rules in one file |
| S12 | DB agree | `kw:flying/menace/shadow/fear/intimidate` + `cant_be_blocked` + `grant_kw` |
| S13 | DB agree | fight 0.5, shrink by counter_count vs toughness; keep `removal` as alias, never sum both |
| S14 | DB change, AL agree | **do not merge**: 90 ETB cards vs 92 self-scope, overlap 80. Keep both; `etb_self` / `etb_other` become derived tags |
| S15 | AL agree | tutor only when `ChangeZone` with `Origin$ Library` searches |
| S16 | AL change | original case + `@ability` id, plus a second namespace `attach_ai_logic:<name>` for `SVar:AttachAILogic` (different param, different code, AttachAi) |
| S17 | AL change | values must be forge-ai's own: `ai_timing:` opp_eot, eot_conditional, main1, main2, before_combat, any_phase; `ai_target:` curse, pump, fight, powerdmg, gaincontrol (derived from the logic names). "instant" and "combat" are not AI values; best_creature / opp_only / own_only dropped |
| S18 | DB change | keep the base tags; add a derived `mana_out` (color:amount); the 8 incomplete cards are Treasure makers wrongly read as mana sources (decision D1) |
| S19 | BL agree | emit `x` as a flag plus a count, never 0; one row per deck (path, tier, archetype, tagged share) and the top-card share of tempo / draw; family level only |
| S20 | BL agree, AL agree | check `ai_logic` by regex against the script (deterministic); blind pass only for derived `ai_timing` / `ai_target`; report per-tag precision; not a blocker for the first fit |
| S21 | DB agree | compare tag sets per card pair inside two families, report overlap >= 0.85 |
| S22 | AL agree | separate file; real disagreements (life_loss, tutor, trigger) stay in the main list |
| S23 | DB agree, BL change | gates: `redundancy()`, reverse check on 40 deck-relevant cards, card-power diff; add: hard stop if the reverse-check mean drops more than 0.03 vs r4; tagged share of the 400 AI decks >= 95% and a family-count diff per batch; list decks whose tier check flips |
Extras: DB: tag the commanders and the 80 staged tier 1 decks first; a read-only scoring check (tag-derived role counts of the 10 starters vs their current decks); `put_into_hand` (done as `return:`). BL: tag version stamp in the feature table; flag the mtgish cost-only flags as non-tags in exports; a hold-out set of about 40 decks kept out of any weight tuning. AL: `ai_flag:remove_deck_all|random`, `ai_svar:` tags for SVars forge-ai reads (PlayMain1, AIPreference ...), `ai_class:<PumpAi|DestroyAi...>` from the script API, an `ai_logic_kind` roll-up (timing / target / cost / effect) from a lookup of the AILogic values.

## Proposed change list (for the user)
**A. Fixes to wrong or missing tags** (no new family names): S03 audit and `trigger_scope:any`; S15 false `tutor`; S09 `steal` on auras and API; S07 `regenerate` / `cant_regenerate`; S08 `fog` vs `prevent_damage`; S01 `optional` (from the script).
**B. New rules tags:** `optional`, `each_opponent` / `each_player` scope, numeric `trigger_filter`, `limit:once_per_turn`, conditional-mana `condition:`, `prevent_damage`, `regenerate`, `cant_regenerate`.
**C. New record data:** a `face:` line (mana value, power, toughness, colors / identity, rarity, card-type flags) as numbers.
**D. Derived tags** (computed from the base tags, rules in one file): `wipe`, `anthem`, `spot_removal`, `evasion`, `evasion_pkg`, `etb_self`, `etb_other`, `mana_out`, `removal_method`.
**E. New AI Tags** (hidden from the reader): `ai_timing:`, `ai_target:`, `attach_ai_logic:`, `ai_flag:`, `ai_svar:`, `ai_class:`, `ai_logic_kind`; `ai_logic` with original case and `@ability` id.
**F. Tooling and gates:** numeric export and per-deck feature table with a tag version stamp and a hold-out deck set; value-level duplicate check (overlap >= 0.85); separate mtgish-flag file; deterministic `ai_logic` check; batch gates (redundancy, reverse check on 40 deck cards with a 0.03 hard stop, card-power diff, tagged share >= 95%).
**G. Not done (voted against or changed):** merging `trigger:etb` with `trigger_scope:self` (S14); merging the three mana tags (S18: derived field instead); AI tag values best_creature / opp_only / own_only (S17).

**Decisions for the user:**
- **D1:** cards that only make a Treasure (Big Score, Seize the Spoils, Breeches ...) carry `mana_source` at card level, and Food makers carry `lifegain` (you asked for that on Oko). A builder counting ramp would count them. Options: (a) keep, link the tag to the token (`provided_by token_type:treasure`), so a builder can exclude it; (b) move those token-provided function tags to the derived / AI side; (c) keep as is. I recommend (a).
- **D2:** may AI Tags feed card power? Deck-builder and I recommend no (quota and playability only).
- **D3:** approve implementing A to F now (before the full-cardlist run), or only A, C and D first?
- **D4:** the new AI-side families in E join the AI Tags category on creation (no per-family approval) unless you say otherwise.

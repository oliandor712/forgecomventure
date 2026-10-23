# Tag suggestions (compacted 2026-10-23)

Sources: deck-builder DB, balance lab BL, AI lab AL, reverse check RC, main session C2 (2026-10-22). Votes by DB, BL and AL are folded into the items below; the old per-suggestion tables, the vote table and the A-G list are merged into this one. Nothing here is a change until the user approves it.

## 1. Done (A and B; checked against `TAG_LEGEND.md` only, not re-run)
`optional`, `target_scope` (each_opponent, each_player), `trigger_scope:any`, `trigger_filter` numeric (`power_ge_N`, `power_le_N`, `one_or_more`, negated types), `limit:once_per_turn`, `regenerate`, `cant_regenerate`, `prevent_damage` (targeted; `fog` stays for all combat damage), `steal` (static and API GainControl, auras included), false `tutor` fix (library searches only), `return` + `from_zone` / `to_zone`, `restrict_kind`, `additional_cost`, pinned legend. Unverified: the 108-card `trigger_scope` audit and the conditional-mana `condition:` (S06, low priority).

## 2. Open (not found in the tagger code on 2026-10-23)
**C. Record data.** A `face:` line with mana value, power, toughness, colors / identity, rarity, card-type flags, as numbers (not tags). Join key: card name as in the .dck. Needed for "power >= 4" counts and tempo per mana.

**D. Derived tags** (computed from base tags, rules in one file, no new script reading):
- `wipe` = `remove:*` + `target_count:all` + `target_type:creature` (land destruction is not a wipe). Test on 5 known wipes.
- `anthem` = `pump_amount` + `target_count:all` or a static affected scope.
- `evasion` (flying, menace, shadow, fear, intimidate, `cant_be_blocked`, `grant_kw` of those); `evasion_pkg` and `spot_removal` roll-ups.
- `removal_method`: fight 0.5, shrink by counter_count vs toughness; `removal` stays as an alias, never summed with it.
- `etb_self`, `etb_other` (not a merge: 90 ETB cards vs 92 self-scope, overlap 80); `mana_out` (color:amount).

**E. AI tags** (hidden from the reader): `ai_logic` in original case with `@ability` id; `attach_ai_logic:<name>` from `SVar:AttachAILogic`; `ai_timing:` (opp_eot, eot_conditional, main1, main2, before_combat, any_phase) and `ai_target:` (curse, pump, fight, powerdmg, gaincontrol), derived from forge-ai's own logic names; `ai_flag:`, `ai_svar:`, `ai_class:`, `ai_logic_kind`. Check `ai_logic` against the script by regex (deterministic); blind pass only for the derived tags, with per-tag precision; not a blocker.

**F. Tooling and gates.**
- Numeric export: `tempo`, `draw_count`, `damage_amount`, `token_count`, `mana_amount` as numbers; `x` as a flag plus a count, never 0. One row per deck (path, tier, archetype, tagged share, top-card share of tempo / draw), family level only, with a tag version stamp.
- Hold-out set of about 40 decks kept out of any weight tuning.
- Redundancy check with value-level duplicates (two families, tag-set overlap >= 0.85).
- Separate file for the "cost:mana from mtgish only" noise.
- Batch gates for the full-cardlist run: `redundancy()`, reverse check on 40 deck-relevant cards (hard stop if the mean drops > 0.03 vs r4), card-power diff, tagged share of the 400 AI decks >= 95%, family-count diff, list decks whose tier check flips.
- Tag the commanders and the 80 staged tier 1 decks first; read-only check of tag-derived role counts for the 10 starters.

## 3. Not done on purpose
Merging `trigger:etb` with `trigger_scope:self`; merging the three mana tags (derived `mana_out` instead); AI values best_creature / opp_only / own_only; "instant" and "combat" as AI timing values.

## 4. Decisions for the user (answered 2026-10-23)
- **D1: (a).** Treasure and Food makers keep `mana_source` / `lifegain`, linked to the token (`provided_by token_type:treasure`) so a builder can exclude them.
- **D2: no.** AI tags do not feed card power (quota and playability only).
- **D3: C and D first.** Built 2026-10-23 (local, unpushed): `deckgen/derived_tags.py`, `face:` and `derived:` lines in `STARTER_TAGS.toon`. E and F wait.
- **D4: yes.** New AI-side families in E join the AI Tags category on creation, with no per-family approval.

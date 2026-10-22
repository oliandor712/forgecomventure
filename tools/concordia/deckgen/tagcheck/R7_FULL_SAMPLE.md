# R7: full-sample reverse check with the agent suggestions deployed (2026-10-22)

All 353 starter cards, 9 fresh blind readers (40 per batch), tags as deployed: agent suggestions S01-S09 and S15 with the agents' rule fixes (`tag_variant.py`), typing line separated from ability tags, zone split, tag legend, `cost_reduce_*` and `choose_on_enter` fixes, scorer fixed (name replacement no longer hash-seed dependent).

| | cards with text | mean | good / partial / gap | top-1 / top-5 retrieval |
|---|---|---|---|---|
| r7 full | 348 | **0.914** | 318 / 28 / 2 | 306 / 328 |
| r7, the 174 cards also in r6c/r6d | 174 | 0.918 | | (r6c 0.901, r6d 0.900) |
| r7, other 174 cards | 174 | 0.909 | | |

Pure reader noise on identical inputs was SD 0.019 per card (r6c vs r6d), so the +0.017 on the shared half is above noise but the tag changes between r6 and r7 are several at once (suggestions + typing line), so it is not attributed to one change.

Checked cards: Control Magic 1.00 (`steal` on the aura), Sengir Vampire 1.00 (`trigger_scope:damaged_by_self`), Incinerate 0.87, no empty answers.

Lowest 15 (all below 0.6) and what the reader was missing:
- Leafkin Druid 0.35 (conditional mana: "instead" with a creature-count condition; the S06 condition on mana abilities is not deployed for this form)
- Sea Gate Loremaster 0.38, Saruman the White 0.50, Flow of Knowledge 0.59 (`each_all`: a "number of X you control" count has no readable form)
- Vines of Vastwood 0.44 (kicker effect), Elite Scaleguard 0.44 (trigger filters and counters), Mindcrank 0.48 (life loss -> mill link), Explore 0.49 (land drop + draw), Feign Death 0.50, Ripples of Potential 0.51 (proliferate choice), Temple of the False God 0.51 (land-count condition), Colossal Majesty 0.54 (power condition), Desecrate Reality 0.56 (delirium condition), Kami of Whispered Hopes 0.58, Silvergill Adept 0.59 (alternate additional cost).
- Yedora, Grave Gardener 0.59: reader lost the "nontoken creature you control" filter on "another creature dies".

Most remaining gaps are conditions ("if you control N", "number of X you control") and filters on triggers. Next candidates: `condition:` on mana abilities (S06), a readable `count_<thing>` for "number of X you control", trigger filters (`trigger_filter` with controller and token), kicker/alternate-cost effects.

Unverified: one run, scorer is tf-idf plus concept F1 (bands unvalidated).

## Agent suggestions for the weak cards (deck-builder DB, forge-ai-lab AL, balance lab BL; 2026-10-22; nothing applied)
**Priority (BL):** 1 counts ("number of X you control"), 2 conditional mana (flag + base amount), 3 trigger filters, 4 kicker / alternate cost / delirium as three boolean flags only. Order for the full-cardlist run: counts, trigger filters, mana flag, flags. Counts matter most for deck balance because the amount depends on the deck's own density of X; check after the fit whether scaling cards have larger residuals. BL wants a bounded `scales_with:<thing>` list (creatures, lands, artifacts, enchantments, tokens, cards_in_hand, graveyard, devotion, opp_creatures, other) plus `per_unit`.

**One grammar (DB):** reuse `condition:<thing>_<scope>_<cmp><N>` (count_creature_you_control_ge4, card_types_in_graveyard_ge4, kicked) so a builder can map the value to a deck trait count. Duplicates to avoid: `condition`, `activation_restriction`, `cost`, `x_is` exist; only values and one marker (`cost_additional`) are new.

| Gap | Forge script forms (AL) | Tag shape (DB) | Derivable? |
|---|---|---|---|
| Conditional mana (Leafkin Druid, Temple of the False God, Kami of Whispered Hopes) | (a) `IsPresent$ <filter> \| PresentCompare$ GE5` on the mana ability (31 lines; Temple). (b) amount switch: `Amount$ X`, `SVar:X:Count$Compare Y GE4.2.1`, `SVar:Y:Count$Valid Creature.YouCtrl` (149 uses; Leafkin). Kami: `Count$CardPower` | mana group: `mana_amount:1` + `mana_amount_if:2` + `condition:count_creature_you_control_ge4`, link `conditional_on`; Temple's bare `activation_restriction` becomes valued (`count_land_you_control_ge5`); BL: flag `mana_conditional` + base amount | yes for (a) and Compare over `Count$Valid`; hard for chained Compare and generic `CheckSVar$` (1872 uses) |
| Counts (Sea Gate Loremaster, Saruman the White, Flow of Knowledge) | `SVar:X:Count$Valid <filter>` (2002 uses), followed from `NumCards$`/`Amount$`; siblings: ValidGraveyard 493, ValidHand 254, CardPower 267, CardCounters 291, Devotion 49, xPaid 945 | `x_is:count_<thing>_you_control` already exists on Loremaster and Flow, so the miss is not a missing family. DB: check threshold vs count in both scripts (unverified); add `x_cap` / `x_min` for "up to", link `draw_count scales_with x_is`; AL: `count_of:<type>:<you\|opp>`; BL: bounded `scales_with` + `per_unit` | yes for `Count$Valid`; hard for chained SVars; `TriggerCount$LifeAmount` (Mindcrank) = event amount |
| Trigger filters (Elite Scaleguard, Yedora, Saruman) | `ValidCard$ Type.prop+prop`: `.YouCtrl`/`+YouCtrl` 1098/662, `.OppCtrl` 88, `.Other` 531 and `+Other` 221, `.!token` 123 / `+!token` 88, `.token` 26, `+counters_GE1_P1P1` 43, `.powerGE/LE`, `.cmcGE` 41, `.DamagedBy` 23; `ActivatorThisTurnCast$ EQ2` (110) | extend `trigger_filter`: `you_control\|opp_control\|any_player`, `token\|nontoken`, `has_counter:p1p1`, `nth_spell_2`; BL: three axes controller / token / self-vs-another. Saruman's `trigger_filter:you` and `:ctrl` are leaked fragments to fix | yes: split on `[.+]`; nested comma lists and `sharesCreatureTypeWith` are hard |
| Kicker / alternate cost / delirium (Vines of Vastwood, Silvergill Adept, Desecrate Reality) | `K:Kicker:<cost>` 239; effect side `Count$Kicked.4.0` 105 or `Condition$ Kicked` 58; `K:AlternateAdditionalCost:<A>:<B>` 44; delirium / threshold 349 / metalcraft 118 / hellbent 83 / morbid 41 are `Condition$ <Word>` (40 for delirium) or `Count$<Word>` | sub-group per mode: `condition:kicked` with the bonus in its own group; alternate cost via `cost_additional` marker + `cost:` tags with an `or` link; delirium: `kw:delirium` + `condition:card_types_in_graveyard_ge4`; BL: three boolean flags, no effect detail | table lookup |
| Single cards | Explore: `AdjustLandPlays$ 1` Effect; Feign Death: Animate granting a dies trigger; Ripples: Proliferate + Phases; Colossal Majesty: `IsPresent$ Creature.YouCtrl+powerGE4` on the T line; Mindcrank: `Mode$ LifeLost` + `TriggerCount$LifeAmount` | `extra_land_drop:1`; `grant_trigger:dies`; `phase_out`; `trigger_condition` (same grammar); `trigger:life_loss` linked to the mill group | yes |

Not verified: DB wrote from Forge knowledge without reading scripts; AL's counts are line counts over the whole cardsfolder.

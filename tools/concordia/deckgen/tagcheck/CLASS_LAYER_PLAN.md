# Class and specificity layer: plan (2026-10-30)

Goal: a card's tags say whether it is a setup, an engine, a payoff, a tool, a finisher or filler, and how general or narrow it is, so the readers, the deck builder and the power scorer can measure function and quality. User decisions: universal classes on top of the archetype roles; specificity is reported only (no effect on decks or power); the user labels about 50 cards.

## What exists today (checked 2026-10-30)
| Piece | How it works | Fit |
|---|---|---|
| `strategies/strategies.json` | 45 archetypes, each with named roles (aristocrats: fodder, outlet, payoff ...), each role a tag signature `sig`, example cards, count range `n`, and play-line stages | The class layer maps these role names to classes; nothing in the file changes |
| `strategies/strategy_fit.py` | `fit(ftags, ids)` = number of roles of the declared archetypes the card fills; `niche_penalty` for `niche:*` tags nobody uses; `baseline_hit/min` for ramp, draw, protection, recursion | Stays the builder's input. The class is a second, cross-archetype view of the same signatures |
| `deckgen/build.py`, `starter_build.py` | Score = role fit x weight minus niche penalty; quotas from `baseline_roles`; commander support (`commander_support.py`) and the token payoff rule (`synergy.py`, H17) | Unchanged. Class counts can later feed a "setup/payoff balance" check |
| `power_scorer.py` | `tag_roles()` gives ramp/draw/removal/wipe/counter/tutor/fast from tags; the EDHREC-fitted model uses every tag as a feature (`t:tag`, `f:family`) plus the card's archetype membership (`arch:`, `strat:`) | New derived class and specificity tags would become model features if added to ftags; so they stay OUT of ftags until the user decides (report only) |
| Tag system | `tag_extra.py` rules from the Forge script; `setup_card:<need>` tag already marks cards that do nothing until the deck supplies a need; links (`scales_with`, `requires`, `provides`) | Producer and consumer families are already in the tags |
| Glance test | Form: function, roles, archetypes, power, confidence, unclear | Add `class` and `scope`; score three ways |

## Design
1. **Class (derived by script, never hand-tagged).** `tools/concordia/deckgen/tagcheck/card_class.py`, a pure function of the pool record. Classes: setup, engine, payoff, tool, finisher, filler.
   - Mapping table role name -> class, one row per archetype role in strategies.json (generated, with a hand OVERRIDES block like `gen_effect_params.py`). Examples: fodder, enabler, outlet -> setup; payoff, doubler -> payoff; engine, draw_engine -> engine.
   - Cards matching no archetype role: engine if a repeatable trigger or activation produces a resource; tool if a one-shot effect; finisher by win/drain/extra combat/extra turn tags or power above a cutoff; filler otherwise.
   - A card carries a primary class and an optional secondary (decided 2026-10-30); the output lists both.
2. **Specificity (derived, report only).** Count narrowing tags (`target_filter`, `trigger_filter`, `affected_filter`, `setup_card`, tribal `type:` references, `niche:*`, colour restriction). Bands: general, narrow (needs one archetype), dead-without-X (named `setup_card` need). Output is a report file; no ftags, so the power model and builder do not see it.
3. **Glance form.** Add `class` (from the six) and `scope` (the three bands) to the form and to `glance.py` scoring: agreement of tag reader vs Oracle reader, derived vs Oracle reader, and each vs the user's labels.
4. **Missing-tag fill.** Every disagreement between the Oracle reader and the tag reader or the derived class is listed with the tag families involved, in `GLANCE_FIXES.toon` style. New tags are proposed to the user in `NEW_TAGS_FOR_APPROVAL.md`; nothing is added without approval.

## Steps
| # | Step | Output | Cost |
|---|---|---|---|
| 1 | Write the role -> class table generator and `card_class.py`; run on the whole pool | class counts per archetype and overall, 20 sample cards per class for a sanity check | code only |
| 2 | Specificity score and its report | band counts, list of dead-without-X cards | code only |
| 3 | Pick 50 cards spread over archetypes and classes; user labels class and scope | `class_labels.json` | user time |
| 4 | Add `class` and `scope` to the glance form and scoring; glance G4 on the 72 G2/G3 cards plus the 50 | agreement numbers, miss list | one glance run (3 Sonnet tag readers, 1 Oracle reader) |
| 5 | Fix rules from the misses; propose new tags | `GLANCE_FIXES.toon`, approval list | code, user approval |
| 6 | Report: does the class fit the builder's role counts? Compare class counts per deck with the 80 tier 1 decks | one table | code only |

## Risks
- The Oracle reader is a language model; the user's 50 labels are the only check on it.
- Role names differ per archetype (fodder vs enabler); the mapping table will need user corrections.
- Adding class or specificity to ftags would change the EDHREC-fitted power model; it stays out until the user decides.
- A 72 to 122 card sample moves a score by about 1 point per card.

## Decisions on the open questions (user 2026-10-30)
- A card has a primary class and an optional secondary. Scoring uses the primary; a secondary match counts as a partial hit.
- Finisher is tag-based only (win, alternate win, drain, extra combat, extra turn, mass pump, large X effect); power is not used, so the class stays independent of the power scorer.

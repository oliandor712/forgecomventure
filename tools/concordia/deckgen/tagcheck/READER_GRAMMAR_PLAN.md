# Reader grammar: plan for the best instructions on reading a tag record

Planning document, 2026-10-22 (Claude 1). Nothing in it has been built or run. Numbers come from the reverse-check reports and from `runs/r1..r5/results.json` (recomputed for this plan); r6 to r11 are known only from their reports.

## 1. Goal, and what "best" means
Write one instruction set (a "reader grammar") that tells a reader how to turn a card's tag record (`typing`, `tags`, groups `k1 c0 c1 c1.2 ...`, `links`) into the ability text it describes, so that the text matches the real Oracle text as closely as possible.

"Best" = highest reconstruction accuracy on the reverse check, measured as:
- mean similarity per card (0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1),
- share of cards where the real card is the best match among all cards (top-1),
- no empty answers, no name leaks, low reader-to-reader noise.

Proposed targets (yours to change): mean >= 0.94 on the full 353-card sample (r8 now 0.926), top-1 >= 92% (r8: 312 of 348 = 90%), 0 empty answers, and no card worse than 0.05 below its current score unless explained.

Scope question for you (section 8): the grammar is written for the blind LLM reader. The same text can be the spec for deterministic consumers (deck builder, balance fit), but that is an extra phase.

## 2. Evidence so far
| run | cards | mean | top-1 | what changed (reports) |
|---|---|---|---|---|
| r1 | 353 | 0.777 | 219 (63%) | baseline tags |
| r2 | 353 | 0.863 | 266 | detail tags (static, modal, look-at-top, saga, amounts, grants), opaque tags hidden, "no type line" |
| r3 | 353 | 0.873 | 262 | restrict / team pump / token detail, AI tags hidden, reminder texts supplied |
| r4 | 353 | 0.878 | 266 | `x_is` says what X measures |
| r5 | 176 | 0.887 | 144 | half-sample rerun (changes: see `CHANGES_AND_FEEDBACK.md`) |
| r6a-d | 176 | 0.896-0.902 | | scorer fixed, rule 6a (never empty), cost_reduce / choose_on_enter tags |
| r7 | 353 | 0.914 | 306 | agent suggestions S01-S09, `typing:` line, zone split |
| r8 | 353 | 0.926 | 312 | gap tags (trigger filters, conditional mana, conditions) |
| r9 | 20 | 0.786 -> 0.884 | | `scales`, `x_is` rule "write X, not its definition", `mana_restriction` value |

Floor: a dumb tag-to-words dictionary scores 0.60 (top-1 41%), so about 0.17 of the r1 score was reader skill and the rest was tags.

How the numbers were measured, and what limits them:
- Reader noise on identical inputs: SD 0.019 per card (r6c vs r6d). A 40-card batch mean moves about 0.003 from reader noise, a full-sample paired difference about 0.001-0.002.
- The score rewards matching wording and concepts; the 0.7 / 0.4 bands are unvalidated.
- Almost every step changed several things at once ("two things changed at once", R2). The gain of any single instruction is mostly unknown. Only three instruction-only effects were isolated: rule 6a, "write X not its definition", and the `scales` wording (all small samples).
- Only r1-r5 raw results are in the repo. r6-r11 raw results are not (their run data was outside the repo), so section 3 is computed on r1 and r4.

## 3. Accuracy weights: what the reader most needs to be told
Weight = how much total score the topic costs now, how often it fails, and how much a fix gained when one was tried. Loss figures are from r4 (348 cards, total loss 43.1 = sum of 1 - similarity); "excess loss" = cards carrying the family times how far below the overall mean they score. Families overlap, so these are indicators, not additive shares.

| # | Topic the grammar must cover | Evidence | Weight |
|---|---|---|---|
| 1 | Scope and recipient words: "each / all", "you control", "opponent", "may" (optional) | The four most-missed concepts in every run: r4 each/all 32 cards, you_control 30, may 30, opponent 29 (r1: 34 / 49 / 29 / 29). `each_opponent` cards gained +0.05 to +0.09 (R6). | High |
| 2 | Triggers: `trigger`, `trigger_scope`, `trigger_filter`, `trigger_zone` | Largest excess loss in r4 (trigger 3.5, trigger_scope 2.5); most "unclear" tags (trigger 10 of 166). Filters fixed Yedora-type cards partly (0.59 -> 0.75). | High |
| 3 | Amounts and X: `x_is`, `scales`, `*_amount`, `x_paid`, numbers | Cards missing a number 86 -> 28; `x_is` excess loss 2.4; fixes gained +0.22 (Exsanguinate, Gadwick), +0.56 (Sea Gate Loremaster), 20-card group 0.786 -> 0.884. | High |
| 4 | Never empty, partial text plus placeholder, list the unclear tag | Cloud Key 0.57 -> 0.0 and Stonybrook 0.92 -> 0.37 were gaps the reader could not fill; rule 6a followed by no empty answers. | High (protects against zeros) |
| 5 | Draw and damage families: `draw`, `draw_count`, `damage`, `damage_amount` | Second and third largest excess loss in r4 (2.8, 2.7, 1.6). Cause not yet known: amount, recipient or scope? | Medium, needs diagnosis |
| 6 | Conditions: `condition:`, `mana_conditional`, `activation_restriction` | Few cards, big gains per card (Leafkin Druid 0.35 -> 1.00, Temple of the False God 0.51 -> 1.00). | Medium |
| 7 | Zone moves: `from_zone`, `to_zone`, `take`, `rest_*`, `return`, `put_onto_battlefield`, `controller` | Legend added in r5; recursion tags 6 of 8 unclear. Zombify fell 1.00 -> 0.74 when `controller:owner` was misread, now fixed (H67). | Medium |
| 8 | Groups and links: one group = one printed line, `c1.2` = a step of its ability, `links` requires / provides / lasts / receives / conditional_on | No direct measurement. Weak cards that depend on it: Feign Death (granted trigger) 0.50, Desecrate Reality 0.61. | Medium, unmeasured |
| 9 | Keywords and reminder text: write the keyword, not its reminder | Rule exists; no failure reported. | Low |
| 10 | Output form: Oracle wording, one ability per sentence, ` / `, no type line, "this creature" | Type lines in r1 cost score until dropped by the scorer. | Low for accuracy, required by the scorer |
| 11 | Validity rules: only the tags, never a name, say if you recognise a card | Recognised cards 5 -> 0-1; scores 0.82 vs 0.78 for the rest, so little inflation. | Low, but needed so scores can be trusted |

Cards still weak in r8: Vines of Vastwood 0.52 (kicker bonus), Desecrate Reality 0.61, Saruman 0.63, Ripples of Potential 0.64, Kami of Whispered Hopes 0.59. Several are tag gaps, not reading gaps; the grammar must not be asked to fix those.

## 4. Shape of the grammar (v1 draft outline)
1. Record anatomy: `typing` is context only; `tags` are what the abilities do; groups; links; what `kw:` and `x` mean.
2. Reading procedure, in order: read the typing, read group by group (k lines, then c0, then c1...), merge a group's tags into one sentence, apply links, order sentences as printed, then check each number and scope word.
3. Family cards, one short paragraph each, ordered by the weights in section 3 (scope words and triggers first). Each has the tag shape, the wording to write, and a one-line example taken from non-test cards.
4. Ambiguity rules: conflicting tags, an unreadable tag, a missing amount (placeholder `N` or `X`), when to say less rather than guess.
5. Output form and the "do not" list (names, type lines, reminder text, definitions of X).
6. Worked examples: 5 to 8 short ones, none from the cards used to score.
Length cap: about 1,500 words, with the existing per-batch tag legend kept as is. Test a shorter "top-weights only" version too, because longer instructions do not always help.

## 5. Plan
| Phase | Work | Output | Gate to continue |
|---|---|---|---|
| 0 Freeze | Stamp the tag version (commit + variant), fix the scorer, fix the 353-card test set and add a 150-card hold-out sample of non-starter cards (needs `tag_run.py card` on a random sample of the pool) | `tagcheck/GRAMMAR_BASELINE.md` | scorer selftest passes |
| 1 Weights | Recompute section 3 on the current tags: rerun the current reader once (call it r12, 9 readers) so r1-r11 gaps do not matter; per-family excess loss and "unclear" rate; diagnose item 5 | weight table v2 | you approve the order of topics |
| 2 Draft | Write `tags/READER_GRAMMAR.md` v1 (full) and v1s (top weights only) | two drafts, word counts | you read them (checklist doc) |
| 3 A/B, tags frozen | Same 353 cards, same tags, arms: C0 current prompt, C1 + full grammar, C2 + short grammar. 9 fresh readers per arm; paired per card | `R12_GRAMMAR_AB.md` | an arm beats C0 by > 0.01 mean with no card worse than -0.05 unexplained, using the balance lab's gate (hard stop only on a whole-sample mean drop > 0.03 with >= 150 cards, or a paired drop > 0.05 on changed cards) |
| 4 Iterate | Two rounds: rewrite the families with the most remaining loss, rerun only the affected cards plus about 20 unchanged control cards | grammar v2, v3 | control cards stay within noise (0.02) |
| 5 Hold-out | Run the winning arm and C0 on the 150 hold-out cards | generalisation result | hold-out gain >= half of the 353-card gain; otherwise the grammar is overfit and goes back to phase 4 |
| 6 Human check | Hand-read about 30 cards the scorer rated 0.4-0.9 to see whether the score matches meaning (also validates the bands) | note in the report | scorer and human agree on at least 80% |
| 7 Freeze and wire | Commit `READER_GRAMMAR.md` with a version stamp; load it into `tag-blind-reader` through the per-batch reminders file; add a grammar version to the tag stamp; use it as the regression check in the full-cardlist run | frozen v1 | none |
| 8 Optional | Turn the same text into a formal spec (small EBNF plus a deterministic tags-to-text function) for the deck builder and balance fit | `tag_grammar.ebnf` + tests | needs your yes in section 8 |

Estimated reader runs: phase 1 = 9, phase 3 = 27, phase 4 = about 20 (partial reruns), phase 5 = about 8 per arm, so about 80 to 100 single-reader agent runs in total. Cost per run has not been measured. Elapsed time: not estimated.

## 6. Risks and how the plan handles them
- **Overfitting to the 353 starter cards:** held-out sample (phase 5), examples taken from non-test cards.
- **Confounding:** tags are frozen during phase 3, so any change is the instructions alone. Never change tags and instructions in the same run.
- **Scorer limits:** wording-based, bands unvalidated; phase 6 checks it by hand. A gain below 0.01 is treated as noise.
- **Longer is not better:** the short arm tests that.
- **Reader leakage:** the leak check in `reverse_check.py export` stays on; examples must not use test cards.
- **Reader model or prompt drift:** the grammar version goes into the tag stamp; a new reader model means rerunning phase 3.
- **Tag gaps masquerading as reading gaps:** weak cards are triaged first (tag gap -> tagger fix, reading gap -> grammar).

## 7. Who does what
- Whichever main session is on shift runs the phases; the tag-blind-reader agent is the instrument (a fresh instance per batch, never reused).
- The balance lab owns the paired statistics and the gate; the deck builder reviews the family cards for the consumer view (section 8, phase 8); the AI lab is not needed.
- Reader runs and any reader-prompt change are tag-project work. H55 is gone, so nothing in this plan waits on it. The full-cardlist tagging run is not required first.

## 8. Decisions needed from you
1. **Scope:** LLM reader only (phases 0 to 7), or also a deterministic spec for the deck builder (phase 8)?
2. **Targets:** keep mean >= 0.94 and top-1 >= 92%, or set others.
3. **Budget:** about 80 to 100 single-reader runs OK? (Per-run cost is unmeasured; say if there is a ceiling.)
4. **Hold-out cards:** random from the whole pool (proposed), or a chosen set such as the tier 1 commanders' support cards?
5. **Go:** start with phase 0 and 1 (about 9 reader runs), or wait for the answers above.

## 9. Not verified
- Section 3 uses r1 and r4 raw results only; r6 to r11 figures are from their reports. Excess loss is confounded across overlapping families.
- The cause of the draw and damage losses (item 5) is unknown.
- Effect sizes for each instruction are mostly unknown; the plan exists to measure them.
- The 80 to 100 run count is a planning estimate.

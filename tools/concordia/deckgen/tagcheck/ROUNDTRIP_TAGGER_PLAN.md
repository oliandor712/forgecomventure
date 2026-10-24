# Round-trip tagger: plan (2026-10-23)

Planning document. Nothing here is built or run. Facts come from `tag_run.py`, `reverse_check.py`, `GRAMMAR_PERFORMANCE.md`, `learning/LEARNING_DATA.md`. Revised in place.

## 1. Goal
One script that turns Oracle text into tags, turns those tags back into text, and scores the result against the original Oracle text by word use, word count and word order. It replaces the blind reader for routine checks: deterministic, 0 LLM tokens, same answer every run. The end product is a correct tag set per card; the round trip is the test that no fact was lost.

## 1b. No agents in the tool (user order, 2026-10-23)
The tool runs end to end as scripts: `python3 roundtrip.py run --cards <set>` tags, renders, scores and writes the report and one `RUN_LOG.jsonl` row, with no subagent, no LLM call and no token cost. Agents come after, as an audit of the finished result:
- Audit input: the report's lowest-scoring cards, the lines that did not parse, and tag-set disagreements with the script tagger. Agents read only these, never the whole run.
- Audit job: judge whether a flagged difference is a real tag gap, a renderer wording issue or a scorer tolerance issue, and propose the fix. Fixes are applied to the rules or the parser by the main session, then the tool is rerun.
- Optional blind reader pass (`tag-blind-reader`) on a sample, as in section 7, after tagger or renderer changes. Not part of `run`.

## 2. What exists and what is new
| Piece | Today | In the new script |
|---|---|---|
| Card text to tags | `tag_run.py record()` reads the Forge **script**, cross-checks Oracle and mtgish in `tag_verify.py` | Base kept. New: an Oracle-text parser that produces the same tag vocabulary |
| Tags to text | none (reader only; selftest has a "dumb dictionary" floor) | New `render`: rule table mined from reader outputs and the v2 grammar |
| Compare | `reverse_check.score`: tf-idf cosine 0.4, concept F1 0.4, number F1 0.2 | Kept, plus new count and order terms |
| Data to learn from | reader outputs r1..r18 in `~/tagcheck_runs/`, archive, `learning/` (3,000 graded rebuilds, gap backlog) | Mined into the rule table and the gap list |

Location: `tools/concordia/deckgen/roundtrip.py` (new file; imports `tag_run`, `ability_tags`, `tag_extra`, `reverse_check` helpers; nothing in forge sources is touched).

## 3. Logic flow
1. **Input:** card name, Oracle text, and (when available) the Forge script.
2. **Oracle to tags:** split Oracle into ability lines; match each line against patterns (keyword line, triggered, activated, static, spell effect, modal, saga chapter); emit tags from the approved vocabulary only. Where a line is not understood, emit a placeholder tag (`{unparsed}`), never raw text.
3. **Merge with the script tagger:** base record from `tag_run.record()`; the Oracle parse fills gaps and flags disagreements (same role `tag_verify.py` has now).
4. **Tags to text:** per tag group, the most common reader phrasing for that pattern, in the v2 grammar's fixed forms, ordered keywords first, one ability per line. Unknown tags render as `{tag}` so a gap shows up in the text.
5. **Compare:** normalise both texts with `reverse_check.norm` and `tolerate`, then score (section 5).
6. **Report:** per card the score, missing words, extra words, order breaks and the lines that did not parse; one summary row to `RUN_LOG.jsonl`.

## 4. Mining the reader and grammar data
- Collect (tags, reader text) pairs from the archived runs and `learning/`. Group by tag pattern (trigger group, cost, verb with amounts, filters). Rank phrasings by frequency; pick the top one as canonical, keep the rest as accepted variants for scoring.
- Use cards where the readers agreed (V3 signature match, high score) as the rule source; cards with disagreement go to a review list instead of the table.
- Gap backlog from `learning/LEARNING_DATA.md` (conditions via `SVarCompare$` / `ConditionCompare$`, `DigUntil`, `RollDice`, active-zone, lose-keyword, Eternalize / Embalm, Role tokens, Exhaust, Strive, "doesn't untap") is the first list of Oracle patterns to parse.

## 5. Score
Three terms, all from the normalised texts; weights are for you to set (first proposal in brackets):
- **Word use** [0.4]: concept F1 and number F1 as now. A missing keyword or number counts fully.
- **Word count** [0.2]: ratio of token counts and of ability counts (min over max). Catches dropped or invented abilities.
- **Word order** [0.4]: sequence similarity of the stemmed token list (longest common subsequence ratio), plus ability order. Wording that differs but keeps order loses little.
- Pass band to be set from the 353 starters after the first run; do not reuse the reader bands (0.7 / 0.4), since those were calibrated on reader noise.

## 6. Guard against a trivial pass
A parser that copies Oracle words into tags would score 1.0 and prove nothing. Guards:
- Closed vocabulary: every emitted tag must exist in `TAG_REFERENCE.md` / `TAG_LEGEND.md` (the check `tag_run.py` already runs for new families); free text in a tag fails the card.
- Tag count sanity: tags per ability line within the range seen on the 353 starters.
- Agreement with the script tagger: tag-set F1 between the Oracle parse and the script-based record, reported per card. Large disagreement is a finding either way.
- Renderer gets only the tag record, never the Oracle text (same blind rule as the reader; add a leak check that the renderer module does not import or read Oracle).

## 7. Validation against the real reader
- Run the renderer on the 105-card set and the 24 controls; compare its A with the readers' 0.937 (target: within 0.03) and its ability signature with the readers' majority (target: matches on most cards).
- Keep one reader pass on a sample (about 50k tokens per 100 cards) after tagger or renderer changes, to catch what a shared-schema renderer cannot: ambiguous or misleading tags.

## 8. Phases
| # | Phase | Output | Done when |
|---|---|---|---|
| 1 | Mine pairs from archived runs and `learning/` | `render_rules.json` (pattern, phrasing, count) | rules cover the tag families used by the 353 starters |
| 2 | Renderer (tags to text) | `roundtrip.py render` | runs on all 353; unknown tags show as placeholders |
| 3 | Scorer with count and order terms | `roundtrip.py score` | selftest: perfect text 1.0, another card low, empty 0 |
| 4 | First calibration: script tags to text to Oracle, 353 cards | baseline table, pass band | band set from the data |
| 5 | Oracle parser for the common line forms | `roundtrip.py tag` | tag-set F1 vs script tagger on the starters |
| 6 | Gap backlog patterns | updated parser | per-gap coverage table |
| 7 | Reader check on a sample | numbers vs section 7 targets | targets met or gap list written |

Phases 1-4 give a working renderer-based check on today's tags, before any Oracle parsing exists.

## 9. Decisions for you
1. **Source order:** `human_logic.toon` H54 puts the card script first and treats Oracle as a cross-check. Should the Oracle parse stay a cross-check and gap-filler (recommended), or become a primary source?
2. **Order term:** word order weights wording, so differences in phrasing will cost points. Keep order at 0.4, or lower it?
3. **Scope of the first build:** starters (353) only, or also tier 1 cards (2,000 in `learning/`)?
4. **Name and location** of the script.

## 10. Not verified
- Whether reader phrasings are consistent enough per tag pattern to give one canonical text (V1 0.81 says about 4 in 5 cards agree exactly).
- How many Oracle line forms a rule parser can cover; the starters' trigger table (spell 98, etb_self 81, activated 73, static 39, ...) suggests most lines fall in a handful of forms, but this has not been counted.
- No code run for this plan.

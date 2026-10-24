# Round-trip tagger: plan (2026-10-23)

Planning document. Nothing here is built or run. Facts come from `tag_run.py`, `reverse_check.py`, `GRAMMAR_PERFORMANCE.md`, `learning/LEARNING_DATA.md`. Revised in place.

## 1. Goal
One script that turns Oracle text into tags, turns those tags back into text, and scores the result against the original Oracle text by word use, word count and word order. It replaces the blind reader for routine checks: deterministic, 0 LLM tokens, same answer every run. The end product is a correct tag set per card; the round trip is the test that no fact was lost.

## 1b. No agents in the tool (user order, 2026-10-23)
The tool runs end to end as scripts: `python3 mtg2llm.py run --cards <set>` tags, renders, scores and writes the report and one `RUN_LOG.jsonl` row, with no subagent, no LLM call and no token cost. Agents come after, as an audit of the finished result:
- Audit input: the report's lowest-scoring cards, the lines that did not parse, and tag-set disagreements with the script tagger. Agents read only these, never the whole run.
- Audit job: judge whether a flagged difference is a real tag gap, a renderer wording issue or a scorer tolerance issue, and propose the fix. Fixes are applied to the rules or the parser by the main session, then the tool is rerun.
- Optional blind reader pass (`tag-blind-reader`) on a sample, as in section 7, after tagger or renderer changes. Not part of `run`.

## 2. What exists and what is new
| Piece | Today | In the new script |
|---|---|---|
| Card text to tags | `tag_run.py record()` reads the Forge **script**; `tag_verify.py` cross-checks with Oracle and mtgish | Base kept, script only (mtgish dropped). Gap filler: the Oracle section of the script, read by the tagger |
| Tags to text | none (reader only; selftest has a "dumb dictionary" floor) | New `render`: rule table mined from reader outputs and the v2 grammar |
| Compare | `reverse_check.score`: tf-idf cosine 0.4, concept F1 0.4, number F1 0.2 | Kept, plus new count and order terms |
| Data to learn from | reader outputs r1..r18 in `~/tagcheck_runs/`, archive, `learning/` (3,000 graded rebuilds, gap backlog) | Mined into the rule table and the gap list |

Location: `tools/concordia/deckgen/mtg2llm.py` (new file; imports `tag_run`, `ability_tags`, `tag_extra`, `reverse_check` helpers; nothing in forge sources is touched).

## 3. Logic flow
1. **Input:** card name and the Forge script (its Oracle section is the gap filler).
2. **Script to tags:** `tag_run.record()` as today. Where the script leaves a line untagged, the tagger reads that line from the script's Oracle section with pattern rules and emits tags from the approved vocabulary only; a line it cannot read emits a placeholder tag (`{unparsed}`), never raw text.
3. **Disagreements:** where the Oracle gap filler and the script tags disagree, the script wins and the card is flagged in the report.
4. **Tags to text:** per tag group, the most common reader phrasing for that pattern, in the v2 grammar's fixed forms, ordered keywords first, one ability per line. Unknown tags render as `{tag}` so a gap shows up in the text.
5. **Compare:** normalise both texts with `reverse_check.norm` and `tolerate`, then score (section 5).
6. **Report:** per card the score, missing words, extra words, order breaks and the lines that did not parse; one summary row to `RUN_LOG.jsonl`.

## 4. Mining the reader and grammar data
- Collect (tags, reader text) pairs from the archived runs and `learning/`. Group by tag pattern (trigger group, cost, verb with amounts, filters). Rank phrasings by frequency; pick the top one as canonical, keep the rest as accepted variants for scoring.
- Use cards where the readers agreed (V3 signature match, high score) as the rule source; cards with disagreement go to a review list instead of the table.
- Gap backlog from `learning/LEARNING_DATA.md` (conditions via `SVarCompare$` / `ConditionCompare$`, `DigUntil`, `RollDice`, active-zone, lose-keyword, Eternalize / Embalm, Role tokens, Exhaust, Strive, "doesn't untap") is the first list of Oracle patterns to parse.

## 5. Score
Three terms, all from the normalised texts; weights are for you to set (first proposal in brackets):
- **Word use** [0.6]: concept F1 and number F1 as now. A missing keyword or number counts fully.
- **Word count** [0.2]: ratio of token counts and of ability counts (min over max). Catches dropped or invented abilities.
- **Word order** [0.2, user 2026-10-23]: sequence similarity of the stemmed token list (longest common subsequence ratio), plus ability order. Wording that differs but keeps order loses little.
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
| 2 | Renderer (tags to text) | `mtg2llm.py render` | runs on all 353; unknown tags show as placeholders |
| 3 | Scorer with count and order terms | `mtg2llm.py score` | selftest: perfect text 1.0, another card low, empty 0 |
| 4 | First calibration: script tags to text to Oracle, 353 cards | baseline table, pass band | band set from the data |
| 5 | Oracle gap filler for common line forms | `mtg2llm.py tag` | tag-set F1 vs script-only tags on the starters; unparsed lines counted |
| 6 | Gap backlog patterns | updated parser | per-gap coverage table |
| 7 | Reader check on a sample | numbers vs section 7 targets | targets met or gap list written |

Phases 1-4 give a working renderer-based check on today's tags, before any Oracle parsing exists.

## 9. Decisions
Decided by the user (2026-10-23):
- **Order term** weight 0.2 (word use takes the freed 0.2, now 0.6).
- **Scope:** all data enriches the rules (starters, tier 1 `learning/` data, every archived run). The 353 starters carry the highest weight, since they had the most reader passes.
- **Name:** MTG2LLM (`deckgen/mtg2llm.py`; location assumed, say if it should move).

- **Sources (H54 rewritten 2026-10-23):** card script only; mtgish dropped; the Oracle section inside the script is a gap filler for the tagger and is not read as a separate source; keywords via `KEYWORD_REFERENCE.toon` and the smaller CR files (`CR_TAG_RELEVANT.txt`, `CR_INDEX.txt`); the no-time-limit clause removed. This replaces the earlier idea of a separate Oracle-text parser (phases 5-6 now extend the script reader's Oracle gap filler instead).

## 10. Not verified
- Whether reader phrasings are consistent enough per tag pattern to give one canonical text (V1 0.81 says about 4 in 5 cards agree exactly).
- How many Oracle line forms a rule parser can cover; the starters' trigger table (spell 98, etb_self 81, activated 73, static 39, ...) suggests most lines fall in a handful of forms, but this has not been counted.
- No code run for this plan.

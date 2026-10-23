# Efficiency upgrades, session of 2026-10-23 (main session)

Every change in this session lowers token use for lookups or reader runs. Token figures are bytes/4 estimates; no tokenizer was available, and no real lookup counts per run were logged.

## What was added
| Item | File | Effect (measured sizes) |
|---|---|---|
| Master index with tiers, size guide, task to file map | `tools/agents/INDEX.md`, line in `CLAUDE.md` | Tier 0 start-up about 3k tokens; BIG-file list stops whole reads (CR 259k, mined.json 804k, ...) |
| Slice lookups | `tools/agents/lookup.py` (`cr`, `cr --ex`, `kw`, `tag`, `rule`, `card`, `twin`, `size`) | One rule 0.1-1.3k instead of 259k (whole original); one keyword about 0.1k instead of 30.7k (three keyword files whole) |
| Compact CR | `reference/CR_COMPACT.txt` (212k, 82% of original), `CR_INDEX.txt` (1.2k) | Examples dropped only; verified: all 3,161 rule IDs and all 739 glossary entries present; 3,315 of 3,316 non-example paragraphs exact (the one miss was a checker artefact) |
| Game rules file | `reference/CR_GAME_RULES.txt` (125k): chapters 1-7 and 9, plus general 701, 701.1, 702, 702.1a-d | Analysis only; exact subset of CR_COMPACT |
| Tag-relevant rules | `reference/CR_TAG_RELEVANT.txt` (28.5k, 433 rules: 603, 608, 613-615, 704, 903, 106, 111, 121, 122, 602, 724 + cited sub-rules) | vs 37.8k from the original with examples; analysis only; no tag script reads it |
| Merged keyword reference | `ai_lab/KEYWORD_MERGED.toon` (27k), `KEYWORD_CR_FULLTEXT.toon` (49k, flagged: not read unless absolutely needed) | One row per keyword, gaps filled from CR; 31 rows still without reminder (ability words, name mismatches) |
| Generators | `reference/build_cr_compact.py`, `ai_lab/build_keyword_merged.py` | Files are generated; regenerate, never hand-merge. Parser fix: wrapped cross-references ("See rule\n704.") no longer start a new rule (7 rules were cut short) |
| Slim reader layout is now the default | `deckgen/tagcheck/reverse_check.py export` (`--no-slim` restores old) | 60.8k -> 46.6k reader input for a full 353-card export (-23%); selftest passes; not yet run with a real reader on the new default |
| Original CR and PDF flagged read-only-on-request | `INDEX.md`, `reference/README.md` | |
| Do-not-search note for backups, digests, results | `INDEX.md` | backups: 540 text files, about 490k tokens |

## Findings that drive the next steps (measured)
- Reader run, 15 batches: tag_legend is 12.5k of 15.3k reminder tokens (about 830 per batch, repeated); reader brief 0.9k x 15 = 13k; outputs about 24k.
- Taggers and readers never read the CR; the saving from the CR files goes to the main session when it analyses results.
- Boot reading list is about 20k tokens (MAIN_SESSION_BRIEF 3.2k, CONTEXT 2.8k, human_logic 5.1k, TOOLBOX 3.3k, HANDOVER 2.4k, INDEX 2.8k, CLAUDE.md 0.7k); INDEX overlaps CONTEXT and TOOLBOX.
- Bug found and fixed: `lookup.py cr --ex` did not find sub-rules (indented lines).

## Decisions
- User declined a read deny for `tools/concordia/backups/**` in `.claude/settings.json`. Risks listed in the session: partial protection (bash cat/grep still allowed), blocks rollbacks, applies to every session.

## Requested of the next session: HIGH-EFFORT analysis
Run this at high effort before building anything:
1. Verify the savings with real counts: log `lookup.py` calls for a few sessions and count real tokens; replace the bytes/4 figures.
2. Run one real reader pass on the new slim default and compare with the `r17slim*` scores (mean_sim about 0.94) before relying on it.
3. Test, with scored runs, shortening the tag_legend (about 830 per batch) and batch size 48 vs 24.
4. Trim the boot reading list (overlap of INDEX, CONTEXT, TOOLBOX; read human_logic by area).
5. Open proposals not built: shrink the compaction hook, archive stale files (old tagcheck reports, runs r1..r4), TL;DR blocks in long docs, split or index big generated files.
6. Measure what was not looked at: sim, suite, balance_lab and ai_lab output volumes.

## Unverified
Savings per run depend on how many lookups a run needs (unknown). The CR_TAG_RELEVANT overlap measurement (1.1% wording overlap) was taken before the parser fix and not re-run.

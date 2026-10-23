# R16: slim reader layout (token cut), 2026-10-23

Goal: fewer reader tokens with the same model (Sonnet 5.5, medium) and the same grammar (v2, arm C2). Done on the user's "do 1,2,5" (options from the P4e token analysis).

## What changed (`reverse_check.py export --slim`)
1. Bigger batches: about 21-24 cards per batch (5 batches for 105 cards, was 9 of 12).
2. No duplicate tag data: `tags` lists only tags that no group shows (the full set is `tags` plus every tag in `groups`). Family-level tags absent from `groups` stay (68 of 105 cards have some).
3. One file per batch: the reminders (keywords, tokens, `tag_legend`, `reader_grammar`, `output_format`) sit inside the batch file as `reminders`. `--reminders-extra <json>` adds the grammar and output format to every batch.
Also: the leak check scans `groups`; `consistency.py` counts group tokens in the families; `.claude/agents/tag-blind-reader.md` accepts a batch file with embedded reminders.

## Test: same 105 cards as P4e (85 changed + 20 controls), three readers (r17slim, r17slimb, r17slimc)
| Metric | P4e old layout (R14) | Slim layout | Target |
|---|---|---|---|
| V1 exact agreement | 76.2% | 81.0% | >= 85% |
| V2 mean pairwise token F1 | 0.990 | 0.989 | >= 0.95 |
| V3 ability-signature agreement | 93.3% | 93.3% | >= 98% |
| V4 SD of accuracy across readers | 0.0054 | 0.0038 | <= 0.010 |
| S1 style conformance | 99.0% | 99.4% | >= 98% |
| A mean accuracy | 0.938 | 0.937 | >= 0.916 |

Per-run mean similarity (reverse_check): 0.938, 0.938, 0.935.

## Tokens (as reported by the reader subagents)
| | Old layout | Slim layout |
|---|---|---|
| Reader jobs per 105-card set | 9 | 5 |
| Tokens per batch | about 25-28k (12 cards) | 23k (9 cards) to 32k (24 cards) |
| Tokens per 105-card set | about 234k (estimate: 9 x 26k) | about 147k (set a: 23.3 + 30.2 + 30.4 + 30.5 + 32.3k) |
| Tokens per card | about 2.2k | about 1.4k |

Cut: about 37% per set. The old-layout total is an estimate, not a measured sum.

## Verdict and caveats
- Agreement and accuracy are not worse. V1 +4.8 points is about 5 cards of 105, so it may be noise; V3 is unchanged. V1 and V3 targets are still missed (placeholders are the main limit, see PLACEHOLDER_TRIAGE.md).
- Not tested: batch sizes above 24, one grammar copy shared across batches (grammar is still repeated in each batch file), slim output (option 3), trimmed grammar (option 4).
- One reader tried a non-existent reminders path before using the embedded one; the printed reader prompt still says "two files" in rule 1.
- Single comparison on one card set; the "changed" and "control" splits were not scored separately here.

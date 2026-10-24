# Reader grammar: what it is, how it performs, what it costs (2026-10-23)

Summary document. Sources: `RUN_LOG.jsonl`, `R12_GRAMMAR_AB.md`, `R14_GRAMMAR_V2.md`, `R16_SLIM_LAYOUT.md`, `READER_GRAMMAR_PLAN.md`, `tools/agents/logs/`. Revised in place on each update.

## 1. What the grammar is
The instruction set that fixes how a blind reader (`tag-blind-reader`, Sonnet 5.5 / medium) turns a tag record (`typing`, `tags`, groups `k1 c0 c1 ...`, `links`) into Magic-style ability text. The reader sees no card name, cost, P/T or Oracle text. Goal order (user, 2026-10-22): limit variance between readers first, write like a Magic card second, keep accuracy as a guard (A >= 0.916, no drop over 0.01 against C0).

It travels as `reader_grammar` plus `output_format` inside the per-batch reminders (`reverse_check.py export --reminders-extra <json>`), next to keyword and token reminders and a per-batch `tag_legend`.

## 2. Measures
| Measure | Meaning | Target |
|---|---|---|
| V1 | share of cards where all readers' normalised outputs are identical | >= 0.85 |
| V2 | mean pairwise token F1 between readers | >= 0.95 |
| V3 | share of cards where all readers' ability signatures match | >= 0.98 |
| V4 | per-card SD of accuracy score across readers | <= 0.010 |
| S1 | share of ability sentences passing the Oracle-form linter | >= 0.98 |
| A | accuracy vs real Oracle text (guard) | >= 0.916 |

## 3. Results by arm (3 readers each, identical tags)
| Arm | Grammar | Cards | V1 | V2 | V3 | V4 | S1 | A |
|---|---|---|---|---|---|---|---|---|
| C0 | none | 348 | 0.615 | 0.984 | 0.879 | 0.0077 | 0.953 | 0.932 |
| C1 | v1 full, free text | 348 | 0.776 | 0.988 | 0.928 | 0.0045 | 0.972 | 0.927 |
| C2 | v1 full + per-ability records | 348 | 0.776 | 0.991 | 0.968 | 0.0032 | 0.971 | 0.928 |
| C3 | v1 short | 348 | 0.655 | 0.978 | 0.874 | 0.0089 | 0.976 | 0.924 |
| C2 | v2 | 105 | 0.762 | 0.990 | 0.933 | 0.0054 | 0.990 | 0.938 |
| C2slim | v2, slim layout, batch 24 | 105 | 0.810 | 0.989 | 0.933 | 0.0038 | 0.994 | 0.937 |

Reading:
- Full grammar beats none on every consistency measure; accuracy stays inside the gate in every arm.
- Short v1 (C3) gives no gain over no grammar on V1, V3, V4.
- v2 slim is best on V1, V4, S1. V3 (0.933) and V1 (0.81) still miss targets. v2 ran on 105 cards (85 changed, 20 controls), a harder set than the 348, so it is not directly comparable to v1.
- V1 noise is large: three no-grammar repeats on the same 24 control cards gave V1 0.54, 0.71, 0.83. Treat V1 gaps under about 0.1 as noise.
- Known V3 failure causes (R14): trigger wording ("attacks and isn't blocked" vs "becomes unblocked"), `cost:discard` on spells, and `{trigger}` / `{effect}` placeholders spelled differently by each reader.

## 4. Token cost
| Setup | Tokens per batch | Tokens per card |
|---|---|---|
| No grammar (C0) | about 12k (12 cards) | about 1k |
| v2, old layout | about 25-28k (12 cards) | about 2.2k |
| v2, slim, batch 24 | 23-32k | about 1.4k |
| v2, slim, batch 72 (r18) | 34.0k | about 470 |

- The grammar is about 23 KB of a 26 KB reminders file, identical in every batch, and is re-sent in each batch file.
- Slim layout (reminders inside the batch file, tags not duplicated) cut cost per card about 36% with no quality loss (V2 0.990 to 0.989).
- Batch size curve, one reader per size: tokens per card 24=630, 48=531, 72=472, 96=440. Marginal cost 340-430 per card, fixed about 5k per batch. mean_sim 0.942 / 0.944 / 0.946 / 0.938; top1 24/24, 47/48, 69/72, 92/96. Batch 96 left one card without text.
- Recommended: batch 72.

## 5. Ways to cut the grammar cost further (untested)
1. Send only the grammar sections for tag families present in the batch (R16 option 4). Check V1 and V3 against the C2slim baseline.
2. Prompt caching of a byte-identical grammar prefix; depends on the harness, unverified. Reusing one reader across batches breaks the fresh-instance rule.
3. Slim output format (R16 option 3); needs the scorer to accept it.
4. Per-section ablation on the 105 cards to find sections that do not move V1 or V3.

## 6. Not verified
- v2 on the full 348 cards; recommended next step is one 348-card pass at batch 72 with 3 readers and V1-V4, S1, A computed.
- Batch-size runs used one reader each; V1-V4, S1, A not computed for them.
- Tag-stamp changed on 2026-10-23 (STARTER_TAGS.toon sha1 8a3a549f54): runs before and after are not comparable by hash.
- The cost of the grammar alone at batch 72 (no-grammar arm never re-measured with the slim layout).

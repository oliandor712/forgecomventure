# Phase 3 A/B: reader grammar (tags frozen)

Scored 2026-10-23 by the main session from the archived runs (`archive_20261023/tagcheck_runs.tgz`), with `reverse_check.py compare` and `consistency.py compare`. Same 353 starter cards and tags (sha1 ec0f8f6071) in every arm; 3 readers per arm (a/b/c); 348 cards have reader text (the same 348 in every arm).

## Arms
- C0: current prompt (runs r12a/b/c, the baseline).
- C1: full grammar, free text (r13c1a/b/c).
- C2: full grammar plus per-ability `records` (r13c2a/b/c). Reader `text` was already the records joined with " / "; checked, 0 mismatches. Raw copy kept as `out_raw`.
- C3: short grammar (r13c3a/b/c). **Incomplete: `r13c3c` has only batches 1-7 (280 of 353 cards).** The missing batches were not rerun (user chose option A). C3 is therefore scored two ways below.

## Results
| Metric | Target | C0 | C1 | C2 | C3 (a,b only) | C3 (a,b,c; c incomplete) |
|---|---|---|---|---|---|---|
| V1 | >= 0.85 | 0.615 | 0.776 | 0.776 | 0.733 | 0.537 |
| V2 | >= 0.95 | 0.984 | 0.988 | 0.991 | 0.977 | 0.842 |
| V3 | >= 0.98 | 0.879 | 0.928 | 0.968 | 0.905 | 0.701 |
| V4 SD | <= 0.010 | 0.0077 | 0.0045 | 0.0032 | 0.0060 | 0.0965 |
| S1 | >= 0.98 | 0.953 | 0.972 | 0.971 | 0.981 | 0.979 |
| S1b | (no target) | 0.613 | 0.955 | 0.953 | 0.965 | 0.963 |
| A (accuracy) | >= 0.916 | 0.932 | 0.927 | 0.928 | 0.925 | 0.860 |

The last column is dragged down by the 73 cards `c3c` never wrote (counted as gaps); it is shown only so the number is not hidden. Use the "a,b only" column for C3.

Per-reader mean similarity (`reverse_check`): C0 0.931/0.931/0.935; C1 0.927/0.927/0.927; C2 0.928/0.927/0.927; C3 0.923/0.926/(0.732 incomplete).

## Gate
A must stay >= 0.916 and not fall more than 0.01 against C0. Every complete arm passes (drops of 0.005 for C1, 0.004 for C2, 0.007 for C3).

## Reading
- Both full-grammar arms improve every consistency metric over C0. **C2 (grammar plus per-ability records) is best**: V3 0.879 to 0.968, V2 0.984 to 0.991, V4 SD down to 0.0032, S1b 0.61 to 0.95.
- C2 meets V2 and V4 and the A gate; it **misses V3 (0.968 vs 0.98), V1 (0.776 vs 0.85) and S1 (0.971 vs 0.98)**.
- C3 (short grammar) is worse than the full grammar on V1, V3 and V2, but best on S1 (0.981). Based on two readers only.
- V1 is identical for C1 and C2 (0.776), so the records form does not help V1; it helps V3.
- Accuracy falls slightly in every grammar arm (about 0.005). Within the gate, but real in the direction.

## Not verified / caveats
- No repeat of C0 exists, so the noise between two C0 repeats (the plan's "clear improvement" bar) is not measured. The size of the gains (V3 +0.09, S1b +0.34) is large against the reader-to-reader spread inside an arm, but this is not a significance test.
- C3 with only two readers is not directly comparable to the three-reader arms.
- Scores are from unvalidated metrics (phase 6 human check not done).
- The known reader ambiguities from the handover are still open for grammar v2: `controller:you` wording for graveyard puts vs tutor puts; mill without amount; missing-tag placeholders.

## Suggested next step (user decides; phases 4-8 only on go)
Take C2 into phase 4 (iterate on the patterns that still disagree; target V3 and V1), and add the short grammar's S1 strengths if they can be had without losing V3.

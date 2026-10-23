# Phase 3 A/B: reader grammar (tags frozen)

Scored 2026-10-23 by the main session from the archived runs (`archive_20261023/tagcheck_runs.tgz`), with `reverse_check.py compare` and `consistency.py compare`. Same 353 starter cards and tags (sha1 ec0f8f6071) in every arm; 3 readers per arm (a/b/c); 348 cards have reader text (the same 348 in every arm).

## Arms
- C0: current prompt (runs r12a/b/c, the baseline).
- C1: full grammar, free text (r13c1a/b/c).
- C2: full grammar plus per-ability `records` (r13c2a/b/c). Reader `text` was already the records joined with " / "; checked, 0 mismatches. Raw copy kept as `out_raw`.
- C3: short grammar (r13c3a/b/c), three readers. `r13c3c` first lost batches 8-9 (HTTP 429) and was completed on 2026-10-23: those two batches (73 cards) were read by `tag-blind-reader` (claude-sonnet-5-5, medium); the reader of batches 1-7 is unrecorded. Same inputs as before (v1 short grammar), so the arm is complete.

## Results
| Metric | Target | C0 | C1 | C2 | C3 (a,b,c) | C3 (a,b only, earlier) |
|---|---|---|---|---|---|---|
| V1 | >= 0.85 | 0.615 | 0.776 | 0.776 | 0.655 | 0.733 |
| V2 | >= 0.95 | 0.984 | 0.988 | 0.991 | 0.978 | 0.977 |
| V3 | >= 0.98 | 0.879 | 0.928 | 0.968 | 0.874 | 0.905 |
| V4 SD | <= 0.010 | 0.0077 | 0.0045 | 0.0032 | 0.0089 | 0.0060 |
| S1 | >= 0.98 | 0.953 | 0.972 | 0.971 | 0.976 | 0.981 |
| S1b | (no target) | 0.613 | 0.955 | 0.953 | 0.962 | 0.965 |
| A (accuracy) | >= 0.916 | 0.932 | 0.927 | 0.928 | 0.924 | 0.925 |

The earlier two-reader figure is kept for comparison only; the three-reader column is the one to use. Adding the third reader lowers V1 (0.733 to 0.655) and V3, the same effect any extra reader has on agreement metrics.

Per-reader mean similarity (`reverse_check`): C0 0.931/0.931/0.935; C1 0.927/0.927/0.927; C2 0.928/0.927/0.927; C3 0.923/0.926/0.921.

## Gate
A must stay >= 0.916 and not fall more than 0.01 against C0. Every arm passes (drops of 0.005 for C1, 0.004 for C2, 0.008 for C3).

## Reading
- Both full-grammar arms improve every consistency metric over C0. **C2 (grammar plus per-ability records) is best**: V3 0.879 to 0.968, V2 0.984 to 0.991, V4 SD down to 0.0032, S1b 0.61 to 0.95.
- C2 meets V2 and V4 and the A gate; it **misses V3 (0.968 vs 0.98), V1 (0.776 vs 0.85) and S1 (0.971 vs 0.98)**.
- C3 (short grammar), now with three readers, is worse than the full grammar on V1 (0.655), V3 (0.874) and V4 (0.0089) and no better than C0 on V3; S1 (0.976) is the only metric where it is close to the C1/C2 level. The short grammar is not the way to V1 0.85.
- V1 is identical for C1 and C2 (0.776), so the records form does not help V1; it helps V3.
- Accuracy falls slightly in every grammar arm (about 0.005). Within the gate, but real in the direction.

## Not verified / caveats
- No repeat of C0 exists, so the noise between two C0 repeats (the plan's "clear improvement" bar) is not measured. The size of the gains (V3 +0.09, S1b +0.34) is large against the reader-to-reader spread inside an arm, but this is not a significance test.
- Batches 8-9 of C3 were read by a different reader model/effort than batches 1-7 (unrecorded), so C3 reader 3 is not a clean single-reader run.
- Scores are from unvalidated metrics (phase 6 human check not done).
- The known reader ambiguities from the handover are still open for grammar v2: `controller:you` wording for graveyard puts vs tutor puts; mill without amount; missing-tag placeholders.

## Suggested next step (user decides; phases 4-8 only on go)
Take C2 into phase 4 (iterate on the patterns that still disagree; target V3 and V1), and add the short grammar's S1 strengths if they can be had without losing V3.

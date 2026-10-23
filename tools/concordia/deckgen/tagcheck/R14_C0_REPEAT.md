# C0 repeat on 24 control cards (2026-10-23)

Purpose (audit plan P4e): measure the noise of the unchanged C0 prompt. Result: **the repeat is not a noise measurement, because the reader model changed.** The baseline readers (r12) were `tag-blind-reader` at **sonnet / high**; commit `438fcbb12c1` (2026-10-23) set the agent to **claude-haiku-5-5 / low** to follow the subagent rule, and the repeat (r14c0a/b/c) ran on that.

## Setup
24 cards (seed 14, from `~/control24.txt`) whose C2 outputs had no placeholder other than `{cost}`; same tags (sha1 ec0f8f6071), same prompt and `--legend` reminders as r12; batch size 8 (3 batches), 3 readers, all 9 batches written. Baseline = the same 24 cards cut out of r12a/b/c (`r12suba/b/c`, scores recomputed with `consistency.py compare`).

## Results (same 24 cards, 3 readers each)
| Metric | Target | r12 Sonnet/high | r14 Haiku/low |
|---|---|---|---|
| V1 exact agreement | >= 0.85 | 0.833 | 0.542 |
| V2 mean pairwise F1 | >= 0.95 | 1.000 | 0.960 |
| V3 ability signature | >= 0.98 | 1.000 | 0.750 |
| V4 SD | <= 0.010 | 0.0007 | 0.0092 |
| S1 | >= 0.98 | 0.973 | 0.963 |
| A (accuracy) | >= 0.916 | 0.952 | 0.946 |

Mean similarity per reader: r12 sub 0.951/0.952/0.952; r14 0.939/0.949/0.950.

## Reading
- Accuracy is about the same (0.946 vs 0.952), consistency is much worse: V3 falls from 1.00 to 0.75 and V1 from 0.83 to 0.54 on identical cards, tags and prompt.
- So reader capability, not the prompt, drives much of the consistency. The 353-card C0 baseline (V3 0.879) is a Sonnet/high figure; a Haiku/low C0 would be lower, and the phase 3 gains (C1/C2) were measured with Sonnet/high readers.
- 24 cards and one Haiku sample per slot: small, and the control set is biased toward easy cards. Treat the size of the gap as indicative.
- The true same-model noise floor is still **not measured**.

## Consequences for the plan (decisions for the user)
1. Which reader model for phases 4-8? Sonnet/high keeps results comparable with the baseline and phase 3, but conflicts with the standing rule that subagents are Haiku/low only. Haiku/low is allowed but needs its own C0 and C2 baseline (re-run the 353 cards, about 27 reader runs per arm) before any comparison.
2. This strengthens phase 8 (deterministic renderer): it removes reader capability as a variable.
3. Noise floor: a Sonnet/high C0 repeat on the 24 cards needs the rule relaxed; otherwise measure Haiku/low noise by repeating this run once more.

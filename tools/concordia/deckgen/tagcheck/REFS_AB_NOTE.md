# Readers with vs without the tag references (round 4, 72 identical gap cards)

Refs = the four sanitized files in `~/tagcheck_runs/_refs/` (family meanings, legend, keyword and token reminder text; no card data or examples).

| Run | Refs | Mean sim | Good / partial / gap | Top1 | Unclear tags | Cards with a placeholder |
|---|---|---|---|---|---|---|
| g4a | no | .682 | 39 / 26 / 7 | 63 | 126 | 56 |
| g4b | yes | .684 | 39 / 29 / 4 | 68 | 118 | 49 |
| g4c | yes | .683 | 39 / 27 / 6 | 63 | 110 | 50 |

Deviation: small. Mean sim +.001 to +.002, same good count. Refs readers left about 7 to 13% fewer tags unclear and used placeholders on 6 to 7 fewer cards; gap-band cards fell 7 to 4 and 6. The two refs readers differ from each other as much as from the control (top1 68 vs 63), so one run per arm cannot separate the effect from reader noise. Recognised cards: 0 in every run.
Conclusion: refs help a little on unclear tags, not measurably on score. Kept for rounds 5-10 (all arms with refs) as the user asked.

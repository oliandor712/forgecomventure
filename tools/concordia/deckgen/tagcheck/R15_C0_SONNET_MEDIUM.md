# R15: C0 repeat with Sonnet/medium readers (2026-10-23)

Same 24 control cards, same C0 prompt, 3 readers (runs `r15c0a/b/c`, 3 batches of 8 each). Requested by the user after R14 was confounded by the reader model change.

| Run | Reader | V1 | V2 | V3 | V4 SD | S1 | A |
|---|---|---|---|---|---|---|---|
| r12 (filtered to 24) | Sonnet/high | 0.833 | 1.000 | 1.000 | 0.0007 | 0.973 | 0.952 |
| r15 | Sonnet/medium | 0.708 | 0.982 | 0.958 | 0.0060 | 0.973 | 0.949 |
| r14 | Haiku/low | 0.542 | 0.960 | 0.750 | 0.0092 | 0.963 | 0.946 |

Reading: consistency falls steadily with reader strength (V3 1.00 / 0.96 / 0.75), accuracy barely moves (0.952 / 0.949 / 0.946). Target V3 0.98 and V4 0.010 are met only by Sonnet/high here; V1 0.85 by none.

## Caveats
- A repeat with identical model and effort (Sonnet/high vs Sonnet/high) is still not measured, so the pure noise floor is unknown. R15 vs r12 mixes effort change and noise.
- The project rule says subagents are Haiku/low and `.claude/settings.json` sets `CLAUDE_CODE_SUBAGENT_MODEL=claude-haiku-5-5`. I passed `model: sonnet, effort: medium` on the user's request, but cannot confirm the model actually applied (each reader finished in about 10-17 s). If the env var overrides, R15 is another Haiku run, and its better score than R14 would be noise, which would itself be a noise measurement.
- n = 24 cards; one card changes V1 by 0.042.

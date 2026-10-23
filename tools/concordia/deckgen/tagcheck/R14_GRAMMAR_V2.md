# P4e: grammar v2 rerun (2026-10-23)

Plan row: `TAG_RUN_AUDIT_AND_PLAN.md` P4e. Tags: git a2b2c55ed4d (STARTER_TAGS.toon sha1 4c51c22cb4). Readers: `tag-blind-reader`, Sonnet 5.5 / medium, one fresh instance per batch.

## Set
- 105 cards: 85 changed by P4c/P4d (diff of the current export against the r12a baseline) plus 20 control cards (unchanged tags).
- Arm C2 with grammar v2 (full grammar, per-ability records), 3 independent readers: `r16c2a/b/c` (9 batches of up to 12 cards each).
- Arm C0 (no grammar) repeat on the 20 controls, 3 readers: `r16c0a/b/c` (2 batches of 10). Purpose: noise on unchanged cards.
- All 33 outputs present, card ids match their inputs.

## Results (3 readers, identical tags)
| Set | n | V1 | V2 | V3 | V4 SD | S1 | S1b | A |
|---|---|---|---|---|---|---|---|---|
| C2 v2, all | 105 | 0.762 | 0.990 | 0.933 | 0.0054 | 0.990 | 0.970 | 0.938 |
| C2 v2, changed only | 85 | 0.741 | 0.989 (F1) | 0.929 | | | | |
| C2 v2, controls only | 20 | 0.850 | 0.996 (F1) | 0.950 | | | | |
| C0 repeat, controls | 20 | 0.750 | 0.985 | 0.900 | 0.0029 | 1.000 | 0.582 | 0.969 |
Reference, C2 v1 on 353 cards: V1 0.776, V2 0.991, V3 0.968, V4 SD 0.0032, S1 0.971, A 0.928. Targets: V3 >= 0.98, V1 >= 0.85, V2 >= 0.95, V4 SD <= 0.010, S1 >= 0.98, A >= 0.916.

## Against the P4e acceptance rule
- Control cards stay within noise: C2 v2 on the 20 controls V1 0.85 / V3 0.95 against the C0 repeat 0.75 / 0.90 on the same cards (one card is 5 points). The controls did not get worse. Cannot be tested tighter at n = 20.
- V3 >= 0.98 on the changed set: **not met**, 0.929 (6 of 85 cards differ in signature). The 105-card total is 0.933.
- A >= 0.916: met (0.938).
- Met: V2, V4, S1 (0.990, up from 0.971). Missed: V1 (0.762 against 0.85), V3.
- The changed set is the hard set (cards with new tags), so 0.929 is not comparable to v1's 0.968 on 353 cards; no v1 number exists for these same 85 cards.

## V3 failures (7 of 105)
Changed: Daretti, Rocketeer Engineer; Big Score; Goblin Vandal; Syr Konrad, the Grim; Dragon's Rage Channeler; Saruman the White. Control: Search for Tomorrow (the C0 repeat failed Evolving Wilds and Ripples of Potential).
Cause by card (from the three outputs, reader text only):
- Goblin Vandal: "attacks and isn't blocked" against "becomes unblocked" (trigger wording).
- Big Score: additional cost vs a cost with colon vs a separate "Discard a card, then draw" sentence (`cost:discard` with a spell).
- Syr Konrad and Saruman the White: `{trigger}` / `{effect}` placeholders written differently by each reader (missing-tag placeholders; the reader fills one differently each time).
- Families on the failing cards: `trigger_filter` 3, `controller` 2, `from_zone` 2, `put_onto_battlefield` 2, `num` 2.
Not yet checked: Daretti, Dragon's Rage Channeler, Search for Tomorrow.

## Reader token cost (observed, per 12-card batch)
C2 reader about 24-28k tokens (4 tool calls); C0 reader about 12k. The reminders file for C2 is about 26 KB, of which the grammar is 23 KB and identical in every batch. Each card carries its tags twice in the batch file (`tags` and `groups`), and the output repeats each ability text twice. Options listed in the session reply; nothing changed.

## Unverified
Noise floor is still not measured on one fixed set: the controls are 20 cards, and a one-card difference is 5 points. Scores come from `reverse_check.py compare` and `consistency.py compare` (the second wrote to a scratchpad file, not to `GRAMMAR_BASELINE.md`; `REVERSE_CHECK_REPORT.md` was restored with git checkout).

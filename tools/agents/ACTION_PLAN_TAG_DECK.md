# Action plan: tag/deck integration (2026-10-24)

Source: the agreed list and open points in `MEETING_FEEDBACK.md`; vision in `VISION.md`. Main session does the work; agents only when you ask. Nothing live (enemies.json, live decks) changes without your word. Code, data and records wait for your "push"; this document is pushed with docpush.

## Checked facts (open points 3 and 4)

- `TAG_GAPS.toon` is read only by `tagcheck/guards.py` and `tag_reports.py`; `build.py` and `commander_support.py` do not read it. The builder's round-1 claim was right.
- Tier numbers live in three places, as three kinds of number (all inside each other's range today, but nothing ties them):
  - bands: `deck_tier.py` (T2 power 19-31, T4 34-42) and `CONTEXT.md` (T1 <=19, T2 19-31, T3 27-38, T4 34-42, T5 >=39)
  - builder targets: `build.py` `TARGET_POWER` T2 26.5, T3 35.5, T4 40, T5 46.5
  - builder floor and ceiling: T1 from `t1.POWER` (H08 16-18), T2 24.5-30.0
  So the mismatch is real but it is three tables, not a conflict. Item 5 of the list stands.

## Decisions I need from you

| # | Decision | My proposal |
|---|---|---|
| D1 | Who owns the Oracle truth check (reader tests rendering, not truth)? | `tag_verify` plus the starter-set human line checks (rules H71-H73); the reader never claims truth |
| D2 | Sample floor for the commander supported-vs-unsupported test | 25 matched sets per commander (H28 effect-size line), 40 games per deck for a 70-30 read |
| D3 | Run the map and commander_support step first? | Yes: it is the smallest step that makes two tools read one vocabulary |

## Steps, in order

| Step | Work | Done when | Needs |
|---|---|---|---|
| 1 | **Name map.** Script that generates old-to-new tag names from `tag_run.record` over the starter and tier decks (not hand-written). Acceptance: render both vocabularies through mtg2llm and compare; fail on any tag that disappears. | Map file plus a passing check; unmapped tags listed | none |
| 2 | **Tag version stamp.** One id (hash of the tagger record and rule files). Add it to build output, `games_meta.tsv`, suite rows, commander rows. | Every output row carries it; old rows read as "unstamped" | step 1 |
| 3 | **commander_support on the tagger record.** `profile`/`supports` read mapped tags; keep old output for a diff. | Same or better support lists on all current commanders; every change explained | step 1, D3 |
| 4 | **Gap and check-status handling.** Add a check-status field to the record (reader readable, Oracle verified, unverified, who set it). Builder and commander_support read `TAG_GAPS.toon`; gap or unverified tags give no ability bonus and flag the deck. | Flag list printed per deck; flagged decks marked in the diff | steps 1-3, D1 |
| 5 | **build.py, deck_tier.py on the tagger record.** Replace `ability_tags(p)` and `at.tags_of` use via the map. | `build.py --dry` on T1 and tier 2-5 samples: same cards or each change explained | steps 1-4 |
| 6 | **One tier table.** `deck_tier.py` bands, `build.py` target/floor/ceiling and `CONTEXT.md` read one data file with a dated baseline. | No tier number defined twice | step 5; you confirm the numbers |
| 7 | **Regeneration diff report.** After any tag change, regenerate decks and commander rows in one pass; write a per-deck diff (tier, power, commander support), mark old sims stale. | Report on current decks, nothing written to live decks | steps 2, 5, 6 |
| 8 | **Row fields.** Check the suite and game logs for deck id, archetype, colour, timing, command-zone moves, commander cast count; add the missing ones. | Fields present in `games_meta.tsv` or noted as a balance-lab task | step 2 |
| 9 | **Commander harmony.** Score term plus a separate reported score; test with the D2 sample floor. | Result table of supported vs unsupported builds | steps 3, 8, D2 |
| 10 | **Reader metric and second-batch rule.** Report rules accepted, gap rows closed and share rendered with no reader per run; a mined rule needs a second batch before it enters render/compose rules. | Added to `reverse_check.py compare`; one past run backfilled | none (can run beside 1-9) |
| 11 | **Feedback paths.** Misleading tags found by builder, AI lab or balance come back as reader test cases; balance adjusts decks only in bounded, logged steps (target/weakness in decks.json). | Short procedure in `CONTEXT.md` (pushes on your "push") | steps 7, 9 |

## Checks for every step

- Selftests and starter run byte-identical where the step should not change output (baselines in the temp folder).
- Old-versus-new comparison on one T1 deck and the three-card test before and after.
- `human_logic.toon` rules beat any metric; a conflict stops the step and comes to you.
- Estimated size: steps 1-3 are the first session of work; 4-6 the second; 7-11 after the first sims.

## Not in this plan

- Any change to live decks or `enemies.json`.
- AI lab use of the tags (separate track; it only needs steps 1, 2 and 4).
- Moving `tag_reports.py` tables to data files (step 3 part 3 awaits your decision).

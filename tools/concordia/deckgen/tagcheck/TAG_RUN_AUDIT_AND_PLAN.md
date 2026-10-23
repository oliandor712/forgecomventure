# Tag run audit and new plan (2026-10-23)

Audit by the main session of the reader-grammar project data, followed by a revised plan for phases 4-8. Nothing was changed except this document. Supersedes the phase table in `READER_GRAMMAR_PLAN.md` section 5 for phases 4-8 (that file stays as history).

## 1. What was checked and how

| Check | Result |
|---|---|
| Phase 3 scores reproduced from the run dirs (`consistency.py compare`, r12, r13c1, r13c2) | **Match `R12_GRAMMAR_AB.md` exactly** (V1 0.615/0.776/0.776, V3 0.879/0.928/0.968, A 0.932/0.927/0.928, n=348) |
| C3 and other arms not recomputed | C3 figures taken from the report, unverified by me |
| Run dirs `~/tagcheck_runs/r13c*`: batches | 9 runs complete (9 batches each); **r13c3c has 7 of 9** (73 cards missing), as reported |
| `reverse_check.py selftest`, `consistency.py selftest` | Both pass (perfect 1.00, shuffled 0.16, empty 0.00, mechanical floor 0.61; leak check clean) |
| Tags under test | `tags/STARTER_TAGS.toon`: 353 cards, 10 starter decks, unchanged since 2026-10-22 commit `22ed0a7ba61`. Its LF-normalised sha1 is `ec0f8f6071`, the stamp used in the baseline |
| Repo state after the audit | Clean (the selftests write only to `~/tagcheck_runs/selftest`) |

## 2. Findings

1. **Stamp is not portable (bug).** `consistency.py` hashes the raw bytes. On this Windows checkout (`core.autocrlf=true`) that gives `06ea9b8cb4`, on Linux `ec0f8f6071`. Same content, different stamp, so reports made here show a different "tag version". Fix: hash after removing `\r`.
2. **HANDOVER.md is stale.** It still says phase 3 is unscored and lists the setup script path in a deleted container. Phase 3 was scored and pushed (`35a6b826684`). It also says the archive is in a container; it is in the repo (`tagcheck/archive_20261023/`, 6 MB) and the run dirs are on this machine.
3. **Placeholders cap V1, not the grammar.** 88 of 348 cards (25%) have an unfilled placeholder (`{cost}`, `{effect}`, `{filter}`, `{trigger}`) in at least one C2 reader output, 326 occurrences. These are tags that do not carry the information (the "missing-tag placeholders" ambiguity). Rough re-count with a simple normaliser (not the official V1): C2 exact agreement is 98 of 142 (69%) on cards with a placeholder and 172 of 206 (83.5%) on cards without. So even with zero placeholders V1 is about 83-84%, below 0.85, and placeholders cost roughly 8 points. Cards in C0 with placeholders: 93; C1: 90; C2: 88; C3: 93. Grammar barely changed this.
4. **The grammar made the placeholders worse in kind.** C0 used mostly `{cost}`/`{effect}`/`{target}`; the grammar arms use `{filter}` 86-87 times. The grammar standardised spelling (good) but `{filter}` shows the tags lack filter detail on about 90 occurrences.
5. **V3 residual is small and specific.** C2 fails V3 on 11 of 348 cards (3.2%); need 7 or fewer for 98%. Families: `draw` 5 cards, `trigger_filter` 3, `token_*` 2 each, `discard` 2, `counter` 2, `trigger_zone` 2. Named examples: Fact or Fiction (piles, reveal order), Curse of Opulence (who attacks), Unexpected Windfall (additional cost wording), Sweep Away (return then put).
6. **No noise floor.** There is no C0 repeat, so "clear improvement" in the plan's gate is unmeasured. The gains are large (V3 +0.09, S1b +0.34) but not tested.
7. **A drops about 0.005 in every grammar arm**, within the 0.01 gate, consistent in direction. The accuracy metric (tf-idf + concept F1 + number F1, bands 0.7/0.4) is still unvalidated by a human (phase 6).
8. **Scope gap.** All results are on 353 starter cards. The 150-card hold-out (`holdout_cards.txt`) is defined but was never tagged or read. Generalisation is unknown.
9. **Rate limit.** Phase 3 lost reader c3c to HTTP 429. Haiku/low subagents and a cap of 5 concurrent now apply (CLAUDE.md); the plan's old "20 concurrent" estimate is obsolete.
10. **Loose ends from `learning/`.** `COVERAGE.json`: category `OTHER` has 194 cards and no family on either side; `TRIGGER_CONDITION` has 105 cards with no family in old or new tags; `FILTER` 73 and `TIMING` 16. These are the same gaps that appear as `{filter}`/`{trigger}` placeholders.

## 3. New plan

Principle: the tags, not the grammar, now limit V1. Fix the tags that cause placeholders first, then iterate the grammar, then hold-out. Phase 8 (deterministic renderer) moves up because it removes reader variance entirely and is the only route to V1 of 0.85+.

| Step | Work | Output | Gate |
|---|---|---|---|
| P4a Housekeeping | Fix the sha1 stamp (strip `\r`); bring `HANDOVER.md` up to date; re-stamp `GRAMMAR_BASELINE.md` note | small commit | `consistency.py selftest` passes; stamp equal on Windows and Linux |
| P4b Placeholder triage | List every placeholder occurrence in C2 outputs grouped by (card, placeholder, tag family present/absent). For each group decide: tag is missing, tag exists but grammar does not say how to read it, or reader choice | `PLACEHOLDER_TRIAGE.md` | you read it |
| P4c Tag proposals | For missing information (mainly filter, effect, trigger, cost) propose new or extended tags through the normal approval route (`NEW_TAGS_FOR_APPROVAL.md`); no tag change without your approval | proposal list | your approval per tag |
| P4d Grammar v2 | Grammar fixes for the grammar-only items: `controller:you` wording for graveyard puts vs tutor puts, mill without amount, one spelling for unknown parts, Fact or Fiction and Curse of Opulence patterns; keep the C2 `records` form | `READER_GRAMMAR.md` v2 | selftests pass |
| P4e Rerun | Rerun C2 grammar v2 only on cards changed by P4c/P4d plus 20 unchanged control cards, 3 readers; run **one C0 repeat on the same control cards** to measure noise | `R14_GRAMMAR_V2.md` | control cards stay within the measured noise; V3 >= 0.98 on the changed set; A >= 0.916 |
| P5 Hold-out | Tag the 150 hold-out cards (`tag_run.py card`), read with C0 and best arm, 3 readers | generalisation result | hold-out V3 gain >= half of the 353-card gain; else back to P4d |
| P6 Human check | Hand-read about 30 outputs: Magic-card feel, and agreement of the metrics with human same/different | note in the report | >= 80% agreement; validates the score bands |
| P7 Freeze and wire | Commit grammar with a version stamp, load into `tag-blind-reader` reminders, add the grammar version to the tag stamp, V1-V3 as regression check | frozen v1 | none |
| P8 Executable grammar | `tag_render.py` (tags to text, deterministic) with tests; compare to reader majority and Oracle | renderer plus tests | agreement with reader majority >= 95% of cards; A not below best reader arm |

Order change from before: P4b-P4c come before more grammar work; P8 may start in parallel with P5 once P4d is frozen, because the renderer uses the same phrase book.

## 4. Cost and limits

- Reader runs: P4e about 70 cards x 3 readers x 2 arms (C2 v2 and C0 repeat), under 10 reader runs of 8-10 cards each; P5 about 150 cards x 3 readers x 2 arms, about 40 batch runs. Total far below the old 130-190 estimate. Cost per run is unmeasured.
- Readers: `tag-blind-reader` is Haiku/low, at most 5 running at once, started only when you ask. Check the rate limit before launching.

## 5. Decisions needed from you

1. Approve P4a (stamp fix and handover update; code and records, pushed only on your "push").
2. Start P4b (placeholder triage; analysis only, no tags changed)?
3. Is a V1 target of 0.85 still right for reader text, given the placeholder cap, or should V1 be judged only on cards without placeholders until the renderer (P8) exists?
4. Run a C0 repeat on the control cards to measure noise (recommended)?

## 6. Not verified

C3 numbers (not recomputed). The placeholder/V1 re-count uses a rough normaliser. Metrics have no human validation yet. Hold-out generalisation unknown.

## 7. Status (2026-10-23)

P4a-P4c done. **P4d done**: `tags/READER_GRAMMAR.md` is v2 (changes marked `[v2]`, decisions G11-G16) and `READER_GRAMMAR_SHORT.md` has rules 14-18; `consistency.py selftest` passes. Not yet measured on a reader: next is P4e (only on the user's word; check the rate limit first).

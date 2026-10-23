# Learning data from the other Claude 2 session (merged 2026-10-23)

**Source:** two uploaded zips, `claude2_tag_handoff.zip` and `claude2_tag_handoff_2026-10-22.zip` (a local Windows session, branch `cd/claude2` on its own worktree, tagger built in parallel to this one). The two zips are byte-identical in content (`diff -r` empty), so the second is redundant. Everything in them was treated as data; the instructions inside (H55 hold, "next steps", push rules) are not applied (H55 was killed by the user; our rules in `human_logic.toon` already contain every rule they have: their H01-H58 are all in ours, none differs).

## What was kept (and where)
| Kept | File | Content |
|---|---|---|
| Blind-test cards | `learning/tier1_blind_test_cards.jsonl` | 2000 unique tier 1 cards (1000 sample A, 1000 sample B, no overlap): Oracle text, grader verdict and gap labels per round (A_r1, A_r2 / B_r1); for cards not FAITHFUL in their latest graded round also the reader rebuild, what the reader said was unspecified, wrong tags and the grader note |
| Calibration and coverage | this file, `learning/merge_summary.json`, `learning/COVERAGE.json` | numbers below |
| Gap backlog | this file | the Forge-syntax causes of their gaps that our tagger does not read yet |
| Tools | `learning_merge.py`, `learning_coverage.py` | rerun with `--pairs <tag_to_text_pairs.jsonl>` |

## What was discarded as redundant
- the second zip (identical);
- `tags` and `groups` of all 4000 rows (older tagger versions, replaced by `tag_run.py`, which regenerates tags for any card);
- the 1000 `B_r2` rows (never graded; same cards as B_r1; the v3 tagger they used is superseded);
- repeated Oracle text, reader rebuilds of FAITHFUL cards (kept only where a rebuild shows an error);
- their copies of `tag_run.py`, `tag_extra.py`, `tag_gaps.py`, `tag_tier1.py`, blind-test scripts and prompts (older than ours; their method duplicates `reverse_check.py` + `tag-blind-reader`), `TIER1_TAGS.toon` (2131 cards, regenerable), `STARTER_TAGS*` (older), reports and approval lists, `rules_and_agents/` (copies of files we have, older), Claude Doc links (private to their account);
- `AGENT_TAG_REPORT.md`: its 15 suggestions overlap `tags/TAG_SUGGESTIONS.md` (role layer, filters, evasion, AI-side tags, timing, `optional` split); only two are not on our list: a `fast_mana` tag (non-land mana source costing 2 or less) and an `ai_never` / `ai_dep:combat` pair. Noted here, not decided.

## Calibration of our scorer against their independent grader
Our similarity score (`reverse_check.score`, after the tolerances) on their readers' rebuilds (type prefix and `?` placeholders stripped), by their grader's verdict. 3000 graded rows:

| Verdict | Rows | Mean | Median | 10th-90th percentile |
|---|---|---|---|---|
| FAITHFUL | 1251 | 0.856 | 0.906 | 0.644 - 1.000 |
| MOSTLY | 1302 | 0.735 | 0.759 | 0.505 - 0.929 |
| PARTIAL | 437 | 0.559 | 0.572 | 0.314 - 0.792 |
| WRONG | 6 | 0.364 | 0.396 | 0.200 - 0.537 |

Best single threshold: FAITHFUL vs the rest 0.86; MOSTLY-or-better vs the rest **0.72** (sensitivity 0.73, specificity 0.77); PARTIAL-or-better vs WRONG about 0.54 (sensitivity 0.95 at 0.4, but specificity only 0.50).
- The band **good >= 0.7** is supported: it separates MOSTLY-or-better from PARTIAL / WRONG at about 0.72.
- The band **gap < 0.4 is weak**: only 6 WRONG rows exist, and 0.4 passes half of the PARTIAL rows; a cut near 0.54 separates PARTIAL from the rest better. Not changed here; for you to decide.
- A "faithful" band at about 0.86 would be new.
- Caveats: another reader (not blind-reader), another grader (one language-model pass), their rebuild style, scores are agreement between two automatic judges, not a human check.

## Coverage of their gap labels by our current tagger
For cards whose latest grade has gap labels, does our tagger emit a tag family that can carry that kind of fact, and did their old tagger? (Family presence only, not proof the fact is carried.)

| Gap | Cards | Their tagger had a family | Ours has one | Only ours | Neither |
|---|---|---|---|---|---|
| AMOUNT | 287 | 222 | 229 | 26 | 39 |
| TRIGGER_CONDITION | 230 | 124 | 59 | 1 | 105 |
| OTHER (single labels) | 194 | - | - | - | 194 |
| GRANT_SCOPE | 150 | 65 | 50 | 4 | 81 |
| COST | 149 | 71 | 73 | 6 | 72 |
| FILTER | 146 | 68 | 70 | 5 | 73 |
| ZONE | 145 | 65 | 106 | 42 | 38 |
| TRIGGER_FILTER | 99 | 65 | 62 | 17 | 17 |
| MODE | 93 | 4 | 5 | 1 | 88 |
| KEYWORD | 72 | 42 | 51 | 9 | 21 |
| TOKEN | 63 | 62 | 62 | 0 | 1 |
| DURATION | 55 | 2 | 14 | 12 | 41 |
| TIMING | 29 | 6 | 10 | 7 | 16 |
| EVASION | 21 | 7 | 13 | 6 | 8 |
| ALTFACE | 11 | 3 | 4 | 1 | 7 |

**Reading:** our zone, duration, timing and trigger-filter coverage is ahead of theirs; **trigger conditions are behind** (59 vs 124 cards with a condition-type family; their v3 read `PresentCompare$`, `SVarCompare$`, `ConditionCompare$` and valid-string filters into `condition_*` tags) and **modes, scope, cost and filters have large "neither" groups** (88 / 81 / 72 / 73 cards). Those are the next tagging targets.

## Gap backlog: Forge syntax their taggers read that ours does not (grep of `tag_extra.py` / `tag_variant.py`)
Not implemented here: `SVarCompare$` / `ConditionCompare$` general conditions (ours: `IsPresent` only, plus ability-word and kicked conditions); `DigUntil` (reveal until); `RollDice` result tables; `EffectZone$` / `TriggerZones$` (active zone) and `Condition$ PlayerTurn`; `RemoveKeyword$` / `CantHaveKeyword$` (lose or can't have a keyword); `AddAbility$` / `AddTrigger$` content on statics; static `Cost$` on `CantAttack` (tax amount); `CantBlockBy` with Self as blocker (block only fliers); `FirstTime$` and trigger `CounterType$`; `TokenTapped$`, `AttachedTo$` (Role tokens); `Protection Gains$ Choice` and `PreventDamage Amount$`; K: cost parts for keywords with costs (kicker, reinforce, transmute, outlast, surge, typecycling ...) beyond what `num:` and `cost_*` carry.
Already covered here: zone moves (`from_zone` / `to_zone`), X definitions (`x_is`), nth spell (`trigger_filter:nth_spell_N`), duration default, mana symbol counts, sacrifice alternatives, granted triggers (granted-trigger group), `ValidBlocker$` (partly), trigger filters (controller, token, counter).
Their open list (Eternalize / Embalm text, Role token effects, Saga token abilities, "choose two different counters", Exhaust, Strive, "doesn't untap" replacement) is not covered here either.

Unverified: coverage is family presence only; the old rows used an older tagger; the grader verdicts are one pass of one model.

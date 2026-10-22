# Reader grammar: plan for one fixed way to read a tag record

Planning document, revised 2026-10-22 (Claude 1) after the user set the goals below. Nothing in it has been built or run. Numbers come from the reverse-check reports and from `runs/r1..r5/results.json` (recomputed); r6 to r11 are known only from their reports.

## 1. Goals (user, 2026-10-22)
1. **Primary: limit variance.** The same set of ability tags must be read the same way every time: the same reader twice, and different readers, give the same text.
2. **Secondary: write like a Magic card.** The reader's output follows the way Oracle text is structured and worded (keywords first, one ability per line, the standard trigger / activated / static forms, standard phrases and number style).
3. **Guard, not goal: accuracy.** Matching the real Oracle text (the old reverse-check score) must not get worse. It is a non-regression gate, no longer the thing being maximised.

"Grammar" here = the instruction set that fixes how a reader turns a tag record (`typing`, `tags`, groups `k1 c0 c1 c1.2 ...`, `links`) into text. The strongest way to guarantee the same reading every time is to make the grammar executable (section 5, phase 8). That is my recommendation; decision in section 8.

## 2. How variance is measured (new, none of this exists yet)
The old reverse check scores one reader against the real card. It cannot see two readers disagreeing in wording when both score alike. New measures, all on identical tag inputs read by k independent readers (proposed k = 3):

| Measure | Definition | Why |
|---|---|---|
| V1 exact agreement | share of cards where all k outputs are identical after normalising case, punctuation and spacing | strictest "same way every time" |
| V2 text agreement | mean pairwise token F1 between outputs of the same card | partial credit for near-identical wording |
| V3 structure agreement | outputs parsed into an ability signature (ordered list of kinds: keyword / triggered / activated / static / spell effect, with their trigger event, cost tags and effect verbs); share of cards where all k signatures match | catches reordering, merged or split abilities, missing or added clauses |
| V4 score spread | per-card standard deviation of the old accuracy score across the k readers | continuity with earlier numbers (6c vs 6d: SD 0.019) |
| S1 style conformance | share of an output's ability sentences that match the Oracle-form linter (section 4, rule set B) | secondary goal |
| A accuracy (guard) | mean similarity as before | must not fall by more than 0.01 |

Proposed targets (yours to change): V3 >= 98% of cards, V1 >= 85%, V2 >= 0.95, V4 SD <= 0.010 (now 0.019), S1 >= 98%, A not below the r8 level of 0.926 minus 0.01. Baselines for V1, V2, V3 and S1 are unknown until phase 1.

## 3. What the earlier runs say about variance
- Reader noise on identical inputs was SD 0.019 per card (r6c vs r6d, 174 cards); 2 cards moved by more than 0.1, none by more than 0.2. Before the scorer and reader-rule fixes it was SD 0.081 with 12 and 4 such cards. Most of that older "variance" was the scorer (name replacement depended on the hash seed), the rest was tags the reader could not read.
- Score spread understates text spread: two readers can phrase the same ability differently and both score 0.9. No run kept the readers' texts side by side for identical inputs, so wording variance has never been measured. That is phase 1.
- Known sources of reader-to-reader differences, from the reports:
  1. **Definitions and padding:** r8 readers wrote "X is the amount of mana paid for X", r7 readers did not (Exsanguinate and Gadwick moved by about 0.22 on identical tags). Fixed for `x_paid` by a rule; the same class of difference can exist elsewhere.
  2. **Gaps filled by guessing:** Cloud Key scored 0.57 for one reader and 0.0 for another when the tags gave nothing to say. A placeholder rule (6a) removed the empties.
  3. **Scope and optional words:** "you control", "each / all", "opponent", "may" are the most often dropped or added concepts (about 30 cards each in r4). These are the places two readers most likely differ.
  4. **Equivalent wordings:** "put onto the battlefield" vs "return to the battlefield", "target creature an opponent controls" vs "target opposing creature", "deals X damage" vs "X damage is dealt". Not measured; expected from how free-form text behaves.
  5. **Ordering and splitting:** one ability as one sentence or two; abilities in tag order vs printed order. Not measured.
  6. **Self-reference:** "this creature" vs "it" vs the card name (names are blocked; type comes from `typing`).
- Reader integrity so far: leak check clean, recognised cards 0 to 1 per run.

## 4. Shape of the grammar
**A. Reading procedure (fixes order and merging)**
1. Read `typing` only to choose the self-reference word (`this creature`, `this permanent`, `this spell`, `this land`...).
2. Process groups in a fixed order: `k` groups (keyword lines) first, then `c0` (card-level), then `c1`, `c2`, ... in order; a sub-group `cN.M` is a step of group `cN`; read it as the next sentence of that ability.
3. Each group becomes exactly one ability, written in one fixed form (rule set B). Links decide wording inside an ability (`requires` = cost or condition, `lasts` = duration, `receives` = what the effect gives, `produces` = what it makes, `conditional_on` = "if ...").
4. Fixed precedence for competing tags and a fixed way to say "unclear": placeholder tokens `{cost}`, `N`, `X`, and the tag is named in `unclear`; never guess a number or a filter.
5. Never add a definition, a reminder text, a type line or a name; never drop a scope tag.

**B. Oracle structure and wording (secondary goal)**
- Output = the card's rules text, one ability per line (joined by ` / ` in the file), keywords first, then abilities in printed order.
- Keyword abilities: the keyword with its number or cost, no reminder text. Several keywords on one line separated by commas where Oracle does so.
- Triggered: `When / Whenever / At the beginning of <event>, <effect>.` (`When` for one-time events such as enters or dies, `Whenever` for repeatable ones, `At the beginning of` for steps and phases), with the optional limits in the standard spots (`This ability triggers only once each turn.`).
- Activated: `<cost>: <effect>.` with costs in Oracle order and symbols (`{T}`, `{1}{B}`, `Sacrifice a creature`).
- Static and spell abilities: one sentence per effect, imperative for spells (`Draw a card.`), declarative for permanents (`Creatures you control get +1/+1.`).
- Targets and scope: `target <type>`, `up to N target ...`, `each opponent`, `you control`, `an opponent controls`, `you may` for optional effects, `instead` for replacement effects.
- Numbers and style details (number words vs digits, `its`/`that creature` back-references, capitalisation) are not guessed: they are taken from frequency counts over the Oracle texts of the card pool in phase 0, so the grammar matches how cards are really printed.
- Rule set B is also the **style linter** used for S1.

**C. Phrase book: one canonical sentence per tag pattern.** A table from tag patterns (family, value, scope, links) to one wording, plus a decision table for every tag combination that has more than one valid reading. Built from the families in `TAG_LEGEND.md` and `TAG_REFERENCE.md`, ordered by how much disagreement they cause (measured in phase 1; until then by the earlier miss counts: scope words, triggers, amounts and X, draw and damage families, conditions, zone moves).

**D. Output form (reduces free-form variance).** Instead of free text the reader returns one record per group: `{group, kind, text}` where `kind` is one of keyword / triggered / activated / static / spell and `text` follows B. The file is then joined in the fixed order. This is tested as its own arm.

**E. Worked examples:** 8 to 12 short ones, covering each ability kind, none taken from the cards used for scoring.

Length cap about 1,500 words for the instruction part plus the phrase book as a table; a shorter "top-disagreement families only" version is tested too, because longer instructions do not always help.

## 5. Plan
| Phase | Work | Output | Gate to continue |
|---|---|---|---|
| 0 Freeze and tools | Stamp the tag version; fix the 353-card test set and a 150-card hold-out sample of non-starter cards (needs `tag_run.py card` on a random pool sample); add `consistency` (V1 to V4), the ability-signature parser and the style linter to `reverse_check.py`; count Oracle style statistics (number style, phrase frequencies, ability order) over the card pool | `GRAMMAR_BASELINE.md`, tools with selftests | selftest: identical texts give V1 = 100%, scrambled ability order breaks V3, a text in non-Oracle form fails S1 |
| 1 Variance baseline | Current reader prompt, 3 independent readers per batch (9 batches, 27 reader runs), identical tags | V1 to V4, S1, A; list of cards and tag patterns where readers disagree; per-family share of the disagreement | you approve the target numbers and the order of families |
| 2 Phrase book and grammar draft | Write the phrase book, decision tables and procedure for the highest-disagreement families first; two versions: full and short | `tags/READER_GRAMMAR.md` v1 and v1s | you read the draft (checklist doc) |
| 3 A/B, tags frozen | Same cards and tags; arms C0 current prompt, C1 grammar (free text), C2 grammar + per-group output records (D), C3 = C2 with the short grammar; 3 readers per arm per batch | `R12_GRAMMAR_AB.md` | an arm raises V3 and V1 clearly (more than the noise between two C0 repeats, from phase 1) with A not falling by more than 0.01 (balance lab gate: hard stop on a whole-sample mean drop > 0.03 with >= 150 cards or a paired drop > 0.05 on changed cards) |
| 4 Iterate | Two rounds on the patterns that still disagree; rerun only the affected cards plus about 20 unchanged control cards | grammar v2, v3 | control cards stay within noise |
| 5 Hold-out | Winning arm and C0 on the 150 hold-out cards, 3 readers each | generalisation result | hold-out V3 gain at least half of the 353-card gain; otherwise it is overfit and returns to phase 4 |
| 6 Human check | Hand-read about 30 outputs: do they read like real Magic cards, and do the linter, signature parser and my judgement agree on "same / different" | note in the report | at least 80% agreement; this also validates the old 0.7 / 0.4 score bands |
| 7 Freeze and wire | Commit `READER_GRAMMAR.md` with a version stamp; load it into `tag-blind-reader` through the per-batch reminders file; add the grammar version to the tag stamp; use V1 to V3 as a regression check in the full-cardlist run | frozen v1 | none |
| 8 Executable grammar (recommended) | Turn the phrase book into a deterministic tags-to-text function (small formal grammar plus tests). Variance is then zero by construction. Check it against the reader majority and against Oracle text; the reader then verifies or paraphrases instead of inventing the wording. The deck builder and balance fit can use the same renderer | `tag_render.py`, `tag_grammar.ebnf`, tests | renderer agreement with reader majority >= 95% of cards and accuracy A not below the best reader arm |

Estimated reader runs (single-reader agent runs): phase 1 = 27, phase 3 = 4 arms x 3 readers x 9 batches = 108 (or about 72 without C0, which phase 1 already gives), phase 4 about 30, phase 5 about 24. Total about 130 to 190. Cheaper path: 2 readers instead of 3 and a 150-card subset for phase 3: about 70 in total. Cost per run is unmeasured; elapsed time is not estimated.

## 6. Risks and how the plan handles them
- **Variance cannot reach zero with free-text readers.** Even with a strict grammar a model can choose another synonym. Phase 3 measures how close it gets; phase 8 is the way to a guaranteed result. The reader model's temperature cannot be set from here.
- **A single canonical wording can hide meaning** if the tags are ambiguous. The phrase book lists every ambiguous tag combination and decides it once; unreadable tags stay `unclear`, never guessed.
- **Overfitting to the 353 starter cards:** hold-out sample (phase 5); examples taken from non-test cards.
- **Confounding:** tags are frozen during phase 3, so any change is the instructions alone. Tags and instructions never change in the same run.
- **Metrics are new and unvalidated:** the signature parser and linter are tested by selftest (phase 0) and by hand (phase 6) before they gate anything.
- **Style rules from memory would be wrong in places:** they come from counts over the card pool, not from my recollection.
- **Tag gaps masquerading as reading gaps:** weak cards are triaged first (tag gap goes to the tagger, reading gap goes to the grammar).
- **Reader leakage:** the leak check in `reverse_check.py export` stays on.
- **Reader model or prompt drift:** the grammar version goes into the tag stamp; a new reader model means rerunning phase 3.

## 7. Who does what
- Whichever main session is on shift runs the phases; `tag-blind-reader` is the instrument (a fresh instance per batch, never reused).
- The balance lab owns the paired statistics and the gate; the deck builder reviews the phrase book from the consumer side and is the first user of the renderer; the AI lab is not needed.
- Nothing here waits on H55 (gone) or on the full-cardlist tagging run.

## 8. Decisions needed from you
1. **Executable grammar:** build the renderer (phase 8) as part of this project? It is the only route to truly identical output.
2. **Targets:** keep V3 >= 98%, V1 >= 85%, V2 >= 0.95, V4 SD <= 0.010, S1 >= 98%, accuracy not below 0.926 minus 0.01?
3. **Budget:** about 130 to 190 reader runs (about 70 on the cheaper path)? Per-run cost is unmeasured; say if there is a ceiling.
4. **Self-reference:** `this creature` / `this permanent` by card type (current practice), or the Oracle placeholder `~`?
5. **Hold-out cards:** random from the pool (proposed), or a chosen set?
6. **Go:** start with phase 0 and 1 (tools plus 27 reader runs), or wait?

## 9. Not verified
- No variance baseline exists; V1 to V3, S1 and the signature parser are proposals.
- Section 3 items 4 to 6 are expectations, not measurements. The draw and damage family losses from the earlier plan are still undiagnosed.
- Effect sizes for each instruction are mostly unknown; almost every earlier step changed several things at once.
- The reader-run counts and the targets are planning estimates.

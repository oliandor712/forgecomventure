# Glance test plan (2026-10-25)

**Goal (user):** a card's tags must be readable enough that Claude understands what the card does at a glance. That serves the deck AIs (deck builder, commander_support, balance) and the AI lab. The reader round that rebuilds Oracle text from tags is only a proxy: it stayed flat at 0.73-0.79 through g11-g27, and the legend fix (0.787 -> 0.783) and the structure folds (0.730 -> 0.728) moved nothing. Stop chasing that score; test the goal.

## What the test asks
Each reader sees only the blind tag view of one card (`cards.tag_blind`: typing, tags, groups, links; no name, no Oracle text) plus the `_refs/` files. For every card it fills one fixed form, in JSON, no prose essay:

| Field | Allowed values | Scored against |
|---|---|---|
| `function` | one line, 15 words max: what the card does | Oracle-reader's line (concept match, judged by `concept_f1` words) |
| `roles` | 1-3 from the role names in `tools/concordia/strategies/strategies.json` (fodder, payoff, outlet, ramp, removal, draw, finisher ...) | Oracle-reader's roles, set F1 |
| `archetypes` | top 3 of the 34 ids in `strategies.json` the card fits | Oracle-reader's top 3, hit if any overlap; plus the card's listed `cards` entries in `strategies.json` as a free key where present |
| `power` | band 1-5 (1 filler, 3 solid playable, 5 bomb) | `deck_tier.py` card power band, hit if within 1 |
| `confidence` | 1-5 | calibration: confidence vs. agreement |
| `unclear` | tags the reader could not use | counted; each repeat is a tag to fix |

## Ground truth
A second reader (a different `tag-blind-reader` run) sees the card name and Oracle text and fills the same form. Agreement between the tag reader and the Oracle reader is the score. Claude spot-checks 20 cards by hand and the user may judge 20 (as in the MTG2LLM line check). The Oracle reader never sees the tag view and the tag reader never sees Oracle text.

## Sample
72 cards per round, 3 tag readers per round plus one Oracle reader, stratified: 24 creatures, 12 instants/sorceries, 12 artifacts/enchantments, 12 lands/mana, 12 multi-ability (3+ ability groups). Half from the live T1-T5 decks (what the deck AIs use), half from the pool by `--modern`. No pre-6th cards. Export: `reverse_check.py export --cardlist` with a new `--glance` form (to build: form instead of text key; reuse leak check).

## Metrics (per round, mean over cards and readers)
1. role F1, archetype hit rate, power within 1, function concept match
2. unclear-tag rate (tags listed unclear per card) and which tag families
3. calibration (confidence vs. agreement), reader spread (3 readers agree on role set)
4. tokens per card

## Variants (A/B, same 72 cards)
- A current tags
- B cleaned: drop `forge_line:*`, fold the 51 ambiguous `x` groups by hand-made rules, drop duplicate tags
- C compact: B plus short machine IDs for the 30 most frequent tag families (tests whether shorter tags help or hurt a glance)
Pass: a variant wins if role F1 and archetype hit both rise and unclear-tag rate falls, with the same cards.

## What a miss becomes
Each card where tag reader and Oracle reader disagree on role or archetype is read by Claude: (1) tag missing, (2) tag present but unclear, (3) Oracle reader wrong. Types 1 and 2 go to a fix list `tags/GLANCE_FIXES.toon` (tag, card, reason) and drive tagger and legend changes. The old reader/render-rule loop pauses except for rule mining that costs nothing.

## Consumers check (before tagger work)
Grep which tag families `deckgen/*.py`, `commander_support.py`, `deck_tier.py`, `strategy_fit.py` and `tools/concordia/ai_lab/` read. A family nobody reads is lower priority; a family many read is first. Output: `tags/TAG_CONSUMERS.toon` (family, readers, count).

## Steps
1. Consumers check (cheap, no readers).
2. Build the glance form export and scorer (`reverse_check.py glance-export|glance-compare`).
3. Round G1: variant A on 72 cards, 3 tag readers + 1 Oracle reader. Gets the baseline.
4. Read the misses, write `GLANCE_FIXES.toon`, fix tags/legend, round G2 on the same cards.
5. Variants B and C if G2 shows tag noise matters.
6. Log every round in `tools/agents/logs/log-tag-analyses.toon` (topic `glance`) and the memory file `readers.md`.

## Not decided (user)
Sample mix, whether the user judges 20 cards, whether variant C (short IDs) is worth trying.

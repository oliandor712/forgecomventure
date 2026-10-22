# Reverse tag check, run r1: findings

353 starter cards, 9 blind readers (agent `tag-blind-reader`, tools Read+Write, 40 cards each, tags only). Scored by `reverse_check.py`; full tables in `REVERSE_CHECK_REPORT.md`. Reader outputs and per-card scores are kept in `runs/r1/` (the answer key is not).

## Result
| | readers (r1) | dumb tag-to-words dictionary (floor) |
|---|---|---|
| mean similarity (348 cards with ability text) | 0.77 | 0.60 |
| real card ranked #1 of 353 by its reconstruction | 223 (64%) | 141 (41%) |
| real card in top 5 | 293 (84%) | 238 (68%) |
| good / partial / gap | 232 / 95 / 21 | 121 / 167 / 60 |

The tags carry most of the meaning: a reader who never saw the card or its text got the right card as best match for about two in three cards. By card type: lands 0.91, creatures 0.79, artifacts 0.79, sorceries 0.78, instants 0.72, enchantments 0.64.

## What the tags do not carry (hand-read from the lowest 25 cards and the readers' `unclear` lists)
1. **Static and continuous effects are missing.** Benalish Marshal (anthem) has no ability tag at all; Predatory Wurm's conditional +2/+2 has none; Storm-Kiln Artist's "+1/+0 for each artifact", Kami of Whispered Hopes's replacement effect, Laboratory Maniac's "win instead", Lightning Mare's "can't be blocked by blue creatures" and "can't be countered" are not tagged. Bug in the tagger (static Continuous pump with Affected$ Creature.Other+YouCtrl is not read).
2. **Amounts.** 86 of 348 cards lose a number (+N/+N, N damage, N life, X). X meaning is lost too (devotion, number of Swamps / Elves / Allies). Readers had to write placeholders (N, X); the scorer counts those as missing numbers.
3. **Modal spells** ("choose one") have no mode tags: Valorous Stance, Return of the Wildspeaker, Disciple of the Ring.
4. **Look / reveal / pick effects.** `selection` is opaque: Militia Bugler, Dig Through Time, Fact or Fiction lost "look at the top N, take K with a filter, rest to bottom / piles".
5. **A wrong tag.** Feign Death and Supernatural Stamina are tagged `transform` (and `reanimate`); the real effect is "gains: when this creature dies, return it to the battlefield". The reader read them as transform.
6. **Saga chapters** (Time of Ice) are not tagged; **non-mana costs** ("return a land you control") and **cost amounts** are lost.
7. **Opaque umbrella tags** the readers could not turn into rules text: `tempo:*` (94 cards, a metric, not text), `burn`, `removal`, `selection`, `fixing`, `restrict`, `pump_team`, `artifact_token`, `ai_logic:*` (21).
8. Tag families whose cards read worst: pump_single 0.51, life_loss 0.57, selection 0.58, pump_team 0.61, scales 0.63. Best: put_tapped, land_tutor, cost_sacrifice_target, shuffle, token_pt, tutor_* (0.90-0.94).

## How far to trust the numbers
- **Scorer fixes made after the run (found by reading the outputs, not by the readers):** basic lands' text is only reminder text (it was being deleted); readers wrote type lines ("Elf Druid creature.") which are now dropped before scoring; an empty reconstruction now scores 0 and counts as a gap; a basic land's name as a tag value is not a name leak. Self-test after the fixes: real text 1.00, another card's text 0.16, no text 0.00, dictionary 0.60.
- **Bands (0.7 / 0.4) are unvalidated.** Reading six partial cards (0.55-0.65): Phyrexian Rager and Moment of Heroism are essentially right and lose points only for the missing number; Desecrate Reality and Soratami Savant lose real content. So "partial" mixes both; treat the missing-number column separately (mean 0.78 with numbers ignored).
- **Recognition:** the readers said they recognised 5 cards (Kodama's Reach, Swords to Plowshares, Scavenging Ooze, Kiki-Jiki, Curse of Opulence); those score 0.82 against 0.78 for the rest, so little inflation. Not checked: whether unreported recognition happened.
- **Reader isolation** rests on the tool list (no shell, no search) and the prompt; each reader made 3 tool calls (Read, Write, reply), which fits that. The transcripts were not audited line by line.
- One reader pass per card, one model: a second pass would show reader noise. Not done.

## Suggested next steps (for the full-cardlist run, your call)
Tag static effects (anthem / conditional pump / replacement / restriction), keep amounts and X meaning as tags, add mode tags, split `selection` into look / take / filter / rest, fix the `transform` mis-tag, tag saga chapters; then rerun r1 as r2 and compare per family.

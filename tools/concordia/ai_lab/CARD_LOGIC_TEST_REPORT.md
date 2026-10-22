# Card logic test report: Forge syntax (A) vs mtgish (B)

Main session, 2026-10-22. Research only: no edits to forge-ai, card scripts or `ability_tags.py`. Method A by forge-ai-lab (`CARD_TEST_A_FORGE.md`), method B by the main session (`CARD_TEST_B_MTGISH.md`). Both ran on the same two lists of 50 cards.

## Question
Where should `AILogic$` and ability tags be placed? Each method predicts both for cards, and is scored against cards that already carry them.

- **Set C (control):** 50 tier 1 pool cards that have `AILogic$` and tags. Hidden, predicted, compared with the actual values (leave-one-out).
- **Set T (test):** 50 tier 1 pool cards with no `AILogic$` and no tags (`tags_of` returns nothing for all 50). Proposals only; no ground truth.

## How each method works
| | A: Forge syntax | B: mtgish |
|---|---|---|
| Reads | the script: first A/S/T/R/K line (kind, API, cost shape) | the English rules text, already parsed by mtgish (`i5jb/mtgish`, MIT) |
| Predicts `AILogic$` | most common value among cards with the same primary signature, else same API | value of the most similar card by overlap of mtgish rule nodes |
| Training pool | 1,814 cards with `AILogic$` | 1,676 of them (those present in mtgish) |
| Tags | gap analysis against `ability_tags.RULES` | learned node-to-tag mapping (precision at least 80%, support at least 5) plus gap list |

## Results on set C
| Measure | A: Forge | B: mtgish |
|---|---|---|
| `AILogic$` exact | 18 of 50 (36%) | 33 of 50 (66%) |
| ...exact or partial (A's grading) | 31 of 50 (62%) | n/a |
| Tag score | not scored (the existing tags were produced by `ability_tags.py` from these scripts, so the check is circular) | precision 0.82, recall 0.51 (same circularity; read as agreement, not accuracy) |

**Per card, strict value match:** both right 17, only mtgish right 16, only Forge right 1, neither 16.

**Agreement is a strong signal:** on the 18 control cards where both methods predicted the same value, 17 were correct (94%).

**Why A scores lower:** A uses the first line of the script, and keyword (K) lines usually come first, so Enchant, Flying and Crew became the signature (Enchant auras all predict `NeedsPrevention`; Passenger Ferry's Crew gave `ReplaySpell`). A's own fix, preferring A/S/T lines, has not been run, so 36% is the unfixed figure.

## Results on set T
- Both methods proposed an `AILogic$` for most cards, but they **agreed on only 4 of 50**, and none of those four had a close mtgish lookalike (similarity at least 0.6).
- mtgish found a confident lookalike (at least 0.6) for **11** of the 50.
- A proposed "none needed" for 3 (Bombur, Relentless Pursuit, Death Ward): no card with `AILogic$` shares their ability type.
- Reading: most T cards probably do not need an `AILogic$`; the generic logic for their ability type already handles them. Only cards where the methods agree, or where mtgish finds a close lookalike, are candidates.

## Where tags should go (both methods agree)
The two methods point at the same missing rules from opposite directions (Forge parameters vs mtgish nodes):

| Gap (no tag today) | A: Forge line | B: mtgish nodes | Example cards |
|---|---|---|---|
| Spell-cast, phase, attack, block and landfall triggers | `Mode$ SpellCast / Phase / Attacks / AttackerBlocked` | `WhenAPlayerCastsASpell`, `WhenACreatureAttacks` | Zada, Speedball, Merrow Commerce, Port Inspector, Hedron Rover |
| Animate (land or artifact becomes a creature) | `AB$ Animate` | `SetPT`, `SetCreatureType`, `AddCardtype` | Halsin, Avalanche Caller, Mordenkainen's Polymorph |
| Tap-down and lock auras, cards that stop untapping | Enchant aura with tap | `EnchantPermanent`, `TapPermanent`, `DoesntUntapDuringControllersUntap`, `PermanentRuleEffect` | Frozen in Ice, Bind the Monster, Tangle Kelp, Bombur, Phyrexian Ironfoot |
| Regeneration | `A:Regenerate` | `RegeneratePermanent` | Death Ward, Zombie Musher, Gobhobbler Rats |
| Hand or graveyard to library | `ChangeZone` Destination Library, Origin Hand or Graveyard | `PutGraveyardCardOnTopOfLibrary`, `PutCardInHandIntoLibraryNthFromTop` | Lost Hours, False Mourning, Cogwork Archivist |
| Keyword grants by Effect or static (Unblockable, Protection, Fear) | `AB$ Effect` / `Mode$ Continuous` AddKeyword | `CantBeBlocked`, `Protection`, `Fear` | Frostpeak Yeti, Mask of Law and Grace, Shriek of Dread |
| Self-pump activated abilities | `AB$ Pump`, no ValidTgts | `CreatePermanentLayerEffectUntil` on `ThisPermanent` | Lightning Berserker, Dragon Engine, Prakhata Pillar-Bug |
| Static conditions and aura stats | `S:` Continuous with condition | `PermanentLayerEffect` conditions | Gobhobbler Rats, Thrash of Raptors, Lignify |

## Where AILogic$ should go
Rule of thumb from set C: **place an `AILogic$` only where Forge-syntax and mtgish agree.** On the control set that rule was right 17 of 18 times. Where only one method has an answer, treat it as a lead, not a placement. mtgish alone is useful when the nearest card is at least 0.6 similar (24 of 29 right, 83%). Below that it is 9 of 21 (43%).

## Caveats
- One sample of 50 per set; the percentages are not accuracy for the whole pool.
- Tag scores on set C are circular (the existing tags came from Forge parameters).
- mtgish ignores costs and numeric values, so two cards with the same shape but different timing can get the same wrong value.
- The Oracle line was not checked by A; claims that depend on it are marked unverified in its doc.
- T has no ground truth: the proposals are unreviewed.
- Nothing here has been applied. Any change to `ability_tags.py` or card scripts needs an approved dry run.

## Suggested next steps (advice only, not started)
1. A re-scores set C with A/S/T lines preferred over K lines (A's own first fix).
2. Add the eight gap rows to `ability_tags.RULES` one at a time, each tested on set C and a fresh T sample, with an approved dry run.
3. Use "both methods agree" as the filter for candidate `AILogic$` placements, then have the AI lab check the semantics of each in code before any card script is edited.

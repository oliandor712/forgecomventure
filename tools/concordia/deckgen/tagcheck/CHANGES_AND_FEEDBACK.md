# Tag project: your feedback, what changed, agent updates, r1 -> r3 (Claude 2 night shift, 2026-10-22)

## 1. Your feedback and what it changed
| Your note | Change made |
|---|---|
| Approve all new tags | 58 families marked approved in `tags/NEW_TAGS_FOR_APPROVAL.md` |
| Sample tag run: script + Oracle + mtgish + AILogic + CR/keyword reference; samples with note fields | `tag_verify.py` cross-check layer; `STARTER_TAGS_SAMPLE.md` (3 per type, 1 per supertype, note column) |
| Self-sacrifice is not an outlet | `sacrifice_outlet` now only for creature / other sacrifice (20 cards -> 6) |
| Reverse-check tool with a strict blind reader | `tagcheck/reverse_check.py`, agent `tag-blind-reader` (Read+Write only), leak check, selftest |
| Apply next steps; flag opaque tags | static / replacement / modal / look-at-top / saga / amounts / grant tags; opaque tags moved to ignore_tags (r2) |
| Restrict more robust (A/B, A, B, doesn't untap, loses ability) | `restrict_kind:` (+ cant_activate, attack-tax, scope self, durations next_untap / while_control); evasion no longer `restrict` |
| Remake pump_team and artifact_token, unflag | `pump_all` + amount / keywords / who; `token_ability:` for standard tokens |
| Segregate opaque, umbrella, AI logic as AI Tags the reader never sees; add token names and reminder texts; reader gets reminder text | `ai_tags:` line (172 cards); `TOKEN_REMINDER_TEXT.toon`, `KEYWORD_REMINDER_FILL.toon`; per-batch `reminders_NN.json` |
| Check missing reminder texts in databases / the CR | Scryfall API + Forge Oracle lines + CR rule text; every row now has text (CR rows are labelled rule text, not printed reminder) |
| mode count / mode choose redundant | merged: `modal:1_of_3` |
| take_ tags redundant | merged: `take:may_1_creature_power_le_2_to_hand`, `rest_dest:library_bottom_random` |
| piles_ tags redundant | merged: `piles_split:opponent` |
| Is condition_present different from static? | answered: different (gate vs kind of ability); proposal below |

## 2. Reverse check, same 353 cards, same scorer (348 with ability text)
| | r1 | r2 | r3 |
|---|---|---|---|
| what changed | baseline | detail tags, opaque flagged | restrict / team pump / token detail, AI Tags hidden, reminder texts for the reader |
| mean similarity | 0.774 | 0.861 | 0.871 |
| good / partial / gap | 234 / 93 / 21 | 293 / 51 / 4 | 306 / 40 / 2 |
| real card ranked #1 | 219 | 266 | 262 |
| real card in top 5 | 295 | 323 | 325 |
| cards missing a number | 86 | 36 | 28 |
| cards the reader said it recognised | 5 | 1 | 0 |

By type (r1 / r2 / r3): creatures 0.78 / 0.86 / 0.87, instants 0.73 / 0.84 / 0.86, sorceries 0.78 / 0.85 / 0.87, enchantments 0.71 / 0.88 / 0.89, artifacts 0.79 / 0.89 / 0.88, lands 0.90 / 0.92 / 0.91.
Biggest r2 -> r3 gains: Trumpet Blast 0.40 -> 1.00, Syr Alin 0.55 -> 1.00, Goreclaw 0.60 -> 1.00, Overrun 0.61 -> 1.00, Time of Ice 0.77 -> 0.94, Return of the Wildspeaker 0.41 -> 0.72, Pacifism 0.79 -> 1.00. Small losses: Pounce -0.16, Zuran Spellcaster -0.14, Ravenous Rats -0.13, Keldon Raider -0.13, Rogue's Passage -0.13 (reader variation or a tag that now says less; not examined).

**Still weak (r3):** Leafkin Druid 0.29 (conditional mana), Sea Gate Loremaster, Welcoming Vampire (trigger filters), Elite Scaleguard, Mentor of the Meek, Flow of Knowledge, Swords to Plowshares 0.56 and Feed the Swarm 0.53 (`x_is` does not read "its power" / "mana value" yet, so X has no meaning). Most-lost concepts: each / all (33 cards), you control (33), opponent (30), may (29).

**Trust:** one pass per run; the r3 gain over r2 is small (+0.01 mean, rank #1 slightly down) and within reader noise; the r1 -> r2 jump (+0.09) is the real one. Bands unvalidated. Reader isolation rests on the tool list and prompt.

## 3. Agent updates (all in this container's group)
- **forge-ai-lab:** pushed patch 014 + its unticked entry, `AI_LOGIC_TAG_REVIEW.md`, results n014 / n005 / n008 and `ab_recipe.sh`. Nothing applied to any card script or forge-ai. Its own 40-game tests: 014 casts per game -25%, wins noise; 005 v3 switch activations 356 -> 52, wins 5 vs 1 (n.s.); 008 no regression, no benefit. Omen of the Sea anomaly withdrawn.
- **deck-balance-lab:** running 9 x 40-game A/B runs for 014, 005 (+001), 008 under your standing order; 5 done at last report: 014 (120 games) wins 6 vs 10 (n.s.), casts 784 -> 643; 005 (80 games) wins 7 vs 6, activations 742 -> 106. 008 not started. Nothing pushed until all nine finish.
- **deck-builder:** setup only, idle, H55 respected.

## 4. Waiting on you
1. Next AI patch: 004 (Harsh Justice reflect), 007 (attackers curse through a blocker, AI lab's pick) or 009 (don't over-pump)?
2. 44 new tag families are proposed (`NEW_TAGS_FOR_APPROVAL.md`); two behaviour changes (drop umbrella `removal`, list keywords once) are still unapproved.
3. Merge `condition_present` / `_zone` / `_compare` into one readable `condition:` tag (e.g. `condition:you_control_garruk_planeswalker`)? Yes / no.
4. AI Tags list (tempo, ai_logic, burn, removal, selection, fixing, restrict, pump_team, artifact_token): right, or move any back to the reader?
5. Say "push" for the code, tag data, run data and keyword files (documents are already on `campaign-design`). Nothing but documents has reached `campaign-design` from this shift; everything is backed up on `cd/claude2`.

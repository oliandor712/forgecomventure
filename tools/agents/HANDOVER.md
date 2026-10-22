# Shift handover (Claude 1 day shift, Claude 2 night shift)

The outgoing session rewrites this file at the end of its shift (see MAIN_SESSION_BRIEF.md section 8). The incoming session reads it first. Only the session on shift edits it.

Last updated: 2026-10-22, end of Claude 2's first shift
Outgoing: Claude 2 (`session_01Gq6ZyZAehyS8qZDopm3Dym`, branch `cd/claude2`, backed up to origin/cd/claude2)

## Done this shift
- **Tagging, sample tag run:** cross-check layer `tag_verify.py` (Oracle, mtgish, keyword reference/CR, AILogic); mtgish loader reads two-faced cards; AI Tags segregated (`ai_tags:` line; the reader never sees them); new tag families for static / replacement / modal / look-at-top / saga / amounts / grants / `restrict_kind` / `pump_all` / `token_ability` / `x_is` (readable value, linked to its amount tag and the object it measures); redundant pairs merged (`modal:1_of_3`, `take:...`, `piles_split:who`); self-sacrifice no longer an outlet (20 -> 6). Reports and samples regenerated in `deckgen/tags/`.
- **Reverse tag check:** `deckgen/tagcheck/` (`reverse_check.py`, agent `tag-blind-reader`, per-batch reminder files). Runs r1-r4 on the 353 starter cards: mean similarity 0.774 / 0.861 / 0.871 / 0.876; real card ranked #1 219 / 266 / 262 / 266. Findings: `R1_FINDINGS.md`, `R2_FINDINGS.md`, `CHANGES_AND_FEEDBACK.md`, `REVERSE_CHECK_REPORT.md` (latest = r4). Run data in `tagcheck/runs/r1..r4`.
- **Keyword repository:** `ai_lab/TOKEN_REMINDER_TEXT.toon` (CR 111.10 tokens), `ai_lab/KEYWORD_REMINDER_FILL.toon` (gaps filled from Scryfall API, Forge Oracle lines and CR rule text; generators `tagcheck/build_token_reference.py`, `build_reminder_fill.py [--forge|--cr]`).
- **AI lab (Claude 2 clone):** reviewed the tags (`ai_lab/AI_LOGIC_TAG_REVIEW.md`); patch 014 and tests of 014 / 005 (+001) / 008; patch 005 v4 (empty-opponent-field rule) + test-only log patch 015 + deck `opp_burn_40`; `ab_recipe.sh`.
- **Balance lab (Claude 2 clone):** 9 x 40-game A/B runs for 014, 005 (+001), 008 (`ai_lab/results/ab/`).
- `human_logic.toon` rows H59-H64 appended (count line fixed to 63).

## Open items and pending approvals
- **Tag families:** 44 proposed families await the user's tick in `deckgen/tags/NEW_TAGS_FOR_APPROVAL.md` (58 were approved 2026-10-22); two behaviour changes still unapproved (drop umbrella `removal` when a method tag exists; list keywords once).
- **User decisions pending:** (1) merge `condition_present/_zone/_compare` into one readable `condition:` tag? (2) the AI Tags list (tempo, ai_logic, burn, removal, selection, fixing, restrict, pump_team, artifact_token): right? (3) next AI patch to write: 004 (Harsh Justice reflect), 007 (attacker curses through the blocker, AI lab's pick, needs the Shield Dancer unflag) or 009 (don't over-pump).
- **AI patches (AI_CHANGES_APPROVAL.md, all unticked, none applied):** 014 timing only, strength effect unproven (120 games: wins 6 vs 10 ns, casts 784 -> 643). 005 + 001: switch spam fixed (activations 1122 -> 222 in 120 games), strength unproven. 008: no effect seen, parked until a scenario test. 005 v4 (user requirement: ignore the after-blocks gate when the opponent has no creature that could block) is built and smoke-tested (10 games); its volume runs (r005v4sa-c Sai matchup, r005v4ba-c burn matchup, 40 games each) were started and then killed by the user's "pause all": nothing pushed for v4 volume.
- **H55 hold stays** (tag index not declared complete): no tier 1 deck work, no AI lab proposals beyond the user-ordered patch tests.
- **Reverse check, weak spots for the full-cardlist run:** conditional mana (Leafkin Druid), trigger filters (power / type / once per turn), "may" (optional), "each / all", "you control", "opponent" wording, `recursion` and `target_type` tags the readers could not read, Feign Death. `condition_*` merge above.
- Operations: `sync_check.py verify` printed NOT SYNCED at the last push (expected: it compares with Claude 1's end-of-shift manifest). `pool.pkl` is not regenerated (no check needed it).

## Agent states (Claude 2's group; ids in `projects/claude2_agents.md`; never message them from Claude 1)
- forge-ai-lab `session_012GGR4uHxSZZdoF7AUfDwRN`: paused, idle. Has pushed patch 014, 005 v4, 015, results n014/n005/n008, `ab_recipe.sh`, decks.
- deck-balance-lab `session_015WzCaTSu8xpFdrSVLifceE`: paused, idle, no processes or timers. 005 v4 volume runs lost (killed).
- deck-builder `session_01SAbP8j8tKrW3EME5sgBTfV`: idle since setup, H55 respected, nothing pushed.
- Claude 1's agents (`forge-ai-lab session_018TohPY7UPn5mh9b7aJ4at5`, `deck-balance-lab session_01PwU5ft7yoiwonjyndwCVv9`, `deck-builder session_01EiE27ZRU9BUAnaYQYocKuB`) were not contacted.

## Unverified or uncertain
- Reverse-check scores: one reader pass per run (no reader-noise estimate); r3 and r4 differ from r2 by amounts within noise except for named cards; quality bands (0.7 / 0.4) unvalidated; reader isolation rests on the tool list and prompt, transcripts not audited line by line.
- The AI lab's claim that "pause all" came from the user in the balance lab's chat is unverified from here; treated as the user's order.
- The patch test results are the agents' reports (summaries pushed by them); I recomputed the Fisher p-values only.
- `KEYWORD_REMINDER_FILL.toon`: Scryfall-derived rows use a single-parenthetical heuristic; some may be partial; rows labelled `cr_rule_*` are rules text, not printed reminders.
- Scryfall bulk host `data.scryfall.io` is blocked in the sandbox; only the API works.

## Next suggested step
Wait for the user's decisions above. Then: either resume the balance lab for the 005 v4 volume runs (recipes in the AI lab's last message / `ab_recipe.sh`), or start the full-cardlist tagging run once the user says the tag index is complete (lifts H55).

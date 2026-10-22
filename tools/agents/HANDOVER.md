# Shift handover (Claude 1 day shift, Claude 2 night shift)

The outgoing session rewrites this file at the end of its shift (see MAIN_SESSION_BRIEF.md section 8). The incoming session reads it first. Only the session on shift edits it.

Last updated: 2026-10-22, end of Claude 2's second shift (the user said "push, end shift")
Outgoing: Claude 2 (`session_01Gq6ZyZAehyS8qZDopm3Dym`, branch `cd/claude2`, pushed to `campaign-design` on the user's "push")

## Done this shift (Claude 2, second shift)
- **Tag data, deployed:** agent suggestions A+B (optional, unless_cost, each_opponent / each_player, trigger_scope any / damaged_by_self, numeric trigger_filter, limit:once_per_turn, cant_regenerate, steal on auras, tutor fix) in `deckgen/tag_variant.py` (`TAG_VARIANT=off` disables); gap tags (trigger filters you_control / opp_control / token / nontoken / has_counter / nth_spell, conditional mana `mana_conditional` + `mana_amount_if` + `condition:`, ability-word and kicked conditions, `cost_additional`, `extra_land_drop`, `phase_out`, `trigger:life_loss`, valued `mana_restriction`, `cost_reduce_for/_amount/_mana`, `choose_on_enter` + `choice_option`, `scales:<thing>` on every count, landwalk under `evasion`); zone moves share `from_zone:` / `to_zone:`; Feign Death granted-trigger group; Kami static replace; `reanimate` is now an AI umbrella derived from `put_onto_battlefield` + `from_zone:graveyard`; `controller:owner|you`.
- **Record layout:** `typing:` line (what the card is) separate from `tags:` (abilities); `TAG_LEGEND.md` and generated `TAG_REFERENCE.md` (every family with meaning, source, values).
- **Reverse check:** scorer bug fixed (card-name replacement depended on the hash seed; this was most of the "reader variance"); reader noise on identical inputs is SD 0.019 per card; legend and `typing` key in batches; reader rule: never leave a card empty, write X not its definition. Full-sample means: r7 0.914, r8 0.926 (353 cards, 9 readers). Reports: `tagcheck/R6_VARIANT_COMPARE.md`, `tagcheck/R7_FULL_SAMPLE.md`.
- **Agent feedback rounds** (deck-builder, forge-ai-lab, balance lab) merged into `TAG_SUGGESTIONS.md`, `R6_VARIANT_COMPARE.md`, `R7_FULL_SAMPLE.md`.
- **Decisions by the user:** H55 killed ("kill h55"); A and B of the decomposition (legend + zone split) done; H63 stands; raw A/B logs purged (summaries kept; the purge reaches `campaign-design` with this push).
- Investigated and reported (no files): decompiling the Forge AI is unnecessary, the original source is in `forge-ai/` (192 files, 57.6k lines); proposed a read-only map (decision flow, API-to-AI table, combat model, special cases). Not started.

## Open items and pending approvals
- **Asked, not answered:** (1) drop `target_scope:any` (redundant with "no scope tag"; 3 cards carry it, 99 targeting cards have none); (2) `controller:owner` only where the Oracle text states it, `controller:you` always (readers now add "under its owner's control" where the text is silent; Zombify 1.00 -> 0.74); (3) add a redundancy-gate rule for "a value equal to the tag being absent"; (4) drop the bare keyword tags from AI tags (18 tags on 17 cards, all derivable from `grant_kw`; nothing reads them); (5) decomposition: none left; (6) start the Forge AI source map (items 1 and 2 first or all five).
- **TAG_SUGGESTIONS.md** still lists D1 (token-provided function tags: `provided_by` link recommended), D2 (AI Tags feed card power: no), D3 and D4; change list C (`face:` numbers), D (derived tags), F (tooling, gates, version stamp) are not implemented. Balance lab's gate rule for the full run: hard stop only on a whole-sample mean drop > 0.03 with >= 150 cards, a paired drop > 0.05 on changed cards, or an unexpected family-count diff; version stamp wanted (tag_run commit, variant, card count, per-family counts, reader pass id).
- Remaining weak cards (r8): Feign Death and Kami now fixed (r10/r11), Vines of Vastwood 0.52 (kicker bonus), Desecrate Reality 0.61, Saruman 0.63, Ripples of Potential 0.64; `mana_restriction:static_foretelling_or_instant_or_sorcery` is an ugly value to tidy.
- **AI patches** (`docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`): all unticked, none applied. Patch 005 v4 volume runs not rerun.
- **Next full-cardlist tagging run:** H55 is gone, so it may start when the user says so (gates in TAG_SUGGESTIONS S23 and the balance lab's rule above).
- `sync_check.py verify` may print NOT SYNCED after this push (expected until Claude 1's next manifest).

## Agent states (Claude 2's group; ids in `projects/claude2_agents.md`; never message them from Claude 1)
- forge-ai-lab `session_012GGR4uHxSZZdoF7AUfDwRN`: idle (answered the R6 and R7 feedback rounds), nothing pushed this shift.
- deck-balance-lab `session_015WzCaTSu8xpFdrSVLifceE`: idle. It pushed the raw A/B logs on a "USER ORDER" claimed in its own chat; the user then told Claude 2 to purge them. Told to push nothing unless the user says so in that chat.
- deck-builder `session_01SAbP8j8tKrW3EME5sgBTfV`: idle (answered both feedback rounds).
- Blind-reader subagents are one-off and finished. Claude 1's agents (018TohPY..., 01PwU5ft..., 01EiE27Z...) were not touched.

## Unverified or uncertain
- Reverse-check scores: one pass per version, no repeat at the r8 tag version; quality bands (0.7 / 0.4) unvalidated; reader isolation rests on the tool list and prompt. r9 / r10 / r11 are small subsets (20 / 6 / 12 cards, one reader each).
- The agents' feedback on script patterns: deck-builder wrote from memory (no script read); forge-ai-lab's counts are line counts over the whole cardsfolder.
- `S06` conditional mana handles `IsPresent$` and `Count$Compare` over `Count$Valid`; chained compares and generic `CheckSVar$` are not derived.
- Tag layout change (`typing:` line) is only read by `tag_run.py` and `reverse_check.py`; no other tool parses `STARTER_TAGS.toon` (checked by grep).
- The end-of-shift auto-push order for Claude 2 was withdrawn by the user earlier; this push is on the explicit "push, end shift".

## Next suggested step
Wait for the user's answers to the open questions above. Then: either apply the answers and run the full-cardlist tagging run, start the Forge AI source map, or resume the balance lab for the 005 v4 volume runs.

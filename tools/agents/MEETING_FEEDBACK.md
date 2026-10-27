# Meeting feedback on the tag/deck vision (2026-10-24)

Agents: tag-blind-reader, deck-balance-lab, forge-ai-lab, deck builder/commander script (general-purpose, haiku). Three rounds through shared files; the main session moderated and scrutinized. Input: tools/agents/VISION.md. Advice only: no source, deck or enemies.json was changed. Anything here that conflicts with a rule in human_logic.toon loses to the rule.

## Agreed list (all four signed; two wording fixes applied)

1. One shared tag source: the tagger record feeds builder, commander script, power_scorer, AI lab, balance. Record carries per-ability rows and structured values (amounts, costs, zones, targets), keywords, P/T, commander cost and command-zone flag.
2. Generated old-to-new name map is the first deliverable, accepted by running the renderer on both vocabularies, with a fail-on-silent-drop check.
3. Tag-record version stamped on every suite run, game batch, deck build and commander row; results across versions never pooled.
4. A tag change marks affected decks, digests and sims stale; regeneration in one pass with a per-deck diff (tier, power, commander support) before any live change. Nothing live (enemies.json, live decks) changes without the user's word.
5. One difficulty axis and one tier-to-power table with a dated baseline, read by build.py, power_scorer.py, balance lab and docs; reconcile the three current number sets first.
6. Tier step = measured per-stage win-rate change against H29 targets. Sample floor: 25 games per AI deck and 40 per starter (H28 targets); no claim about a 70-30 gap below about 40 games per arm. Balance feeds the builder only through bounded, logged adjustments.
7. Commander harmony: score term plus separate reported score, tested by supported-vs-unsupported win-rate gap.
8. Per-row fields on every game and suite record: deck id, archetype, colour, timing, command-zone moves and commander cast count. These are record fields, not tags.
9. Check-status per tag naming who set it (reader readable / Oracle verified / unverified); missing fields go to TAG_GAPS. Gap or unverified tags add no ability bonus, flag the deck, and flagged decks are excluded from tier pass rates; AI rules are not approved on gap tags.
10. Reader stays out of the balance path (feeds render_rules, compose_rules, TAG_GAPS only). Misleading tags found by builder, AI lab or balance return as reader test cases; rules mined from one run are confirmed on a second batch. A countable reader metric (rules accepted, gap rows closed, share rendered with no reader) judges runs.
11. human_logic.toon beats any metric, AI-lab or balance finding; conflicts are held for the user.

## Moderator scrutiny of round 3

- Balance's objection to item 6 checked against H28 and is correct (H28: 25 per AI deck, 40 per starter, about 40 per deck for a 70-30 read). The draft's "40 games per arm (H28)" was a merge error. Fixed above. The ai lab signed "as drafted" and the builder only flagged it; neither caught it, and the ai lab's own round 2 had used the same wording.
- Reader's item 8 wording fix applied (cost is card data in item 1, cast count is record data in item 8).
- Open, not settled by the agents:
  1. Three agents asked in round 2 that the vision name who owns the Oracle truth check (the reader tests rendering, not truth). The draft dropped it. Needs an owner.
  2. Item 7 (supported vs unsupported commander test) has no sample floor. H28 gives about 25 matched sets per bonus for a 25-point effect; nobody applied it.
  3. The builder withdrew its round 1 claim that the builder does not read TAG_GAPS.toon as unverified, and it was never checked.
  4. The balance lab's tier power bands (for example T2 19-31) and the builder's three-set mismatch claim were quoted by the agents, not checked by the moderator against power_scorer.py and build.py.
  5. Item 2 (generated name map with no-silent-drop) is the builder's hard requirement; no agent estimated its size or the order of work.

## Full conversation
Moved verbatim to `tools/agents/archive/MEETING_FEEDBACK_full_conversation_2026-10-24.md` (rounds 1-3 per agent).

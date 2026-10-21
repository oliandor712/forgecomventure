# Unflagged cards

Cards whose `AI:RemoveDeck:All` flag was removed with the user's approval. `pool.py` skips flagged cards, so these now enter the deck pool. Checked 2026-10-21 by exact name match on the tier and starter decks.

| Card | Patch | Applied | Decks using it now | How the AI plays it (ai_lab/DECISION_LOGIC.md) |
|---|---|---|---|---|
| Thwart the Enemy | 002-fog-unflag.patch | 2026-10-21 | none | Fog effect. The AI casts it only when `ComputerUtil.hasAFogEffect` is true (AiBlockController, block phase), in the opponent's declare-blockers step against unblocked attackers. Measured with the flag: 0 casts; without it: 19 casts (2 copies, 30-card decks), 8 at normal density. |
| Vine Snare | 002-fog-unflag.patch | 2026-10-21 | none | Same fog path as Thwart the Enemy. Cast median turn 14 (range 8-27) in the full log pass. |
| Endure | 003-white-fog-unflag.patch | 2026-10-21 | none | White fog. Measured: 0 casts with the flag; 15 casts (2 copies) and 2 at normal density without it. Median cast turn 25 (21-29) in the full log pass. Patch 004 is needed for Harsh Justice, not for these three. |

Backup of the card scripts before the change: `tools/concordia/backups/2026-10-21_cards_pre_002_003`.

Approval: `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`, entries 002 and 003 (ticked by the user in chat 2026-10-21).

Note: a broad text search also matches "Boseiju, Who Endures" in 26 decks. That is a different card and is not an unflagged card.

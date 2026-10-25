# Dry regeneration report (2026-10-25, step 7)

Dry build of `decks.json` on the record (tag stamp af7ccddc4c); live decks and `enemies.json` untouched.

- 195 of 200 decks built. 5 commander entries no longer exist in the pool after H73 (Alchemy-named cards out): T2_U_Ertai, T2_B_Sengir, T4_G_Kaysa, T5_U_Hakim, T2_R_Zirilan. Decision needed: swap commanders or allow those cards.
- Power in band 177/195; creature window 161/195; both 146/195. One FAIL, 183 human-logic WARNs on 162 decks (mostly H09 staple printings, H11 creature count, H16).
- 177 decks use at least one card whose tags are held back (check status); the card list prints per deck in the build log.
- Tier 2-5 targets (tier_table.json) are not yet recalibrated after the popularity change; many T4/T5 decks sit below the creature window.
- No old full-run baseline exists, so this is a state report, not a before/after diff. Old sims count as stale (tag stamp changed).
- Step 8 (row fields: tag stamp, deck id, command-zone moves) is left to the balance lab: changing CSV/TSV headers would break existing logs.

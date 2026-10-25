# Dry regeneration report (2026-10-25, step 7; rerun after the creature and tier 1 power changes)

Dry build of `decks.json` on the record (tag stamp af7ccddc4c); live decks and `enemies.json` untouched. Rules in force: creatures at least 15 with a builder soft cap of 35 (H11), tier 1 power 16-21 (H08, target 18.5).

- 195 of 200 decks built. 5 commander entries are not in the pool: they have only printings older than Sixth Edition (`PRE6_CUTOFF` 1999-04-21 in `pool.py`), not H73: T2_U_Ertai, T2_B_Sengir, T4_G_Kaysa, T5_U_Hakim, T2_R_Zirilan. Decision needed: swap commanders or add a cutoff exception list.
- Creatures: none under 15, none over 35 (max 35); average per tier T1 34.2, T2 32.8, T3 33.4, T4 32.1, T5 30.5.
- Power in band: T1 40/40 (16-21, average 18.0), T2 37/37, T3 38/40, T4 33/39, T5 34/39 (178/195). The T3 to T5 misses are decks below their band; `tier_table.json` targets are not yet recalibrated after the popularity change.
- One FAIL: T2_R_Eron, commander rarity S (allowed C/R/U). 24 H14-H17 WARNs (H17 commander support 12, H14 8, H15 4); 155 H09 staple-printing WARNs and 10 H10.
- 190 decks use at least one card whose tags are held back (check status); the card list prints per deck in the build log.
- The "reach window" figure of earlier runs is gone: creature windows no longer exist, and the dry summary's archetype columns read `-/-` because `decks.json` carries no archetype for these rows.
- No old full-run baseline exists, so this is a state report, not a before/after diff. Old sims count as stale (tag stamp changed).
- Step 8 (row fields: tag stamp, deck id, command-zone moves) is left to the balance lab: changing CSV/TSV headers would break existing logs.

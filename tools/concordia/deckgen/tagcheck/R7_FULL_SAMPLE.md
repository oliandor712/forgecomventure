# R7: full-sample reverse check with the agent suggestions deployed (2026-10-22)

All 353 starter cards, 9 fresh blind readers (40 per batch), tags as deployed: agent suggestions S01-S09 and S15 with the agents' rule fixes (`tag_variant.py`), typing line separated from ability tags, zone split, tag legend, `cost_reduce_*` and `choose_on_enter` fixes, scorer fixed (name replacement no longer hash-seed dependent).

| | cards with text | mean | good / partial / gap | top-1 / top-5 retrieval |
|---|---|---|---|---|
| r7 full | 348 | **0.914** | 318 / 28 / 2 | 306 / 328 |
| r7, the 174 cards also in r6c/r6d | 174 | 0.918 | | (r6c 0.901, r6d 0.900) |
| r7, other 174 cards | 174 | 0.909 | | |

Pure reader noise on identical inputs was SD 0.019 per card (r6c vs r6d), so the +0.017 on the shared half is above noise but the tag changes between r6 and r7 are several at once (suggestions + typing line), so it is not attributed to one change.

Checked cards: Control Magic 1.00 (`steal` on the aura), Sengir Vampire 1.00 (`trigger_scope:damaged_by_self`), Incinerate 0.87, no empty answers.

Lowest 15 (all below 0.6) and what the reader was missing:
- Leafkin Druid 0.35 (conditional mana: "instead" with a creature-count condition; the S06 condition on mana abilities is not deployed for this form)
- Sea Gate Loremaster 0.38, Saruman the White 0.50, Flow of Knowledge 0.59 (`each_all`: a "number of X you control" count has no readable form)
- Vines of Vastwood 0.44 (kicker effect), Elite Scaleguard 0.44 (trigger filters and counters), Mindcrank 0.48 (life loss -> mill link), Explore 0.49 (land drop + draw), Feign Death 0.50, Ripples of Potential 0.51 (proliferate choice), Temple of the False God 0.51 (land-count condition), Colossal Majesty 0.54 (power condition), Desecrate Reality 0.56 (delirium condition), Kami of Whispered Hopes 0.58, Silvergill Adept 0.59 (alternate additional cost).
- Yedora, Grave Gardener 0.59: reader lost the "nontoken creature you control" filter on "another creature dies".

Most remaining gaps are conditions ("if you control N", "number of X you control") and filters on triggers. Next candidates: `condition:` on mana abilities (S06), a readable `count_<thing>` for "number of X you control", trigger filters (`trigger_filter` with controller and token), kicker/alternate-cost effects.

Unverified: one run, scorer is tf-idf plus concept F1 (bands unvalidated).

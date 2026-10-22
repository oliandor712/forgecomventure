# Tag decomposition and symbol shorthand: investigation

Request: split compound tags (`return:graveyard_to_hand`) into zone + syntax parts, shorten syntax words (`to`, `may`) to symbols, pin reference text per tag. Investigation only; nothing changed.

## Measured on STARTER_TAGS.toon (353 cards)
- 3344 tag uses, 543 distinct tags, 421 distinct words, 51,572 chars.
- Compound-value tags (value with 2+ joined parts, e.g. `_to_`, `_of_`, `up_to`) are rare: about 25 distinct tags, about 40 uses. Families: return(3), take(4), modal(3), replace(2), rest_dest(2), condition(3), token_ability(3), x_is (13 of 21), restrict_kind, cost_exile_from.
- Zone words are already shared across families (`graveyard` x59, `battlefield` x37, `exile` x25, `library` x16, `hand` x18), so zone vocabulary is already reusable at word level.
- Symbol shorthand prototype (to>, may?, up_to<=, all*, graveyard gy, battlefield bf, ...): 51,572 -> 50,234 chars, **2.6% smaller**. Not worth it.

## Findings
1. Size/processing gain is small. The list is dominated by plain family:value tags, not compounds. Decomposing the 25 compounds saves nothing; each part becomes a separate tag (more tokens: `return:graveyard_to_hand` 1 tag vs `return from:graveyard to:hand` 3).
2. Where decomposition does help is **querying, not size**: a deck builder asking "anything that moves cards graveyard -> X" or "all graveyard-to-hand" needs a prefix scan today (`return:graveyard_*`). With separate `from:`/`to:` zone tags in the same group it is one set match. Same for `take:*_to_hand` vs `tutor`.
3. Symbols hurt the reverse check. Blind readers (LLMs) read words better than glyphs; `>` and `?` are ambiguous and tokenise badly. They would need a legend per batch, and every misread costs score. Words stay.
4. Pinned reference text is the real readability win and cheap: the per-batch `reminders_NN.json` already feeds readers keyword/token text. Adding one line per family *present in the batch* (e.g. `return = card moves from a zone back to another zone`; values listed with meaning) costs a few hundred chars per batch and fixes compound parsing without changing the tags. Also usable by deck builder/balance agents through DOC in tag_extra/tag_verify, which already holds meaning/source per family.
5. Risk of decomposing: redundancy gate, cross-check, links and the reverse-check scorer all key on family:value strings; splitting needs changes in all four plus every agent doc. Medium work for a small gain.

## Recommendation
- No symbols.
- Do not decompose generally. Optional narrow step: for the zone-move families only (return, take, rest_dest, put_onto_battlefield, cost_exile_from) emit `from:<zone>` and `to:<zone>` as two tags in the same group instead of one compound. About 20 tags change.
- Do pin reference text: add per-family legend lines to the batch reminders file and the STARTER_TAGS header. Zero tag changes. Can be tested with a half-sample reverse check against r5 (run needs your word).

Decision for you: (a) legend only, (b) legend + zone-move split, (c) leave as is.

# Card script to TOON converter: answers sheet

Fill in the **Answer** line under each question. Tick one option with `[x]`, or write your own under "Other". Add anything else under **Notes**. The brief this sheet goes with is in the chat (sections 1-5). Nothing has been built yet.

---

## Q1. Scope

Which cards should the converter cover?

- [ ] A. All of `forge-gui/res/cardsfolder` (total not yet counted)
- [ ] B. Tier-1 eligible pool (12,853 cards)
- [ ] C. Concordia decks only
- [ ] D. Other: ____________

**Answer:**

**Notes:**

---

## Q2. Who reads the output

- [ ] A. Agents only (machine-first; oracle text optional)
- [ ] B. Agents and humans (include verbatim oracle text and readable names)
- [ ] C. Other: ____________

**Answer:**

**Notes:**

---

## Q3. Fidelity

- [ ] A. Lossless: every script key kept, so the Forge script can be rebuilt from the TOON (larger files)
- [ ] B. Semantic: only the fields the tags and AI mapping need (smaller files)
- [ ] C. Lossless for abilities, semantic for everything else
- [ ] D. Other: ____________

**Answer:**

**Notes:**

---

## Q4. Tag vocabulary and ownership

Should the converter emit tags, or only facts (with tags derived by a separate rules file)?

- [ ] A. Emit facts only; tags come from a separate rules file
- [ ] B. Emit facts and tags in the same pass
- [ ] C. Other: ____________

Who owns the canonical tag list?

- [ ] 1. Keep it in `deckgen/ability_tags.py` (`RULES` and `POLICY`)
- [ ] 2. A new vocabulary file under the converter's folder
- [ ] 3. Other: ____________

**Answer (emit):**

**Answer (owner):**

**Notes:**

---

## Q5. Priority consumer

Which consumer should the first schema cut serve?

- [ ] A. Deck-builder tags (H31-H49: potential P/T, ability-led tags, land types)
- [ ] B. AI logic mapping (`AILogic$`, `AIPreference`, `AI:RemoveDeck`)
- [ ] C. Both, equally
- [ ] D. Other: ____________

**Answer:**

**Notes:**

---

## Q6. Language and reuse

- [ ] A. Python, reusing `ability_tags.parse()` where it fits
- [ ] B. Python, new parser (no reuse)
- [ ] C. Other: ____________

**Answer:**

**Notes:**

---

## Q7. Acceptance test (what "done" means)

- [ ] A. The converter reproduces the current `ABILITY_TAGS.toon` tags for all 12,853 cards
- [ ] B. A sample of cards round-trips back to equivalent Forge script text
- [ ] C. Both A and B
- [ ] D. Other: ____________

**Answer:**

**Notes:**

---

## Q8. Location, owner and commits

Where should the code live?

- [ ] A. `tools/concordia/cardtoon/` (new folder)
- [ ] B. Inside `tools/concordia/deckgen/`
- [ ] C. Other: ____________

Output folder for the generated TOON?

- [ ] 1. `tools/concordia/cardtoon/out/`
- [ ] 2. `deckgen/cards/`
- [ ] 3. Other: ____________

Who owns it?

- [ ] I. Main session
- [ ] II. A new agent (name: ____________)
- [ ] III. Other: ____________

**Answer (location):**

**Answer (output):**

**Answer (owner):**

**Notes:**

---

## Q9. Runtime and size

Maximum time for a full run (minutes):

**Answer:**

Is a generated output of a few tens of MB acceptable?

- [ ] Yes
- [ ] No, max size: ______ MB

**Notes:**

---

## Q10. Phasing

Approve these phases?

1. Brief and schema
2. Converter on a 50-card sample
3. Full run and validation
4. First consumer wired to the tags

- [ ] A. Yes, as listed
- [ ] B. Yes, but change: ____________
- [ ] C. No, use a different split

**Answer:**

**Notes:**

---

## Anything else

**Notes:**

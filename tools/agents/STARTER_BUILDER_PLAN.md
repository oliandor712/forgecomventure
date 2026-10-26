# Starter builder: improvement plan (2026-10-25)

Tool: `tools/concordia/deckgen/starter_build.py`. State after this session: five Normal decks (Adeline W, Hermes U, Rev B, Anax R, Ruxa G) are live in `decks/starter`, glance-reviewed once and rebuilt without rejects, NOT re-reviewed. Alt commanders are off (`zone_flags.ALT_ENABLED = False`).

## Measured cost of the review (this session)
One deck wave = 3 tag readers (16-26k tokens each) + 1 oracle reader (37-43k) = about 120-130k subagent tokens. Five decks, first pass = about 650k; the W redo and the U redraft added more. Readers also wasted tokens reading stale `out/` and `oout/` files (the tool cannot delete them; Windows blocked `Remove-Item`). Every rebuild changes only 1-3 cards but a re-review would read all 62.

## A. Leaner token use (do first, biggest saving)
**Status 2026-10-26: A1, A2, A3, A4 and A5 built** (`glance.py` `--cache`, `starter_build.py review-export`). Cache `staging_starters/verdicts.json` keyed by card name + tag-view hash + Oracle-text hash; fewer than 10 fresh cards = one tag reader, one batch; each review gets a fresh run dir (id in `<deck>.run`); prompts saved to `PROMPTS.txt` in the run dir; the cost estimate prints at export. Tested on 4-5 cards with faked reader output (hit, miss, all-cached); no real wave run yet. Caveat: a cached card carries the reader verdicts of the wave that stored it (1-3 tag readers) and the Oracle form was judged under that deck's context.

1. **Verdict cache.** Store each reader verdict keyed by (card name, tag hash) for the oracle side and (tag hash) for the tag side in `staging_starters/verdicts.json`. `review-export` writes only cards with no cached verdict. Staples recur across decks (Sol Ring, Swords...), and a rebuild changes 1-3 cards, so a wave falls from 62 cards to a handful: est. 85-95% fewer reader tokens on re-reviews.
2. **Delta waves.** If fewer than 10 cards are uncached, one tag reader + one oracle reader in a single batch (no 3-way split; fixed cost per batch is about 5k).
3. **Fresh run dirs.** `review-export` writes to `S_<deck>_<timestamp>/` so no stale `out/` exists; readers then never need to read the target file first (that read broke their "one file only" rule in every run).
4. **One prompt file.** The tool writes the reader prompts to `run/PROMPTS.txt`; the main session sends a short "follow prompt N" instead of retyping ~350 words x 4 per deck.
5. **Cost gate.** Print the expected token cost before a wave, and ask the usage tool first (SESSION rule: check the rate limit before readers).

## B. Builder logic
1. **One command** `build`: draft -> export -> (wait for readers) -> compare -> redraft with the rejects, looped until no rejects or 3 rounds. Today every ban list is retyped by hand.
2. **Persist bans and strategy** in `.picks.json` and add `draft --from-picks X` so a redraft needs no flags.
3. **Global reject list** (`rejects_global.json`): the same cards came back in several decks: Herald's Horn (W, G), Mindcrank (U, G), Leonin Bladetrap (U, G), Golden Egg (W, B), Mask of Memory (R, G). Feed it as a penalty into every draft.
4. **Why these get picked:** utility-role slots and staple/precon bonuses admit off-plan artifacts (equipment, card-draw rocks) with fit 0. Require fit > 0 or a stated role for filler picks; cap off-plan artifacts at 3.
5. **Review bug:** `review-compare` flags the commander as a reject (Rev). Exempt it.
6. **Power under target:** W 25.3, U 25.2, B 25.4 (target 27, H19). Add a power-fill pass: swap the lowest-fit, lowest-power cards for higher-power on-plan cards within role caps.
7. **Commander ranking:** `support_n` counts cards passing any single test (inflated). Count cards passing the commander's tests AND an archetype tag; keep the lessened support weight (user 2026-10-25).
8. **All-tags audit:** strategy fit and niche penalty use `ftags`; role caps and mana count use coarse `p['tags']`. Decide whether role caps should use `ftags` too; test on W/U.
9. **Exit codes:** `review-export` exits 255 although it works; fix so the shell does not show a failure.
10. **Windows encoding:** `hall_roster.py` opens files without `encoding='utf-8'`; needed `PYTHONUTF8=1`. Fix in the script.
11. **Pair and sideboard step:** Alt commander per colour, Normal/Alt differ by 5-8 cards (H20), each holds the other's swap cards (H22). Alt stays off until this exists.
12. **Final check command** `check-all`: 100 cards, creatures >= 15, power vs 27, commander legal, colour identity, all ten decks, non-zero exit on failure.

## C. Tag and rule gaps found while generating decks
- **Skyscanner**: tags say burn/control/tribal, Oracle says flying draw-on-ETB (blink, card draw). Tag bug: find the tagger line that produced it. Candidate for `tags/GLANCE_FIXES.toon`.
- **B deck**: 16 tag-vs-Oracle archetype disagreements (U 0, W 1, R 4, G 0) were not read by hand. Read them; they may show a systematic tag gap.
- **Equipment/voltron**: tags and Oracle agree, but the plans (tokens, blink) do not want equipment. The fit score does not penalise it, so a strategy "anti-fit" list is missing from `strategies.json`.
- **G (Ruxa)**: only 44/61 support the commander (others 51-53). The blink+graveyard pairing may fit poorly; check other strategy pairs.
- **Rule H19** (power ~27) is unmet for three decks; **H20/H22** have no code yet. State in the rules whether a power miss under 2 is acceptable for starters.
- **Process gap:** "build version" in a user request is ambiguous; it meant live `decks/starter` on branch `campaign-design`. Record it so it is not re-asked.
- **Shell gotcha:** a `cd` in the PowerShell tool persists and silently changes the working directory; use absolute paths.

## D. Verification before the next live change
1. Re-review the five rebuilt lists (delta waves once A1-A3 exist; full waves now cost ~650k).
2. In-game test of all five colours: Seal Angel dialog with Alt off, hall unlock of the starter commander, deck loads, 100 cards.
3. Playtest sim (sim/setup.sh classpath) for win-rate against tier 1 once the user approves a sim run.

## Suggested order
A3, A1, B5, B2, B1 (cuts cost and removes the hand work) -> B4, B3, B6 -> C reads -> B11 (Alt pair) -> D.
Each step moves the glance or deck goal: A cuts review cost 85%+; B4/B3/B6 raise deck quality; C fixes tags the readers disagreed on.

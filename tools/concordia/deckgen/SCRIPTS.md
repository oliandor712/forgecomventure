# deckgen and tagcheck: what each Python script does

Read this before opening a script. Each entry is at most 4 sentences, taken from the script's own header. Paths are relative to `tools/concordia/deckgen/`. Update the entry when a script's job changes.

## Deck generator (run in order: mine, pool, build)

- **mine.py** - Step 1. Rates every Commander deck shipped with Forge against the tiers and saves `mined.json`. That file feeds card popularity in `pool.py`.
- **pool.py** - Step 2. Builds `pool.pkl`, the list of every Commander-legal, AI-playable card with colour identity, tags, rarity options, power and popularity. Alchemy cards, old (pre-Sixth) printings only, banned and restricted cards are removed here.
- **build.py** - Step 3. Builds the tier decks listed in `decks.json` into `decks/tier1..3` and rates each with `deck_tier.py`. Commander themes, role counts and the human-logic rules (H17 etc.) are applied here.
- **gen_mono.py** - Adds mono-colour tier decks to `decks.json` and builds them, to fill the difficulty curve's mono-colour roles (wild creatures, pass keepers, Wardens). `--per N` sets new commanders per tier and colour; `--dry` only plans.
- **variants.py** - Gives each tier deck a sibling led by an alternate, budget-leaning commander of the same colour identity, with 5-8 cards changed. Candidates are scored on fit with the deck's creatures and the tier's commander rules.
- **t1_plan.py** - Plans the fresh tier 1 rebuild: a pool of 100 commanders (20 per colour), 80 chosen, each with an archetype and subarchetype, written to `t1_fresh.json` for `build.py`. Commander rules for tier 1 are encoded here.
- **starter_tune.py** - Tunes the five player starter decks toward a deck power target with few swaps. A swap keeps role, card type, colour and a mana value within 1.
- **hall_roster.py** - Writes the Commander Hall roster (`world/commanders.json`) for the two-commander starters. No roster entry is unlocked at the start; the Seal Angel flags unlock the two starter commanders.
- **categorize.py** - Writes `CATEGORIES.toon`: one row per deck (tiers 1-5 and starters) with colours, archetype and deck power. Read-only on decks.
- **budget_lands.py** - Lists near-staple nonbasic lands and cheap mana rocks from budget decks, for the tier 1-2 builder. "Budget" is judged without prices, from precons and small GitHub decklists.
- **staples.py** - Defines staples: cards nearly every Commander deck plays that do not win games alone (Sol Ring, Arcane Signet). They are kept apart from Game Changers (Forge's `gamechangers.txt`).
- **commander_support.py** - Reads a commander's text into a support profile (tribe, trigger, resource items) and counts the deck cards that support it. Replaces the generic keyword check behind `build.py` H17.
- **scryfall_bulk.py** - Refreshes the Scryfall bulk card file when a newer one exists, or looks up a few cards through the API (`--lookup`). Other tools read Oracle text, rarity and colour identity from it.
- **spellbinder_signals.py** - Turns the Spellbinder decklists cached in `deckgen/spellbinder/` into per-card usage signals (`signals.json`). The deck tools use them in the card power score.

## Tagger (card script to tags)

- **ability_tags.py** - Ability-led tags: parses a card script into abilities (A: lines, SVar sub-abilities, triggers, statics, keywords), normalises each to a signature and tags what it does. Tags follow what an ability does, never a per-card list.
- **tag_run.py** - The tagging run (design in `TAG_LINKS.md`, rules H50-H55). Builds one record per card from the script alone (Oracle is only a gap filler), writes `tags/STARTER_TAGS.*`, and calls `tag_guard.apply` before writing.
- **tag_extra.py** - New tag families that fill gaps seen in the references, each proposed in `NEW_TAGS_FOR_APPROVAL.md` until the user approves it. `extra(face_lines, svars, types, text)` returns flat tags and links.
- **tag_variant.py** - Post-pass applying agent suggestions S01-S09 and S15 to a record. Set `TAG_VARIANT=off` to get tags without it for comparisons.
- **tag_verify.py** - Cross-check layer: fills gaps from the Oracle line, keywords and other references that the script tags lack. Its additions land in group `x`.
- **tag_twins.py** - Indexes every non-keyword Oracle line of the tagged starters with its tag group, and finds the closest already-tagged lines (with a % similarity) for an untagged line. A twin is a starting point for the tagger, never copied blindly.
- **derived_tags.py** - Computes `face:` (mana value, power, toughness, loyalty, colours, rarity) and derived tags from base tags. The rules live here only.

## tagcheck/ (check the tags, render them back to text)

- **tagcheck/mtg2llm.py** - MTG2LLM: renders tags to card text with no reader and no Oracle at render time, then scores it. `mine` builds `render_rules.json` from archived reader runs; the renderer uses exact rules, then composed rules, then near-match for colour or name only, then `{missing}` (fail closed). `scan` tags and renders the whole pool and writes `tags/POOL_GAPS.toon` (per card: unrendered units and `gap_words`, the Oracle words the render lacks, so reader runs can target the biggest gaps); planeswalkers are set aside from scan and `unseen`.
- **tagcheck/rule_lint.py** - Reader-free lint of the mined rule tables: a rule whose canon lacks the cue for one of its tags, or says draw/mill with no matching tag, is quarantined. The reverse check (`REVERSE`) is untested and its regexes are broken (see review).
- **tagcheck/tag_guard.py** - Keeps a worse tag run from overriding a better one. Scores each section of a new record against the best stored one in `tags/STARTER_TAGS.best.json` with the reader-free score, and keeps the better section; ties keep the stored record. Each run is logged to `tools/agents/logs/guard-runs.toon`.
- **tagcheck/rule_guard.py** - Keeps a worse `mtg2llm.py mine` run from overriding better rule tables. New patterns are added; a changed canon is taken only when the starter cards using it score higher; the compose table is replaced only when the mean starter score is higher. `mine --force` skips it.
- **tagcheck/sync.py** - Two-way link between the tagger and the tag check. Renders every tagged starter unit and writes `tags/TAG_GAPS.toon`: `open_slot` rows are tag gaps (tagger side), `no_rule` rows are rule gaps (mtg2llm side). `tag_run.py` prints the last summary at start and refreshes the file at the end; `mtg2llm.py mine` refreshes it too.
- **tagcheck/tag_audit.py** - Reader-free tag audit: checks that features the script and Oracle carry have a matching tag family. A miss is a tag gap, which the renderer cannot fix.
- **tagcheck/reverse_check.py** - The reverse check: a blind reader sees only the tags and writes the ability text, which is scored against the real text. Also holds the shared score (0.4 cosine, 0.4 concept F1, 0.2 number F1). `export --gaps N` takes the N biggest-gap cards from `POOL_GAPS.toon` (`mtg2llm.gap_targets`, skipping cards of earlier runs; runs of one round, g4a/g4b/g4c, share one list). `compare` then runs the standard post-run step: a memory row, mining of missing Oracle words into `tags/READER_GAP_WORDS.toon`, `mtg2llm.py mine` and `scan` (`--no-mine` only writes the memory row).
- **tagcheck/run_memory.py** - `save(script, what, result)` appends one row per run of any tag-related script (tag_guard, rule_guard, sync, mtg2llm scan/mine, tag_run, tag_audit) to the user memory file `tag-script-runs.toon`.
- **tagcheck/reader_refs.py** - Builds `~/tagcheck_runs/_refs/`, the sanitized tag reference folder blind readers may read (family meanings, legend, keyword and token reminder text; example columns, card names and counts removed), then leak-scans it for pool card names. `python3 reader_refs.py` rebuilds and prints the scan.
- **tagcheck/consistency.py** - Measures how much k independent readers agree on identical tag inputs (exact agreement, token F1, signature agreement, score SD, style conformance).
- **tagcheck/placeholder_triage.py** - Lists every unfilled placeholder (`{cost}`, `{effect}`, ...) in finished reader runs, grouped by placeholder and class, next to the real Oracle text.
- **tagcheck/run_log.py** - Writes machine-readable records of each reader run under `~/tagcheck_runs/<run>/` (manifest with arm, grammar version, model, tag stamp, hashes).
- **tagcheck/oracle_style_stats.py** - Counts how Oracle text is really written over the card pool, so the grammar copies printed style; also draws the random hold-out sample (seed 20261022).
- **tagcheck/build_reminder_fill.py** - Fills reminder texts missing from `KEYWORD_REMINDER_TEXT.toon` from the Scryfall API (polite rate limit, one search per keyword) into `KEYWORD_REMINDER_FILL.toon`.
- **tagcheck/build_token_reference.py** - Builds `ai_lab/TOKEN_REMINDER_TEXT.toon`: predefined token names and definitions from the Comprehensive Rules (111.10) plus the Oracle reminder wording. The blind reader may read it per batch.
- **tagcheck/learning_merge.py** - Merges the tier 1 blind-test data from the other session's handoff package (4000 rows) into one deduplicated set and calibrates the scorer against that session's grader verdicts.
- **tagcheck/learning_coverage.py** - For cards in the merged blind-test data with graded gaps, checks whether the current tagger emits a tag family that can carry that fact. Family presence is a proxy for coverage, not proof of accuracy.

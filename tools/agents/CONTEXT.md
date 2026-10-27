# Shared context for the Concordia main session and subagents

The main session reads this with `MAIN_SESSION_BRIEF.md`; a subagent reads it, then its brief in `.claude/agents/<name>.md`. Where this file and a brief disagree, this file wins.

## Single session
There is one main session. Branch: `campaign-design`. Subagents are described under "Subagents".

## The project
- Concordia is a Pokémon-like Commander campaign plane for Forge Adventure, in the fork `oliandor712/forgecomventure`.
  All work goes to branch `campaign-design`. No PRs.
- The plane's data lives in `forge-gui/res/adventure/Concordia/`: decks in `decks/tier1..5`, `starter`, `tutorial`;
  `world/enemies.json`; `maps/`; `config.json`.
- The design docs are in `docs/Adventure/Campaign/`: `OVERWORLD.md` (zones, flags, §5.1 the difficulty curve),
  `ENCOUNTER_TIERS.md`, `DECK_REVIEW_SPELLBINDER.md`, `AI_RESEARCH.md`, `AI_FLAGGED_CARDS.md`, `AI_TAGS_REFERENCE.md`.
- The user tests on Windows. The user decides what goes into the game; agents propose.

## Standing rules (main session and subagents)
1. **Equal life on both sides in every simulation, no exceptions.** Life bonuses are eliminated as an option (user,
   2026-10-20); don't test them.
2. **Don't change `forge-core`, `forge-game` or `forge-ai`** on the branch: the user hasn't approved AI-module changes.
   Code ideas go in patch files in your own folder.
3. **A subagent writes only in its role's folders** (table below), plus its listed docs. Never write build output, classpaths, `forge-gui/data/`,
   or a modified `forge-gui-mobile/pom.xml`.
4. **Pushing:** subagents never commit or push; the main session does. Pushes follow `MAIN_SESSION_BRIEF.md` (only on the user's "push"; `git pull --no-rebase origin campaign-design` first; never force).
5. **Low speed, low usage.** Stay inside the time box given, keep replies short, and never paste large files or logs.
6. **Stop on request.** When the main session or the user says stop, a subagent ends at a safe point and reports what is done.
7. **Test updates are pre-approved (user, 2026-10-20).** You may change your test tooling without asking: sims,
   logging, batch runners, test decks, report scripts, and patched scratch copies of forge-ai or card scripts used
   only for testing. Before replacing a file that is already committed, copy the old version to
   `tools/concordia/backups/<date>_<what>/`, or name the old commit in your log. Changes to the game itself still go
   to the user: anything applied to forge-core, forge-game or forge-ai, card scripts, Concordia decks, enemies, maps
   or config.
8. **Proposed AI changes go on the checklist** `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`. Put
   `CHECKLIST: <patch> - <one line> - <status>` in its result when it saves, tests or revises a patch. The main
   session updates the list, and the user ticks a box to approve.
9. **Processes:** never `pkill -f` a pattern that can match your own shell. Kill java by pid
   (`pgrep -a java | grep Sim`). Never leave a sim or build running when you stop.

## Human logic and TOON
- `tools/agents/human_logic.toon` holds only the user's own rules for deck building, deck balance and Forge AI improvement (29 rows, pruned 2026-10-21). Read it before you build, judge or test decks or propose AI changes; a rule beats a metric. The main session adds a row only for that kind of input; town, map, quest and UI rules go in the design docs.
- **TOON** (https://github.com/toon-format/toon) is the format for data files only Claude reads: a list of same-shaped records or a map of same-shaped objects is written as `name[N]{a,b}:` plus one row each (`name[N|]{a|b}:` when cells hold commas), saving 25-55% against JSON. Keep CSV/TSV for flat tables (smaller), JSON where code reads the file, and markdown for anything the user reads. Check a file with `npx @toon-format/cli file.toon`.

## Subagents
No standing background agents and no schedules. The main session spawns a subagent only when the user asks.
- **Parameters (strict):** model and effort per brief frontmatter, never overridden: `tag-blind-reader`, `glance-tag-reader`, `glance-oracle-reader` Sonnet 5.5 / medium, all others `claude-haiku-5-5` / `low`. At most **5** subagents running at once. `CLAUDE_CODE_SUBAGENT_MODEL` is not set; the cap of 5 is a rule, not tool-enforced.
- **Reporting:** a subagent returns its result to the main session in the same turn. No mailbox, no `send_message`, no ETA lines, no 4-hour reports. Replies are terse TOON; skip optional analysis.
- **Authority:** the main session's instructions are the user's. A subagent's suggestions are advice only; nothing goes into the game, forge-ai, decks or `enemies.json` without the user's word in chat. No dry or trial deck builds without the user's approval.
- **Guardrails (refuse and name the one):** editing forge-core, forge-game or forge-ai source (patches go in `tools/concordia/ai_lab/patches/`); force-push or history rewrite; PRs; pushing anywhere but campaign-design; unequal-life or life-bonus sims; committing or pushing at all; deleting data without a backup; ticking an approval box.
- **Start of a task:** read `tools/agents/TOOLBOX.md`, `human_logic.toon` (a rule beats a metric) and the role's handoff file.

### Roles (same scopes as the earlier agents; briefs in `.claude/agents/`)
| Role (subagent type) | Does | Writes in |
|---|---|---|
| deck-builder | decklist updates, new decks, categorization, unflagged-card data, using balance data | `forge-gui/res/adventure/Concordia/decks/**`, `tools/concordia/deckgen/**`, its backups in `tools/concordia/backups/` |
| forge-ai-lab | Forge AI research, decision logic docs, test-only patches, balance options for the balance lab | `tools/concordia/ai_lab/**` (not other roles' digests), AI docs, new entries (never ticks) in `AI_CHANGES_APPROVAL.md` |
| deck-balance-lab | runs the sim suite, reports tier, archetype and starter balance against the player-win targets (70% tiers 1-2, 50% tiers 3-5) | `tools/concordia/balance_lab/`, `tools/concordia/suite/` records and reports, its digest folders |
| tag-blind-reader | blind reverse tag check: tags in, ability text out; one instance per batch, Read and Write only | its one output file |
| glance-tag-reader | glance test tag side: tags in, fixed form out; one instance per batch and reader slot, Read and Write only | its one output file |
| glance-oracle-reader | glance test ground truth: name and Oracle text in, same form out; Read and Write only | its one output file |

Briefs still carry the old session/messaging instructions (ETA lines, `send_message`, pushing); this section overrides them.

## Tools
- **Simulator:** run `tools/concordia/sim/setup.sh` once per container. It takes about 1.5 minutes from an empty cache:
  it fetches from Maven Central and leaves out the jitpack-only TenPatch dependency, which is blocked by the network
  policy. It compiles every `.java` in `tools/concordia/sim/`, `tools/concordia/balance_lab/` and `tools/concordia/ai_lab/`. Run sims with
  `tools/concordia/sim/run.sh <Class> <args>`, for example
  `run.sh DeckSim forge-gui/ <games> <timeoutSec> deckA lifeA deckB lifeB label`. Re-run `setup.sh` after adding a sim
  class. For a patched build, use a scratch worktree and `SIM_CACHE=<scratch> SIM_REBUILD=1`.
- **Small test decks:** `python3 tools/concordia/ai_lab/minideck.py SRC.dck OUT.dck --size 40 --test "A;B;C"` (the AI lab uses 40 cards at 20 life each since 2026-10-20; 30 decked too often) keeps the
  commander and the test cards, adds 12 lands and fills with the source deck's cheapest cards. Shrink the opponent the
  same way (no `--test`). Forge sims accept 30-card Commander decks (verified). Games run about 22-25 turns, so a few
  end by decking: compare casts rather than wins.
- **Piloted games:** `tools/concordia/sim/PilotSim.java` plays two decks where outside pilots decide the flagged-card
  plays and Forge AI does the rest (protocol in its header; `pilot_wait.sh` waits for a side's next prompt). Logs of
  each run go to `tools/concordia/ai_lab/pilot/<date>_<name>/`. `-Dpilot.A=rules` plays built-in pilot rules with no
  tokens spent; `ask` uses the file protocol; `ai` is plain Forge AI.
- **Deck stats:** `python3 tools/concordia/power_scorer.py <deck.dck> [--tier N] --json` gives counts, deck power (the
  average card power) and tier checks.
- **Card data roster:** Forge card scripts and editions (offline); the cube ranking; Spellbinder cEDH and precon
  inclusion rates (`deckgen/spellbinder/signals.json`, collected by the main session through its connector); public
  GitHub decklists (`deckgen/external/`, local only); Scryfall (`deckgen/scryfall_bulk.py`: the bulk file, not
  per-card API calls, at most one check per 12 h; throttled lookups with back-off on 429). Prices are never used.
- **Network:** Maven Central, PyPI, raw.githubusercontent.com and `git clone` of public GitHub repos work. Most other
  sites (jitpack, EDHREC, MTGJSON, Archidekt) are blocked; Scryfall is allowed.

## Current state
- **Decks:** 400 AI decks, 80 per tier, all passing their tier checks: the 200 below plus one variant each
  (`deckgen/variants.py`, variants.json): an alternate commander of the same colors, budget-leaning, sharing the
  deck's creature types, with 5-8 cards changed. The base 200: Each tier has 20 original decks (tier 1 is
  mono-color; tiers 2-5 mix one to three colors) plus 20 new mono-color decks, 4 per color, built by
  `tools/concordia/deckgen/gen_mono.py` and seeded from public GitHub decklists that are kept local only. Five starter
  decks for the player, each with an _Alt version (alternate commander, 5-8 cards changed; power 27).
- **Card power** (`power_scorer.card_power`) = 35·raw + 15·efficiency + 15·role + 10·rarity + 5·EDHREC popularity +
  10·Game Changer + 5·fast mana + 5·tutor. Raw power is the highest of the cube rank, the Spellbinder cEDH inclusion
  rate and 0.6 × EDHREC popularity (Scryfall's EDHREC rank, log-scaled).
- **Deck power by tier** (deck average card power, rebuilt 2026-10-20): T1 12-13, T2 21-28, T3 30-38, T4 34-42,
  T5 40-46. Bands: T1 17-23 (tier_rules.py), T2 22-30, T3 29-37, T4 35.5-41.5, T5 >=40 (one source: tools/concordia/tier_table.json, with the builder targets, floor and ceiling). Staples per deck: T1 0, T2 19, T3 30, T4 34,
  T5 38 on average; watch-list cards capped T1 0 / T2 1 / T3 2 / T4 4 / T5 8.
- **Difficulty curve** (OVERWORLD.md §5.1): a zone's stage locks at the player's first fight there, from the Seals held:
  seals 0-1 stage 1, 2-3 stage 2, 4-5 stage 3 (`util/TierLock.java`, config `tierLock`).
  - Wild creatures, random-dungeon enemies, pass keepers, grove guardians and the Warden are mono-color, picked by deck
    power window.
  - Trainers are 1-2 colors at stage 1 and 2-3 after that.
  - The Green zone is the built template. The other four color zones aren't built yet.
- **Enemy start bonuses:** Forge can give an enemy cards on the battlefield at the start of a duel, through an
  `EffectData` with `startBattleWithCard`, `lifeModifier` or `changeStartCards` (`scene/DuelScene.java` ~360). The user
  thinks Forge's own bonuses are too heavy-handed and wants smaller ones, such as a land or a 1-drop, measured against
  no bonus.

- Archetype and engine-goal reference (condensed, generated): `tools/agents/reference/ARCHETYPES.toon`.

## Feedback paths (tag, deck and balance loop)
- **Misleading tag found** by the builder, the AI lab or balance (a card whose tags do not match its Oracle text): add the card to `tools/concordia/deckgen/tagcheck/holdout_cards.txt` or the next reader batch as a test case, note it in `tags/TAG_GAPS.toon` through `tagcheck/guards.py` (never hand-edit), and run `reverse_check.py` plus `reader_metric.py update <run>`. Until the check clears it, `tag_status.py` holds its tags back, so decks get no ability bonus from them.
- **Balance adjusts decks** only in bounded, logged steps: `target` or `weakness` in `decks.json`, one deck per step, each logged in `HANDOVER.md` with the old and new value and the sim record it rests on. No other deck field changes for balance.
- **Second-batch rule:** a mined render or compose rule is pending until a second, different run lists it (`tags/RULE_BATCHES.json`; `python3 tagcheck/reader_metric.py pending`).
- **Old sims go stale** when the tag stamp changes: compare `tag_stamp` in `human_pass.toon` with the stamp on the sim rows before reusing them.

## Recent updates
- 2026-10-22: Rules references for all agents: tools/agents/reference/MTG_COMP_RULES_20260807.txt (Magic Comprehensive Rules, effective 2026-08-07; keywords are rules 701 and 702); tools/concordia/ai_lab/KEYWORD_REFERENCE.toon, KEYWORD_REMINDER_TEXT.toon, KEYWORD_FIRST_RELEASE.toon
- 2026-10-23: Agent roles, schedules, messaging and cooperation rules replaced by the Subagents section (Haiku 5.5, low effort, max 5, spawned only on the user's request)

# Shared context for the Concordia background agents

Read this first on every run, then your own brief (`.claude/agents/<name>.md`). The main session keeps it current
through the agent manager (`.claude/skills/agent-manager/`). The newest changes are listed under "Recent updates" at the
bottom. When this file and your brief disagree, this file wins, because it is newer.

## The project
- Concordia is a Pokémon-like Commander campaign plane for Forge Adventure, in the fork `oliandor712/forgecomventure`.
  All work goes to branch `campaign-design`. No PRs.
- The plane's data lives in `forge-gui/res/adventure/Concordia/`: decks in `decks/tier1..5`, `starter`, `tutorial`;
  `world/enemies.json`; `maps/`; `config.json`.
- The design docs are in `docs/Adventure/Campaign/`: `OVERWORLD.md` (zones, flags, §5.1 the difficulty curve),
  `ENCOUNTER_TIERS.md`, `DECK_REVIEW_SPELLBINDER.md`, `AI_RESEARCH.md`, `AI_FLAGGED_CARDS.md`, `AI_TAGS_REFERENCE.md`.
- The user tests on Windows. The user decides what goes into the game; agents propose.

## Standing rules (all agents)
1. **Equal life on both sides in every simulation, no exceptions.** Life bonuses are eliminated as an option (user,
   2026-10-20); don't test them.
2. **Don't change `forge-core`, `forge-game` or `forge-ai`** on the branch: the user hasn't approved AI-module changes.
   Code ideas go in patch files in your own folder.
3. **Write only in your own folder**, plus your listed docs. Never commit build output, classpaths, `forge-gui/data/`,
   or a modified `forge-gui-mobile/pom.xml`.
4. **Pushing:** pull with `git pull --no-rebase origin campaign-design` before you push. If a push is rejected, pull
   again and retry. On a network error, back off 2/4/8/16 s. Never force-push. If the push still fails, report it and
   push first thing next run.
5. **Low speed, low usage.** Stay inside your time box, keep replies short, and never paste large files or logs.
6. **Pause on request.** When the main session or the user says pause, stop at a safe point, log it and push. Resume
   only when told, or at the time given.
7. **Test updates are pre-approved (user, 2026-10-20).** You may change your test tooling without asking: sims,
   logging, batch runners, test decks, report scripts, and patched scratch copies of forge-ai or card scripts used
   only for testing. Before replacing a file that is already committed, copy the old version to
   `tools/concordia/backups/<date>_<what>/`, or name the old commit in your log. Changes to the game itself still go
   to the user: anything applied to forge-core, forge-game or forge-ai, card scripts, Concordia decks, enemies, maps
   or config.
8. **Proposed AI changes go on the checklist** `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`. Put
   `CHECKLIST: <patch> - <one line> - <status>` in your run report when you save, test or revise a patch. The main
   session updates the list, and the user ticks a box to approve.
9. **Pauses come only from the main session** (day or night). The agent coordinator was removed on 2026-10-20; ignore
   any earlier "hold"/"resume" rule tied to it.
10. **Processes:** never `pkill -f` a pattern that can match your own shell. Kill java by pid
   (`pgrep -a java | grep Sim`). Never leave a sim or build running when you stop.

## Human logic and TOON
- `tools/agents/human_logic.toon` holds the user's own deck-balance rules (30 so far). Read it before you build, judge or test decks; a rule beats a metric. The main session adds a row whenever the user gives deck-balance input.
- **TOON** (https://github.com/toon-format/toon) is the format for data files only Claude reads: a list of same-shaped records or a map of same-shaped objects is written as `name[N]{a,b}:` plus one row each (`name[N|]{a|b}:` when cells hold commas), saving 25-55% against JSON. Keep CSV/TSV for flat tables (smaller), JSON where code reads the file, and markdown for anything the user reads. Check a file with `npx @toon-format/cli file.toon`.

## Asking the main session for analysis
**No per-run messages.** Don't send_message the main session after a run or batch: every message wakes it and costs tokens. Push your results and put them in your 4-hour report. Message it only for a blocker you can't fix.
Put a line starting `ANALYSIS REQUEST:` in your **4-hour report** (not after every test; batch them, to keep the
request-and-answer loop slow and cheap; an urgent blocker may go at once). Give the question, the files it concerns, and what you need
back. The main session reads your reports at its 4-hour check-ins. It files the answer in
`tools/agents/analysis/<your name>.md` and sends it to you. That file is your training data: read it with this one,
build on its findings, and cite entries by date and title.

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
- **Deck stats:** `python3 tools/concordia/deck_tier.py <deck.dck> [--tier N] --json` gives counts, deck power (the
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
- **Card power** (`deck_tier.card_power`) = 35·raw + 15·efficiency + 15·role + 10·rarity + 5·EDHREC popularity +
  10·Game Changer + 5·fast mana + 5·tutor. Raw power is the highest of the cube rank, the Spellbinder cEDH inclusion
  rate and 0.6 × EDHREC popularity (Scryfall's EDHREC rank, log-scaled).
- **Deck power by tier** (deck average card power, rebuilt 2026-10-20): T1 12-13, T2 21-28, T3 30-38, T4 34-42,
  T5 40-46. Bands: T1 <=19, T2 19-31, T3 27-38, T4 34-42, T5 >=39. Staples per deck: T1 0, T2 19, T3 30, T4 34,
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

## Agents
| Agent | Brief | Session | Schedule |
|---|---|---|---|
| forge-ai-lab | `.claude/agents/forge-ai-lab.md` | session_01SdzhYuPRVSAtP7QLaagBxk | step every 2 h at :06 (was hourly; changed at the user's request), about 5 min; report every 4 h |
| deck-balance-lab | `.claude/agents/deck-balance-lab.md` | session_011UrsiVw1s1nsvYUSkv2iLy | hourly batch, at most 10 min, at :10; report every 4 h at :25 |

The main session checks on all agents every 4 hours (at :40) and fixes blockers.

## Recent updates
- 2026-10-21: 
- 2026-10-21: 
- 2026-10-21: Added tools/agents/human_logic.toon (the user's deck-balance rules) and the TOON rule above. Nothing else was converted: existing markdown tables save under 1% and the rest is prose, CSV or code-read JSON.
- 2026-10-21: 
- 2026-10-21: 
- 2026-10-21: Starters were reworked at 5439eb01 (2026-10-21T01:16:50Z; the 01:11 batch still ran the old decks): Squee leads red, Barrin is blue's alt, Breeches is red's alt, green and black swaps. All starter games before that time are on old decks. deck-balance-lab: count starter games only from the 02:10 batch on (STARTER_EPOCH 01:25Z), so the 50/50 split between _Normal and _Alt starts from zero (run_batch.py STARTER_EPOCH does this); split the report at the same commit.
- 2026-10-21: The agent_operations_master doc was deleted at the user's request; the check-in no longer refreshes a doc or reads an inbox. Requests reach the main session in chat only.
- 2026-10-20: 
- 2026-10-20: 200 variant decks added (one per AI deck: alternate commander, 5-8 cards changed), so each tier folder now holds 80 decks; pools and random picks include them. Starters: power 27, blue rerolled to Gadwick wizards, and each colour has a _Normal and _Alt starter (split starter games 50/50). deck-balance-lab: weight coverage toward the new variants until they reach the median game count.
- 2026-10-20: 
- 2026-10-20: forge-ai-lab's shrunk test decks (ai_lab/decks/*_30/_40, all from minideck.py) were regenerated from the current tier decks (T1-2 floor raise, T1 creature loosening), same size, lands and test-card copies. Old copies in tools/concordia/backups/2026-10-20_ai_lab_test_decks_pre_regen/. Results before this commit used the old test decks; don't pool them with new runs. lab001_switchpt and opp_sai_30 (not minideck builds) are unchanged.
- 2026-10-20: 

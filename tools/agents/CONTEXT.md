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
1. **Equal life on both sides in every simulation.** The one exception is a test of a life bonus itself, and the record
   must say so.
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
7. **Processes:** never `pkill -f` a pattern that can match your own shell. Kill java by pid
   (`pgrep -a java | grep Sim`). Never leave a sim or build running when you stop.

## Asking the main session for analysis
Put a line starting `ANALYSIS REQUEST:` in your run report: the question, the files it concerns, and what you need
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
- **Decks:** 200 AI decks, 40 per tier, all passing their tier checks. Each tier has 20 original decks (tier 1 is
  mono-color; tiers 2-5 mix one to three colors) plus 20 new mono-color decks, 4 per color, built by
  `tools/concordia/deckgen/gen_mono.py` and seeded from public GitHub decklists that are kept local only. Five starter
  decks for the player.
- **Card power** (`deck_tier.card_power`) = 35·raw + 15·efficiency + 15·role + 10·rarity + 5·EDHREC popularity +
  10·Game Changer + 5·fast mana + 5·tutor. Raw power is the highest of the cube rank, the Spellbinder cEDH inclusion
  rate and 0.6 × EDHREC popularity (Scryfall's EDHREC rank, log-scaled).
- **Deck power by tier** (deck average card power): T1 13-15, T2 21-28, T3 30-38, T4 34-41, T5 40-46. Starters 26-31.
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
| forge-ai-lab | `.claude/agents/forge-ai-lab.md` | session_01SdzhYuPRVSAtP7QLaagBxk | hourly step, about 5 min, at :06; report every 4 h |
| deck-balance-lab | `.claude/agents/deck-balance-lab.md` | session_011UrsiVw1s1nsvYUSkv2iLy | hourly batch, at most 10 min, at :10; report every 4 h at :40 |

The main session checks on both every 4 hours (at :20) and fixes blockers.

## Recent updates
- 2026-10-20: EDHREC popularity (Scryfall) added to card power; deck power rose about 1.5 at T1-T3; zone power windows shifted to match. New: ANALYSIS REQUEST lines in your reports get answered into tools/agents/analysis/<you>.md (your training data).
- 2026-10-20: Scryfall card data downloaded: deckgen/scryfall/cards.json.gz (35k cards: EDHREC rank, Game Changer, legality, identity; no prices), read with scryfall_bulk.load(). Bulk refresh at most every 12 h.
- 2026-10-20: Card data roster: Scryfall (tools/concordia/deckgen/scryfall_bulk.py, bulk oracle_cards, at most one check per 12 h; /cards/collection lookups throttled). Blocked by the network policy until the user allows api.scryfall.com and data.scryfall.io.
- 2026-10-20: The first piloted test match was discarded at the user's request (too many problems); don't use its data. PilotSim now has a no-token rules mode (-Dpilot.A=rules).
- 2026-10-20: ai_lab/minideck.py shrinks a deck to a 30-card test deck (commander + test cards + 12 lands + the source deck's cheapest cards); Forge sims accept 30-card Commander decks, verified. setup.sh now also compiles tools/concordia/ai_lab/*.java (AiLabSim was missing).
- 2026-10-20: Agent manager added: this file is the shared context (read first every run); tools/agents/registry.json logs your standing requests. Briefs now point here.
- 2026-10-20: `tools/concordia/sim/setup.sh` and `run.sh` added. They fix the "no Maven repository" blocker and were
  verified from an empty cache. Don't edit `forge-gui-mobile/pom.xml` by hand.
- 2026-10-20: added the push-retry rule (standing rule 4).
- 2026-10-20: decks doubled to 200, and the difficulty curve built into the Green zone.

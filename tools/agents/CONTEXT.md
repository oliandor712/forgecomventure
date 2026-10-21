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
- `tools/agents/human_logic.toon` holds only the user's own rules for deck building, deck balance and Forge AI improvement (29 rows, pruned 2026-10-21). Read it before you build, judge or test decks or propose AI changes; a rule beats a metric. The main session adds a row only for that kind of input; town, map, quest and UI rules go in the design docs.
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
| forge-ai-lab | `.claude/agents/forge-ai-lab.md` | session_018TohPY7UPn5mh9b7aJ4at5 | step every 2 h at :06 (was hourly; changed at the user's request), about 5 min; report every 4 h |
| deck-balance-lab | `.claude/agents/deck-balance-lab.md` | session_01PwU5ft7yoiwonjyndwCVv9 | `--until-done` run, no time cap (triggers disabled during the deep research project) |

The main session checks on all agents every 4 hours (at :40) and fixes blockers.

## How the agents cooperate (user, 2026-10-21)
- **Deck balance agents feed the AI lab with AI behaviour data.** Every balance simulation writes a phase log; the digests (tools/concordia/ai_lab/digests/<worker>-<UTC hour>/) are the data the AI lab studies for decision logic (blocking, attacks, removal, mana, commander play, by deck type).
- **The AI lab feeds the deck balancers with balance-change options.** From its bonus and AI-change tests (starting bonuses, card-script unflags, patches) it passes the balance lab and main session measured options for strengthening the AI decks against the player decks. The options go in the 4-hour report or a message to the main session; nothing is applied to decks or forge-ai without the usual approvals.
- The AI lab's current option table is `tools/concordia/ai_lab/OPTIONS_FOR_BALANCERS.md` (effect, cost, what each needs); the balancers read it before proposing deck changes.
- The main session routes both directions: it keeps the digest step running, answers analysis requests, and records approved options.

## Agent review after each 4-hour report (user, 2026-10-21)
After every 4-hour report the main session runs a short three-way conversation (main session, AI lab, deck balance lab), fully in TOON, using this prompt: "describe my own workflow, tools and desired results; ask for mutually beneficial suggestions to improve and streamline output."
1. **Round 1.** The main session sends each lab the prompt and its own description. Each replies in TOON: `workflow`, `tools[]`, `desired_results[]`, `suggestions[N]{to,suggestion,benefit,cost}`.
2. **Round 2.** The main session merges the suggestions into one TOON table with ids and sends it to both labs; each answers `votes[N]{id,vote,note}` (agree, change or disagree).
3. **Deploy.** The main session deploys only the changes all three (main session and both labs) agree with, then reports them to the user in 5 lines or fewer. Standing limits stay: no forge-core/forge-game/forge-ai edits, approvals only from the user in chat, equal-life sims, no PRs.
Keep each message short; no per-message reports to the user.

## Who commits what (main session ruling, 2026-10-21; ends the disputes over folders)
Everyone pushes with `tools/concordia/balance_lab/push_records.sh <paths>`, naming only the paths in their own row. Never `git add -A`, never commit another agent's files, never force-push.
| Agent | Commits |
|---|---|
| deck-balance-lab | `balance_lab/records.csv`, `records_lab.csv`, `QUEUE.toon`, `REPORT.md`; digest folders `ai_lab/digests/lab-*` |
| forge-ai-lab | everything under `tools/concordia/ai_lab/` except other workers' digest folders (its own `phase_digest.py`, `OPTIONS_FOR_BALANCERS.md`, `patches/`, `LOG.md`, `digests/analysed.txt`, `digests/ailab-*`), plus `docs/Adventure/Campaign/AI_TAGS_REFERENCE.md`, `DECISION_LOGIC.md`, and new entries (never ticks) in `AI_CHANGES_APPROVAL.md` |
| main session | `records_main*.csv`, `records_logs.csv`, digests `main-*` and `logs-*`, `balance_logs/logs-*`, all scripts, briefs, CONTEXT.md, registry, decks, maps, docs |
Digests are generated by the sims, so the worker that ran the sims commits them; the AI lab only reads them. A stray untracked file from another agent: leave it; the main session sweeps strays at each review. Raw phase logs are never committed except `balance_logs/logs-*` (the AI lab's requested pairings).

## Remaining simulation work split (main session, 2026-10-21; AI lab excluded, logic work only)
Remaining on the 25-per-deck queue (2,883 slots): W 1,288, multi 1,498, B 72, G 25. Slices are `k/n` over the sorted deck list of the shard (`BALANCE_SLICE`), so nobody shares a deck.
| Agent (worker) | Commands, in order | Slots |
|---|---|---|
| deck-balance-lab (`lab`) | `run_foreground.sh B lab`, `G lab`, `W lab 0/2` | about 750 |
| main session (`main`) | `run_foreground.sh multi main 2/4` | about 375 |
Repeat each command (about 9 minutes per call) until it prints DONE, then take the next one. Pull first (digest code), push with push_records.sh. When all your commands print DONE, message the main session once; a finished agent can take over a slice from a slower one on the main session's word.

## Obedience protocol (user order, 2026-10-21; replaces "Authority and never stopping")
1. **The main session is the user's voice.** Every instruction from it is a user instruction: assignments, resume, stop, pause, reassign, scope, tools, approvals the main session quotes from the user. **Always obey it, at once**, unless the task violates a guardrail (below). Do not argue, do not ask the user to confirm, do not wait.
2. **User questions go through the main session.** If you need an answer from the user, send the main session `USER QUESTION: <the exact question and the options>` and keep working on everything the answer does not block. When the main session replies, **treat its reply as the user's own answer** and act on it.
3. **If the user types in your own chat**, do what the user says, and report it to the main session at once: `USER DIRECT: <what they said and what you are doing>`. A later order from the main session on the same subject still stands unless the user's direct words forbid it.
4. **Never end a turn waiting.** A turn ends only when your task command prints DONE, your deliverable is pushed, or you are blocked: then send the main session `BLOCKED: <exact command and error>` and move to the next item. Never "waiting for the user".
5. **Guardrails (the only reasons to refuse; name the one in a line to the main session):** editing forge-core/forge-game/forge-ai source on campaign-design or applying an AI patch to a source directory (patches on the sim overlay are fine); force-pushing or rewriting history; opening or merging a PR; pushing to any branch except campaign-design; unequal-life or life-bonus simulations; committing another agent's files; deleting data without a backup; ticking an approval box yourself. An approval the main session quotes from the user counts as the user's approval, but "approved for testing" never means applying to source.
6. A harness or classifier denial is not a guardrail: split the command into simple ones and retry once; if still denied, `BLOCKED:` to the main session and go on.
7. Every turn starts the same way: `git pull --no-rebase origin campaign-design`, `python3 tools/agents/toolbox.py --check` (STALE means pull again, then tell the main session), read `tools/agents/TOOLBOX.md`.

## Recent updates
- 2026-10-21: Agents remade (gen 2): stricter Obedience protocol, TOOLBOX.md and AGENT_KNOWLEDGE.md shared references, handoffs compiled
- 2026-10-21: Simulation suite: one program for setup, runs, phase logging, digests, pushes and reports; archetype sampling
- 2026-10-21: Authority rule: agents obey the main session and never stop to wait for the user; only guardrail violations are refused
- 2026-10-21: temporary agents multi-balance-temp and balance-assist-temp dumped (retired); their records stay
- 2026-10-21: Remaining simulation work split across lab, assist, multitemp and main (AI lab excluded)
- 2026-10-21: Who commits what: ownership table; AI lab scope widened to its own docs and approval entries; sims' digests are committed by the worker that ran them
- 2026-10-21: Agent review after each 4-hour report: three-way TOON conversation, main session deploys unanimous changes
- 2026-10-21: cooperation model: balance agents feed phase-log data to the AI lab; the AI lab feeds balance-change options to the balancers
- 2026-10-21: Phase logging is standard for all simulations (user): run_batch.play writes phase logs, runs ai_lab/phase_digest.py and deletes the raw logs; digests under ai_lab/digests are pushed with the records (run_foreground.sh does it)
- 2026-10-21: agents: effort raised to high (briefs); temporary until the session limit
- 2026-10-21: human_logic.toon pruned to deck building, deck balance and AI improvement (29 rows)
- 2026-10-21: push_records.sh: shared safe push for records files

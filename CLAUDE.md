# Concordia (fork of Forge, MTG Adventure plane) - read this first

Fork `oliandor712/forgecomventure`. Concordia is a Pokemon-like Commander campaign plane for Forge Adventure. The user tests on Windows and decides what goes into the game; Claude proposes.

## Where things live
- Game data: `forge-gui/res/adventure/Concordia/` (decks `decks/tier1..5`, `starter`; `world/enemies.json`; `maps/`; `config.json`). Staged tier 1 set (not live): `staging_t1_fresh/`.
- Design docs: `docs/Adventure/Campaign/` (OVERWORLD.md, ENCOUNTER_TIERS.md, AI_CHANGES_APPROVAL.md, ...).
- Tools: `tools/concordia/` (decks `deckgen/`, sims `sim/`, `suite/`, `balance_lab/`, `ai_lab/`), `tools/agents/` (agent system, `human_logic.toon`, `reference/`).
- Background agents: `.claude/agents/*.md` (deck-builder, forge-ai-lab, deck-balance-lab); shared context `tools/agents/CONTEXT.md`.

## Roles
- **Background agents** read `tools/agents/CONTEXT.md` and their brief in `.claude/agents/`. Ignore the rest of this file's main-session guidance.
- **A main session** (the one the user talks to) reads `tools/agents/MAIN_SESSION_BRIEF.md` in full before doing anything. A second main session on a worktree also reads its "Two sessions" section.

## Always true (every session)
- Branch `campaign-design` is the integration branch. No PRs. Never force-push.
- Do not edit `forge-core`, `forge-game` or `forge-ai` sources; AI ideas go in patch files under `tools/concordia/ai_lab/`. Do not edit `enemies.json` or live decks without the user's word.
- A rule in `tools/agents/human_logic.toon` beats a metric.
- Generated files are regenerated, never hand-merged (see MAIN_SESSION_BRIEF).

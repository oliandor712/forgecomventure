# Concordia (fork of Forge, MTG Adventure plane) - read this first

Fork `oliandor712/forgecomventure`. Concordia is a Pokemon-like Commander campaign plane for Forge Adventure. The user tests on Windows and decides what goes into the game; Claude proposes.

## Where things live
- **New session:** the start script is `START.md` (repo root).
- **Lookup first:** read `tools/agents/INDEX.md` (task to file map, size guide). Never read BIG files whole (Comprehensive Rules, STARTER_TAGS, ABILITY_TWINS, records.csv); use `python3 tools/agents/lookup.py` slices, or Grep then Read with offset/limit.
- Game data: `forge-gui/res/adventure/Concordia/` (decks `decks/tier1..5`, `starter`; `world/enemies.json`; `maps/`; `config.json`). Staged tier 1 set (not live): `staging_t1_fresh/`.
- Design docs: `docs/Adventure/Campaign/` (OVERWORLD.md, ENCOUNTER_TIERS.md, AI_CHANGES_APPROVAL.md, ...).
- Tools: `tools/concordia/` (decks `deckgen/`, sims `sim/`, `suite/`, `balance_lab/`, `ai_lab/`), `tools/agents/` (agent system, `human_logic.toon`, `reference/`).
- Background agents: `.claude/agents/*.md` (deck-builder, forge-ai-lab, deck-balance-lab); shared context `tools/agents/CONTEXT.md`.

## Roles
- **Background agents** read `tools/agents/CONTEXT.md` and their brief in `.claude/agents/`. Ignore the rest of this file's main-session guidance.
- **A main session** (the one the user talks to) reads `tools/agents/MAIN_SESSION_BRIEF.md` in full before doing anything. There is one main session; no background agents are used unless the user asks.

## Always true (every session)
- **Subagents (strict):** model and effort come from each `.claude/agents/*.md` frontmatter and are never overridden in the Agent call: `tag-blind-reader` is `claude-sonnet-5-5` / `medium`, all other agents `claude-haiku-5-5` / `low`. At most 5 running at once (a rule, not tool-enforced). `CLAUDE_CODE_SUBAGENT_MODEL` is not set, so the frontmatter applies; for built-in agent types without frontmatter (general-purpose, Explore, Plan, ...) the Agent call must pass `model: haiku`. Only spawn when the user asks.
- Branch `campaign-design` is the integration branch. No PRs. Never force-push.
- Do not edit `forge-core`, `forge-game` or `forge-ai` sources; AI ideas go in patch files under `tools/concordia/ai_lab/`. Do not edit `enemies.json` or live decks without the user's word.
- A rule in `tools/agents/human_logic.toon` beats a metric.
- Generated files are regenerated, never hand-merged (see MAIN_SESSION_BRIEF).
- Documents (reports, checklists, plain `.md` for the user) are pushed automatically with `python3 tools/agents/docpush.py <paths>` at every update, and revised in place (no near-identical copies). Everything else (code, decks, data, records, instruction files) pushes only on the user's "push".

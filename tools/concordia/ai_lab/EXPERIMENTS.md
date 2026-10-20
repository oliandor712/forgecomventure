# Forge AI lab experiments

One entry per experiment (see `.claude/agents/forge-ai-lab.md`). Newest last.

## Candidate list (not yet tested)
Source: `AI_FLAGGED_CARDS.md` "Other stale signals" (117 `RemoveDeck:All` cards whose main ability already has `AILogic$`). Candidates found by grep of `forge-gui/res/cardsfolder`, `AI:RemoveDeck:All` plus `A:` with the named logic:
- `AILogic$ SwitchPT`: myr_quadropod, turtleshell_changeling, crag_puca, aquamoeba
- `AILogic$ Fog`: thwart_the_enemy, vine_snare, harsh_justice, endure, shield_dancer
- `AILogic$ Evasion`: falter, flash_of_defiance, camouflage, ember_gale, seismic_stomp, magmatic_chasm
- `AILogic$ NeedsPrevention`: beacon_of_destiny, martyrs_cause, oracles_attendants, intervention_pact, jade_monolith
- `AILogic$ Pump`: irresistible_prey, kjeldoran_pride, shapesharer, satyr_piper

Plan for experiment 001: card-script-only patch (drop the stale flag) on 2-3 `SwitchPT` cards (Turtleshell Changeling, Myr Quadropod, Aquamoeba; `PumpAi.java:55`), test deck plus a tier2 opponent, equal life, up to 4 games, detect casts/activations in the log.

## Pause (2026-10-20 14:47Z)
Main session asked for a pause during a large deck-generation job. State: no experiment started; experiment 001 (drop stale flag on Turtleshell Changeling, Myr Quadropod, Aquamoeba) is planned only. No scratch worktree, build or sim exists; nothing is running.

# Forge AI lab experiments


**Convention (user, 2026-10-20): 30-card test games start at 20 life each (equal; changed from 15).** Experiment 001 was run before this rule at 40/40; re-run it at 20/20 when convenient.
**Update (user, 2026-10-20): 10 games per condition, and from the next test on decks are 40 cards (`minideck.py --size 40`) to limit decking; life stays 20 each.** Experiments 001-002 used 30 cards.
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

## Resumed (2026-10-20 14:57Z)
Main session finished its deck job. Normal hourly schedule; next step is experiment 001 setup.

## 001: unflag SwitchPT cards (Aquamoeba, Turtleshell Changeling, Myr Quadropod)
- **Hypothesis:** the `AI:RemoveDeck:All` flag is stale; `PumpAi` already has `AILogic$ SwitchPT` (`PumpAi.java:54`), so removing the flag lets the AI cast and use them.
- **Change:** `patches/001-switchpt-unflag.patch` (card scripts only; tested from a scratch assets copy, nothing applied to the branch).
- **Test:** `AiLabSim` (`tools/concordia/ai_lab/`), deck `Lab001 Alandra` vs `Thopter Workshop` (T2_U_Sai), both shrunk to commander + 29 with `shrink_deck.py` (full 99-card decks rarely drew the cards: 8 games, 0 casts), equal life 40, 4 games each, 150 s cap.
- **Result:** baseline 0 casts / 0 activations. Patched: 7 casts (Turtleshell in 4/4 games), 26 activations, effect matches the text (P/T switched). Wins 1-3 vs 2-2 (noise). Turtleshell sometimes activated many times a turn-cycle (max 12 in one game).
- **Verdict:** worth proposing; scale the same check to the other 114 `All` cards that already carry an `AILogic$` (Fog, Evasion, NeedsPrevention, Pump). Note: with 30-card decks the games end by decking around turn 24.

### 001 re-run at 20/20 life (2026-10-20, per the 20-life convention)
Same decks (30 cards), 4 games each, equal life 20. Baseline (flag kept): 0 casts, 0 activations, wins 1-3, avg 20.3 turns. Patched: 7 casts (Turtleshell 3, Aquamoeba 2, Myr Quadropod 2), 30 activations, wins 1-3, avg 19.8 turns. Same picture as the 40/40 run: the flag alone keeps the three cards unplayed; removing it makes the AI cast and use them. Wins are noise at 4 games. Verdict unchanged: worth proposing.

## 002: unflag Fog-logic instants (Thwart the Enemy, Vine Snare)
- **Hypothesis:** `AILogic$ Fog` is already handled (`EffectAi.java:112`), so the flag is stale and the AI will cast them when under attack.
- **Change:** `patches/002-fog-unflag.patch` (card scripts only, tested from a scratch assets copy).
- **Test:** `lab002_fog_30.dck` (Arasta, 30 cards, 2 copies of each test card) vs `opp_mirri_30.dck`, equal life 20, 10 games per condition (new user rule: 10 games).
- **Result:** baseline 0 casts. Patched 19 casts (Thwart 11, Vine Snare 8), in games they were drawn. Wins 0-10 vs 2-8, avg turns 19.2 vs 22.7: the AI is surviving longer, consistent with the fogs working. A quick 4-game pilot gave the same casts-vs-none picture.
- **Not yet checked:** that each cast came at a sensible time (during an attack), and Endure / Harsh Justice / Shield Dancer.
- **Verdict:** worth proposing; next, read the game log for cast timing on a few casts.

## 003: unflag white Fog-logic cards (Endure, Shield Dancer; Harsh Justice tested but excluded)
- **Change:** `patches/003-white-fog-unflag.patch` (Endure, Shield Dancer). Scratch assets copy had all three unflagged.
- **Test:** `lab003_whitefog_40.dck` (Adeline, 40 cards, 2 copies of each test card) vs `opp_red_40.dck`, equal life 20, 10 games per condition (first run with the 40-card rule).
- **Result:** baseline 0 casts. Patched: Endure 15 casts, Shield Dancer 11 casts and 19 activations; Harsh Justice 0 casts although it was still in hand at game end in 4 of 10 games. Wins 6-4 vs 4-6, avg turns 17.1 vs 24.1 (the AI survives longer).
- **Open question (Harsh Justice):** it is not a plain fog (it reflects combat damage) and has `ActivationPhases$ Declare Attackers` and `CheckSVar$ Y` (`HasPropertyBeenAttackedThisCombat`). With the flag gone the AI still never casts it; likely `FogAi` (`ability/FogAi.java`) never sees a damage threat that justifies it, or the SVar check fails. Needs a read of `FogAi.canPlay` and a targeted test; not part of the patch.
- **Verdict:** Endure and Shield Dancer: worth proposing. Still to check: cast timing in the logs.

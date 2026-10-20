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

## Re-run of 001-003 with natural card density (n001, n002, n003; user request 2026-10-20)
Change from the first runs: 1 copy of each test card (not 2) in 40-card decks built with `minideck.py --size 40`, so the flagged cards are about as likely to be drawn as any other card; 10 games per condition, equal life 20, baseline (flag kept) and patched (flag removed) in parallel via `run_exp.sh`, phase-annotated logs in `results/n00X-{baseline,patched}/`, summaries `results/n00X-summary.txt`. Same 8 card patches as 001-003; opponents Sai (blue), Mirri (green), red 40-card deck.

| Test | Cards | Baseline casts | Patched casts / activations | Wins A (baseline -> patched) | Games card seen (patched) |
|---|---|---|---|---|---|
| n001 SwitchPT | Aquamoeba / Turtleshell / Myr Quadropod | 0 / 0 / 0 | 3 / 5 / 7; 6 / 32 / 54 | 0-10 -> 0-10 | 4 / 6 / 7 |
| n002 Fog | Thwart the Enemy / Vine Snare | 0 / 0 | 4 / 4 | 0-10 -> 0-10 | 4 / 4 |
| n003 white Fog | Shield Dancer / Harsh Justice / Endure | 0 / 0 / 0 | 9 casts (6 act.) / 0 / 2 | 9-1 -> 8-2 | 4 / 0 / 2 |

Findings: (1) with natural density the flag is still the whole difference: baseline never casts any of the 8 cards, patched casts every card it draws (except Harsh Justice, never seen). (2) Phases of the patched activations (n001): 70 log lines in B's beginning-of-combat, 20 in declare blockers, 15 postcombat main (casts), 2 in declare attackers; so the SwitchPT cards are used in combat, not idly, but activation counts are high (Myr Quadropod 54 over 7 games). (3) Fogs are cast rarely (4 each in 10 games) which fits "only when threatened". (4) Win rates do not move; the opponents are stronger than these decks in n001/n002.

## Main-session analysis of 001-003 (filed in tools/agents/analysis/forge-ai-lab.md) and my follow-up plan
- True Fogs (Thwart the Enemy, Vine Snare, Endure) are timed correctly (FogAi: opponent's declare blockers, life in danger). Patches 002 and 003 (now Endure only) stand.
- SwitchPT (001) is mostly wasted: PumpAi:57,:83 only check "in combat / not used this turn". Patch 001 is demoted to "needs a guard": **planned patch 005** = PumpAi SwitchPT guard (switch an unblocked attacker with toughness > power; switch a blocked attacker that dies anyway only if the switch kills a blocker; switch a blocker only to kill and survive; never outside its own combat).
- Harsh Justice can never be cast (declare attackers vs FogAi's declare blockers). **Planned patch 004** = `AILogic$ ReflectCombatDamage` in EffectAi, cast in the opponent's declare attackers when expected unblocked attacking power >= 3 or >= the attacker's life. Shield Dancer targets the best attacker rather than the creature it blocks (EffectAi:136-140): goes with the Choose*/EffectAi logic work.
- Logging to add to AiLabSim per playable window of a flagged card: AiPlayDecision code, host role (attacking/blocking/neither) and opposing P/T, predicted damage, outcome (host survived, what it killed), and a "useful" column so every experiment reports a useful-play rate. A cast count alone does not prove good play.

## 005: SwitchPT as two creatures (PumpAi code patch; user's idea) 
- **Hypothesis:** treating the host as two creatures (current P/T vs switched T/P) and switching only when the other version scores higher in this combat removes the spam (92 activations/10 games, none useful) while keeping the good switches.
- **Change:** `patches/005-switchpt-two-versions.patch` (PumpAi.java only; tested in the scratch worktree with the 001 card flags removed). Declare-blockers only; unblocked attacker scores damage (lethal 10000), blocked attacker/blocker scores kills of opposing creatures minus own value if it dies.
- **Test:** n001 deck/opponent as above, 10 games, equal life 20. Logs: `results/n001-twoversions/`, `results/n001-guard/` (simple-rule version).
- **Result:** unguarded 92 activations (58 with the creature not in combat); simple guard 4; two-version scoring 8, all in declare blockers. Samples: Myr Quadropod unblocked switched to 4 power (+2 damage to B, 15 -> 7 life); Aquamoeba switched when blocked and traded with Thopter Mechanic. Wins unchanged (A 1-9), too few activations to move results.
- **Verdict:** keep; the log lines show correct-phase, mostly beneficial uses. Next: add the per-activation logging the main session asked for (role, P/T, blocks, outcome, useful flag) and re-test at more activations (deck with several switch cards).

### 005 v3 (revised after main-session review)
Patch 005 now uses `ComputerUtilCard.shouldPumpCard` for the "which version" decision, charges discard costs (60 spare land / 120), counts planeswalker loyalty as lethal. v2 saved in `tools/concordia/backups/2026-10-20_005-v2-patch/`. Test n001, 10 games, equal life 20: 20 casts, 2 activations (declare blockers), logs `results/n001-v3/`. Activation history: 92 (flag only) -> 4 (v1) -> 8 (v2) -> 2 (v3). Open: too few activations to judge usefulness; needs a switch-heavy deck and the extra log columns. Also pending from the review: mana opportunity cost, exposure to instant-speed removal, AiCardMemory marker for the Echoing Truth case.

## Test set s005 / s006: code patches 005 v3 and 006, A/B against unpatched jars (run_code_ab.sh)
Setup: both arms use the scratch assets (card flags removed); "base" = unpatched forge-ai jars, "code" = scratch worktree jars (patches 005 v3 + 006 together). 40-card decks with 3 copies of each test card (deliberately above natural density, to give the logic more decisions; note it), 10 games, equal life 20. Logs: `results/s005-{base,code}/`, `results/s006-{base,code}/`.
- **s005 SwitchPT** (Alandra deck x3 copies of Aquamoeba/Turtleshell/Myr Quadropod vs Sai): base 68 activations (17 in B's beginning of combat, 17 in declare blockers, rest counted twice in the log lines), casts 30; code 14 activations, all in declare blockers, casts 43. Wins A 2-8 vs 1-9 (noise). Host died the same turn after an activation: 0 times in either arm (the log does not include other creatures' zone changes, so kills are not measured yet).
- **s006 Fog** (Arasta deck x3 Thwart/Vine Snare vs Mirri): base 18 casts, code 17 casts, all in B's declare blockers in both arms. Wins A 5-5 vs 2-8 (noise). Patch 006 (count Effect fogs) shows no measurable difference here: it only changes the mana-reservation when life is in danger; needs a targeted scenario to test.
- **Verdict:** 005 v3 cuts activations about 80% and removes the beginning-of-combat spam; whether the remaining 14 are good needs the kill/loss outcome columns. 006: no evidence either way yet.

## 008: shouldPumpCard counts gang-block co-blockers (code patch; main-session gap A)
`ComputerUtilCard.shouldPumpCard` (blocker branch, ~line 1665) built `pumpedCombat` with only the pumped blocker, dropping co-blockers' damage. `patches/008-pump-gang-block.patch` adds them. Test s008 (switch-heavy deck, 10 games, equal life 20, logs `results/s008-code/`, which now also include zone changes so kills are visible): 3 switch activations, all declare blockers; 8 of 12 activation turns had a creature go to the graveyard (all creatures, not attributed). Inconclusive: needs a controlled gang-block scenario (several blockers vs Sai) and per-activation kill attribution. Also logged: AiLabSim context now includes ZONE_CHANGE and STACK_ADD lines; still missing: mana available and hand size at activation.

## Regression sim for patch 008 (and the whole scratch build: 005 v3 + 006 + 008), per main-session request
Two pairings of 40-card tier 2-3 decks with pump instants (`minideck.py --size 40`, no forced cards): r008a Shroofus (T3 G) vs Kiki-Jiki (T2 R); r008b Legolas (T2 G) vs Zilortha (T3 RG). 10 games per arm, equal life 20, base = unpatched jars, code = scratch worktree jars. Watched cards: the pump instants of both decks (counts are both sides together). Logs in `results/r008{a,b}-{base,code}/`.
| Pairing | Base pump casts (cards seen) | Code pump casts (cards seen) | Wins A: base -> code |
|---|---|---|---|
| r008a | 11 (15 draws) | 16 (20) | 4-6 -> 9-1 |
| r008b | 9 (15) | 14 (21) | 3-7 -> 5-5 |
Casts per card drawn: 0.73 -> 0.80 (a), 0.60 -> 0.67 (b): no red flag (the raw cast increase comes from drawing more of the watched cards, which is run-to-run variance in 10 games). Wins moved toward side A in both pairings (7 -> 14 of 20) but that is not attributable to the patch with these counts (both sides run the same code); I would not read it as a result. Combat kills and blocker losses are not yet compared: the log lacks per-combat kill attribution. Verdict: no sign that 008 (or the rest of the scratch build) distorts pump use; still needs the controlled gang-block scenario and a larger regression (more decks, 20+ games) before it is proposed.

## g008: controlled gang-block test, base vs 008 ONLY (main-session order (c))
Code arm = a separate scratch worktree with only patch 008 applied (cache `simcache-008`); base = unpatched jars (`run_code_ab.sh` now takes `CODE_CP`). Defender: Arasta green 40 cards with 2 copies each of Giant Growth, Titanic Growth, Blossoming Defense (so the blocker branch of shouldPumpCard is exercised); attacker: Selvala (T4 G) 40 cards; 10 games, equal life 20. Logs `results/g008-{base,code}/`.
- Pump casts: base 31 (22 watched draws), code 25 (20): 1.41 vs 1.25 casts per draw. Phases: base 23 declare blockers + 8 beginning of combat; code 20 + 5. No pump cast outside combat in either arm.
- Gang blocks (an attacker blocked by 2+ creatures) in turns with a pump cast: 4 in each arm. Creatures to graveyard in those turns: 28 vs 15 (not attributed to pumps; code games were shorter, 17.3 vs 24.9 turns). Wins A 6-4 vs 7-3.
- Verdict: no red flag (casts per draw -0.16, below the ~15 points = 0.15-per-trick threshold only marginally; within noise for 10 games) and no sign of non-combat pumping. But the 008-specific path (co-blocker damage making a kill) is not isolated: only 4 gang-block turns per arm, and no pred/actual per-event log yet. Next: add the per-event log (pumped_id, group ids, pred, actual, useful) and run 20 games per arm.

## Shadow-mode test of patch 008 (main-session design: same game state, both answers)
Scratch build of 008 now computes the blocker-branch decisions of `shouldPumpCard` twice (without / with co-blockers) and prints `SHADOW` when they differ (`pumpedDies`, `kills <creature>`), plus `SHADOWREACH` on every blocker-branch evaluation. 20 games (2 x 10) on the g008 decks (Arasta tricks defender vs Selvala fatty), equal life 20, acting on the 008 answer; logs `results/shadow008/`.
Result: 406 blocker-branch evaluations, 37 with co-blockers (5 with 1, 7 with 2, 25 with 3), and **0 disagreements** between the base and 008 answers. So in these 20 games patch 008 never changed a pump decision: the changed code is reached with co-blockers (37 times) but the gang-block damage never flipped the "pumped dies" or "kills" answer. Either the cases are rare in this matchup or the co-blockers' damage rarely matters for the kill check. Verdict: 008 has no demonstrated effect here; do not propose it on this evidence. Candidate next: a hand-built situation (3 small blockers, an attacker whose toughness is between one and all blockers' damage) to see if the fix can ever flip, and main-session candidate 009 (pumps stacking past what is needed).

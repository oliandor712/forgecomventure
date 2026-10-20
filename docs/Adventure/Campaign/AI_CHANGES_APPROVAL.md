# Forge AI changes: final approval checklist

Every proposed change to how the Forge AI plays, from the AI lab (`.claude/agents/forge-ai-lab.md`) and the main
session's analyses (`tools/agents/analysis/forge-ai-lab.md`).

- **Nothing here is applied to `campaign-design`** until you tick its box and ask for it to be applied.
- **Test-side updates are pre-approved:** the agents' sims, logging, test decks and scratch copies, with old versions
  backed up.
- **Updates:** the main session updates this list at each 4-hour check-in and whenever the AI lab saves a patch.

Each item says what it changes, where, and what the tests show. "Ready" means tested, with a result worth applying;
"needs work" means not ready yet.

## Card-script changes (data only: removing a stale `AI:RemoveDeck:All` flag)

- [ ] **002, unflag the green Fogs: Thwart the Enemy, Vine Snare**: Ready.
  - Patch: `tools/concordia/ai_lab/patches/002-fog-unflag.patch`.
  - Tested: 0 casts with the flag, 19 without it (2 copies, 30-card decks), and 8 at normal card density.
  - Every cast came in the opponent's declare blockers step, facing unblocked attackers.
- [ ] **003, unflag Endure**: Ready.
  - Patch: `patches/003-white-fog-unflag.patch`.
  - Tested: 0 casts with the flag; 15 casts (2 copies) and 2 at normal density without it.
  - It was cast only when the AI was under real threat.
- [ ] **001, unflag the switch creatures: Aquamoeba, Turtleshell Changeling, Myr Quadropod**: Needs work.
  - Patch: `patches/001-switchpt-unflag.patch`.
  - The AI now casts them, but it spams the switch: 58 of the 60 activations at normal density came with the creature
    not in combat.
  - Apply only together with 005.

## forge-ai code changes (the AI's own logic; none approved yet)

- [ ] **005, switch as "two versions"**: Tested, needs work.
  - Where: `forge-ai/.../ability/PumpAi.java`. Patch: `tools/concordia/ai_lab/patches/005-switchpt-two-versions.patch`.
  - What it does: switch only in declare blockers of a combat the creature is in. Compare the creature as it is with
    it switched, and switch only if the switched version does better. At most one switch and one switch back per
    turn.
  - Tested in 10 games: activations went from about 92 to 8, all well timed.
    - Good: an unblocked Myr Quadropod switched to hit for 4.
    - Fair: an Aquamoeba switched to trade with its blocker.
  - Still to fix (main-session review):
    - Use Forge's own combat predictor (`ComputerUtilCard.shouldPumpCard`, line 1470), which handles first strike,
      deathtouch and similar.
    - Subtract the activation cost: Aquamoeba discards a card.
    - Tell the rest of the AI when a switch is chosen to trade. Today another routine then bounced the creature with
      Echoing Truth.
    - Allow the switch that saves it from damage.
  - Wins are unchanged: 1-9 in all versions.
- [ ] **006, Fog count includes Effect-based Fogs**: Planned.
  - Where: `FogAi.java:116-133` (`countAvailableFogs`).
  - Count spells with `AILogic$ Fog` as Fogs, so the AI's "3 or more Fogs in hand" play works for decks built on those
    cards.
- [ ] **007, attacker curses aimed through the blocker (Shield Dancer and similar)**: Planned.
  - Where: `EffectAi.java:136-140`.
  - Target only an attacker this creature is blocking, and only when the redirected damage kills it. Otherwise don't
    activate.
- [ ] **004, Harsh Justice logic (`AILogic$ ReflectCombatDamage`)**: Planned.
  - Where: `EffectAi.java`, about 20 lines, plus one card-script line.
  - Cast it during the opponent's declare attackers step when the attacking power it can't block well is at least 3,
    or at least the attacker's life.
  - Without it, Harsh Justice can never be cast.
- [ ] **Shield Dancer unflag**: Needs work. It waits for 007.

## How a box gets ticked

1. The AI lab tests the change in a scratch copy (pre-approved) and records the "useful play" rate as well as casts
   and wins.
2. The main session updates the item's status here and points to the result.
3. You tick the box and ask for it to be applied. The main session then applies the patch to `campaign-design`,
   backs up the replaced files in `tools/concordia/backups/`, and re-runs the checks.

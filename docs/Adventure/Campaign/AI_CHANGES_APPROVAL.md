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

- [ ] **005, switch as "two versions"**: Tested (v3), close to ready.
  - Where: `forge-ai/.../ability/PumpAi.java`. Patch: `tools/concordia/ai_lab/patches/005-switchpt-two-versions.patch`.
  - Switch only after blocks, for a creature in this combat, when Forge's combat predictor (`shouldPumpCard`) says the
    switched version does better, net of the activation cost.
  - Code A/B (3 copies each, 10 games): activations went from 68 to 14, all in declare blockers. About 5-6 of the 7
    activation lines reviewed were clearly useful (unblocked switches for +3/+4 damage; a doomed Aquamoeba taking a
    blocker with it), compared with about 0 at baseline.
  - Left to check: gang blocks. A switch that completes a group block was not taken, possibly a kill of the enemy
    commander. Also more logging (object ids, mana, kills).
- [ ] **008, gang blocks in pump decisions**: Written, needs testing.
  - Where: `ComputerUtilCard.shouldPumpCard`, the blocker branch (around line 1663-1675). Patch:
    `patches/008-pump-gang-block.patch`.
  - When deciding whether to pump (or switch) a blocker, count the other blockers' damage too, so "my pump completes a
    group block's kill" is seen.
  - Shared by every pump spell and ability, so it needs a regression sim on ordinary decks with pump spells, plus a
    controlled gang-block test.
  - The 10-game test was inconclusive: no gang block came up.
  - Kept separate from 005, which works without it. 005 gets better with it.
- [ ] **006, Fog count includes Effect-based Fogs**: Tested, no effect; parked.
  - Where: `FogAi.java:116-133`. In the A/B test it changed nothing measurable.
  - It only matters when the AI holds 3 or more Fogs and isn't in danger, which only a deck built around Fogs would
    see. Low priority unless such an encounter deck is planned.
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

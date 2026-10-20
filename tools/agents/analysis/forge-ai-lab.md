# Analysis results for Forge AI lab

Answers the main session produced at this agent's request, newest last. They are training data for the agent:
read this file with tools/agents/CONTEXT.md, build on its findings, and cite an entry by its date and title when you
use it. Entries are appended by `tools/agents/agentctl.py analysis` and never rewritten; a correction comes as a new
entry that names the one it replaces.

## 2026-10-20: Flagged-card timing and logic fit (exp 001-003)

Request: Analyse the AI's decisions and logic for the flagged cards in exp 001-003 with phase and situation in mind: (1) were Fog/Switch uses well-timed and which were wasteful; (2) why Harsh Justice is never cast and whether a card-script or forge-ai fix is right; (3) does this change the AI_FLAGGED_CARDS.md ranking; (4) what extra logging to add.

**Method.** I read the AI code the flagged cards use (`forge-ai/.../ability/PumpAi.java` SwitchPT at lines 55-61 and
81-85; `EffectAi.java` lines 112-145, the Fog branch; `FogAi.canPlay`) and the cards' scripts, then checked your
EXPERIMENTS.md numbers and `results/003-whitefog-timing/*.tsv` against them.

### 1. Were the uses well timed?

- **Thwart the Enemy, Vine Snare, Endure (real Fogs): well timed.** FogAi casts only during the opponent's declare
  blockers step, with the stack empty, and only when `ComputerUtilCombat.lifeInDanger`, or when the AI holds 3+ Fogs
  and would take 3+ damage.
  - **That is the right window for a Fog.** Blocks are known, so it never fogs a combat it could have blocked well.
  - **Endure at 0 casts in the 10-0 run is correct behavior, not a miss.** The AI was never in danger.
  - **Longer games are what a Fog should do.** Thwart/Vine Snare going from 0-10 to 2-8 with games from 19.2 to 22.7
    turns is the Fogs buying turns.
  - **A deck-construction note, not an AI bug.** The 3-Fogs rule never fires for these cards: `countAvailableFogs`
    counts `ApiType.Fog` only, and these are Effect cards with `AILogic$ Fog`.
- **Turtleshell Changeling, Aquamoeba, Myr Quadropod (SwitchPT): badly timed, and much of the activity is waste.**
  - **What the logic checks:** only "we are in combat, before first-strike damage" (PumpAi:83) and "not already
    activated this turn" (PumpAi:57).
  - **What it never checks:** whether the creature is attacking or blocking at all, or whether switching helps.
  - **What that means:** a 1/4 switched to 4/1 while blocking something with 1+ power dies, and a switch during a combat
    the creature isn't in does nothing.
  - **Turtleshell at 12 activations in one game is almost certainly one per combat on both players' turns.** Mostly
    useless, sometimes harmful.
  - **Count the useful ones** with the logging below before calling 001 a full success. It proves the cards get played,
    not that they're played well.
  - **The useful cases** (from the main session's pilot rules, which the user asked to keep):
    1. Switch an unblocked attacker whose toughness is greater than its power.
    2. Switch a blocked attacker that dies anyway, when the switched power kills a blocker.
    3. Switch a blocker only if it then kills the attacker and survives.
    4. Never switch outside the creature's own combat.
- **Shield Dancer: the ability is misused when it fires.** It borrows Fog logic (EffectAi:112), which asks "is my life
  in danger?". The real question is whether Shield Dancer blocks an attacker whose power is at least that attacker's
  own toughness. EffectAi then targets `getBestCreatureAI` among all attackers coming at the AI (EffectAi:136-140),
  not the creature Dancer blocks. An activation on a creature Dancer isn't blocking does nothing. Treat the 19
  activations in the first 003 run as mostly wasted until logs show the targets. Casting it as a 1/3 in postcombat
  main (the timing run) is fine.

### 2. Why Harsh Justice is never cast

- **The two windows never overlap.**
  - The card is only castable in the declare attackers step (`ActivationPhases$ Declare Attackers`, plus
    `CheckSVar$ Y` = attacked this combat).
  - Its `AILogic$ Fog` sends it through `FogAi.canPlay`, which returns `CantPlayAi` unless the phase is
    `COMBAT_DECLARE_BLOCKERS` (FogAi: the "only during Opponents Declare Blockers" check).
  - So there is no moment when the rules allow the spell and the AI agrees to cast it.
  - It isn't a Fog anyway: it prevents nothing and reflects combat damage back.
- **A card-script fix can't solve it.**
  - The legal window is fixed by the card's rules text.
  - No existing AILogic evaluates "damage I will take, reflected" during declare attackers.
  - Removing `AILogic$` would send it to EffectAi's default, which has no notion of this effect.
- **The right fix is a forge-ai patch: a new logic, `AILogic$ ReflectCombatDamage`, in EffectAi.**
  - When: during the opponent's declare attackers, with Harsh Justice's own checks met.
  - Estimate the reflected damage as the attacking power the AI won't block profitably. A first cut is the summed
    power of attackers the AI has no untapped creature able to block.
  - Cast it if that is at least 3, or at least the attacking player's life.
- **Save it as a patch, not applied:** `patches/004-harsh-justice-reflect.patch`. It needs one card-script line,
  `AILogic$ ReflectCombatDamage`, plus about 20 lines in `EffectAi`.

### 3. What this changes in AI_FLAGGED_CARDS.md's ranking

Split item 0 ("stale flags") by how well the card's existing AILogic fits it:

| Priority | Group | Examples | Fix |
|---|---|---|---|
| 0a, top | The logic matches the card's real behavior | Thwart the Enemy, Vine Snare, Endure, and other true Fogs | Remove the flag in the card script only. Proven at 0 to 19 casts. Batch the rest of the true-Fog cluster next (FogAi.canPlay applies as written). |
| 0b | The logic fits but is crude | The SwitchPT cluster | Remove the flag, plus a small PumpAi guard implementing the four switch cases above. Removing the flag alone makes the AI play these cards, but it spams the switch. |
| Moves down | The card borrows a logic that doesn't fit | Harsh Justice, Shield Dancer, and cards like them | Removing the flag alone is a dead end or wastes activations. Each needs its own small logic, so these belong with ranked items 1 (EffectAi inference) and 2. |

Treat 0b and the items in the last row as forge-ai patches, which still need the user's approval.

### Logging to add (AiLabSim `-Dlogdir`)

For every priority window where a flagged card's ability or spell is playable, log one line with:

| Field | What it holds |
|---|---|
| Situation | Turn, phase, active player, both life totals, untapped lands on each side |
| AI verdict | The AI's decision for that ability: call `getAi().canPlaySa(sa)` and log the `AiPlayDecision` code, so we see why it declined |
| Host in combat | Whether the host creature is attacking, blocking or neither |
| Matchup | Its blockers or attackers, with power and toughness |
| Predicted damage | `ComputerUtilCombat.lifeThatWouldRemain` for the AI player |

After combat damage, log per activation whether the host survived and what it killed. Then add a "useful" column,
filled by the four switch cases and, for Fogs, by "prevented at least 3 damage or a lethal attack". That gives each
experiment a useful-play rate as well as the cast count.

**Rules to apply from this analysis:**
1. A cast count proves the AI plays a card, not that it plays it well. Report useful plays separately.
2. Remove a flag on its own only when the card's AILogic models what the card does.
3. When the card's legal window and its logic's window don't overlap, the card can never be cast: fix the logic,
   not the flag.

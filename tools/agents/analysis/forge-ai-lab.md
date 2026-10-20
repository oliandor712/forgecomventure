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

## 2026-10-20: Quality of use at natural density (n001-n003)

Request: Judge from the phase-annotated n001-n003 patched logs whether each flagged card's use was sensible (SwitchPT spam and beginning-of-combat activations; Fog timing; Shield Dancer targeting), and give general logic changes with file:line plus extra log columns.

**Data.** The phase-annotated logs `results/n001|n002|n003-patched/*.tsv`. I classified every cast or activation of a
flagged card by:
- whose turn it was;
- the phase;
- whether the card's own creature appears in that turn's combat lines (attacking or blocking).

### (a) SwitchPT is spam: every activation in n001 was pointless

| Activations | When | Combat |
|---|---|---|
| 34 | Opponent's beginning of combat | creature not in combat |
| 15 | Own postcombat main | creature not in combat |
| 9 | Own declare blockers step | creature not in combat |
| 2 | Opponent's turn | creature in combat (both Aquamoeba) |

- **No switch improved a combat result.** Of the two in-combat activations, 1 came at the opponent's beginning of
  combat (before blocks) and 1 at declare blockers, where it did nothing useful.
- **Beginning-of-combat switches on the opponent's turn are worse than pointless.**
  - No blocks exist yet.
  - A 1/4 that becomes a 4/1 before blocks dies to any 1-power attacker it then blocks.
- **Why it happens:** PumpAi only checks "in combat, before first-strike damage" (`PumpAi.java:81-85`) and "not
  already used this turn" (`PumpAi.java:55-61`).
  - So it fires once in every combat that has any creature in it, on both players' turns.
  - The 15 postcombat activations are not explained by that phase rule. Check `AiPlayDecision` for them: they may come
    through the "save it from damage" pump path (a response to burn), which can be a valid use. Log the stack when it
    activates (see the logging list).

### (b) The Fogs were well timed

- **All 8 Thwart the Enemy and Vine Snare casts came in the opponent's declare blockers step,** with 1-5 unblocked
  attackers.
- **At least one stopped a near-lethal attack:** A went 9 to 4 through first strike, and the Fog covered the rest.
- **The weakest cast** was Thwart the Enemy against a single unblocked Mirri, Cat Warrior with A at 5-6 life.
  Defensible, since the AI was low.
- **Both Endure casts were in declare blockers against 3 unblocked attackers.** Fine.
- **Keep FogAi's timing.** Its rule (opponent's declare blockers, life in danger) is the right model for prevent
  effects.

### (c) Shield Dancer's activation is mis-targeted

- In n003 game 2, turn 33, Shield Dancer blocked Skirk Prospector. The AI activated it twice that step, targeting
  Gempalm Incinerator, which Dawnbringer Cleric was blocking.
- **The ability only works on an attacker that deals damage to Shield Dancer,** so both activations were wasted mana
  at 4 life.
- **The cause:** EffectAi's Fog branch targets `ComputerUtilCard.getBestCreatureAI` among all attackers (`EffectAi.java:136-140`).
- **Casting it as a creature** (6 casts in main phases) is fine.

### (d) General rules: reusable logic changes

1. **Pump-self that changes stats, like SwitchPT** (`PumpAi.java:55-61` and `81-85`).
   - Activate only in your declare blockers step or your opponent's, after blocks, and only if the host is attacking
     or blocking. (The one exception: responding on the stack to damage aimed at the host, when the new toughness
     survives it.)
   - Decide by simulating: compare `ComputerUtilCombat.combatantWouldBeDestroyed(ai, host, combat)`
     (`ComputerUtilCombat.java:675`) and the damage the host deals, with and without the switch. Activate only if the
     switch:
     - adds damage to an unblocked attacker;
     - kills a blocker or attacker while the host still survives;
     - or kills one when the host dies either way.
   - This one guard covers every "switch" and "+X/-X self" card. It is the same rule set the pilot sim's `rules` mode
     plays.
2. **Prevent effects** (FogAi, which is already sound).
   - `FogAi.countAvailableFogs` (`FogAi.java:116-133`) counts only `ApiType.Fog`. Count Effect spells with
     `AILogic$ Fog` too, so the "3 or more Fogs in hand" branch works for those decks.
   - If a card's `ActivationPhases` excludes declare blockers (Harsh Justice), FogAi can never say yes. Route such
     cards to their own logic (the `ReflectCombatDamage` proposal from the first analysis), not to Fog.
3. **Effects aimed at an attacker that the effect's own source must face, like Shield Dancer** (`EffectAi.java:136-140`).
   - When the replacement effect names the effect's source as its target (Shield Dancer's
     `ValidTarget$ Card.EffectSource`), narrow the candidates to attackers that the host itself blocks:
     `combat.getBlockers(attacker).contains(host)`.
   - Then pick the one whose redirected damage kills it, i.e. power at least its own toughness.
   - With no such attacker, don't activate.
   - Reuse this rule for any curse on an attacker that only works through the blocker.

All three are forge-ai changes, so save them as patch files only: `patches/005-switchpt-combat-sim.patch`,
`006-fog-count-effect-fogs.patch`, `007-curse-blocked-attacker.patch`. They need the user's approval before going in.

**Log columns to add for each flagged activation:**

| Column | What it holds |
|---|---|
| `host_role` | attacking, blocking or none |
| Host stats | the host's power/toughness before and after |
| Opposing creatures | for the host, or for the target: whether it's blocked, and by what |
| `pred_life` | `ComputerUtilCombat.lifeThatWouldRemain` for the AI |
| `on_stack` | what was on the stack when it activated (separates responses from spam) |
| `decision` | the `AiPlayDecision` for declined windows |
| `result` | after damage: did the host survive, and what died |

From those, compute a **useful** flag per play, using the rules in (d).

**Rules to apply:**
1. Judge a flagged card by its useful-play rate, not its cast count. At natural density, removing the flag alone
   raises casts but not wins (0-10 both ways in n001 and n002).
2. Prevent effects need a real threat (the opponent's declare blockers, life in danger), and FogAi already does that.
3. Self-pump and redirect effects need a combat simulation with and without the effect, plus a target the host itself
   is fighting.

## 2026-10-20: Patch 005 two-version SwitchPT review

Request: Judge each activation in n001-twoversions (g4, g6, g9): better version or not, missed alternatives (first strike, deathtouch, tricks, double blocks), soundness of versionScore's value model; is two versions the general pattern for 'become X temporarily' cards; concrete PumpAi corrections with patch lines and extra log columns.

**Data.** `patches/005-switchpt-two-versions.patch` and `results/n001-twoversions/` g4, g6 and g9 (the activations,
with that turn's combat, damage and life lines).

### Each activation

| Game, turn | What happened | Verdict |
|---|---|---|
| g6 T14 | Myr Quadropod attacking, unblocked, switched to 4/1, hit for 4 (B 15 to 7) | Right: the better version |
| g9 T17 | Aquamoeba attacking, blocked by Thopter Mechanic, switched to 3/1, killed the Mechanic, died | Defensible trade, but the score ignored the cost. Aquamoeba's switch costs a card from hand, so it traded a creature plus a card for one creature |
| g4 T23 | On B's attack, Myr Quadropod and Turtleshell Changeling both switched while blocking | Mixed (below) |

On g4:
- **Turtleshell (4/1) took 1 damage from Barkform Harvester and died.** If its 4 damage killed the 3-toughness
  Harvester, it's a fair trade. Confirm with the damage lines.
- **Myr was then bounced by A's own Echoing Truth in the same step.** The switch made Myr a 4/1 that would die, so a
  second part of the AI (its "save my creature" logic) spent a card bouncing it.
- **That sequence is a loss:** mana for the switch, a spell, and Myr gone from the board, to avoid a trade the switch
  logic had just chosen.

### Corrections to the patch (line numbers are the patch's `+` lines)

1. **Score with Forge's own combat predictor, not hand-written damage math** (lines 54-85, `versionScore`).
   - Today's math misses first strike and double strike, deathtouch, indestructible, prevention, trample, lifelink,
     and damage the creature already took this turn. Line 81 compares to full toughness; it should use toughness
     minus damage already marked.
   - `ComputerUtilCard.shouldPumpCard(ai, sa, host, p - t, t - p, emptyList)` (ComputerUtilCard.java:1470) already
     simulates a pumped creature in the current combat, all of those included. A switch is a pump of +(t-p)/+(p-t).
   - Use it as the decision. Keep the two-version idea for what it does well, picking between versions: call
     `shouldPumpCard` for the switch, and for the switch back while switched.
2. **Subtract the activation cost** (add it to line 50's comparison).
   - Aquamoeba's "Discard a card" costs card value. A cheap estimate: `evaluateCreature`-scale 60 for a spare land
     (more lands than turns left), 120 for any other card.
   - Mana costs (Turtleshell {1}{U}, Myr {3}): subtract 10 per mana that a spell in hand could have used this turn.
   - Then switch only if the gain beats the cost.
3. **Don't choose a trade that another AI routine will then pay to undo** (lines 76-83).
   - When the chosen version dies (`toHost >= toughness`), put the host in `AiCardMemory`, using a new memory set or
     `MemorySet.HELD_MANA_SOURCES_FOR_ENEMY_DECLBLK`'s pattern, so the "save my creature" logic skips it this turn
     (the g4 Echoing Truth).
   - Or require that the kill be worth clearly more: value(kills) > 1.25 × value(host).
4. **Keep the per-turn cap** (line 25: at most a switch and a switch back). Keep the phase gate (lines 96-97: declare
   blockers, in combat).
   - Also allow the save-from-damage case: switch in response to damage aimed at the host when the new toughness
     survives it. Today's gate blocks that useful case.
5. **Value model** (line 67): power × 10 versus kills by `evaluateCreature`. It's fine as long as the two scales
   never meet in one comparison, and today each branch compares like with like, as you say. With correction 1 they
   stop mattering anyway.
   - Keep the lethal shortcut at 10000. Count planeswalker defenders too: power at least its loyalty.

### Is two versions the right general pattern? Yes, for "becomes X temporarily" cards

This covers switches, pumping itself, Animate or BecomeCreature (manlands, vehicles, awakening), and turning a morph
face up. The rule: compare the card as it is now with the card as it would become, in the current combat and board,
using Forge's existing predictors on a copy with the change applied:
- **Building the copy:** `CardCopyService` LKI copy + `addChangedCardTypes` / `addPTBoost`;
- **Predicting the outcome:** `ComputerUtilCombat.attackerWouldBeDestroyed` / `blockerWouldBeDestroyed`,
  `ComputerUtilCard.evaluateCreature`.

Then subtract the cost and act only if the gain is clear. Two extra checks for things that last until end of turn:
- **Exposure:** an animated land can be killed by sorcery-speed or instant removal. Subtract a risk term when the
  opponent has open mana.
- **Timing:** for animating to attack, decide before declare attackers. Use the version's attack value against the
  expected blocks (the existing `AiAttackController` evaluation of the copy).

### Logging to add for every switch or "become X" activation

| Column | What it holds |
|---|---|
| `score_now` / `score_switched` | The predictor's outcome per version: survives or dies, what it kills, and the damage to the player |
| `cost` | The card discarded (and its value), or the mana spent |
| `role` | Attacker unblocked, attacker blocked, or blocker, and the opposing P/T plus keywords (first strike, deathtouch) |
| `followups` | Any other spell or ability the AI aimed at the host later that turn (catches the g4 bounce) |
| `outcome` | After damage: host survived or died, kills, damage dealt |
| `useful` | 1 if the outcome beat the unswitched version, judged from the outcome after the game |

**Rules to apply:**
1. Pick between versions with Forge's combat predictor, including first strike and deathtouch, never with
   hand-written damage math.
2. Count the activation cost, cards above all, before choosing a version.
3. When a version is chosen to trade, tell the rest of the AI, so another routine doesn't pay to undo it.
4. Two versions is the general pattern for any "becomes X until end of turn" card: compare now against transformed,
   then subtract the cost and the exposure.

## 2026-10-20: s005/s006 code A/B review

Request: (1) judge the s005-code activations and what shouldPumpCard still misses; (2) is 14 vs 68 too conservative; (3) what scenario would show 006's effect; (4) which log columns first.

**Data.** `results/s005-code/*.tsv`. For each turn I parsed the declare attackers and blockers lines and the damage
lines. My parser finds 7 activation lines, not 14; the log may write one line per activation or one per resolution.
Keep object ids on activation lines so they can be matched (logging list below).

### (1) The activations

| Game, turn | What happened | Verdict |
|---|---|---|
| g0 T12, g2 T9, g2 T11 | Turtleshell attacking, unblocked, switched, hit for 5, 4 and 4 | Useful (+3 to +4 damage each) |
| g4 T9, g5 T11 | Myr Quadropod attacking, unblocked, switched, hit for 4 and 5 | Useful |
| g9 T18 | Aquamoeba triple-blocked (Thopter Token, Spectrum Sentinel, Thopter Mechanic), switched to 3/1 | Right call: it dies either way and the switch lets it kill a blocker. The damage lines are missing, so the kill can't be confirmed |
| g2 T14 | Turtleshell blocking Thopter Mechanic (2 power) | Unclear |

On g2 T14: the damage lines show Turtleshell #8 dealing 1, meaning not switched at damage, and #7 taking 1 from Sai.
Either the activated Turtleshell was the other copy, or it switched and switched back. Probably 2 mana for nothing.
Object ids on the activation line will settle it.

**Score:** 5 to 6 clearly useful out of 7, against about 0 of 68 at baseline. A large real improvement.

### (2) Too conservative? Mostly right, with two gaps

18 combats had a flagged creature attacking or blocking with no switch. Most declines were correct:
- Turtleshell blocking Etherium Sculptor (g5 T16) or Brass Man (g8 T19), and Myr blocking Spectrum Sentinel
  (g3 T21). Switching kills the attacker but the 4/1 dies, trading a 4-drop for a 2-drop.

**Gap A: gang blocks.**
- Several turns have 2-4 of A's creatures blocking Sai, Master Thopterist, B's commander: g1 T20, g4 T14, g5 T16,
  g6 T13.
- In g5 T16, Aquamoeba and Myr block Sai. A switched Myr adds +3 damage, likely enough to kill the commander. Sai deals
  its damage to the creature of B's choice, so the Myr risk is small. No switch happened.
- **Check whether `shouldPumpCard` for a blocker counts the other blockers' damage.** It should use the combined
  damage (`ComputerUtilCombat.totalDamageOfBlockers` or `attackerWouldBeDestroyed(ai, attacker, combat)` with the pump
  applied). If it judges the pumped blocker alone, it misses every "my switch completes a gang block" kill.

**Gap B: unblocked attackers left unswitched.**
- g3 T6: Aquamoeba unblocked dealt 1. A switch would have dealt 3, at the cost of a discard.
- g5 T9: Myr unblocked dealt 1.
- These are probably mana or cost choices, Myr's {3} being unavailable or the discard judged too costly. That's
  fine, but they can't be verified without mana available and hand size in the log.

### (3) Patch 006 needs a scenario where life is NOT in danger

- FogAi's count only matters in the `fogs > 2 && dmg > 2` branch (FogAi.java, before the `lifeInDanger` check). With
  the patch, a hand of 3 or more Effect Fogs makes the AI fog an attack of 3 or more damage even at a safe life total.
  Without it, the AI only fogs when in danger.
- **The test:**
  - The AI's deck holds 3-4 copies each of Thwart the Enemy, Vine Snare and Endure.
  - Both sides at 40 life (equal), against a go-wide deck that attacks every turn for 3-8.
  - Measure casts made while not in danger, damage prevented, and whether those Fogs were missing later when the AI
    was in danger.
- **I expect 006 to make the AI spend Fogs earlier,** which helps only a deck built around Fogs. Concordia has no such
  deck, so **park 006** (low priority) unless a Fog-themed encounter deck is planned.

### (4) Log columns, in this order

1. **Object id and controller** on every activation and damage line, plus mana available and hand size when a flagged
   ability was playable.
2. **Zone changes for every creature in a combat** that has a flagged card, so kills are counted.
3. **role** (attacker unblocked, attacker blocked, blocker) and the opposing creatures' power, toughness and keywords.
4. **score_now / score_switched**, or the `shouldPumpCard` verdict, and the activation **cost**.
5. **outcome**, and a **useful** flag (did the switch beat the unswitched result).

**Rules to apply:**
1. A switch on an unblocked attacker is the reliable win, and v3 takes those.
2. The remaining upside is gang blocks: evaluate a blocker's pump with the whole block's damage.
3. Don't pay for a patch with no scenario: 006 only matters for decks built around Fogs.

## 2026-10-20: s008 gang-block patch review

Request: Check whether 008 shows up in s008-code (g0 T13, g7 T37); is a controlled gang-block scenario the right next test; merge 008 into 005 or keep separate.

**Data.** `patches/008-pump-gang-block.patch`; `results/s008-code` g0 T13 and g7 T37, with the new zone-change and
stack lines.

### Does 008 show up? No: neither activation reaches the changed code

- **g0 T13:** Myr Quadropod was attacking, unblocked. It switched and hit for 4 (B 18 to 11). Useful, but this is
  005's unblocked-attacker case.
- **g7 T37:** Turtleshell was attacking, and A activated it twice in declare blockers.
  - In between, B sacrificed a run of artifacts to Sai's ability: Thopters, Hope of Ghirapur and equipment, all shown
    as zone changes. That changed the combat.
  - The second activation reads as a switch back after the blocks changed. That's legal under 005's "one switch and
    one switch back" rule and plausibly correct, but the log doesn't show Turtleshell's own blocks or damage, so it
    can't be judged.
- **Why 008 never ran:** it changes `shouldPumpCard`'s blocker branch, so it only runs when the AI's creature is one
  of several blockers on the same attacker. Neither activation was a block.

### Next test: yes, a controlled gang-block scenario, plus a regression sim

1. **Gang block (what 008 is for):**
   - The Alandra deck defends with several 1-power and 4-toughness blockers, switch cards included.
   - The opponent deck attacks with one or two big creatures: 5/5 to 7/7 green or red fatties from `decks/tier3`,
     with mono-green T3 and T4 decks as opponents.
   - Both sides at 20 life, 10 games per arm, same seeds where possible.
   - Measure the gang-block combats where a switched blocker completes a kill, base against code. The code arm should
     kill the big attacker more often, without losing more blockers.
2. **Regression, because 008 changes every Pump decision while blocking:**
   - Pick 4 ordinary decks with pump instants, such as Giant Growth or Brute Force, from tiers 2-4 (search for
     `Pump` + `NumAtt$` instants in their lists).
   - Play 10 games each, base against code, at equal life.
   - Report pump casts, combat kills and win rate. Any big change in pump casts is a red flag to investigate before
     proposing.

### Merge into 005 or keep separate? Keep 008 separate

- **005** changes only SwitchPT handling in PumpAi.
- **008** changes the shared `ComputerUtilCard.shouldPumpCard` that every pump spell and ability uses. It needs its own
  regression result and its own approval box.
- **005 works without 008.** 008 only adds the gang-block cases. On the checklist: 008 is a separate item, and 005's
  note says "better with 008".

**Rules to apply:**
1. Check that a test reaches the changed code before reading its results. Here, a gang block with a flagged card
   among the blockers.
2. A change to shared helpers like `shouldPumpCard` needs a regression sim on ordinary decks before it's proposed.
3. Keep separate patches separate when their reach differs, so each can be approved on its own evidence.

## 2026-10-20: Regression for 008: not enough yet

Request: Is the r008 regression (2 pairings x 10 games) enough for 008, or 20+ games, real pump-trick decks, or the gang-block scenario first; which pump events to log for kill attribution.

**Data.** `results/r008{a,b}-{base,code}` and the EXPERIMENTS.md section "Regression sim for patch 008".

### Verdict: not enough yet

Three problems, in order:
1. **The arms change three things at once.** Code ran 005 v3, 006 and 008 together, so nothing is attributable to
   008. A regression for 008 must be base against 008 only (a scratch build with just that patch).
2. **The decks barely reach 008's code.** 008 changes the blocker branch of `shouldPumpCard`. Only 2 of the watched
   cards are real combat pumps; most "pump instants" in these decks are removal or bite spells, which use other AI
   paths. Casts per card drawn (0.73 to 0.80, 0.60 to 0.67) are within noise for these counts, so no red flag, but no
   evidence either.
3. **No kill attribution,** so the question 008 asks ("did my pump plus the other blockers kill the attacker?") isn't
   measured.

### Next, in this order

1. **The controlled gang block (c) first.** It proves the benefit and tells you what to log.
   - The Alandra switch deck defends with 3 or more small blockers. Force switch cards and 2 Giant Growth-style
     instants with `minideck --test ... --copies 2`.
   - The opponent attacks with 1-2 big creatures (a tier 3-4 green fatty deck).
   - 10 games, base against 008 only.
2. **Then the regression (a + b): 20 games per arm, base against 008 only, on decks with real pump tricks.**
   - Make two pump-trick test decks with minideck: green with Giant Growth, Titanic Growth and Blossoming Defense, and
     white with Brute Force-type tricks or Moment of Heroism. Two copies each, 40 cards.
   - Play them against ordinary tier 2-3 decks.
   - What would be a red flag: pump casts per drawn trick changing by more than about 15 percentage points, or more
     pumps cast while not in combat.

### Logging for kill attribution, per pump or switch event

| Column | What it holds |
|---|---|
| `pumped_id` | The pumped creature's object id and controller |
| `role` | Attacker or blocker, plus the ids of every creature in that combat group (an attacker and all its blockers) |
| `pred` | The predicted outcome from shouldPumpCard: kills which ids, loses which ids |
| `actual` | After combat damage: the ids of every creature from that group put into a graveyard this step (from your ZONE_CHANGE lines, matched by id) |
| `useful` | 1 if `actual` matches the pump's purpose: an opposing creature died that wouldn't have without the pump, or the pumped creature survived when it otherwise wouldn't. Judge "otherwise" by simple math on the logged P/T |

Also, a note about pkill: you used `pkill -f` once and it killed your own shell. Good that you've switched to killing
by pid; it's standing rule 10 in CONTEXT.md.

**Rules to apply:**
1. Test one patch at a time against base.
2. Pick decks that reach the changed code path.
3. Measure the decision's purpose (kills, survival) by object id, not only casts and wins.

## 2026-10-20: g008 gang-block test review; shadow-mode logging

Request: Parse g008 base/code gang-block combats (blockers, trick, deaths); is any code cast a decision base would not make; per-event log before or after the 20-game run.

**Data.** `results/g008-{base,code}/*.tsv`. I parsed every turn with a trick cast (Giant Growth, Titanic Growth,
Blossoming Defense), its declare-blockers lines and its graveyard zone changes.

**A parsing note.** The log line reads "<blockers> to block <attacker>". Selvala's name has a comma in it, so a naive
"X and Y" test counts single blocks by Selvala as gang blocks. The real gang blocks are below.

### The real gang blocks

| Arm, game, turn | Who blocked whom | Trick cast | Graveyard that combat | Reading |
|---|---|---|---|---|
| base g0 T26 | B's Collector Ouphe and Leaf Gilder block A's Deadly Recluse | Blossoming Defense on the Recluse (the attacker) | Recluse, Gilder, Ouphe (+1) | Attacker-side pump: not 008's path |
| base g4 T36 | 5 of A's creatures block B's Phyrexian Dreadnought | Titanic Growth ×2 + Blossoming Defense ×2, all on Deadly Recluse | 4 of A's blockers died; Dreadnought not in the list | Over-pumping (below) |
| base g8 T27 | A's Spider Token and Sylvan Ranger block B's Collector Ouphe | Blossoming Defense on Sylvan Ranger | Ouphe, Spider Token | Fine |
| code g4 T15 | A's Grappler Spider and Canopy Spider block B's Krallenhorde Howler | Blossoming Defense on Canopy Spider | Howler, Grappler Spider | Fine; the same shape as base g8 T27 |
| code g2 T15 | B's Leaf Gilder and Selvala block A's Arasta | Giant Growth on Deadly Recluse (another creature) | none | No gang-block decision |

**The over-pumping in base g4 T36:**
- Four tricks went on one blocker in one combat, and that blocker has deathtouch.
- Deathtouch already kills whatever it damages, so extra power does nothing. Only toughness (surviving) matters.
- A lost 4 creatures and 4 cards, and the Dreadnought apparently survived.
- **This is a bug in the unpatched AI, not in 008.** The pump logic doesn't stop once an earlier pump this combat
  already secured the outcome, and it values power on a deathtouch creature.
- I'm adding it as a candidate checklist item, **009**: don't stack pumps past what the predicted outcome needs, and
  don't count power for a creature with deathtouch.

### Is any code cast a decision the base wouldn't make?

- **Can't tell from these runs.** The arms are different games, so no decision lines up with a counterpart.
- The two comparable gang blocks (code g4 T15 and base g8 T27) got the same kind of decision.
- With 4 gang-block turns per arm, a game-level A/B won't isolate 008's path even at 20 games.

### Log first, then run. And make the log a shadow mode

- **Build per-event logging before the 20-game run,** as you suggest. Best of all, add a shadow evaluation.
- **How it works:** at every `shouldPumpCard` call, compute both answers, the unpatched blocker-branch result and the
  008 result. Act on one of them (the arm's), and log `SHADOW pumped_id role group_ids base=<y/n> 008=<y/n>`
  whenever they differ.
- **Why it wins:** each disagreement is exactly a decision 008 changes, in the same game state. Then judge each with
  `pred`, `actual` and `useful`.
- **It's cheap:** 10 games of the pump-trick decks in the code arm give every disagreement with its outcome, and no
  game-level noise.
- **Then the 20-game regression only checks the totals:** casts per drawn trick, and pumps outside combat.

**Rules to apply:**
1. To isolate a decision change, evaluate both versions on the same game state (a shadow mode) instead of comparing
   different games.
2. Read gang-block logs carefully. Card names contain commas; parse by object id, not by "and".
3. Watch for over-pumping: several tricks on one creature in one combat, or power on deathtouch. It's a separate
   problem (candidate 009).

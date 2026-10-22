# Tag links: syntax for tags that depend on each other (design draft, nothing built)

User request 2026-10-22: link tags that depend on each other (for example `first_strike` + until end of turn) so a reader knows how they work together. Syntax is the point. Draft by the main session; no code changed, `ability_tags.py` untouched.

## Why
`first_strike` alone says nothing. "Target creature gains first strike until end of turn" is one clause where the trigger, the grant, the thing granted, who gets it and how long it lasts belong together. A flat tag list loses that.

## What the rules say (Comprehensive Rules, effective 2026-08-07, tools/agents/reference/)
- 603.1 triggered ability: "[When/Whenever/At] [trigger condition], [effect]". 602.1 activated: "[Cost]: [Effect]". 604.1 static: simply true; 604.2 it makes continuous effects active while the permanent is on the battlefield.
- 611.2a a continuous effect from a resolving spell or ability lasts as stated ("until end of turn"); with no stated duration it lasts until the end of the game. 514.2 "until end of turn" effects end in the cleanup step.
- 611.2c for a resolving spell or ability that changes characteristics, the set of affected objects is fixed when the effect begins; for a static ability it is re-checked all the time.
- 613.1f layer 6 applies ability-adding and ability-removing effects, so "gains first strike" is a layer 6 grant.
- 702.7 first strike is a static ability that changes the combat damage step.
- Forge default (PumpEffect.java lines 94 and 135): a Pump is removed at end of turn unless `Duration$ Permanent` or `Perpetual`. So Forge assumes end of turn where the CR default would be "end of game"; the duration must be read from the script or mtgish, never assumed from the CR.

## Model
A card has card-level tags (cardtype, supertype, type, kw, color, num) and zero or more clauses. A clause is one trigger/cost/condition leading to one effect. The roles come straight from the rules text above:

`trigger | cost | condition | verb | payload | affected | duration | limits`

- verb: grant, pump, destroy, exile, bounce, draw, create, counter ...
- payload: what is granted or changed (`first_strike`, `lifelink`, a stat change, a token)
- affected: who gets it (`target:creature`, `equipped`, `you_control:creature+counter:p1p1`, `self`)
- duration (from Forge `Duration$` and mtgish `Until*`): `duration:eot`, `duration:static` (static ability, while the source is on the battlefield), `duration:permanent`, `duration:perpetual`, `duration:until_leaves` (UntilHostLeavesPlay), `duration:while_control`
- limits: `sorcery_speed`, `once_per_turn`, `optional`

## Record format (TOON)
```
card: Wingbeat Warrior
tags: cardtype:creature type:bird type:soldier type:warrior flying evasion kw:morph color:white num:2
clauses[1]{id,trigger,cost,condition,verb,payload,affected,duration,limits}:
  c1,flip-up,,,grant,first_strike,target:creature,duration:eot,
links[3]{from,rel,to}:
  c1.trigger,requires,kw:morph
  c1.payload,lasts,c1.duration
  c1.affected,receives,c1.payload
```
The flat tags the current deck builder reads are derived from the clause: `flip-up`, `first_strike`, `pump_single`, `duration:eot`. Links are extra and optional; a reader that ignores them still works.

## Relations
| rel | meaning | example |
|---|---|---|
| requires | the clause only works if the card has this | `flip-up` requires `kw:morph` (megamorph counts as morph, CR 702.37b) |
| provides | the card makes something another card needs | `kw:outlast` provides `counters_plus` (CR 702.107) |
| lasts | a payload is bounded by a duration | grant lasts `duration:eot` |
| receives | the affected object gets the payload | target creature receives first_strike |
| scales_with | strength depends on a count | lifelink grant `scales_with` `scales:counters` |
| conditional_on | clause applies only under a condition | lifelink only if a +1/+1 counter is present |
| bounded_by | restricted by a limit | `bounded_by` `sorcery_speed` |

## Worked examples
1. **Wingbeat Warrior** (above). Forge: `T:Mode$ TurnFaceUp` gives trigger `flip-up`; `Execute$ TrigPump` leads to `DB$ Pump | KW$ First Strike | ValidTgts$ Creature` which gives verb grant, payload first_strike, affected target:creature; no `Duration$` on a Pump, so `duration:eot`. mtgish: this ability is missing from its output, so the clause comes from Forge only.
2. **Abzan Battle Priest.** Forge `S:Mode$ Continuous | Affected$ Creature.YouCtrl+counters_GE1_P1P1 | AddKeyword$ Lifelink`; mtgish `EachPermanentLayerEffect(And([IsCardtype(Creature), ControlledByAPlayer(You), HasACounterOfType(PTCounter(+1,+1))]), [AddAbility([Lifelink])])`.
```
clauses[1]{id,trigger,cost,condition,verb,payload,affected,duration,limits}:
  c1,static,,counter:p1p1,grant,lifelink,you_control:creature,duration:static,
links[2]{from,rel,to}:
  c1.payload,scales_with,scales:counters
  kw:outlast,provides,counters_plus
```
3. **Sparring Collar.** Forge `K:Equip`, `S:Continuous | AffectedDefined$ Equipped | AddKeyword$ First Strike`, `A:AB$ Attach | Cost$ R R`.
```
clauses[2]{id,trigger,cost,condition,verb,payload,affected,duration,limits}:
  c1,static,,,grant,first_strike,equipped,duration:static,
  c2,activated,mana:RR,,attach,self,you_control:creature,,sorcery_speed
links[2]{from,rel,to}:
  c1.affected,requires,kw:equip
  c2.verb,provides,c1.affected
```

## How to read each source into clauses
- **Forge:** `T:` line `Mode$` = trigger; `Execute$ X` points to the SVar that holds the effect; `A:` `AB$`/`SP$` with `Cost$` = cost; `S:` `Mode$ Continuous` = static (duration:static); `DB$ Pump | KW$` or `AddKeyword$` = payload; `ValidTgts$`/`Affected$`/`Defined$` = affected; `Duration$` = duration, with a Pump that has none defaulting to eot. Follow `SubAbility$` chains and link their clauses with `then`.
- **mtgish:** `TriggerA(...)`, `Activated(cost, ...)`, `PermanentLayerEffect`/`EachPermanentLayerEffect` = static, `CreatePermanentLayerEffectUntil(..., UntilEndOfTurn)` = a timed grant. mtgish sometimes drops an ability (Wingbeat Warrior), so merge with Forge instead of trusting it alone.
- **Keywords:** resolve once through KEYWORD_REFERENCE.toon and the CR rule number (KEYWORD_REMINDER_TEXT.toon), then add `kw:` plus qualifier tags; linked clauses (like flip-up for morph) come from the reminder text.

## Decisions (user, 2026-10-22)
1. Links are stored per card (H53). The full tag, relation and duration vocabulary is written during the cardlist run, not now.
2. Sub-ability chains: decided during the cardlist run (the user deferred rule gaps to the run).
3. Source order is Forge first, AILogic$ as a reference, mtgish as a less reliable second opinion (H54).
4. Still to list during the run: trigger vocabulary from Forge `Mode$` values and the eight gap groups from the card-logic test.

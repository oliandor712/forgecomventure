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
3. Source order: 1st card script, 2nd mtgish (less reliable), 3rd Forge AI (AILogic$ and forge-ai) as a reference (H54).
4. Still to list during the run: trigger vocabulary from Forge `Mode$` values and the eight gap groups from the card-logic test.

## How linking shows in the output (implemented in `tag_run.py`, 2026-10-22)
No hash. Linked tags are identified by group ids that are positional within one card:
- `k1, k2 ...` = the card's K: lines in order (a keyword plus its qualifier tags, e.g. `k2: kw:morph num:2 color:white`).
- `c0` = card-level tags (type-derived, loyalty, defense, transform). `c1, c2 ...` = the card's A:/S:/T:/R: lines in order, the same numbering as the `clauses` table.
- Tags in the same group came from the same script line, so they belong together (a token's type, count and colour; a cost and the effect it pays for). The flat `tags:` line is the union, for tools that only need the set.
- `links[]` rows connect things across groups using `group:tag` references or group ids: `c1:flip-up requires k2`, `c1:payload lasts c1:duration`, `c3:token_make conditional_on c3:effect:sacrifice`, `c1:mana_source produces c1:mana:white`.
- A card-wide id is `<card name>#<group id>` if needed across cards.
Limits: tags from the old `ability_tags` tagger (draw, token_make, removal ...) are card-level and carry no group yet; only tags created in this work are grouped. Relations in use: requires, provides, lasts, receives, produces, filters, pairs_with, conditional_on.

## Added 2026-10-22 (user notes on the sample)
- **Sub-ability groups:** a script line that chains steps (`SubAbility$`, `Execute$`, modal `Choices$`) gets one group per step: `c3` is the line, `c3.2`, `c3.3` the following steps. Target tags sit in the group of the step they belong to (Victimize: target_count:2, target_zone:graveyard, put_onto_battlefield, reanimate share `c1.2`; the sacrifice cost is `c1`).
- **Sacrifice outlet:** sacrificing a land is not an outlet (the old `sacrifice_outlet` is dropped); sacrificing a creature or other non-land is always `sacrifice_outlet`. "Sacrifice ... If you do, ..." marks the sacrifice as a cost (`cost:sacrifice cost_if_you_do`).
- **put_onto_battlefield** (with `put_from:<zone>`) means the card is put onto the battlefield without being cast: its mana cost and any cast triggers are skipped. Enter-the-battlefield triggers still happen (CR 603.6a). It is separate from `trigger:etb`, which is a trigger on entering. Confirmed by the user 2026-10-22.
- **tempo:** `tempo:+n` = cards added to your hand or battlefield minus cards removed when the ability resolves. Draws and cards put into hand or onto the battlefield from the library or graveyard count 1 each; tokens count 0.5 each; exiled-and-playable cards (impulse draw) count like draws; the spell card itself (instants and sorceries), sacrificed permanents and discarded cards count minus. Only positive values are tagged (tempo 0 and negative are not); `tempo:x` is tagged when an amount is a variable. Computed per ability on the line's group. Captain's Call +0.5 (three tokens = 1.5, minus the spell); Harrow none.
- **impulse_draw** carries `impulse_draw_count:<n|x>` and the same links as draw (count, duration, tempo). **restrict** is also tagged when an effect stops other creatures from blocking. **mana_amount** is always tagged on a mana source. `each_you_control` was dropped as redundant with `target_count` and `target_scope`.
- **draw_count / discard_count**, **enters_untapped**, **enters_tapped_conditional**, **loyalty_change** (renamed from loyalty_cost).

## Redundancy check (user order 2026-10-22: part of all future tag generation)
`tag_run.py` calls `redundancy(recs)` on every run and writes `tags/REDUNDANCY_CHECK.md`: a bare tag next to its valued form, two families on exactly the same cards, a family whose cards are a subset of another's (implied), a family with one value, values that always travel together. Findings are candidates: merge, drop, or whitelist in `REDUNDANCY_OK` / `VALUES_OK` with a reason. The full-cardlist run must keep this check, and a new tag family is not proposed for approval while it has an open finding against another proposed family.

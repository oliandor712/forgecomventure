# New ability-level tags for the mtg2llm gap record (for approval)

Written 2026-10-27. Source: the 35 rows still open in `MTG2LLM_GAPS.toon` after the hand pass. Each is a Forge effect, trigger or cost that `tag_extra.py` does not tag yet, so the renderer only sees a trigger or cost and cannot write the effect. Nothing is implemented; these are PROPOSED (H56) until you approve them. `NEW_TAGS_FOR_APPROVAL.md` is generated and stays as is; this page covers this batch only.

Redundancy check: each candidate was compared with `TAG_REFERENCE.md` and the approved list. Candidates an existing family already covers were dropped (table 3) and will reuse that family.

## 1. New tag families (7)

| Approve | Tag family | Meaning | Forge source | Cards (open rows) | Values |
|---|---|---|---|---|---|
| [ ] proposed | `mill_count` | how many cards are milled. Who is milled stays with the existing role tags `mill` / `self_mill`; this adds only the amount (same pattern as `scry_count`, `discard_count`) | `Mill` NumCards$ | Blight Titan, Barrowgoyf | mill_count:N, mill_count:x (x_is says what) |
| [ ] proposed | `flip_coin` | the effect flips a coin; the sub-effects of the winning and losing flip are the groups tagged `flip_win` / `flip_lose` | `FlipCoin`, WinSubAbility$ / LoseSubAbility$ | Creepy Doll, Volatile Rig | flip_coin; flip_win; flip_lose |
| [ ] proposed | `secret_choice` | a player chooses secretly, then the choices are revealed and compared | Secretly$ on `ChooseNumber` / `ChooseCard` | Wheel of Misfortune, Expert-Level Safe | secret_choice:number; secret_choice:card |
| [ ] proposed | `lose_game` | the effect makes a player lose the game (a state trigger on 0 counters is `trigger:state`, table 2) | `LosesGame` | Nine Lives | lose_game |
| [ ] proposed | `counter_remove` | removes counters as an effect, not a cost (`cost:remove_counters` is the cost). `remove:*` is not reused: that family means removing a permanent | `RemoveCounter` | Phantom Nantuko | counter_remove:N; counter_remove:all |
| [ ] proposed | `grant_type` | an effect gives a permanent an extra card or land type (all lands are also Forests); `grant_ability` covers abilities only | `Animate` / `Effect` AddType$ | Yavimaya, Cradle of Growth | grant_type:forest |
| [ ] proposed | `cost_energy` | the cost pays energy counters (the `cost` family has tap, mana, life, discard, sacrifice but no energy) | `PayEnergy<N>` in Cost$ | Aethertide Whale | cost_energy:N |

## 2. New values inside families you already approved (no new family)

| Family | New values | Forge source | Cards |
|---|---|---|---|
| `trigger` | trigger:damage_dealt | Mode$ DamageDone / DamageDoneOnce (combat only: the existing `trigger:combat_damage` is kept and used when CombatDamage$ True) | Barrowgoyf, Creepy Doll, Dissipation Field, Jaws, Jeskai Elder, Kediss, Sphere Grid, Toski, Volatile Rig (9) |
| `trigger` | trigger:blocks | Mode$ Blocks | Ashcoat of the Shadow Swarm |
| `trigger` | trigger:cycled | Mode$ Cycled | Magmakin Artillerist |
| `trigger` | trigger:counter_added | Mode$ CounterAddedOnce | Evolution Witness |
| `trigger` | trigger:mana_spent | Mode$ ManaExpend | Teapot Slinger |
| `trigger` | trigger:state | Mode$ Always (state trigger) | Nine Lives |
| `cost` | cost:energy (amount in `cost_energy`) | PayEnergy | Aethertide Whale |

## 3. Candidates dropped as redundant (existing tags reused)

| Candidate | Reuse instead | Cards |
|---|---|---|
| `incubate` | `token_make` + `token_type:incubator` + `counter_count:N` + `counter:p1p1` (an Incubator token is a token with counters) | Blight Titan |
| `grant_trigger` (AddTrigger) | `grant_ability:<kind>_trigger`, the approved family | Lord of Shatterskull Pass, Well Rested |
| `trigger:destroyed` | `trigger:dies` (Mode$ Destroyed on a creature) | Jaws, Relentless Predator |
| `trigger:discard_all` | `trigger:discard` + `trigger_filter:one_or_more` | Magmakin Artillerist |
| `bolster_trigger` | `bolster:N`; only the TrigPutCounter mapping is missing in `tag_extra.py` | Sandsteppe War Riders |
| `loot` | `discard_count:N` + `draw_count:N` in the same group | Jeskai Elder |
| `dig_until` | `look_top` + `take` cover most reveal-until effects; one card only, hand line instead | Ensnared by the Mara |

## 4. No tag (a parser or hand-line fix, nothing to approve)

Cleanup (Barrowgoyf, Sphinx's Tutelage, Ensnared by the Mara: structural, not an effect), VillainousChoice (Ensnared by the Mara), level ranges (Lord of Shatterskull Pass), empty saga chapters (Summon: Yojimbo), `forge_line:etbcounter` and `forge_line:partner_with` (Charred Graverobber, Phantom Nantuko, Chakram Retriever: keyword lines to map to the existing `kw:` / `counter` tags).

## 5. After approval

Add the branches to `tag_extra.py` (+ `DOC`), rerun `tag_run.py starter`, `tag_reports.py`, `mtg2llm.py scan`, and the gap check. Expected effect: most of the 35 open rows clear; the rest need hand lines. Log in `log-code-analyses.toon`.

Say "approve all" or mark rows. Unmarked rows stay proposed.

# Starter land picker and commander support: changelog (2026-10-27)

Scope: `tools/concordia/deckgen/` (starter builder, tags, commander support). Status of options and open questions is in `STARTER_BUILDER_CHANGES_2026-10-27.md`; this file lists what changed, in order, with the rule ids in `tools/agents/human_logic.toon`. Nothing live changed (no live decks, no `enemies.json`, no forge-core/game/ai). All builds are staged in `forge-gui/res/adventure/Concordia/staging_starters/`. Code is not committed.

## Tags
| Tag | Rule | Meaning | File |
|---|---|---|---|
| `mana_sink` | H96 | Repeatable activated ability with a mana-only cost and no tap. Reminder text ignored. Excluded: sacrifice, exile, discard, `{Q}`, "tap an untapped", pay-life costs; effects that grant keywords, transform, adapt, monstrosity, renown, regenerate; once-only and once-per-turn abilities. 1,185 cards, 6 lands. | `tag_extra.py` |
| `setup_card:<need>` | H98 | General tag, any archetype: a card that needs setup before it works. `setup_card:mana` (Dark Depths with `counter_remove`) counts as land utility only with 10 ramp pieces in the deck. | `tag_extra.py`, `starter_build.py` (`SETUP_MANA_RAMP`) |
| `restricted_to:<type>` | H99 | Mana only for X spells, or recursion of X cards. 63 cards, 16 lands. Haven of the Spirit Dragon = `restricted_to:dragon`. A land has utility only when the type is the commander's or an allowed tribe. | `tag_extra.py`, `starter_build.py` |

## Land picker (`starter_build.py`, `land_score`)
`1000*coverage + 100*utility - 150*colourless_penalty - 50*tempo_negative - 20*mana_filter - 10*tapped - 5*life - sacrifice_other + 0.02*power`, returned only with coverage or utility (H90, H91). Utility is `3*support`, zeroed by `tempo:negative`, an unpaid `setup_card:mana`, or an untyped `restricted_to`.
- H97: the staples warning is no longer printed or enforced by the starter builder (the tier builders still use it).
- H100: a colourless-only land gets -150 unless the deck has `{C}` pips or the land has its own synergy (Drownyard Temple: recursion).
- H101: colourless is the sixth colour. `{C}` pips of the spells and commander are counted like colour pips; colourless-only lands are capped at the `{C}` pip share times 37 lands, at least the largest `{C}` cost of one card, minus colourless rocks.
- H102: a `{C}` spell is picked only if colourless sources (4 assumed lands plus rocks) / 37 >= 0.8 x the `{C}` share of all pips, the rule `power_scorer.check_tier` applies to coloured sources. The 14-source floor is skipped. A first placeholder (4 sources per pip) was discarded.
- `synergy.py`: `big_impact` lets a Land through the mana-dump test only with `mana_sink`.

## Commander support (`commander_support.py`, `t1_plan.py`)
- H103: `token_scales:<Y>` profile item when the commander's token count is tied to Y ("for each / per / number of Y" next to "create"). A card supports it with `token_make` and (it is a Y, or its text counts Y). When present, plain `token` is dropped from the profile. `t1_plan.py` reads either item. Captain America, Liberator: `attack, etb_self, scales:Equipment, token_scales:Equipment, tribe:Soldier`.

## Test builds (W starter, Captain America, Liberator; lifegain + tokens)
| Build | Power | Supporting | Creatures | Nonbasic lands | Note |
|---|---|---|---|---|---|
| r3 | 28.5 | 37/63 | 34 | Urza's Saga, Plaza of Heroes, Treasure Vault, Vesuva, Drownyard Temple, Witch's Clinic | Kozilek's Command in |
| r4 | 28.5 | 37/63 | 34 | Urza's Saga, Plaza of Heroes, Vesuva, Drownyard Temple, Buried Ruin, Abundant Countryside | pip-share cap; Kozilek's Command in |
| r5 | 27.7 | 23/63 | 31 | Plaza of Heroes, Vesuva, Drownyard Temple, Buried Ruin, Haunted Fengraf, Lazotep Quarry | token_scales; Kozilek's Command out |
| r6 | 27.7 | 23/63 | 31 | same as r5 | colourless sized as a colour |

Kozilek's Command was in r3/r4 only because its `token_make` (0/1 Eldrazi Spawn for a target player) passed the plain `token` test. It leaves in r5/r6 through H103, not through the colourless gate.

## Not verified
- Whether 23/63 supporting cards is acceptable, or plain token makers should count as weaker support.
- Soldier theme listed in r4's "themes unlocked" but not in r5/r6; cause unchecked.
- The colourless gate is lenient (about 1 source covers a `{C}{C}` card among ~60 coloured pips) and its effect alone was not tested; 37 lands is hard-coded.
- `restricted_to` gates lands only; 47 non-land tagged cards not reviewed.
- Other four colour starters not rebuilt; `review-apply` guard, ArcMind token flow and H85 key-card narrowing still open.
- `TAG_REFERENCE.md` does not list `setup_card` or `restricted_to` until a tagged card is in a starter run.

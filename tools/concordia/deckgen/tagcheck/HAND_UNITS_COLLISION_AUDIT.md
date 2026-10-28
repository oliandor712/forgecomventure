# hand_units.json collision audit (2026-10-27, read-only)

Method: 85 pattern keys are shared by 2+ pool cards. For each hit card the hand line was compared with the card's Oracle text (numbers normalised to N, card name to "this"). 20 keys are fully identical (class a, harmless). 65 have at least one differing hit card (class b). The class-b list was triaged from the first 2-3 differing cards per key, not every hit card: the "N differ" counts are matcher counts and include wording noise on multi-ability cards. Nothing in hand_units.json or the tags was changed. Every tag below is PROPOSED only (H56).

## 1. Keyword costs baked into one card's line (delete the line or key by card; the generic keyword render already knows the real cost)
Flashback {5}{B}{B} (22 hit, others cost 3B / 7BBB), Kicker {5}{R}, Cycling {R} / {3}{G} / {2}{W}, Escape {3}{B}{B} + four cards (others five / three cards), Mutate {1}{U}, Blitz {2}{R}{R}, Emerge {5}{G}{G} (Decimator of the Provinces is {6}{G}{G}{G}), Level up {R}, Channel {3}{B} (Takenuma, abandoned).
PROPOSED: a cost value on the keyword tag (`flashback_cost:...`, `escape_exile:N`) so pattern() stops hiding it, or delete these lines.

## 2. Number or count abstracted by N (same shape, different number)
- you get six {E}: other cards give two. PROPOSED `gain_energy:N`.
- Look at the top six (Peer Through Depths = five; Uncovered Clues = four and "up to two"; Silundi Vision similar). PROPOSED `look_top:N` plus `select:up_to_N`.
- Devoted Paladin +1/+1 vs line +2/+1. Black Waltz No. 3 deals 2 vs line 1. Ash Zealot deals 3 vs line 4. Barbed Wire / Copper Tablet 1 damage to that player vs line 4 damage to you (scope also differs). Archive Trap mills 13, Mind Sculpt 7 vs line mill 2 repeat (Sphinx's Tutelage). Savvy Hunter sacrifice two Foods vs three. Rooftop Percher exile up to two vs one. Seller of Songbirds / Soul of Migration 1/1 Bird vs 3/4 (Raid). Urbis Protector 4/4 Angel vs 3/3.
PROPOSED: `damage_amount:N`, `mill_count:N`, `sac_count:N`, `token_pt:P/T` as values in the hand-line key or the render, not abstracted.

## 3. Missing condition, scope or marker (real tag gaps, the peer's examples are all confirmed)
- Mold Shambler / Woodfall Primus: line says "if it was kicked"; Woodfall Primus has no kicker. Missing `condition:kicked`.
- Archfiend of Despair / Witch Hunt: line is the Witch Hunt "target opponent chosen at random gains control"; Archfiend is a different ability (loses life equal to life lost). Missing `target_scope:random_opponent`, and the key is too generic for two unrelated abilities.
- Eiganjo / Gideon's Memorial: Eiganjo channel deals 4 damage to an attacking/blocking creature; Gideon's Memorial's channel is a different effect. Missing channel effect detail (`channel` plus effect tags are collapsed).
- Anax and Cymede / Decimator: line is a cast trigger "When you cast this spell, creatures get +2/+2 and trample"; Anax is Heroic ("whenever you cast a spell that targets it", +1/+1). Missing `trigger:cast_self` vs `trigger:cast_targeting_self`.
- Teller of Tales: "Spirit or Arcane spell", "tap or untap" vs line "any spell, untap". Missing spell-type filter and tap-or-untap choice.
- Ancestor Dragon: "one or more creatures you control attack" vs line "this creature attacks" (trigger scope).
- Drannith Stinger: "cycle another card" vs "cycle this card".
- Urbis Protector / Shuri's Fabricator / T'Challa: line has an intervening-if ("opponent controls more creatures / lands"); these cards have none. Missing `condition:opp_more_creatures|lands`.
- Oyobi: cast a Spirit or Arcane spell vs line cast from graveyard. Magda: Dwarf becomes tapped vs sacrifice Food.
- Eivor, Rampant Frogantua vs Barrowgoyf: mill is mandatory vs "you may". Torgaar: "may sacrifice any number" vs mandatory sacrifice. Missing `optional`.
- Quantum Riddler: replacement ("draw that many plus one") vs line "each draws a card". Iron Mastiff: roll d20 vs fixed 6 damage (Lord of Shatterskull Pass line). Missing `roll_die`.
- Banshee of the Dread Choir / Blazing Specter: "that player discards" vs line "you may draw, then discard" (Jeskai Elder): direction of discard.
- Felidar Sovereign / Liliana's Contract: upkeep win with different condition (life 40 vs five colours).
- Circle of Flame / Falkenrath Perforator: attacker filter (without flying, attacks you) vs any creature.
- City on Fire / Curse of Bloodletting: "source you control" vs "source ... enchanted player".
- Mana Bloom / Oni of Wild Places: upkeep return an artifact vs a red creature (type filter).
- Elvish Archivist / Tocasia's Welcome: artifact creatures vs artifacts / mana value 3 or less.
- Niv-Mizzet, Dracogenius vs Ophidian Eye: "a player" vs "an opponent", enchanted vs self.
- Amarant Coral / Gargantos vs Kediss: "commander" vs "opponent" subject.
- Ashcoat of the Shadow Swarm / Freelance Muscle: Rats get +X/+X vs self +X/+X with a different X.
- Clawing Torment / Night of Souls' Betrayal: enchanted permanent vs all creatures.
- Field of Ruin: the line omits "each player searches for a basic land".

## 4. Line is one card's text but the key is a generic fragment (the real collision risk; re-key by card or delete)
Likely from the recent hand pass (key matches dozens of unrelated cards): "Each land is a Forest" (Yavimaya; 15 hit, 15 differ, Auras and lands), "Enchanted creature has flying and Sacrifice a creature..." (30/29), Sphere Grid combat-damage counter (31/28), Jaws "noncreature artifact sacrificed" (13/12, matches plain each-opponent burn like Boltwave), Nine Lives incarnation-counter prevent and upkeep 4 damage lines, Muster the Departed populate (9/8), Sphinx's Tutelage (6/5), Jeskai Elder (25/20), Saga "II — Draw a card" / "II — Each opponent discards" / "II — counter on up to two" (the chapter text sits under a key with no effect detail), "Cartouche return", "Cast a noncreature spell, 1 damage" , "differently named" Sandsteppe bolster (15/14), First strike during your turn (19/17, mostly wording noise), lifelink Aura lines (7/6, 5/3), Soulbond (8/7).
PROPOSED: re-key these by card (e.g. `Card Name|pattern`), or delete, on the user's word. Re-keying needs a loader change in mtg2llm (not yet done).

## Next (needs the user's word)
1. Delete or re-key section 4 lines (about 20 keys). 2. Delete section 1 cost lines. 3. Approve section 2/3 value and condition tags (go through NEW_TAGS_FOR_APPROVAL.md).

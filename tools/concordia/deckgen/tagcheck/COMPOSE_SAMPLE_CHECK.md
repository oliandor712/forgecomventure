# MTG2LLM composed-line check

Each entry is one ability that the renderer built by composing mined parts (no exact rule existed for it). Compare the **Composed** line with the card's Oracle text for that ability. Fill **Verdict** (ok / wrong / unsure) and **Note** (what is off: wrong joiner, wrong number, missing clause, odd grammar, wrong target).
50 random abilities from the 1000-card run; pre-6th-only cards excluded; trigger-only lines with an {effect} placeholder left out.

Tally: ok ___ / wrong ___ / unsure ___

---

## 1. Warren Instigator (unit c1)

- **Tags:** put_onto_battlefield from_zone:hand controller:you
- **Composed:** Put {filter} from your hand onto the battlefield under your control.
- **Oracle:** Double strike / Whenever Warren Instigator deals damage to an opponent, you may put a Goblin creature card from your hand onto the battlefield.
- **Verdict:** 
- **Note:** 


## 2. Ley Druid (unit x)

- **Tags:** untap
- **Composed:** Untap this permanent.
- **Oracle:** {T}: Untap target land.
- **Verdict:** 
- **Note:** 


## 3. Call of the Full Moon (unit c2)

- **Tags:** trigger:upkeep effect:sacrifice
- **Composed:** At the beginning of your upkeep, sacrifice this enchantment.
- **Oracle:** Enchant creature / Enchanted creature gets +3/+2 and has trample. (It can deal excess combat damage to the player or planeswalker it's attacking.) / At the beginning of each upkeep, if a player cast two or more spells last turn, sacrifice Call of the Full Moon.
- **Verdict:** 
- **Note:** 


## 4. Icatian Priest (unit c1)

- **Tags:** cost_mana:1ww target_count:one target_type:creature pump_amount:+1/+1 duration:eot pump_single
- **Composed:** {1}{W}{W}: Target creature gets +1/+1 until end of turn.
- **Oracle:** {1}{W}{W}: Target creature gets +1/+1 until end of turn.
- **Verdict:** 
- **Note:** 


## 5. Fiery Hellhound (unit c1)

- **Tags:** cost_mana:r pump_amount:+1/+0 duration:eot
- **Composed:** {R}: This creature gets +1/+0 until end of turn.
- **Oracle:** {R}: Fiery Hellhound gets +1/+0 until end of turn.
- **Verdict:** 
- **Note:** 


## 6. Incubator Drone (unit k1)

- **Tags:** kw:devoid
- **Composed:** Devoid
- **Oracle:** Devoid (This card has no color.) / When Incubator Drone enters, create a 1/1 colorless Eldrazi Scion creature token. It has "Sacrifice this creature: Add {C}."
- **Verdict:** 
- **Note:** 


## 7. Flourishing Fox (unit k1)

- **Tags:** kw:cycling num:1
- **Composed:** Cycling {1}
- **Oracle:** Whenever you cycle another card, put a +1/+1 counter on Flourishing Fox. / Cycling {1} ({1}, Discard this card: Draw a card.)
- **Verdict:** 
- **Note:** 


## 8. Angelic Page (unit c1)

- **Tags:** cost:tap target_count:one target_type:creature target_filter:attacking target_filter:blocking pump_amount:+1/+1 duration:eot pump_single
- **Composed:** {T}: Target attacking gets +1/+1 until end of turn.
- **Oracle:** Flying / {T}: Target attacking or blocking creature gets +1/+1 until end of turn.
- **Verdict:** 
- **Note:** 


## 9. Korlash, Heir to Blackblade (unit c2)

- **Tags:** cost_mana:1b regenerate
- **Composed:** {1}{B}: Regenerate this creature.
- **Oracle:** Korlash, Heir to Blackblade's power and toughness are each equal to the number of Swamps you control. / {1}{B}: Regenerate Korlash. / Grandeur — Discard another card named Korlash, Heir to Blackblade: Search your library for up to two Swamp cards, put them onto the battlefield tapped, then shuffle.
- **Verdict:** 
- **Note:** 


## 10. Feral Thallid (unit c2)

- **Tags:** cost:remove_counters regenerate
- **Composed:** Remove a fade counter: Regenerate this creature.
- **Oracle:** At the beginning of your upkeep, put a spore counter on Feral Thallid. / Remove three spore counters from Feral Thallid: Regenerate Feral Thallid.
- **Verdict:** 
- **Note:** 


## 11. Krumar Bond-Kin (unit k1)

- **Tags:** kw:morph num:4 color:black
- **Composed:** Morph {4}{B}
- **Oracle:** Morph {4}{B} (You may cast this card face down as a 2/2 creature for {3}. Turn it face up any time for its morph cost.)
- **Verdict:** 
- **Note:** 


## 12. Esika's Chariot (unit k1)

- **Tags:** kw:crew num:4
- **Composed:** Crew 4
- **Oracle:** When Esika's Chariot enters, create two 2/2 green Cat creature tokens. / Whenever Esika's Chariot attacks, create a token that's a copy of target token you control. / Crew 4
- **Verdict:** 
- **Note:** 


## 13. Merrow Levitator (unit c2)

- **Tags:** trigger:spell_cast optional
- **Composed:** Whenever you cast a spell, you may N.
- **Oracle:** {T}: Target creature gains flying until end of turn. / Whenever you cast a blue spell, you may untap Merrow Levitator.
- **Verdict:** 
- **Note:** 


## 14. Mardu Blazebringer (unit x)

- **Tags:** sacrifice
- **Composed:** Sacrifice this permanent.
- **Oracle:** When Mardu Blazebringer attacks or blocks, sacrifice it at end of combat.
- **Verdict:** 
- **Note:** 


## 15. Verdigris (unit c1)

- **Tags:** target_count:one target_type:artifact remove:destroy
- **Composed:** Destroy target artifact or enchantment.
- **Oracle:** Destroy target artifact.
- **Verdict:** 
- **Note:** 


## 16. Sapphire Collector (unit k1)

- **Tags:** kw:prowess
- **Composed:** Prowess
- **Oracle:** Prowess / When you cast your second noncreature spell in a turn, conjure a card named Mox Sapphire into your hand. This ability triggers only once. / {2}{U}: Target instant or sorcery card in your graveyard gains flashback until end of turn. The flashback cost is equal to its mana cost.
- **Verdict:** 
- **Note:** 


## 17. Mutated Cultist (unit k1)

- **Tags:** kw:devoid
- **Composed:** Devoid
- **Oracle:** Devoid / When you cast this spell, remove all counters from up to one target permanent or opponent. The next spell you cast this turn costs {1} less to cast for each counter removed this way. / Deathtouch
- **Verdict:** 
- **Note:** 


## 18. Tamiyo's Journal (unit c1)

- **Tags:** trigger:upkeep investigate
- **Composed:** At the beginning of your upkeep, add {U} or {B}.
- **Oracle:** At the beginning of your upkeep, investigate. (Create a Clue token. It's an artifact with "{2}, Sacrifice this token: Draw a card.") / {T}, Sacrifice three Clues: Search your library for a card, put that card into your hand, then shuffle.
- **Verdict:** 
- **Note:** 


## 19. Skittering Precursor (unit k1)

- **Tags:** kw:devoid
- **Composed:** Devoid
- **Oracle:** Devoid (This card has no color.) / Menace / Whenever you sacrifice a nontoken permanent, create a 0/1 colorless Eldrazi Spawn creature token with "Sacrifice this creature: Add {C}."
- **Verdict:** 
- **Note:** 


## 20. Serpent of the Pass (unit c2)

- **Tags:** cost_reduce duration:static
- **Composed:** {Spells} cost {N} less to cast.
- **Oracle:** If there are three or more Lesson cards in your graveyard, you may cast this spell as though it had flash. / This spell costs {1} less to cast for each noncreature, nonland card in your graveyard.
- **Verdict:** 
- **Note:** 


## 21. Seize the Day (unit x)

- **Tags:** untap
- **Composed:** Untap this permanent.
- **Oracle:** Untap target creature. After this main phase, there is an additional combat phase followed by an additional main phase. / Flashback {2}{R} (You may cast this card from your graveyard for its flashback cost. Then exile it.)
- **Verdict:** 
- **Note:** 


## 22. Solar Blast (unit k1)

- **Tags:** kw:cycling num:1 color:red
- **Composed:** Cycling {1}{R}
- **Oracle:** Solar Blast deals 3 damage to any target. / Cycling {1}{R}{R} ({1}{R}{R}, Discard this card: Draw a card.) / When you cycle Solar Blast, you may have it deal 1 damage to any target.
- **Verdict:** 
- **Note:** 


## 23. Avengers Quinjet (unit k2)

- **Tags:** kw:crew num:3
- **Composed:** Crew 3
- **Oracle:** Flying / Whenever this Vehicle enters or attacks, choose one — / • You may put a Hero creature card from your hand onto the battlefield. / • Return target Hero creature card from your graveyard to your hand. / Crew 3
- **Verdict:** 
- **Note:** 


## 24. Unstoppable Ogre (unit c1)

- **Tags:** trigger:etb duration:eot pump_single trigger_scope:self target_count:one target_type:creature restrict_kind:cant_block duration:eot
- **Composed:** When this creature enters, target creature can't block this turn.
- **Oracle:** When Unstoppable Ogre enters, target creature can't block this turn.
- **Verdict:** 
- **Note:** 


## 25. Debtors' Knell (unit c1)

- **Tags:** trigger:upkeep target_count:one target_type:creature target_zone:graveyard put_onto_battlefield from_zone:graveyard controller:you
- **Composed:** At the beginning of your upkeep, put target creature card from your graveyard onto the battlefield under your control.
- **Oracle:** ({W/B} can be paid with either {W} or {B}.) / At the beginning of your upkeep, put target creature card from a graveyard onto the battlefield under your control.
- **Verdict:** 
- **Note:** 


## 26. Boneyard Lurker (unit c1)

- **Tags:** target_count:one target_type:permanent target_scope:you_control target_zone:graveyard return from_zone:graveyard to_zone:hand
- **Composed:** Return target permanent card from your graveyard to your hand.
- **Oracle:** Mutate {2}{B/G}{B/G} (If you cast this spell for its mutate cost, put it over or under target non-Human creature you own. They mutate into the creature on top plus all abilities from under it.) / Whenever this creature mutates, return target permanent card from your graveyard to your hand.
- **Verdict:** 
- **Note:** 


## 27. Ominous Seas (unit k1)

- **Tags:** kw:cycling num:2
- **Composed:** Cycling {2}
- **Oracle:** Whenever you draw a card, put a foreshadow counter on Ominous Seas. / Remove eight foreshadow counters from Ominous Seas: Create an 8/8 blue Kraken creature token. / Cycling {2} ({2}, Discard this card: Draw a card.)
- **Verdict:** 
- **Note:** 


## 28. March Toward Perfection (unit c1)

- **Tags:** return from_zone:stack to_zone:battlefield put_onto_battlefield controller:you
- **Composed:** Return {card} from the stack to the battlefield under your control.
- **Oracle:** You get a boon with "When you cast your next Phyrexian creature spell, that creature enters with an additional +1/+1 counter and deathtouch counter on it." / Draft a card from March Toward Perfection's spellbook.
- **Verdict:** 
- **Note:** 


## 29. Suture Spirit (unit c1)

- **Tags:** target_count:one target_type:creature regenerate
- **Composed:** Regenerate target creature.
- **Oracle:** Flying / {W/B}{W/B}{W/B}: Regenerate target creature.
- **Verdict:** 
- **Note:** 


## 30. Pooling Venom (unit k1)

- **Tags:** kw:enchant target_type:land
- **Composed:** Enchant land
- **Oracle:** Enchant land / Whenever enchanted land becomes tapped, its controller loses 2 life. / {3}{B}: Destroy enchanted land.
- **Verdict:** 
- **Note:** 


## 31. Furnace Hellkite (unit c1)

- **Tags:** cost_mana:r pump_amount:+1/+0 duration:eot
- **Composed:** {R}: This creature gets +1/+0 until end of turn.
- **Oracle:** Affinity for artifacts (This spell costs {1} less to cast for each artifact you control.) / Flying / {R}: Furnace Hellkite gets +1/+0 until end of turn.
- **Verdict:** 
- **Note:** 


## 32. Elven Raft-Steerer (unit x)

- **Tags:** untap
- **Composed:** Untap this permanent.
- **Oracle:** Landfall — Whenever a land you control enters, choose one — / • Tap target creature an opponent controls. / • Untap target creature you control.
- **Verdict:** 
- **Note:** 


## 33. Indatha Triome (unit k1)

- **Tags:** kw:cycling num:3
- **Composed:** Cycling {3}
- **Oracle:** ({T}: Add {W}, {B}, or {G}.) / Indatha Triome enters tapped. / Cycling {3} ({3}, Discard this card: Draw a card.)
- **Verdict:** 
- **Note:** 


## 34. Dauthi Warlord (unit k1)

- **Tags:** kw:shadow
- **Composed:** Shadow
- **Oracle:** Shadow (This creature can block or be blocked by only creatures with shadow.) / Dauthi Warlord's power is equal to the number of creatures with shadow on the battlefield.
- **Verdict:** 
- **Note:** 


## 35. Blighted Burgeoning (unit k1)

- **Tags:** kw:enchant target_type:land
- **Composed:** Enchant land
- **Oracle:** Enchant land / When Blighted Burgeoning enters, incubate 2. (Create an Incubator token with two +1/+1 counters on it and "{2}: Transform this token." It transforms into a 0/0 Phyrexian artifact creature.) / Whenever enchanted land is tapped for mana, its controller adds an additional one mana of any color.
- **Verdict:** 
- **Note:** 


## 36. Agent of Atlas (unit k1)

- **Tags:** kw:prowess
- **Composed:** Prowess
- **Oracle:** Prowess (Whenever you cast a noncreature spell, this creature gets +1/+1 until end of turn.)
- **Verdict:** 
- **Note:** 


## 37. Conqueror's Foothold (unit k1)

- **Tags:** kw:crew num:4
- **Composed:** Crew 4
- **Oracle:** When Conqueror's Galleon attacks, exile it at end of combat, then return it to the battlefield transformed under your control. / Crew 4 (Tap any number of creatures you control with total power 4 or more: This Vehicle becomes an artifact creature until end of turn.)
- **Verdict:** 
- **Note:** 


## 38. Ghitu Embercoiler (unit k1)

- **Tags:** kw:prowess
- **Composed:** Prowess
- **Oracle:** Prowess / At the beginning of your first main phase, you may discard a card. If you do, seek a card with greater mana value and exile it. Until the end of your next turn, you may play the exiled card.
- **Verdict:** 
- **Note:** 


## 39. Frenzied Fugue (unit k1)

- **Tags:** kw:enchant target_type:permanent
- **Composed:** Enchant permanent
- **Oracle:** Enchant permanent / When Frenzied Fugue enters or at the beginning of your upkeep, gain control of enchanted permanent until end of turn. Untap that permanent. It gains haste until end of turn.
- **Verdict:** 
- **Note:** 


## 40. Maelstrom Archangel (unit c1)

- **Tags:** optional cast_free
- **Composed:** You may cast {N card} without paying its mana cost.
- **Oracle:** Flying / Whenever Maelstrom Archangel deals combat damage to a player, you may cast a spell from your hand without paying its mana cost.
- **Verdict:** 
- **Note:** 


## 41. I Am Duskmourn (unit c1)

- **Tags:** optional cast_free
- **Composed:** You may cast {N card} without paying its mana cost.
- **Oracle:** (An ongoing scheme remains face up until it's abandoned.) / At the beginning of your end step, you may cast a spell from your hand without paying its mana cost. If you do, abandon this scheme.
- **Verdict:** 
- **Note:** 


## 42. Stormcatch Mentor (unit k2)

- **Tags:** kw:prowess
- **Composed:** Prowess
- **Oracle:** Haste / Prowess (Whenever you cast a noncreature spell, this creature gets +1/+1 until end of turn.) / Instant and sorcery spells you cast cost {1} less to cast.
- **Verdict:** 
- **Note:** 


## 43. Wave-Wing Elemental (unit c1)

- **Tags:** trigger:etb duration:eot trigger_scope:any trigger_filter:you_control trigger_filter:land pump_amount:+2/+2
- **Composed:** Whenever a land you control enters, this creature gets +2/+2 until end of turn.
- **Oracle:** Flying / Landfall — Whenever a land you control enters, Wave-Wing Elemental gets +2/+2 until end of turn.
- **Verdict:** 
- **Note:** 


## 44. Death Ward (unit c1)

- **Tags:** target_count:one target_type:creature regenerate
- **Composed:** Regenerate target creature.
- **Oracle:** Regenerate target creature.
- **Verdict:** 
- **Note:** 


## 45. Archangel Avacyn (unit c1)

- **Tags:** trigger:etb duration:eot indestructible trigger_scope:self target_count:all target_type:creature target_scope:you_control duration:eot grant_kw:indestructible
- **Composed:** When this creature enters, each creature you control gains indestructible.
- **Oracle:** Flash / Flying, vigilance / When Archangel Avacyn enters, creatures you control gain indestructible until end of turn. / When a non-Angel creature you control dies, transform Archangel Avacyn at the beginning of the next upkeep.
- **Verdict:** 
- **Note:** 


## 46. Rooting Moloch (unit k1)

- **Tags:** kw:cycling num:2
- **Composed:** Cycling {2}
- **Oracle:** When Rooting Moloch enters, exile target card with a cycling ability from your graveyard. Until the end of your next turn, you may play that card. / Cycling {2} ({2}, Discard this card: Draw a card.)
- **Verdict:** 
- **Note:** 


## 47. War Elemental (unit c1)

- **Tags:** trigger:etb trigger_scope:self effect:sacrifice
- **Composed:** When this creature enters, sacrifice this enchantment.
- **Oracle:** When War Elemental enters, sacrifice it unless an opponent was dealt damage this turn. / Whenever an opponent is dealt damage, put that many +1/+1 counters on War Elemental.
- **Verdict:** 
- **Note:** 


## 48. Enigma Eidolon (unit c2)

- **Tags:** trigger:spell_cast optional return from_zone:graveyard to_zone:hand
- **Composed:** Whenever you cast a spell, you may return it from your graveyard to your hand.
- **Oracle:** {U}, Sacrifice Enigma Eidolon: Target player mills three cards. / Whenever you cast a multicolored spell, you may return Enigma Eidolon from your graveyard to your hand.
- **Verdict:** 
- **Note:** 


## 49. Blot Out (unit c1)

- **Tags:** target_count:one target_type:opponent remove:exile
- **Composed:** Exile target opponent.
- **Oracle:** Target opponent exiles a creature or planeswalker they control with the greatest mana value among creatures and planeswalkers they control.
- **Verdict:** 
- **Note:** 


## 50. Bedlam Reveler (unit k1)

- **Tags:** kw:prowess
- **Composed:** Prowess
- **Oracle:** This spell costs {1} less to cast for each instant and sorcery card in your graveyard. / Prowess / When Bedlam Reveler enters, discard your hand, then draw three cards.
- **Verdict:** 
- **Note:** 


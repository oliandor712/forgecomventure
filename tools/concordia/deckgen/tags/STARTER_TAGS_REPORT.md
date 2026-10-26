# Starter deck tagging run: report

10 decks, 571 distinct cards, 571 tagged, 0 with no script (none).

## Most common tags

cardtype:creature 296, target_count:one 202, trigger:etb 179, trigger_scope:self 167, token_make 162, target_type:creature 143, draw 124, token_count:1 98, tempo:+1 97, cardtype:instant 95, mana_source 79, token_color:colorless 79, type:human 74, target_scope:you_control 73, tempo:+0.5 73, colorless_card 71, token_cardtype:artifact 71, cardtype:artifact 69, cost:tap 67, cardtype:sorcery 66, lifegain 66, draw_count:1 65, artifact_token 59, token_pt:1/1 58, damage 53, duration:eot 53, cost:sacrifice 50, from_zone:graveyard 50, duration:static 48, trigger:dies 44, supertype:legendary 42, kw:flying 41, put_onto_battlefield 40, target_zone:graveyard 40, trigger_zone:graveyard 40, trigger_filter:you_control 40, optional 40, cardtype:enchantment 40, return 37, to_zone:hand 37

## Trigger types seen in clauses

spell 162, etb_self 154, activated 125, static 67, dies_self 25, spell_cast 22, etb_other 19, attacks 17, replacement 17, phase 15, dies_other 14, combat_damage 6, leaves_self 6, attackersdeclared 5, changeszoneall 4, gain_life 3, damagedoneonce 2, sacrificed 2, cycled 2, discarded 1, counteraddedonce 1, mutates 1, becomestarget 1, attackerunblocked 1, spellcastorcopy 1, lifelost 1, damage 1, taps 1, blocked 1, discardedall 1

## Most common verbs (script API)

token 87, changezone 71, draw 55, static_continuous 45, mana 36, dealdamage 30, destroy 22, putcounter 15, pump 15, loselife+gainlife 14, charm 14, pumpall 13, replace_moved 12, static_reducecost 11, draw+loselife 9, changezone+token 8, mill 6, changezoneall 6, draw+token 6, gainlife 6, draw+discard 6, destroy+token 5, discard 4, changezone+changezone 4, damageall 4, dealdamage+gainlife 3, effect 3, immediatetrigger 3, static_cantblockby 3, pump+fight 3

## Cards with no ability tag beyond type, keyword and cost tags (17)

Typhoid Rats, Thornweald Archer, Deadly Recluse, Ambush Viper, Leatherback Baloth, Tajuru Pathwarden, Gigantosaurus, Colossal Dreadmaw, Kalonian Tusker, Alpine Grizzly, Magnigoth Sentry, Brazen Scourge, Savannah Lions, Fencing Ace, Aven Squire, Skyhunter Skirmisher, Leonin Skyhunter


## Cross-check layer (Oracle gap filler, keyword reference/CR, Forge AI)

Cards where the cross-check added tags: 60; tags added in total: 65 (life_loss 27, fight 8, trigger:combat_damage 6, trigger:etb 3, untap 3, trigger:end_step 3, token_make 2, trigger:dies 2, cost:mana 2, cost:discard 1, cost:life 1, discard 1, trigger:attacks 1, surveil 1, trigger:beginning_of_combat 1, damage 1, trigger:discard 1, remove:destroy 1).

Cards with an ai_logic tag: 38.

Flags (Oracle line and script tags disagree, nothing added): 28 on 28 cards.

- Bucknard's Everfull Purse: extra? steal: no Oracle phrase supports it
- Return of the Wildspeaker: extra? draw: no Oracle phrase supports it
- Rishkar's Expertise: extra? draw: no Oracle phrase supports it
- Pulse of Murasa: bounce: Oracle line says it, script tags lack bounce
- Cache Grab: extra? mill: no Oracle phrase supports it
- The Binding of the Titans: extra? mill: no Oracle phrase supports it
- Town Greeter: extra? mill: no Oracle phrase supports it
- Gate to the Afterlife: draw: Oracle line says it, script tags lack draw
- Spider Food: extra? remove:destroy: no Oracle phrase supports it
- Ghost Quarter: extra? tutor: no Oracle phrase supports it
- Herald's Horn: extra? tutor: no Oracle phrase supports it
- Kinetic Augur: extra? draw: no Oracle phrase supports it
- Starforged Sword: extra? draw: no Oracle phrase supports it
- Barrin, Tolarian Archmage: extra? bounce: no Oracle phrase supports it
- Mindcrank: extra? mill: no Oracle phrase supports it
- Laboratory Maniac: draw: Oracle line says it, script tags lack draw
- Fact or Fiction: extra? tutor: no Oracle phrase supports it
- Disruptor of Currents: extra? bounce: no Oracle phrase supports it
- Filter Out: extra? bounce: no Oracle phrase supports it
- Arcanis the Omnipotent: extra? bounce: no Oracle phrase supports it
- Time of Ice: extra? bounce: no Oracle phrase supports it
- Psychic Spiral: extra? mill: no Oracle phrase supports it
- Bill Ferny, Bree Swindler: extra? steal: no Oracle phrase supports it
- Daring Waverider: exile_effect: Oracle line says it, script tags lack exile
- Loran of the Third Path: extra? remove:destroy: no Oracle phrase supports it
- Crumb and Get It: extra? draw: no Oracle phrase supports it
- Commander Sofia Daguerre: extra? remove:destroy: no Oracle phrase supports it
- Sandstone Oracle: extra? draw: no Oracle phrase supports it

## Double check of this run

- Structure checks on 571 records (no duplicate or upper-case tags; every supertype and card type in the Types line has its tag; every K: line has a kw: or forge_line: tag): K: line without kw tag: Paradise Plume (etbreplacement), Herald's Horn (etbreplacement), Cloud Key (etbreplacement)
- Comparison with the original run (before the cross-check layer, checked 2026-10-22 after the self-sacrifice fix): 80 tags added on 80 cards changed (22 ai_logic, 58 other tags on 51 cards); 14 `sacrifice_outlet` tags removed (self-sacrifice is not an outlet, user 2026-10-22); nothing else removed or changed.
- By hand: every cross-check addition on the sample cards and about 40 others was read against the Oracle text (see `STARTER_TAGS_SAMPLE.md`); the findings are listed under 'Known problems' below.

## Known problems (found by the double check; tags NOT changed, your call)

- `tutor` is wrongly tagged on cards that look at the top card or split piles (Herald's Horn, Fact or Fiction): the older tagger treats 'put into your hand' as a tutor; the cross-check flags them as `extra?`.
- Planeswalker tags (Davriel, Chandra) pick up unrelated tags from the whole card text (draw, lifegain, reanimate on Davriel): the older `ability_tags` reads all text, not per ability; per-ability groups are right, the card-level list is noisy.
- `landtype:swamp` on Corrupt and `landtype:island` on Flow of Knowledge sit after the ability tags: by H45 they mark 'cares about a land type', not the card's own type.
- Fixed (user 2026-10-22): a card sacrificing itself as a cost is not a sacrifice outlet (14 cards, e.g. Mind Stone, Sakura-Tribe Elder; 6 real outlets remain). The cross-check no longer reads quoted text, so a token's own 'Sacrifice this creature' ability is not added as the card's cost (Carrier Thrall, Skittering Invasion).
- Fixed earlier in this run: a basic-land sacrifice (Alpine Guide 'sacrifice a Mountain') was tagged sacrifice_outlet; now treated as a land sacrifice (user rule).
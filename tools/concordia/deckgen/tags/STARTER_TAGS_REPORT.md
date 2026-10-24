# Starter deck tagging run: report

10 decks, 353 distinct cards, 353 tagged, 0 with no script (none).

## Most common tags

cardtype:creature 200, target_count:one 128, target_type:creature 92, trigger:etb 92, trigger_scope:self 89, cardtype:instant 64, draw 60, tempo:+1 55, type:human 52, token_make 47, cost:tap 41, target_scope:you_control 37, lifegain 37, damage 37, duration:eot 37, mana_source 35, draw_count:1 35, cardtype:sorcery 34, type:wizard 33, put_onto_battlefield 29, cardtype:artifact 28, duration:static 28, tempo:+0.5 27, burn 26, token_count:1 26, remove:destroy 25, cost:sacrifice 24, controller:you 24, kw:flying 24, type:goblin 24, supertype:legendary 23, trigger_filter:you_control 23, trigger:dies 22, token_pt:1/1 22, mana_amount:1 21, from_zone:graveyard 21, life_loss 20, trigger_zone:graveyard 20, optional 19, target_scope:opp_control 19

## Trigger types seen in clauses

spell 98, etb_self 81, activated 73, static 39, attacks 15, dies_self 14, spell_cast 13, phase 10, etb_other 10, replacement 8, dies_other 5, leaves_self 5, combat_damage 3, gain_life 2, changeszoneall 2, discarded 1, zone_hand_graveyard 1, zone_graveyard_any 1, attackerunblocked 1, spellcastorcopy 1, attackersdeclared 1, lifelost 1, sacrificed 1

## Most common verbs (script API)

changezone 44, draw 32, token 31, dealdamage 28, static_continuous 25, mana 22, destroy 18, loselife+gainlife 11, pump 9, pumpall 9, draw+loselife 8, putcounter 7, static_reducecost 6, replace_moved 5, mill 5, charm 5, changezoneall 4, discard 3, dealdamage+gainlife 3, gainlife 3, pump+fight 3, putcounter+pump 3, dig 3, copypermanent 3, draw+token 3, counter 3, changezone+changezone 3, pump+draw 2, pump+dealdamage 2, fight 2

## Cards with no ability tag beyond type, keyword and cost tags (17)

Typhoid Rats, Thornweald Archer, Deadly Recluse, Ambush Viper, Leatherback Baloth, Tajuru Pathwarden, Gigantosaurus, Colossal Dreadmaw, Kalonian Tusker, Alpine Grizzly, Magnigoth Sentry, Brazen Scourge, Savannah Lions, Fencing Ace, Aven Squire, Skyhunter Skirmisher, Leonin Skyhunter


## Cross-check layer (Oracle gap filler, keyword reference/CR, Forge AI)

Cards where the cross-check added tags: 40; tags added in total: 42 (life_loss 20, fight 7, trigger:combat_damage 3, untap 3, trigger:end_step 2, cost:discard 1, cost:life 1, discard 1, trigger:attacks 1, surveil 1, cost:mana 1, token_make 1).

Cards with an ai_logic tag: 21.

Flags (Oracle line and script tags disagree, nothing added): 14 on 14 cards.

- Return of the Wildspeaker: extra? draw: no Oracle phrase supports it
- Rishkar's Expertise: extra? draw: no Oracle phrase supports it
- Pulse of Murasa: bounce: Oracle line says it, script tags lack bounce
- Barrin, Tolarian Archmage: extra? bounce: no Oracle phrase supports it
- Mindcrank: extra? mill: no Oracle phrase supports it
- Herald's Horn: extra? tutor: no Oracle phrase supports it
- Laboratory Maniac: draw: Oracle line says it, script tags lack draw
- Fact or Fiction: extra? tutor: no Oracle phrase supports it
- Disruptor of Currents: extra? bounce: no Oracle phrase supports it
- Filter Out: extra? bounce: no Oracle phrase supports it
- Arcanis the Omnipotent: extra? bounce: no Oracle phrase supports it
- Time of Ice: extra? bounce: no Oracle phrase supports it
- Psychic Spiral: extra? mill: no Oracle phrase supports it
- Loran of the Third Path: extra? remove:destroy: no Oracle phrase supports it

## Double check of this run

- Structure checks on 353 records (no duplicate or upper-case tags; every supertype and card type in the Types line has its tag; every K: line has a kw: or forge_line: tag): K: line without kw tag: Cloud Key (etbreplacement), Herald's Horn (etbreplacement)
- Comparison with the original run (before the cross-check layer, checked 2026-10-22 after the self-sacrifice fix): 80 tags added on 80 cards changed (22 ai_logic, 58 other tags on 51 cards); 14 `sacrifice_outlet` tags removed (self-sacrifice is not an outlet, user 2026-10-22); nothing else removed or changed.
- By hand: every cross-check addition on the sample cards and about 40 others was read against the Oracle text (see `STARTER_TAGS_SAMPLE.md`); the findings are listed under 'Known problems' below.

## Known problems (found by the double check; tags NOT changed, your call)

- `tutor` is wrongly tagged on cards that look at the top card or split piles (Herald's Horn, Fact or Fiction): the older tagger treats 'put into your hand' as a tutor; the cross-check flags them as `extra?`.
- Planeswalker tags (Davriel, Chandra) pick up unrelated tags from the whole card text (draw, lifegain, reanimate on Davriel): the older `ability_tags` reads all text, not per ability; per-ability groups are right, the card-level list is noisy.
- `landtype:swamp` on Corrupt and `landtype:island` on Flow of Knowledge sit after the ability tags: by H45 they mark 'cares about a land type', not the card's own type.
- Fixed (user 2026-10-22): a card sacrificing itself as a cost is not a sacrifice outlet (14 cards, e.g. Mind Stone, Sakura-Tribe Elder; 6 real outlets remain). The cross-check no longer reads quoted text, so a token's own 'Sacrifice this creature' ability is not added as the card's cost (Carrier Thrall, Skittering Invasion).
- Fixed earlier in this run: a basic-land sacrifice (Alpine Guide 'sacrifice a Mountain') was tagged sacrifice_outlet; now treated as a land sacrifice (user rule).
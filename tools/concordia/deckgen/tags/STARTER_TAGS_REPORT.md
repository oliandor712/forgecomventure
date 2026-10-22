# Starter deck tagging run: report

10 decks, 353 distinct cards, 353 tagged, 0 with no script (none).

## Most common tags

cardtype:creature 200, target_count:one 128, trigger_scope:self 92, target_type:creature 91, trigger:etb 90, cardtype:instant 64, draw 60, tempo:+1 55, type:human 52, token_make 47, cost:tap 41, cost:mana 38, target_scope:you_control 37, lifegain 37, damage 37, mana_source 35, draw_count:1 35, cardtype:sorcery 34, duration:eot 34, type:wizard 33, cardtype:artifact 28, tempo:+0.5 27, put_onto_battlefield 26, burn 26, token_count:1 26, remove:destroy 25, kw:flying 24, type:goblin 24, supertype:legendary 23, cost:sacrifice 23, token_pt:1/1 22, life_loss 20, mana_amount:1 20, trigger:dies 20, trigger_zone:graveyard 20, target_scope:opp_control 19, cost_sacrifice_target:self 18, type:vampire 17, tutor 17, type:soldier 17

## Trigger types seen in clauses

spell 98, etb_self 81, activated 73, static 39, attacks 15, dies_self 14, spell_cast 13, phase 10, etb_other 10, replacement 8, dies_other 5, leaves_self 5, combat_damage 3, gain_life 2, changeszoneall 2, discarded 1, zone_hand_graveyard 1, zone_graveyard_any 1, attackerunblocked 1, spellcastorcopy 1, attackersdeclared 1, lifelost 1, sacrificed 1

## Most common verbs (script API)

changezone 44, draw 32, token 31, dealdamage 28, static_continuous 25, mana 22, destroy 18, loselife+gainlife 11, pump 9, pumpall 9, draw+loselife 8, putcounter 7, static_reducecost 6, replace_moved 5, mill 5, charm 5, changezoneall 4, discard 3, dealdamage+gainlife 3, gainlife 3, pump+fight 3, putcounter+pump 3, dig 3, copypermanent 3, draw+token 3, counter 3, changezone+changezone 3, pump+draw 2, pump+dealdamage 2, fight 2

## Cards with no ability tag beyond type, keyword and cost tags (17)

Typhoid Rats, Thornweald Archer, Deadly Recluse, Ambush Viper, Leatherback Baloth, Tajuru Pathwarden, Gigantosaurus, Colossal Dreadmaw, Kalonian Tusker, Alpine Grizzly, Magnigoth Sentry, Brazen Scourge, Savannah Lions, Fencing Ace, Aven Squire, Skyhunter Skirmisher, Leonin Skyhunter

## mtgish second-opinion flags

not in mtgish: 0 ()

script has more abilities than mtgish rules: 0 ()


## Cross-check layer (oracle, mtgish, keyword reference/CR, Forge AI)

Cards where the cross-check added tags: 51; tags added in total: 58 (life_loss 20, fight 7, scry 6, trigger:upkeep 5, trigger:combat_damage 3, trigger:gain_life 2, cost:remove_counters 2, trigger:beginning_of_combat 2, untap 2, trigger:end_step 2, cost:discard 1, cost:life 1, discard 1, surveil 1, cost:mana 1, cost:exile 1, token_make 1).

Cards with an ai_logic tag: 21.

Flags (one source disagrees, nothing added): 62 on 57 cards.

- Nazar, the Velvet Fang: cost cost:remove_counters from mtgish only
- Carrier Thrall: cost cost:sacrifice from mtgish only
- Malakir Bloodwitch: life_loss: only mtgish says it, script tags lack life_loss
- Feed the Swarm: life_loss: only mtgish says it, script tags lack life_loss
- Supernatural Stamina: trigger trigger:dies from mtgish only (WhenAPermanentDies)
- Feign Death: trigger trigger:dies from mtgish only (WhenAPermanentDies)
- Swiftfoot Boots: cost cost:mana from mtgish only
- Josu Vess, Lich Knight: cost cost:mana from mtgish only
- Syr Konrad, the Grim: trigger trigger:graveyard from mtgish only (WhenACardIsPutIntoAGraveyardFromAnywhereOtherThanTheBattlefield)
- Syr Konrad, the Grim: trigger trigger:graveyard_leave from mtgish only (WhenAGraveyardCardLeaves)
- Gwenna, Eyes of Gaea: untap: only mtgish says it, script tags lack untap
- Search for Tomorrow: cost cost:mana from mtgish only
- Professor of Zoomancy: lifegain: only mtgish says it, script tags lack lifegain
- Professor of Zoomancy: trigger trigger:dies from mtgish only (WhenAPermanentDies)
- Territorial Allosaurus: cost cost:mana from mtgish only
- Vines of Vastwood: cost cost:mana from mtgish only
- Pulse of Murasa: bounce: only oracle says it, script tags lack bounce
- Goreclaw, Terror of Qal Sisma: cost cost:mana from mtgish only
- Impulsive Pilferer: cost cost:mana from mtgish only
- Akki Ronin: cost cost:discard from mtgish only
- Goblin Vandal: trigger trigger:attacks from oracle only
- Goblin Vandal: cost cost:mana from mtgish only
- Goblin Heelcutter: cost cost:mana from mtgish only
- Daretti, Rocketeer Engineer: cost cost:sacrifice from mtgish only
- Loyal Apprentice: trigger trigger:beginning_of_combat from mtgish only (AtTheBeginningOfCombatDuringAPlayersTurn)
- Storm-Kiln Artist: trigger trigger:copy_spell from mtgish only (WhenAPlayerCopiesASpell)
- Coruscation Mage: cost cost:mana from mtgish only
- Light Up the Stage: cost cost:mana from mtgish only
- Curse of Opulence: trigger trigger:attacked from mtgish only (WhenAPlayerIsAttacked)
- Bonesplitter: cost cost:mana from mtgish only
- Keldon Raider: cost cost:discard from mtgish only
- Squee, Dubious Monarch: exile_effect: only mtgish says it, script tags lack exile
- Squee, Dubious Monarch: cost cost:exile from mtgish only
- Squee, Dubious Monarch: cost cost:mana from mtgish only
- Lonely Sandbar: cost cost:mana from mtgish only
- Dramatic Reversal: untap: only oracle says it, script tags lack untap
- Brotherhood Regalia: cost cost:mana from mtgish only
- Hero's Blade: cost cost:mana from mtgish only
- Mask of Memory: cost cost:mana from mtgish only
- Trailblazer's Boots: cost cost:mana from mtgish only
- Expel from Orazca: cost cost:tuck from mtgish only
- Fireshrieker: cost cost:mana from mtgish only
- Herald's Horn: extra? tutor: no mtgish action or Oracle phrase supports it
- Laboratory Maniac: draw: only oracle says it, script tags lack draw
- Sage's Dousing: cost cost:mana from mtgish only
- Fact or Fiction: extra? tutor: no mtgish action or Oracle phrase supports it
- Hieroglyphic Illumination: cost cost:mana from mtgish only
- Propaganda: cost cost:mana from mtgish only
- Rite of Replication: cost cost:mana from mtgish only
- Sweep Away: cost cost:tuck from mtgish only
- Disciple of the Ring: exile_effect: only mtgish says it, script tags lack exile
- Saruman the White: cost cost:mana from mtgish only
- Skittering Invasion: cost cost:sacrifice from mtgish only
- Haliya, Guided by Light: cost cost:mana from mtgish only
- Mentor of the Meek: cost cost:mana from mtgish only
- Restoration Angel: cost cost:exile from mtgish only
- Frontline Medic: cost cost:mana from mtgish only
- Ghostly Prison: cost cost:mana from mtgish only
- Ancestral Blade: cost cost:mana from mtgish only
- Heirloom Blade: cost cost:mana from mtgish only
- Felidar Guardian: cost cost:exile from mtgish only
- Fateful Absence: token: only mtgish says it, script tags lack token_make

## Double check of this run

- Structure checks on 353 records (no duplicate or upper-case tags; every supertype and card type in the Types line has its tag; every K: line has a kw: or forge_line: tag): all passed
- Comparison with the original run (before the cross-check layer, checked 2026-10-22 after the self-sacrifice fix): 80 tags added on 80 cards changed (22 ai_logic, 58 other tags on 51 cards); 14 `sacrifice_outlet` tags removed (self-sacrifice is not an outlet, user 2026-10-22); nothing else removed or changed.
- By hand: every cross-check addition on the sample cards and about 40 others was read against the Oracle text (see `STARTER_TAGS_SAMPLE.md`); the findings are listed under 'Known problems' below.

## Known problems (found by the double check; tags NOT changed, your call)

- `tutor` is wrongly tagged on cards that look at the top card or split piles (Herald's Horn, Fact or Fiction): the older tagger treats 'put into your hand' as a tutor; the cross-check flags them as `extra?`.
- Planeswalker tags (Davriel, Chandra) pick up unrelated tags from the whole card text (draw, lifegain, reanimate on Davriel): the older `ability_tags` reads all text, not per ability; per-ability groups are right, the card-level list is noisy.
- `landtype:swamp` on Corrupt and `landtype:island` on Flow of Knowledge sit after the ability tags: by H45 they mark 'cares about a land type', not the card's own type.
- Flags 'cost:mana from mtgish only' are mostly Equip/Encore/kicker costs the script holds on a K: line; not added.
- Fixed (user 2026-10-22): a card sacrificing itself as a cost is not a sacrifice outlet (14 cards, e.g. Mind Stone, Sakura-Tribe Elder; 6 real outlets remain). The cross-check no longer reads quoted text, so a token's own 'Sacrifice this creature' ability is not added as the card's cost (Carrier Thrall, Skittering Invasion).
- Fixed earlier in this run: a basic-land sacrifice (Alpine Guide 'sacrifice a Mountain') was tagged sacrifice_outlet; now treated as a land sacrifice (user rule). mtgish loader now reads two-faced, adventure and split cards (battles were missing).
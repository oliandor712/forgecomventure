"""New tags created to fill gaps seen across the references (human_logic.toon H56). Every tag family here is logged in
tags/NEW_TAGS_FOR_APPROVAL.md and is PROPOSED until the user approves it. Source of each rule: the user's feedback on the starter sample
(tags/TAG_FEEDBACK_STARTER_SAMPLE.md), the Forge script, and the Comprehensive Rules.
extra(face_lines, svars, types, text) -> (flat tags, links, groups {id: tags}). A group id says which script line a tag came from: tags in the same group are linked."""
import re

COLORS = {"W": "white", "U": "blue", "B": "black", "R": "red", "G": "green", "C": "colorless"}
KWNAMES = {"flying", "trample", "haste", "vigilance", "lifelink", "deathtouch", "menace", "reach", "first", "double", "indestructible", "hexproof", "defender"}

# pinned reference text: family -> one line meaning (and how its values read). Shown to blind readers (batch tag_legend, only families present) and written to tags/TAG_LEGEND.md
LEGEND = {
 "counter": "a counter on a permanent; counter:landmark = a landmark counter (Treasure Map: counts up to three, then the card flips); counter:p1p1 = +1/+1 counter",
 "win": "the card wins the game outright; win:alt_condition = a win condition other than reducing life to zero (its trigger or cost tags say when)",
 "produce_colors": "which colours the mana ability can make when they depend on lands: opp_lands_can = any colour a land an opponent controls could produce",
 "power_scales": "the creature's power is the number of that kind of thing you control (power_scales:creatures_you_control)",
 "from_zone": "zone the card comes from (graveyard, hand, library, exile). Pairs with the other tags of the same group: return, put_onto_battlefield, cost:exile",
 "to_zone": "zone the card goes to (hand, library, exile, battlefield). Pairs with return or take in the same group",
 "return": "a card is returned from one zone to another; read with from_zone and to_zone (return from_zone:graveyard to_zone:hand = return a card from graveyard to hand)",
 "put_onto_battlefield": "a card is put onto the battlefield without being cast; from_zone says where from",
 "look_top": "look at the top N cards of a library",
 "take": "of the looked-at cards, take this many (may_ = optional, all = every matching card, then an optional type or filter); to_zone says where they go",
 "rest_to_zone": "where the looked-at cards that were not taken go; rest_order says the position",
 "rest_order": "position of the rest in the library: bottom, or bottom_random (bottom in a random order)",
 "modal": "choose N of M modes (modal:1_of_3 = choose one of three)",
 "replace": "a replacement effect: replace:<event>_to_<what> (draw_to_winsgame = instead of drawing, win the game; damagedone_to_other = changes damage that would be dealt to another permanent, e.g. with prevent_damage a shield for your other creatures)",
 "condition": "the ability works only while this is true (a permanent or card you control, or an empty library)",
 "restrict_kind": "kind of restriction placed on a creature (cant_attack, cant_block, cant_attack_or_block, cant_attack_unless_cost)",
 "token_ability": "ability the created token has, in words (tap_sacrifice_add_mana_any_color = {T}, Sacrifice: Add one mana of any color)",
 "token_type": "token type; junk_exileplay = the Junk token (artifact: {T}, Sacrifice: exile the top card of your library, you may play it this turn, sorcery speed only)",
 "exile_from": "exiles cards from a zone other than the battlefield",
 "cost": "non-mana cost of the ability (tap, sacrifice, remove_counters, exile with from_zone, life, discard, return)",
 "duration": "how long an effect lasts (eot = until end of turn, static = while the source is on the battlefield, next_untap, while_control, end_step, until_monarch_changes = until an opponent becomes the monarch...)",
 "affected_scope": "whose permanents the effect or static ability affects (you_control, opponent_controls, all)",
 "trigger": "event that triggers the ability (attacks, dies, etb, gain_life, beginning_of_combat ...)",
 "piles_split": "cards are split into two piles by this player",
 "lifegain_amount": "life gained (number, x, or equal_to_life_lost)",
 "choose_on_enter": "as this card enters the battlefield its controller chooses something (color, card_type, creature_type, player ...); other tags of the card refer to the choice (cost_reduce_for:chosen_type = spells of the chosen type)",
 "cost_reduce_for": "which spells a cost reduction applies to (a card type, a creature type, or chosen_type); cost_reduce_amount is how much cheaper",
 "enters_prepared": "the creature enters prepared: while prepared its controller may cast a copy of the spell on its other half (the spell half's tags are in the card's groups); casting it unprepares the creature",
 "choice_option": "one of the options the choice offers (choose_on_enter lists them: artifact, creature, enchantment ...)",
 "cost_reduce_mana": "the kind of mana the cost is reduced by (generic = any mana)",
 "cost_reduce_amount": "how much each affected spell costs less (generic mana)",
 "mana_conditional": "the mana ability adds a different amount, or works only, when the condition: tag of its group holds",
 "mana_amount_if": "mana added when the condition holds; mana_amount is the base amount otherwise",
 "extra_land_drop": "its controller may play this many additional lands each turn",
 "phase_out": "permanents phase out",
 "colorless_card": "the card is a colorless spell (no colored mana symbol, no color indicator, or Devoid; lands excluded); colorless is the sixth colour, so the deck needs colorless-capable mana for it",
 "unless_cost": "the effect happens unless a player pays a cost (a tax, not a choice); unless_cost_amount says how much",
 "niche": "the card is only good in a deck built around the named theme (niche:artifact, niche:landfall, niche:tribal ...); the power score gives it half role credit; a card with this tag fits few decks",
 "mech": "the card needs a rule or component many decks and the Forge AI handle poorly (mech:monarch, mech:vote, mech:day_night ...); the deck builder allows it only from a set tier",
 "alt_additional_cost": "an alternative additional cost as the card is cast (reveal a card or pay mana, for example); the cost tags follow",
 "additional_cost": "the spell has a mandatory additional cost to cast it (discard a card, sacrifice a creature ...); the cost tags (not the mana cost) say which; it is not the spell's own mana cost",
 "scales": "the amount (X) of this ability is the number of that kind of thing you control: write it as 'for each <thing> you control' (scales:island on a draw_count:x = draw a card for each Island you control)",
 "mana_restriction": "the mana can be spent only on what the value says (mana_restriction:instant_or_sorcery = spend this mana only to cast an instant or sorcery spell)",
 "x_is": "what the amount is when it is not a plain number. Do NOT write the letter X for these: count_<thing>_you_control = 'for each <thing> you control'; own_power / target_power = 'equal to that creature's power'; previous_result = 'equal to the amount the previous effect produced' (damage dealt, life lost ...). Only x_paid means the letter X (the X in the mana cost). Example: damage_amount:x x_is:count_creature_you_control = deals damage equal to the number of creatures you control",
 "controller": "who controls the permanent after the effect: controller:you (default: it enters under the control of the player who controls the effect) or controller:owner (only when the Oracle text says 'under its owner's control')",
 "optional": "the effect of this group is optional (you may ...)",
 "target_scope": "whose things or which players the effect hits (you_control, opp_control; no tag = whoever controls it; each_opponent = every opponent, each_player = every player; no value means a single chosen target)",
 "trigger_scope": "which cards fire a zone-change trigger: self = this card only, other = another card, any = this card or any other card",
 "trigger_filter": "narrows the triggering card or spell: a card type (always named for another card's zone-change trigger: trigger_filter:creature = another creature), a negated type (noncreature = noncreature spell), power_ge_N / power_le_N (power at least / at most N), one_or_more (triggers once for a group)",
 "cost_mana": "the mana part of an activation cost, symbols joined (cost_mana:2b = {2}{B}, cost_mana:x = {X}); cost:mana is not tagged when this tag is present",
 "investigate": "investigate (CR 701.16): create a Clue token",
 "bolster": "bolster N (CR 701.39): put N +1/+1 counters on the creature you control with the least toughness; the value is N",
 "monarch": "you become the monarch (CR 724)",
 "unless_cost_amount": "the mana an 'unless pays' tax asks for (unless_cost_amount:2 = unless its controller pays {2}); also the per-creature attack tax",
 "limit": "limit on how often the ability works (once_per_turn = only once each turn)",
 "regenerate": "regenerates a creature", "cant_regenerate": "the destroyed creature can't be regenerated",
 "prevent_damage": "prevents damage that would be dealt (a targeted shield, not all combat damage)",
 "steal": "gain control of a permanent",
 "cant_be_blocked": "cannot be blocked, with the exception named in the value (by_creature_blue = by blue creatures)",
}

# meanings of the older families that have no DOC / LEGEND entry: family -> (meaning, source / reference). Used by the generated tags/TAG_REFERENCE.md
REF_EXTRA = {
 "cardtype": ("card type from the Types line: creature, instant, sorcery, artifact, enchantment, land, planeswalker, kindred", "script Types: line; CR 205.2"),
 "type": ("creature or other subtype from the Types line (human, wizard, equipment ...)", "script Types: line; CR 205.3"),
 "supertype": ("supertype: legendary, basic, snow, world", "script Types: line; CR 205.4"),
 "landtype": ("basic land type of a basic land (swamp, forest ...): the land taps for that mana", "script Types: line; CR 305.6"),
 "kw": ("keyword ability the card has; qualifiers (numbers, costs, colours) follow as separate tags", "script K: line; CR 702; reminder text in ai_lab/KEYWORD_REMINDER_TEXT.toon"),
 "optional": ("the effect of the group is optional (you may ...)", "script Optional$ True / OptionalDecider$ You (agent suggestion S01)"),
 "unless_cost": ("the effect happens unless a player pays a cost (a tax, not a choice)", "script UnlessCost$"),
 "limit": ("limit on how often an ability works: once_per_turn, or N_per_turn", "script ActivationLimit$"),
 "mana_source": ("the card or ability adds mana (qualifiers: mana, mana_amount, mana_choice, mana_restriction)", "script Mana abilities (AB$ Mana, Produced$); CR 106"),
 "cost_reduce": ("spells cost less to cast (qualifiers: cost_reduce_for, cost_reduce_amount, cost_reduce_mana)", "script S: Mode$ ReduceCost; CR 601.2f"),
 "cost_reduce_amount": ("how much cheaper each affected spell is", "script Amount$ on ReduceCost"),
 "cost_reduce_mana": ("the kind of mana the reduction takes off (generic = any mana)", "script ReduceCost; CR 601.2f"),
 "mana_conditional": ("the mana ability adds a different amount, or works only, when a condition holds (the condition is a condition: tag in the same group)", "script IsPresent$ on the mana ability, or Amount$ with Count$Compare"),
 "mana_amount_if": ("mana added when the condition holds (mana_amount is the base amount)", "script Count$Compare <SVar> <op><n>.<then>.<else>"),
 "extra_land_drop": ("lets its controller play additional lands each turn (value = how many more)", "script AdjustLandPlays$"),
 "phase_out": ("permanents phase out", "script Phases; CR 702.26"),
 "alt_additional_cost": ("the card has an alternative additional cost (reveal a card or pay mana ...); the cost tags follow", "script K:AlternateAdditionalCost; CR 118.8"),
 "additional_cost": ("the spell has a mandatory additional cost (discard a card, sacrifice a creature ...); the cost tags say which", "script A:SP$ with CostDesc$ As an additional cost to cast; CR 118.8"),
 "cost_exile_target": ("what is exiled from the graveyard as a cost", "script Cost$ ExileFromGrave"),
 "choose_on_enter": ("as the card enters, its controller chooses something (color, card_type, creature_type, player ...); later tags refer to the choice", "script K:ETBReplacement with a Choose* effect; CR 614.12"),
 "enters_prepared": ("the creature enters prepared (may cast a copy of its spell half; casting it unprepares)", "script K:ETBReplacement with AlterAttribute Attributes$ Prepared; AlternateMode:Prepare"),
 "choice_option": ("one of the options the choice offers", "script ValidTypes$ / Choices$ of the Choose effect"),
 "draw": ("draws cards (amount in draw_count)", "script Draw; CR 121"),
 "token_make": ("creates tokens: 'Create a 1/1 white Soldier creature token' (qualifiers: token_count, token_type, token_pt, token_color, token_kw)", "script Token; CR 111"),
 "counters_plus": ("puts +1/+1 counters on something: 'Put a +1/+1 counter on target creature'", "script PutCounter P1P1; CR 122"),
 "put_tapped": ("the card is put onto the battlefield tapped", "script ChangeZone Tapped$ True"),
 "counterspell": ("counters a spell", "script Counter; CR 701.6"),
 "mill": ("puts cards from the top of a library into a graveyard", "script Mill; CR 701.17"),
 "reveal": ("reveals cards", "script Reveal / PeekAndReveal; CR 701.16"),
 "scales": ("the effect grows with the number of things of this kind you control (scales:elf = per Elf you control); basic land types and graveyard-style counts included", "script Count$ variables (ability_tags.py)"),
 "cant_regenerate": ("the creature can't be regenerated", "script NoRegen$ True / Mode$ CantRegenerate; CR 701.19 (agent suggestion S07)"),
 "num": ("number in a keyword cost or qualifier (kicker, ward, equip amounts)", "script K: line"),
 "reanimate": ("AI umbrella: any effect that moves a card from a graveyard onto the battlefield; derived from put_onto_battlefield + from_zone:graveyard (the readable detail is those tags and controller)", "AI Tags category; derived in tag_variant.py"),
 "pump_single": ("pumps one target creature", "script Pump with a target"),
 "bounce": ("returns a permanent to its owner's hand", "script ChangeZone Battlefield -> Hand"),
 "sacrifice_outlet": ("can sacrifice other permanents (not just itself or lands)", "script Cost$ Sac<..>; human_logic rule on self/land sacrifice"),
 "evasion": ("hard to block: menace, shadow, fear, intimidate, landwalk, can't be blocked (flying keeps its own tag)", "ability_tags.KEYWORD_TAGS and cant_be_blocked; landwalk added on the user's order 2026-10-22"),
 "self_mill": ("mills the card's own controller: 'Mill three cards' (you put cards from your library into your graveyard)", "script Mill with a Defined player"),
 "shrink": ("gives -X/-X to a creature", "script Pump with negative amounts"),
 "protection_trick": ("gives protection or indestructibility at instant speed", "script Pump KW$ Protection / Indestructible"),
 "clone": ("enters as a copy of another permanent: 'You may have this enter as a copy of any creature on the battlefield'", "script Clone / ETBReplacement Clone"),
 "proliferate": ("adds a counter of each kind to chosen permanents/players", "script Proliferate; CR 701.34"),
 "attack_tax": ("attackers must pay a cost per attacker", "script Mode$ CantAttack with a cost"),
 "steal_temp": ("gains control until end of turn", "script GainControl with Untap / LoseControl"),
 "steal_grants_haste": ("the stolen permanent gains haste", "script GainControl AddKWs$ Haste"),
 "tap_down": ("taps target permanents and keeps them tapped", "script Tap / TapAll"),
 "grave_hate": ("exiles or punishes cards in graveyards", "script ChangeZone Graveyard -> Exile"),
 "lord": ("gives a bonus to all creatures of a type", "script S: Continuous with a type filter"),
 "burn": ("AI tag: damage or life loss that can hit a player (any target, player or opponent); the damage itself is tagged damage, damage_amount and target_type", "ability_tags.py rule: DealDamage with ValidTgts Any|Player|Opponent, or LoseLife on an opponent; AI Tags category"),
 "land_tutor": ("AI tag: searches the library for a land", "AI Tags category"),
 "selection": ("AI tag: card selection (look, scry, loot)", "AI Tags category"),
 "artifact_token": ("AI tag: creates artifact tokens", "AI Tags category"),
 "pump_team": ("AI tag: pumps several creatures", "AI Tags category"),
 "removal": ("AI tag: umbrella for removal when no method tag applies", "AI Tags category"),
 "fixing": ("AI tag: fixes mana colours", "AI Tags category"),
 "evasion_grant": ("AI tag: grants an evasion keyword", "AI Tags category"),
 "extra_turn": ("the card takes an extra turn (script AddTurn); capped per tier in tier_rules (none below T4, 1 at T4, 2 at T5)", "user 2026-10-26: own tag, replaces the name list in power_scorer"),
 "haste_grant": ("AI tag: grants haste", "AI Tags category"),
}

# family -> (meaning, why / user note)
DOC = {
 "mill_count:<n|x>": ("how many cards are milled (who is milled: mill / self_mill)", "mtg2llm gap record, approved 2026-10-27: Blight Titan, Barrowgoyf"),
 "flip_coin + flip_win / flip_lose": ("the effect flips a coin; flip_win / flip_lose mark that an outcome has a sub-effect", "approved 2026-10-27: Creepy Doll, Volatile Rig"),
 "secret_choice:<number|card|player>": ("a player chooses secretly, then the choices are revealed and compared", "approved 2026-10-27: Wheel of Misfortune, Expert-Level Safe"),
 "lose_game": ("the effect makes a player lose the game", "approved 2026-10-27: Nine Lives"),
 "counter_remove:<n|all|x>": ("removes counters as an effect (cost:remove_counters is the cost)", "approved 2026-10-27: Phantom Nantuko"),
 "grant_type:<type>": ("a static effect gives permanents an extra type (all lands are also Forests)", "approved 2026-10-27: Yavimaya, Cradle of Growth"),
 "cost_energy:<n> (cost:energy)": ("the cost pays energy counters", "approved 2026-10-27: Aethertide Whale"),
 "niche": ("the card is only good in a deck built around the named theme; value = the theme (artifact, enchantment, landfall, tribal, self_mill, graveyard_hate, land, storm ...); the power score gives these cards 0.5 role credit", "user 2026-10-25 (niche cards), power_scorer.py NICHE_ROLE"),
 "mech": ("the card needs a mechanic or component many decks and the Forge AI handle poorly (value = mechanic: monarch, graveyard_cast, vote, day_night, ring ...); build.py MECH_MIN_TIER gates it by tier. It repeats the effect tag where one exists (monarch / mech:monarch): the effect tag says what the card does, mech says where the builder may use it", "user 2026-10-25 (replaces build.SKIP_TEXT)"),
 "colorless_card": ("the card is a colorless spell (no colored mana symbol, no color indicator, or Devoid; lands excluded); the deck needs colorless-capable mana for it (colorless is the sixth colour, H78)", "user 2026-10-26: color and mana tags include colorless"),
 "mana:<color>": ("colour of mana an ability produces (white, blue, black, red, green, colorless, any, commander_identity; colorless is the sixth colour, H78)", "feedback: link color type to mana source (Arcane Signet, Plains, Temple, Frost Marsh)"),
 "mana_amount:<n>": ("how much mana is produced per activation; always tagged on a mana source ability, also when it is 1", "Temple of the False God; user note: always tag mana_amount"),
 "mana_restriction": ("the mana can only be spent on certain things; the value says on what (instant_or_sorcery, creature_spell, artifact_spell_or_activated_ability ...)", "Vodalian Arcanist; script RestrictValid$"),
 "mana_choice": ("the ability lets you choose between colours", "Frost Marsh, Arcane Signet"),
 "trigger:tap": ("the ability is a tap ability (basic lands tap for one colour of mana)", "feedback: Plains, Frost Marsh trigger type"),
 "activation_restriction": ("the ability can only be activated under a condition", "Temple of the False God"),
 "enters_tapped": ("the permanent enters tapped", "Myriad Landscape, Frost Marsh"),
 "cost:tap / cost:sacrifice / cost:mana / cost:life / cost:discard": ("what the activation cost contains; sacrifice is also tagged when it is a cost", "Harrow, Blighted Woodland, Myriad Landscape"),
 "effect:sacrifice": ("sacrifice happens as an effect (not a cost)", "Garruk, Kiki-Jiki, Victimize"),
 "loyalty:<n> / loyalty_change:+n|-n / counters:loyalty": ("planeswalker loyalty, and the loyalty change an ability makes (renamed from loyalty_cost, user note); loyalty is a kind of counter", "Oko, Rowan"),
 "defense:<n>": ("battle defense value", "Invasion of ... battles"),
 "transform": ("the card has a back face (double-faced) or an ability transforms it: write 'Transform this permanent' / 'When ..., transform it'; with nothing else it is just a double-faced card", "Invasion battles"),
 "becomes:<type> / loses_all_abilities": ("an Animate effect: what it becomes, and that it loses all abilities", "Oko"),
 "tutor / tutor_count:<n|up_to_n> / tutor_target:<type> / tutor_dest:<zone> / shuffle": ("library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle", "Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow"),
 "token_type:<t> / token_count:<n|x> / token_color:<c> / token_pt:<p/t> / token_kw:<k>": ("what a token ability creates; Food and Treasure are token types", "Captain's Call, Memnarch, Oko, Garruk"),
 "remove:destroy|exile|bounce|tuck|sacrifice": ("how a card removes something; replaces the single 'removal' tag when a method is known", "Scorching Dragonfire, Oblivion Ring"),
 "damage / damage_amount:<n>": ("deals damage (damage is damage, not removal)", "Scorching Dragonfire, Rowan"),
 "die_replace:exile": ("'if it would die, exile it instead'", "Scorching Dragonfire, Garruk"),
 "target_count:one|up_to_<n>|all|x|each": ("how many things the effect picks", "Filter Out, Rowan, Oko"),
 "trigger_scope:self|other": ("whether a zone-change trigger is about this card or other cards (enters, dies, leaves)", "found in the cross-check: Morbid Opportunist, Welcoming Vampire"),
 "exile_from:<zone>": ("exiles cards out of a zone other than the battlefield (graveyard, hand, library)", "found in the cross-check: Scavenging Ooze, Squee"),
 "token_type:copy": ("the token is a copy of another permanent", "found in the cross-check: Kiki-Jiki, Rite of Replication"),
 "draw_count:<n|x> / discard_count:<n|x>": ("how many cards an ability draws or makes a player discard", "user note: tag draw count"),
 "named:<Full_Name>": ("the printed name of ANOTHER card (or a named token/Role) that an ability mentions: 'a card named X', 'Partner with X'; words joined by _, casing kept; emitted only by tagcheck/mtg2llm.py tag, only with a value taken from the card's own script; own name, keywords, types and token words are never named:", "user task 2026-10-23: names must survive the tag -> render round trip; Pir, Toothy, Agency Outfitter"),
 "scry_count:<n|x>": ("how many cards a scry looks at (one tag says both that it scrys and how many, like draw_count; x = a variable amount, see x_is)", "user 2026-10-23: scry carries its number like other numbered effects"),
 "tempo:+n|x": ("net cards added to your hand or battlefield minus cards removed (the spell itself, sacrificed or discarded cards) when the ability resolves; tokens count 0.5 each; only positive values are tagged; tempo:x when an amount is a variable", "user note: tempo gain (+1), applied to every ability that adds more cards than it removes"),
 "put_onto_battlefield + from_zone:<zone>": ("a card is put onto the battlefield from a zone (put_onto_battlefield from_zone:library) without being cast, so its mana cost and 'when you cast' triggers are skipped; enter-the-battlefield triggers still happen (CR 603.6a). Distinct from trigger:etb, which is a trigger on entering", "user note, confirmed 2026-10-22: the tag means 'not cast'"),
 "cost_mana:<symbols>": ("the mana part of an activation cost (cost_mana:2b = {2}{B})", "P4c E, user 2026-10-23 (placeholder triage: {cost} was 117 of 317 placeholders)"),
 "investigate": ("investigate (CR 701.16): create a Clue token", "user 2026-10-23, P4c D (Thraben Inspector)"),
 "bolster:<n>": ("bolster N (CR 701.39): put N +1/+1 counters on the creature you control with the least toughness", "user 2026-10-23, P4c D (Elite Scaleguard)"),
 "setup_card:<need>": ("general tag, any archetype: the card does nothing until the deck supplies <need>; need = mana (big mana to pay an activation cost), counters (+1/+1 or other counters), graveyard, tokens. The builder counts the card's utility only when the deck meets the need (mana: 10 ramp pieces)", "user 2026-10-27, Dark Depths (setup_card:mana)"),
 "restricted_to:<type>": ("general tag, any archetype: the card's mana (spend only to cast <type> spells) or return ability (target <type> card from your graveyard) names a creature type, so it works only in a deck with that type. The builder gives it commander support only when the type is the commander's or an allowed tribe", "user 2026-10-27, Haven of the Spirit Dragon (restricted_to:dragon)"),
 "monarch": ("you become the monarch (CR 724)", "user 2026-10-23, P4c D (Palace Jailer)"),
 "unless_cost_amount:<symbols>": ("the mana an 'unless pays' tax or attack tax asks for", "P4c E, user 2026-10-23 (Sage's Dousing, Ghostly Prison)"),
 "cost_if_you_do": ("the 'If you do' part marks the preceding sacrifice/discard as a cost", "user note on Victimize"),
 "enters_untapped / enters_tapped_conditional": ("lands that enter untapped, or tapped unless a condition holds (enters_tapped stays for always-tapped)", "user note: tag whether a land enters tapped"),
 "cast_free": ("casts a spell without paying its mana cost", "found in the cross-check: Rishkar's Expertise"),
 "target_zone:<zone>": ("the zone the targets are in (graveyard, exile, hand, library)", "Victimize"),
 "target_type:<t> / target_filter:<f> / target_scope:you_control|opp_control": ("what the effect can pick: card type, filters such as nonland, and whose", "Filter Out, Scorching Dragonfire, Oblivion Ring"),
 "trigger:etb|dies|leaves|attacks|spell_cast|... / trigger_zone:graveyard / trigger_filter:<type>": ("trigger event, the zone it goes to, and a card-type filter on cast triggers", "Rancor, Oblivion Ring, Bontu's Monument"),
 "delayed:end_step / duration:end_step": ("an effect that happens at the next end step", "Kiki-Jiki"),
 "impulse_draw / impulse_draw_count:<n|x>": ("exile cards and let you play them for a limited time; counted and linked like draw (count, duration, tempo)", "Invasion of Kaldheim; user note: same links as draw"),
 "must_attack": ("creatures must attack each combat (a can't-block effect on other creatures is tagged restrict, not a separate tag)", "Rabblemaster; user: cant_block tag removed"),
 "exchange_control": ("swap control of two permanents (linked to steal)", "Oko"),
 "steal": ("gain control of something (linked to haste when the effect grants it)", "Rowan"),
 "cost_reduce_for:<type> + color:<c>": ("which spells a cost reduction applies to (colorless is the sixth colour: color:colorless, H78)", "Bontu's Monument"),
 "counter:<type>": ("which counters are placed (the count and scope of the targets are target_count and target_scope)", "Invasion of Moag"),
 "cost_sacrifice_target:<t>": ("what a sacrifice cost sacrifices (self, land, creature ...)", "Harrow, Blighted Woodland"),
 "sacrifice_type:<t>": ("what an edict makes players sacrifice", "Garruk"),
 "token_cardtype:artifact": ("the token is an artifact", "Memnarch, Oko"),
 "affects:<tribe>": ("which creature type a static effect applies to", "Goblin Rabblemaster"),
 "steal_grants_<kw>": ("the control-gain effect also gives a keyword (linked to steal)", "Rowan"),
 "return_exiled": ("returns what this card exiled when it leaves", "Oblivion Ring"),
 "protection_from:<colour|type>": ("what a Protection keyword protects from (kw:protection stays the keyword)", "user: protection parsed as the keyword, colours and types as separate tags"),
 "forge_line:<name>": ("a Forge engine line that is not a rules keyword. forge_line:etbcounter = 'enters with counters on it' (the counter tags say which); forge_line:etbreplacement = an 'as this enters' choice or replacement", "found in the cross-check: these were wrongly tagged kw:"),
 "landwalk:<landtype>": ("which land type a landwalk keyword names", "user: landwalk type as its own tag"),
 "pump_amount:<+p/+t> / grant_kw:<kw> / duration:static": ("a continuous (static) effect that changes power/toughness or grants a keyword while the source is on the battlefield (duration:static marks it as static); the amount is the +p/+t (x when it scales)", "reverse check r1: Benalish Marshal, Predatory Wurm, Storm-Kiln Artist had no ability tag"),
 "affected_type:<t> / affected_scope:you_control|opp_control / affected_filter:other": ("what a static effect applies to (anthem: other creatures you control)", "reverse check r1: Benalish Marshal"),

 "condition:<readable>": ("a static or replacement effect that only applies while something is present, as one tag (condition:planeswalker_garruk_you_control, condition:no_card_you_own_in_library, condition:at_least_4_creature_you_control); replaces condition_present / _zone / _compare", "reverse check r1: Predatory Wurm, Laboratory Maniac; user 2026-10-22: prune redundant proposed tags"),
 "x_is:<what>": ("what a variable amount (X) measures, as one readable value read from the script's variable: target_power, target_mana_value, sacrificed_power, triggering_damage, life_lost_by_opponents_this_turn, count_land_you_control, count_creature_in_graveyard, devotion_black, x_paid, own_power, ... with arithmetic as a suffix (_times_2, _plus_1, _half_up); linked to its amount tag (scales_with) and to the object it measures (measures)", "reverse check r1/r2: Swords to Plowshares, Feed the Swarm, Gray Merchant, Exsanguinate; user 2026-10-22: make x_is robust with linked conditions (target power, life lost ...)"),
 "replace:<event>_to_<what>[_<detail>]": ("a replacement effect ('instead') as one tag: the event replaced, what happens instead, and a detail (replace:draw_to_winsgame, replace:addcounter_to_replacecounter_counternum_plus_1); replaces replacement / replace_event / replace_with / replace_detail", "reverse check r1: Kami of Whispered Hopes, Laboratory Maniac"),
 "return + from_zone:<zone> + to_zone:<zone>": ("a card returns from the graveyard or exile to hand or library (return from_zone:graveyard to_zone:hand); the readable detail behind the AI umbrella tag recursion. from_zone / to_zone are the shared zone tags used by every zone-move tag (return, take, put_onto_battlefield, cost:exile)", "reverse check r5: Elvish Regrower lost its meaning when recursion became an AI tag"),
 "cant_be_countered / cant_be_blocked[:by_<what>]": ("this spell can't be countered / this creature can't be blocked (by creatures of that kind); evasion, not a restriction", "reverse check r1: Lightning Mare, Brotherhood Regalia"),
 "modal:<chosen>_of_<modes>": ("a modal spell: how many modes are chosen of how many exist (modal:1_of_3 = choose one of three); replaces the separate mode_count and mode_choose tags (user: redundant)", "reverse check r1: Valorous Stance, Return of the Wildspeaker"),
 "look_top:<n> / take:[may_]<count>[_<filter>] + to_zone:<zone> / rest_to_zone:<zone> + rest_order:bottom[_random]": ("look at the top N cards, take K (matching a filter, optionally = may) to a zone (to_zone), put the rest in a zone (rest_to_zone) in a position (rest_order bottom_random = on the bottom in random order); one take tag replaces take_count, take_filter, take_optional (user: redundant); zones are separate shared to_zone tags", "reverse check r1: Militia Bugler, Dig Through Time"),
 "piles_split:<who>": ("cards are divided into two piles by that player; one tag replaces piles_split + pile_separator (user: redundant)", "reverse check r1: Fact or Fiction"),
 "restrict / restrict_kind:cant_attack_or_block|cant_attack|cant_block|cant_activate|doesnt_untap|loses_abilities|cant_attack_unless_cost": ("an effect that stops something from acting: can't attack or block (A/B), can't attack (A), can't block (B), its abilities can't be activated, doesn't untap, or loses its abilities; `restrict` stays as the umbrella, the kind says which; who is affected is in the target / affected tags and how long in the duration tag", "user 2026-10-22: make restrict robust (Pacifism, Goblin Heelcutter, Icy Blast, Merfolk Trickster)"),

 "token_ability:<what it does>": ("what a standard artifact token does when sacrificed or paid for (Treasure, Food, Clue, Blood, Gold, Map; CR 111.10), written out so artifact_token and token_type need no outside knowledge", "user 2026-10-22: remake artifact_token more readable"),
 "restrict_scope:self": ("the restriction is a drawback on the card itself (a creature that can't block)", "restrict robustness: Bloodghast, Bog Hoodlums"),
 "cant_be_blocked": ("the creature can't be blocked (evasion granted by a static effect); a restriction on the blocked player's creatures is `restrict`, not this", "restrict robustness: Brotherhood Regalia"),
 "duration:next_untap / duration:while_control": ("an effect lasts until the next untap step / for as long as you control the source", "restrict detail: Icy Blast, Exhaustion, Time of Ice"),
 "grant_kw:<kw>": ("an effect gives a keyword for a time (duration tag says how long; eot when none is written, as Forge does)", "reverse check r1: Valorous Stance (modes were not read)"),
 "grant_ability:<what>": ("an effect gives a permanent an ability or trigger for a time, not a transformation (grant_ability:dies_trigger); replaces grant_ability + granted_trigger", "reverse check r1: Feign Death, Supernatural Stamina were mis-tagged transform"),
 "saga_chapter": ("marks an ability as a saga chapter (the chapter number is not kept; how many chapters the saga has is kw:chapter + num)", "reverse check r1: Time of Ice"),
 "lifegain_amount:<n|x|equal_to_life_lost> / life_loss_amount:<n|x> / counter_count:<n|x>": ("amounts the first run dropped: life gained or lost, counters placed", "reverse check r1: 86 of 348 cards lost a number"),
 "cost:return / cost_return_target:<t> / cost:exile + from_zone:graveyard": ("non-mana costs: return a permanent you control to hand; exile a card from your graveyard", "reverse check r1: Soratami Savant, Disciple of the Ring"),
 "recursion:return_self": ("the card returns itself (to hand, from the graveyard)", "Rancor"),
}


from common import snake as tok, params   # noqa: E402


def filt(s):
    """a Forge filter word as readable tag text: powerGE4 -> power_ge_4"""
    return tok(re.sub(r"(power|toughness|cmc)(GE|LE|EQ|GT|LT)(\d+|X)", r"\1_\2_\3", s))



def target_tags(p, out, api=""):
    v = p.get("ValidTgts") or ""
    allv = p.get("ChangeType") if ("ValidTgts" not in p and api.endswith("All")) else None
    allv = allv or p.get("ValidCards") or p.get("AllValid")
    if v:
        mn, mx = p.get("TargetMin"), p.get("TargetMax")
        if mn == "0" and mx and mx.isdigit(): out.append("target_count:up_to_" + mx)
        elif mx and mx.isdigit() and int(mx) > 1: out.append("target_count:" + mx)
        elif mx == "X": out.append("target_count:x")
        else: out.append("target_count:one")
        f = v
    elif allv:
        out.append("target_count:all"); f = allv
    else:
        return
    for part in f.split(","):
        bits = part.split("+")
        main = bits[0].split(".")
        if main[0] and main[0] not in ("Any",):
            out.append("target_type:" + tok(main[0]))
        else: out.append("target_type:any")
        rest = main[1:] + bits[1:]
        for r in rest:
            if r in ("YouCtrl", "YouOwn"): out.append("target_scope:you_control")
            elif r in ("OppCtrl", "YouDontCtrl"): out.append("target_scope:opp_control")
            elif r in ("cmcEven", "cmcOdd"): out.append("target_filter:%s_mana_value" % r[3:].lower())
            elif r.startswith("non") or r in ("Other", "Basic", "Legendary", "Tapped", "Untapped"): out.append("target_filter:" + filt(r))
            elif r and main[0] in ("Permanent", "Card", "Creature") and (r[0].isupper() or r in ("attacking", "blocking", "tapped", "untapped") or re.match(r"(power|toughness|cmc)(GE|LE|EQ|GT|LT)", r)): out.append("target_filter:" + filt(r))


def token_tags(p, out):
    s = p.get("TokenScript", "")
    n = p.get("TokenAmount", "1")
    out.append("token_count:" + ("x" if not n.isdigit() else n))
    parts = s.split("_")
    if not parts or not parts[0]: return
    cols = [COLORS[c.upper()] for c in parts[0] if c.upper() in COLORS]
    for c in cols: out.append("token_color:" + c)
    rest = parts[1:]
    if len(rest) >= 2 and rest[0].isdigit() and rest[1].isdigit():
        out.append("token_pt:%s/%s" % (rest[0], rest[1])); rest = rest[2:]
    types = []
    for w in rest:
        if w in ("a", "e", "sac"):
            if w == "a": out.append("token_cardtype:artifact")
            continue
        if w in KWNAMES: out.append("token_kw:" + w)
        else: types.append(w)
    if types: out.append("token_type:" + "_".join(types))
    ty = "_".join(types)
    TOKEN_ABILITY = {"treasure": "tap_sacrifice_add_mana_any_color", "food": "pay_2_tap_sacrifice_gain_3_life", "clue": "pay_2_sacrifice_draw_a_card",
                     "blood": "pay_1_tap_discard_sacrifice_draw_a_card", "gold": "sacrifice_add_mana_any_color", "map": "pay_1_tap_sacrifice_target_creature_explores"}
    if ty in TOKEN_ABILITY: out.append("token_ability:" + TOKEN_ABILITY[ty])      # what the standard artifact token does (CR 111.10), so the type name needs no outside knowledge
    for key, prov in (("food", "lifegain"), ("treasure", "mana_source"), ("clue", "draw"), ("blood", "discard")):
        if ty == key: out.append(prov)


def compact_mana(c):
    """'1 B' -> '1b'; '' when the string is not plain mana symbols"""
    c = (c or "").strip()
    return c.replace(" ", "").lower() if re.fullmatch(r"(?:(?:\d+|X|[WUBRGC])\s*)+", c) else ""


CTYPES = ("Creature", "Land", "Artifact", "Enchantment", "Planeswalker", "Instant", "Sorcery", "Battle")


def spell_filters(vc):
    """card types named by a ValidCard filter, a negated type as 'non<type>' (Card.nonCreature -> noncreature); Self-only parts name no filter"""
    out = []
    for part in [x for x in vc.split(",") if x]:
        if re.match(r"^\w+\.Self$", part): continue
        for neg, ty in re.findall(r"(?<![A-Za-z])(non)?(%s)(?![a-z])" % "|".join(CTYPES), part):
            out.append((neg + ty).lower())
    return list(dict.fromkeys(out))


def cost_tags(cost, out):
    if not cost: return
    if re.search(r"(^|\s)T(\s|$)", cost): out.append("cost:tap")
    m = re.search(r"Sac<[^/>]*/([^/>]*)", cost)
    if "Sac<" in cost:
        out.append("cost:sacrifice"); 
        if m: out.append("cost_sacrifice_target:" + ("self" if m.group(1) == "CARDNAME" else tok(m.group(1).split(".")[0])))
    m = re.search(r"Return<\d+/([^/>]*)", cost)
    if m: out += ["cost:return", "cost_return_target:" + tok(m.group(1).split(".")[0])]
    m = re.search(r"ExileFromGrave<\d+/([^/>]*)", cost)
    if m: out += ["cost:exile", "from_zone:graveyard", "cost_exile_target:" + tok(m.group(1).replace(";", "_or_").split(".")[0])]
    if "PayLife" in cost: out.append("cost:life")
    m = re.search(r"PayEnergy<(\d+)", cost)
    if m: out += ["cost:energy", "cost_energy:" + m.group(1)]
    if "Discard<" in cost: out.append("cost:discard")
    for m in re.finditer(r"AddCounter<(\d+)/LOYALTY>", cost): out += ["loyalty_change:+" + m.group(1), "counters:loyalty"]
    for m in re.finditer(r"SubCounter<(\d+)/LOYALTY>", cost): out += ["loyalty_change:-" + m.group(1), "counters:loyalty"]
    if re.search(r"SubCounter<\d+/(?!LOYALTY)", cost): out.append("cost:remove_counters")
    c2 = re.sub(r"\w+<[^>]*>", "", cost)
    if re.search(r"(^|\s)(\d+|X|[WUBRGC])(\s|$)", c2):
        out.append("cost:mana")
        out.append("cost_mana:" + "".join(re.findall(r"(?:^|\s)(\d+|X|[WUBRGC])(?=\s|$)", c2)).lower())      # the mana amount of the cost, symbols joined (2b = {2}{B}); user 2026-10-23 (P4c E)


PROP = {"CardPower": "power", "CardToughness": "toughness", "CardManaCost": "mana_value", "CardManaCostLKI": "mana_value", "DamageAmount": "damage", "LifeAmount": "life",
        "LifeGained": "life_gained", "xPaid": "x_paid", "YourLifeTotal": "your_life_total", "YourStartingLife": "your_starting_life", "LifeYouGainedThisTurn": "life_gained_this_turn",
        "LifeOppsLostThisTurn": "life_lost_by_opponents_this_turn", "Domain": "domain", "Converge": "colors_spent", "Party": "party_size", "ChosenNumber": "chosen_number",
        "Kicked": "kicked", "TimesKicked": "times_kicked", "CastTotalManaSpent": "mana_spent", "RememberedSize": "remembered_count", "RememberedNumber": "previous_result",
        "YouDrewThisTurn": "cards_drawn_this_turn", "CardsInYourHand": "cards_in_your_hand", "CardsInHand": "cards_in_hand", "Intensity": "intensity", "Amount": "amount",
        "CounterNum": "counters", "CardsDiscardedThisTurn": "cards_discarded_this_turn", "CardsDrawnThisTurn": "cards_drawn_this_turn"}
SRC = {"Targeted": "target", "ParentTargeted": "target", "TargetedLKI": "target", "TargetedPlayer": "target_player", "Sacrificed": "sacrificed", "TriggeredCard": "triggering",
       "TriggeredSpellAbility": "triggering", "TriggerCount": "triggering", "Remembered": "remembered", "ReplaceCount": "replaced", "Discarded": "discarded", "Exiled": "exiled"}
OPS = [(r"^Twice$", "times_2"), (r"^Thrice$", "times_3"), (r"^Times\.(\d+)$", "times_%s"), (r"^Plus\.(\d+)$", "plus_%s"), (r"^Minus\.(\d+)$", "minus_%s"), (r"^Half(Up|Down)$", "half_%s")]


VPROP = {"GreatestCardPower": "greatest_power", "GreatestCardManaCost": "greatest_mana_value", "GreatestCardToughness": "greatest_toughness", "Colors": "colors", "DifferentCardPower": "different_powers",
         "CardPower": "total_power", "CardToughness": "total_toughness", "CardManaCost": "total_mana_value", "CardTypes": "card_types", "CardCounters": "counters", "DifferentCardManaCost": "different_mana_values", "DifferentCardNames": "different_names"}


def readable_filter(f):
    f = re.sub(r"YouCtrl", "_you_control", f); f = re.sub(r"OppCtrl", "_opponents_control", f); f = re.sub(r"YouOwn", "_you_own", f)
    return filt(f)


def xdesc(v, sv, depth=0):
    """what a variable amount measures, as one readable tag value, read from the script's variable definition (Forge Count$/Targeted$/Sacrificed$/TriggerCount$/ReplaceCount$ ...):
    target_power, target_mana_value, sacrificed_power, triggering_damage, life_lost_by_opponents_this_turn, count_land_you_control, devotion_black, x_paid ...
    Arithmetic after '/' is appended (times_2, plus_1, half_up)."""
    if not v or re.fullmatch(r"[+-]?\d+", v) or depth > 3: return None
    body = sv.get(v.lstrip("+-"), v if "$" in v else "")
    if not body: return None
    base, *ops = body.split("/")
    m = re.match(r"^(\w+)\$(.*)$", base.strip())
    if not m: return None
    src, rest = m.group(1), m.group(2).strip()
    suffix = ""
    for o in ops:
        for rx, fmt in OPS:
            mm = re.match(rx, o.strip())
            if mm: suffix += "_" + (fmt % mm.group(1) if "%s" in fmt else fmt); break
    if src == "SVar":                                         # SVar$X/Twice: another variable, doubled etc.
        inner = xdesc(rest.split("/")[0], sv, depth + 1)
        return (inner + suffix) if inner else None
    if src in ("Number", "Compare") or not rest and src == "Number": return None
    if src == "Count":
        if rest.startswith(("Compare", "Kicked", "Condition")): return None        # conditional values (if X then a else b), not a measured amount
        if rest.startswith("Valid"):
            zone = {"ValidGraveyard": "graveyard", "ValidHand": "hand", "ValidLibrary": "library", "ValidExile": "exile", "Valid": "battlefield"}.get(re.match(r"^Valid\w*", rest).group(0), "battlefield")
            filt_, _, prop_ = re.sub(r"^Valid\w*\s*", "", rest).partition("$")
            where = readable_filter(filt_) + ("" if zone == "battlefield" else "_in_" + zone)
            if prop_:                                         # Count$Valid Creature.YouCtrl$GreatestCardPower = the greatest power among them, not how many
                head = VPROP.get(re.split(r"[ .]", prop_)[0], tok(prop_)[:30])
                return ("%s_among_%s" % (head, where) + suffix).replace("__", "_")
            return ("count_%s" % where + suffix).replace("count__", "count_")
        if rest.startswith("Devotion"): return "devotion_" + tok(rest.split(".", 1)[-1]) + suffix
        if rest.startswith("CardCounters"): return "counters_on_this_" + tok(rest.split(".", 1)[-1].replace("P1P1", "plus_one")) + suffix
        if rest.startswith("ThisTurn"): return "this_turn_" + tok(rest)[:44] + suffix
        key = re.split(r"[ .]", rest)[0]
        return PROP.get(key, tok(rest)[:44]) + suffix if key != "CardPower" else "own_power" + suffix
    word = SRC.get(src)
    if word:
        key = re.split(r"[ .]", rest)[0]
        prop = PROP.get(key)
        if rest.startswith("Valid"): return "%s_count_%s" % (word, readable_filter(re.sub(r"^Valid\w*\s*", "", rest))) + suffix
        if rest.startswith("CardCounters"): return "%s_counters_%s" % (word, tok(rest.split(".", 1)[-1].replace("P1P1", "plus_one"))) + suffix
        if prop: return "%s_%s" % (word, prop) + suffix
        return "%s_%s" % (word, tok(rest)[:36]) + suffix
    if src == "PlayerCountOpponents" or src.startswith("PlayerCount"): return "players_" + tok(rest)[:44] + suffix
    return tok(src + "_" + rest)[:48] + suffix


def x_is(v, sv):
    d = xdesc(v, sv)
    return d


def x_links(groups, links):
    """link each variable amount to what it measures: the amount tag (pump_amount:+x/+0, life_loss_amount:x, counter_count:x, damage_amount:x, draw_count:x ...) 'scales_with' its x_is tag,
    and an x_is that measures a target / sacrificed permanent / triggering object is linked to that object's tag"""
    for gid, ts in groups.items():
        main = gid.split(".")[0]
        for t in ts:
            if not t.startswith("x_is:"): continue
            for u in ts:
                if u != t and (re.search(r"(^|_)amount:|count:|pump_amount:", u) and (u.endswith(":x") or ":+x" in u or u.endswith("x/+0") or "x/" in u or u.endswith(":y"))):
                    links.append(("%s:%s" % (gid, u), "scales_with", "%s:%s" % (gid, t)))
            d = t[5:]
            target = next((("%s:%s" % (g, u)) for g in (gid, main) for u in groups.get(g, []) if u.startswith("target_type:")), None)
            if d.startswith(("target_", "target_player_")) and target: links.append(("%s:%s" % (gid, t), "measures", target))
            if d.startswith("sacrificed_"):
                sac = next((("%s:%s" % (g, u)) for g in (gid, main, "c0") for u in groups.get(g, []) if u.startswith(("cost_sacrifice_target:", "sacrifice_type:"))), None)
                if sac: links.append(("%s:%s" % (gid, t), "measures", sac))
        for u in ts:
            if u.endswith("_amount:equal_to_life_lost"):
                prev = next((("%s:%s" % (g, w)) for g, tw in groups.items() if g.split(".")[0] == main and g != gid for w in tw if w.startswith("life_loss_amount:")), None)
                if prev: links.append(("%s:%s" % (gid, u), "depends_on", prev))


def sign(v, sv, extra_tags):
    """+n / -n / +x for a pump amount; a variable also gets x_is:<what> in extra_tags"""
    if v is None: return "+0"
    if re.fullmatch(r"[+-]?\d+", v): return v if v[0] in "+-" else "+" + v
    w = x_is(v, sv)
    if w: extra_tags.append("x_is:" + w)
    return ("-" if v.startswith("-") else "+") + "x"


def present_tags(p, add):
    """one readable condition tag instead of present / zone / compare: condition:you_control_garruk_planeswalker, condition:no_card_you_own_in_library, condition:at_least_4_creature_you_control"""
    if "IsPresent" in p:
        what = readable_filter(p["IsPresent"].replace("YouCtrl", "you_control"))
        zone = tok(p["PresentZone"]) if p.get("PresentZone") and p["PresentZone"] != "Battlefield" else ""
        cmp_ = p.get("PresentCompare", "GE1")
        m = re.match(r"^(EQ|GE|LE|GT|LT)(\d+)$", cmp_)
        pre = "" if not m else {"EQ0": "no_", "GE1": ""}.get(cmp_, {"GE": "at_least_%s_", "LE": "at_most_%s_", "EQ": "exactly_%s_", "GT": "more_than_%s_", "LT": "fewer_than_%s_"}[m.group(1)] % m.group(2))
        add("condition:" + pre + what + ("_in_" + zone if zone else ""))


def affected_tags(p, add):
    a = p.get("Affected") or p.get("AffectedDefined") or ""
    if a in ("Self", "Card.Self", "Creature.Self") or a.startswith("Self"):
        add("affected_scope:self"); return
    for part in a.split(",")[:1]:
        bits = part.split("+"); main = bits[0].split(".")
        if main[0]: add("affected_type:" + tok(main[0]))
        for r in main[1:] + bits[1:]:
            if r in ("YouCtrl", "YouOwn"): add("affected_scope:you_control")
            elif r in ("OppCtrl",): add("affected_scope:opp_control")
            elif r in ("Other", "StrictlyOther"): add("affected_filter:other")
            elif r: add("affected_filter:" + filt(r))


def restrict_kinds(text):
    """what a restriction text (a HIDDEN keyword string, a static / replacement SVar, a description) forbids; the user's variables: A/B, A, B, doesn't untap, loses abilities"""
    t = text.lower()
    out = []
    if re.search(r"can't attack or block|cantattack,\s*cantblock|cantblock,\s*cantattack", t): out.append("cant_attack_or_block")
    else:
        if re.search(r"can't attack\b|mode\$ cantattack\b(?!unless)", t) and "cantattackunless" not in t: out.append("cant_attack")
        if re.search(r"can't block\b|mode\$ cantblock\b(?!by)", t): out.append("cant_block")
    if re.search(r"doesn't untap|event\$ untap", t): out.append("doesnt_untap")
    return out


def restrict_add(kinds, add, text=""):
    for k in kinds: add("restrict", "restrict_kind:" + k)
    t = text.lower()
    if "next untap step" in t: add("duration:next_untap")
    if "as long as you control" in t: add("duration:while_control")


def _owner_stated(text):
    """controller:owner only when the Oracle line says 'under its owner's control' (user 2026-10-22); otherwise controller:you"""
    o = next((l[7:] for l in text.split("\n") if l.startswith("Oracle:")), "")
    return bool(re.search(r"under (?:its|their) owner's control", o.replace("\\n", " "), re.I))


def extra(lines, sv, types, text):
    groups = {"c0": []}          # group id -> tags: c0 = card level, cN = the N-th A/S/T/R line (same numbering as tag_run clauses)
    cur = ["c0"]
    links = []
    def add(*t): groups[cur[0]].extend(t)
    def lk(a, rel, b): links.append(("%s:%s" % (cur[0], a), rel, "%s:%s" % (cur[0], b)))
    for l in lines:
        if l.startswith("Loyalty:"): add("loyalty:" + l[8:].strip(), "counters:loyalty")
        if l.startswith("Defense:"): add("defense:" + l[8:].strip())
    for l in lines:                                      # K:ETBReplacement:Other:<svar> with a Choose* effect: "as this enters, choose a colour / type / player ..." (replaces the opaque forge_line:etbreplacement)
        m = re.match(r"^K:ETBReplacement:\w+:(\w+)", l)
        sx = sv.get(m.group(1), "") if m else ""
        if "AlterAttribute" in sx and "Attributes$ Prepared" in sx: add("enters_prepared")
        pc_ = re.search(r"DB\$ PutCounter\b.*\bCounterType\$ (\w+(?:,\w+)+)", sx)   # 'enters with your choice of a deathtouch or a lifelink counter': a choice among counter types
        if pc_: add("choose_on_enter:option", "trigger:etb", *["choice_option:" + tok(o_) for o_ in pc_.group(1).split(",")])
        mm = re.search(r"DB\$ (Choose\w+|NamedCard|NameCard|GenericChoice)", sx)
        if mm:
            api_ = mm.group(1); ty_ = re.search(r"\bType\$ ([\w ]+?) ?(?:\||$)", sx)
            what = {"ChooseColor": "color", "ChoosePlayer": "player", "ChooseCard": "card", "ChooseNumber": "number", "NamedCard": "card_name", "NameCard": "card_name", "GenericChoice": "option", "ChooseDirection": "direction"}.get(api_)
            if api_ == "ChooseType": what = {"Creature": "creature_type", "Card": "card_type", "Basic Land": "basic_land_type", "Land": "land_type"}.get(ty_.group(1).strip() if ty_ else "", "type")
            if what:
                add("choose_on_enter:" + what, "trigger:etb")        # user (Cloud Key): ETB -> choice -> the choice drives the later effect
                vt_ = re.search(r"\bValidTypes\$ ([\w,]+)", sx)
                if vt_: add(*["choice_option:" + tok(o_) for o_ in vt_.group(1).split(",")])
                ch_ = re.search(r"\bChoices\$ ([\w,]+)", sx) if api_ == "GenericChoice" else None   # GenericChoice (Siege cards, Archangel of Strife): the options are SVar names
                if ch_: add(*["choice_option:" + tok(o_) for o_ in ch_.group(1).split(",")])
    if "AlternateMode:DoubleFaced" in text or "AlternateMode:Modal" in text: add("transform")
    if "Basic" in types.split() and "Land" in types.split():
        for t, c in (("Plains", "white"), ("Island", "blue"), ("Swamp", "black"), ("Mountain", "red"), ("Forest", "green")):
            if t in types.split(): add("mana_source", "mana:" + c, "mana_amount:1", "trigger:tap"); lk("mana_source", "produces", "mana:" + c)
    oracle = next((l[7:] for l in lines if l.startswith("Oracle:")), "")
    if re.search(r"enters(?: the battlefield)? tapped", oracle) and "Basic" not in types.split():
        add("enters_tapped_conditional" if re.search(r"enters(?: the battlefield)? tapped unless|you may pay \d+ life\. If you don't", oracle) else "enters_tapped")
    elif "Land" in types.split(): add("enters_untapped")
    if "Land" in types.split() and re.search(r"deals? \d+ damage to you|you may pay \d+ life\. If you don't", oracle): add("cost:life")   # painlands, shocklands, City of Brass: a life cost with no Pay cost in the script (user 2026-10-27, land priority H91)
    if {"Land", "Artifact"} & set(types.split()) and "Creature" not in types.split() and any(re.match(r"^[^:]*\{[0-9WUBRGCX]\}[^:]*: Add .*(\{[WUBRG]\}|any (color|colour|one color))", seg) for seg in re.split(r"\\n|\n", oracle)): add("mana_filter")   # pays mana to change mana colour: neutral mana, tilts colour coverage (user 2026-10-27)
    _nr = re.sub(r"\([^)]*\)", "", oracle)   # reminder text out
    for seg in re.split(r"\\n|\n", _nr):
        cost, _, eff = seg.partition(":")
        if (re.match(r"^[^:{]*\{[0-9WUBRGCX/]+\}", cost) and eff and "{T}" not in cost and not seg.startswith(("Equip", "Cycling", "Crew", "Channel", "Reconfigure", "Ninjutsu", "Level", "Unearth", "Flashback", "Escape", "Landcycling"))
                and not eff.startswith(" Add ") and not re.search(r"(?i)sacrifice|exile|discard|\{Q\}|tap an untapped|pay \d+ life", cost)
                and not re.search(r"(?i)only once|once (?:each|per) turn|only (?:one|a single) time|\bgains?\b|\bhas\b|\bhave\b|\bbecomes?\b|transform|\badapt\b|monstrosity|renown|\bregenerate", eff)):
            add("mana_sink"); break   # an activated ability with a mana-only cost and no tap, repeatable (no sacrifice cost, keyword grant or transform): a mana dump (user 2026-10-27)
    bodies = []
    for l in lines:
        m = re.match(r"^(A|S|T|R):(.*)$", l)
        if m: bodies.append((m.group(1), m.group(2), l))
    gids = {}                                    # body index -> group id (saga chapters get s<i>)
    for l in lines:
        mc = re.match(r"^K:Chapter:(\d+):(.*)$", l)
        if mc:
            for i, svn in enumerate(mc.group(2).split(","), 1):
                if svn in sv:
                    bodies.append(("C", sv[svn], l)); gids[len(bodies)] = "s%d" % i
    seen_sv = set()
    def chain(b):
        out = [b]
        p = params(b)
        for k in ("Execute", "SubAbility", "Choices", "RepeatSubAbility", "FallbackAbility", "TrueSubAbility", "FalseSubAbility"):
            for nx in re.split(r"[ ,]+", p.get(k, "")):
                if nx in sv and nx not in seen_sv:
                    seen_sv.add(nx); out += chain(sv[nx])
        return out
    for n_, (kind, body, line) in enumerate(bodies, 1):
        cur[0] = gids.get(n_, "c%d" % n_)
        groups.setdefault(cur[0], [])
        p = params(body)
        if kind == "C": add("saga_chapter")
        if kind == "A": cost_tags(p.get("Cost", ""), groups[cur[0]])
        if "Sac<" in line and "cost:sacrifice" not in groups[cur[0]]: add("cost:sacrifice")
        if "Discard<" in line and "cost:discard" not in groups[cur[0]]: add("cost:discard")
        if kind == "T":
            mode = p.get("Mode", "")
            if mode in ("ChangesZone", "ChangesZoneAll"):
                o, d = p.get("Origin", "Any"), p.get("Destination", "")
                add("trigger_scope:self" if "Card.Self" in p.get("ValidCard", "") else "trigger_scope:other")
                if d == "Battlefield": add("trigger:etb")
                elif o == "Battlefield" and d == "Graveyard": add("trigger:dies", "trigger_zone:graveyard")
                elif o == "Battlefield": add("trigger:leaves")
            elif mode in ("SpellCast", "SpellCastOrCopy"):
                add("trigger:spell_cast")
                for tf in spell_filters(p.get("ValidCard", "")): add("trigger_filter:" + tf)      # Card.nonCreature -> noncreature (negation is part of the value, P4c B)
            elif mode in ("Attacks", "AttackersDeclared", "AttackerBlocked", "AttackerUnblocked"): add("trigger:attacks" if mode in ("Attacks", "AttackersDeclared") else "trigger:" + tok(mode))
            elif mode == "Discarded": add("trigger:discard")
            elif mode == "DiscardedAll": add("trigger:discard", "trigger_filter:one_or_more")
            elif mode in ("DamageDone", "DamageDoneOnce"): add("trigger:combat_damage" if p.get("CombatDamage") == "True" else "trigger:damage_dealt")
            elif mode == "Blocks": add("trigger:blocks")
            elif mode == "Cycled": add("trigger:cycled")
            elif mode == "CounterAddedOnce": add("trigger:counter_added")
            elif mode == "ManaExpend": add("trigger:mana_spent")
            elif mode == "Always": add("trigger:state")
            elif mode == "Destroyed" and "Self" in p.get("ValidCard", ""): add("trigger:dies")
            elif mode == "LifeGained": add("trigger:gain_life")
            elif mode == "Phase" and p.get("Phase") == "BeginCombat": add("trigger:beginning_of_combat")
            elif mode == "Phase" and p.get("Phase") == "Upkeep": add("trigger:upkeep")
        if kind == "S":
            mode = p.get("Mode", "")
            if mode == "MustAttack":
                add("must_attack")
                for ty in re.findall(r"[A-Z][a-z]+", p.get("ValidCreature", "")):
                    if ty not in ("Creature", "Other", "You", "Ctrl"): add("affects:" + tok(ty))
            if p.get("AddType") and mode == "Continuous": [add("grant_type:" + tok(x)) for x in p["AddType"].split(" & ")]
            if mode == "CantBlock":
                if p.get("ValidCreature", p.get("ValidAttacker", "Creature")) not in ("Card.Self", "Creature.Self"): add("restrict")
            if mode == "CantBlockBy" and not p.get("ValidBlocker") and "Self" not in p.get("ValidAttacker", ""): add("cant_be_blocked")      # equipped / enchanted creature can't be blocked: evasion, not a restriction
            if mode == "ReduceCost":
                vc = p.get("ValidCard", "")
                add("cost_reduce", "duration:static")      # user (Cloud Key): the reduction is a static ability
                if p.get("Amount", "").isdigit(): add("cost_reduce_amount:" + p["Amount"])
                if "ChosenType" in vc: add("cost_reduce_for:chosen_type"); links.append(("%s:cost_reduce_for" % cur[0], "uses", "c0:choose_on_enter"))
                if p.get("Amount", "").isdigit() and not re.search(r"Color|Black|White|Blue|Red|Green", vc): add("cost_reduce_mana:generic")
                for ty in re.findall(r"[A-Z][a-z]+", vc):
                    if ty in ("Creature", "Artifact", "Enchantment", "Instant", "Sorcery", "Planeswalker", "Land"): add("cost_reduce_for:" + tok(ty)); lk("cost_reduce", "filters", "cardtype:" + tok(ty))
                    elif ty not in ("Card", "Spell", "Other", "You", "Ctrl", "Chosen", "Type", "White", "Blue", "Black", "Red", "Green", "Colorless", "Non", "Self", "Opp") and "," in vc + ",": add("cost_reduce_for:" + tok(ty))
                    elif ty in ("White", "Blue", "Black", "Red", "Green", "Colorless"): add("color:" + tok(ty)); lk("cost_reduce", "filters", "color:" + tok(ty))
        if kind == "S" and p.get("Mode") == "Continuous" and p.get("CharacteristicDefining") == "True" and p.get("SetPower"):   # Adeline: power = creatures you control
            m_ = re.match(r"Count\$Valid ([A-Za-z]+)\.YouCtrl$", sv.get(p["SetPower"], ""))
            if m_: add("power_scales:%ss_you_control" % tok(m_.group(1)))
        if kind == "S" and p.get("Mode") == "Continuous":
            xt = []
            if "AddPower" in p or "AddToughness" in p:
                add("duration:static", "pump_amount:%s/%s" % (sign(p.get("AddPower"), sv, xt), sign(p.get("AddToughness"), sv, xt)))
            for k in ("AddKeyword", "AddHiddenKeyword"):
                for kw_ in re.split(r"\s*&\s*", p.get(k, "")):
                    if kw_: add("grant_kw:" + tok(kw_.split(":")[0]), "duration:static")
            affected_tags(p, add); present_tags(p, add); add(*xt)
        if kind == "S" and re.fullmatch(r"Cant\w+(,Cant\w+)*", p.get("Mode", "")) and {"CantAttack", "CantBlock", "CantBeActivated"} & set(p["Mode"].split(",")):
            modes = set(p["Mode"].split(","))
            ks = (["cant_attack_or_block"] if {"CantAttack", "CantBlock"} <= modes else ["cant_attack"] * ("CantAttack" in modes) + ["cant_block"] * ("CantBlock" in modes)) + ["cant_activate"] * ("CantBeActivated" in modes)
            restrict_add(ks, add, p.get("Description", ""))
            vc = p.get("ValidCard", p.get("ValidCreature", ""))
            if "Self" in vc: add("restrict_scope:self")                   # a drawback on the card itself (Bloodghast: can't block)
            else: affected_tags({"Affected": vc}, add)
        if kind == "S" and p.get("Mode") == "CantBlockBy" and "Self" not in p.get("ValidAttacker", "") and p.get("ValidBlocker"):
            restrict_add(["cant_block"], add, p.get("Description", "")); affected_tags({"Affected": p["ValidBlocker"].split(",")[0]}, add)   # these creatures can't block (Bower Passage)
        if kind == "S" and p.get("Mode") == "CantAttackUnless": add("restrict", "restrict_kind:cant_attack_unless_cost", *(["unless_cost_amount:" + compact_mana(p["Cost"])] if compact_mana(p.get("Cost", "")) else []))
        if kind == "S" and p.get("Mode") == "Continuous" and "doesn't untap" in p.get("AddHiddenKeyword", "").lower():
            restrict_add(["doesnt_untap"], add, p.get("AddHiddenKeyword", "")); affected_tags(p, add)
        if kind == "S" and p.get("Mode") == "CantBlockBy" and "Self" in p.get("ValidAttacker", ""):
            add("cant_be_blocked:by_" + tok(p.get("ValidBlocker", "").replace(".", "_")))
        if kind == "R":
            ev = p.get("Event", "")
            if ev == "Counter" and "Self" in p.get("ValidCard", "") and p.get("Layer") == "CantHappen": add("cant_be_countered")
            elif ev == "Untap" and p.get("Layer") == "CantHappen":
                restrict_add(["doesnt_untap"], add, p.get("Description", "")); affected_tags({"Affected": p.get("ValidCard", "")}, add)
            elif ev == "AddCounter" and re.search(r"ReplaceCount\$CounterNum/Plus\.(\d+)", "\n".join(sv.values()) if False else sv.get((re.search(r"Amount\$ (\w+)", sv.get(p.get("ReplaceWith", ""), "")) or [0, ""])[1], "")):
                # "if counters would be put on a permanent you control, that many plus N are put instead" (user: static ability, replace effect, N+1 counters)
                nn = re.search(r"Plus\.(\d+)", sv[re.search(r"Amount\$ (\w+)", sv[p["ReplaceWith"]]).group(1)]).group(1)
                add("duration:static", "replace:add_counters_plus_" + nn)
                if p.get("ValidCounterType"): add("counter:" + tok(p["ValidCounterType"]))
                affected_tags({"Affected": p.get("ValidCard", "").replace("+inZoneBattlefield", "")}, add)
            elif ev:
                rw = sv.get(p.get("ReplaceWith", ""), "")
                api_ = (re.match(r"^DB\$ (\w+)", rw) or [0, ""])[1]
                rp = re.search(r"Amount\$ (\w+)", rw)
                det = tok(sv[rp.group(1)].split("$", 1)[-1])[:40] if rp and rp.group(1) in sv else ""
                if not (ev == "Moved" and (api_ == "Tap" or "Exile" in rw)):          # enters tapped / dies-exiled already have enters_tapped / die_replace:exile
                    add("replace:%s_to_%s%s" % (tok(ev), tok(api_) or "other", "_" + det if det else ""))      # one tag: event replaced, what happens instead, detail
                present_tags(p, add)
        if kind == "R" and p.get("Event") == "Moved" and p.get("Destination") == "Graveyard":
            if "Exile" in sv.get(p.get("ReplaceWith", ""), ""): add("die_replace:exile")
        main_gid = cur[0]
        pos = neg = 0
        unk = False
        sacgid = None
        last_exile = "x"
        desc_main = p.get("SpellDescription", "") + p.get("Description", "") + p.get("TriggerDescription", "")
        for m_ in re.finditer(r"Sac<(\d+)/", line): neg += int(m_.group(1))
        for m_ in re.finditer(r"Discard<(\d+)/", line): neg += int(m_.group(1))
        is_spell = kind == "A" and body.startswith("SP$") and any(t in types.split() for t in ("Instant", "Sorcery"))
        if is_spell: neg += 1
        def cnt(s, dflt=1):
            global_unk[0] = global_unk[0] or not (s or "").isdigit() and s not in (None, "")
            return int(s) if (s or "").isdigit() else dflt
        global_unk = [False]
        for ci, b in enumerate(chain(body)):
            cur[0] = main_gid if ci == 0 else "%s.%d" % (main_gid, ci + 1)
            groups.setdefault(cur[0], [])
            bp = params(b)
            api = (re.match(r"^(?:AB|SP|DB)\$ (\w+)", b) or [0, ""])[1]
            if not (kind == "T" and b is body): target_tags(bp, groups[cur[0]], api)   # a trigger line's ValidCard(s) filter describes the event, not a target
            if bp.get("ValidTgts") and bp.get("Origin") in ("Graveyard", "Exile", "Hand", "Library"): add("target_zone:" + bp["Origin"].lower())
            if api == "ManaReflected":                         # Fellwar Stone, Exotic Orchard: the colours come from lands (their controller says whose)
                add("mana_source", "mana_choice", "mana_amount:1", "produce_colors:" + ("opp_lands_can" if "OppCtrl" in bp.get("Valid", "") else "your_lands_can" if "YouCtrl" in bp.get("Valid", "") else "lands_can"))
            if api == "WinsGame": add("win:alt_condition")      # Happily Ever After, Thassa's Oracle: a card that wins the game outright (the condition is its trigger or cost)
            if api == "Effect" and bp.get("Triggers"):          # a one-shot spell that sets up a delayed trigger (Ondu Rising: whenever a creature attacks this turn, it gains lifelink)
                for nm_ in re.split(r"[ ,]+", bp["Triggers"]):
                    tp_ = params(sv.get(nm_, ""))
                    for ex_ in [params(sv.get(tp_.get("Execute", ""), ""))]:
                        if ex_.get("KW") and "Attacker" in ex_.get("Defined", ""):
                            for kw_ in re.split(r"\s*&\s*", ex_["KW"]): add("grant_kw:" + tok(kw_.split(":")[0]))
                            add("target_scope:attackers")
            if api == "Mana":
                pr = bp.get("Produced", "")
                add("mana_source")
                if pr.startswith("Combo"):
                    rest = pr[5:].strip()
                    if rest == "ColorIdentity": add("mana:commander_identity", "mana_choice"); links.append(("mana_source", "produces", "mana:commander_identity"))
                    elif rest == "Any": add("mana:any", "mana_choice")
                    else:
                        for c in rest.split(): 
                            if c in COLORS: add("mana:" + COLORS[c]); links.append(("mana_source", "produces", "mana:" + COLORS[c]))
                        add("mana_choice")
                elif pr == "Any": add("mana:any")
                else:
                    for c in pr.split():
                        if c in COLORS: add("mana:" + COLORS[c]); links.append(("mana_source", "produces", "mana:" + COLORS[c]))
                add("mana_amount:" + (bp.get("Amount", "1").lower() if bp.get("Amount", "1").isdigit() or not x_is(bp.get("Amount"), sv) else "x"))      # a variable amount is x whatever the script calls it (Y, Z ...)
                if not bp.get("Amount", "1").isdigit() and x_is(bp.get("Amount"), sv): add("x_is:" + x_is(bp.get("Amount"), sv))
                if "RestrictValid" in bp:           # value = what the mana can be spent on (instant_or_sorcery, creature_spell, activated_ability ...)
                    rv_ = []
                    for part_ in bp["RestrictValid"].split(","):
                        if part_.startswith("Spell."): w_ = part_[6:].split("+")[0]; rv_.append(("non" + w_[3:].lower() if w_.startswith("non") else w_.lower()) + ("_spell" if w_.lower() in ("creature", "artifact", "legendary", "noncreature") else ""))
                        elif part_.startswith("Activated"): rv_.append("activated_ability")
                        else: rv_.append(tok(part_))
                    add("mana_restriction:" + "_or_".join(dict.fromkeys(rv_)))
                if "IsPresent" in bp or "ConditionPresent" in bp: add("activation_restriction")
            if "IsPresent" in bp and api != "Mana" and kind == "A": add("activation_restriction")
            if api == "ChangeZone" or api == "ChangeZoneAll":
                o, d = bp.get("Origin", ""), bp.get("Destination", "")
                for w_ in re.findall(r"cmc(Even|Odd)", bp.get("ChangeType", "")): add("target_filter:%s_mana_value" % w_.lower())      # Desecrate Reality: return a permanent with an odd mana value
                if o == "Library" and bp.get("Defined") == "TopOfLibrary":       # the top card, not a search (Herald's Horn): no tutor tags
                    add("take:may_1_chosen_type" if "ChosenType" in bp.get("ConditionPresent", "") else "take:1", "to_zone:" + tok(d))
                elif o == "Library":
                    add("tutor")
                    n = bp.get("ChangeNum", "1")
                    add("tutor_count:" + ("up_to_" + n if n.isdigit() and int(n) > 1 else n))
                    ct = bp.get("ChangeType", "")
                    add("tutor_target:" + tok(ct.replace("Land.Basic", "basic_land").split("+")[0]))
                    dest = {"Battlefield": "battlefield_tapped" if bp.get("Tapped") == "True" else "battlefield", "Hand": "hand"}.get(d, tok(d))
                    add("tutor_dest:" + dest)
                    desc = bp.get("SpellDescription", "") + line
                    if "shuffle" in desc.lower(): add("shuffle")
                elif o == "Battlefield" and d == "Exile": add("remove:exile")
                elif o == "Battlefield" and d == "Hand": add("remove:bounce")
                elif o == "Battlefield" and d == "Library": add("remove:tuck")
                elif o == "Graveyard" and d == "Hand" and bp.get("Defined", "").startswith("TriggeredNewCard"): add("recursion:return_self")
                if o in ("Graveyard", "Exile") and d in ("Hand", "Library"): add("return", "from_zone:" + o.lower(), "to_zone:" + d.lower())     # readable detail for the AI umbrella tag recursion
                if o == "Hand" and d == "Exile": add("impulse_draw_part:exile_hand")
                if d == "Battlefield" and o in ("Library", "Hand", "Graveyard", "Exile"):
                    add("put_onto_battlefield", "from_zone:" + o.lower())
                    if bp.get("Tapped") == "True": add("put_tapped")
                    add("controller:owner" if (bp.get("GainControl") != "True" and _owner_stated(text)) else "controller:you")      # who controls it on the battlefield (reanimate is derived from put_onto_battlefield + from_zone:graveyard)
                if o == "Library" and d in ("Hand", "Battlefield"): pos += cnt(bp.get("ChangeNum", "1"))
                elif o in ("Graveyard", "Exile") and d in ("Hand", "Battlefield") and bp.get("Defined") != "ExiledWith":
                    pos += cnt(bp.get("TargetMax", bp.get("ChangeNum", "1")))
                if d == "Exile" and o in ("Graveyard", "Hand", "Library"): add("exile_from:" + o.lower())
                if "shuffle" in (bp.get("SpellDescription", "") + line).lower(): add("shuffle")
            if api in ("Destroy", "DestroyAll"): add("remove:destroy")
            if api in ("DealDamage", "DamageAll"):
                add("damage")
                if bp.get("NumDmg", "").isdigit(): add("damage_amount:" + bp["NumDmg"])
                if "ReplaceDyingDefined" in bp: add("die_replace:exile")
            if api == "Sacrifice":
                add("effect:sacrifice"); sacgid = cur[0]
                if bp.get("Defined", "You") in ("You", "Player"): neg += 1
                if re.search(r"Sacrifice[^.]*\.\s*If you do", desc_main): add("cost:sacrifice", "cost_if_you_do")
                if "SacValid" in bp and tok(bp["SacValid"].split(".")[0]) != "land": add("sacrifice_outlet")
                if bp.get("Defined") in ("Player", "Opponent", "Player.Opponent"):
                    add("remove:sacrifice")
                if "SacValid" in bp: add("sacrifice_type:" + tok(bp["SacValid"].split(".")[0]))
            if bp.get("ConditionDefined") == "Remembered" and api == "Token" and sacgid: links.append(("%s:token_make" % cur[0], "conditional_on", "%s:effect:sacrifice" % sacgid))
            if api == "ChangeZone" and bp.get("Defined") == "ExiledWith": add("return_exiled"); lk("return_exiled", "pairs_with", "trigger:leaves")
            if api == "Dig": last_exile = bp.get("DigNum", "1")
            if api == "ChangeZoneAll" and bp.get("Destination") == "Exile": last_exile = "x"
            if api == "ChangeZone" and bp.get("Destination") == "Exile": last_exile = bp.get("ChangeNum", "1")
            if api == "Effect":
                if any("Mode$ BecomeMonarch" in sv.get(t_, "") for t_ in re.split(r"[ ,]+", bp.get("Triggers", ""))): add("duration:until_monarch_changes")      # Palace Jailer: exiled until an opponent becomes the monarch
                for sname in re.split(r"[ ,]+", bp.get("StaticAbilities", "")):
                    if "MayPlay" in sv.get(sname, ""):
                        add("impulse_draw", "impulse_draw_count:" + str(last_exile).lower())
                        if str(last_exile).isdigit(): pos += int(last_exile)
                        else: global_unk[0] = True
                        lk("impulse_draw", "pairs_with", "impulse_draw_count:" + str(last_exile).lower())
                        d = bp.get("Duration", "")
                        add({"UntilTheEndOfYourNextTurn": "duration:next_turn_end", "EndOfTurn": "duration:eot"}.get(d, "duration:eot" if not d else "duration:" + tok(d)))
            xt2 = []
            if api in ("GainLife", "LoseLife"):
                la = bp.get("LifeAmount", "")
                key_ = "lifegain_amount" if api == "GainLife" else "life_loss_amount"
                if la.isdigit(): add("%s:%s" % (key_, la))
                elif la == "AFLifeLost" or sv.get(la, "").startswith("Number$0"): add("%s:equal_to_life_lost" % key_)
                else:
                    add("%s:x" % key_)
                    w = x_is(la, sv)
                    if w: add("x_is:" + w)
            if api in ("Pump", "PumpAll") and ("NumAtt" in bp or "NumDef" in bp):
                add("pump_amount:%s/%s" % (sign(bp.get("NumAtt"), sv, xt2), sign(bp.get("NumDef"), sv, xt2))); add(*xt2)
            if api == "PumpAll" and "Duration" not in bp: add("duration:eot")      # team pump: who is pumped is in the target_* tags (target_count:all, type, scope, filter)
            if api in ("PutCounter", "PutCounterAll") and bp.get("CounterNum"):
                cn = bp["CounterNum"]
                add("counter_count:" + (cn if cn.isdigit() else "x"))
                w = x_is(cn, sv)
                if w: add("x_is:" + w)
            if api == "DealDamage" and not bp.get("NumDmg", "1").isdigit():
                w = x_is(bp.get("NumDmg"), sv)
                if w: add("damage_amount:x", "x_is:" + w)
            if api in ("Pump", "PumpAll") and ("HIDDEN" in bp.get("KW", "") or "can't" in bp.get("KW", "").lower()):
                ks = restrict_kinds(bp["KW"])
                restrict_add(ks, add, bp["KW"] + " " + bp.get("SpellDescription", ""))
                if ks and not any(x.startswith("duration:") for x in groups[cur[0]]):
                    add("duration:" + ({"Permanent": "permanent"}.get(bp.get("Duration", ""), "eot")) if "next untap step" not in bp["KW"].lower() else "duration:next_untap")
            if api == "Effect":
                for nm in re.split(r"[ ,]+", bp.get("StaticAbilities", "") + " " + bp.get("ReplacementEffects", "")):
                    ks = restrict_kinds(sv.get(nm, ""))
                    if ks: restrict_add(ks, add, sv.get(nm, "") + " " + bp.get("Duration", "").replace("AsLongAsControl", "as long as you control") + " " + bp.get("SpellDescription", ""))
            for nm in re.split(r"[ ,]+", bp.get("StaticAbilities", "")):
                cb = params(sv.get(nm, ""))
                if cb.get("Mode") != "CantBlockBy": continue
                # Rogue's Passage: the remembered creature can't be blocked this turn; with a ValidBlocker it is only unblockable by those blockers (the static-ability branch above does the same)
                add(*(["cant_be_blocked:by_" + tok(cb["ValidBlocker"].replace(".", "_"))] if cb.get("ValidBlocker") else ["cant_be_blocked"]), "duration:eot")
            if api == "Protection":
                add("grant_kw:protection", "duration:" + ({"Permanent": "permanent"}.get(bp.get("Duration", ""), "eot")))
                g_ = bp.get("Gains", "")
                if g_.startswith("Choice"): add("protection_from:choice")      # Shelter: protection from the color of your choice
                elif g_: add("protection_from:" + tok(g_))
            if api == "Animate" and bp.get("RemoveAllAbilities") == "True":
                add("restrict", "restrict_kind:loses_abilities", "duration:permanent" if bp.get("Permanent") == "True" else "duration:eot")
            if api in ("Pump", "PumpAll") and bp.get("KW"):
                for kw_ in re.split(r"\s*&\s*", bp["KW"]):
                    if kw_ and not kw_.startswith("HIDDEN"): add("grant_kw:" + tok(kw_.split(":")[0]))
                add("duration:" + ({"EndOfTurn": "eot", "Permanent": "permanent"}.get(bp.get("Duration", ""), tok(bp["Duration"])) if bp.get("Duration") else "eot"))
            if api == "Charm":                                    # one tag: how many modes are chosen of how many (modal:1_of_3), instead of separate count and choose tags
                nmodes = len(re.split(r"[ ,]+", bp.get("Choices", ""))) if bp.get("Choices") else 0
                add("modal:%s_of_%d" % (bp.get("CharmNum", "1").lower().replace("x", "x"), nmodes))
            if api == "Dig":                                      # look_top:N + ONE take tag (count, filter, destination, optional) + the rest
                ncards = bp.get("ChangeNum", "1").lower()
                tk = ncards + ("_" + filt(bp["ChangeValid"]) if bp.get("ChangeValid") else "")
                add("look_top:" + bp.get("DigNum", "1").lower(), "take:" + ("may_" if bp.get("Optional") == "True" else "") + tk, "to_zone:" + (tok(bp["DestinationZone"]) if bp.get("DestinationZone") else "hand"))
                if bp.get("DestinationZone2"): add("rest_to_zone:" + tok(bp["DestinationZone2"]), *(["rest_order:" + ("bottom_random" if bp.get("RestRandomOrder") == "True" else "bottom")] if bp.get("LibraryPosition") == "-1" else []))
            if api == "PeekAndReveal": add("look_top:" + bp.get("PeekAmount", "1").lower(), "reveal")
            if api == "Investigate": add("investigate")                               # P4c D, user 2026-10-23
            if bp.get("Bolster", "").isdigit(): add("bolster:" + bp["Bolster"])       # P4c D: bolster N
            if api == "BecomeMonarch": add("monarch")                                 # P4c D
            if ci > 0 and b.startswith("AB$") and bp.get("Cost"): cost_tags(bp["Cost"], groups[cur[0]])      # a cost paid inside a trigger's sub-ability (Nazar: you may remove three counters)
            if bp.get("DefinedPlayer") == "Player.Other":
                add("target_scope:each_other_player")
                if bp.get("ChangeType"): add("target_type:" + tok(bp["ChangeType"].split(".")[0]))
                if " may " in " " + desc_main.lower() + " ": add("optional")
            if bp.get("TargetsForEachPlayer") == "True": add("target_scope:each_opponent")
            if api == "TwoPiles": add("piles_split:" + (tok(bp.get("Separator", "")) or "you"))       # one tag: who splits the cards into two piles (opponent / you)
            if api == "Token":
                token_tags(bp, groups[cur[0]])
                ta = bp.get("TokenAmount", "1")
                if not ta.isdigit() and x_is(ta, sv): add("x_is:" + x_is(ta, sv))
                if bp.get("TokenOwner", "You") == "You": pos += 0.5 * cnt(bp.get("TokenAmount", "1"))   # tokens count half (user)
            if api == "Draw":
                nd = bp.get("NumCards", "1"); add("draw_count:" + (nd if nd.isdigit() else "x"))
                if not nd.isdigit() and x_is(nd, sv): add("x_is:" + x_is(nd, sv))
                if bp.get("Defined", "You") == "You": pos += cnt(nd)
            if api == "Scry":
                ns = bp.get("ScryNum", "1"); add("scry_count:" + (ns if ns.isdigit() else "x"))
                if not ns.isdigit() and x_is(ns, sv): add("x_is:" + x_is(ns, sv))
            if api == "Discard":
                nd = bp.get("NumCards", "1"); add("discard_count:" + (nd if nd.isdigit() else "x"))
                if not nd.isdigit() and x_is(nd, sv): add("x_is:" + x_is(nd, sv))
                if bp.get("Defined", "You") == "You": neg += cnt(nd)
                if re.search(r"Discard[^.]*\.\s*If you do", desc_main): add("cost:discard", "cost_if_you_do")
            if api == "Mill":                                     # mtg2llm gap record, approved 2026-10-27: amount only (who stays with mill / self_mill)
                nm = bp.get("NumCards", "1"); add("mill_count:" + (nm if nm.isdigit() else "x"))
                if not nm.isdigit() and x_is(nm, sv): add("x_is:" + x_is(nm, sv))
            if api == "FlipCoin":
                add("flip_coin")
                if "WinSubAbility" in bp: add("flip_win")
                if "LoseSubAbility" in bp: add("flip_lose")
            if api in ("ChooseNumber", "ChooseCard", "ChoosePlayer") and bp.get("Secretly") == "True": add("secret_choice:" + {"ChooseNumber": "number", "ChooseCard": "card", "ChoosePlayer": "player"}[api])
            if api == "LosesGame": add("lose_game")
            if api == "RemoveCounter":
                nr = bp.get("CounterNum", "1"); add("counter_remove:" + (nr if nr.isdigit() else "all" if nr == "All" else "x"))
            if api == "Incubate": add("token_make", "token_type:incubator", "counter:p1p1", "counter_count:" + (bp.get("Amount", "1") if bp.get("Amount", "1").isdigit() else "x"))
            if api == "SetState" and bp.get("Mode") == "Transform": add("transform")       # "Transform CARDNAME" step of an ability (Mysterious Tome)
            if api == "CopyPermanent": add("token_make", "token_type:copy"); pos += 0.5
            if api == "Play" and bp.get("WithoutManaCost") == "True": add("cast_free")
            if api == "ExchangeControl": add("exchange_control", "steal"); lk("exchange_control", "pairs_with", "steal")
            if api == "GainControl":
                add("steal")
                if "AddKWs" in bp: add("steal_grants_" + tok(bp["AddKWs"])); lk("steal", "pairs_with", tok(bp["AddKWs"]))
                if bp.get("LoseControl") == "EOT": add("duration:eot")
            if api == "Animate":
                if bp.get("RemoveAllAbilities") == "True": add("loses_all_abilities")
                if bp.get("RemoveAllAbilities") == "True" and not (bp.get("Types") or bp.get("Colors")):
                    add("loses_all_abilities")                  # a curse that only removes abilities (Merfolk Trickster) does not make the permanent something else
                elif bp.get("Types") or bp.get("RemoveAllAbilities") == "True" or bp.get("Colors"):
                    add("transform")
                    for ty in (bp.get("Types", "")).split(","):
                        if ty: add("becomes:" + tok(ty))
                else:
                    gt = []                                   # gives an ability or trigger, no change of what the permanent is (Feign Death)
                    for tn in re.split(r"[ ,]+", bp.get("Triggers", "")):
                        t_ = sv.get(tn, "")
                        if "Origin$ Battlefield" in t_ and "Destination$ Graveyard" in t_: gt.append("dies_trigger")
                        elif t_: gt.append(tok((re.search(r"Mode\$ (\w+)", t_) or [0, "trigger"])[1]) + "_trigger")
                    add(*("grant_ability:" + g for g in gt)) if gt else add("grant_ability:other")
            if api == "PutCounter" or api == "PutCounterAll":
                if bp.get("CounterType"): add("counter:" + tok(bp["CounterType"]))
            if api == "CopyPermanent" and bp.get("AtEOT") == "Sacrifice": add("delayed:end_step", "effect:sacrifice", "duration:end_step")
            if "KW" in bp and "can't block" in bp["KW"]:
                if "ValidTgts" in bp or bp.get("Defined") == "Targeted": add("restrict")   # can't-block effect on other creatures (user)
            if "MayPlay" in b or "MayPlay$" in b: add("impulse_draw")
        cur[0] = main_gid
        if global_unk[0]: groups[main_gid].append("tempo:x")                     # unknown amount is tracked too (user)
        elif pos - neg > 0: groups[main_gid].append("tempo:+%g" % (pos - neg))   # known amounts only when positive; tempo 0 and negative are not tagged (user)
    if "Land" in types.split():   # user 2026-10-27: Forbidden Orchard gives the opponent the token (not a token maker); Dark Depths is a mana dump (mana_sink, counter_remove), not negative tempo
        gives_opp = re.search(r"(target|each) opponent creates", oracle)
        setup = re.search(r"enters with \w+ [\w ]*counters", oracle) and re.search(r"\{\d+\}: Remove a[n]? [\w ]*counter", oracle)
        g0 = next(iter(groups), "m1")
        if gives_opp:
            for ts in groups.values(): ts[:] = [t for t in ts if not (t == "token_make" or t.startswith("token_") or t.startswith("tempo:"))]
            groups[g0] = groups.get(g0, []) + ["tempo:negative", "gives_opponent_token"]
        if setup:   # user 2026-10-27: not a negative-tempo or setup tag; a mana dump with counter move/remove synergy
            groups[g0] = groups.get(g0, []) + ["setup_card:mana", "counter_remove"]
    _nt = {"Creature", "Noncreature", "Artifact", "Enchantment", "Land", "Instant", "Sorcery", "Planeswalker", "Legendary", "Nonland", "Historic", "Permanent", "Spell", "Colorless", "White", "Blue", "Black", "Red", "Green", "Multicolored", "Basic", "Snow", "Equipment", "Aura", "Vehicle", "Saga", "Food", "Clue", "Treasure", "Battle", "Kindred", "Tribal", "Token", "Other", "Another", "Each", "Target", "Any", "That", "This", "Face"}
    _rt = []   # user 2026-10-27: mana or a return ability that names a creature type works only for that type (Haven of the Spirit Dragon); the builder gives it support only when the deck has the type
    for _m in re.finditer(r"[Ss]pend this mana only to cast (?:an? )?([A-Z][a-z]+)(?: or ([A-Z][a-z]+))?(?: creature)? spells?", oracle):
        _rt += [g for g in _m.groups() if g]
    for _m in re.finditer(r"[Rr]eturn (?:up to \w+ )?target ([A-Z][a-z]+)(?: or ([A-Z][a-z]+))?(?: creature)? cards? from your graveyard", oracle):
        _rt += [g for g in _m.groups() if g]
    _rt = [x for x in dict.fromkeys(_rt) if x not in _nt]
    if _rt:
        g0 = next(iter(groups), "m1")
        groups[g0] = groups.get(g0, []) + ["restricted_to:" + x.lower() for x in _rt]
    out_groups = {}
    for gid, ts in groups.items():
        ts = [t for t in dict.fromkeys(ts) if not t.startswith("impulse_draw_part")]
        if ts: out_groups[gid] = ts
    links = list(links); x_links(out_groups, links)
    flat = list(dict.fromkeys(t for ts in out_groups.values() for t in ts))
    return flat, list(dict.fromkeys(links)), out_groups

#!/usr/bin/env python3
"""Master archetype list (Spellweave 45 as the base, our former 35 merged under it, 2026-10-26) and baseline roles (recursion, ramp, card draw).
Originally a synthesis of four public Commander strategy guides into data for the deck builder and balancer (2026-10-25).
Sources (facts only, no page prose is stored): sw = spellweave.app/guides/edh-archetypes, em = edhmatch.com/strategies/<slug>,
cf = commander-forge.com/archetypes, tz = turnzerohq.com/guides/archetypes.
Writes strategies.json (what build/balance code reads) and ../../agents/logs/strategy-sources.toon (per-source learning rows).
Usage: python3 build_strategies.py            # regenerate both files
Role signals are ftags prefixes (pool.pkl 'ftags'): "x" matches tag x and "x:*"; "x:y" matches exactly."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "../../agents/logs/strategy-sources.toon")
SRC = {"sw": "https://spellweave.app/guides/edh-archetypes", "em": "https://www.edhmatch.com/strategies",
       "cf": "https://commander-forge.com/archetypes", "tz": "https://turnzerohq.com/guides/archetypes", "edhrec": "https://edhrec.com/themes"}

def R(sig, cards=(), n=None): return {"sig": list(sig), "cards": list(cards), "n": n}

# id: plan, stages (play line), roles, wins, weak (text), weak_tags (opposing tags that hurt it), overlaps, subs, colors, bracket, src facts
A = {}
def add(id, plan, stages, roles, wins, weak, weak_tags, overlaps, colors, src, subs=(), bracket=None, notes=""):
    A[id] = dict(id=id, plan=plan, stages=stages, roles=roles, wins=wins, weak=weak, weak_tags=weak_tags,
                 overlaps=overlaps, subs=list(subs), colors=colors, bracket=bracket, notes=notes, src=src)

add("aristocrats", "cheap recursive bodies feed a free outlet while death triggers drain, draw and make Treasure",
    ["setup: cheap creatures and token makers", "engine: 1-3 mana free sacrifice outlets", "payoff: stack 2-3 death-trigger payoffs", "rebuild: recursion after sweepers", "win: chain sacrifices until drain finishes the table"],
    {"fodder": R(["token_make", "recursion", "reanimate"], ["Reassembling Skeleton", "Bloodghast", "Gravecrawler"], [10, 12]),
     "outlet": R(["sacrifice_outlet", "cost_sacrifice_target"], ["Viscera Seer", "Carrion Feeder", "Ashnod's Altar"], [5, 8]),
     "payoff": R(["trigger:dies", "life_loss", "drain"], ["Blood Artist", "Zulaport Cutthroat", "Bastion of Remembrance", "Grave Pact", "Dictate of Erebos", "Mayhem Devil", "Pitiless Plunderer"], [8, 10]),
     "card_adv": R(["draw", "cost_sacrifice_target"], ["Village Rites", "Deadly Dispute"], [8, 10]),
     "edict": R(["sacrifice", "effect:sacrifice"], [], [6, 8]),
     "recursion": R(["recursion", "reanimate"], ["Meren of Clan Nel Toth"], None)},
    ["drain by stacked death triggers on a mass sacrifice turn", "recurring sac loop for infinite triggers", "grind then drain"],
    "graveyard hate and exile stop recursion; Hushbringer-style trigger stops; activated-ability taxes slow outlets; slow versus fast combo",
    ["grave_hate", "restrict_kind:cant_activate"], ["tokens", "lifegain", "graveyard"],
    ["B", "WB", "BR", "BG", "WBR"], dict(sw="stack 2-3 drain triggers with a free outlet; bracket 2-4", em="payoffs 8-10, outlets 5-8, fodder 10-12, engine pieces cost 1-3; sacrifice page: outlets 3-5, sac-tied card advantage 8-10, edict interaction 6-8", cf="sub: aristocrats, blood artist, food chain, treasure sac; Sacrifice group of 17; need fodder+outlet+payoff, outlet redundancy", tz="usually also go-wide"),
    subs=["aristocrats", "blood_artist", "food_chain", "treasure_sac", "sacrifice"], bracket=[2, 4])

add("tokens", "go wide, double output, then one large alpha strike or a non-combat damage payoff",
    ["early: repeatable generators (prefer over one-shots)", "mid: doublers and anthems; keep one generator back vs sweepers", "finish: overrun, or damage per creature entering"],
    {"generator": R(["token_make"], ["Krenko, Mob Boss", "Adeline, Resplendent Cathar", "Rhys the Redeemed", "Trostani, Selesnya's Voice", "Tendershoot Dryad", "Secure the Wastes", "Avenger of Zendikar"], [10, 14]),
     "doubler": R(["token_count", "replace"], ["Doubling Season", "Anointed Procession", "Parallel Lives", "Mondrak, Glory Dominus"], [2, 4]),
     "anthem": R(["pump_team", "lord"], ["Cathars' Crusade", "Intangible Virtue", "Divine Visitation"], [4, 6]),
     "finisher": R(["pump_team", "grant_kw:trample"], ["Craterhoof Behemoth", "Overwhelming Stampede", "Triumph of the Hordes"], None),
     "drain": R(["damage", "trigger:etb"], ["Impact Tremors", "Purphoros, God of the Forge"], None),
     "draw": R(["draw"], ["Skullclamp"], [6, 8]),
     "protection": R(["protection_trick", "phase_out", "kw:indestructible"], ["Heroic Intervention", "Flawless Maneuver", "Selfless Spirit", "Boros Charm"], [3, 5]),
     "ramp": R(["mana_source"], [], [8, 10])},
    ["mass pump plus trample alpha", "Impact Tremors / Purphoros non-combat damage", "tokens upgraded by Divine Visitation"],
    "board wipes; Propaganda effects and big blockers; removal on doublers/anthems; overcommitting",
    ["removal", "restrict_kind:cant_attack", "attack_tax"], ["aristocrats", "counters", "stompy", "tribal", "blink"],
    ["GW", "WB", "RG", "UR", "RGW"], dict(sw="2-3 turns wide then mass pump or doubler; bracket n/a", em="generators 10-14, doublers 2-4, anthems 4-6, draw 6-8, ramp 8-10, wipe answers 3-5", cf="sub: go wide, anthems, populate, convoke", tz="Doubling Season + Parallel Lives quadruples; sample 36 lands 12 ramp 9 removal 32 creatures 7 draw 1 wipe; Jetmir escalates at 3/6/9 attackers"),
    subs=["go_wide", "anthems", "populate", "convoke"])

add("tribal", "density of one creature type; lords stack multiplicatively; payoffs reward casting or attacking with the type",
    ["early: type two-drops and cost reducers", "mid: lords and card-advantage payoffs", "finish: mass pump or type-specific payoff"],
    {"lord": R(["lord", "pump_team"], ["Goblin King", "Lord of Atlantis", "Elvish Archdruid", "Goblin Chieftain", "Merrow Reejerey"], None),
     "cost_reducer": R(["cost_reduce"], ["Urza's Incubator", "Herald's Horn"], None),
     "card_adv": R(["draw", "trigger:spell_cast"], ["Kindred Discovery", "Vanquisher's Banner"], None),
     "anthem": R(["pump_team"], ["Coat of Arms", "Shared Animosity"], None),
     "support_grant_type": R(["grant_type"], [], None),
     "protection": R(["cant_be_countered"], ["Cavern of Souls", "Path of Ancestry"], None),
     "recursion": R(["recursion", "reanimate"], ["Patriarch's Bidding"], None)},
    ["mass pump on a wide board", "Shared Animosity lethal", "type-specific payoffs (Gishath, Lathril, Kumena)"],
    "board wipes, Engineered Plague, Extinction; targeted removal on lords; filler creatures kept only for type",
    ["removal"], ["aristocrats", "tokens", "stompy"], ["any"],
    dict(sw="variants aggro, combo (Slivers, Wizards), value (Merfolk, Faeries)", em=None, cf="sub under Creatures: Tribal, Aggro, Extra Combat, Power Matters", tz="three lords outscale one; commit to a type, deploy lords and payoffs, attack as one"),
    notes="Concordia rule H74: tribe match counts only with tribal abilities. Tag niche:tribal marks cards that only pay off in a matching deck.")

add("voltron", "one protected threat (usually the commander) wins by 21 commander damage, often in two swings",
    ["pick the single threat", "attach equipment/auras: power, evasion, protection", "hold protection so removal or bounce does not reset", "rebuild by re-equipping or recasting", "remove players one at a time"],
    {"attach": R(["kw:equip", "kw:enchant", "kw:bestow"], ["Sword of the Animist", "Commander's Plate", "Sword of Feast and Famine", "All That Glitters", "Shielded by Faith", "Battle Mastery", "Ethereal Armor"], [12, 18]),
     "attach_helper": R(["cost_reduce", "put_onto_battlefield"], ["Sigarda's Aid", "Puresteel Paladin", "Hammer of Nazahn", "Colossus Hammer"], [4, 6]),
     "protection": R(["protection_trick", "kw:hexproof", "phase_out", "kw:indestructible"], ["Swiftfoot Boots", "Lightning Greaves", "Heroic Intervention", "Flawless Maneuver", "Teferi's Protection", "Snakeskin Veil"], [6, 8]),
     "evasion": R(["evasion", "cant_be_blocked", "kw:flying", "kw:trample"], ["Rogue's Passage"], None),
     "tutor": R(["tutor"], ["Steelshaper's Gift", "Open the Armory"], None),
     "ramp": R(["mana_source"], [], [8, 10]),
     "damage_multiplier": R(["kw:double_strike", "trigger:beginning_of_combat"], [], None)},
    ["21 commander damage on each opponent", "double strike / extra combats", "evasive or unblockable commander"],
    "edicts, exile, mass bounce bypass protection; Maze of Ith, fog, propaganda; commander tax; aura-heavy builds lose cards when the creature dies",
    ["sacrifice", "bounce", "fog", "attack_tax", "tap_down"], ["equipment", "counters", "enchantress", "infect"],
    ["RW", "WU", "GW", "UR"], dict(sw="two attacks of 10-11 for 21; bracket 2-3", em="equipment/auras 12-18, helpers 4-6, protection 6-8, ramp 8-10", cf="subs: equipment, aura, infect, double strike", tz="the opposite approach to go wide"),
    subs=["equipment_voltron", "aura_voltron", "infect_voltron", "double_strike"], bracket=[2, 3])

add("equipment", "weapons are the engine that makes ordinary creatures real attackers; gear spreads across a team",
    ["deploy carriers that survive removal", "tutor or draw the right equipment", "reduce equip costs or attach free", "move gear between carriers", "win via commander damage or a team sharing tools"],
    {"equipment": R(["kw:equip", "target_type:equipment"], ["Colossus Hammer", "Sword of Feast and Famine"], [10, 14]),
     "tutor": R(["tutor"], ["Stoneforge Mystic", "Steelshaper's Gift", "Open the Armory"], None),
     "cost_reducer": R(["cost_reduce"], ["Puresteel Paladin", "Sigarda's Aid", "Brass Squire"], None),
     "draw": R(["draw"], ["Sram, Senior Edificer"], None),
     "carrier": R(["evasion"], [], [12, 18]),
     "protection": R(["protection_trick"], [], [6, 10])},
    ["commander damage from a safe carrier", "spread weapons over tokens", "sword triggers plus extra combats"],
    "artifact removal and wipes; equip mana after carrier dies; gear with no creatures does nothing",
    ["removal_artifact"], ["voltron", "stompy", "artifacts"], ["W", "RW", "R"],
    dict(em="equipment 10-14, lands 34-36 plus rocks, creatures 12-18, protection 6-10; recovers from sweepers because gear stays", cf="sub of Artifact: Equipment; Sram, Wyleth, Akiri in sw"),
    subs=["equipment"])

add("reanimator", "stock the graveyard with a 7+ mana creature then reanimate it for 2-3 mana on turn 2-4",
    ["stock: discard, self-mill, Entomb-style tutors", "cast a cheap reanimation spell on the target", "use enter/attack triggers immediately", "hold backup recursion for graveyard hate", "close with repeated or mass return"],
    {"enabler": R(["discard", "self_mill", "tutor_dest:graveyard", "cost:discard"], ["Entomb", "Buried Alive", "Faithless Looting"], [6, 8]),
     "reanimation": R(["reanimate", "from_zone:graveyard"], ["Reanimate", "Animate Dead", "Necromancy", "Victimize", "Living Death"], [8, 12]),
     "target": R(["cmc_ge_7"], ["Atraxa, Grand Unifier", "Archon of Cruelty", "Ashen Rider", "Razaketh, the Foulblooded", "Sheoldred, Whispering One"], [6, 10]),
     "protection": R(["counterspell"], [], None)},
    ["early reanimated bomb", "Living Death mass return", "sac outlet + reanimation loop"],
    "graveyard hate at instant speed (Rest in Peace, Bojuka Bog, Leyline of the Void); exile removal; counterspells; no target in hand; predictable key turn",
    ["grave_hate", "counterspell"], ["graveyard", "aristocrats", "mill"], ["B", "UB", "WB", "BG"],
    dict(sw="fill graveyard turn 2-3 then reanimate for 2-3 mana", em="reanimation 8-12, setup 6-8, targets 6-10", cf="sub of Graveyard: Reanimator, Self-Mill, Dredge, Flashback"),
    subs=["reanimator"])

add("graveyard", "the graveyard is a second hand: fill it, then recur many small resources (creatures, lands, spells)",
    ["fill: self-mill, discard, sacrifice, dredge", "replay creatures, lands, spells so removal only delays", "convert recursion to card advantage/mana", "rebuild after sweepers", "close by grinding or a recursion-payoff loop"],
    {"filler": R(["self_mill", "discard", "mill", "kw:dredge"], ["Stitcher's Supplier", "Fauna Shaman"], [8, 10]),
     "recursion": R(["recursion", "reanimate", "from_zone:graveyard", "kw:flashback", "kw:escape"], ["Eternal Witness", "Life from the Loam", "Muldrotha, the Gravetide", "Genesis", "Meren of Clan Nel Toth"], [8, 12]),
     "payoff": R(["trigger:dies", "life_loss"], ["Syr Konrad, the Grim"], None),
     "backup_engine": R(["recursion"], [], [1, 2])},
    ["drain via recursion payoffs", "grind out answers then attack", "outlet plus recursion loop"],
    "graveyard hate; exile removal; slow setup; visible recursion lines",
    ["grave_hate"], ["aristocrats", "reanimator", "mill"], ["BG", "BGU", "UB", "WBG"],
    dict(sw="dredge, flashback, escape; overlaps reanimator and self-mill", edhrec="Reanimator, Graveyard, Self-Mill, Dredge, Birthing Pod, Flashback, Retrace pages; no recursion tag", em="fillers 8-10, recursion 8-12, 1-2 backup engines, favor ETB/death-trigger creatures", cf="same Graveyard group as reanimator"),
    subs=["dredge", "flashback", "escape", "retrace"])

add("mill", "empty libraries (three opponents: repeatable and doubled mill) or cash in stocked graveyards",
    ["choose opponent mill or self-mill", "deploy repeatable mill over several turns", "add doublers", "protect engines", "cash graveyards for recursion, theft or drain"],
    {"engine": R(["mill", "self_mill", "mill_count"], ["Mesmeric Orb", "Ruin Crab", "Sphinx's Tutelage", "Fleet Swallower"], [8, 12]),
     "doubler": R(["mill", "replace"], ["Bruvac the Grandiloquent", "Fraying Sanity"], [2, 3]),
     "payoff": R(["mill", "mill_count"], ["Consuming Aberration", "Bloodchief Ascension", "Maddening Cacophony"], None),
     "outlet": R(["sacrifice_outlet"], ["Altar of Dementia"], None),
     "interaction": R(["remove", "counterspell"], [], [8, 10]),
     "graveyard_exile": R(["exile_from", "grave_hate"], [], None)},
    ["empty libraries with doubled mill or Traumatize", "self-mill into Jace, Wielder of Mysteries / Laboratory Maniac", "mass reanimation or theft"],
    "three 99-card libraries are slow; shuffle-back effects; mill feeds reanimator opponents; graveyard hate",
    ["grave_hate"], ["reanimator", "graveyard", "self_mill", "control"], ["U", "UB", "BGU"],
    dict(sw="win by empty library", em="engines 8-12, multipliers 2-3, interaction 8-10", cf="subs: self-mill, opponent mill, mill combo, Bruvac"),
    subs=["opponent_mill", "mill_combo"])

add("spellslinger", "many cheap instants and sorceries each turn feed per-cast payoffs",
    ["fill the deck with cheap, flexible spells", "convert each cast to damage, tokens, cards or mana", "hold interaction that also advances the engine", "refill with cantrips, wheels, recursion", "close with triggers, a token force or a large spell"],
    {"payoff": R(["trigger:spell_cast", "kw:prowess"], ["Guttersnipe", "Talrand, Sky Summoner", "Archmage Emeritus", "Young Pyromancer", "Storm-Kiln Artist"], [6, 10]),
     "cantrip": R(["draw", "selection", "scry_count"], ["Opt", "Brainstorm", "Frantic Search"], [8, 12]),
     "cost_reducer": R(["cost_reduce", "mana_source"], ["Goblin Electromancer", "Baral, Chief of Compliance", "Birgi, God of Storytelling"], None),
     "copy": R(["clone", "token_type:copy"], ["Galvanic Iteration", "Twincast", "Fork"], None),
     "rebuy": R(["kw:flashback", "recursion"], ["Mystic Sanctuary"], None),
     "spells": R(["cardtype:instant", "cardtype:sorcery"], [], [25, 35])},
    ["burn payoffs over many casts", "spell-made tokens", "copied finisher or large X spell", "Aetherflux Reservoir"],
    "fragile payoff creatures; taxes (Eidolon of Rhetoric, Damping Sphere, Rule of Law); discard; slow board impact",
    ["restrict", "attack_tax", "counterspell"], ["storm", "combo", "control"], ["UR", "UBR", "URW"],
    dict(sw="explosive chain turns; weak to taxes", em="instants/sorceries 25-35, payoffs 6-10, cantrips 8-12, interaction 8-10, curve 1-3", cf="subs: cantrips, copy spells, big spells, magecraft; Demanding"),
    subs=["cantrips", "copy_spells", "big_spells", "magecraft"])

add("storm", "bank many cheap spells in one turn until the storm count is lethal",
    ["cantrip to sculpt; hold rituals", "count mana before committing", "cost reducers and rituals turn spells into mana and cards", "commit to a payoff only with count and protection ready"],
    {"cantrip": R(["draw", "selection"], ["Ponder", "Preordain", "Brainstorm"], None),
     "ritual": R(["mana", "mana_burst", "cardtype:instant"], ["Jeska's Will", "Pyretic Ritual", "Cabal Ritual", "Mana Geyser"], None),
     "cost_reducer": R(["cost_reduce"], ["Birgi, God of Storytelling", "Baral, Chief of Compliance"], None),
     "refuel": R(["discard", "draw"], ["Windfall", "Past in Flames"], None),
     "payoff": R(["kw:storm", "niche:storm"], ["Grapeshot", "Tendrils of Agony", "Aetherflux Reservoir", "Mind's Desire", "Brain Freeze"], [2, 3]),
     "spells": R(["cardtype:instant", "cardtype:sorcery"], [], [25, 35])},
    ["Grapeshot/Tendrils lethal count", "Aetherflux Reservoir shot", "Brain Freeze mill", "run 2-3 payoffs"],
    "one counterspell on the payoff; Rule of Law, Thalia taxes, graveyard hate; visible sculpting; long turns unwelcome in casual pods",
    ["counterspell", "attack_tax", "grave_hate", "restrict"], ["spellslinger", "combo", "big_mana"], ["UR", "UBR", "R"],
    dict(sw="storm copies equal prior spells; tax-weak", em="25-35 cheap spells (1-2 mana), a few tutors, 2-3 payoffs"),
    )

add("combo", "tutor, protect, win in one decisive moment; 2-3 compact combos with redundancy",
    ["early: ramp, draw and tutor toward pieces", "read the table before committing", "hold protection through disruption", "win in one moment, not through combat"],
    {"tutor": R(["tutor"], ["Demonic Tutor", "Mystical Tutor", "Enlightened Tutor"], [5, 10]),
     "draw_select": R(["draw", "selection"], [], [8, 12]),
     "enabler": R(["mana_source", "untap"], ["Isochron Scepter", "Dramatic Reversal"], None),
     "payoff_engine": R(["token_type:copy", "clone"], ["Kiki-Jiki, Mirror Breaker", "Zealous Conscripts", "Walking Ballista", "Heliod, Sun-Crowned", "Exquisite Blood", "Sanguine Bond", "Thassa's Oracle", "Demonic Consultation", "Tainted Pact", "Underworld Breach", "Brain Freeze"], [2, 3]),
     "protection": R(["counterspell", "protection_trick"], [], [6, 10]),
     "remove": R(["remove"], [], None),
     "support_alt_win": R(["lose_game"], [], None)},
    ["infinite mana into X spell", "Kiki-Jiki loops", "Thassa's Oracle package", "drain loop", "Scepter + Dramatic Reversal"],
    "single counterspell or removal; tutor punishers (Opposition Agent, Aven Mindcensor, Archivist of Oghma); hand attack; Null Rod, Collector Ouphe; stax strands tutors",
    ["counterspell", "restrict", "discard"], ["spellslinger", "storm", "control", "stax"], ["UB", "UR", "WB", "BG"],
    dict(sw="bracket 3-4", em="combos 2-3, tutors 5-10, draw 8-12, protection 6-10, redundancy", tz="often a backup plan in other archetypes"), bracket=[3, 4])

add("counters", "grow creatures with +1/+1 counters and multiply them until the weakest creature is huge",
    ["cast creatures that enter with counters", "multipliers so each trigger gives more", "spread counters across bodies", "convert big creatures to cards/mana/life/pressure", "protect the engine, attack with creatures that outgrow blocks"],
    {"multiplier": R(["counters_plus", "replace"], ["Hardened Scales", "Branching Evolution", "Conclave Mentor", "Doubling Season"], [3, 5]),
     "enabler": R(["counter:p1p1", "counters_plus"], ["Rishkar, Peema Renegade", "Mikaeus, the Lunarch"], [15, 20]),
     "proliferate": R(["proliferate"], ["Evolution Sage", "Inexorable Tide", "Karn's Bastion", "Flux Channeler", "Contagion Engine"], [4, 8]),
     "seed": R(["counter", "loyalty_change"], [], None),
     "draw_payoff": R(["draw", "counters_plus"], ["Fathom Mage", "Champion of Lambholt", "Inspiring Call", "Rishkar's Expertise"], [6, 8]),
     "protection": R(["protection_trick"], ["The Ozolith", "Nesting Grounds", "Heroic Intervention"], [3, 5]),
     "ramp": R(["mana_source"], [], [8, 10]),
     "spend": R(["counter_remove"], [], None)},
    ["tall trampling board", "Simic Ascendancy", "Overwhelming Stampede", "evasion/removal to pass blockers"],
    "board wipes (Farewell, Toxic Deluge); Solemnity; Vampire Hexmage; setup turns; removal on doublers",
    ["removal", "counter_prevent"], ["infect", "superfriends", "tokens", "voltron", "lifegain"], ["GW", "GU", "WBG"],
    dict(sw="doublers, distributors, payoffs, proliferate", em="multipliers 3-5, creatures 15-20, proliferate 4-6, draw 6-8, ramp 8-10, protection 3-5", cf="subs: +1/+1, proliferate, modular, hydras", tz="Atraxa archetype (proliferate)"),
    subs=["p1p1", "modular", "hydras", "proliferate"])

add("infect", "poison (infect/toxic) instead of life loss; 10 counters via a pumped evasive attacker plus proliferate",
    ["attack early with infect/toxic creatures", "pump an evasive attacker for 10 in one or two hits", "proliferate to finish", "protect the swing"],
    {"creature": R(["kw:infect", "kw:toxic"], ["Skithiryx, the Blight Dragon", "Blightsteel Colossus", "Inkmoth Nexus"], [15, 20]),
     "pump": R(["pump_single", "grant_kw:infect"], ["Groundswell", "Might of Old Krosa", "Berserk", "Triumph of the Hordes", "Grafted Exoskeleton"], [6, 10]),
     "proliferate": R(["proliferate"], ["Evolution Sage", "Contagion Engine", "Tezzeret's Gambit"], [5, 8]),
     "protection": R(["protection_trick"], [], [6, 8])},
    ["ten poison on each opponent", "proliferate after combat"],
    "table aggression; fog, deathtouch blockers, wipes; some pods ban poison; lifegain irrelevant to the clock",
    ["fog", "removal"], ["voltron", "counters", "stompy"], ["BG", "GU", "WBG"],
    dict(em="creatures 15-20, pump 6-10, proliferate 5-8, protection 6-8", cf="sub of Voltron: Infect"))

add("lifegain", "convert life gained into counters, cards, tokens, drain or a charged Aetherflux Reservoir",
    ["gain life in repeat small increments", "payoffs turn each trigger into value", "use the life buffer to play patiently", "close with drain loop, oversized board or Reservoir"],
    {"trigger": R(["lifegain", "kw:lifelink", "trigger:gain_life"], ["Soul Warden", "Essence Warden", "Suture Priest", "Authority of the Consuls"], [8, 12]),
     "payoff": R(["trigger:gain_life"], ["Ajani's Pridemate", "Heliod, Sun-Crowned", "Vito, Thorn of the Dusk Rose", "Archangel of Thune"], [6, 10]),
     "drain": R(["life_loss", "drain"], ["Sanguine Bond", "Exquisite Blood"], None),
     "conversion": R(["draw"], ["Aetherflux Reservoir", "Well of Lost Dreams"], None),
     "ramp": R(["mana_source"], [], [10, 12]),
     "interaction": R(["remove"], [], [6, 8])},
    ["Vito/Sanguine Bond drain loop", "oversized payoff creatures", "Aetherflux Reservoir"],
    "life does not stop commander damage, poison or combo; payoffs draw removal; Tainted Remedy, Rain of Gore, Roiling Vortex; slow start",
    ["life_loss", "restrict"], ["aristocrats", "counters", "group_hug", "enchantress"], ["W", "WB", "GW", "WBG"],
    dict(sw="bracket 1-3", em="sources 8-12, payoffs 6-10, ramp 10-12, removal 6-8; redundant Pridemate/Vito/Heliod effects first", cf="subs: soul sisters, payoffs, angel lifegain, drain; Beginner friendly"),
    subs=["soul_sisters", "payoffs", "angel_lifegain", "drain"], bracket=[1, 3])

add("blink", "flicker creatures to reuse enter-the-battlefield triggers; a blink on a draw creature is a repeating engine",
    ["cast ETB creatures that draw, remove, ramp, drain or make tokens", "reuse with flicker spells and repeatable engines", "hold instant-speed blink as protection", "grind card and board advantage", "finish with token engine or trigger loop"],
    {"flicker": R(["clone", "remove:exile", "return", "put_onto_battlefield"], ["Ephemerate", "Momentary Blink", "Ghostly Flicker", "Conjurer's Closet"], [8, 12]),
     "engine": R(["trigger:end_step", "put_onto_battlefield"], ["Thassa, Deep-Dwelling", "Soulherder", "Teleportation Circle", "Panharmonicon"], None),
     "etb_creature": R(["trigger:etb"], ["Mulldrifter", "Thragtusk", "Ravenous Chupacabra", "Reflector Mage", "Eternal Witness", "Sun Titan", "Knight of Autumn", "Agent of Treachery"], [20, 25]),
     "recursion": R(["recursion"], ["Archaeomancer", "Mnemonic Wall"], None),
     "finisher": R(["life_loss", "token_make"], ["Gray Merchant of Asphodel", "Deadeye Navigator", "Peregrine Drake", "Palinchron"], None)},
    ["out-card then outsize removal", "token-producer blink for width", "looped drain triggers", "extra turns (Time Stretch)"],
    "Torpor Orb and Hushbringer; exile or commander removal; slow clock",
    ["restrict"], ["control", "tokens"], ["WU", "GWU", "WUB"],
    dict(sw="engines, ETB targets, Panharmonicon, Deadeye Navigator loop", em="flicker 8-12, ETB creatures 20-25", cf="subs: ETB value, flicker combo, Panharmonicon, Soulherder"),
    subs=["etb_value", "flicker_combo", "panharmonicon", "soulherder"])

add("landfall", "every land drop is a trigger; extra drops plus recursion give 3+ triggers a turn",
    ["play land / fetch for extra triggers", "stack extra land drops", "recur lands from the graveyard", "convert triggers to tokens, counters, cards, damage, combats"],
    {"payoff": R(["condition:landfall", "niche:landfall"], ["Avenger of Zendikar", "Scute Swarm", "Omnath, Locus of Creation", "Omnath, Locus of Rage", "Valakut Exploration", "Felidar Retreat", "Tireless Tracker", "Tatyova, Benthic Druid"], [8, 10]),
     "extra_drop": R(["extra_land_drop"], ["Exploration", "Oracle of Mul Daya", "Azusa, Lost but Seeking", "Dryad of the Ilysian Grove", "Wayward Swordtooth"], [4, 6]),
     "recursion": R(["recursion", "from_zone:graveyard"], ["Crucible of Worlds", "Ramunap Excavator", "Life from the Loam"], [2, 3]),
     "fetch": R(["niche:lands", "land_tutor"], ["Evolving Wilds", "Cultivate", "Three Visits"], None),
     "ramp": R(["mana_source", "land_tutor"], ["Lotus Cobra"], None),
     "interaction": R(["remove"], [], [5, 7])},
    ["go wide with Scute Swarm/Avenger", "landfall damage", "extra combats (Moraug)"],
    "board wipes; missed land drops; early removal on Cobra/Azusa; Strip Mine, Wasteland, Blood Moon, Back to Basics",
    ["removal_land", "restrict"], ["lands_matter", "big_mana", "tokens"], ["G", "RG", "GU", "GW"],
    dict(sw="lands matter / landfall; extra drops plus recursion", em="payoffs 8-10, extra drops 4-6, recursion 2-3, interaction 5-7, 40+ lands", cf="Lands group: landfall, land destruction, land recursion, Maze's End", tz="lands matter is usually also ramp"),
    subs=["landfall", "land_recursion", "extra_drops"])

add("big_mana", "ramp past normal development and cast few huge spells that change the board at once",
    ["turns 1-3: ramp and doublers", "protect the mana engine", "cast a few haymakers", "after sweepers rebuild through land ramp"],
    {"ramp": R(["mana_source", "land_tutor"], [], [12, 15]),
     "multiplier": R(["mana_amount", "replace"], ["Nyxbloom Ancient", "Mana Reflection", "Zendikar Resurgent"], [2, 4]),
     "mana_land": R(["mana_source"], ["Nykthos, Shrine to Nyx", "Cabal Coffers"], None),
     "draw": R(["draw"], [], [8, 10]),
     "haymaker": R(["x_is:x_paid"], ["Torment of Hailfire", "Genesis Wave", "Expropriate", "Rishkar's Expertise"], [4, 6]),
     "interaction": R(["remove", "counterspell"], [], [5, 7])},
    ["X spells", "Torment of Hailfire", "Expropriate", "Genesis Wave"],
    "single counterspell wastes a turn; aggro and fast combo; visible mana invites pressure",
    ["counterspell"], ["storm", "landfall", "lands_matter"], ["G", "RG", "GUR", "B"],
    dict(em="ramp 12-15, multipliers 2-4, draw 8-10, haymakers 4-6, mana sources 38-40, interaction 5-7"))

add("stax", "they cannot, you can: lock costs and resources early, then win under the lock",
    ["deploy taxes and locks before key turns", "build parity breakers (rocks, tokens, untappers, commander)", "deny resources", "hold removal for leaks", "finish by attrition, combat or compact combo"],
    {"lock": R(["restrict", "restrict_kind:doesnt_untap", "attack_tax"], ["Winter Orb", "Static Orb", "Sphere of Resistance", "Smokestack", "Thalia, Guardian of Thraben", "Drannith Magistrate", "Collector Ouphe", "Archon of Emeria", "Rule of Law", "Stasis"], [8, 12]),
     "parity_breaker": R(["mana_source", "untap", "token_make"], ["Smothering Tithe", "Rhystic Study"], [4, 6]),
     "fodder": R(["token_type:treasure", "token_type:clue_draw"], [], None),
     "win": R([], [], [1, 2])},
    ["resilient commander attack under the lock", "Smokestack attrition", "two-card combo"],
    "opponents ramp before locks land; artifact/enchantment removal dismantles locks; own restrictions without parity breakers; politics",
    ["removal_artifact", "removal_enchantment"], ["control", "combo", "artifacts"], ["W", "WU", "WB"],
    dict(sw="bracket 3-4", em="locks 8-12, parity breakers 4-6, choose one clear win condition", cf="subs: tax, resource denial, hatebears, Winter Orb; Demanding"),
    subs=["tax", "resource_denial", "hatebears", "winter_orb"], bracket=[3, 4])

add("control", "decide which threats matter, answer them, win late with a protected finisher or engine",
    ["hold mana and answer what matters", "sweepers reset crowded boards then rebuild with draw", "trade one-for-one sparingly", "accumulate card advantage", "close with protected finisher or combo"],
    {"answer": R(["counterspell", "remove"], ["Swords to Plowshares", "Cyclonic Rift"], [8, 12]),
     "sweeper": R(["remove"], ["Supreme Verdict"], [6, 10]),
     "draw_engine": R(["draw"], ["Rhystic Study", "Mystic Remora"], None),
     "finisher": R(["cmc_ge_5"], ["Teferi, Hero of Dominaria"], [2, 3])},
    ["protected finisher", "planeswalker", "combo after interaction spent", "card advantage"],
    "one-for-one answers lose value to three opponents; slow clocks; fast rebuilders",
    ["cant_be_countered"], ["blink", "mill", "stax", "combo"], ["WU", "UB", "WUB", "UR"],
    dict(em="wipes 6-10, answers 8-12, finishers 2-3, lands 36-38", cf="subs: draw-go, tap-out control, pillowfort, mass removal"),
    subs=["draw_go", "tap_out", "pillowfort", "mass_removal"])

add("group_hug", "give the table cards, lands or mana and profit from how they use it",
    ["give lands or mana first", "steer attacks and removal toward others", "pay off every draw or land drop", "hold interaction for the best user of gifts", "win with a hidden spell or late payoff"],
    {"shared": R(["gift_all", "draw", "put_onto_battlefield"], ["Howling Mine", "Temple Bell", "Rites of Flourishing", "Kynaios and Tiro of Meletis", "Phelddagrif"], [8, 12]),
     "breaker": R(["draw", "mana_source"], ["Smothering Tithe", "Consecrated Sphinx", "Zedruu the Greathearted"], [4, 6]),
     "pillowfort": R(["attack_tax", "restrict"], ["Propaganda", "Ghostly Prison"], None),
     "win": R([], ["Approach of the Second Sun"], None)},
    ["Approach of the Second Sun", "alternate win with large hand", "politics"],
    "accelerates opponents; little pressure; hidden win conditions draw interaction",
    ["removal"], ["lifegain"], ["U", "GU", "WUR"],
    dict(em="shared effects 8-12, breakers 4-6, lands 36-38", sw="Kynaios and Tiro, Phelddagrif, Kenrith"))

add("enchantress", "cheap enchantments replace themselves through draw triggers; constellation or aura payoff converts them to a win",
    ["cast cheap enchantments", "enchantress triggers replace them", "stack 2+ draw engines", "protect the engine", "finish with constellation, tokens or aura Voltron"],
    {"draw": R(["draw", "trigger:spell_cast"], ["Argothian Enchantress", "Enchantress's Presence", "Setessan Champion", "Mesa Enchantress", "Sythis, Harvest's Hand", "Tuvasa the Sunlit"], [6, 10]),
     "cheap_ench": R(["cardtype:enchantment", "kw:enchant"], ["Wild Growth", "Utopia Sprawl", "Sanctum Weaver", "Fertile Ground"], None),
     "protection": R(["protection_trick"], ["Sterling Grove", "Greater Auramancy", "Heroic Intervention"], None),
     "payoff": R(["ench_payoff", "token_make"], ["Sigil of the Empty Throne", "Ajani's Chosen"], None),
     "recursion": R(["recursion"], ["Hall of Heliod's Generosity"], None)},
    ["constellation triggers", "enchantment-cast tokens", "aura Voltron", "card lead"],
    "enchantment removal and wipes (Farewell, Bane of Progress, Back to Nature); losing enchantresses; payoff-heavy hands",
    ["removal_enchantment", "removal"], ["voltron", "lifegain"], ["GW", "GWU", "WB"],
    dict(sw="Sythis, Tuvasa", em="enchantress effects 6-10, low curve, 34-36 lands", cf="subs: aura, enchantment tokens, constellation, pillowfort"),
    subs=["aura", "enchantment_tokens", "constellation", "pillowfort"])

add("artifacts", "connect cheap artifacts, rocks and utility pieces into one engine",
    ["deploy cheap artifacts and rocks to critical mass", "cost reducers/affinity/Treasure cast several per turn", "untap, sacrifice, recur artifacts", "rebuild from graveyard", "win with constructs, loops, drain or one big artifact"],
    {"artifact": R(["cardtype:artifact"], [], [25, 35]),
     "cost_reducer": R(["cost_reduce", "kw:affinity"], ["Etherium Sculptor", "Foundry Inspector", "Cloud Key"], [3, 5]),
     "treasure": R(["token_type:treasure", "artifact_token"], ["Academy Manufactor"], None),
     "untapper": R(["untap"], ["Clock of Omens", "Unwinding Clock"], None),
     "recursion": R(["recursion"], ["Emry, Lurker of the Loch", "Teshar, Ancestor's Apostle"], None),
     "draw": R(["draw"], ["Mystic Forge", "Reckoner's Bargain"], None),
     "protection": R(["protection_trick"], ["Welding Jar", "Darksteel Forge"], None),
     "win": R(["x_is:count_artifact_you_control"], ["Urza, Lord High Artificer", "Cyberdrive Awakener", "Marionette Master", "Aetherflux Reservoir"], None)},
    ["construct armies", "mana loops", "Marionette Master / Reservoir drain"],
    "mass artifact removal (Vandalblast, Farewell, Bane of Progress); Collector Ouphe, Stony Silence; slow start",
    ["removal_artifact", "restrict"], ["equipment", "stax", "treasure"], ["U", "UR", "WU", "WUB"],
    dict(em="artifacts 25-35, cost reducers 3-5", cf="subs: artifact tokens, affinity, equipment, artifact combo", sw="Urza, Breya, Jhoira"),
    subs=["artifact_tokens", "affinity", "equipment", "artifact_combo"])

add("superfriends", "planeswalker density protected by blockers; loyalty doubling and extra activations",
    ["land a walker", "protect it", "activate again; surviving walkers are a resource", "multiple ultimates in one turn via doubling"],
    {"walker": R(["loyalty_change", "loyalty", "cardtype:planeswalker"], ["Saheeli, Filigree Master"], None),
     "doubler": R(["counters_plus", "replace"], ["Doubling Season", "Deepglow Skate", "Vorinclex, Monstrous Raider"], None),
     "extra_activation": R(["loyalty_change"], ["The Chain Veil", "Oath of Teferi"], None),
     "defense": R(["token_make", "remove"], ["Elspeth, Sun's Champion", "Ugin, the Spirit Dragon"], None),
     "mana": R(["mana_source"], ["Nissa, Who Shakes the World", "Interplanar Beacon"], None),
     "remove": R(["remove"], ["Karn Liberated"], None)},
    ["multiple ultimates one turn", "accumulated walker value"],
    "walkers without defense are free attack targets; slow and mana-hungry; archenemy after two ultimates",
    ["removal_planeswalker"], ["counters", "control"], ["WUB", "G", "WUBG"],
    dict(tz="Atraxa, Carth the Lion, Sisay, Commodore Guff, Freyalise, Dihada, Nahiri, Jared Carthalion, Ramos, Saheeli commanders"))

add("burn", "direct damage to faces scaled to 120 life across three opponents: each-opponent effects and multipliers",
    ["prioritise each-opponent damage and doublers", "repeatable pingers", "earthquake effects"],
    {"damage": R(["burn", "damage", "damage_amount"], ["Torbran, Thane of Red Fell", "Purphoros, God of the Forge", "Kaervek the Merciless"], None),
     "multiplier": R(["replace"], ["Torbran, Thane of Red Fell"], None),
     "pinger": R(["damage", "cost:tap"], [], None)},
    ["face damage with multipliers", "Earthquake", "group slug"],
    "single-target burn is inefficient in multiplayer; lifegain",
    ["lifegain"], ["stompy", "spellslinger", "group_slug"], ["R", "BR", "UR"],
    dict(sw="burn must scale to 120 life", cf="subs: direct damage, ping, group slug, earthquake"), subs=["direct_damage", "ping", "group_slug", "earthquake"])

# ---- master-list additions (user 2026-10-26: Spellweave 45 is the base; ours merged under it) ----
add("stompy", "cheap-to-mid big creatures outsize the table; haste, trample and pump close fast (our former aggro folded in)",
    ["turn 1-3: mana creatures and efficient bodies", "turn 3-5: oversized threats that outclass blockers", "anthems, haste and attack triggers scale the bodies", "extra combats and combat draw refuel", "close with trample or mass pump"],
    {"creature": R(["cardtype:creature"], [], [25, 35]),
     "big_body": R(["condition:creature_you_control_power_ge_4", "scales:creature_power_ge_4", "kw:trample"], ["Ghalta, Primal Hunger", "Rampaging Baloths", "Overwhelming Stampede"], [8, 12]),
     "anthem": R(["pump_team", "lord"], ["Shared Animosity", "Cathars' Crusade"], [2, 4]),
     "haste": R(["haste_grant", "kw:haste"], ["Fervor", "Rising of the Day"], None),
     "extra_combat": R(["trigger:beginning_of_combat"], ["Aggravated Assault", "Moraug, Fury of Akoum"], [2, 3]),
     "refuel": R(["draw", "trigger:combat_damage"], ["Reconnaissance Mission", "Toski, Bearer of Secrets"], None),
     "finisher": R(["damage", "grant_kw:trample"], ["Impact Tremors", "Craterhoof Behemoth", "Isshin, Two Heavens as One"], None),
     "remove": R(["remove"], [], None)},
    ["wide or tall anthem attacks over consecutive turns", "extra combats for 40+ in a turn", "trample pump alpha"],
    "board wipes; running out of gas; pillowfort and lifegain; fog; late topdecks",
    ["removal", "attack_tax", "fog"], ["tokens", "equipment", "infect", "tribal", "extra_combats"], ["G", "RG", "RW", "R"],
    dict(sw="Stompy (niche list); big efficient creatures", em="creatures 25-35, anthems 2-4, extra combats 2-3, lands 33-35 (aggro page)", cf="Creatures group: aggro; Beginner friendly"),
    subs=["aggro", "extra_combat", "power_matters"])

add("lands_matter", "lands are the resource: extra drops, land recursion and land payoffs; land destruction and Maze's End are variants",
    ["turn 1-3: land ramp and extra land drops", "mid: land-count payoffs and recursion from the graveyard", "deny opposing lands in the land-destruction variant", "close with a land-count X spell, creature lands or Maze's End"],
    {"ramp_land": R(["land_tutor", "extra_land_drop"], ["Cultivate", "Exploration", "Oracle of Mul Daya", "Azusa, Lost but Seeking"], [8, 12]),
     "payoff": R(["x_is:count_land_you_control", "niche:lands", "niche:land"], ["Field of the Dead", "Crucible of Worlds", "Titania, Protector of Argoth"], [6, 10]),
     "recursion": R(["recursion", "from_zone:graveyard"], ["Life from the Loam", "Ramunap Excavator"], [2, 3]),
     "denial": R([], ["Armageddon", "Wasteland", "Strip Mine"], None),
     "interaction": R(["remove"], [], [5, 7])},
    ["land-count X spell", "Field of the Dead / creature lands", "Maze's End", "land destruction lock"],
    "Strip Mine, Wasteland, Blood Moon, Back to Basics; wipes; slow start without ramp",
    ["removal_land", "restrict"], ["landfall", "big_mana", "stax"], ["G", "RG", "GU", "GW"],
    dict(sw="Lands Matter (featured); separate from Landfall", em="lands 40+ (landfall page)", cf="Lands group: landfall, land destruction, land recursion, Maze's End", tz="lands matter is usually also ramp"),
    subs=["land_destruction", "mazes_end", "land_recursion"])

add("outlaws", "typal ninja-pirate-rogue-assassin-mercenary-warlock deck that triggers on committing crimes (targeting opponents)",
    ["early: cheap outlaw bodies", "mid: crime triggers (target an opponent, their spell or permanent) pay off", "lords and tutors for the outlaw types", "close with evasive outlaw swarm or a crime payoff"],
    {"outlaw": R(["type:assassin", "type:pirate", "type:rogue", "type:mercenary", "type:warlock"], ["Slickshot Show-Off", "Magda, Brazen Outlaw"], [18, 28]),
     "lord": R(["lord:assassin", "lord:pirate", "lord:rogue", "scales:outlaw"], [], [3, 6]),
     "crime_trigger": R(["trigger_filter:pirate", "trigger_filter:rogue", "trigger_filter:assassin"], [], None),
     "cost_reducer": R(["cost_reduce_for:rogue"], [], None),
     "tutor": R(["tutor_target:permanent_mercenary"], ["Mercenary Informer"], None)},
    ["evasive outlaw alpha", "crime payoff value", "treasure engine"],
    "wipes; few payoffs outside outlaw types; targeted removal on lords; tribal filler dilutes the deck",
    ["removal"], ["tribal", "treasure", "stompy"], ["B", "BR", "UB", "R"],
    dict(sw="Outlaws (niche list)"), notes="Outlaws is a mechanic family (Thunder Junction), not a creature type; tag coverage is partial (types plus lords)")

add("clones", "copy the best permanent on the table, yours or theirs, and recur copy effects",
    ["play a flexible clone on turn 3-5", "copy the strongest creature or ETB value piece", "add copy triggers (Sakashima, Helm of the Host)", "close with copied bombs"],
    {"clone": R(["clone", "token_type:copy"], ["Clone", "Phyrexian Metamorph", "Sakashima of a Thousand Faces", "Vesuvan Shapeshifter"], [10, 16]),
     "etb_target": R(["trigger:etb"], ["Mulldrifter", "Thragtusk"], [10, 14]),
     "recursion": R(["recursion"], [], None),
     "remove": R(["remove"], [], [6, 8])},
    ["copy the biggest threat", "legend-rule tricks with Sakashima", "ETB copies"],
    "no good targets on an empty board; wipes; counterspells on key clones",
    ["removal"], ["blink", "combo"], ["U", "UR", "UG"],
    dict(sw="Clones (niche list)"))

add("extra_combats", "extra combat steps multiply attack triggers and damage per turn",
    ["deploy attack-trigger creatures", "extra combat enablers", "untap and pump per combat", "close with a multi-combat alpha"],
    {"extra_combat": R(["trigger:beginning_of_combat"], ["Aggravated Assault", "Relentless Assault", "Combat Celebrant", "Moraug, Fury of Akoum", "Najeela, the Blade-Blossom"], [6, 10]),
     "attack_trigger": R(["trigger:combat_damage", "kw:melee", "kw:myriad"], ["Hellkite Charger"], [8, 12]),
     "haste": R(["haste_grant", "kw:haste"], ["Fervor"], None),
     "pump": R(["pump_team", "grant_kw:trample"], ["Overwhelming Stampede"], [2, 4])},
    ["multiple combats with attack triggers", "pumped trample alpha"],
    "fog; blockers; wipes; one creature carries the combat",
    ["removal", "fog"], ["stompy", "voltron"], ["R", "RW", "RG"],
    dict(sw="Extra Combats (niche list)", cf="Creatures sub: Extra Combat"), notes="no ftag marks extra-combat effects; trigger:beginning_of_combat is coarse (see note)")

add("mutate", "stack mutate creatures onto the best body so every mutate trigger and attack trigger repeats",
    ["early: cheap non-Human bodies as targets", "mutate for value on attack", "protect the stack", "recover with recursion"],
    {"mutate": R(["kw:mutate", "x_is:timesmutated"], ["Gemrazer", "Brokkos, Apex of Forever", "Illuna, Apex of Wishes"], [12, 20]),
     "target": R(["cardtype:creature"], [], [12, 18]),
     "protection": R(["protection_trick", "kw:hexproof"], [], [4, 6]),
     "recursion": R(["recursion"], [], None)},
    ["mutated attacker with stacked triggers"],
    "removal on a mutate stack loses cards; Human targets are illegal; wipes",
    ["removal"], ["voltron", "counters"], ["G", "GU", "GRU"],
    dict(sw="Mutate (niche list)"), notes="only 34 mutate cards in the pool")

add("polymorph", "sacrifice a cheap creature to put a bigger one onto the battlefield from the library",
    ["play cheap creatures", "Polymorph effects find the bomb", "bomb has ETB or an immediate win", "protect the sacrificed fodder line"],
    {"polymorph": R(["put_onto_battlefield", "effect:sacrifice"], ["Transmogrify", "Artificial Evolution"], [6, 10]),
     "fodder": R(["token_make"], [], [8, 12]),
     "bomb": R(["cmc_ge_7"], [], [6, 10]),
     "protection": R(["counterspell", "protection_trick"], [], [4, 6])},
    ["polymorph into a game-winning creature"],
    "counterspells on the spell; no bomb in the library; edict removal",
    ["counterspell"], ["reanimator", "combo"], ["U", "UG", "UR"],
    dict(sw="Polymorph (niche list)"), notes="no polymorph ftag; signals are coarse")

add("self_mill", "put cards from your own library into the graveyard, then use them with recursion and graveyard payoffs",
    ["fill the graveyard", "play mill-synergy creatures and dredge", "cash the graveyard in recursion", "close with a graveyard-size payoff"],
    {"filler": R(["self_mill", "mill_count", "kw:dredge", "tutor_dest:graveyard"], ["Stitcher's Supplier", "Hermit Druid", "Fauna Shaman"], [8, 12]),
     "recursion": R(["recursion", "from_zone:graveyard", "kw:escape", "kw:flashback"], ["Muldrotha, the Gravetide", "Eternal Witness"], [8, 12]),
     "payoff": R(["scales:graveyard", "scales:card_you_own_in_graveyard", "scales:creature_you_own_in_graveyard"], [], [3, 5]),
     "draw": R(["draw"], [], [6, 8])},
    ["graveyard-size payoff", "recursion value", "reanimated bomb"],
    "graveyard hate; exile removal; self-mill risk in a tight library",
    ["grave_hate"], ["graveyard", "reanimator", "mill"], ["BG", "UB", "BGU", "G"],
    dict(sw="Self-Mill (niche list)", edhrec="Self-Mill, Dredge pages"))

add("energy", "generate energy counters and spend them on repeatable effects",
    ["early: energy producers", "mid: spend energy on engines and attacks", "keep a producer surplus", "close with energy-pumped attackers"],
    {"producer": R(["counter:energy"], ["Aetherworks Marvel", "Guide of Souls", "Longtusk Cub"], [12, 18]),
     "payoff": R(["counter:energy", "cost_energy"], ["Aether Hub"], [6, 10]),
     "multiplier": R(["counters_plus", "replace"], ["Ammit Eternal"], None),
     "draw": R(["draw"], [], [6, 8])},
    ["energy-pumped attackers", "Aetherworks Marvel loops"],
    "wipes; the colours with energy cards are few; energy is not a payoff on its own",
    ["removal"], ["artifacts", "counters"], ["RU", "G", "UG", "UR"],
    dict(sw="Energy (niche list)"), notes="counter:energy matches 131 cards; producer and payoff share the tag (no split in the pool)")

add("vehicles", "vehicles are the threats; crew creatures supply the pilot; vehicle payoffs reward the count",
    ["early: cheap crew creatures", "deploy vehicles that outclass the crew cost", "protect the crew line", "close with a big vehicle or crewed alpha"],
    {"vehicle": R(["type:vehicle", "niche:vehicle"], ["Smuggler's Copter", "Skysovereign, Consul Flagship", "Heart of Kiran"], [8, 12]),
     "crew": R(["kw:crew", "grant_kw:crew", "token_type:pilot_crewbuff", "token_type:pilot_crewsaddlebuff"], [], [12, 18]),
     "payoff": R(["scales:vehicle", "trigger_filter:vehicle", "affected_type:vehicle", "x_is:count_vehicle_you_control_times_2"], [], [3, 6]),
     "remove": R(["remove"], [], [5, 7])},
    ["crewed vehicle alpha", "vehicle count payoff"],
    "artifact removal; wipes leave vehicles but kill the crew; Torpor Orb",
    ["removal_artifact"], ["artifacts", "stompy"], ["R", "RW", "WU", "U"],
    dict(sw="Vehicles (niche list)"), notes="niche:vehicle only 13 cards; kw:crew is on the vehicles themselves (174 cards)")

add("sagas", "sagas deliver chapter value over turns; recursion, proliferation and lore-counter tricks reuse them",
    ["play sagas early", "reuse chapters with lore-counter effects and blink", "recur sagas with sacrifice or flicker", "close with the last chapter payoffs"],
    {"saga": R(["kw:chapter", "saga_chapter"], ["Urza's Saga", "The Eldest Reborn", "Ashiok's Reaper"], [12, 20]),
     "reuse": R(["niche:saga", "affected_type:saga", "proliferate", "recursion"], ["Narset, Enlightened Exile", "Doubling Season"], [4, 8]),
     "enabler": R(["mana_source", "draw"], [], [8, 10])},
    ["chapter-chain value", "reused finishing chapter"],
    "enchantment removal; sagas are slow; low stand-alone power",
    ["removal_enchantment"], ["enchantress", "blink", "counters"], ["WB", "GW", "BG", "WU"],
    dict(sw="Sagas (niche list)"), notes="saga_chapter and kw:chapter mark 209 cards")

add("discard", "make opponents discard, then punish an empty hand or a cluttered graveyard",
    ["early: cheap discard to strip hands", "keep opponents hellbent", "punisher payoffs", "close with a drain payoff or a locked table"],
    {"discard": R(["discard"], ["Hymn to Tourach", "Mind Twist", "Duress", "Thoughtseize"], [8, 12]),
     "punisher": R(["trigger:discard", "condition:hellbent"], ["Waste Not", "Megrim", "Liliana of the Veil"], [3, 6]),
     "symmetrical": R(["kw:madness", "cost:discard"], [], None),
     "remove": R(["remove"], [], [6, 8]),
     "draw": R(["draw"], [], [6, 8])},
    ["opponent discard lock with punishers", "empty hands then drain"],
    "three opponents refill; discard is weak against topdecks; speed",
    ["restrict"], ["wheels", "control", "stax"], ["B", "UB", "BR", "BG"],
    dict(sw="Discard (niche list)"))

add("group_slug", "symmetrical or each-player damage and life loss that favour a deck prepared for it",
    ["early: cheap blockers and lifegain", "deploy damage engines", "protect your own life total", "close with the last life total"],
    {"slug": R(["damage", "life_loss", "burn"], ["Sulfuric Vortex", "Zo-Zu the Punisher", "Manabarbs", "Pestilence"], [8, 12]),
     "lifegain": R(["lifegain", "kw:lifelink"], [], [4, 6]),
     "blocker": R(["cardtype:creature"], [], [10, 14]),
     "remove": R(["remove"], [], [5, 7])},
    ["drain the table slowly", "Pestilence / Sulfuric Vortex"],
    "lifegain; fog; faster decks; politics (you are the obvious threat)",
    ["lifegain"], ["burn", "stax", "pillow_fort"], ["R", "BR", "B"],
    dict(sw="Group Slug (niche list)", cf="Burn sub: group slug"))

add("forced_combat", "force opposing creatures to attack each other or you, and win by choosing the fights",
    ["early: blockers", "goad/must-attack effects aim the table at each other", "manage your own defenses", "close when others are depleted"],
    {"force": R(["goad", "must_attack"], ["Disrupt Decorum", "Agitator Ant", "Kardur, Doomscourge"], [6, 10]),
     "protection": R(["attack_tax", "restrict_kind:cant_attack"], ["Propaganda"], [4, 6]),
     "blocker": R(["cardtype:creature"], [], [10, 14]),
     "remove": R(["remove"], [], [5, 7])},
    ["opponents fight each other, you finish"],
    "fog; opponents with no creatures; aggro decks you cannot block",
    ["fog"], ["pillow_fort", "group_hug", "stompy"], ["R", "RB", "RW"],
    dict(sw="Forced Combat (niche list)"), notes="goad is an oracle-text tag (deckgen/text_tags.py, 81 cards); must_attack covers 88 cards")

add("pillow_fort", "attack taxes and deterrents keep attackers away while a late engine wins",
    ["early: tax effects and deterrents", "mid: card advantage and a defended engine", "late: finisher behind the wall"],
    {"fort": R(["attack_tax", "restrict_kind:cant_attack", "restrict_kind:cant_attack_unless_cost"], ["Propaganda", "Ghostly Prison", "Sphere of Safety", "Norn's Annex", "Crawlspace"], [8, 12]),
     "draw": R(["draw"], ["Mystic Remora", "Phyrexian Arena"], [6, 8]),
     "protection": R(["protection_trick", "kw:hexproof"], [], [3, 5]),
     "finisher": R(["cmc_ge_5"], [], [2, 4])},
    ["win from behind the wall"],
    "commander damage from decks that ignore the tax; enchantment removal; no pressure on others",
    ["removal_enchantment"], ["stax", "control", "group_hug"], ["W", "WU", "WB"],
    dict(sw="Pillow Fort (niche list)", cf="Control sub: pillowfort", em="pillowfort: tax effects first"))

add("upkeep_triggers", "turn-start payoffs: upkeep triggers that grow or cost, doubled by trigger copiers",
    ["early: upkeep engines", "stack triggers", "trigger doublers", "close with a growing payoff"],
    {"engine": R(["trigger:upkeep", "kw:cumulative_upkeep"], ["Phyrexian Arena", "Mystic Remora", "Paradox Haze", "Eldrazi Monument"], [10, 16]),
     "doubler": R(["replace", "trigger:upkeep"], ["Paradox Haze"], [2, 4]),
     "draw": R(["draw"], [], [6, 8]),
     "protection": R(["protection_trick"], [], [3, 5])},
    ["engine pile that outgrows the table"],
    "enchantment/artifact removal; slow; upkeep triggers also appear on cards unrelated to the plan",
    ["removal_enchantment", "removal_artifact"], ["enchantress", "control"], ["U", "UB", "B", "W"],
    dict(sw="Upkeep Triggers (niche list)"), notes="trigger:upkeep matches 711 cards; filter in the builder needs the commander")

# Baseline roles every deck carries, outside the archetype picker (user 2026-10-26: ramp, card draw and recursion are roles, not archetypes).
# Counts: recursion 2-5 = Spellweave EDH Deck Roles (no colour split); ramp 10-12 = EDHMatch ramp page, Draftsim ~10; draw ~10 = Draftsim/Tapped Out template, EDHMatch engines 10-15.
BASELINE = {
    "recursion": dict(sig=["recursion", "reanimate", "from_zone:graveyard"], cards=["Eternal Witness", "Regrowth", "Sun Titan", "Mnemonic Wall"], n=[2, 5], src="sw",
                      note="baseline for every deck, no per-colour split; black decks and the graveyard archetypes run more (see recursion_by_archetype)"),
    "ramp": dict(sig=["mana_source", "land_tutor"], cards=["Sol Ring", "Arcane Signet", "Cultivate", "Rampant Growth"], n=[10, 12], src="em, draftsim",
                 note="sources at 2 mana or less first; big_mana and lands_matter archetypes go higher"),
    "card_draw": dict(sig=["draw", "draw_count"], cards=["Rhystic Study", "Mystic Remora", "Phyrexian Arena"], n=[8, 12], src="draftsim, tappedout",
                      note="counted with selection; control and draw-heavy archetypes go higher")}
BASELINE["protection"] = dict(sig=["protection_trick", "regenerate", "protection_from", "grant_kw:protection", "phase_out", "kw:hexproof", "kw:indestructible", "kw:protection"],
                              cards=[], n=[3, 6], src="doc thread 2026-10-27", note="protect the commander and the engine; voltron, equipment, tokens, counters, combo, infect run more (see protection_by_archetype)")
BASELINE["ramp"]["sig"] = BASELINE["ramp"]["sig"] + ["fixing"]
PROTECTION_BY_ARCHETYPE = {a: [6, 10] for a in ("voltron", "equipment", "tokens", "counters", "combo", "infect")}
RECURSION_BY_ARCHETYPE = {"graveyard": [8, 12], "reanimator": [8, 12], "self_mill": [8, 12], "aristocrats": [4, 8], "blink": [3, 6], "landfall": [2, 3], "lands_matter": [2, 3], "mill": [4, 8]}
ALIASES = {"sacrifice": "aristocrats", "proliferate": "counters", "aggro": "stompy", "counters_plus": "counters", "chaos": None, "colorless": None, "ramp": None, "card_draw": None}

STUB_SIG = {"treasure": ["token_type:treasure", "cost_sacrifice_target:treasure"], "wheels": ["wheels"], "impulse_draw": ["impulse_draw"], "legends_matter": ["legend_payoff"]}
# archetypes seen only as one-liners on Spellweave (no detail on the page)
for i, (plan, ex) in {"treasure": ("make Treasure and convert it to mana, drain or sacrifice value", ["Prosper, Tome-Bound", "Korvold, Fae-Cursed King", "Magda, Brazen Outlaw"]),
                      "wheels": ("symmetrical discard-and-draw with punishers", ["Nekusar, the Mindrazer", "Xyris, the Writhing Storm", "The Locust God"]),
                      "impulse_draw": ("exile-and-play cards for card advantage", ["Prosper, Tome-Bound", "Birgi, God of Storytelling", "Etali, Primal Conqueror", "Narset, Enlightened Exile", "Notion Thief"]),
                      "legends_matter": ("legendary-density payoffs", ["Sisay, Weatherlight Captain", "Jodah, Archmage Eternal", "Kethis, the Hidden Hand", "Dihada, Binder of Wills"])}.items():
    add(i, plan, [], {"core": R(STUB_SIG[i], ex, None)}, [], "", [], [], [], dict(sw="one-line entry, no engine/weakness detail"))

add("theft", "take opponents' permanents or cast their cards, then profit from the borrowed pieces",
    ["control early threats", "steal the best permanent or spell", "sacrifice or flicker stolen permanents for value", "win with the table's own cards"],
    {"steal": R(["steal", "steal_temp"], [], [8, 12]), "remove": R(["remove"], [], [5, 7])},
    ["borrowed bombs"], "removal on the stolen card; slow without a steal target", [], ["control", "outlaws"], ["U", "R", "UR"], dict(sw="added from the doc thread; no source page"))

# oracle/ftag signatures for the one-line stubs (2026-10-27)
HOMES = {"bounce": ["control", "blink"], "tap_down": ["control", "stax"], "fog": ["pillow_fort"], "look_top": ["impulse_draw", "spellslinger"], "surveil": ["self_mill", "spellslinger"],
         "mech:graveyard_cast": ["graveyard", "self_mill"], "cast_free": ["polymorph", "storm", "combo"], "investigate": ["artifacts", "treasure"], "fight": ["stompy"],
         "monarch": ["group_hug", "pillow_fort"], "evasion_grant": ["voltron", "extra_combats"], "extra_turn": ["combo"]}
for _t, _ids in HOMES.items():
    for _i in _ids:
        if _i in A: A[_i]["roles"].setdefault("support_" + _t.replace(":", "_"), R([_t], [], None))


# TurnZero per-archetype pages (raw/tz, from fetch_sources.py): top-10 defining cards and commanders with their stated effect
TZ = {"aggro": "stompy", "aristocrats": "aristocrats", "artifacts": "artifacts", "blink": "blink", "combo": "combo", "control": "control",
      "counters": "counters", "enchantress": "enchantress", "go-wide": "tokens", "graveyard-recursion": "graveyard", "group-hug": "group_hug",
      "lands-matter": "lands_matter", "lifegain": "lifegain", "mill": "mill", "spellslinger": "spellslinger", "stax": "stax",
      "superfriends": "superfriends", "tribal": "tribal", "voltron": "voltron"}
def tz_lists(slug):
    import re
    p = os.path.join(HERE, "raw", "tz", slug + ".txt")
    if not os.path.exists(p): return {}
    L = open(p, encoding="utf8").read().splitlines(); out = {}
    for key, pat in (("key_cards", r"^Top 10 .* Cards$"), ("key_commanders", r"^Top 10 .* Commanders$")):
        i = next((n for n, l in enumerate(L) if re.match(pat, l)), None)
        if i is None: continue
        items = []; j = i + 1
        while j < len(L) and not L[j].startswith(("Top 10", "Deck Lab", "What to Watch", "See which")):
            if L[j].endswith(" ↗") and j + 1 < len(L): items.append({"name": L[j][:-2], "why": L[j + 1]}); j += 2
            else: j += 1
        out[key] = items
    w = next((n for n, l in enumerate(L) if l == "What to Watch Out For"), None)
    if w is not None: out["watch_out"] = L[w + 1]
    return out
for slug, aid in TZ.items():
    if aid in A:
        d = tz_lists(slug)
        for k, v in d.items(): A[aid]["tz_" + k] = v

# niche subcategory: thin or tag-poor archetypes. crossover = parent archetypes with heavy card overlap; strategy_fit.fit adds half the parents' role matches (2026-10-27, mapping is judgment, overlaps not yet measured)
NICHE = {"mutate": ["voltron", "counters", "stompy"], "infect": ["counters", "voltron", "stompy"], "forced_combat": ["group_hug", "stompy", "outlaws"],
         "pillow_fort": ["control", "group_hug", "enchantress"], "vehicles": ["artifacts", "stompy", "outlaws"], "landfall": ["lands_matter", "big_mana"],
         "sagas": ["enchantress", "blink"], "enchantress": ["sagas", "control", "pillow_fort"], "group_hug": ["pillow_fort", "forced_combat"],
         "treasure": ["artifacts", "aristocrats", "outlaws"], "theft": ["control", "outlaws"], "wheels": ["group_hug", "control"], "impulse_draw": ["outlaws", "stompy"], "legends_matter": ["voltron", "stompy"]}
for _i, _p in NICHE.items():
    if _i in A: A[_i]["niche"] = True; A[_i]["crossover"] = [x for x in _p if x in A]

TOON_COLS = "archetype,source,url,facts"

def jtoon(v): return str(v).replace("\n", " ").replace(",", ";")

REF = os.path.join(HERE, "../../agents/reference/ARCHETYPES.toon")

def write_ref():
    """condensed reference for the deck builder, main session and readers: engine goals (baseline roles), then one row per archetype"""
    def rng(n): return "-".join(map(str, n)) if n else "-"
    L = ["# Archetype and engine reference, generated by tools/concordia/strategies/build_strategies.py (do not hand-edit). Full data: strategies/strategies.json.",
         "# Engine goals apply to nearly every deck; an archetype row lists its role slots as role:min-max (a role with no count is a signal only). niche = thin archetype that borrows its crossover parents' fit.",
         f"engine[{len(BASELINE)}|]{{role|count|signals|note}}:"]
    for k, b in BASELINE.items():
        L.append("  " + "|".join([k, rng(b["n"]), "+".join(b["sig"]), jtoon(b.get("note", ""))]))
    L.append("engine_uplift: recursion " + "; ".join(f"{a} {rng(n)}" for a, n in RECURSION_BY_ARCHETYPE.items()) + " | protection " + "; ".join(f"{a} {rng(n)}" for a, n in PROTECTION_BY_ARCHETYPE.items()))
    L.append("removal: one family `remove:*` (destroy, exile, bounce, tuck, sacrifice); a card counts 1 whether it hits one creature or any number")
    L.append(f"archetypes[{len(A)}|]{{id|plan|roles|crossover|colors}}:")
    for a in A.values():
        roles = ",".join(f"{r}:{rng(d['n'])}" for r, d in a["roles"].items() if not r.startswith("support_"))
        L.append("  " + "|".join([a["id"], jtoon(a["plan"]), roles, ("niche>" + "+".join(a["crossover"])) if a.get("niche") else "", "+".join(a["colors"])]))
    open(REF, "w", encoding="utf-8").write("\n".join(L) + "\n")

def main():
    write_ref()
    json.dump({"version": 2, "generated": "2026-10-26", "baseline_roles": BASELINE, "recursion_by_archetype": RECURSION_BY_ARCHETYPE, "protection_by_archetype": PROTECTION_BY_ARCHETYPE, "aliases": ALIASES, "sources": SRC,
               "note": "removal_mass/edict/extra_combat are not ftags; mapped to removal/sacrifice/trigger:beginning_of_combat (coarse). Named cards absent from pool are reference only. ftags signals: 'x' matches tag x and x:*, 'x:y' exact. cmc_ge_N is a computed condition. weak_tags are opposing-deck tags that hurt the archetype (use in balancer).",
               "archetypes": A}, open(os.path.join(HERE, "strategies.json"), "w"), indent=1)
    rows = []
    for a in A.values():
        for k, f in a["src"].items():
            if f: rows.append((a["id"], k, SRC[k], jtoon(f)))
    with open(LOG, "w") as fh:
        fh.write("# Public strategy guide facts per archetype and source, fetched 2026-10-25. Facts and counts only (no page prose stored).\n")
        fh.write(f"strategy_sources[{len(rows)}]{{{TOON_COLS}}}:\n")
        for r in rows: fh.write("  " + ",".join(r) + "\n")
    print(len(A), "archetypes,", len(rows), "source rows")

if __name__ == "__main__": main()

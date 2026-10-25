#!/usr/bin/env python3
"""Synthesis of four public Commander strategy guides into data for the deck builder and balancer (2026-10-25).
Sources (facts only, no page prose is stored): sw = spellweave.app/guides/edh-archetypes, em = edhmatch.com/strategies/<slug>,
cf = commander-forge.com/archetypes, tz = turnzerohq.com/guides/archetypes.
Writes strategies.json (what build/balance code reads) and ../../agents/logs/strategy-sources.toon (per-source learning rows).
Usage: python3 build_strategies.py            # regenerate both files
Role signals are ftags prefixes (pool.pkl 'ftags'): "x" matches tag x and "x:*"; "x:y" matches exactly."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "../../agents/logs/strategy-sources.toon")
SRC = {"sw": "https://spellweave.app/guides/edh-archetypes", "em": "https://www.edhmatch.com/strategies",
       "cf": "https://commander-forge.com/archetypes", "tz": "https://turnzerohq.com/guides/archetypes"}

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
     "recursion": R(["recursion", "reanimate"], ["Meren of Clan Nel Toth"], None)},
    ["drain by stacked death triggers on a mass sacrifice turn", "recurring sac loop for infinite triggers", "grind then drain"],
    "graveyard hate and exile stop recursion; Hushbringer-style trigger stops; activated-ability taxes slow outlets; slow versus fast combo",
    ["grave_hate", "restrict_kind:cant_activate"], ["sacrifice", "tokens", "lifegain", "graveyard"],
    ["B", "WB", "BR", "BG", "WBR"], dict(sw="stack 2-3 drain triggers with a free outlet; bracket 2-4", em="payoffs 8-10, outlets 5-8, fodder 10-12, engine pieces cost 1-3", cf="sub: aristocrats, blood artist, food chain, treasure sac; need fodder+outlet+payoff, outlet redundancy", tz="usually also go-wide"),
    subs=["aristocrats", "blood_artist", "food_chain", "treasure_sac"], bracket=[2, 4])

add("sacrifice", "permanents are expendable fuel for outlets; value comes from the sacrifice itself, not only deaths",
    ["early: fodder plus at least one free outlet", "mid: sacrifice for mana, cards or triggers; sacrifice in response to removal", "rebuild with recursion and tokens", "win: drain, edicts or attack with rebuilt board"],
    {"outlet": R(["sacrifice_outlet"], ["Viscera Seer", "Carrion Feeder", "Ashnod's Altar", "Phyrexian Altar"], [3, 5]),
     "fodder": R(["token_make", "recursion"], ["Reassembling Skeleton"], [8, 10]),
     "payoff": R(["trigger:dies", "sacrifice"], ["Grave Pact", "Pitiless Plunderer"], None),
     "card_adv": R(["draw", "cost_sacrifice_target"], ["Village Rites", "Deadly Dispute"], [8, 10]),
     "interaction": R(["sacrifice", "effect:sacrifice"], [], [6, 8])},
    ["drain via stacked death payoffs", "outlet plus recursion loops", "edict grind then attack"],
    "graveyard hate; loses outlets or payoff enchantments; token-light draws; slow vs fast combo",
    ["grave_hate"], ["aristocrats", "tokens", "graveyard", "reanimator"], ["B", "BG", "BR", "BRG"],
    dict(em="outlets 3-5, fodder 8-10, sac-tied card advantage 8-10, edict interaction 6-8, low curve", cf="Sacrifice group of 17; needs fodder, outlet, payoff"))

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
    ["removal", "restrict_kind:cant_attack", "attack_tax"], ["aristocrats", "counters", "aggro", "tribal", "blink", "proliferate"],
    ["GW", "WB", "RG", "UR", "RGW"], dict(sw="2-3 turns wide then mass pump or doubler; bracket n/a", em="generators 10-14, doublers 2-4, anthems 4-6, draw 6-8, ramp 8-10, wipe answers 3-5", cf="sub: go wide, anthems, populate, convoke", tz="Doubling Season + Parallel Lives quadruples; sample 36 lands 12 ramp 9 removal 32 creatures 7 draw 1 wipe; Jetmir escalates at 3/6/9 attackers"),
    subs=["go_wide", "anthems", "populate", "convoke"])

add("tribal", "density of one creature type; lords stack multiplicatively; payoffs reward casting or attacking with the type",
    ["early: type two-drops and cost reducers", "mid: lords and card-advantage payoffs", "finish: mass pump or type-specific payoff"],
    {"lord": R(["lord", "pump_team"], ["Goblin King", "Lord of Atlantis", "Elvish Archdruid", "Goblin Chieftain", "Merrow Reejerey"], None),
     "cost_reducer": R(["cost_reduce"], ["Urza's Incubator", "Herald's Horn"], None),
     "card_adv": R(["draw", "trigger:spell_cast"], ["Kindred Discovery", "Vanquisher's Banner"], None),
     "anthem": R(["pump_team"], ["Coat of Arms", "Shared Animosity"], None),
     "protection": R(["cant_be_countered"], ["Cavern of Souls", "Path of Ancestry"], None),
     "recursion": R(["recursion", "reanimate"], ["Patriarch's Bidding"], None)},
    ["mass pump on a wide board", "Shared Animosity lethal", "type-specific payoffs (Gishath, Lathril, Kumena)"],
    "board wipes, Engineered Plague, Extinction; targeted removal on lords; filler creatures kept only for type",
    ["removal"], ["aristocrats", "tokens", "aggro"], ["any"],
    dict(sw="variants aggro, combo (Slivers, Wizards), value (Merfolk, Faeries)", em=None, cf="sub under Creatures: Tribal, Aggro, Extra Combat, Power Matters", tz="three lords outscale one; commit to a type, deploy lords and payoffs, attack as one"),
    notes="Concordia rule H74: tribe match counts only with tribal abilities. Tag niche:tribal marks cards that only pay off in a matching deck.")

add("voltron", "one protected threat (usually the commander) wins by 21 commander damage, often in two swings",
    ["pick the single threat", "attach equipment/auras: power, evasion, protection", "hold protection so removal or bounce does not reset", "rebuild by re-equipping or recasting", "remove players one at a time"],
    {"attach": R(["equip", "kw:equip", "kw:enchant", "kw:bestow"], ["Sword of the Animist", "Commander's Plate", "Sword of Feast and Famine", "All That Glitters", "Shielded by Faith", "Battle Mastery", "Ethereal Armor"], [12, 18]),
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
    {"equipment": R(["equip", "kw:equip", "target_type:equipment"], ["Colossus Hammer", "Sword of Feast and Famine"], [10, 14]),
     "tutor": R(["tutor"], ["Stoneforge Mystic", "Steelshaper's Gift", "Open the Armory"], None),
     "cost_reducer": R(["cost_reduce"], ["Puresteel Paladin", "Sigarda's Aid", "Brass Squire"], None),
     "draw": R(["draw"], ["Sram, Senior Edificer"], None),
     "carrier": R(["evasion", "grant_double_strike"], [], [12, 18]),
     "protection": R(["protection_trick"], [], [6, 10])},
    ["commander damage from a safe carrier", "spread weapons over tokens", "sword triggers plus extra combats"],
    "artifact removal and wipes; equip mana after carrier dies; gear with no creatures does nothing",
    ["removal_artifact"], ["voltron", "aggro", "artifacts"], ["W", "RW", "R"],
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
    ["grave_hate", "counterspell"], ["graveyard", "sacrifice", "mill"], ["B", "UB", "WB", "BG"],
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
    ["grave_hate"], ["aristocrats", "sacrifice", "reanimator", "mill"], ["BG", "BGU", "UB", "WBG"],
    dict(sw="dredge, flashback, escape; overlaps reanimator and self-mill", em="fillers 8-10, recursion 8-12, 1-2 backup engines, favor ETB/death-trigger creatures", cf="same Graveyard group as reanimator"),
    subs=["self_mill", "dredge", "flashback"])

add("mill", "empty libraries (three opponents: repeatable and doubled mill) or cash in stocked graveyards",
    ["choose opponent mill or self-mill", "deploy repeatable mill over several turns", "add doublers", "protect engines", "cash graveyards for recursion, theft or drain"],
    {"engine": R(["mill", "self_mill"], ["Mesmeric Orb", "Ruin Crab", "Sphinx's Tutelage", "Fleet Swallower"], [8, 12]),
     "doubler": R(["mill", "replace"], ["Bruvac the Grandiloquent", "Fraying Sanity"], [2, 3]),
     "payoff": R(["mill"], ["Consuming Aberration", "Bloodchief Ascension", "Maddening Cacophony"], None),
     "outlet": R(["sacrifice_outlet"], ["Altar of Dementia"], None),
     "interaction": R(["removal", "counterspell"], [], [8, 10]),
     "graveyard_exile": R(["exile_from", "grave_hate"], [], None)},
    ["empty libraries with doubled mill or Traumatize", "self-mill into Jace, Wielder of Mysteries / Laboratory Maniac", "mass reanimation or theft"],
    "three 99-card libraries are slow; shuffle-back effects; mill feeds reanimator opponents; graveyard hate",
    ["grave_hate"], ["reanimator", "graveyard", "control"], ["U", "UB", "BGU"],
    dict(sw="win by empty library", em="engines 8-12, multipliers 2-3, interaction 8-10", cf="subs: self-mill, opponent mill, mill combo, Bruvac"),
    subs=["self_mill", "opponent_mill", "mill_combo"])

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
    ["restrict", "attack_tax", "counterspell"], ["storm", "combo", "control", "card_draw"], ["UR", "UBR", "URW"],
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
     "removal": R(["removal"], [], None)},
    ["infinite mana into X spell", "Kiki-Jiki loops", "Thassa's Oracle package", "drain loop", "Scepter + Dramatic Reversal"],
    "single counterspell or removal; tutor punishers (Opposition Agent, Aven Mindcensor, Archivist of Oghma); hand attack; Null Rod, Collector Ouphe; stax strands tutors",
    ["counterspell", "restrict", "discard"], ["spellslinger", "storm", "control", "stax"], ["UB", "UR", "WB", "BG"],
    dict(sw="bracket 3-4", em="combos 2-3, tutors 5-10, draw 8-12, protection 6-10, redundancy", tz="often a backup plan in other archetypes"), bracket=[3, 4])

add("counters", "grow creatures with +1/+1 counters and multiply them until the weakest creature is huge",
    ["cast creatures that enter with counters", "multipliers so each trigger gives more", "spread counters across bodies", "convert big creatures to cards/mana/life/pressure", "protect the engine, attack with creatures that outgrow blocks"],
    {"multiplier": R(["counters_plus", "replace"], ["Hardened Scales", "Branching Evolution", "Conclave Mentor", "Doubling Season"], [3, 5]),
     "enabler": R(["counter:p1p1", "counters_plus"], ["Rishkar, Peema Renegade", "Mikaeus, the Lunarch"], [15, 20]),
     "proliferate": R(["proliferate"], ["Evolution Sage", "Inexorable Tide", "Karn's Bastion"], [4, 6]),
     "draw_payoff": R(["draw", "counters_plus"], ["Fathom Mage", "Champion of Lambholt", "Inspiring Call", "Rishkar's Expertise"], [6, 8]),
     "protection": R(["protection_trick"], ["The Ozolith", "Nesting Grounds", "Heroic Intervention"], [3, 5]),
     "ramp": R(["mana_source"], [], [8, 10])},
    ["tall trampling board", "Simic Ascendancy", "Overwhelming Stampede", "evasion/removal to pass blockers"],
    "board wipes (Farewell, Toxic Deluge); Solemnity; Vampire Hexmage; setup turns; removal on doublers",
    ["removal", "counter_prevent"], ["proliferate", "tokens", "voltron", "lifegain"], ["GW", "GU", "WBG"],
    dict(sw="doublers, distributors, payoffs, proliferate", em="multipliers 3-5, creatures 15-20, proliferate 4-6, draw 6-8, ramp 8-10, protection 3-5", cf="subs: +1/+1, proliferate, modular, hydras"),
    subs=["p1p1", "modular", "hydras"])

add("proliferate", "seed any counter type, then one trigger adds to all of them",
    ["place first counters (+1/+1, poison, loyalty, charge)", "trigger proliferate from spells, lands, abilities", "spread across creatures, walkers, artifacts", "protect board", "pick route (combat, ultimates, poison)"],
    {"engine": R(["proliferate"], ["Evolution Sage", "Flux Channeler", "Inexorable Tide", "Contagion Engine", "Karn's Bastion"], [8, 12]),
     "seed": R(["counter", "loyalty_change"], [], [10, 15]),
     "protection": R(["protection_trick"], ["The Ozolith"], None),
     "draw": R(["draw"], [], [8, 10])},
    ["grown counter board", "planeswalker ultimates", "ten poison via proliferate", "Simic Ascendancy"],
    "proliferate multiplies but does not create; board wipes; slow; poison draws attention",
    ["removal"], ["counters", "infect", "superfriends"], ["GU", "WUBG", "WU", "UB"],
    dict(em="engines 8-12, seeds 10-15, draw 8-10, poison 1-2 optional; careful with sagas/vanishing/fading", cf="sub of Counters", tz="Atraxa archetype"))

add("infect", "poison (infect/toxic) instead of life loss; 10 counters via a pumped evasive attacker plus proliferate",
    ["attack early with infect/toxic creatures", "pump an evasive attacker for 10 in one or two hits", "proliferate to finish", "protect the swing"],
    {"creature": R(["kw:infect", "kw:toxic"], ["Skithiryx, the Blight Dragon", "Blightsteel Colossus", "Inkmoth Nexus"], [15, 20]),
     "pump": R(["pump_single", "grant_kw:infect"], ["Groundswell", "Might of Old Krosa", "Berserk", "Triumph of the Hordes", "Grafted Exoskeleton"], [6, 10]),
     "proliferate": R(["proliferate"], ["Evolution Sage", "Contagion Engine", "Tezzeret's Gambit"], [5, 8]),
     "protection": R(["protection_trick"], [], [6, 8])},
    ["ten poison on each opponent", "proliferate after combat"],
    "table aggression; fog, deathtouch blockers, wipes; some pods ban poison; lifegain irrelevant to the clock",
    ["fog", "removal"], ["voltron", "proliferate", "aggro"], ["BG", "GU", "WBG"],
    dict(em="creatures 15-20, pump 6-10, proliferate 5-8, protection 6-8", cf="sub of Voltron: Infect"))

add("lifegain", "convert life gained into counters, cards, tokens, drain or a charged Aetherflux Reservoir",
    ["gain life in repeat small increments", "payoffs turn each trigger into value", "use the life buffer to play patiently", "close with drain loop, oversized board or Reservoir"],
    {"trigger": R(["lifegain", "kw:lifelink", "trigger:gain_life"], ["Soul Warden", "Essence Warden", "Suture Priest", "Authority of the Consuls"], [8, 12]),
     "payoff": R(["trigger:gain_life"], ["Ajani's Pridemate", "Heliod, Sun-Crowned", "Vito, Thorn of the Dusk Rose", "Archangel of Thune"], [6, 10]),
     "drain": R(["life_loss", "drain"], ["Sanguine Bond", "Exquisite Blood"], None),
     "conversion": R(["draw"], ["Aetherflux Reservoir", "Well of Lost Dreams"], None),
     "ramp": R(["mana_source"], [], [10, 12]),
     "interaction": R(["removal", "removal"], [], [6, 8])},
    ["Vito/Sanguine Bond drain loop", "oversized payoff creatures", "Aetherflux Reservoir"],
    "life does not stop commander damage, poison or combo; payoffs draw removal; Tainted Remedy, Rain of Gore, Roiling Vortex; slow start",
    ["life_loss", "restrict"], ["aristocrats", "counters", "group_hug", "enchantress"], ["W", "WB", "GW", "WBG"],
    dict(sw="bracket 1-3", em="sources 8-12, payoffs 6-10, ramp 10-12, removal 6-8; redundant Pridemate/Vito/Heliod effects first", cf="subs: soul sisters, payoffs, angel lifegain, drain; Beginner friendly"),
    subs=["soul_sisters", "payoffs", "angel_lifegain", "drain"], bracket=[1, 3])

add("blink", "flicker creatures to reuse enter-the-battlefield triggers; a blink on a draw creature is a repeating engine",
    ["cast ETB creatures that draw, remove, ramp, drain or make tokens", "reuse with flicker spells and repeatable engines", "hold instant-speed blink as protection", "grind card and board advantage", "finish with token engine or trigger loop"],
    {"flicker": R(["clone", "exile", "return", "put_onto_battlefield"], ["Ephemerate", "Momentary Blink", "Ghostly Flicker", "Conjurer's Closet"], [8, 12]),
     "engine": R(["trigger:end_step", "put_onto_battlefield"], ["Thassa, Deep-Dwelling", "Soulherder", "Teleportation Circle", "Panharmonicon"], None),
     "etb_creature": R(["trigger:etb"], ["Mulldrifter", "Thragtusk", "Ravenous Chupacabra", "Reflector Mage", "Eternal Witness", "Sun Titan", "Knight of Autumn", "Agent of Treachery"], [20, 25]),
     "recursion": R(["recursion"], ["Archaeomancer", "Mnemonic Wall"], None),
     "finisher": R(["life_loss", "token_make"], ["Gray Merchant of Asphodel", "Deadeye Navigator", "Peregrine Drake", "Palinchron"], None)},
    ["out-card then outsize removal", "token-producer blink for width", "looped drain triggers", "extra turns (Time Stretch)"],
    "Torpor Orb and Hushbringer; exile or commander removal; slow clock",
    ["restrict"], ["control", "card_draw", "tokens"], ["WU", "GWU", "WUB"],
    dict(sw="engines, ETB targets, Panharmonicon, Deadeye Navigator loop", em="flicker 8-12, ETB creatures 20-25", cf="subs: ETB value, flicker combo, Panharmonicon, Soulherder"),
    subs=["etb_value", "flicker_combo", "panharmonicon", "soulherder"])

add("landfall", "every land drop is a trigger; extra drops plus recursion give 3+ triggers a turn",
    ["play land / fetch for extra triggers", "stack extra land drops", "recur lands from the graveyard", "convert triggers to tokens, counters, cards, damage, combats"],
    {"payoff": R(["condition:landfall", "niche:landfall"], ["Avenger of Zendikar", "Scute Swarm", "Omnath, Locus of Creation", "Omnath, Locus of Rage", "Valakut Exploration", "Felidar Retreat", "Tireless Tracker", "Tatyova, Benthic Druid"], [8, 10]),
     "extra_drop": R(["extra_land_drop"], ["Exploration", "Oracle of Mul Daya", "Azusa, Lost but Seeking", "Dryad of the Ilysian Grove", "Wayward Swordtooth"], [4, 6]),
     "recursion": R(["recursion", "from_zone:graveyard"], ["Crucible of Worlds", "Ramunap Excavator", "Life from the Loam"], [2, 3]),
     "fetch": R(["niche:lands", "land_tutor"], ["Evolving Wilds", "Cultivate", "Three Visits"], None),
     "ramp": R(["mana_source", "land_tutor"], ["Lotus Cobra"], None),
     "interaction": R(["removal"], [], [5, 7])},
    ["go wide with Scute Swarm/Avenger", "landfall damage", "extra combats (Moraug)"],
    "board wipes; missed land drops; early removal on Cobra/Azusa; Strip Mine, Wasteland, Blood Moon, Back to Basics",
    ["removal_land", "restrict"], ["ramp", "big_mana", "tokens"], ["G", "RG", "GU", "GW"],
    dict(sw="lands matter / landfall; extra drops plus recursion", em="payoffs 8-10, extra drops 4-6, recursion 2-3, interaction 5-7, 40+ lands", cf="Lands group: landfall, land destruction, land recursion, Maze's End", tz="lands matter is usually also ramp"),
    subs=["landfall", "land_destruction", "land_recursion", "mazes_end"])

add("ramp", "accelerate early so later turns come sooner; mana lead converts to threats ahead of curve",
    ["turns 1-3: rocks, dorks, land ramp", "have more mana than the table", "deploy threats ahead of curve", "close with scaling top-end"],
    {"ramp": R(["mana_source", "land_tutor", "tutor_target:basic_land"], ["Sol Ring", "Cultivate", "Sakura-Tribe Elder", "Llanowar Elves", "Arcane Signet", "Kodama's Reach", "Rampant Growth"], [10, 12]),
     "multiplier": R(["mana_amount", "replace"], ["Zendikar Resurgent", "Mana Reflection", "Nyxbloom Ancient"], None),
     "draw": R(["draw"], [], [8, 10]),
     "interaction": R(["removal", "counterspell"], [], [8, 10]),
     "finisher": R(["x_is:x_paid"], ["Craterhoof Behemoth"], None)},
    ["scaling top-end threats", "big X spells", "mana-lead tempo"],
    "exposes you to aggro and combo; one big threat dies to removal; wipes hit dorks and rocks",
    ["removal", "counterspell"], ["big_mana", "landfall", "artifacts", "group_hug"], ["G", "GU", "RG", "GW"],
    dict(em="ramp 10-12 (prioritise 2-mana), lands 37-40, draw 8-10, interaction 8-10", tz="ramp pairs with lands matter"))

add("big_mana", "ramp past normal development and cast few huge spells that change the board at once",
    ["turns 1-3: ramp and doublers", "protect the mana engine", "cast a few haymakers", "after sweepers rebuild through land ramp"],
    {"ramp": R(["mana_source", "land_tutor"], [], [12, 15]),
     "multiplier": R(["mana_amount", "replace"], ["Nyxbloom Ancient", "Mana Reflection", "Zendikar Resurgent"], [2, 4]),
     "mana_land": R(["mana_source"], ["Nykthos, Shrine to Nyx", "Cabal Coffers"], None),
     "draw": R(["draw"], [], [8, 10]),
     "haymaker": R(["x_is:x_paid"], ["Torment of Hailfire", "Genesis Wave", "Expropriate", "Rishkar's Expertise"], [4, 6]),
     "interaction": R(["removal", "counterspell"], [], [5, 7])},
    ["X spells", "Torment of Hailfire", "Expropriate", "Genesis Wave"],
    "single counterspell wastes a turn; aggro and fast combo; visible mana invites pressure",
    ["counterspell"], ["ramp", "storm", "landfall"], ["G", "RG", "GUR", "B"],
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
    {"answer": R(["counterspell", "removal"], ["Swords to Plowshares", "Cyclonic Rift"], [8, 12]),
     "sweeper": R(["removal"], ["Supreme Verdict"], [6, 10]),
     "draw_engine": R(["draw"], ["Rhystic Study", "Mystic Remora"], None),
     "finisher": R(["cmc_ge_5"], ["Teferi, Hero of Dominaria"], [2, 3])},
    ["protected finisher", "planeswalker", "combo after interaction spent", "card advantage"],
    "one-for-one answers lose value to three opponents; slow clocks; fast rebuilders",
    ["cant_be_countered"], ["card_draw", "blink", "mill", "stax", "combo"], ["WU", "UB", "WUB", "UR"],
    dict(em="wipes 6-10, answers 8-12, finishers 2-3, lands 36-38", cf="subs: draw-go, tap-out control, pillowfort, mass removal"),
    subs=["draw_go", "tap_out", "pillowfort", "mass_removal"])

add("group_hug", "give the table cards, lands or mana and profit from how they use it",
    ["give lands or mana first", "steer attacks and removal toward others", "pay off every draw or land drop", "hold interaction for the best user of gifts", "win with a hidden spell or late payoff"],
    {"shared": R(["draw", "put_onto_battlefield"], ["Howling Mine", "Temple Bell", "Rites of Flourishing", "Kynaios and Tiro of Meletis", "Phelddagrif"], [8, 12]),
     "breaker": R(["draw", "mana_source"], ["Smothering Tithe", "Consecrated Sphinx", "Zedruu the Greathearted"], [4, 6]),
     "pillowfort": R(["attack_tax", "restrict"], ["Propaganda", "Ghostly Prison"], None),
     "win": R([], ["Approach of the Second Sun"], None)},
    ["Approach of the Second Sun", "alternate win with large hand", "politics"],
    "accelerates opponents; little pressure; hidden win conditions draw interaction",
    ["removal"], ["lifegain", "card_draw", "ramp"], ["U", "GU", "WUR"],
    dict(em="shared effects 8-12, breakers 4-6, lands 36-38", sw="Kynaios and Tiro, Phelddagrif, Kenrith"))

add("enchantress", "cheap enchantments replace themselves through draw triggers; constellation or aura payoff converts them to a win",
    ["cast cheap enchantments", "enchantress triggers replace them", "stack 2+ draw engines", "protect the engine", "finish with constellation, tokens or aura Voltron"],
    {"draw": R(["draw", "trigger:spell_cast"], ["Argothian Enchantress", "Enchantress's Presence", "Setessan Champion", "Mesa Enchantress", "Sythis, Harvest's Hand", "Tuvasa the Sunlit"], [6, 10]),
     "cheap_ench": R(["cardtype:enchantment", "kw:enchant"], ["Wild Growth", "Utopia Sprawl", "Sanctum Weaver", "Fertile Ground"], None),
     "protection": R(["protection_trick"], ["Sterling Grove", "Greater Auramancy", "Heroic Intervention"], None),
     "payoff": R(["token_make"], ["Sigil of the Empty Throne", "Ajani's Chosen"], None),
     "recursion": R(["recursion"], ["Hall of Heliod's Generosity"], None)},
    ["constellation triggers", "enchantment-cast tokens", "aura Voltron", "card lead"],
    "enchantment removal and wipes (Farewell, Bane of Progress, Back to Nature); losing enchantresses; payoff-heavy hands",
    ["removal_enchantment", "removal"], ["card_draw", "voltron", "lifegain"], ["GW", "GWU", "WB"],
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
    ["removal_artifact", "restrict"], ["equipment", "stax", "ramp", "treasure"], ["U", "UR", "WU", "WUB"],
    dict(em="artifacts 25-35, cost reducers 3-5", cf="subs: artifact tokens, affinity, equipment, artifact combo", sw="Urza, Breya, Jhoira"),
    subs=["artifact_tokens", "affinity", "equipment", "artifact_combo"])

add("superfriends", "planeswalker density protected by blockers; loyalty doubling and extra activations",
    ["land a walker", "protect it", "activate again; surviving walkers are a resource", "multiple ultimates in one turn via doubling"],
    {"walker": R(["loyalty_change", "loyalty", "cardtype:planeswalker"], ["Saheeli, Filigree Master"], None),
     "doubler": R(["counters_plus", "replace"], ["Doubling Season", "Deepglow Skate", "Vorinclex, Monstrous Raider"], None),
     "extra_activation": R(["loyalty_change"], ["The Chain Veil", "Oath of Teferi"], None),
     "defense": R(["token_make", "removal"], ["Elspeth, Sun's Champion", "Ugin, the Spirit Dragon"], None),
     "mana": R(["mana_source"], ["Nissa, Who Shakes the World", "Interplanar Beacon"], None),
     "removal": R(["removal"], ["Karn Liberated"], None)},
    ["multiple ultimates one turn", "accumulated walker value"],
    "walkers without defense are free attack targets; slow and mana-hungry; archenemy after two ultimates",
    ["removal_planeswalker"], ["counters", "proliferate", "control"], ["WUB", "G", "WUBG"],
    dict(tz="Atraxa, Carth the Lion, Sisay, Commodore Guff, Freyalise, Dihada, Nahiri, Jared Carthalion, Ramos, Saheeli commanders"))

add("aggro", "commit cheap threats early and attack often; 120 total damage across the table",
    ["deploy 1-3 mana creatures early", "attack before engines stabilise", "spread pressure at the opponent who absorbs least", "anthems, haste, attack triggers scale bodies", "chain extra combats", "refuel with combat draw"],
    {"creature": R(["cardtype:creature"], [], [25, 35]),
     "anthem": R(["pump_team", "lord"], ["Shared Animosity", "Cathars' Crusade"], [2, 4]),
     "haste": R(["haste_grant", "kw:haste"], ["Fervor", "Rising of the Day"], None),
     "extra_combat": R(["trigger:beginning_of_combat"], ["Aggravated Assault", "Moraug, Fury of Akoum"], [2, 3]),
     "refuel": R(["draw", "trigger:combat_damage"], ["Reconnaissance Mission", "Toski, Bearer of Secrets"], None),
     "finisher": R(["damage"], ["Impact Tremors", "Isshin, Two Heavens as One"], None),
     "removal": R(["removal"], [], None)},
    ["wide anthem attacks over consecutive turns", "extra combats for 40+ in a turn", "burn/drain at low life"],
    "board wipes; running out of gas; pillowfort and lifegain; late topdecks",
    ["removal", "attack_tax", "fog"], ["tokens", "equipment", "infect", "tribal"], ["RW", "RG", "BRW", "R"],
    dict(em="creatures 25-35, anthems 2-4, extra combats 2-3, lands 33-35", cf="Creatures group: aggro; Beginner friendly"),
    subs=["aggro", "extra_combat", "power_matters"])

add("card_draw", "draw beyond the normal turn draw and convert a full hand to damage, drain or stocked interaction",
    ["deploy cheap draw engines early", "draw extra", "convert to damage/drain/tokens/answers", "hold interaction", "win late with card advantage"],
    {"engine": R(["draw", "draw_count"], ["Rhystic Study", "Mystic Remora", "Guardian Project", "Windfall"], [10, 15]),
     "cantrip": R(["draw", "selection"], ["Brainstorm", "Ponder"], None),
     "payoff": R(["draw"], ["Niv-Mizzet, Parun", "Sheoldred, the Apocalypse", "Psychosis Crawler", "Consecrated Sphinx"], [3, 5]),
     "no_max_hand": R(["restrict"], ["Reliquary Tower", "Thought Vessel"], None)},
    ["draw-damage triggers", "Sheoldred plus wheels", "out-resource late game", "Laboratory Maniac"],
    "engines draw removal; little board presence; Notion Thief, Narset; decking risk",
    ["discard", "restrict"], ["control", "spellslinger", "group_hug", "enchantress", "blink"], ["U", "UR", "UB", "GU"],
    dict(em="engines 10-15, payoffs 3-5, dense interaction, more lands or ramp"))

add("burn", "direct damage to faces scaled to 120 life across three opponents: each-opponent effects and multipliers",
    ["prioritise each-opponent damage and doublers", "repeatable pingers", "earthquake effects"],
    {"damage": R(["burn", "damage", "damage_amount"], ["Torbran, Thane of Red Fell", "Purphoros, God of the Forge", "Kaervek the Merciless"], None),
     "multiplier": R(["replace"], ["Torbran, Thane of Red Fell"], None),
     "pinger": R(["damage", "cost:tap"], [], None)},
    ["face damage with multipliers", "Earthquake", "group slug"],
    "single-target burn is inefficient in multiplayer; lifegain",
    ["lifegain"], ["aggro", "spellslinger"], ["R", "BR", "UR"],
    dict(sw="burn must scale to 120 life", cf="subs: direct damage, ping, group slug, earthquake"), subs=["direct_damage", "ping", "group_slug", "earthquake"])

add("chaos", "randomness, cascade and theft: warp the game with symmetrical effects your deck is built to exploit",
    ["pick effects your deck exploits", "cascade chains, coin flips, theft"],
    {"cascade": R(["kw:cascade", "cast_free"], [], None), "theft": R(["steal", "steal_temp"], ["Gonti, Lord of Luxury"], None)},
    ["free-spell chains", "stolen permanents"], "symmetrical chaos helps everyone", [], ["group_hug"], ["R", "UR", "RG"],
    dict(cf="subs: coin flip, cascade, theft, possibility storm; Zndrsplt, Yidris, Gonti, Kalamax"), subs=["coin_flip", "cascade", "theft", "possibility_storm"])

# archetypes seen only as one-liners on Spellweave (no detail on the page)
for i, (plan, ex) in {"treasure": ("make Treasure and convert it to mana, drain or sacrifice value", ["Prosper, Tome-Bound", "Korvold, Fae-Cursed King", "Magda, Brazen Outlaw"]),
                      "wheels": ("symmetrical discard-and-draw with punishers", ["Nekusar, the Mindrazer", "Xyris, the Writhing Storm", "The Locust God"]),
                      "impulse_draw": ("exile-and-play cards for card advantage", ["Prosper, Tome-Bound", "Birgi, God of Storytelling", "Etali, Primal Conqueror", "Narset, Enlightened Exile", "Notion Thief"]),
                      "legends_matter": ("legendary-density payoffs", ["Sisay, Weatherlight Captain", "Jodah, Archmage Eternal", "Kethis, the Hidden Hand", "Dihada, Binder of Wills"])}.items():
    add(i, plan, [], {"core": R([], ex, None)}, [], "", [], [], [], dict(sw="one-line entry, no engine/weakness detail"))


# TurnZero per-archetype pages (raw/tz, from fetch_sources.py): top-10 defining cards and commanders with their stated effect
TZ = {"aggro": "aggro", "aristocrats": "aristocrats", "artifacts": "artifacts", "blink": "blink", "combo": "combo", "control": "control",
      "counters": "counters", "enchantress": "enchantress", "go-wide": "tokens", "graveyard-recursion": "graveyard", "group-hug": "group_hug",
      "lands-matter": "landfall", "lifegain": "lifegain", "mill": "mill", "ramp": "ramp", "spellslinger": "spellslinger", "stax": "stax",
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

TOON_COLS = "archetype,source,url,facts"

def jtoon(v): return str(v).replace("\n", " ").replace(",", ";")

def main():
    json.dump({"version": 1, "generated": "2026-10-25", "sources": SRC,
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

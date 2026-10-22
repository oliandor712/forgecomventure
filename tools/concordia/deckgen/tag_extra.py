"""New tags created to fill gaps seen across the references (human_logic.toon H56). Every tag family here is logged in
tags/NEW_TAGS_FOR_APPROVAL.md and is PROPOSED until the user approves it. Source of each rule: the user's feedback on the starter sample
(tags/TAG_FEEDBACK_STARTER_SAMPLE.md), the Forge script, and the Comprehensive Rules.
extra(face_lines, svars, types, text) -> (flat tags, links, groups {id: tags}). A group id says which script line a tag came from: tags in the same group are linked."""
import re

COLORS = {"W": "white", "U": "blue", "B": "black", "R": "red", "G": "green", "C": "colorless"}
KWNAMES = {"flying", "trample", "haste", "vigilance", "lifelink", "deathtouch", "menace", "reach", "first", "double", "indestructible", "hexproof", "defender"}

# family -> (meaning, why / user note)
DOC = {
 "mana:<color>": ("colour of mana an ability produces (white, blue, black, red, green, colorless, any, commander_identity)", "feedback: link color type to mana source (Arcane Signet, Plains, Temple, Frost Marsh)"),
 "mana_amount:<n>": ("how much mana is produced per activation", "Temple of the False God"),
 "mana_restriction": ("the mana can only be spent on certain things", "Vodalian Arcanist"),
 "mana_choice": ("the ability lets you choose between colours", "Frost Marsh, Arcane Signet"),
 "trigger:tap": ("the ability is a tap ability (basic lands tap for one colour of mana)", "feedback: Plains, Frost Marsh trigger type"),
 "activation_restriction": ("the ability can only be activated under a condition", "Temple of the False God"),
 "enters_tapped": ("the permanent enters tapped", "Myriad Landscape, Frost Marsh"),
 "cost:tap / cost:sacrifice / cost:mana / cost:life / cost:discard": ("what the activation cost contains; sacrifice is also tagged when it is a cost", "Harrow, Blighted Woodland, Myriad Landscape"),
 "effect:sacrifice": ("sacrifice happens as an effect (not a cost)", "Garruk, Kiki-Jiki, Victimize"),
 "loyalty:<n> / loyalty_cost:+n|-n / counters:loyalty": ("planeswalker loyalty and loyalty costs; loyalty is a kind of counter", "Oko, Rowan"),
 "defense:<n>": ("battle defense value", "Invasion of ... battles"),
 "transform": ("card transforms (double-faced) or becomes a different thing", "Invasion battles"),
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
 "cast_free": ("casts a spell without paying its mana cost", "found in the cross-check: Rishkar's Expertise"),
 "target_zone:<zone>": ("the zone the targets are in (graveyard, exile, hand, library)", "Victimize"),
 "target_type:<t> / target_filter:<f> / target_scope:you_control|opp_control": ("what the effect can pick: card type, filters such as nonland, and whose", "Filter Out, Scorching Dragonfire, Oblivion Ring"),
 "trigger:etb|dies|leaves|attacks|spell_cast|... / trigger_zone:graveyard / trigger_filter:<type>": ("trigger event, the zone it goes to, and a card-type filter on cast triggers", "Rancor, Oblivion Ring, Bontu's Monument"),
 "delayed:end_step / duration:end_step": ("an effect that happens at the next end step", "Kiki-Jiki"),
 "impulse_draw": ("exile cards and let you play them for a limited time", "Invasion of Kaldheim"),
 "must_attack / cant_block": ("combat restrictions", "Rabblemaster, Rowan"),
 "exchange_control": ("swap control of two permanents (linked to steal)", "Oko"),
 "steal": ("gain control of something (linked to haste when the effect grants it)", "Rowan"),
 "cost_reduce_for:<type> + color:<c>": ("which spells a cost reduction applies to", "Bontu's Monument"),
 "counter:<type> / each_you_control": ("which counters are placed and on what", "Invasion of Moag"),
 "cost_sacrifice_target:<t>": ("what a sacrifice cost sacrifices (self, land, creature ...)", "Harrow, Blighted Woodland"),
 "sacrifice_type:<t>": ("what an edict makes players sacrifice", "Garruk"),
 "token_cardtype:artifact": ("the token is an artifact", "Memnarch, Oko"),
 "affects:<tribe>": ("which creature type a static effect applies to", "Goblin Rabblemaster"),
 "steal_grants_<kw>": ("the control-gain effect also gives a keyword (linked to steal)", "Rowan"),
 "return_exiled": ("returns what this card exiled when it leaves", "Oblivion Ring"),
 "protection_from:<colour|type>": ("what a Protection keyword protects from (kw:protection stays the keyword)", "user: protection parsed as the keyword, colours and types as separate tags"),
 "forge_line:<name>": ("a Forge engine line that is not a rules keyword (ETBReplacement, AlternateAdditionalCost, etbCounter ...)", "found in the cross-check: these were wrongly tagged kw:"),
 "landwalk:<landtype>": ("which land type a landwalk keyword names", "user: landwalk type as its own tag"),
 "recursion:return_self": ("the card returns itself (to hand, from the graveyard)", "Rancor"),
}


def tok(s): return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def params(body):
    d = {}
    for item in body.split(" | "):
        m = re.match(r"^(\w+)\$ ?(.*)$", item)
        if m: d[m.group(1)] = m.group(2)
    return d


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
        if main[0] and main[0] not in ("Any",): out.append("target_type:" + tok(main[0]))
        else: out.append("target_type:any")
        rest = main[1:] + bits[1:]
        for r in rest:
            if r in ("YouCtrl", "YouOwn"): out.append("target_scope:you_control")
            elif r in ("OppCtrl", "YouDontCtrl"): out.append("target_scope:opp_control")
            elif r.startswith("non") or r in ("Other", "Basic", "Legendary", "Tapped", "Untapped"): out.append("target_filter:" + tok(r))
            elif r and r[0].isupper() and main[0] in ("Permanent", "Card", "Creature"): out.append("target_filter:" + tok(r))


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
    for key, prov in (("food", "lifegain"), ("treasure", "mana_source"), ("clue", "draw"), ("blood", "discard")):
        if ty == key: out.append(prov)


def cost_tags(cost, out):
    if not cost: return
    if re.search(r"(^|\s)T(\s|$)", cost): out.append("cost:tap")
    m = re.search(r"Sac<[^/>]*/([^/>]*)", cost)
    if "Sac<" in cost:
        out.append("cost:sacrifice"); 
        if m: out.append("cost_sacrifice_target:" + ("self" if m.group(1) == "CARDNAME" else tok(m.group(1).split(".")[0])))
    if "PayLife" in cost: out.append("cost:life")
    if "Discard<" in cost: out.append("cost:discard")
    for m in re.finditer(r"AddCounter<(\d+)/LOYALTY>", cost): out += ["loyalty_cost:+" + m.group(1), "counters:loyalty"]
    for m in re.finditer(r"SubCounter<(\d+)/LOYALTY>", cost): out += ["loyalty_cost:-" + m.group(1), "counters:loyalty"]
    c2 = re.sub(r"\w+<[^>]*>", "", cost)
    if re.search(r"(^|\s)(\d+|X|[WUBRGC])(\s|$)", c2): out.append("cost:mana")


def extra(lines, sv, types, text):
    groups = {"c0": []}          # group id -> tags: c0 = card level, cN = the N-th A/S/T/R line (same numbering as tag_run clauses)
    cur = ["c0"]
    links = []
    def add(*t): groups[cur[0]].extend(t)
    def lk(a, rel, b): links.append(("%s:%s" % (cur[0], a), rel, "%s:%s" % (cur[0], b)))
    for l in lines:
        if l.startswith("Loyalty:"): add("loyalty:" + l[8:].strip(), "counters:loyalty")
        if l.startswith("Defense:"): add("defense:" + l[8:].strip())
    if "AlternateMode:DoubleFaced" in text or "AlternateMode:Modal" in text: add("transform")
    if "Basic" in types.split() and "Land" in types.split():
        for t, c in (("Plains", "white"), ("Island", "blue"), ("Swamp", "black"), ("Mountain", "red"), ("Forest", "green")):
            if t in types.split(): add("mana_source", "mana:" + c, "trigger:tap"); lk("mana_source", "produces", "mana:" + c)
    oracle = next((l[7:] for l in lines if l.startswith("Oracle:")), "")
    if re.search(r"enters(?: the battlefield)? tapped(?!.*unless)", oracle) and "Basic" not in types.split(): add("enters_tapped")
    bodies = []
    for l in lines:
        m = re.match(r"^(A|S|T|R):(.*)$", l)
        if m: bodies.append((m.group(1), m.group(2), l))
    seen_sv = set()
    def chain(b):
        out = [b]
        p = params(b)
        for k in ("Execute", "SubAbility", "Choices", "RepeatSubAbility", "FallbackAbility"):
            for nx in re.split(r"[ ,]+", p.get(k, "")):
                if nx in sv and nx not in seen_sv:
                    seen_sv.add(nx); out += chain(sv[nx])
        return out
    for n_, (kind, body, line) in enumerate(bodies, 1):
        cur[0] = "c%d" % n_
        groups.setdefault(cur[0], [])
        p = params(body)
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
                for ty in re.findall(r"[A-Z][a-z]+", p.get("ValidCard", "")): add("trigger_filter:" + tok(ty))
            elif mode in ("Attacks", "AttackersDeclared", "AttackerBlocked", "AttackerUnblocked"): add("trigger:attacks" if mode in ("Attacks", "AttackersDeclared") else "trigger:" + tok(mode))
            elif mode == "Discarded": add("trigger:discard")
        if kind == "S":
            mode = p.get("Mode", "")
            if mode == "MustAttack":
                add("must_attack")
                for ty in re.findall(r"[A-Z][a-z]+", p.get("ValidCreature", "")):
                    if ty not in ("Creature", "Other", "You", "Ctrl"): add("affects:" + tok(ty))
            if mode in ("CantBlock", "CantBlockBy"): add("cant_block")
            if mode == "ReduceCost":
                vc = p.get("ValidCard", "")
                add("cost_reduce")
                for ty in re.findall(r"[A-Z][a-z]+", vc):
                    if ty in ("Creature", "Artifact", "Enchantment", "Instant", "Sorcery", "Planeswalker", "Land"): add("cost_reduce_for:" + tok(ty)); lk("cost_reduce", "filters", "cardtype:" + tok(ty))
                    elif ty in ("White", "Blue", "Black", "Red", "Green"): add("color:" + tok(ty)); lk("cost_reduce", "filters", "color:" + tok(ty))
        if kind == "R" and p.get("Event") == "Moved" and p.get("Destination") == "Graveyard":
            if "Exile" in sv.get(p.get("ReplaceWith", ""), ""): add("die_replace:exile")
        for b in chain(body):
            bp = params(b)
            api = (re.match(r"^(?:AB|SP|DB)\$ (\w+)", b) or [0, ""])[1]
            if not (kind == "T" and b is body): target_tags(bp, groups[cur[0]], api)   # a trigger line's ValidCard(s) filter describes the event, not a target
            if bp.get("ValidTgts") and bp.get("Origin") in ("Graveyard", "Exile", "Hand", "Library"): add("target_zone:" + bp["Origin"].lower())
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
                if bp.get("Amount", "1") not in ("1",): add("mana_amount:" + bp["Amount"])
                if "RestrictValid" in bp: add("mana_restriction")
                if "IsPresent" in bp or "ConditionPresent" in bp: add("activation_restriction")
            if "IsPresent" in bp and api != "Mana" and kind == "A": add("activation_restriction")
            if api == "ChangeZone" or api == "ChangeZoneAll":
                o, d = bp.get("Origin", ""), bp.get("Destination", "")
                if o == "Library":
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
                if o == "Hand" and d == "Exile": add("impulse_draw_part:exile_hand")
                if d == "Exile" and o in ("Graveyard", "Hand", "Library"): add("exile_from:" + o.lower())
                if "shuffle" in (bp.get("SpellDescription", "") + line).lower(): add("shuffle")
            if api in ("Destroy", "DestroyAll"): add("remove:destroy")
            if api in ("DealDamage", "DamageAll"):
                add("damage")
                if bp.get("NumDmg", "").isdigit(): add("damage_amount:" + bp["NumDmg"])
                if "ReplaceDyingDefined" in bp: add("die_replace:exile")
            if api == "Sacrifice":
                add("effect:sacrifice")
                if bp.get("Defined") in ("Player", "Opponent", "Player.Opponent"):
                    add("remove:sacrifice")
                if "SacValid" in bp: add("sacrifice_type:" + tok(bp["SacValid"].split(".")[0]))
            if bp.get("ConditionDefined") == "Remembered" and api == "Token": lk("token_make", "conditional_on", "effect:sacrifice")
            if api == "ChangeZone" and bp.get("Defined") == "ExiledWith": add("return_exiled"); lk("return_exiled", "pairs_with", "trigger:leaves")
            if api == "Effect":
                for sname in re.split(r"[ ,]+", bp.get("StaticAbilities", "")):
                    if "MayPlay" in sv.get(sname, ""):
                        add("impulse_draw")
                        d = bp.get("Duration", "")
                        add({"UntilTheEndOfYourNextTurn": "duration:next_turn_end", "EndOfTurn": "duration:eot"}.get(d, "duration:eot" if not d else "duration:" + tok(d)))
            if api == "Token": token_tags(bp, groups[cur[0]])
            if api == "CopyPermanent": add("token_make", "token_type:copy")
            if api == "Play" and bp.get("WithoutManaCost") == "True": add("cast_free")
            if api == "ExchangeControl": add("exchange_control", "steal"); lk("exchange_control", "pairs_with", "steal")
            if api == "GainControl":
                add("steal")
                if "AddKWs" in bp: add("steal_grants_" + tok(bp["AddKWs"])); lk("steal", "pairs_with", tok(bp["AddKWs"]))
                if bp.get("LoseControl") == "EOT": add("duration:eot")
            if api == "Animate":
                if bp.get("RemoveAllAbilities") == "True": add("loses_all_abilities")
                add("transform")
                for ty in (bp.get("Types", "")).split(","):
                    if ty: add("becomes:" + tok(ty))
            if api == "PutCounter" or api == "PutCounterAll":
                if bp.get("CounterType"): add("counter:" + tok(bp["CounterType"]))
                if api == "PutCounterAll": add("each_you_control")
            if api == "CopyPermanent" and bp.get("AtEOT") == "Sacrifice": add("delayed:end_step", "effect:sacrifice", "duration:end_step")
            if "KW" in bp and "can't block" in bp["KW"]: add("cant_block")
            if "MayPlay" in b or "MayPlay$" in b: add("impulse_draw")
    out_groups = {}
    for gid, ts in groups.items():
        ts = [t for t in dict.fromkeys(ts) if not t.startswith("impulse_draw_part")]
        if ts: out_groups[gid] = ts
    flat = list(dict.fromkeys(t for ts in out_groups.values() for t in ts))
    return flat, list(dict.fromkeys(links)), out_groups

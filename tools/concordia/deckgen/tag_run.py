#!/usr/bin/env python3
"""Tagging run (design: deckgen/TAG_LINKS.md; user rules human_logic.toon H50-H55).
Sources (H54 rewritten 2026-10-23): the card script only; its Oracle section is a gap filler (tag_verify), not a separate source; mtgish is dropped. Forge AI (AILogic$ etc.) stays a reference input.
Per card: tags (supertype, cardtype, subtype/landtype first, then kw + qualifiers, then ability tags), clauses, links, AI reference.

  python3 tag_run.py starter            tag every card in decks/starter/*.dck -> tags/STARTER_TAGS.toon + STARTER_TAGS_REPORT.md
  python3 tag_run.py card "Name" ...    print records\n  (the starter command also writes tags/NEW_TAGS_FOR_APPROVAL.md and tags/STARTER_TAGS_SAMPLE.md)
"""
import os, re, sys, json, glob, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ability_tags as AT
import tag_extra as TX
import tag_verify as TV
from common import q, snake, params, card_files   # noqa: E402
import derived_tags as DT

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SUPERTYPES = {"Legendary", "Basic", "Snow", "World", "Ongoing"}
CARDTYPES = ["Creature", "Instant", "Sorcery", "Enchantment", "Artifact", "Planeswalker", "Land", "Battle", "Kindred", "Conspiracy", "Dungeon", "Phenomenon", "Plane", "Scheme", "Vanguard"]   # CR 205.2a
BASIC_LAND = {"Plains", "Island", "Swamp", "Mountain", "Forest"}
COLOR = {"W": "white", "U": "blue", "B": "black", "R": "red", "G": "green", "C": "colorless"}   # C = the sixth colour (H78)
COLORWORD = {"white": "white", "blue": "blue", "black": "black", "red": "red", "green": "green"}
KWSET, REMIND = set(), {}
from itertools import takewhile as C_takewhile
KW_MANA_COST = {"squad", "flashback", "kicker", "multikicker", "cycling", "escape", "mutate", "blitz", "emerge", "buyback", "suspend", "madness", "unearth", "disturb", "embalm", "eternalize", "bestow", "evoke", "dash", "prowl", "morph", "megamorph", "reconfigure", "foretell", "overload", "spectacle", "surge", "miracle", "awaken", "entwine", "replicate", "splice", "transmute", "scavenge", "outlast", "monstrosity", "adapt", "prototype", "ninjutsu", "echo", "level_up", "bloodthirst_cost"}   # keywords whose K: line carries a mana cost to keep whole (B0)
try:
    for _l in open(os.path.join(HERE, "..", "ai_lab", "KEYWORD_REFERENCE.toon"), encoding="utf-8"):
        _m = re.match(r'^  "?([^,"]+)"?,(?:keyword|action),', _l)
        if _m:
            for _p in re.split(r" and |/", _m.group(1)): KWSET.add(re.sub(r"[^a-z0-9]", "", _p.lower()))
    import csv as _csv
    for _l in open(os.path.join(HERE, "..", "ai_lab", "KEYWORD_REMINDER_TEXT.toon"), encoding="utf-8"):
        if re.match(r"^  70[12]\.\d+,", _l):
            _f = next(_csv.reader([_l.strip()]))
            REMIND[re.sub(r"[^a-z0-9]", "", _f[1].lower())] = _f[3]
except OSError:
    pass


def provides(base):
    """tags a keyword supplies, read from its reminder text (KEYWORD_REMINDER_TEXT.toon, from the Comprehensive Rules and Oracle lines)"""
    t = REMIND.get(re.sub(r"[^a-z0-9]", "", base.lower()), "")
    out = []
    if re.search(r"[+]N/[+]N counter", t): out.append("counters_plus")
    if re.search(r"create .*token", t, re.I): out.append("token_make")
    if re.search(r"\bdraw", t, re.I): out.append("draw")
    if re.search(r"gain .*life", t, re.I): out.append("lifegain")
    return out


def kw_tags(line):
    """K: line -> base keyword tag plus qualifier tags (user 2026-10-22). Names that are not rules keywords (Forge engine lines such as ETBReplacement)
    become forge_line:<name>. Protection qualifiers are protection_from:<colour|type>; Enchant/Equip target types are target_type:<t>;
    colours, numbers and cost kinds in the cost are color:, num:, cost:."""
    parts = line[2:].split(":")
    base = parts[0].strip()
    rest = ":".join(parts[1:])
    m = re.match(r"^Protection from (.+)$", base, re.I)
    if m:
        tags = ["kw:protection"]
        for w in re.findall(r"\b(white|blue|black|red|green|colorless|everything|[a-z]+s)\b", m.group(1), re.I):
            tags.append("protection_from:" + w.lower().rstrip("s") if w.lower() not in COLORWORD and w.lower() not in ("everything", "colorless") else "protection_from:" + w.lower())
        return list(dict.fromkeys(tags))
    key = snake(base).replace("_", "")
    if KWSET and key not in KWSET:
        if snake(base) == "multikicker" and re.fullmatch(r"(\d+|X)?( ?[WUBRGC])*", rest.strip()) and rest.strip():      # B1: Multikicker:2 / :1 W, one cost, kept whole like the B0 keywords
            return ["forge_line:multikicker", "cost_mana:" + "".join(m.lower() for m in rest.split())]
        return ["forge_line:" + snake(base)]
    tags = ["kw:" + snake(base)]
    if not rest: return tags
    if snake(base) == "protection":
        for w, c in COLORWORD.items():
            if re.search(r"\b%s\b" % w, rest, re.I): tags.append("protection_from:" + c)
        for ty in ("Creature", "Artifact", "Enchantment", "Instant", "Sorcery", "Land", "Planeswalker", "Everything", "Multicolored", "Player"):
            if re.search(r"\b%s\b" % ty, rest): tags.append("protection_from:" + ty.lower())
        for sub in re.findall(r"\.([A-Z][a-z]+)", rest):
            if sub.lower() not in COLORWORD and sub not in ("Chosen", "Color"): tags.append("protection_from:" + sub.lower())
        return list(dict.fromkeys(tags))
    if snake(base) in ("enchant", "equip", "fortify", "attach"):
        for ty in ("Creature", "Artifact", "Enchantment", "Land", "Planeswalker", "Vehicle", "Permanent", "Player", "Equipment", "Aura"):
            if re.search(r"\b%s\b" % ty, rest): tags.append("target_type:" + ty.lower())
    for m2 in re.findall(r"\b(Plains|Island|Swamp|Mountain|Forest)\b", rest): tags.append("landwalk:" + m2.lower())
    cost = re.sub(r"\([^)]*\)", "", rest)
    for t in re.split(r"[ :<>/]+", cost):
        if t.isdigit(): tags.append("num:" + t)
        elif t == "X": tags.append("num:x")
        elif t in COLOR: tags.append("color:" + COLOR[t])
    mana = list(C_takewhile(lambda t: t.isdigit() or t == "X" or t in COLOR, [t for t in re.split(r"[ :<>/]+", cost) if t]))      # B0 (user 2026-10-27): num:/color: lose the pip count ({5}{B}{B} = num:5 color:black), so the keyword's mana cost is also kept whole
    one_cost = sum(1 for seg in cost.split(":") if seg.split() and (seg.split()[0].isdigit() or seg.split()[0] == "X" or seg.split()[0] in COLOR)) <= 1      # Kicker:1 G:2 G has two costs; one cost_mana would be a guess
    if mana and one_cost and snake(base) in KW_MANA_COST: tags.append("cost_mana:" + "".join(m.lower() for m in mana))
    if snake(base) == "suspend" and ":" in rest:      # Suspend:4:1 R = time counters, then the cost; the cost alone is cost_mana
        sm = [t for t in re.split(r"[ ]+", rest.split(":", 1)[1].strip()) if t.isdigit() or t == "X" or t in COLOR]
        if sm: tags.append("cost_mana:" + "".join(m.lower() for m in sm))
    if "PayLife" in rest: tags.append("cost:life")
    if "Sac<" in rest: tags.append("cost:sacrifice")
    if "Discard<" in rest: tags.append("cost:discard")
    return list(dict.fromkeys(tags))


def type_tags(types):
    words = types.split()
    sup = [w for w in words if w in SUPERTYPES]
    ct = [w for w in words if w in CARDTYPES]
    sub = [w for w in words if w not in SUPERTYPES and w not in CARDTYPES]
    out = ["supertype:" + snake(w) for w in sup] + ["cardtype:" + snake(w) for w in ct]
    for w in sub:
        out.append(("landtype:" if (w in BASIC_LAND and "Land" in ct) else "type:") + snake(w))
    return out


TRIG = {"Attacks": "attacks", "AttackerBlocked": "blocked", "SpellCast": "spell_cast", "Phase": "phase", "TurnFaceUp": "flip-up", "Taps": "taps",
        "TapsForMana": "taps_for_mana", "Drawn": "draws", "LifeGained": "gain_life", "Sacrificed": "sacrificed", "Discarded": "discarded"}


def trigger_of(body):
    m = re.search(r"Mode\$ (\w+)", body)
    mode = m.group(1) if m else ""
    if mode == "ChangesZone":
        o = (re.search(r"Origin\$ (\w+)", body) or [0, "Any"])[1]; d = (re.search(r"Destination\$ (\w+)", body) or [0, ""])[1]
        who = "self" if "Card.Self" in body else "other"
        if d == "Battlefield": return "etb_" + who
        if o == "Battlefield" and d == "Graveyard": return "dies_" + who
        if o == "Battlefield": return "leaves_" + who
        return "zone_%s_%s" % (o.lower(), d.lower())
    if mode == "DamageDone": return "combat_damage" if "CombatDamage$ True" in body else "damage"
    return TRIG.get(mode, snake(mode))


def clause_from(sv, first, kind, cid, line):
    """one clause: trigger, cost, verb, payload, affected, duration. sv = SVar dict."""
    p = params(first)
    trig = cost = ""
    if kind == "T": trig = trigger_of(first)
    elif kind == "S": trig = "static"
    elif kind == "R": trig = "replacement"
    elif kind == "A": trig = "activated" if "Cost$" in first and not first.startswith("SP$") else "spell"
    cost = p.get("Cost", "")
    chain = []
    cur = first
    seen = 0
    if kind == "T" and p.get("Execute") in sv: cur = sv[p["Execute"]]
    while cur and seen < 6:
        chain.append(cur); seen += 1
        nx = params(cur).get("SubAbility")
        cur = sv.get(nx) if nx in sv else None
    if kind in ("S", "R"): chain = [first]
    verbs, payload, affected, dur = [], [], [], ""
    for c in chain:
        cp = params(c)
        api = (re.match(r"^(?:AB|SP|DB)\$ (\w+)", c) or [0, ""])[1] if re.match(r"^(AB|SP|DB)\$", c) else ""
        if kind == "S": api = "static_" + snake(cp.get("Mode", ""))
        verbs.append(api.lower() if api else snake(cp.get("Mode", "")) or "?")
        for k in ("KW", "Keywords", "AddKeyword", "AddAbility"):
            if k in cp: payload += [snake(x) for x in re.split(r"\s*[&,]\s*", cp[k])]
        for k in ("NumAtt", "NumDef", "AddPower", "AddToughness", "NumDmg", "LifeAmount", "NumCards", "TokenScript", "CounterType"):
            if k in cp: payload.append("%s=%s" % (k.lower(), cp[k]))
        for k in ("ValidTgts", "Defined", "Affected", "AffectedDefined", "ValidCard"):
            if k in cp: affected.append("%s=%s" % (k, cp[k]))
        if "Duration" in cp: dur = cp["Duration"]
    if not dur:
        if kind == "S" and "Continuous" in first: dur = "static"
        elif any(v in ("pump", "pumpall") for v in verbs): dur = "eot(forge_default)"
    dur = {"EndOfTurn": "eot", "static": "static", "Permanent": "permanent", "Perpetual": "perpetual", "UntilHostLeavesPlay": "until_leaves"}.get(dur, dur)
    return dict(id=cid, trigger=trig, cost=cost, verb="+".join(verbs), payload=" ".join(payload), affected=" ".join(affected), duration=("duration:" + dur) if dur else "")


NICHE_TYPES = {"artifact", "enchantment", "planeswalker", "battle", "land", "aura", "equipment", "vehicle", "saga"}
NOT_TRIBE = {"green", "white", "blue", "black", "red", "colorless", "multicolor", "artifact", "enchantment", "chosentype", "strictlyother", "creature"}   # lord:<x> that is not a creature type


def record(name, text):
    face = text.split("\nALTERNATE")[0]
    if "AlternateMode:Prepare" in face and "\nALTERNATE" in text:   # spell half of a prepare card: its ability lines and SVars are read with the creature half (types, Oracle and the rest of the second face are not)
        alt = text.split("\nALTERNATE", 1)[1]
        cf = re.search(r"^CopyFaceFrom:(.+)$", alt, re.M)   # the spell half is another card's face (Blazing Firesinger = Seething Song)
        if cf and find_text(cf.group(1).strip()): alt = find_text(cf.group(1).strip()).split("\nALTERNATE")[0]
        face += "\n" + "\n".join(l for l in alt.split("\n") if re.match(r"^(A|S|T|R|SVar):", l))
    lines = face.split("\n")
    sv = {}
    for l in lines:
        m = re.match(r"^SVar:(\w+):(.*)$", l)
        if m: sv[m.group(1)] = m.group(2)
    for l in list(lines):   # K:Haunt:<SVar> keeps its effect in the SVar (enters / haunted creature dies): read it as an ability line of its own
        m = re.match(r"^K:Haunt:(\w+)", l)
        if m and m.group(1) in sv and re.match(r"^(DB|AB|SP)\$", sv[m.group(1)]): lines.append("A:" + sv[m.group(1)])
    types = next((l[6:] for l in lines if l.startswith("Types:")), "")
    tags = type_tags(types)
    mc = next((l[9:] for l in lines if l.startswith("ManaCost:")), "")
    if mc and "Land" not in types.split() and not re.search(r"[WUBRG]", mc) and not any(l.startswith("Colors:") for l in lines) or any(l.strip() == "K:Devoid" for l in lines):
        tags.append("colorless_card")      # a colorless spell: needs colorless-capable mana in the deck (H78; user 2026-10-26)
    kgroups = {}
    for l in lines:
        if l.startswith("K:"):
            kt = kw_tags(l)
            kgroups["k%d" % (len(kgroups) + 1)] = kt
            tags += kt
    base = sorted(t for t in AT.tags_of(text) if not t.startswith(("has:", "needs:", "hint:")))
    ex_tags, ex_links, ex_groups = TX.extra(lines, sv, types, text)
    if any(t.startswith("choose_on_enter:") or t == "enters_prepared" for t in ex_tags):   # the opaque forge_line:etbreplacement is replaced by the readable choose_on_enter tag
        tags = [t for t in tags if t != "forge_line:etbreplacement"]
        kgroups = {g: [t for t in ts if t != "forge_line:etbreplacement"] for g, ts in kgroups.items()}
    clauses, links = [], list(ex_links)
    n = 0
    for l in lines:
        m = re.match(r"^(A|S|T|R):(.*)$", l)
        if not m: continue
        n += 1
        cl = clause_from(sv, m.group(2), m.group(1), "c%d" % n, l)
        cl["secondary"] = "Secondary$ True" in l
        cl["kind"] = m.group(1)
        if cl["verb"] == "?" and m.group(1) == "R": cl["verb"] = "replace_" + snake(params(m.group(2)).get("Event", ""))
        clauses.append(cl)
        if cl["trigger"] == "flip-up":
            mk = next((k for k, v in kgroups.items() if "kw:morph" in v), "kw:morph")
            links.append(("c%d:flip-up" % n, "requires", mk)); tags.append("flip-up"); ex_groups.setdefault("c%d" % n, []).append("flip-up")
        if cl["payload"] and cl["duration"]:
            links.append(("c%d:payload" % n, "lasts", "c%d:duration" % n))
            if cl["duration"].startswith("duration:eot"): tags.append("duration:eot"); ex_groups.setdefault(cl["id"], []).append("duration:eot")
        if cl["payload"] and cl["affected"]: links.append(("c%d:affected" % n, "receives", "c%d:payload" % n))
    for l in lines:
        if l.startswith("K:"):
            b = l[2:].split(":")[0].strip()
            kid = next((k for k, v in kgroups.items() if v and v[0] == "kw:" + snake(b)), "kw:" + snake(b))
            for pv in provides(b):
                tags.append(pv); links.append((kid, "provides", pv))
    for cl in clauses:
        for pl in cl["payload"].split():
            if "=" not in pl and snake(pl) in KWSET.union({"first_strike", "double_strike", "lifelink", "deathtouch", "flying", "trample", "haste", "vigilance", "menace", "reach", "hexproof", "indestructible"}): tags.append(snake(pl)); ex_groups.setdefault(cl["id"], []).append(snake(pl))
            if pl == "lifelink": tags.append("lifegain"); ex_groups.setdefault(cl["id"], []).append("lifegain")
        if "counters_" in cl["affected"]: tags.append("scales:counters"); ex_groups.setdefault(cl["id"], []).append("scales:counters")
        if cl["verb"] in ("pump", "pumpall") and cl["payload"] and "ValidTgts" in cl["affected"]: tags.append("pump_single"); ex_groups.setdefault(cl["id"], []).append("pump_single")
    # sacrifice outlet (user): a land sacrificed is not an outlet; a creature (or other non-land) sacrificed always is
    sact = {t.split(":", 1)[1] for t in ex_tags if t.startswith(("cost_sacrifice_target:", "sacrifice_type:"))}
    sact = {("land" if x in {b.lower() for b in BASIC_LAND} else x) for x in sact}   # a Mountain is a land
    if "self" in sact and "Land" in types.split(): sact.discard("self"); sact.add("land")
    if sact and not (sact - {"land", "self"}):   # only lands or the card itself sacrificed (user 2026-10-22): not an outlet, whichever source tagged it
        base = [t for t in base if t != "sacrifice_outlet"]; ex_tags = [t for t in ex_tags if t != "sacrifice_outlet"]
        tags = [t for t in tags if t != "sacrifice_outlet"]
        ex_groups = {g: [t for t in ts if t != "sacrifice_outlet"] for g, ts in ex_groups.items()}
    elif sact - {"land", "self"}: ex_tags = ex_tags + ["sacrifice_outlet"]; ex_groups.setdefault("c0", []).append("sacrifice_outlet")
    tags = list(dict.fromkeys(tags + base + ex_tags))
    # keyword listed once: drop the plain tag when kw:<name> is present (user: trample listed twice)
    tags = [t for t in tags if not ("kw:" + t) in tags]
    # removal split by method (user): drop the umbrella 'removal' when a method tag exists
    if "removal" in tags and any(t.startswith("remove:") or t == "damage" for t in tags): tags.remove("removal")
    # bare keyword tags on granting cards (trample on Rancor ...) are dropped (user 2026-10-22): grant_kw:<kw> already says it
    tags = [t for t in tags if t not in TV.BARE_KEYWORDS]
    # three one-card bare tags dropped (user 2026-10-26): infect and grant_double_strike repeat grant_kw:*, equip repeats token_make / kw:equip
    tags = [t for t in tags if t not in ("infect", "grant_double_strike", "equip")]
    # umbrella tags (haste_grant, land_tutor, recursion ...) stay intact: they belong to the AI Tags category (tag_verify.is_ai_tag), not to the rules tags
    if "restrict" in tags and not any(x.startswith("restrict_kind:") for x in tags) and any(x.startswith("cant_be_blocked") for x in tags):
        tags = [x for x in tags if x != "restrict"]   # 'can't be blocked (by X)' is evasion, not a restriction on someone else
    if "duration:next_untap" in tags or "duration:while_control" in tags: tags = [t for t in tags if t != "duration:permanent"]   # Forge's Duration$ Permanent on a 'next untap step' / 'as long as you control' effect is a script detail
    tags = list(dict.fromkeys(t.lower() for t in tags))   # all tags lower case (scales:Goblin -> scales:goblin)
    ver = TV.verify(tags, text, KWSET, REMIND)
    tags = list(dict.fromkeys(tags + ver["add"]))
    if ver["add"]: ex_groups["v"] = list(ver["add"])
    ex_tags = ex_tags + ver["add"]
    if os.environ.get("TAG_VARIANT") != "off":   # agent suggestions S01-S09, S15 (tag_variant.py), deployed on the user's order 2026-10-22; TAG_VARIANT=off for the old tags
        import tag_variant as TVAR
        tags, ex_groups = TVAR.apply(name, face, lines, sv, tags, ex_groups)
    # cost:mana is dropped when cost_mana:<symbols> says it (user 2026-10-23), in the tags and in every group
    if any(t.startswith("cost_mana:") for t in tags):
        tags = [t for t in tags if t != "cost:mana"]; ex_tags = [t for t in ex_tags if t != "cost:mana"]; base = [t for t in base if t != "cost:mana"]
        ex_groups = {g: [t for t in ts if t != "cost:mana"] for g, ts in ex_groups.items()}; kgroups = {g: [t for t in ts if t != "cost:mana"] for g, ts in kgroups.items()}
    # niche:<archetype> = the effect only pays in a deck built around that archetype (user 2026-10-25); the card keeps its tags, consumers weigh them down
    if "Land" in types.split() and "land_tutor" in tags and "cost_sacrifice_target:self" in tags and not re.search(r"ChangeType\$ ?(?:Land|Card)\.Basic", face): tags.append("niche:lands")   # fetchland that names land types (Polluted Delta): sacrifice outlet / land-recursion decks; a basic-land fetch (Evolving Wilds, Fabled Passage) fixes mana in any deck
    for nt, arch in (("grave_hate", "graveyard_hate"), ("self_mill", "self_mill"), ("haunt", "haunt")):
        if nt in tags: tags.append("niche:" + arch)
    if any(t in ("flip_coin", "roll_die") or t.startswith(("roll_die:", "secret_choice:")) for t in tags): tags.append("niche:chaos")   # coin, die and secret-choice cards pay only in chaos decks (user 2026-10-27)
    tset, ttypes = set(tags), types.split()
    if any(t.startswith("lord:") and t[5:] not in NOT_TRIBE for t in tset): tags.append("niche:tribal")   # lord of one creature type (user 2026-10-25: all suggested)
    if "condition:landfall" in tset or any(t.startswith(("x_is:landfall", "token_type:bird_landfall")) for t in tset) or re.search(r"TriggerDescription\$[^|\n]*\bLandfall\b|^Oracle:.*\bLandfall\b\s*[\u2014-]", face, re.M): tags.append("niche:landfall")
    tt = {t.split(":", 1)[1] for t in tset if t.startswith(("target_type:", "affected_type:"))}   # niche by target type (user 2026-10-25): every targeted/affected type is a non-creature, non-spell card type; mixed cards (Austere Command) and noncreature/nonland filters stay general
    tt_niche = {x for t in tt for x in t.split("_") if x in NICHE_TYPES}
    if tt_niche and all(set(t.split("_")) <= NICHE_TYPES for t in tt) and not any(t.startswith(("target_filter:non", "affected_filter:non")) for t in tset):
        tags += ["niche:" + x for x in sorted(tt_niche)]
    if any(t in tset for t in ("kw:storm", "kw:gravestorm", "grant_kw:storm", "storm")): tags.append("niche:storm")
    ora = " ".join(re.findall(r"^Oracle:(.*)$", face, re.M))
    for mt, rx in MECH_RX:   # mech:<mechanic> = the card needs a rule or component many decks and the AI handle poorly; build.py MECH_MIN_TIER gates it by tier (user 2026-10-25, replaces build.SKIP_TEXT)
        if re.search(rx, ora, re.I): tags.append("mech:" + mt)
    ex_tags = ex_tags + [t for t in tags if t.startswith(("niche:", "mech:"))]   # niche tags count as new in "new", like the other cross-check additions
    ai = sorted(set(re.findall(r"AILogic\$ ?([A-Za-z0-9_]+)", face)) | set(re.findall(r"^SVar:AttachAILogic:(\w+)", face, re.M)))
    aipref = "AIPreference" in face or "SVar:AIPreference" in face
    rd = "AI:RemoveDeck" in face
    ex_groups = relocate_v(ex_groups)
    groups = dict(kgroups)
    for gid, ts in ex_groups.items(): groups[gid] = [t.lower() for t in dict.fromkeys(ts)]
    def gkey(g): return (0 if g == "c0" else 1 if g.startswith("k") else 3 if g == "v" else 2, [int(x) for x in re.findall(r"\d+", g)])
    groups = dict(sorted(groups.items(), key=lambda kv: gkey(kv[0])))
    ai_tags = [x for x in tags if TV.is_ai_tag(x)]
    links = [l for l in links if not any(e.partition(":")[0] in ("c%d" % i for i in range(1, 30)) and not any(g == e.partition(":")[0] or g.startswith(e.partition(":")[0] + ".") for g in groups) for e in (l[0], l[2]))]      # drop links to a clause that has no tags and so no group
    links = list(links) + DT.provided_by(set(tags), set(base))
    return dict(name=name, face=DT.face(text, name), derived=DT.derived(tags, groups, base), ai_tags=ai_tags, groups=groups, base=[t.lower() for t in base], new=[t.lower() for t in ex_tags if t.lower() in tags], tags=tags, clauses=clauses, links=links, verify=ver, ai=ai, aipref=aipref, removedeck=rd, nlines=n)


_EP = {}
def _effect_params():
    if not _EP:
        try: _EP.update(json.load(open(os.path.join(HERE, "tagcheck", "effect_params.json"), encoding="utf8")))
        except OSError: pass
    return _EP


def relocate_v(ex_groups):
    """TAG_SYNTAX decision 4 (user 2026-10-27): a verb tag the cross-check group v added (Nazar: life_loss) moves to the one step group that holds its parameters (life_loss_amount:3);
    ambiguous or parameterless verbs stay in v"""
    ep = _effect_params()
    if "v" not in ex_groups or not ep: return ex_groups
    keep = []
    for t in ex_groups["v"]:
        f = t.split(":")[0]
        homes = [g for g, ts in ex_groups.items() if g not in ("v", "c0") and any(ep.get(u.split(":")[0], {}).get("verb") == f for u in ts)]
        if len(homes) == 1: ex_groups[homes[0]].append(t)
        else: keep.append(t)
    if keep: ex_groups["v"] = keep
    else: del ex_groups["v"]
    return ex_groups


VERB_WORDS = {"tutor": r"\bsearch", "shuffle": r"\bshuffle", "put_onto_battlefield": r"onto the battlefield", "return": r"\breturn", "draw": r"\bdraws?\b", "life_loss": r"\blo(?:se|ses)\b",
              "lifegain": r"\bgains?\b", "damage": r"\bdeals?\b", "token_make": r"\bcreate", "remove": r"\b(?:exile|destroy|sacrifice)", "counter": r"\bcounters?\b", "discard": r"\bdiscard",
              "scry": r"\bscry", "mill": r"\bmill", "mana_source": r"\badd\b", "pump_single": r"\bgets?\b", "fight": r"\bfights?\b", "untap": r"\buntap", "investigate": r"\binvestigate",
              "surveil": r"\bsurveil", "impulse_draw": r"\bexile the top", "look_top": r"\blook at the top|\breveal the top"}


def verb_order(text, groups):
    """Oracle phrase position of each verb of each group (TAG_SYNTAX decision 2): {gid: [verb, ...]} in the order the verbs appear in the Oracle text; verbs with no match keep tag order at the end"""
    ep = _effect_params()
    ora = " ".join(re.findall(r"^Oracle:(.*)$", text, re.M)).lower()
    out = {}
    for g, ts in groups.items():
        vs = []
        for t in ts:
            f = t.split(":")[0]
            v = f if f in VERB_WORDS or f in ("kw", "remove") else ep.get(f, {}).get("verb")
            if isinstance(v, str) and v not in vs and f not in ("kw",): vs.append(v)
        if len(vs) > 1:
            def pos(v):
                m = re.search(VERB_WORDS.get(v, r"$^"), ora)
                return m.start() if m else 10 ** 6
            out[g] = sorted(vs, key=pos)      # stable: ties and misses keep tag order
    return out


def render(r):
    TYPING = ("supertype:", "cardtype:", "type:", "landtype:")      # the card's own typing, kept apart from the tags of its abilities (user 2026-10-22)
    o = ["card: " + q(r["name"]), "typing: " + " ".join(x for x in r["tags"] if x.startswith(TYPING)),
         "tags: " + " ".join(x for x in r["tags"] if not TV.is_ai_tag(x) and not x.startswith(TYPING))]
    if r["ai_tags"]: o.append("ai_tags: " + " ".join(r["ai_tags"]))
    o.append("face: " + r["face"])
    if r["derived"]: o.append("derived: " + " ".join(r["derived"]))
    o.append("clauses[%d]{id,trigger,cost,verb,payload,affected,duration}:" % len(r["clauses"]))
    for c in r["clauses"]: o.append("  " + ",".join(q(c[k]) for k in ("id", "trigger", "cost", "verb", "payload", "affected", "duration")))
    if r["links"]:
        o.append("links[%d]{from,rel,to}:" % len(r["links"]))
        for a, b, c in r["links"]: o.append("  %s,%s,%s" % (a, b, c))
    o.append("groups[%d]{id,source,tags}:" % len([1 for g, ts in r["groups"].items() if [x for x in ts if not TV.is_ai_tag(x)]]))
    for gid, ts in r["groups"].items():
        src = "saga chapter %s" % gid[1:] if re.match(r"^s\d+$", gid) else "cross-check (oracle gap filler/keyword/ai)" if gid == "v" else "card" if gid == "c0" else ("K line" if gid.startswith("k") else ("sub-ability of " + gid.split(".")[0] if "." in gid else "%s line" % next((c.get("kind", "?") for c in r["clauses"] if c["id"] == gid), "?")))
        ts = [x for x in ts if not TV.is_ai_tag(x)]
        if ts: o.append("  %s,%s,%s" % (gid, src, q(" ".join(ts))))
    if r["verify"]["flags"]: o.append("verify_flags: " + " | ".join(r["verify"]["flags"]))
    o.append("forge_ai: AILogic=%s%s%s" % ("/".join(r["ai"]) or "-", " AIPreference" if r["aipref"] else "", " RemoveDeck" if r["removedeck"] else ""))
    return "\n".join(o)


_IDX = {}


def find_text(name):
    """script text by card name; falls back to an index of every Name: line because multi-face scripts are filed as front_back.txt (e.g. gumdrop_poisoner_tempt_with_treats.txt)"""
    t = AT.card_text(name)
    if t: return t
    if not _IDX:
        for p in card_files(ROOT):
            try:
                with open(p, errors="replace") as fh: x = fh.read()
            except OSError: continue
            m = re.search(r"^Name:(.*)$", x, re.M)
            if m: _IDX.setdefault(m.group(1).strip().lower(), p)
            for m2 in re.finditer(r"^Name:(.*)$", x, re.M): _IDX.setdefault(m2.group(1).strip().lower(), p)
    p = _IDX.get(name.lower())
    if not p: return ""
    with open(p, errors="replace") as fh: return fh.read()


MECH_RX = (("sticker", r"\bsticker"), ("attraction", r"\battractions?\b|\bvisit\b"), ("contraption", r"contraption"), ("vote", r"\bvote\b|council's dilemma"),
           ("ante", r"\bante\b"), ("initiative", r"initiative"), ("day_night", r"day and night|becomes (?:day|night)"), ("ring", r"ring tempts"),
           ("monarch", r"the monarch"), ("venture", r"venture into"), ("speed", r"\bspeed\b|start your engines"), ("planechase", r"planechase|planeswalk(?:s|ed)? to"),
           ("scheme", r"\bscheme\b"), ("graveyard_cast", r"you may cast .* from your graveyard"))


def tags(name):
    """the single flat tag set of a card: record()['tags'] including the typing tags and niche:* tags, the one source every consumer should read (empty set when the script is missing)"""
    text = find_text(name)
    return set(record(name, text)["tags"]) if text else set()


def deck_cards(path):
    names = collections.Counter()
    for l in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"^(\d+) ([^|]+)\|", l)
        if m: names[m.group(2).strip()] += int(m.group(1))
    return names


def main(a):
    if a and a[0] == "card":
        for n in a[1:]:
            print(render(record(n, find_text(n))), end="\n\n")
            try:
                import tag_twins
                tag_twins.main(["card", n])   # similar already-tagged ability lines, for reference
            except Exception as ex:
                print("(no twins:", ex, ")")
        return
    import importlib   # by name: the starter run lives in tag_reports, which imports the guards, which import this module (no import cycle)
    importlib.import_module("tag_reports").starter_main(a)


if __name__ == "__main__":
    main(sys.argv[1:])

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
import derived_tags as DT

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SUPERTYPES = {"Legendary", "Basic", "Snow", "World", "Ongoing"}
CARDTYPES = ["Creature", "Instant", "Sorcery", "Enchantment", "Artifact", "Planeswalker", "Land", "Battle", "Kindred", "Conspiracy", "Dungeon", "Phenomenon", "Plane", "Scheme", "Vanguard"]   # CR 205.2a
BASIC_LAND = {"Plains", "Island", "Swamp", "Mountain", "Forest"}
COLOR = {"W": "white", "U": "blue", "B": "black", "R": "red", "G": "green"}
COLORWORD = {"white": "white", "blue": "blue", "black": "black", "red": "red", "green": "green"}
KW_ACTIVE = re.compile(r"^(A|S|T|R):")
KWSET, REMIND = set(), {}
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


def q(x):
    x = str(x)
    return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"' if x == "" or re.search(r'[,"\\]', x) else x


def snake(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


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


def params(body):
    d = {}
    for item in body.split(" | "):
        m = re.match(r"^(\w+)\$ ?(.*)$", item)
        if m: d[m.group(1)] = m.group(2)
    return d


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


def record(name, text):
    face = text.split("\nALTERNATE")[0]
    lines = face.split("\n")
    sv = {}
    for l in lines:
        m = re.match(r"^SVar:(\w+):(.*)$", l)
        if m: sv[m.group(1)] = m.group(2)
    types = next((l[6:] for l in lines if l.startswith("Types:")), "")
    tags = type_tags(types)
    kgroups = {}
    for l in lines:
        if l.startswith("K:"):
            kt = kw_tags(l)
            kgroups["k%d" % (len(kgroups) + 1)] = kt
            tags += kt
    base = sorted(t for t in AT.tags_of(text) if not t.startswith(("has:", "needs:", "hint:")))
    ex_tags, ex_links, ex_groups = TX.extra(lines, sv, types, text)
    if any(t.startswith("choose_on_enter:") for t in ex_tags):   # the opaque forge_line:etbreplacement is replaced by the readable choose_on_enter tag
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
    ai = sorted(set(re.findall(r"AILogic\$ ?([A-Za-z0-9_]+)", face)) | set(re.findall(r"^SVar:AttachAILogic:(\w+)", face, re.M)))
    aipref = "AIPreference" in face or "SVar:AIPreference" in face
    rd = "AI:RemoveDeck" in face
    groups = dict(kgroups)
    for gid, ts in ex_groups.items(): groups[gid] = [t.lower() for t in dict.fromkeys(ts)]
    def gkey(g): return (0 if g == "c0" else 1 if g.startswith("k") else 3 if g == "v" else 2, [int(x) for x in re.findall(r"\d+", g)])
    groups = dict(sorted(groups.items(), key=lambda kv: gkey(kv[0])))
    ai_tags = [x for x in tags if TV.is_ai_tag(x)]
    links = list(links) + DT.provided_by(set(tags), set(base))
    return dict(name=name, face=DT.face(text, name), derived=DT.derived(tags, groups, base), ai_tags=ai_tags, groups=groups, base=[t.lower() for t in base], new=[t.lower() for t in ex_tags if t.lower() in tags], tags=tags, clauses=clauses, links=links, verify=ver, ai=ai, aipref=aipref, removedeck=rd, nlines=n)


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
        for p in glob.glob(os.path.join(ROOT, "forge-gui/res/cardsfolder/*/*.txt")):
            try:
                with open(p, errors="replace") as fh: x = fh.read()
            except OSError: continue
            m = re.search(r"^Name:(.*)$", x, re.M)
            if m: _IDX.setdefault(m.group(1).strip().lower(), p)
            for m2 in re.finditer(r"^Name:(.*)$", x, re.M): _IDX.setdefault(m2.group(1).strip().lower(), p)
    p = _IDX.get(name.lower())
    if not p: return ""
    with open(p, errors="replace") as fh: return fh.read()


PREV_SAMPLE = {"Vodalian Arcanist", "Goblin Rabblemaster", "Colossal Dreadmaw", "Filter Out", "Scorching Dragonfire", "Harrow", "Victimize", "Search for Tomorrow",
               "Captain's Call", "Rancor", "Pacifism", "Oblivion Ring", "Memnarch, the Warden", "Arcane Signet", "Bontu's Monument", "Oko, Thief of Crowns",
               "Rowan, Fearless Sparkmage", "Garruk, Veiled Butcher", "Temple of the False God", "Blighted Woodland", "Myriad Landscape", "Invasion of Kaldheim",
               "Invasion of New Phyrexia", "Invasion of Moag", "Kiki-Jiki, Mirror Breaker", "Plains", "Frost Marsh"}   # cards already shown in the first sample (user feedback exists)
SAMPLE_TYPES = ["cardtype:creature", "cardtype:instant", "cardtype:sorcery", "cardtype:enchantment", "cardtype:artifact", "cardtype:planeswalker", "cardtype:land", "cardtype:battle", "cardtype:kindred"]
SAMPLE_SUPER = ["supertype:legendary", "supertype:basic", "supertype:snow", "supertype:world"]


def richness(r):
    fams = {t.split(":")[0] for t in r["tags"] if not t.startswith(("cardtype", "supertype", "type", "landtype", "color", "num"))}
    return (len(fams), len(r["tags"]))


def pick(recs, tag, n):
    """n cards with the tag, not in the first sample: the richest, the middle one, and one the cross-check added to or flagged (else the next richest)"""
    pool = sorted((r for r in recs if tag in r["tags"] and r["name"] not in PREV_SAMPLE), key=richness, reverse=True)
    if len(pool) <= n: return pool
    out = [pool[0], pool[len(pool) // 2]]
    third = next((r for r in pool if (r["verify"]["add"] or r["verify"]["flags"]) and r not in out), None) or next(r for r in pool if r not in out)
    return (out + [third])[:n]


def pool_pick(tag, n):
    word = tag.split(":")[1].capitalize()
    cands = []
    for p in sorted(glob.glob(os.path.join(ROOT, "forge-gui/res/cardsfolder/*/*.txt"))):
        try: x = open(p, errors="replace").read()
        except OSError: continue
        if re.search(r"^Types:.*\b%s\b" % word, x.split("\nALTERNATE")[0], re.M):
            nm = re.search(r"^Name:(.*)$", x, re.M).group(1).strip()
            if nm not in PREV_SAMPLE: cands.append(nm)
    recs = [record(nm, find_text(nm)) for nm in cands[:60]]
    return pick(recs, tag, n)


def sample_row(r, text, starter_names):
    text = text or find_text(r["name"].replace(" (not in starter decks)", ""))
    oracle = next((l[7:] for l in text.split("\n") if l.startswith("Oracle:")), "").replace("\\n", " / ").replace("|", "/")
    grp = "<br>".join("%s: %s" % (k, " ".join(x for x in v if not TV.is_ai_tag(x))) for k, v in r["groups"].items() if [x for x in v if not TV.is_ai_tag(x)])
    v = r["verify"]
    chk = "<br>".join(["added: " + " ".join("%s [%s]" % (t, "+".join(v["sources"][t])) for t in v["add"] if not t.startswith("ai_logic"))] * bool([t for t in v["add"] if not t.startswith("ai_logic")]) + ["flag: " + f for f in v["flags"]] + ["AI: " + "/".join(v["ai"])] * bool(v["ai"]))
    return "| %s | %s | %s | %s | %s | %s | |" % (r["name"], oracle, " ".join(x for x in r["tags"] if not TV.is_ai_tag(x)), " ".join(r["ai_tags"]) or "-", grp, chk or "agrees")


def write_sample(recs):
    """sample report: Oracle text, tags, linked groups and cross-check result per card, with an empty note field for the user"""
    texts = {r["name"]: find_text(r["name"]) for r in recs}   # texts of pool cards are added below
    out = ["# Sample tag run: starter-deck cards (3 per card type, 1 per supertype)\n",
           "Generated by `deckgen/tag_run.py starter` (revised in place each run). Sources: card script (its Oracle section is the gap filler), keyword reference and the smaller CR files, Forge AI `AILogic$` (reference). Cards are chosen from the starter decks and exclude the 27 cards of the first sample (you gave feedback on those: `TAG_FEEDBACK_STARTER_SAMPLE.md`). For each type: the card with the most ability families, a middle one, and one the cross-check changed or flagged.\n",
           "**How to read:** *Oracle text* is the printed text (`/` = line break). *Tags* run supertype, cardtype, subtype/landtype, keyword and qualifiers, ability tags. *Linked groups*: tags of one script line (k = K: line, c = A/S/T/R line and its sub-steps, c0 = card level, v = added by the cross-check). *Cross-check*: `added` = tags the Oracle gap filler supported and the script tags lacked (triggers, costs, keywords), with their sources; `flag` = the Oracle line and the script tags disagree (not added, needs your word); `AI` = AILogic value. *Your note*: type your feedback in the last column (right / missing / extra tag, and what).\n"]
    for sec in SAMPLE_TYPES + SAMPLE_SUPER:
        k = 3 if sec.startswith("cardtype") else 1
        cards = pick(recs, sec, k)
        out += ["\n## %s\n" % sec]
        if not cards:
            cards = pool_pick(sec, k)
            for r in cards: texts[r["name"]] = find_text(r["name"])
            out.append("No such card in the starter decks (%d starter cards): %d taken from the whole card pool, marked (not in starter decks).\n" % (len(recs), len(cards)))
            for r in cards: r["name"] += " (not in starter decks)"
        out += ["| Card | Oracle text | Tags | AI tags | Linked groups | Cross-check | Your note |", "|---|---|---|---|---|---|---|"]
        out += [sample_row(r, texts.get(r["name"].replace(" (not in starter decks)", ""), ""), None) for r in cards]
    open(os.path.join(HERE, "tags", "STARTER_TAGS_SAMPLE.md"), "w").write("\n".join(out) + "\n")


# tag families the user approved in chat on 2026-10-22: the first 58 ("Approve all new tags") and the rest later the same day ("approve all tags", after the redundancy prune); a family created later stays proposed until approved
APPROVED = ['activation_restriction', 'affects', 'cast_free', 'color', 'cost', 'cost_if_you_do', 'cost_reduce_for', 'cost_sacrifice_target', 'counter', 'damage', 'damage_amount', 'delayed', 'die_replace', 'discard_count', 'draw_count', 'duration', 'effect', 'enters_tapped', 'enters_untapped', 'exile_from', 'impulse_draw', 'impulse_draw_count', 'loses_all_abilities', 'mana', 'mana_amount', 'mana_choice', 'mana_restriction', 'must_attack', 'put_from', 'put_onto_battlefield', 'put_tapped', 'recursion', 'remove', 'return_exiled', 'sacrifice_type', 'shuffle', 'steal', 'steal_grants_haste', 'target_count', 'target_filter', 'target_scope', 'target_type', 'target_zone', 'tempo', 'token_cardtype', 'token_color', 'token_count', 'token_kw', 'token_pt', 'token_type', 'transform', 'trigger', 'trigger_filter', 'trigger_scope', 'trigger_zone', 'tutor_count', 'tutor_dest', 'tutor_target', 'affected_filter', 'affected_scope', 'affected_type', 'ai_logic', 'cant_be_blocked', 'cant_be_countered', 'condition', 'cost_exile_target', 'cost_return_target', 'counter_count', 'fight', 'grant_ability', 'grant_kw', 'life_loss', 'life_loss_amount', 'lifegain_amount', 'look_top', 'modal', 'piles_split', 'pump_amount', 'replace', 'rest_to_zone', 'rest_order', 'from_zone', 'to_zone', 'restrict_kind', 'reveal', 'saga_chapter', 'scry_count', 'surveil', 'take', 'token_ability', 'untap', 'x_is', 'optional', 'unless_cost', 'limit', 'regenerate', 'cant_regenerate', 'prevent_damage', 'choose_on_enter', 'choice_option', 'cost_reduce_amount', 'cost_reduce_mana', 'cost_reduce_for', 'mana_conditional', 'mana_amount_if', 'extra_land_drop', 'phase_out', 'cost_additional', 'controller']   


PROPOSED_OFFLINE = ["named"]
APPROVED_LATER = ['cost_mana', 'return', 'unless_cost_amount', 'investigate', 'monarch', 'bolster']   # approved by the user in chat on 2026-10-23


def write_reference(recs):
    """tags/TAG_REFERENCE.md: every tag family in the run with meaning, source/reference, values and counts, for the user's review (generated, do not edit by hand)"""
    doc = {}
    for k, (m, w) in list(TX.DOC.items()) + list(TV.DOC.items()):
        for part in re.split(r" / | \+ ", k):
            doc[part.split(":")[0].split(" ")[0]] = (m, w)
    fam = collections.OrderedDict()
    for r in recs:
        for t in r["tags"]:
            f = t.split(":")[0]
            fam.setdefault(f, collections.OrderedDict()).setdefault(t, set()).add(r["name"])
    TYPING = {"supertype", "cardtype", "type", "landtype"}
    def cat(f, vals):
        if f in TYPING: return "1 Typing line (what the card is)"
        if any(TV.is_ai_tag(t) for t in vals): return "9 AI Tags (hidden from the blind reader)"
        if f in ("kw", "forge_line", "protection_from", "landwalk"): return "2 Keywords and engine lines"
        if f in ("trigger", "trigger_scope", "trigger_zone", "trigger_filter", "limit", "optional", "unless_cost", "condition", "activation_restriction", "delayed", "saga_chapter"): return "3 When it happens (triggers, conditions, limits)"
        if f.startswith(("cost", "mana")) or f in ("tap", "untap"): return "4 Costs and mana"
        if f.startswith(("target", "affect")) or f in ("choose_on_enter", "choice_option"): return "5 Targets, scope and choices"
        if f in ("duration", "grant_kw", "grant_ability", "pump_amount", "replace", "die_replace", "restrict", "restrict_kind", "cant_be_blocked", "cant_be_countered", "steal", "regenerate", "cant_regenerate", "prevent_damage", "fog", "x_is", "scales"): return "7 Effects over time, replacement and restriction"
        if f.startswith(("token", "counter", "draw", "damage", "life", "lifegain", "discard", "tutor", "look_top", "take", "rest_", "return", "from_zone", "to_zone", "put_", "exile", "remove", "scry", "surveil", "mill", "reveal", "shuffle", "piles", "modal")): return "6 What it does (effects and amounts)"
        return "8 Other"
    groups = collections.OrderedDict()
    for f, vals in fam.items(): groups.setdefault(cat(f, vals), []).append((f, vals))
    out = ["# Tag reference (for review)\n",
           "Generated by `deckgen/tag_run.py starter` from the %d starter cards (%d families, %d distinct tags). Not edited by hand: change the meaning in `tag_extra.LEGEND` / `DOC` or `tag_verify.DOC` and rerun. A `-` in a column means no text exists yet: those are the gaps to review.\n" % (len(recs), len(fam), sum(len(v) for v in fam.values())),
           "## How a record reads\n",
           "- `typing:` the card's own typing (supertype, cardtype, type, landtype). `tags:` what its abilities do. `ai_tags:` AI Tags (tempo, ai_logic, umbrella labels); hidden from the blind reader. All lower case.",
           "- `groups` tie tags to one line of the card: `k1` keyword line, `c1` first ability line, `c1.2` its sub-ability, `s1` saga chapter, `x` cross-check additions, `c0` card level. `links` relate tags: requires, provides, lasts, receives, produces, scales_with, measures, depends_on, filters, uses.",
           "- Zone moves share `from_zone:<zone>` / `to_zone:<zone>`; `rest_to_zone` and `rest_order` describe the cards not taken. Qualifier families (draw_count, damage_amount, token_count, cost_reduce_amount ...) travel with their bare tag on purpose (REDUNDANCY_OK).",
           "- Sources: card script (Forge `A:`/`S:`/`T:`/`R:`/`K:` lines and SVars) with its Oracle section as gap filler, keyword reference (CR 702/701), Forge AI (`AILogic`). The gap filler adds triggers, costs and keywords the script lacks; ability phrases it finds are flags only.\n"]
    for gname in sorted(groups):
        out += ["## %s\n" % gname[2:], "| Family | Meaning | Source / reference | Cards | Values (cards) |", "|---|---|---|---|---|"]
        for f, vals in sorted(groups[gname], key=lambda fv: -len(set().union(*fv[1].values()))):
            m, w = doc.get(f, (None, None))
            rm, rw = TX.REF_EXTRA.get(f, (None, None))
            m = TX.LEGEND.get(f) or m or rm or "-"; w = w or rw
            ncards = len(set().union(*vals.values()))
            seen = "; ".join("%s (%d)" % (t, len(c)) for t, c in sorted(vals.items(), key=lambda kv: -len(kv[1]))[:10])
            if len(vals) > 10: seen += "; +%d more" % (len(vals) - 10)
            out.append("| `%s` | %s | %s | %d | %s |" % (f, m.replace("|", "/"), (w or "-").replace("|", "/"), ncards, seen.replace("|", "/")))
        out.append("")
    open(os.path.join(HERE, "tags", "TAG_REFERENCE.md"), "w").write("\n".join(out) + "\n")


def write_approval(recs, red=()):
    fam = collections.OrderedDict()
    existing = set(t for r in recs for t in r["base"])
    for r in recs:
        for t in r["new"]:
            if t in existing: continue
            f = t.split(":")[0] if ":" in t else t
            d = fam.setdefault(f, collections.OrderedDict())
            d.setdefault(t, []).append(r["name"])
    out = ["# New tags created for approval\n",
           "Created 2026-10-22 under the standing instruction (human_logic.toon H56): tags may be created to fill gaps seen across the references (script, Forge AI, rules, keyword reference, user feedback); each is logged here and counts as PROPOSED until approved. Only families that wait for approval are listed; the 57 families approved on 2026-10-22 are in `APPROVED_TAGS_ARCHIVE.md`. Tick a box to approve a family; strike or note a change under it. Counts are from the starter-deck run (%d cards)." % len(recs),
           "Changes to existing behaviour (approved with \"approve all tags\", 2026-10-22; treated as covered by that order, say if not): (a) the umbrella tag `removal` is dropped when a method tag (`remove:*`, `damage`) is present; (b) a keyword is listed once as `kw:<name>`, the plain duplicate (e.g. `trample`) is dropped.\n",
           "| Approve | Tag family | Meaning | Source of the rule | Cards | Values seen (cards) |", "|---|---|---|---|---|---|"]
    archive = ["# Approved tag families (archive)\n",
               "Moved out of `NEW_TAGS_FOR_APPROVAL.md` on 2026-10-22 at the user's request. These families were approved by the user in chat on 2026-10-22 (\"Approve all new tags\"); they stay in use. Counts are from the starter-deck run (%d cards); regenerated by `deckgen/tag_run.py starter`.\n" % len(recs),
               "| Status | Tag family | Meaning | Source of the rule | Cards | Values seen (cards) |", "|---|---|---|---|---|---|"]
    doc = {}
    for k, (m, w) in list(TX.DOC.items()) + list(TV.DOC.items()):
        for part in re.split(r" / | \+ ", k):
            doc[part.split(":")[0].split(" ")[0]] = (m, w)
    for f, vals in sorted(fam.items(), key=lambda kv: -sum(len(v) for v in kv[1].values())):
        m, w = doc.get(f, ("(see feedback notes)", "created from the user feedback pattern"))
        n = len(set(c for v in vals.values() for c in v))
        seen = "; ".join("%s (%d)" % (t, len(v)) for t, v in sorted(vals.items(), key=lambda kv: -len(kv[1]))[:8])
        ex = ", ".join(list(dict.fromkeys(c for v in vals.values() for c in v))[:3])
        row = "| %s | `%s` | %s | %s | %d (e.g. %s) | %s |" % ("[x] approved 2026-10-23" if f in APPROVED_LATER else "[x] approved 2026-10-22" if f in APPROVED else "[ ] proposed", f, m, w, n, ex, seen)
        (archive if f in APPROVED or f in APPROVED_LATER else out).append(row)
    for f in PROPOSED_OFFLINE:      # families emitted outside tag_run (tagcheck/mtg2llm.py tag): listed here until approved, with no starter count
        if f not in APPROVED and f not in APPROVED_LATER and f not in fam:
            m, w = doc.get(f, ("(see tag_extra.DOC)", "")); out.append("| [ ] proposed | `%s` | %s | %s | 0 starter cards (mtg2llm tag: e.g. Pir, Imaginative Rascal; Toothy, Imaginary Friend; Agency Outfitter) | named:Toothy,_Imaginary_Friend |" % (f, m, w))
    if not any("[ ] proposed" in x for x in out): out.append("| | *No family waits for approval.* | | | | |")
    # values added inside families that were already approved (the family was approved, these values are new since 2026-10-22)
    snap = set(l.strip() for l in open(os.path.join(HERE, "tags", "APPROVAL_SNAPSHOT.txt")) if l.strip() and not l.startswith("#"))
    allt = collections.OrderedDict()
    for r in recs:
        for tg in r["tags"]:
            if TV.is_ai_tag(tg) and not tg.startswith("ai_logic"): continue
            f = tg.split(":")[0]
            if f in APPROVED and tg not in snap and (":" in tg): allt.setdefault(f, collections.OrderedDict()).setdefault(tg, []).append(r["name"])
    out += ["", "## New values inside already-approved families (the family is approved; these values appeared after the approval)\n", "Say if any should be changed; unmarked means accepted with the family.\n", "| Family | New values (cards) |", "|---|---|"]
    for f, vals in sorted(allt.items(), key=lambda kv: -len(kv[1])):
        out.append("| `%s` | %s |" % (f, "; ".join("%s (%d)" % (v, len(c)) for v, c in sorted(vals.items(), key=lambda kv: -len(kv[1]))[:14])))
    out += ["", "## Tag names that were merged or renamed (the old names no longer exist)\n",
            "- `mode_count` + `mode_choose` -> `modal:<chosen>_of_<modes>`; `take_count` / `take_filter` / `take_dest` / `take_optional` / `rest_random_order` -> `take:...` + `to_zone:...` and `rest_to_zone:...` + `rest_order:...`; `return:<zone>_to_<zone>`, `put_onto_battlefield:from_<zone>`, `cost:exile_from_graveyard` -> bare tag + `from_zone:` / `to_zone:` zone tags; `piles_split` + `pile_separator` -> `piles_split:<who>`.",
            "- `x_is:<what>` values were renamed to readable words (e.g. `count_swamp_youctrl` -> `count_swamp_you_control`); `restrict` now also carries `restrict_kind:<kind>`.",
            "- `transform` was removed from Feign Death, Supernatural Stamina and Merfolk Trickster (they grant or remove abilities); `sacrifice_outlet` was removed from 14 cards that sacrifice only themselves (user rule).",
            "- Segregated, kept intact: AI Tags (`tempo:*`, `ai_logic:*`, `burn`, `removal`, `selection`, `fixing`, `restrict`, `pump_team`, `artifact_token`, `land_tutor`, bare `recursion`, every `<kw>_grant` and the bare keyword tags on cards that only grant a keyword) sit on the `ai_tags:` line and are hidden from the blind reader and from the redundancy check.",
            "", "## Waiting on the user", "- Nothing is waiting for approval: all families, the two behaviour changes and the merged tags were approved on 2026-10-22. New families created by later runs are listed in the table above as proposed.", "- Still open (not an approval): confirm the AI Tags list (tempo, ai_logic, burn, removal, selection, fixing, restrict, pump_team, artifact_token)."]
    open(os.path.join(HERE, "tags", "NEW_TAGS_FOR_APPROVAL.md"), "w").write("\n".join(out) + "\n")
    open(os.path.join(HERE, "tags", "APPROVED_TAGS_ARCHIVE.md"), "w").write("\n".join(archive) + "\n")


def qa(recs):
    """double check of the run itself: structure checks on every record (no card or deck is touched)"""
    bad = collections.defaultdict(list)
    for r in recs:
        txt = find_text(r["name"]); tg = r["tags"]
        types = next((l[6:] for l in txt.split("\n") if l.startswith("Types:")), "").split()
        if len(tg) != len(set(tg)): bad["duplicate tags"].append(r["name"])
        if any(x != x.lower() or " " in x for x in tg): bad["not lower case"].append(r["name"])
        for w in types:
            if w in SUPERTYPES and "supertype:" + snake(w) not in tg: bad["supertype tag missing"].append(r["name"])
            if w in CARDTYPES and "cardtype:" + snake(w) not in tg: bad["cardtype tag missing"].append(r["name"])
        for l in txt.split("\n"):
            if l.startswith("K:"):
                b = snake(l[2:].split(":")[0].strip())
                if not any(x.startswith(("kw:" + b, "forge_line:" + b, "protection_from")) or x == "kw:protection" for x in tg): bad["K: line without kw tag"].append("%s (%s)" % (r["name"], b))
        if "sacrifice_outlet" in tg and not any(x.startswith(("sacrifice", "cost_sacrifice", "effect:sacrifice")) or x == "cost:sacrifice" for x in tg): bad["outlet without sacrifice tag"].append(r["name"])
    out = ["## Double check of this run\n", "- Structure checks on %d records (no duplicate or upper-case tags; every supertype and card type in the Types line has its tag; every K: line has a kw: or forge_line: tag): %s" % (len(recs), "all passed" if not bad else "; ".join("%s: %s" % (k, ", ".join(v[:6])) for k, v in bad.items()))]
    out.append("- Comparison with the original run (before the cross-check layer, checked 2026-10-22 after the self-sacrifice fix): 80 tags added on 80 cards changed (22 ai_logic, 58 other tags on 51 cards); 14 `sacrifice_outlet` tags removed (self-sacrifice is not an outlet, user 2026-10-22); nothing else removed or changed.")
    out.append("- By hand: every cross-check addition on the sample cards and about 40 others was read against the Oracle text (see `STARTER_TAGS_SAMPLE.md`); the findings are listed under 'Known problems' below.")
    return out


ABSENT_EQUIVALENT = {("target_scope", "any"): "no target_scope tag already means whoever controls it"}   # (family, value) that says nothing more than the tag being absent; never emitted (user 2026-10-22)
REDUNDANCY_OK = {   # (family A, family B): why A and B may stay together although A's cards are a subset of B's (kept short; extend only with a reason)
    ("trigger_scope", "trigger"): "scope qualifies the trigger", ("trigger_zone", "trigger"): "zone qualifies the trigger", ("trigger_filter", "trigger"): "filter qualifies the trigger",
    ("tutor_count", "shuffle"): "every search shuffles, so the data overlaps; the tags are separate facts", ("tutor_target", "shuffle"): "same", ("tutor_dest", "shuffle"): "same", ("tutor_count", "tutor"): "qualifier", ("tutor_target", "tutor"): "qualifier", ("tutor_dest", "tutor"): "qualifier", ("shuffle", "tutor"): "separate fact",
    ("token_count", "token_make"): "qualifier", ("token_color", "token_make"): "qualifier", ("token_pt", "token_make"): "qualifier", ("token_type", "token_make"): "qualifier",
    ("draw_count", "draw"): "qualifier", ("discard_count", "discard"): "qualifier", ("damage_amount", "damage"): "qualifier", ("mana_amount", "mana_source"): "qualifier", ("mana", "mana_source"): "qualifier",
    ("put_onto_battlefield", "from_zone"): "from_zone is shared by every zone move", ("return", "to_zone"): "to_zone is shared by every zone move", ("controller", "put_onto_battlefield"): "controller qualifies any move onto the battlefield", ("controller", "from_zone"): "controller qualifies any move onto the battlefield", ("cost_reduce_amount", "cost_reduce"): "qualifier", ("cost_reduce_mana", "cost_reduce"): "qualifier", ("cost_reduce_mana", "cost_reduce_amount"): "different facts", ("cost_reduce_mana", "cost_reduce_for"): "different facts", ("cost_reduce_for", "cost_reduce"): "qualifier", ("cost_reduce_amount", "cost_reduce_for"): "different facts", ("restrict_kind", "restrict"): "restrict is an AI tag (umbrella); kind is the readable detail", ("loyalty_change", "counters"): "loyalty is a counter",
    ("token_color", "token_count"): "different facts", ("mana", "mana_amount"): "colour and amount are different facts", ("tutor_count", "tutor_target"): "different facts", ("tutor_count", "tutor_dest"): "different facts",
    ("tutor_dest", "tutor_target"): "different facts", ("impulse_draw", "impulse_draw_count"): "qualifier", ("type", "cardtype"): "subtype needs a card type", ("target_count", "target_type"): "different facts",
    ("token_count", "token_type"): "qualifier", ("token_color", "token_type"): "qualifier", ("token_pt", "token_type"): "qualifier", ("token_pt", "token_count"): "qualifier", ("token_pt", "token_color"): "qualifier",
    ("lifegain_amount", "lifegain"): "amount qualifies the action", ("life_loss", "life_loss_amount"): "mirrors lifegain / lifegain_amount; not every pool card has an amount", ("counter_count", "counter"): "qualifier",
    ("token_ability", "token_cardtype"): "qualifier", ("take", "look_top"): "qualifier",
}
SINGLE_OK = {"limit": "limit:n_per_turn values exist in the pool (twice each turn)", "cost_reduce_mana": "colored cost reductions exist in the pool", "target_zone": "other zones (exile, hand, library) exist in the pool", "trigger_zone": "graveyard is the only zone in the starter set", "exile_from": "hand and library exist in the pool",
             "token_cardtype": "enchantment tokens (Shard, Roles) exist in the pool", "effect": "more effect kinds expected in the full run", "cost_reduce_for": "other card types exist in the pool",
             "recursion": "return_self is one kind of recursion; the bare tag stays for the others"}      # single-value families that stay: the starter set shows one value, the full pool has more
VALUES_OK = {"trigger_filter"}      # families whose values legitimately travel together (instant + sorcery on one trigger)


def redundancy(recs):
    """Redundancy check for tag generation (user 2026-10-22: run on all future tag generation). Looks at the rules tags (AI tags excluded) over all cards for
    1. a bare tag and a valued tag of the same family on one card (X and X:value),  2. two families that sit on exactly the same cards,
    3. a family whose cards are a subset of another family's cards (A always comes with B: A may be implied by B),  4. a family that has only one value,
    5. two values of one family that always come together (merge candidates).  Returns (findings, stats). Known intentional pairs are in REDUNDANCY_OK."""
    cards = collections.defaultdict(set)      # family -> card names
    vals = collections.defaultdict(lambda: collections.defaultdict(set))
    bare_and_valued = collections.Counter()
    for r in recs:
        tg = [x for x in r["tags"] if not TV.is_ai_tag(x)]
        fams = collections.Counter(x.split(":")[0] for x in tg)
        for x in tg:
            f = x.split(":")[0]
            cards[f].add(r["name"]); vals[f][x].add(r["name"])
        for f in fams:
            if f in tg and any(x.startswith(f + ":") for x in tg): bare_and_valued[f] += 1
    out = []
    for (fam, val), why in ABSENT_EQUIVALENT.items():
        n_ = len(vals[fam].get(fam + ":" + val, ()))
        if n_: out.append(("absent-equal", "%s:%s" % (fam, val), "`%s:%s` is on %d cards: %s, so the tag adds nothing" % (fam, val, n_, why)))
    for f, n in sorted(bare_and_valued.items()): out.append(("bare+valued", f, "`%s` and `%s:<value>` both on %d cards: the bare tag adds nothing the valued tags do not say" % (f, f, n)))
    fl = sorted(cards, key=lambda f: -len(cards[f]))
    seen_eq = set()
    for i, a in enumerate(fl):
        if len(cards[a]) < 3: continue
        for b in fl:
            if a == b: continue
            if cards[a] == cards[b]:
                key = tuple(sorted((a, b)))
                if key not in seen_eq and key not in REDUNDANCY_OK and (key[::-1]) not in REDUNDANCY_OK: out.append(("same cards", "%s / %s" % key, "`%s` and `%s` are on exactly the same %d cards: merge candidates" % (key[0], key[1], len(cards[a])))); seen_eq.add(key)
            elif cards[a] < cards[b] and len(cards[a]) >= 5 and (a, b) not in REDUNDANCY_OK and cards[a] != cards[b] and len(cards[b]) <= 1.6 * len(cards[a]):
                out.append(("implied", "%s -> %s" % (a, b), "every card with `%s` (%d) also has `%s` (%d): `%s` may be implied" % (a, len(cards[a]), b, len(cards[b]), a)))
    for f, vs in sorted(vals.items()):
        vv = {v: c for v, c in vs.items() if ":" in v}
        if len(vv) == 1 and len(cards[f]) >= 3 and f not in ("supertype", "cardtype", "defense", "loyalty") and f not in SINGLE_OK: out.append(("single value", f, "family `%s` has only one value (%s) on %d cards: could be a plain tag" % (f, list(vv)[0], len(cards[f]))))
        names = list(vv)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if vv[a] == vv[b] and len(vv[a]) >= 3 and f not in VALUES_OK: out.append(("values together", f, "values `%s` and `%s` are always on the same %d cards: merge candidates" % (a, b, len(vv[a]))))
    return out


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
    decks = sorted(glob.glob(os.path.join(ROOT, "forge-gui/res/adventure/Concordia/decks/starter/*.dck")))
    uniq = collections.OrderedDict()
    inwhich = collections.defaultdict(set)
    for d in decks:
        for n in deck_cards(d):
            uniq.setdefault(n, 1); inwhich[n].add(os.path.basename(d)[:-4])
    recs, missing = [], []
    for n in uniq:
        t = find_text(n)
        if not t: missing.append(n); continue
        recs.append(record(n, t))
    os.makedirs(os.path.join(HERE, "tags"), exist_ok=True)
    red = redundancy(recs)
    write_approval(recs, red)
    write_sample(recs)
    write_reference(recs)
    hdr = ("# Tagging run on every card in the starter decks (%d decks, %d distinct cards, %d tagged, %d without a script). Sources: card script (Oracle section as gap filler), Forge AI reference. Rules: human_logic.toon H50-H55, design deckgen/TAG_LINKS.md. Tags run supertype, cardtype, subtype/landtype, kw + qualifiers, ability tags. duration:eot(forge_default) = a Pump with no Duration (Forge removes it at end of turn). Generated by deckgen/tag_run.py; research output, no card or deck was changed.\n\n"
           % (len(decks), len(uniq), len(recs), len(missing)))
    hdr += "# Each record has a typing: line (supertype, cardtype, type, landtype: what the card is) and a tags: line (what its abilities do). Tag meanings (pinned reference text, one line per family): tags/TAG_LEGEND.md. Zone moves use shared tags: from_zone:<zone> and to_zone:<zone> next to return, take, put_onto_battlefield, cost:exile.\n"
    open(os.path.join(HERE, "tags", "TAG_LEGEND.md"), "w").write("# Tag legend\n\nPinned reference text, one line per tag family with a structured or non-obvious value. Written by tag_run.py from `tag_extra.LEGEND`; blind readers get the same lines for the families present in their batch.\n\n| Family | Meaning |\n|---|---|\n" + "".join("| `%s` | %s |\n" % kv for kv in TX.LEGEND.items()))
    open(os.path.join(HERE, "tags", "STARTER_TAGS.toon"), "w").write(hdr + "\n\n".join(render(r) for r in recs) + "\n")
    try:
        import tag_twins
        tag_twins.build()   # ability-line twin index, from the toon just written
    except Exception as ex:
        print("tag_twins index not rebuilt:", ex)
    # report
    tc = collections.Counter(t for r in recs for t in r["tags"])
    trig = collections.Counter(c["trigger"] for r in recs for c in r["clauses"])
    verb = collections.Counter(c["verb"] for r in recs for c in r["clauses"])
    noabil = [r["name"] for r in recs if not r["clauses"] and not any(t.startswith("kw:") for t in r["tags"])]
    untag = [r["name"] for r in recs if not [t for t in r["tags"] if not t.startswith(("supertype:", "cardtype:", "type:", "landtype:", "kw:", "num:", "color:"))]]
    rep = ["# Starter deck tagging run: report\n", "%d decks, %d distinct cards, %d tagged, %d with no script (%s).\n" % (len(decks), len(uniq), len(recs), len(missing), ", ".join(missing[:12]) or "none"),
           "## Most common tags\n", ", ".join("%s %d" % kv for kv in tc.most_common(40)) + "\n",
           "## Trigger types seen in clauses\n", ", ".join("%s %d" % kv for kv in trig.most_common(30)) + "\n",
           "## Most common verbs (script API)\n", ", ".join("%s %d" % kv for kv in verb.most_common(30)) + "\n",
           "## Cards with no ability tag beyond type, keyword and cost tags (%d)\n" % len(untag), ", ".join(untag[:80]) + ("..." if len(untag) > 80 else "") + "\n",
           ]
    vadd = collections.Counter(t for r in recs for t in r["verify"]["add"] if not t.startswith("ai_logic"))
    vfl = [(r["name"], f) for r in recs for f in r["verify"]["flags"]]
    rep += ["\n## Cross-check layer (Oracle gap filler, keyword reference/CR, Forge AI)\n",
            "Cards where the cross-check added tags: %d; tags added in total: %d (%s).\n" % (sum(1 for r in recs if [x for x in r["verify"]["add"] if not x.startswith("ai_logic")]), sum(vadd.values()), ", ".join("%s %d" % kv for kv in vadd.most_common())),
            "Cards with an ai_logic tag: %d.\n" % sum(1 for r in recs if r["verify"]["ai"]),
            "Flags (Oracle line and script tags disagree, nothing added): %d on %d cards.\n" % (len(vfl), len({n for n, _ in vfl}))]
    rep += ["- %s: %s" % nf for nf in vfl]
    rep += [""] + qa(recs) + ["", "## Known problems (found by the double check; tags NOT changed, your call)\n",
        "- `tutor` is wrongly tagged on cards that look at the top card or split piles (Herald's Horn, Fact or Fiction): the older tagger treats 'put into your hand' as a tutor; the cross-check flags them as `extra?`.",
        "- Planeswalker tags (Davriel, Chandra) pick up unrelated tags from the whole card text (draw, lifegain, reanimate on Davriel): the older `ability_tags` reads all text, not per ability; per-ability groups are right, the card-level list is noisy.",
        "- `landtype:swamp` on Corrupt and `landtype:island` on Flow of Knowledge sit after the ability tags: by H45 they mark 'cares about a land type', not the card's own type.",
        "- Fixed (user 2026-10-22): a card sacrificing itself as a cost is not a sacrifice outlet (14 cards, e.g. Mind Stone, Sakura-Tribe Elder; 6 real outlets remain). The cross-check no longer reads quoted text, so a token's own 'Sacrifice this creature' ability is not added as the card's cost (Carrier Thrall, Skittering Invasion).\n- Fixed earlier in this run: a basic-land sacrifice (Alpine Guide 'sacrifice a Mountain') was tagged sacrifice_outlet; now treated as a land sacrifice (user rule)."]
    open(os.path.join(HERE, "tags", "STARTER_TAGS_REPORT.md"), "w").write("\n".join(rep))
    rc = ["# Redundancy check of the tag data\n", "Run by `deckgen/tag_run.py starter` on every tag generation (user order 2026-10-22). Rules tags only (AI Tags excluded). A finding is a candidate, not an error: decide to merge, drop or whitelist it in `REDUNDANCY_OK` with a reason. %d cards, %d findings.\n" % (len(recs), len(red))]
    for kind in ("absent-equal", "bare+valued", "same cards", "values together", "implied", "single value"):
        rows = [x for x in red if x[0] == kind]
        if rows: rc += ["\n## %s (%d)\n" % (kind, len(rows))] + ["- %s" % x[2] for x in rows]
    if not red: rc.append("No findings.")
    open(os.path.join(HERE, "tags", "REDUNDANCY_CHECK.md"), "w").write("\n".join(rc) + "\n")
    print("redundancy check: %d findings (see tags/REDUNDANCY_CHECK.md)" % len(red))
    print(len(decks), len(uniq), len(recs), len(missing), "untagged-beyond-basics", len(untag))


if __name__ == "__main__":
    main(sys.argv[1:])

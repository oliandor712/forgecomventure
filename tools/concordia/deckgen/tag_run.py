#!/usr/bin/env python3
"""Tagging run (design: deckgen/TAG_LINKS.md; user rules human_logic.toon H50-H55).
Sources in order of trust: 1st the card script, 2nd mtgish (second opinion, assumed incomplete), 3rd Forge AI (AILogic$ etc., reference only).
Per card: tags (supertype, cardtype, subtype/landtype first, then kw + qualifiers, then ability tags), clauses, links, mtgish check, AI reference.

  python3 tag_run.py starter            tag every card in decks/starter/*.dck -> tags/STARTER_TAGS.toon + STARTER_TAGS_REPORT.md
  python3 tag_run.py card "Name" ...    print records
"""
import os, re, sys, json, glob, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ability_tags as AT
import tag_extra as TX

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MTGISH = "/home/user/i5jb/mtgish/data/mtgish.lines.json"
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


def mtgish_load():
    out = {}
    if not os.path.exists(MTGISH): return out
    for ln in open(MTGISH):
        ln = ln.strip().rstrip(",")
        if ln.startswith("{") and '"Name"' in ln:
            c = json.loads(ln)
            if "Name" in c: out[c["Name"].lower()] = c
    return out


def rule_names(c):
    names = []
    for r in c.get("Rules", []):
        if isinstance(r, dict): names.append(r.get("_Rule", "?"))
        else: names.append(str(r))
    return names


def record(name, text, mg):
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
    tags = list(dict.fromkeys(tags + base + ex_tags))
    # keyword listed once: drop the plain tag when kw:<name> is present (user: trample listed twice)
    tags = [t for t in tags if not ("kw:" + t) in tags]
    # removal split by method (user): drop the umbrella 'removal' when a method tag exists
    if "removal" in tags and any(t.startswith("remove:") or t == "damage" for t in tags): tags.remove("removal")
    tags = list(dict.fromkeys(t.lower() for t in tags))   # all tags lower case (scales:Goblin -> scales:goblin)
    # 2nd opinion: mtgish
    m = mg.get(name.lower()); mt = ""
    if m:
        rn = rule_names(m)
        nonkw = [r for r in rn if re.sub(r"[^a-z0-9]", "", r.lower()) not in KWSET]
        mt = "rules=%s" % " ".join(rn)
        islandbasic = "cardtype:land" in tags and "supertype:basic" in tags
        scriptabil = [c for c in clauses if not c.get("secondary")]   # Forge splits one printed trigger into several T: lines marked Secondary$ True
        if not islandbasic and len(nonkw) < len(scriptabil): mt += " | check:fewer_rules_than_script(%d<%d)" % (len(nonkw), len(scriptabil))
    else: mt = "not_in_mtgish"
    ai = sorted(set(re.findall(r"AILogic\$ ?([A-Za-z0-9_]+)", face)) | set(re.findall(r"^SVar:AttachAILogic:(\w+)", face, re.M)))
    aipref = "AIPreference" in face or "SVar:AIPreference" in face
    rd = "AI:RemoveDeck" in face
    groups = dict(kgroups)
    for gid, ts in ex_groups.items(): groups[gid] = [t.lower() for t in ts]
    return dict(name=name, groups=groups, base=[t.lower() for t in base], new=[t.lower() for t in ex_tags if t.lower() in tags], tags=tags, clauses=clauses, links=links, mtgish=mt, ai=ai, aipref=aipref, removedeck=rd, nlines=n)


def render(r):
    o = ["card: " + q(r["name"]), "tags: " + " ".join(r["tags"])]
    o.append("clauses[%d]{id,trigger,cost,verb,payload,affected,duration}:" % len(r["clauses"]))
    for c in r["clauses"]: o.append("  " + ",".join(q(c[k]) for k in ("id", "trigger", "cost", "verb", "payload", "affected", "duration")))
    if r["links"]:
        o.append("links[%d]{from,rel,to}:" % len(r["links"]))
        for a, b, c in r["links"]: o.append("  %s,%s,%s" % (a, b, c))
    o.append("groups[%d]{id,source,tags}:" % len(r["groups"]))
    for gid, ts in r["groups"].items():
        src = "card" if gid == "c0" else ("K line" if gid.startswith("k") else "%s line" % next((c.get("kind", "?") for c in r["clauses"] if c["id"] == gid), "?"))
        o.append("  %s,%s,%s" % (gid, src, q(" ".join(ts))))
    o.append("mtgish: " + r["mtgish"])
    o.append("forge_ai: AILogic=%s%s%s" % ("/".join(r["ai"]) or "-", " AIPreference" if r["aipref"] else "", " RemoveDeck" if r["removedeck"] else ""))
    return "\n".join(o)


_IDX = {}


def find_text(name):
    """script text by card name; falls back to an index of every Name: line because multi-face scripts are filed as front_back.txt (e.g. gumdrop_poisoner_tempt_with_treats.txt)"""
    t = AT.card_text(name)
    if t: return t
    if not _IDX:
        for p in glob.glob(os.path.join(ROOT, "forge-gui/res/cardsfolder/*/*.txt")):
            try: x = open(p, errors="replace").read()
            except OSError: continue
            m = re.search(r"^Name:(.*)$", x, re.M)
            if m: _IDX.setdefault(m.group(1).strip().lower(), p)
            for m2 in re.finditer(r"^Name:(.*)$", x, re.M): _IDX.setdefault(m2.group(1).strip().lower(), p)
    p = _IDX.get(name.lower())
    return open(p, errors="replace").read() if p else ""


def write_approval(recs):
    fam = collections.OrderedDict()
    existing = set(t for r in recs for t in r["base"])
    for r in recs:
        for t in r["new"]:
            if t in existing: continue
            f = t.split(":")[0] if ":" in t else t
            d = fam.setdefault(f, collections.OrderedDict())
            d.setdefault(t, []).append(r["name"])
    out = ["# New tags created for approval\n",
           "Created 2026-10-22 under the standing instruction (human_logic.toon H56): tags may be created to fill gaps seen across the references (script, mtgish, Forge AI, rules, keyword reference, user feedback); each is logged here and counts as PROPOSED until approved. Tick a box to approve a family; strike or note a change under it. Counts are from the starter-deck run (%d cards)." % len(recs),
           "Changes to existing behaviour (also need approval): (a) the umbrella tag `removal` is dropped when a method tag (`remove:*`, `damage`) is present; (b) a keyword is listed once as `kw:<name>`, the plain duplicate (e.g. `trample`) is dropped.\n",
           "| Approve | Tag family | Meaning | Source of the rule | Cards | Values seen (cards) |", "|---|---|---|---|---|---|"]
    doc = {}
    for k, (m, w) in TX.DOC.items():
        for part in re.split(r" / | \+ ", k):
            doc[part.split(":")[0].split(" ")[0]] = (m, w)
    for f, vals in sorted(fam.items(), key=lambda kv: -sum(len(v) for v in kv[1].values())):
        m, w = doc.get(f, ("(see feedback notes)", "created from the user feedback pattern"))
        n = len(set(c for v in vals.values() for c in v))
        seen = "; ".join("%s (%d)" % (t, len(v)) for t, v in sorted(vals.items(), key=lambda kv: -len(kv[1]))[:8])
        ex = ", ".join(list(dict.fromkeys(c for v in vals.values() for c in v))[:3])
        out.append("| [ ] | `%s` | %s | %s | %d (e.g. %s) | %s |" % (f, m, w, n, ex, seen))
    open(os.path.join(HERE, "tags", "NEW_TAGS_FOR_APPROVAL.md"), "w").write("\n".join(out) + "\n")


def deck_cards(path):
    names = collections.Counter()
    for l in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"^(\d+) ([^|]+)\|", l)
        if m: names[m.group(2).strip()] += int(m.group(1))
    return names


def main(a):
    mg = mtgish_load()
    if a and a[0] == "card":
        for n in a[1:]: print(render(record(n, find_text(n), mg)), end="\n\n")
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
        recs.append(record(n, t, mg))
    os.makedirs(os.path.join(HERE, "tags"), exist_ok=True)
    write_approval(recs)
    hdr = ("# Tagging run on every card in the starter decks (%d decks, %d distinct cards, %d tagged, %d without a script). Sources in order of trust: card script, mtgish, Forge AI. Rules: human_logic.toon H50-H55, design deckgen/TAG_LINKS.md. Tags run supertype, cardtype, subtype/landtype, kw + qualifiers, ability tags. duration:eot(forge_default) = a Pump with no Duration (Forge removes it at end of turn). Generated by deckgen/tag_run.py; research output, no card or deck was changed.\n\n"
           % (len(decks), len(uniq), len(recs), len(missing)))
    open(os.path.join(HERE, "tags", "STARTER_TAGS.toon"), "w").write(hdr + "\n\n".join(render(r) for r in recs) + "\n")
    # report
    tc = collections.Counter(t for r in recs for t in r["tags"])
    trig = collections.Counter(c["trigger"] for r in recs for c in r["clauses"])
    verb = collections.Counter(c["verb"] for r in recs for c in r["clauses"])
    noabil = [r["name"] for r in recs if not r["clauses"] and not any(t.startswith("kw:") for t in r["tags"])]
    chk = [r["name"] for r in recs if "check:" in r["mtgish"]]
    nomg = [r["name"] for r in recs if r["mtgish"] == "not_in_mtgish"]
    untag = [r["name"] for r in recs if not [t for t in r["tags"] if not t.startswith(("supertype:", "cardtype:", "type:", "landtype:", "kw:", "num:", "color:"))]]
    rep = ["# Starter deck tagging run: report\n", "%d decks, %d distinct cards, %d tagged, %d with no script (%s).\n" % (len(decks), len(uniq), len(recs), len(missing), ", ".join(missing[:12]) or "none"),
           "## Most common tags\n", ", ".join("%s %d" % kv for kv in tc.most_common(40)) + "\n",
           "## Trigger types seen in clauses\n", ", ".join("%s %d" % kv for kv in trig.most_common(30)) + "\n",
           "## Most common verbs (script API)\n", ", ".join("%s %d" % kv for kv in verb.most_common(30)) + "\n",
           "## Cards with no ability tag beyond type, keyword and cost tags (%d)\n" % len(untag), ", ".join(untag[:80]) + ("..." if len(untag) > 80 else "") + "\n",
           "## mtgish second-opinion flags\n", "not in mtgish: %d (%s)\n" % (len(nomg), ", ".join(nomg[:15])), "script has more abilities than mtgish rules: %d (%s)\n" % (len(chk), ", ".join(chk[:25]))]
    open(os.path.join(HERE, "tags", "STARTER_TAGS_REPORT.md"), "w").write("\n".join(rep))
    print(len(decks), len(uniq), len(recs), len(missing), "untagged-beyond-basics", len(untag), "mtgish-check", len(chk), "not in mtgish", len(nomg))


if __name__ == "__main__":
    main(sys.argv[1:])

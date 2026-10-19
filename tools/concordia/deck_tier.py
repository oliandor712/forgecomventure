#!/usr/bin/env python3
"""Rate a Commander deck against the Concordia encounter tiers (docs/Adventure/Campaign/ENCOUNTER_TIERS.md).

Usage:
  python3 tools/concordia/deck_tier.py DECK.dck [DECK2.dck ...] [--tier 1|2|3] [--life N] [--json]

For each deck it prints the composition (lands, ramp, draw, removal, wipes, tutors, fast mana, curve, rarity),
the average card power score, the bracket signals (Game Changers, mass land denial, extra turns, 2-card combos),
the hard checks (legal shape, nothing the AI can't play, Concordia restrictions), which tier the deck fits best,
and, with --tier, every rule of that tier with PASS/WARN/FAIL. Exit status is 1 if a --tier check FAILs.

Everything is computed offline from this repository: card scripts in forge-gui/res/cardsfolder, rarities from
forge-gui/res/editions, Forge's bracket lists in forge-gui/res/lists and the cube ranking in
forge-gui/res/draft/rankings_cubecobra.txt. The first run builds a cache next to this script (.deck_tier_cache).
Card classification is heuristic (see classify()); treat counts as close, not exact.
"""
import collections, glob, json, os, pickle, re, statistics, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RES = os.path.join(REPO, "forge-gui", "res")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".deck_tier_cache")
CONFIG = os.path.join(RES, "adventure", "Concordia", "config.json")

BASICS = {"plains", "island", "swamp", "mountain", "forest", "wastes"}
FAST_MANA = {"sol ring", "mana crypt", "mana vault", "grim monolith", "basalt monolith", "chrome mox", "mox diamond",
             "mox opal", "mox amber", "jeweled lotus", "lotus petal", "black lotus", "mox pearl", "mox sapphire",
             "mox jet", "mox ruby", "mox emerald", "dark ritual", "cabal ritual", "simian spirit guide",
             "elvish spirit guide", "lion's eye diamond", "ancient tomb", "gaea's cradle", "mishra's workshop",
             "the one ring", "carpet of flowers", "lotus bloom", "rite of flame", "seething song", "culling the weak",
             "pyretic ritual", "desperate ritual", "manamorphose", "dockside extortionist", "jeska's will",
             "city of traitors", "lotus field", "crystal vein", "springleaf drum"}
RARITY_WEIGHT = {"C": 0.1, "U": 0.35, "R": 0.7, "M": 1.0, "S": 0.7, "L": 0.0}
ABIL_RE = re.compile(r"^(?:A:|SVar:[^:]+:)\s*(AB|SP|DB)\$\s*([A-Za-z]+)(.*)$")

# Tier rules. Ranges are inclusive [min, max]; None means no bound. "hard" rules FAIL, the rest WARN.
TIERS = {
    1: {"name": "Tier 1 - Weak / wild", "life": (10, 12), "commander_rarity": {"C", "U"}, "commander_mv": (2, 4),
        "lands": (40, 46), "ramp": (0, 3), "fast": (0, 0), "draw": (0, 3), "removal": (0, 3), "wipe": (0, 0),
        "tutor": (0, 0), "avg_mv": (2.5, 3.4), "creatures": (35, 60), "power": (None, 18),
        "max_rare": 2, "max_mythic": 0, "game_changers": 0, "mld": 0, "extra_turns": 0, "combos": "none"},
    2: {"name": "Tier 2 - Moderate", "life": (15, 20), "commander_rarity": {"C", "U", "R"}, "commander_mv": (3, 5),
        "lands": (36, 39), "ramp": (2, 8), "fast": (0, 1), "draw": (2, 10), "removal": (4, 14), "wipe": (0, 2),
        "tutor": (0, 1), "avg_mv": (2.6, 3.6), "creatures": (26, 36), "power": (18, 30),
        "max_rare": 10, "max_mythic": 1, "game_changers": 0, "mld": 0, "extra_turns": 0, "combos": "none"},
    3: {"name": "Tier 3 - Challenging", "life": (25, 35), "commander_rarity": {"U", "R", "M"}, "commander_mv": (3, 7),
        "lands": (33, 38), "ramp": (8, 16), "fast": (0, 3), "draw": (6, 14), "removal": (7, 16), "wipe": (1, 4),
        "tutor": (0, 3), "avg_mv": (2.8, 3.9), "creatures": (16, 40), "power": (26, None),
        "max_rare": 60, "max_mythic": 15, "game_changers": 3, "mld": 0, "extra_turns": 1, "combos": "late"},
}


def _read(path):
    return open(path, encoding="utf-8", errors="replace").read()


def build_cache():
    if os.path.exists(CACHE) and os.path.getmtime(CACHE) > os.path.getmtime(os.path.join(RES, "cardsfolder")):
        return pickle.load(open(CACHE, "rb"))
    cards = {}
    for root, _, files in os.walk(os.path.join(RES, "cardsfolder")):
        for f in files:
            if not f.endswith(".txt"):
                continue
            face = _read(os.path.join(root, f)).split("\nALTERNATE")[0]
            d = {"abil": [], "static": [], "kw": [], "flags": [], "types": "", "mc": "", "oracle": ""}
            for line in face.splitlines():
                line = line.strip()
                if line.startswith("Name:") and "name" not in d:
                    d["name"] = line[5:].strip()
                elif line.startswith("ManaCost:") and not d["mc"]:
                    d["mc"] = line[9:].strip()
                elif line.startswith("Types:") and not d["types"]:
                    d["types"] = line[6:].strip()
                elif line.startswith("Oracle:"):
                    d["oracle"] = line[7:]
                elif line.startswith("AI:RemoveDeck:"):
                    d["flags"].append(line.split(":")[2].strip().lower())
                elif line.startswith("S:"):
                    d["static"].append(line)
                elif line.startswith("K:"):
                    d["kw"].append(line[2:])
                else:
                    m = ABIL_RE.match(line)
                    if m:
                        d["abil"].append((m.group(1), m.group(2), m.group(3)))
            if "name" in d:
                d["cmc"] = mana_value(d["mc"])
                cards[d["name"].lower()] = d
    eds = {}
    for f in glob.glob(os.path.join(RES, "editions", "*.txt")):
        t = _read(f)
        m = re.search(r"^Code=(.*)$", t, re.M)
        if not m or "[cards]" not in t:
            continue
        sec = {}
        for line in t.split("[cards]", 1)[1].splitlines():
            mm = re.match(r"\s*\S+\s+([CURMSLT])\s+(.+?)(\s+@.*)?$", line)
            if mm:
                sec.setdefault(mm.group(2).strip().lower(), mm.group(1))
        eds[m.group(1).strip().upper()] = sec
    lists = {}
    for key, fn in (("gc", "gamechangers.txt"), ("mld", "mass-land-denial.txt"), ("extra", "extra-turns.txt"),
                    ("chained", "chained-extra-turns.txt")):
        p = os.path.join(RES, "lists", fn)
        lists[key] = {l.strip().lower() for l in _read(p).splitlines() if l.strip() and not l.startswith("#")} if os.path.exists(p) else set()
    combos = []
    p = os.path.join(RES, "lists", "commander-bracket-combos.txt")
    if os.path.exists(p):
        for l in _read(p).splitlines():
            parts = [x.strip() for x in l.split("|")]
            if len(parts) >= 3 and parts[0] in ("early_game", "late_game"):
                combos.append((parts[0], frozenset(x.lower() for x in parts[1:] if x)))
    cube = {}
    p = os.path.join(RES, "draft", "rankings_cubecobra.txt")
    if os.path.exists(p):
        for l in _read(p).splitlines():
            m = re.match(r"#(\d+)\|([^|]+)\|", l)
            if m:
                cube.setdefault(m.group(2).strip().lower(), int(m.group(1)))
    data = {"cards": cards, "eds": eds, "lists": lists, "combos": combos, "cube": cube}
    pickle.dump(data, open(CACHE, "wb"))
    return data


def mana_value(cost):
    if not cost or cost == "no cost":
        return 0
    mv = 0
    for sym in cost.split():
        if sym.isdigit():
            mv += int(sym)
        elif sym == "X":
            continue
        elif "/" in sym:  # hybrid: 2/W counts 2, W/U counts 1
            mv += 2 if sym.startswith("2/") else 1
        else:
            mv += 1
    return mv


def classify(c):
    """Category tags for one card, from its Forge script."""
    tags = set()
    types = c["types"].split()
    name = c["name"].lower()
    if "Land" in types:
        tags.add("land")
        tags.add("basic" if name in BASICS or name.startswith("snow-covered ") else "nonbasic")
        return tags
    if "Creature" in types:
        tags.add("creature")
    perm = any(t in types for t in ("Artifact", "Creature", "Enchantment", "Planeswalker", "Battle"))
    for kind, eff, rest in c["abil"]:
        tgt = "ValidTgts$" in rest
        if eff == "Mana" and kind == "AB" and perm:
            tags.add("ramp")
            m = re.search(r"Amount\$\s*(\d+)", rest)
            if c["cmc"] == 0 or (c["cmc"] <= 1 and m and int(m.group(1)) >= 2):
                tags.add("fast")
        if eff == "ChangeZone" and "Origin$ Library" in rest:
            ct = re.search(r"ChangeType\$\s*([^|]+)", rest)
            ct = ct.group(1).strip() if ct else "Card"
            land_only = bool(re.match(r"^(Land|Basic|Plains|Island|Swamp|Mountain|Forest|Card\.Basic)", ct))
            if land_only and "Destination$ Battlefield" in rest:
                tags.add("ramp")
            elif not land_only and "Remembered" not in ct and "Defined$" not in rest and "Self" not in ct \
                    and re.search(r"Destination\$\s*(Hand|Battlefield|Library)", rest):
                tags.add("tutor")
        if eff == "Draw":
            m = re.search(r"NumCards\$\s*(\w+)", rest)
            n = m.group(1) if m else "1"
            if (kind == "AB" and "Sac<1/CARDNAME>" not in rest) or not n.isdigit() or int(n) >= 2:
                tags.add("draw")
        if eff in ("Dig", "DigUntil") and "DestinationZone$ Hand" in rest and re.search(r"ChangeNum\$\s*([2-9]|All)", rest):
            tags.add("draw")
        if tgt and "Defined$ You" not in rest:
            if eff in ("Destroy", "Fight") or (eff == "DealDamage" and re.search(r"ValidTgts\$[^|]*(Creature|Any|Permanent|Planeswalker)", rest)):
                tags.add("removal")
            elif eff == "ChangeZone" and "Origin$ Battlefield" in rest and re.search(r"Destination\$\s*(Exile|Hand|Library|Graveyard)", rest) \
                    and re.search(r"ValidTgts\$[^|]*(Creature|Permanent|Artifact|Enchantment|Planeswalker|Card)", rest) and "YouCtrl" not in rest:
                tags.add("removal")
            elif eff == "Sacrifice" and re.search(r"ValidTgts\$[^|]*(Player|Opponent)", rest):
                tags.add("removal")
            elif eff == "Pump" and re.search(r"NumDef\$\s*-", rest):
                tags.add("removal")
            elif eff == "Counter":
                tags.add("counter")
        if eff in ("DestroyAll", "DamageAll", "SacrificeAll") or \
                (eff == "ChangeZoneAll" and "Origin$ Battlefield" in rest and "Creature" in rest) or \
                (eff == "PumpAll" and re.search(r"NumDef\$\s*-", rest)):
            tags.add("wipe")
    if any(k.startswith("Enchant") and "Creature" in k for k in c["kw"]) and \
            any(re.search(r"Mode\$\s*[^|]*CantAttack", s) for s in c["static"]):
        tags.add("removal")
    if any("AdjustLandPlays" in s for s in c["static"]):
        tags.add("ramp")
    if name in FAST_MANA:
        tags.add("fast")
    return tags


def rarity_of(data, name, ed):
    eds = data["eds"]
    n = name.lower()
    if ed and ed in eds and n in eds[ed]:
        return eds[ed][n]
    found = [v[n] for v in eds.values() if n in v]
    return collections.Counter(found).most_common(1)[0][0] if found else "?"


def card_power(data, c, tags, rarity):
    """0-100 power estimate: cube rank (raw power), mana efficiency, role, rarity, Game Changer, fast mana, tutor."""
    name = c["name"].lower()
    rank = data["cube"].get(name)
    cube = 1 - (rank - 1) / 4000 if rank else 0.0
    eff = max(0.0, min(1.0, (6 - c["cmc"]) / 5))
    role = 1.0 if tags & {"ramp", "draw", "removal", "wipe", "counter", "tutor"} else 0.0
    p = 35 * cube + 15 * eff + 15 * role + 15 * RARITY_WEIGHT.get(rarity, 0.3)
    p += 10 * (name in data["lists"]["gc"]) + 5 * ("fast" in tags) + 5 * ("tutor" in tags)
    return round(min(100.0, p), 1)


def rate(path, data, config):
    cards = data["cards"]
    sec = None
    entries = {"commander": [], "main": []}
    problems = []
    for line in _read(path).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            sec = line.strip("[]").lower()
            continue
        if sec not in entries:
            continue
        m = re.match(r"^(?:(\d+)\s+)?([^|]+?)(?:\|([^|]+))?(?:\|.*)?$", line)
        if m:
            entries[sec].append((int(m.group(1) or 1), m.group(2).strip(), (m.group(3) or "").strip().upper()))
    counts = collections.Counter()
    curve = collections.Counter()
    rarity = collections.Counter()
    mvs, powers, names = [], [], collections.Counter()
    flagged, unknown = [], []
    restricted = {x.lower() for x in config.get("restrictedCards", [])}
    banned_sets = set(config.get("restrictedEditions", []))
    for section in ("commander", "main"):
        for n, name, ed in entries[section]:
            c = cards.get(name.lower())
            if c is None:
                unknown.append(name)
                continue
            names[c["name"].lower()] += n
            if any(f in ("all", "random") for f in c["flags"]):
                flagged.append(c["name"])
            if c["name"].lower() in restricted or ed in banned_sets:
                problems.append("restricted in Concordia: " + c["name"])
            if section == "commander":
                continue
            tags = classify(c)
            r = rarity_of(data, c["name"], ed)
            for t in tags:
                counts[t] += n
            if "land" not in tags:
                rarity[r] += n
                mvs += [c["cmc"]] * n
                curve[min(c["cmc"], 7)] += n
                powers += [card_power(data, c, tags, r)] * n
    commanders = []
    for n, name, ed in entries["commander"]:
        c = cards.get(name.lower())
        if c:
            commanders.append({"name": c["name"], "mv": c["cmc"], "rarity": rarity_of(data, c["name"], ed),
                               "legendary_creature": "Legendary" in c["types"] and "Creature" in c["types"],
                               "power": card_power(data, c, classify(c), rarity_of(data, c["name"], ed))})
    total = sum(n for n, _, _ in entries["main"]) + sum(n for n, _, _ in entries["commander"])
    deck_names = set(names)
    gc = sorted(x for x in deck_names if x in data["lists"]["gc"])
    mld = sorted(x for x in deck_names if x in data["lists"]["mld"])
    extra = sorted(x for x in deck_names if x in data["lists"]["extra"])
    chained = sorted(x for x in deck_names if x in data["lists"]["chained"])
    combos = {"early_game": [], "late_game": []}
    for kind, pieces in data["combos"]:
        if pieces <= deck_names:
            combos[kind].append(" + ".join(sorted(pieces)))
    dupes = sorted(k for k, v in names.items() if v > 1 and k not in BASICS and not k.startswith("snow-covered "))
    if total != 100:
        problems.append("deck has %d cards, expected 100" % total)
    if len(commanders) != 1 or not all(c["legendary_creature"] for c in commanders):
        problems.append("needs exactly one legendary creature commander")
    if dupes:
        problems.append("not singleton: " + ", ".join(dupes))
    if flagged:
        problems.append("cards the AI can't play (AI:RemoveDeck): " + ", ".join(sorted(set(flagged))))
    if unknown:
        problems.append("unknown cards: " + ", ".join(unknown))
    return {
        "deck": os.path.relpath(path, REPO) if path.startswith(REPO) else path, "total": total,
        "commanders": commanders, "lands": counts["land"], "basic": counts["basic"], "nonbasic": counts["nonbasic"],
        "creatures": counts["creature"], "ramp": counts["ramp"], "fast": counts["fast"], "draw": counts["draw"],
        "removal": counts["removal"] + counts["counter"], "wipe": counts["wipe"], "tutor": counts["tutor"],
        "avg_mv": round(statistics.mean(mvs), 2) if mvs else 0.0,
        "curve": [curve[i] for i in range(8)], "rarity": {k: rarity[k] for k in "CURMS?" if rarity[k]},
        "power": round(statistics.mean(powers), 1) if powers else 0.0,
        "top_power": sorted(powers, reverse=True)[:10],
        "game_changers": gc, "mass_land_denial": mld, "extra_turns": extra, "chained_extra_turns": chained,
        "combos": combos, "problems": problems,
    }


def check_tier(r, tier, life=None):
    spec = TIERS[tier]
    out = []

    def rng(label, value, bounds, hard=False):
        lo, hi = bounds
        ok = (lo is None or value >= lo) and (hi is None or value <= hi)
        out.append(("PASS" if ok else ("FAIL" if hard else "WARN"), "%s %s (target %s-%s)" % (label, value, "" if lo is None else lo, "" if hi is None else hi)))

    for p in r["problems"]:
        out.append(("FAIL", p))
    if life is not None:
        rng("life", life, spec["life"], hard=True)
    for c in r["commanders"]:
        out.append(("PASS" if c["rarity"] in spec["commander_rarity"] else "FAIL",
                    "commander %s rarity %s (allowed %s)" % (c["name"], c["rarity"], "/".join(sorted(spec["commander_rarity"])))))
        rng("commander mana value", c["mv"], spec["commander_mv"])
    for key in ("lands", "creatures", "ramp", "fast", "draw", "removal", "wipe", "tutor", "avg_mv", "power"):
        rng(key, r[key], spec[key], hard=key in ("fast",))
    out.append(("PASS" if r["rarity"].get("R", 0) <= spec["max_rare"] else "WARN", "rares %d (max %d)" % (r["rarity"].get("R", 0), spec["max_rare"])))
    out.append(("PASS" if r["rarity"].get("M", 0) <= spec["max_mythic"] else "FAIL", "mythics %d (max %d)" % (r["rarity"].get("M", 0), spec["max_mythic"])))
    out.append(("PASS" if len(r["game_changers"]) <= spec["game_changers"] else "FAIL", "Game Changers %d (max %d) %s" % (len(r["game_changers"]), spec["game_changers"], r["game_changers"] or "")))
    out.append(("PASS" if len(r["mass_land_denial"]) <= spec["mld"] else "FAIL", "mass land denial %s" % (r["mass_land_denial"] or "none")))
    out.append(("PASS" if len(r["extra_turns"]) <= spec["extra_turns"] and not r["chained_extra_turns"] else "FAIL", "extra turns %s" % (r["extra_turns"] or "none")))
    early, late = r["combos"]["early_game"], r["combos"]["late_game"]
    combo_ok = not early and (spec["combos"] == "late" or not late)
    out.append(("PASS" if combo_ok else "FAIL", "two-card combos: early %s, late %s" % (early or "none", late or "none")))
    return out


def best_tier(r):
    scores = {}
    for t in TIERS:
        res = check_tier(r, t)
        scores[t] = (sum(1 for s, _ in res if s == "FAIL"), sum(1 for s, _ in res if s == "WARN"))
    return min(scores, key=lambda t: scores[t]), scores


def main(argv):
    tier = life = None
    as_json = False
    paths = []
    it = iter(argv)
    for a in it:
        if a == "--tier":
            tier = int(next(it))
        elif a == "--life":
            life = int(next(it))
        elif a == "--json":
            as_json = True
        else:
            paths += sorted(glob.glob(a)) or [a]
    if not paths:
        print(__doc__)
        return 2
    data = build_cache()
    config = json.load(open(CONFIG)) if os.path.exists(CONFIG) else {}
    failed = False
    for p in paths:
        r = rate(p, data, config)
        fit, scores = best_tier(r)
        r["best_tier"] = fit
        if tier:
            r["checks"] = check_tier(r, tier, life)
            failed |= any(s == "FAIL" for s, _ in r["checks"])
        if as_json:
            print(json.dumps(r))
            continue
        cm = ", ".join("%s (MV %s, %s)" % (c["name"], c["mv"], c["rarity"]) for c in r["commanders"])
        print("== %s" % r["deck"])
        print("  commander: %s   cards: %d" % (cm, r["total"]))
        print("  lands %d (basic %d)  creatures %d  ramp %d  fast %d  draw %d  removal %d  wipes %d  tutors %d" % (
            r["lands"], r["basic"], r["creatures"], r["ramp"], r["fast"], r["draw"], r["removal"], r["wipe"], r["tutor"]))
        print("  avg mana value %.2f  curve 0-7+: %s  rarity %s" % (r["avg_mv"], "-".join(map(str, r["curve"])), r["rarity"]))
        print("  power %.1f (top ten %s)" % (r["power"], r["top_power"]))
        print("  Game Changers %s  mass land denial %s  extra turns %s  combos early %d / late %d" % (
            r["game_changers"] or "none", r["mass_land_denial"] or "none", r["extra_turns"] or "none",
            len(r["combos"]["early_game"]), len(r["combos"]["late_game"])))
        print("  best fit: %s   (fails/warnings per tier: %s)" % (TIERS[fit]["name"], {t: s for t, s in scores.items()}))
        if tier:
            print("  checks for %s:" % TIERS[tier]["name"])
            for status, text in r["checks"]:
                print("    %-4s %s" % (status, text))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

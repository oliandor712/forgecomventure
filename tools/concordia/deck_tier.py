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
GOAL OF THE POWER SCORER: the EDHREC rank and the cube ranking are a crutch, not the target. The scorer's own opinion (what the
card does: roles, mana efficiency, rarity, tags) should approximate the EDHREC rank when the rank is controlled for, i.e. computed
without the cube/EDHREC/cEDH terms and compared with them. An exact match is not the goal; the goal is a 15% difference, the
same as the reader goals: a card's percentile in the independent opinion is within 15 points of its percentile in the EDHREC
rank, for 85% of non-land cards. Baseline 2026-10-26 (roles, efficiency, rarity alone): 35% of cards within 15 points, mean
difference 27 points. No check script yet; the independent terms need to grow.

Card roles come from the tag_run tags stored in deckgen/pool.pkl (tag_roles()); a card without tags falls back to the script rules in classify(). Treat counts as close, not exact.
"""
import collections, glob, json, math, os, pickle, re, statistics, sys
from tier_rules import TIERS, TIER_TABLE  # per-tier rules (one source of truth)
import tier_rules as tr

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

def _read(path):
    return open(path, encoding="utf-8", errors="replace").read()


def build_cache():
    # the cache is valid only if no card script is newer than it (the directory's own mtime misses edits to files inside subfolders:
    # unflagging a card with patches 002/003 left a stale cache that still treated the cards as AI:RemoveDeck:All)
    if os.path.exists(CACHE):
        newest = max((os.path.getmtime(os.path.join(r, f)) for r, _, fs in os.walk(os.path.join(RES, "cardsfolder")) for f in fs), default=0)
        if os.path.getmtime(CACHE) > newest:
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


def classify(c, ftags=None):
    """Category tags for one card. With ftags (tag_run.tags, the single tag source) the roles come from the tags (tag_roles);
    without them from the Forge script (fallback for a card with no tags)."""
    tags = set()
    types = c["types"].split()
    name = c["name"].lower()
    if "Land" in types:
        tags.add("land")
        tags.add("basic" if name in BASICS or name.startswith("snow-covered ") else "nonbasic")
        return tags
    if "Creature" in types:
        tags.add("creature")
    if ftags:
        return tags | tag_roles(c, ftags)
    perm = any(t in types for t in ("Artifact", "Creature", "Enchantment", "Planeswalker", "Battle"))
    for kind, eff, rest in c["abil"]:
        tgt = "ValidTgts$" in rest
        if eff == "AddTurn":
            tags.add("extra_turn")
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


REPEAT_TRIG = {"spell_cast", "upkeep", "attacks", "combat_damage", "end_step", "beginning_of_combat", "gain_life", "discard", "life_loss", "tap"}
_LANDISH = re.compile(r"^(basic_)?(land|forest|plains|island|swamp|mountain)|basic")
_NEG_PUMP = re.compile(r"^pump_amount:-[^/]+/-")


def tag_roles(c, ftags):
    """ramp / fast / draw / removal / wipe / counter / tutor / extra_turn from the card's tag_run tags (non-land cards).
    Same intent as the script rules in classify(): ramp = a permanent that makes mana (or a Treasure), or a spell that puts a land onto
    the battlefield; draw = 2+ cards, X, or repeatable (activated or a recurring trigger), not a one-off cantrip; removal = a targeted
    remove/burn/fight/-X/-X/edict/pacifism effect not aimed only at your own permanents; wipe = the same effect on all."""
    F = set(ftags)
    types = c["types"].split()
    perm = any(t in types for t in ("Artifact", "Creature", "Enchantment", "Planeswalker", "Battle"))
    has = lambda p: any(t.startswith(p) for t in F)
    val = lambda p: {t[len(p):] for t in F if t.startswith(p)}
    out = set()
    scopes = val("target_scope:")
    aimed = scopes != {"you_control"}              # not only at your own permanents
    ttype = val("target_type:")
    dmg = "damage" in F or bool(val("damage_amount:"))
    removes = bool(val("remove:")) or dmg or any(_NEG_PUMP.match(t) for t in F)
    targeted = any(t.startswith("target_count:") and t != "target_count:all" for t in F)
    # mana
    treasure = "token_make" in F and "token_type:treasure" in F and not scopes & {"opp_control", "each_opponent"}
    if perm and ("mana_source" in F or treasure):
        out.add("ramp")
        amt = [int(a) for a in val("mana_amount:") if a.isdigit()]
        if c["cmc"] == 0 or (c["cmc"] <= 1 and amt and max(amt) >= 2):
            out.add("fast")
    if "land_tutor" in F and val("tutor_dest:") & {"battlefield", "battlefield_tapped"}:
        out.add("ramp")
    if has("extra_land_drop"):
        out.add("ramp")
    if c["name"].lower() in FAST_MANA:
        out.add("fast")
    # draw
    if "draw" in F:
        n = val("draw_count:")
        big = "x" in n or any(a.isdigit() and int(a) >= 2 for a in n)
        trig = val("trigger:")
        repeat = bool(trig & REPEAT_TRIG) or bool(trig & {"etb", "dies", "leaves"} and "trigger_scope:self" not in F) or ("mana_source" not in F and bool(val("cost:") & {"tap", "mana", "discard", "life", "remove_counters", "return", "exile"}))
        if big or repeat:
            out.add("draw")
    # interaction
    if "counterspell" in F:
        out.add("counter")
    if "extra_turn" in F:
        out.add("extra_turn")
    if "tutor" in F and "land_tutor" not in F and val("tutor_dest:") & {"hand", "battlefield", "battlefield_tapped", "library"} and any(t and "remembered" not in t and "samename" not in t and not _LANDISH.search(t) for t in val("tutor_target:")):
        out.add("tutor")
    if removes and "target_count:all" in F and not targeted and (aimed or dmg):
        if ttype & {"creature", "permanent", "any", "land", "artifact", "enchantment"}:
            out.add("wipe")
    elif removes and targeted and not (ttype == {"card"} and "from_zone:graveyard" in F):
        # remove:/-X/-X must not be aimed only at your own permanents; damage names its source in target_scope, so it only needs a creature/any/planeswalker/permanent target
        if ((val("remove:") or any(_NEG_PUMP.match(t) for t in F)) and aimed) or (dmg and ttype & {"creature", "any", "planeswalker", "battle", "permanent"}):
            out.add("removal")
    if "fight" in F and targeted:
        out.add("removal")
    if "effect:sacrifice" in F and ttype & {"player", "opponent"} and val("sacrifice_type:"):
        out.add("removal")
    if val("restrict_kind:") & {"cant_attack", "cant_attack_or_block"} and "affected_filter:enchantedby" in F and "creature" in val("affected_type:"):
        out.add("removal")
    return out


PRIMARY = ("Creature", "Planeswalker", "Battle", "Instant", "Sorcery", "Artifact", "Enchantment")


def primary_type(c):
    """The type Moxfield groups a card under: creature first, then planeswalker, battle, instant, sorcery, artifact."""
    types = c["types"].split()
    return next((t for t in PRIMARY if t in types), "Other")


def source_colors(c):
    """Colours a land can make, from its mana abilities, basic land types and fetch targets."""
    cols = set()
    types = c["types"].split()
    for col, basic in zip("WUBRG", ("Plains", "Island", "Swamp", "Mountain", "Forest")):
        if basic in types or c["name"] == basic:
            cols.add(col)
    for kind, eff, rest in c["abil"]:
        if eff == "Mana":
            m = re.search(r"Produced\$\s*([^|]+)", rest)
            prod = m.group(1) if m else ""
            if "Any" in prod or "Combo" in prod and "Any" in rest:
                cols |= set("WUBRG")
            cols |= set(re.findall(r"[WUBRG]", prod.replace("Combo", "")))
        if eff == "ChangeZone" and "Origin$ Library" in rest:
            for col, basic in zip("WUBRG", ("Plains", "Island", "Swamp", "Mountain", "Forest")):
                if basic in rest or "Basic" in rest or "Land" in rest.split("ChangeType$")[-1][:12]:
                    cols.add(col)
    if "Command Tower" == c["name"] or "Exotic Orchard" == c["name"]:
        cols |= set("WUBRG")
    return cols


def rarity_of(data, name, ed):
    eds = data["eds"]
    n = name.lower()
    if ed and ed in eds and n in eds[ed]:
        return eds[ed][n]
    found = [v[n] for v in eds.values() if n in v]
    return collections.Counter(found).most_common(1)[0][0] if found else "?"


SIGNALS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deckgen", "spellbinder", "signals.json")
CEDH_FULL = 0.4  # a card in 40% of the cEDH decks that could play it counts as top raw power
_signals = None


def color_identity(c):
    """Colours in the mana cost and in mana symbols of the rules text (reminder text skipped)."""
    s = set(re.findall(r"[WUBRG]", c["mc"]))
    for sym in re.findall(r"\{([^}]*)\}", re.sub(r"\([^)]*\)", "", c["oracle"])):
        s |= set(re.findall(r"[WUBRG]", sym))
    return frozenset(s)


def cedh_strength(c):
    """0-1 from the card's Spellbinder cEDH inclusion rate (deckgen/spellbinder_signals.py), or None when there's no
    signals file or too few cEDH decks could play the card's colours to say."""
    global _signals
    if _signals is None:
        _signals = {}
        if os.path.exists(SIGNALS):
            s = json.load(open(SIGNALS))
            _signals = {"cards": s["cards"], "min": s.get("min_eligible", 5),
                        "ids": [(frozenset(i), n) for i, n in s["sources"].get("cedh", {}).get("identities", {}).items()]}
    if not _signals or not _signals["ids"]:
        return None
    ci = color_identity(c)
    if sum(n for i, n in _signals["ids"] if ci <= i) < _signals["min"]:
        return None
    return min(1.0, _signals["cards"].get(c["name"].lower().split(" // ")[0], {}).get("cedh", 0.0) / CEDH_FULL)


STAPLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deckgen", "staples.json")
_cat = None


def category(name):
    """'staple', 'game_changer', 'watch' or '' from deckgen/staples.py's output (deckgen/staples.json)."""
    global _cat
    if _cat is None:
        _cat = {k: v["category"] for k, v in json.load(open(STAPLES)).items()} if os.path.exists(STAPLES) else {}
    return _cat.get(name.lower(), "")


SCRYFALL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deckgen", "scryfall", "cards.json")
NICHE_ROLE = 0.5   # share of the role term a niche:* card keeps (tag_run.py: pays only in a matching deck)
EDH_LIFT = 0.6     # raw power an EDHREC rank alone can lift a card to (popularity is not pure strength)
_edh = None


def edhrec(c):
    """0-1 popularity from the card's EDHREC rank in Scryfall's data (deckgen/scryfall_bulk.py): 1 for rank 1, about
    0.65 for rank 35, 0.3 for rank 1500, 0 past rank 30000 or with no data."""
    global _edh
    if _edh is None:
        import gzip
        _edh = {}
        for p in (SCRYFALL, SCRYFALL + ".gz"):
            if os.path.exists(p):
                d = json.load(gzip.open(p, "rt") if p.endswith(".gz") else open(p))
                _edh = {k: v.get("edhrec_rank") for k, v in d.items() if v.get("edhrec_rank")}
                break
    r = _edh.get(c["name"].lower().split(" // ")[0])
    return max(0.0, 1 - math.log10(r) / math.log10(30000)) if r else 0.0


_dp = None
DECKS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deckgen", "external", "decks.json")


def deckpop(c):
    """0-1 popularity from the collected decklists (deckgen/collect_decks.py: precons plus the most viewed Archidekt decks per
    bracket): the share of those decks running the card, 1 at 30% or more, square-root curve. 0 when the file is missing."""
    global _dp
    if _dp is None:
        _dp = {}
        if os.path.exists(DECKS_JSON):
            ds = [x for x in json.load(open(DECKS_JSON, encoding="utf-8"))["decks"] if x["source"] != "edhrec"]
            cnt = collections.Counter(k for x in ds for k in {n.lower().split(" // ")[0] for n in set(x["cards"]) | set(x["commanders"])})   # keyed by front face, like the lookup below (split/adventure/MDFC cards)
            _dp = {k: min(1.0, v / (0.30 * len(ds))) ** 0.5 for k, v in cnt.items()} if ds else {}
    return _dp.get(c["name"].lower().split(" // ")[0], 0.0)


def inputs_status():
    """The external popularity inputs of card_power and whether each is present: {name: size in bytes or None}. They are not
    committed, so power numbers differ between machines that lack one; pool.py records this next to pool.pkl and card_power warns."""
    ps = {"scryfall/cards.json": [SCRYFALL, SCRYFALL + ".gz"], "external/decks.json": [DECKS_JSON], "spellbinder/signals.json": [SIGNALS]}
    return {k: next((os.path.getsize(p) for p in v if os.path.exists(p)), None) for k, v in ps.items()}


_warned = False


def _warn_inputs():
    global _warned
    if not _warned:
        _warned = True
        miss = [k for k, v in inputs_status().items() if v is None]
        if miss:
            print("WARNING deck_tier.card_power: missing input(s) %s; popularity/cEDH terms count as 0, power numbers are not comparable "
                  "with tier_table.json" % ", ".join(miss), file=sys.stderr)


POOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deckgen", "pool.pkl")
_poolf = None


def _warn_pool_stale():
    """One warning when pool.pkl was built from other tagger files than the current ones (pool_meta.json fingerprint vs tag_version.stamp())."""
    try:
        sys.path.insert(0, os.path.dirname(POOL))
        import tag_version
        fp = json.load(open(os.path.join(os.path.dirname(POOL), "pool_meta.json"))).get("fingerprint", {})
        import pool as _p      # same staples hash pool.py stores, so a staples.json edit is caught too
        if fp.get("tags") != tag_version.stamp() or fp.get("staples") != _p._h(STAPLES): print("WARNING deck_tier: pool.pkl is older than the tagger files (run deckgen/pool.py --if-stale); roles and categories may be stale", file=sys.stderr)
    except (OSError, ValueError, ImportError): pass


def ftags_of(name):
    """The card's tag_run tags (ftags) as stored in deckgen/pool.pkl; () when there is no pool or the card is not in it."""
    global _poolf
    if _poolf is None:
        _poolf = {}
        if not os.path.exists(POOL): print("WARNING deck_tier: no deckgen/pool.pkl, tags fall back to script rules (run deckgen/pool.py)", file=sys.stderr)
        else:
            _warn_pool_stale()
            _poolf = {k: tuple(v.get("ftags", ())) for k, v in pickle.load(open(POOL, "rb")).items()}
    return _poolf.get(name.lower(), ())


def mech_of(name):
    """Tuple of the card's mech:* tags from deckgen/pool.pkl; () when there is no pool."""
    return tuple(t for t in ftags_of(name) if t.startswith("mech:"))


def niche_of(name):
    """Tuple of the card's niche:* tags from deckgen/pool.pkl (the tag_run tags pool.py stored); () when there is no pool.
    rate() uses it so a deck's power matches the pool's card power."""
    return tuple(t for t in ftags_of(name) if t.startswith("niche:"))


def tags_of(c):
    """classify() with the card's stored tags (roles from tags); script roles only for a card the pool has no tags for."""
    return classify(c, ftags_of(c["name"]) or None)


def effective_cmc(c):
    """Mana value as the card is really paid for, used by the efficiency term only (curve and fast-mana checks keep the printed value).
    Alternative cost on the spell itself (Force of Will, Snuff Out): only its mana, so a free-to-cast spell counts as 0 (user 2026-10-26).
    Self cost reducers (Delve, Convoke, Improvise, Affinity, ReduceCost on Card.Self): minus 2. X in the cost: plus 1 (user 2026-10-26)."""
    mv = c["cmc"]
    best = mv
    for st in c["static"]:
        if "Mode$ AlternativeCost" in st and "ValidSA$ Spell.Self" in st:
            m = re.search(r"\bCost\$ ([^|]*)", st)
            if not m:
                continue
            mana = sum(mana_value(p) for p in m.group(1).split() if re.fullmatch(r"[0-9WUBRGXC]+", p) and not p.startswith("X"))
            best = min(best, mana)
        elif "Mode$ ReduceCost" in st and "ValidCard$ Card.Self" in st:
            best = min(best, max(0, mv - 2))
    if any(k.split(":")[0] in ("Delve", "Convoke", "Improvise", "Affinity") for k in c["kw"]):
        best = min(best, max(0, mv - 2))
    if "X" in c["mc"].split():
        best += 1
    return best


def card_power(data, c, tags, rarity, ftags=()):
    """Power for one rarity; see card_powers."""
    return card_powers(data, c, tags, (rarity,), ftags)[rarity]


def card_powers(data, c, tags, rarities, ftags=()):
    """{rarity: power}; the rarity-independent terms are computed once. ftags (tag_run.tags, optional) halves the role term
    of a niche card (Disenchant, Stone Rain: the effect only pays in a matching deck)."""
    """0-100 power estimate: raw power, mana efficiency, role, rarity, Game Changer, fast mana, tutor.
    40 raw + 15 efficiency (effective_cmc: alternative costs, self cost reducers, X spells) + 15 role + 10 rarity + 10 Game Changer + 5 fast + 5 tutor.
    Popularity counts once, inside raw power (the EDHREC lift below); it is not added again here or in the builder's score.
    Raw power is the cube rank, lifted by the cEDH inclusion rate or by EDHREC popularity (up to EDH_LIFT) when those
    are higher: the cube list misses most casual cards (Birds of Paradise isn't in it). A missing signal never lowers a
    card. Prices are not used (docs/Adventure/Campaign/DECK_REVIEW_SPELLBINDER.md)."""
    _warn_inputs()
    name = c["name"].lower()
    rank = data["cube"].get(name)
    cube = 1 - (rank - 1) / 4000 if rank else 0.0
    pop = max(edhrec(c), deckpop(c))
    cube = max(cube, cedh_strength(c) or 0.0, EDH_LIFT * pop)
    eff = max(0.0, min(1.0, (6 - effective_cmc(c)) / 5))
    role = 1.0 if tags & {"ramp", "draw", "removal", "wipe", "counter", "tutor"} else 0.0
    if any(t.startswith("niche:") for t in ftags): role *= NICHE_ROLE
    base = 40 * cube + 15 * eff + 15 * role + 10 * (name in data["lists"]["gc"]) + 5 * ("fast" in tags) + 5 * ("tutor" in tags)
    return {r: round(min(100.0, base + 10 * RARITY_WEIGHT.get(r, 0.3)), 1) for r in rarities}


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
    ptypes = collections.Counter()
    pips = collections.Counter()
    sources = collections.Counter()
    cheap_ramp_draw = 0
    extra_turn_names = set()
    restricted = {x.lower() for x in config.get("restrictedCards", [])}
    banned_sets = set(config.get("restrictedEditions", []))
    for section in ("commander", "main"):
        for n, name, ed in entries[section]:
            c = cards.get(name.lower())
            if c is None:
                unknown.append(name)
                continue
            names[c["name"].lower()] += n
            if "all" in c["flags"]:  # AI:RemoveDeck:All (Random only affects random deck generators)
                flagged.append(c["name"])
            if c["name"].lower() in restricted or ed in banned_sets:
                problems.append("restricted in Concordia: " + c["name"])
            if section == "commander":
                continue
            tags = tags_of(c)
            if "extra_turn" in tags:
                extra_turn_names.add(c["name"].lower())
            r = rarity_of(data, c["name"], ed)
            for t in tags:
                counts[t] += n
            if "land" in tags:
                for col in source_colors(c):
                    sources[col] += n
            if "land" not in tags:
                ptypes[primary_type(c)] += n
                for col in "WUBRG":
                    pips[col] += c["mc"].count(col) * n
                if tags & {"ramp", "draw"} and c["cmc"] <= 3:
                    cheap_ramp_draw += n
                rarity[r] += n
                mvs += [c["cmc"]] * n
                curve[min(c["cmc"], 7)] += n
                powers += [card_power(data, c, tags, r, niche_of(c["name"]))] * n
            elif c["name"].lower() not in BASICS and not c["name"].lower().startswith("snow-covered "):
                powers += [card_power(data, c, tags, r, niche_of(c["name"]))] * n   # nonbasic lands count toward deck power (user 2026-10-26)
    commanders = []
    for n, name, ed in entries["commander"]:
        c = cards.get(name.lower())
        if c:
            commanders.append({"name": c["name"], "mv": c["cmc"], "rarity": rarity_of(data, c["name"], ed),
                               "legendary_creature": "Legendary" in c["types"] and "Creature" in c["types"],
                               "colours": len(color_identity(c)),
                               "power": card_power(data, c, tags_of(c), rarity_of(data, c["name"], ed), niche_of(c["name"]))})
    total = sum(n for n, _, _ in entries["main"]) + sum(n for n, _, _ in entries["commander"])
    deck_names = set(names)
    gc = sorted(x for x in deck_names if x in data["lists"]["gc"])
    staples = sorted(x for x in deck_names if category(x) == "staple")
    watch = sorted(x for x in deck_names if category(x) == "watch")
    mld = sorted(x for x in deck_names if x in data["lists"]["mld"])
    extra = sorted(x for x in deck_names if x in data["lists"]["extra"] or x in extra_turn_names)
    chained = sorted(x for x in deck_names if x in data["lists"]["chained"])
    mech = sorted("%s (%s)" % (x, t[5:]) for x in deck_names for t in mech_of(x) if tr.MECH_MIN_TIER.get(t[5:], 1) > 1)
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
        "premium50": sum(1 for p in powers if p >= 50), "premium70": sum(1 for p in powers if p >= 70),
        "game_changers": gc, "staples": staples, "watch": watch, "mass_land_denial": mld, "extra_turns": extra, "chained_extra_turns": chained, "mech": mech,
        "combos": combos, "problems": problems,
        "types": dict(ptypes), "pips": {k: v for k, v in pips.items() if v}, "sources": dict(sources),
        "karsten_lands": round(31.4 + 3.13 * (statistics.mean(mvs) if mvs else 0) - 0.28 * cheap_ramp_draw, 1),
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
        if spec["commander_mv"] != (None, None):  # tier 1 has no mana value requirement
            rng("commander mana value", c["mv"], spec["commander_mv"])
        if spec.get("commander_colours"):
            out.append(("PASS" if c["colours"] == spec["commander_colours"] else "WARN",
                        "commander %s colour identity %d (allowed %d)" % (c["name"], c["colours"], spec["commander_colours"])))
    for key in ("lands", "creatures", "ramp", "fast", "draw", "removal", "wipe", "tutor", "avg_mv", "power"):
        rng(key, r[key], spec[key], hard=key in ("fast",))
    if "max_uncommon" in spec:
        out.append(("PASS" if r["rarity"].get("U", 0) <= spec["max_uncommon"] else "FAIL", "uncommons %d (max %d)" % (r["rarity"].get("U", 0), spec["max_uncommon"])))
    curve = r["curve"]
    buckets = {1: curve[0] + curve[1], 2: curve[2], 3: curve[3], 4: curve[4], 5: curve[5], 6: curve[6] + curve[7]}
    off = ["%s%s: %d (%d-%d)" % (k, "+" if k == 6 else "", buckets[k], lo, hi) for k, (lo, hi) in spec["curve"].items() if not lo <= buckets[k] <= hi]
    out.append(("PASS" if not off else "WARN", "mana curve by mana value %s" % ("in range" if not off else ", ".join(off))))
    t = r["types"]
    nonland = sum(t.values()) or 1
    need = []
    for key, n in spec["types"].items():
        have = nonland - t.get("Creature", 0) if key == "noncreature" else sum(t.get(x, 0) for x in key.split("+"))
        if have < n:
            need.append("%s %d (min %d)" % (key, have, n))
    top, share = max(t.items(), key=lambda kv: kv[1]) if t else ("-", 0)
    if share / nonland > spec["max_type_share"]:
        need.append("%s is %d%% of nonland cards (max %d%%)" % (top, round(100 * share / nonland), round(100 * spec["max_type_share"])))
    out.append(("PASS" if not need else "WARN", "card types %s%s" % (" ".join("%s %d" % kv for kv in sorted(t.items(), key=lambda kv: -kv[1])), "" if not need else " - " + "; ".join(need))))
    if spec["karsten"] is not None:
        diff = r["lands"] - r["karsten_lands"]
        out.append(("PASS" if abs(diff) <= spec["karsten"] else "WARN", "lands %d vs Karsten estimate %.1f (allowed +/-%d)" % (r["lands"], r["karsten_lands"], spec["karsten"])))
    pips_total = sum(r["pips"].values())
    if len(r["pips"]) > 1:
        low = []
        for col, n in r["pips"].items():
            src = r["sources"].get(col, 0)
            if src < 14 or src / max(1, r["lands"]) < 0.8 * n / pips_total:
                low.append("%s %d sources for %d%% of pips" % (col, src, round(100 * n / pips_total)))
        out.append(("PASS" if not low else "WARN", "colour sources %s%s" % (r["sources"], "" if not low else " - low: " + "; ".join(low))))
    for key, floor in (("premium50", 50), ("premium70", 70)):
        if key in spec:
            rng("power-%d+ cards" % floor, r[key], spec[key])
    out.append(("PASS" if len(r["watch"]) <= spec["watch"] else "WARN", "watch-list cards %d (max %d) %s" % (len(r["watch"]), spec["watch"], r["watch"] or "")))
    rng("staples", len(r["staples"]), spec["staples"])
    out.append(("PASS" if len(r["game_changers"]) <= spec["game_changers"] else "FAIL", "Game Changers %d (max %d) %s" % (len(r["game_changers"]), spec["game_changers"], r["game_changers"] or "")))
    out.append(("PASS" if len(r["mass_land_denial"]) <= spec["mld"] else "FAIL", "mass land denial %s" % (r["mass_land_denial"] or "none")))
    out.append(("PASS" if len(r["extra_turns"]) <= spec["extra_turns"] and not r["chained_extra_turns"] else "FAIL", "extra turns %s" % (r["extra_turns"] or "none")))
    if os.path.exists(POOL):   # mech:* tier minimums (tier_rules.MECH_MIN_TIER); needs deckgen/pool.pkl for the card tags
        bad = [m for m in r["mech"] if tr.MECH_MIN_TIER.get(m[m.rindex("(") + 1:-1], 1) > tier]
        out.append(("PASS" if not bad else "FAIL", "mechanics above this tier %s" % (bad or "none")))
    else:
        out.append(("WARN", "mechanics tier check skipped: deckgen/pool.pkl missing"))
    early, late = r["combos"]["early_game"], r["combos"]["late_game"]
    combo_ok = not early and (spec["combos"] == "late" or not late)
    out.append(("PASS" if combo_ok else "FAIL", "two-card combos: early %s, late %s" % (early or "none", late or "none")))
    return out


def archetype_checks(path, r, tier):
    """WARN lines for the deck's archetype window (archetype_rules.py): creatures, instants+sorceries, enchantments. Tier 1 only for now."""
    if tier != 1:
        return []
    import archetype_rules as ar
    c = ar.classify(path, tier)
    lo, hi = ar.creature_check(tier, c["archetype"], c["sub"], c["reach"])  # same band as archetype_rules --report
    _, _, isx, ench, _ = ar.windows(tier, c["archetype"], c["sub"], c["reach"])
    label = c["archetype"] + ("/" + c["sub"] if c["sub"] else "")
    out = [("PASS" if lo <= r["creatures"] <= hi else "WARN", "archetype %s: creatures %d (window %d-%d)" % (label, r["creatures"], lo, hi))]
    out.append(("PASS" if c["instant_sorcery"] >= isx else "WARN", "archetype %s: instants+sorceries %d (min %d)" % (label, c["instant_sorcery"], isx)))
    out.append(("PASS" if c["enchantments"] >= ench else "WARN", "archetype %s: enchantments %d (min %d)" % (label, c["enchantments"], ench)))
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
            r["checks"] = check_tier(r, tier, life) + archetype_checks(p, r, tier)
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
        print("  staples %d  watch-list cards %s" % (len(r["staples"]), r["watch"] or "none"))
        print("  Game Changers %s  mass land denial %s  extra turns %s  combos early %d / late %d" % (
            r["game_changers"] or "none", r["mass_land_denial"] or "none", r["extra_turns"] or "none",
            len(r["combos"]["early_game"]), len(r["combos"]["late_game"])))
        print("  card types %s   colour pips %s   sources %s   Karsten lands %.1f" % (r["types"], r["pips"], r["sources"], r["karsten_lands"]))
        print("  best fit: %s   (fails/warnings per tier: %s)" % (TIERS[fit]["name"], {t: s for t, s in scores.items()}))
        if tier:
            print("  checks for %s (Commander Bracket %d):" % (TIERS[tier]["name"], TIERS[tier]["bracket"]))
            for status, text in r["checks"]:
                print("    %-4s %s" % (status, text))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Archetype, subarchetype and card-type quota rules for Concordia decks (user decisions 2026-10-21).

Archetype (tier 1 only; tiers 2-5 keep build_queue's old rule):
  tokens  12+ token makers or "creatures you control get/have" cards
  tribal  the deck's top creature type has 12+ creatures AND the commander's text names that type (Human excluded: too broad)
  aggro   everything else
Interaction is not an archetype. It is a flexibility mark: `reach` = number of removal classes the deck can answer,
in the user's priority order creature, artifact, enchantment, land, token (damage to creature or any target counts as token removal).
Subarchetype (a second label, never a simulation cell):
  low-control  reach 2+ with a creature answer, or any pacify / restrict / tax permanent; a card tagged scales:X counts only with SCALE_NEED X in the deck
  low-aggro    aggro with 9+ non-creature artifacts
  low-tribal / low-tokens   4+ enchantments (tribal / tokens)
A `low-*` deck shifts its primary type (creatures) down 2-4 and a secondary type up 2-4 (SHIFT).
Usage: python3 archetype_rules.py DECK.dck [...]   prints the classification as TOON-like rows."""
import os, re, sys, collections, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
CARDS = os.path.join(ROOT, "forge-gui/res/cardsfolder")
TOKENS_MIN = 12
TRIBE_MIN = 12
LOW_ARTIFACT_MIN = 9
LOW_ENCHANT_MIN = 4
SCALE_NEED = 5  # enchantments (or other X) a "number of X you control" control card needs before it counts as control
REMOVAL_CLASSES = ("creature", "artifact", "enchantment", "land", "token")  # user's priority list, highest first
SKIP_TYPES = {"Creature", "Artifact", "Enchantment", "Legendary", "Snow", "Tribal", "Kindred", "Instant", "Sorcery", "Land"}

# Creature windows (min, max) by tier and archetype; control only exists at tiers 2-5. Ramp and midrange keep the tier range.
CREATURES = {
    1: {"aggro": (33, 36), "tribal": (31, 34), "tokens": (29, 32)},
    2: {"aggro": (33, 36), "tribal": (31, 34), "tokens": (29, 32), "control": (26, 28)},
    3: {"aggro": (32, 36), "tribal": (30, 34), "tokens": (28, 32), "control": (22, 26)},
    4: {"aggro": (32, 36), "tribal": (30, 34), "tokens": (28, 32), "control": (22, 26)},
    5: {"aggro": (30, 34), "tribal": (28, 32), "tokens": (26, 30), "control": (20, 24)},
}
# Minimum instants+sorceries and enchantments by tier and archetype (artifacts: unchanged, tried first as cheap alternates)
INSTANT_SORCERY = {1: {"tokens": 12, "aggro": 10, "tribal": 8}, 2: {"control": 13, "tokens": 11, "aggro": 9, "tribal": 7},
                   3: {"control": 14, "tokens": 12, "aggro": 10, "tribal": 8}, 4: {"control": 14, "tokens": 12, "aggro": 10, "tribal": 8},
                   5: {"control": 14, "tokens": 12, "aggro": 10, "tribal": 8}}
ENCHANTMENT = {1: {"tokens": 4, "tribal": 2, "aggro": 1}, 2: {"tokens": 6, "control": 5, "tribal": 4, "aggro": 3},
               3: {"tokens": 5, "control": 4, "tribal": 3, "aggro": 2}, 4: {"tokens": 5, "control": 4, "tribal": 3, "aggro": 2},
               5: {"tokens": 5, "control": 4, "tribal": 3, "aggro": 2}}
CREATURE_FLOOR = {1: 26, 2: 26, 3: 16, 4: 14, 5: 12}  # deck_tier.py hard minimum per tier
# low-* shift: (primary down, secondary up) in 2..4; reach 2 uses 2, reach 3 uses 3, reach 4+ uses 4
SECONDARY = {"low-control": "instant_sorcery", "low-aggro": "artifact", "low-tribal": "enchantment", "low-tokens": "enchantment"}
LAND_RANGE = {1: (40, 46), 2: (36, 39), 3: (33, 38), 4: (33, 37), 5: (31, 37)}  # deck_tier.py land range per tier


def shift_for(reach):
    return 2 if reach <= 2 else 3 if reach == 3 else 4


def windows(tier, archetype, sub=None, reach=2):
    """(creature min, creature max, instant+sorcery min, enchantment min, artifact bonus) for a deck target."""
    lo, hi = CREATURES.get(tier, {}).get(archetype, (CREATURE_FLOOR[tier], 99))
    isx = INSTANT_SORCERY.get(tier, {}).get(archetype, 0)
    ench = ENCHANTMENT.get(tier, {}).get(archetype, 0)
    art = 0
    if sub:
        d = shift_for(reach)
        lo, hi = max(CREATURE_FLOOR[tier], lo - d), max(CREATURE_FLOOR[tier], hi - d)
        sec = SECONDARY[sub]
        if sec == "instant_sorcery": isx += d
        elif sec == "enchantment": ench += d
        elif sec == "artifact": art += d
    return lo, hi, isx, ench, art


def card_file(name):
    f = os.path.join(CARDS, name[0].lower(), re.sub(r"[^a-z0-9_]", "", name.lower().replace(" ", "_").replace("-", "_")) + ".txt")
    return open(f, errors="replace").read() if os.path.exists(f) else ""


def types_of(t):
    m = re.search(r"^Types:(.*)$", t, re.M)
    return m.group(1).split() if m else []


def removal_classes(t, ty):
    """Removal classes one non-creature card can answer."""
    out = set()
    for ln in t.splitlines():
        if "$" not in ln or "ValidTgts" not in ln or "Defined$ You" in ln: continue
        if not re.search(r"\$ (Destroy|DealDamage|Fight|ChangeZone|Pump|Tap|Sacrifice|Counter)\b", ln): continue
        if re.search(r"\$ ChangeZone\b", ln) and not ("Origin$ Battlefield" in ln and "YouCtrl" not in ln): continue
        if re.search(r"\$ Pump\b", ln) and not re.search(r"NumDef\$ -", ln): continue
        if re.search(r"\$ DealDamage", ln) and not re.search(r"ValidTgts\$[^|]*(Creature|Any|Permanent|Planeswalker)", ln): continue
        v = re.search(r"ValidTgts\$ ?([^|]*)", ln).group(1)
        if re.search(r"Creature|Any|Permanent|Planeswalker", v): out.add("creature")
        if re.search(r"Artifact|Permanent", v): out.add("artifact")
        if re.search(r"Enchantment|Permanent", v): out.add("enchantment")
        if re.search(r"Land|Permanent", v): out.add("land")
        if re.search(r"Token", v): out.add("token")
        if re.search(r"\$ DealDamage", ln) and re.search(r"Creature|Any", v): out.add("token")  # user 2026-10-21
    if re.search(r"^K:Enchant creature", t, re.M) and re.search(r"CantAttack|CantBlock", t): out.add("creature")
    return out


def control_signal(t, ty):
    """(signals, scales) for a non-creature artifact or enchantment: pacify, restrict, tax; scales = X in 'number of X you control'."""
    kind = set(ty) & {"Enchantment", "Artifact"}
    if not kind or "Creature" in ty or "Land" in ty: return set(), set()
    st = [l for l in t.splitlines() if l.startswith("S:")]
    o = set()
    if re.search(r"^K:Enchant creature", t, re.M) and any(re.search(r"CantAttack|CantBlock|DoesntUntap", l) for l in st): o.add("pacify")
    if any(re.search(r"Mode\$ (CantAttack|CantBlock|CantBeCast|CantPlayLand|CantDraw|CantGainLife|CantBeActivated|CantTarget|CantSacrifice)", l)
           and not re.search(r"ValidCard\$ Card\.Self|EnchantedBy|EquippedBy", l) for l in st): o.add("restrict")
    if any("RaiseCost" in l for l in st): o.add("tax")
    scales = set()
    if o:
        for mm in re.finditer(r"Count\$Valid\s+([A-Za-z.,+ ]+?)(?:\.YouCtrl|/|\n|\|)", t):
            scales.add(mm.group(1).split(".")[0])
    return o, scales


def read_deck(path):
    sec, main, cmd = None, [], []
    for ln in open(path, errors="replace"):
        ln = ln.strip()
        if ln.startswith("["): sec = ln; continue
        m = re.match(r"(\d+) ([^|]+)", ln)
        if not m: continue
        (main if sec == "[Main]" else cmd if sec == "[Commander]" else []).append((int(m.group(1)), m.group(2).strip()))
    return main, cmd


def classify(path, tier=None):
    """Classification of one deck: archetype, sub, reach, counts. Tier is read from the path when not given."""
    if tier is None:
        m = re.search(r"tier(\d)", path.replace(os.sep, "/")); tier = int(m.group(1)) if m else 1
    main, cmd = read_deck(path)
    tribes, tokens, art, ench, isx, creatures = collections.Counter(), 0, 0, 0, 0, 0
    classes, lock, scaling = collections.Counter(), 0, []
    for q, name in main:
        t = card_file(name)
        if not t or "Types:Land" in t: continue
        ty = types_of(t)
        if "Creature" in ty:
            creatures += q
            for x in ty:
                if x not in SKIP_TYPES: tribes[x] += q
        if re.search(r"^A:(SP|AB)\$ Token|^SVar:TrigToken", t, re.M) or "TokenScript$" in t or re.search(r"creatures you control (get|have)", t): tokens += q
        if "Creature" not in ty:
            if "Artifact" in ty: art += q
            if "Enchantment" in ty: ench += q
            if "Instant" in ty or "Sorcery" in ty: isx += q
            for c in removal_classes(t, ty): classes[c] += q
            sig, sc = control_signal(t, ty)
            if sig:
                if "pacify" in sig: classes["creature"] += q
                if sig & {"restrict", "tax"}:
                    if sc: scaling.append((name, sorted(sc), q))
                    else: lock += q
    cmd_text = " ".join(" ".join(re.findall(r"^(?:Oracle|Types):(.*)$", card_file(n), re.M)) for _, n in cmd).lower()
    top, n = tribes.most_common(1)[0] if tribes else ("-", 0)
    tribal = n >= TRIBE_MIN and top != "Human" and top.lower() in cmd_text
    arch = "tokens" if tokens >= TOKENS_MIN else "tribal" if tribal else "aggro"
    have = {"Enchantment": ench, "Artifact": art, "Creature": creatures}
    for name, sc, q in scaling:  # a "number of X you control" lock card counts only with enough X
        if any(have.get(x.split()[0], 0) >= SCALE_NEED for x in sc): lock += q
    reach = sum(1 for c in REMOVAL_CLASSES if classes[c] >= 1) + (1 if lock else 0)
    sub = None
    if lock or (reach >= 2 and classes["creature"] >= 1): sub = "low-control"
    elif arch == "aggro" and art >= LOW_ARTIFACT_MIN: sub = "low-aggro"
    elif arch in ("tribal", "tokens") and ench >= LOW_ENCHANT_MIN: sub = "low-" + arch
    return dict(tier=tier, archetype=arch, sub=sub, reach=reach, creatures=creatures, tokens=tokens, top_tribe=top, top_tribe_n=n,
                artifacts=art, enchantments=ench, instant_sorcery=isx, classes=dict(classes))


def report(tier=1):
    """Decks outside their archetype window (creatures, instants+sorceries, enchantments); read-only, for the rebuild approval list."""
    import glob
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "forge-gui/res/adventure/Concordia/decks/tier%d/*.dck" % tier))):
        c = classify(f, tier)
        lo, hi, isx, ench, art = windows(tier, c["archetype"], c["sub"], c["reach"])
        why = []
        if c["creatures"] < lo: why.append("creatures %d<%d" % (c["creatures"], lo))
        if c["creatures"] > hi: why.append("creatures %d>%d" % (c["creatures"], hi))
        if c["instant_sorcery"] < isx: why.append("inst+sorc %d<%d" % (c["instant_sorcery"], isx))
        if c["enchantments"] < ench: why.append("ench %d<%d" % (c["enchantments"], ench))
        if why: rows.append((os.path.basename(f), c["archetype"], c["sub"] or "", "; ".join(why)))
    print("outside[%d|]{deck|archetype|sub|why}:" % len(rows))
    for r in rows: print("  %s|%s|%s|%s" % r)


def main(argv):
    if argv and argv[0] == "--report":
        return report(int(argv[1]) if len(argv) > 1 else 1)
    print("decks[%d|]{file|archetype|sub|reach|creatures|window}:" % len(argv))
    for p in argv:
        c = classify(p)
        lo, hi, isx, ench, art = windows(c["tier"], c["archetype"], c["sub"], c["reach"])
        print("  %s|%s|%s|%d|%d|%d-%d" % (os.path.basename(p), c["archetype"], c["sub"] or "", c["reach"], c["creatures"], lo, hi))


if __name__ == "__main__":
    main(sys.argv[1:])

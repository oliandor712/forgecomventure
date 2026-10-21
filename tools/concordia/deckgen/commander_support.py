#!/usr/bin/env python3
"""Commander ability reader (human logic H31-H36, user form 2026-10-21): turns a commander's text into what supports it, then counts
the deck cards that do. Replaces the generic-keyword check behind build.py H17 (which scored Dwynen, Attuma and Adelbert at 0-1).
Profile items (each one a support test on a deck card):
  tribe:T       'Other Elf creatures', 'Pirates you control', 'Merfolk' ... : creatures of type T (H32)
  scales:Y      'for each Y you control', 'per Y', 'number of Y' : cards of type Y (Equipment, Artifact, Aura ...) (H31)
  modified      equipment, aura and +1/+1-counter cards (H33)
  attack        'when X attacks': evasion, haste, pump (H33)
  etb           'when X enters': enter-the-battlefield creatures, bounce, blink (H33)
  discard       'whenever you discard': discard and loot cards (H33)
  sacrifice     'sacrifice', recursion: sacrifice outlets, dies triggers, recursion (H33)
  control       attack tax, spell tax, deathtouch, opponent interaction: removal, tap, bounce, counters, restrict (H34)
  play_exile    'exile the top card ... you may play': draw and selection (H34)
  lifegain      lifelink / gain life: lifegain cards (drain and burn are a potential synergy only, H36)
  evasion/haste/double_strike/flying keywords: equipment, pump and evasion grants
Usage: python3 commander_support.py        writes COMMANDER_SUPPORT.toon for the 80 tier 1 decks and prints a summary"""
import os, re, sys, glob, collections, pickle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ability_tags as at

ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
DECKS = os.path.join(ROOT, "forge-gui/res/adventure/Concordia/decks")
SKIP = {"Creature", "Artifact", "Enchantment", "Legendary", "Snow", "Tribal", "Kindred", "Instant", "Sorcery", "Land"}
CARD_TYPES = {"Equipment", "Artifact", "Aura", "Enchantment", "Vehicle", "Saga", "Instant", "Sorcery", "Land", "Planeswalker"}


def profile(oracle, types, name=""):
    """-> sorted list of support tests for a commander."""
    t = oracle.replace("\\n", "\n").lower()
    own = {x for x in types.split() if x not in SKIP}
    out = set()
    for w in own:
        if re.search(r"\b" + w.lower() + r"s?\b", t.replace(w.lower() + " creature", "")) and w not in ("Noble", "Advisor", "Hero", "Demigod", "Ally", "Familiar", "Scout"): out.add("tribe:" + w)
    if "devotion to" in t:
        out.add("devotion:" + {"white": "W", "blue": "U", "black": "B", "red": "R", "green": "G"}[re.search(r"devotion to (\w+)", t).group(1)])
    if re.search(r"\+1/\+1 counters?", t): out.add("counters")
    if re.search(r"total power|different power|power \d+ or greater", t): out.add("high_power")
    if re.search(r"prowess|noncreature spell|noncombat damage|instant or sorcery", t): out.add("spells")
    if re.search(r"untap (another )?(target|two)", t): out.add("untap")
    if re.search(r"power or toughness 1 or less", t): out.add("small")
    if re.search(r"indestructible|hexproof|protection from", t): out.add("protection")
    if re.search(r"\bmills?\b", t): out.add("mill")
    if re.search(r"commander you control deals combat damage|can't be blocked", t): out.add("evasion")
    if re.search(r"\bvigilance\b", t): out.add("attack")
    for m in re.finditer(r"\b(artifact)s? (you control|spells)", t): out.add("scales:Artifact")
    for m in re.finditer(r"(?:for each|per|number of) (equipment|artifact|aura|enchantment|vehicle|saga|instant|sorcery|land|creature)s?", t):
        out.add("scales:" + m.group(1).capitalize())
    if "modified" in t: out.add("modified")
    if re.search(r"whenever [^.]*attack|when [^.]*attack", t): out.add("attack")
    nm = name.split(",")[0].lower()
    if nm and re.search(r"when(ever)? (" + re.escape(nm) + r"|this creature)[^.]*enters", t): out.add("etb_self")   # H38: triggers only on the commander itself
    if re.search(r"(when|whenever) (another|a|one or more|an?) [^.]*creatures? [^.]*enters?\b", t) or re.search(r"return another target (permanent|creature) you control to its owner", t): out.add("etb_other")   # H38: another creature enters
    for m in re.finditer(r"\b(artifact|enchantment) creatures? you control", t): out.add("scales:" + m.group(1).capitalize())
    if re.search(r"whenever you discard|discard", t): out.add("discard")
    if re.search(r"sacrifice|from your graveyard to (your hand|the battlefield)|dies", t): out.add("sacrifice")
    if re.search(r"can't attack you|cost[s]? \{\d\} more|opponents? cast|pays \{|deathtouch|can't block|tap target", t): out.add("control")
    if re.search(r"exile the top card.{0,90}you may (play|cast)", t): out.add("play_exile")
    if re.search(r"lifelink|gain[s]? \d* ?life|you gain life", t): out.add("lifegain")
    for kw, tag in (("flying", "evasion"), ("menace", "evasion"), ("haste", "attack"), ("double strike", "double_strike")):
        if re.search(r"(^|\n|, )" + kw, t): out.add(tag)
    if re.search(r"cards? leaves? your graveyard|leave your graveyard", t): out.add("graveyard_leave")   # Tormod
    if re.search(r"(^|\n|, )reach\b", t): out.add("flying_hate")   # H39: reach = flying hate only
    if re.search(r"exile (up to one )?(other )?(another )?target creature you control.{0,90}return|flicker", t): out.add("flicker")   # H39: potential loop with etb
    if "ring tempts" in t or "the ring" in t: out.add("ring")   # H43
    if re.search(r"\bscry\b", t): out.add("scry")   # H43: scry counts as draw synergy
    if re.search(r"\blegendary\b", t): out.add("scales:Legendary")
    for m in re.finditer(r"(?i:create[s]?) [^.]*?\b([A-Z][a-z]+)(?: [A-Z][a-z]+)? creature tokens?", oracle.replace("\\n", "\n")):
        if m.group(1) not in ("Creature", "White", "Blue", "Black", "Red", "Green", "Colorless"): out.add("tribe:" + m.group(1))   # token type is the tribe (H40)
    if re.search(r"(creature )?tokens? you control", t): out.add("token")   # Prava, Jiang: token makers and token pump
    if re.search(r"deals damage equal to its power to target creature", t): out.add("dmg_power")   # Halana's own trigger is the low creature removal
    if re.search(r"sacrifice (a|another|an?) land", t):   # H41: sacrificing a land is a cost
        out.discard("sacrifice"); out.add("protection")
    return sorted(out)


def is_partner(oracle):
    return bool(re.search(r"(^|\n|\\n)partner\b", oracle.lower().replace("\\n", "\n")))   # H37


def supports(item, name, text, tags, types):
    ty = types.split()
    crea = "Creature" in ty
    if item.startswith("tribe:"):
        T = item[6:]
        return (crea and T in ty) or ("Changeling" in text) or ("needs:type:" + T) in tags or re.search(r"\b" + T.lower() + "s?\\b", text.lower().split("oracle:")[-1]) is not None and crea
    if item.startswith("scales:"):
        Y = item[7:]
        return Y in ty or (Y == "Artifact" and "artifact_token" in tags) or (Y == "Equipment" and "equip" in tags) or (Y == "Creature" and crea)
    if item == "modified": return "Equipment" in ty or "Aura" in ty or "counters_plus" in tags or "equip" in tags
    if item == "attack": return crea and bool(tags & {"evasion", "flying", "haste", "evasion_grant"}) or bool(tags & {"pump_single", "pump_team", "haste_grant", "evasion_grant"})
    if item == "etb": return (crea and "etb_trigger" in tags) or bool(tags & {"bounce", "clone"})
    if item == "etb_other": return bool(tags & {"token_make", "clone", "bounce"}) or (crea and "etb_trigger" in tags) or bool(re.search(r"exile target creature you control, then return|flicker", text.lower()))
    if item == "etb_self": return bool(tags & {"bounce", "clone", "recursion", "reanimate"}) or bool(re.search(r"exile target creature you control, then return|flicker", text.lower()))
    if item == "graveyard_leave": return bool(tags & {"recursion", "reanimate", "grave_hate", "self_mill", "discard", "token_make", "temp_reanimate"})
    if item == "token": return bool(tags & {"token_make", "pump_team", "artifact_token"})
    if item == "flying_hate": return bool(re.search(r"with flying|have flying|\breach\b|Creature\.withFlying", text))   # H39: cards that answer flyers, not generic removal
    if item == "dmg_power": return (crea and bool(re.search(r"^PT:([4-9]|\d{2,})/", text, re.M))) or "etb_trigger" in tags
    if item == "flicker": return bool(re.search(r"exile target creature you control, then return|flicker", text.lower())) or (crea and "etb_trigger" in tags)
    if item == "ring": return "ringtempts" in text.lower() or "the ring tempts" in text.lower()
    if item == "scry": return bool(tags & {"selection", "draw"})
    if item == "discard": return bool(tags & {"discard"}) or "draw" in tags and "discard" in tags
    if item == "sacrifice": return bool(tags & {"sacrifice_outlet", "dies_trigger", "recursion", "reanimate", "temp_reanimate"})
    if item == "control": return bool(tags & {"removal", "tap_down", "bounce", "counterspell", "restrict", "attack_tax", "shrink", "fog"}) or "deathtouch" in tags
    if item == "play_exile": return bool(tags & {"draw", "selection"})
    if item == "lifegain": return "lifegain" in tags
    if item.startswith("devotion:"):
        mc = re.search(r"^ManaCost:(.*)$", text, re.M)
        return bool(mc) and item[9:] in mc.group(1) and "Land" not in ty
    if item == "counters": return bool(tags & {"counters_plus", "proliferate"})
    if item == "high_power":
        pt = re.search(r"^PT:(\d+)/", text, re.M)
        return crea and bool(pt) and int(pt.group(1)) >= 4
    if item == "small":
        pt = re.search(r"^PT:(\d+)/(\d+)", text, re.M)
        return crea and bool(pt) and min(int(pt.group(1)), int(pt.group(2))) <= 1
    if item == "spells": return bool({"Instant", "Sorcery"} & set(ty)) and not crea
    if item == "untap": return bool(tags & {"untap_lands", "mana_source"}) and not crea or "mana_source" in tags
    if item == "protection": return bool(tags & {"protection_trick", "fog", "indestructible"})
    if item == "mill": return bool(tags & {"mill", "self_mill"})
    if item == "evasion": return bool(tags & {"evasion", "flying", "evasion_grant", "equip"})
    if item == "double_strike": return bool(tags & {"equip", "grant_double_strike", "pump_single"})
    return False


def read(path):
    sec, main, cmd = None, [], []
    for ln in open(path, errors="replace"):
        ln = ln.strip()
        if ln.startswith("["): sec = ln; continue
        m = re.match(r"(\d+) ([^|]+)", ln)
        if m: (main if sec == "[Main]" else cmd if sec == "[Commander]" else []).append((int(m.group(1)), m.group(2).strip()))
    return main, cmd


def analyse(path, pool):
    main, cmd = read(path)
    cn = cmd[0][1]
    c = pool.get(cn.lower())
    prof = profile(c["oracle"], c["types"], cn) if c else []
    cards = []
    for q, n in main:
        t = at.card_text(n)
        if not t or "Types:Land" in t: continue
        cards.append((n, t, at.tags_of(t), at.parse(t)[5]))
    per = {it: sum(1 for n, t, tg, ty in cards if supports(it, n, t, tg, ty)) for it in prof}
    # a card supports the commander if it passes ANY test
    works = sum(1 for n, t, tg, ty in cards if any(supports(it, n, t, tg, ty) for it in prof))
    return cn, prof, per, works, bool(c) and is_partner(c["oracle"])


def main():
    pool = pickle.load(open(os.path.join(HERE, "pool.pkl"), "rb"))
    rows = []
    for f in sorted(glob.glob(os.path.join(DECKS, "tier1", "*.dck"))):
        cn, prof, per, works, partner = analyse(f, pool)
        rows.append((os.path.basename(f)[3:-4], cn, ";".join(prof) or "none", works, ";".join("%s=%d" % kv for kv in per.items()), "partner" if partner else ""))
    L = ["# Commander support (generated by deckgen/commander_support.py; rules H31-H36). works = deck cards that pass any profile test of the commander's ability; threshold in build.py H17 is 5.",
         "commanders[%d|]{deck|commander|profile|works|per_test|partner}:" % len(rows)] + ["  %s|%s|%s|%d|%s|%s" % r for r in rows]
    open(os.path.join(HERE, "COMMANDER_SUPPORT.toon"), "w").write("\n".join(L) + "\n")
    w = [r[3] for r in rows]
    print("partner commanders in tier 1 (H37: exclude from tier 1): %s" % ", ".join(r[0] for r in rows if r[5]))
    print("%d decks; works >=5: %d, 3-4: %d, <3: %d; profile none: %d" % (len(rows), sum(1 for x in w if x >= 5), sum(1 for x in w if 3 <= x < 5), sum(1 for x in w if x < 3), sum(1 for r in rows if r[2] == "none")))


if __name__ == "__main__" and not (len(sys.argv) > 1 and sys.argv[1] == "pairs"):
    main()


# ---- partner decks (H37, user 2026-10-21): two commanders with complementary tags and triggers
def provides(card):
    """What a commander gives the deck: its ability tags plus its own card types (so a Cat token maker 'provides' token_make and Cat)."""
    t = at.card_text(card["name"])
    return t, at.tags_of(t), at.parse(t)[5]


def pair_score(a, b):
    """Complementary score of two partner commanders: how many of A's support tests B itself passes, and the reverse; a tag both lack scores nothing.
    Returns (score, detail)."""
    ta, tga, tya = provides(a); tb, tgb, tyb = provides(b)
    pa = profile(a["oracle"], a["types"], a["name"]); pb = profile(b["oracle"], b["types"], b["name"])
    ab = [it for it in pa if supports(it, b["name"], tb, tgb, tyb)]
    ba = [it for it in pb if supports(it, a["name"], ta, tga, tya)]
    return len(ab) + len(ba), (ab, ba)


def pairs(top=3):
    pool = pickle.load(open(os.path.join(HERE, "pool.pkl"), "rb"))
    partners = [c for c in pool.values() if is_partner(c["oracle"]) and "Legendary" in c["types"].split()]
    t1 = {}
    for f in sorted(glob.glob(os.path.join(DECKS, "tier1", "*.dck"))):
        main, cmd = read(f)
        c = pool.get(cmd[0][1].lower())
        if c and is_partner(c["oracle"]): t1[os.path.basename(f)[3:-4]] = c
    rows = []
    for dk, a in t1.items():
        cands = []
        for b in partners:
            if b["name"] == a["name"] or len(a["id"] | b["id"]) > 2: continue  # H02: one or two colours
            s, (ab, ba) = pair_score(a, b)
            cands.append((s, b["name"], "".join(sorted(a["id"] | b["id"])) or "C", ";".join(ab), ";".join(ba)))
        cands.sort(key=lambda x: (-x[0], x[1]))
        for s, bn, col, ab, ba in cands[:top]: rows.append((dk, a["name"], bn, s, col, ab or "-", ba or "-"))
    L = ["# Partner commander pairs (generated by deckgen/commander_support.py pairs; H37). score = A's support tests that B itself passes + B's that A passes. Two colours at most (H02). %d partner commanders in the pool; partner commanders are excluded from tier 1 (H37), so these pairs are for other tiers." % len(partners),
         "pairs[%d|]{t1_deck|commander_a|partner_b|score|colours|a_needs_met_by_b|b_needs_met_by_a}:" % len(rows)] + ["  %s|%s|%s|%d|%s|%s|%s" % r for r in rows]
    open(os.path.join(HERE, "COMMANDER_PAIRS.toon"), "w").write("\n".join(L) + "\n")
    print("%d partner commanders in the pool; %d tier 1 partner decks; %d pair rows" % (len(partners), len(t1), len(rows)))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "pairs":
    pairs()

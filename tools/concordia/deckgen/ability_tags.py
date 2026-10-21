#!/usr/bin/env python3
"""Ability-led tags for Concordia deck building (user, 2026-10-21: tags follow what an ability DOES, never a per-card list).

Pipeline
  1. parse a card script into abilities: A: lines and SVar DB$ sub-abilities (API + params), T: trigger modes, S: static modes, K: keywords.
  2. normalise each ability to a SIGNATURE (descriptions, names and numbers stripped) and tag the signature once: thousands of cards
     share a few hundred signatures, so the rules run per signature, not per card.
  3. add the tags Forge itself publishes (DeckHas: / DeckNeeds: / DeckHints: lines, e.g. Ability$Proliferate, Type$Elf) as provides / needs edges.
  4. POLICY holds the user's notes at tag level: archetype weights, synergy edges, subtype groups, staples, mono penalty.
Use:  python3 ability_tags.py                 writes ABILITY_TAGS.toon (tag table + counts) and t1_card_tags.json (tier 1 eligible pool)
      python3 ability_tags.py "Card Name" ... prints a card's tags and bonus
      from ability_tags import tags_of, bonus   (build.py: bonus(tags, archetype, sub, deck_traits))"""
import os, re, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
CARDS = os.path.join(ROOT, "forge-gui/res/cardsfolder")
STRIP = re.compile(r"\| *(SpellDescription|StackDescription|TriggerDescription|Description|TgtPrompt|PrecostDesc|CostDesc|AIPreference|SubAbility|Execute)\$[^|]*")

# ---- ability rules: (tag, regex on the normalised signature). Signature example: "AB Mana | Cost$ T | Produced$ Combo ColorIdentity"
RULES = [
    ("mana_source", r"^(AB|SP|DB) Mana\b"),
    ("fixing", r"^AB Mana.*(Produced\$ (Any|Combo))"),
    ("mana_burst", r"^SP Mana\b"),
    ("cost_reduce", r"^S ReduceCost|Mode\$ ReduceCost"),
    ("land_tutor", r"(?=.*ChangeZone)(?=.*Origin\$ Library)(?=.*Destination\$ (Hand|Battlefield))(?=.*ChangeType\$ [^|]*(Land|Basic|Forest|Plains|Island|Swamp|Mountain))"),
    ("tutor", r"(?=.*ChangeZone)(?=.*Origin\$ Library)(?=.*Destination\$ (Hand|Battlefield|Library))(?!.*ChangeType\$ [^|]*(Land|Basic))"),
    ("self_mill", r"Mill\b.*Defined\$ You|ChangeZone.*Origin\$ Library.*Destination\$ Graveyard"),
    ("mill", r"\bMill\b(?!.*Defined\$ You)"),
    ("draw", r"\b(Draw)\b"),
    ("selection", r"\b(Dig|DigUntil|RearrangeTopOfLibrary|Scry)\b"),
    ("discard", r"\bDiscard\b"),
    ("recursion", r"ChangeZone.*Origin\$ Graveyard.*Destination\$ Hand"),
    ("reanimate", r"ChangeZone.*Origin\$ Graveyard.*Destination\$ Battlefield"),
    ("temp_reanimate", r"ChangeZone.*Origin\$ Graveyard.*Destination\$ Battlefield.*AtEOT"),
    ("grave_hate", r"ChangeZoneAll.*Origin\$ Graveyard.*Destination\$ Exile|ChangeZone.*ValidTgts\$ Card\.inZoneGraveyard.*Destination\$ Exile"),
    ("token_make", r"\b(Token)\b|Populate|Amass"),
    ("clone", r"CopyPermanent|Clone"),
    ("pump_single", r"^(SP|AB) Pump\b.*ValidTgts\$ Creature.*NumAtt\$ \+"),
    ("pump_team", r"\bPumpAll\b|Mode\$ Continuous.*Affected\$ Creature\.YouCtrl.*(AddPower|AddToughness)"),
    ("protection_trick", r"^(SP|AB|DB) (Pump|Protection)\b.*(KW\$ (Protection|Indestructible|Hexproof)|Gains\$ Protection)|\bProtection\b.*ValidTgts"),
    ("fog", r"AILogic\$ Fog|\bFog\b"),
    ("tap_down", r"\bTapAll\b|^(SP|AB) Tap\b"),
    ("steal_temp", r"GainControl.*(Untap|LoseControl)"),
    ("drain", r"LoseLife.*GainLife|GainLife.*LoseLife"),
    ("burn", r"DealDamage.*ValidTgts\$ (Any|Player|Opponent)|LoseLife.*(ValidTgts|Defined)\$ [^|]*(Opponent|Player)|Mode\$ LifeGained.*LoseLife"),
    ("shrink", r"PutCounter.*M1M1|Pump.*NumDef\$ -"),
    ("proliferate", r"\bProliferate\b"),
    ("counters_plus", r"PutCounter.*P1P1|MultiplyCounter"),
    ("attack_tax", r"CantAttackUnless"),
    ("restrict", r"Mode\$ (CantAttack|CantBlock|CantBeCast|CantPlayLand|CantDraw|CantGainLife|CantBeActivated|CantTarget)"),
    ("haste_grant", r"AddKeyword\$ Haste|KW\$ Haste"),
    ("grant_double_strike", r"Double Strike|DoubleStrike"),
    ("equip", r"^K Equip|Attach\b"),
    ("crew", r"^K Crew"),
    ("untap_lands", r"UntapAll.*Land"),
    ("flashback_return", r"Flashback"),
    ("lifegain", r"\bGainLife\b"),
    ("removal", r"^(AB|SP|DB) (Destroy|Fight)\b.*ValidTgts\$ [^|]*(Creature|Permanent|Artifact|Enchantment|Planeswalker)|DealDamage.*ValidTgts\$ [^|]*(Creature|Any)|(?=.*ChangeZone)(?=.*Origin\$ Battlefield)(?=.*Destination\$ (Exile|Graveyard|Library))(?=.*ValidTgts\$ [^|]*(Creature|Permanent|Artifact|Enchantment))"),
    ("bounce", r"ChangeZone.*Origin\$ Battlefield.*Destination\$ Hand"),
    ("counterspell", r"\bCounter\b.*TargetType\$ Spell|^(SP|AB) Counter\b"),
    ("sacrifice_outlet", r"Cost\$ [^|]*Sac<"),
    ("artifact_token", r"\bToken\b.*TokenScript\$ [^|]*(food|treasure|clue|blood)"),
    ("evasion_grant", r"AddKeyword\$ (Flying|Menace|Unblockable|Fear|Intimidate|Shadow)|KW\$ (Flying|Menace)"),
    ("dies_trigger", r"^T ChangesZone.*Origin\$ Battlefield.*Destination\$ Graveyard"),
    ("combat_damage_trigger", r"^T DamageDone.*CombatDamage"),
    ("etb_trigger", r"^T ChangesZone.*Destination\$ Battlefield"),
]
RULES = [(t, re.compile(p)) for t, p in RULES]

# ---- keyword tags (K: lines) and the traits a creature gives a deck
KEYWORD_TAGS = {"Flying": "flying", "Menace": "evasion", "Unblockable": "evasion", "Fear": "evasion", "Intimidate": "evasion", "Shadow": "evasion",
                "Deathtouch": "deathtouch", "Double Strike": "double_strike", "First Strike": "first_strike", "Trample": "trample", "Haste": "haste",
                "Flashback": "flashback", "Haunt": "haunt", "Cycling": "cycling", "Convoke": "convoke", "Lifelink": "lifelink", "Indestructible": "indestructible"}

# ---- POLICY (user's form, applied per tag). arch: weight per archetype (aggro, tribal, tokens, control); syn: traits that raise the weight when the deck has them;
#      need: the deck must hold n of a trait before the tag counts (Sphere of Safety); group: subtype; staple: tier 1 staple; mono: weight in a one-colour deck.
POLICY = {
    "fixing": dict(group="mana", mono=-1.0, note="low priority in mono-colour decks"),
    "mana_source": dict(group="mana", staple=True, note="colourless rock with a sacrifice-draw is a tier 1 staple"),
    "mana_burst": dict(group="ramp", need={"high_curve": 3}, note="AI gains 6+ mana: only with expensive spells in the deck"),
    "cost_reduce": dict(group="curve_remedy", syn=["high_curve"], note="alternate mana-curve / ramp remedy"),
    "land_tutor": dict(group="curve_remedy", syn=["high_curve"], note="alternate ramp; better with a higher curve"),
    "equip": dict(arch=dict(aggro=1, tokens=-1, control=-1), syn=["flying", "evasion"], note="slight aggro priority, unblockable/flying carriers"),
    "grant_double_strike": dict(arch=dict(aggro=1, tokens=-1, control=-1), syn=["evasion", "high_power", "combat_damage_trigger"]),
    "crew": dict(syn=["tokens", "creatures"]),
    "draw": dict(group="card_flow"),
    "combat_damage_trigger": dict(syn=["evasion", "flying"], note="card advantage on hit wants evasion"),
    "pump_single": dict(arch=dict(aggro=1), note="slight aggro priority"),
    "pump_team": dict(syn=["tokens", "creatures"], note="finisher"),
    "self_mill": dict(group="reanimation", syn=["reanimation", "mill", "self_discard"]),
    "recursion": dict(group="reanimation", syn=["reanimation", "mill", "self_discard"]),
    "reanimate": dict(group="reanimation", syn=["mill", "self_discard", "dies_trigger"]),
    "temp_reanimate": dict(group="reanimation", syn=["dies_trigger", "sacrifice"], note="sacrifice at end step feeds dies effects"),
    "discard": dict(group="reanimation", syn=["sacrifice", "reanimation", "card_flow"], note="self-discard feeds reanimation; opposing discard is control"),
    "mill": dict(group="reanimation", syn=["reanimation"]),
    "grave_hate": dict(group="control/grave-hate", staple=True, note="new removal subtype grave-hate; tier 1 staple"),
    "token_make": dict(group="tokens", syn=["tokens", "creatures", "flying"], note="tribal option when the token type matches a tribe (Elf, Angel, Soldier, Spirit)"),
    "clone": dict(syn=["legendary"]),
    "shrink": dict(removal_weight=0.5, note="low removal"),
    "proliferate": dict(syn=["counters"], note="counters of any kind"),
    "counters_plus": dict(syn=["counters"]),
    "fog": dict(group="control/protection", arch=dict(control=1), syn=["deathtouch", "combat_damage_trigger"], note="new subtype protection under control"),
    "protection_trick": dict(group="control/protection", arch=dict(control=1), syn=["high_impact"], note="new subtype protection under control"),
    "burn": dict(group="control/burn", arch=dict(control=1, aggro=1), note="new subtype burn: damage or life loss to the opponent"),
    "drain": dict(group="control/burn", arch=dict(control=1, aggro=1), syn=["high_power", "tokens", "creatures"], note="scales with power or creature count"),
    "steal_temp": dict(arch=dict(aggro=1, control=1)),
    "tap_down": dict(syn=["flying", "evasion"], note="taps non-flyers"),
    "untap_lands": dict(syn=["instants"], note="instant-speed play"),
    "haste_grant": dict(arch=dict(aggro=1), syn=["aggro"]),
    "flashback_return": dict(syn=["flashback"]),
    "attack_tax": dict(group="control/lock", need={"enchantments": 5}, note="scales with enchantments you control"),
    "restrict": dict(group="control/lock"),
    "lifegain": dict(syn=["lifegain_punish"]),
    "removal": dict(group="control/removal", priority=["creature", "artifact", "enchantment", "land", "token"]),
    "bounce": dict(group="control/bounce", syn=["etb_trigger", "creatures"], note="slight priority with enter-the-battlefield triggers"),
    "counterspell": dict(group="control/counter", note="prefer low or alternate cost; avoid 'lose the game' triggers"),
    "artifact_token": dict(syn=["artifacts", "sacrifice"]),
    "sacrifice_outlet": dict(syn=["artifacts", "sacrifice"]),
}
# colour leans (slight): tag -> colours that get a small bonus
COLOUR_LEAN = {"removal_land": "R", "tap_down": "UW", "equip": "UW", "draw": "U", "selection": "U", "clone": "U", "recursion": "B", "reanimate": "B",
               "self_mill": "UB", "mill": "UB", "sacrifice_outlet": "B", "haste_grant": "R"}


def parse(text):
    """-> (abilities as normalised signatures, keywords, deckhas, deckneeds, deckhints, types)"""
    face = text.split("\nALTERNATE")[0]
    svars = dict(re.findall(r"^SVar:(\w+):(.*)$", face, re.M))
    sigs, kws, has, needs, hints, types = [], [], [], [], [], ""
    for ln in face.splitlines():
        if ln.startswith("Types:"): types = ln[6:]
        elif ln.startswith("K:"): kws.append(ln[2:].split(":")[0])
        elif ln.startswith("DeckHas:"): has += [x for x in re.split(r"\s*[&|]\s*", ln[8:]) if x]
        elif ln.startswith("DeckNeeds:"): needs += [x for x in re.split(r"\s*[&|]\s*", ln[10:]) if x]
        elif ln.startswith("DeckHints:"): hints += [x for x in re.split(r"\s*[&|]\s*", ln[10:]) if x]
        elif re.match(r"^(A|S|T):", ln):
            kind = ln[0]
            body = ln[2:]
            if kind == "A": body = re.sub(r"^(AB|SP|DB)\$ ", lambda m: m.group(1) + " ", body)
            else: body = kind + " " + body
            ex = re.search(r"Execute\$ (\w+)", body)
            sub = svars.get(ex.group(1), "") if ex else ""
            sigs.append(norm(body))
            if sub: sigs.append(norm(re.sub(r"^(AB|SP|DB)\$ ", lambda m: m.group(1) + " ", sub)))
    for name, v in svars.items():
        if re.match(r"^(DB|AB|SP)\$ ", v): sigs.append(norm(re.sub(r"^(AB|SP|DB)\$ ", lambda m: m.group(1) + " ", v)))
    return sigs, kws, has, needs, hints, types


KEEP = {"Origin", "Destination", "Produced", "ValidTgts", "Defined", "KW", "Keywords", "AddKeyword", "AddKeywords", "CounterType", "Mode", "Phase", "Gains", "Choices",
        "Cost", "TriggerZones", "Affected", "TargetType", "AtEOT", "AILogic", "ReplacementEffects", "ChangeType", "ValidCard", "ValidCards", "ValidActivatingPlayer",
        "TokenScript", "ValidPlayer", "NumAtt", "NumDef", "LifeAmount", "DefinedPlayer"}
COARSE = {"ValidTgts", "Affected", "ValidCard", "ValidCards", "Defined", "ChangeType", "ValidPlayer", "ValidActivatingPlayer", "DefinedPlayer"}


def norm(s):
    """Signature: API, parameter keys, and values only for the keys that decide what the ability does (coarsened to the first word,
    digits dropped, pump signs kept) so thousands of cards share a few hundred signatures."""
    s = STRIP.sub("", s)
    parts = [x.strip() for x in s.split("|")]
    head = parts[0]
    out = []
    for x in parts[1:]:
        m = re.match(r"^(\w+)\$ ?(.*)$", x)
        if not m: continue
        k, v = m.groups()
        if k not in KEEP: out.append(k + "$"); continue
        if k in ("NumAtt", "NumDef", "LifeAmount"): v = v[:1] if v[:1] in "+-" else "N"
        elif k == "TokenScript": v = " ".join(w for w in ("food", "treasure", "clue", "blood") if w in v.lower())
        elif k == "Cost": v = re.sub(r"Sac<[^>]*>", "Sac<>", v); v = re.sub(r"\b\d+\b", "N", v)
        elif k == "CounterType": pass
        elif k in COARSE: v = re.split(r"[. ,+&]", v.strip())[0]
        else: v = re.sub(r"\b\d+\b", "N", v)
        out.append("%s$ %s" % (k, v))
    return head + " | " + " | ".join(dict.fromkeys(out))


_SIG_CACHE = {}


def tag_signature(sig):
    if sig not in _SIG_CACHE:
        _SIG_CACHE[sig] = frozenset(t for t, rx in RULES if rx.search(sig))
    return _SIG_CACHE[sig]


def tags_of(text):
    """Ability-led tags of one card script (set), plus provides/needs from Forge's Deck lines."""
    sigs, kws, has, needs, hints, types = parse(text)
    tags = set()
    for s in sigs: tags |= tag_signature(s)
    for k in kws:
        if k in KEYWORD_TAGS: tags.add(KEYWORD_TAGS[k])
        if k.startswith("Equip"): tags.add("equip")
        if k.startswith("Crew"): tags.add("crew")
    for h in has: tags.add("has:" + h.replace("Ability$", "").replace("Type$", "type:").replace("$", ":"))
    for n in needs: tags.add("needs:" + n.replace("Ability$", "").replace("Type$", "type:").replace("$", ":"))
    for n in hints: tags.add("hint:" + n.replace("Ability$", "").replace("Type$", "type:").replace("$", ":"))
    if "Equipment" in types: tags.add("equip")
    if "Vehicle" in types: tags.add("crew")
    return tags


def bonus(tags, archetype, sub=None, traits=None, mono=False, colours=""):
    """Deck-building bonus for one card from its tags: archetype weights + synergy hits + mono penalty. traits: {trait: count} of the deck so far."""
    traits = traits or {}
    b = 0.0
    for t in tags:
        p = POLICY.get(t)
        if not p: continue
        need = p.get("need")
        if need and any(traits.get(k, 0) < n for k, n in need.items()): continue
        b += p.get("arch", {}).get(archetype, 0)
        if sub and sub.startswith("low-control"): b += p.get("arch", {}).get("control", 0) * 0.5
        b += 0.5 * sum(1 for s in p.get("syn", []) if traits.get(s, 0) >= 3)
        if mono: b += p.get("mono", 0)
        if p.get("staple"): b += 1.0
    return round(b, 2)


def eligible_pool():
    import pickle
    p = pickle.load(open(os.path.join(HERE, "pool.pkl"), "rb"))
    def pw(c):
        v = [c["power"][r] for r in ("C", "U") if r in c["power"]]
        return min(v) if v else None
    for k, c in p.items():
        t = c["types"].split()
        if "Land" in t or not (set(c["best"]) & {"C", "U"}) or c["gc"] or c["mld"] or c["tags"] & {"fast", "tutor", "wipe"}: continue
        w = pw(c)
        if w is not None and w <= 25.4: yield k, c


def card_text(name):
    f = os.path.join(CARDS, name[0].lower(), re.sub(r"[^a-z0-9_]", "", name.lower().replace(" ", "_").replace("-", "_")) + ".txt")
    return open(f, errors="replace").read() if os.path.exists(f) else ""


def build():
    out, count, sigs_seen = {}, collections.Counter(), set()
    for k, c in eligible_pool():
        text = card_text(c["name"])
        if not text: continue
        sigs = parse(text)[0]; sigs_seen.update(sigs)
        tg = tags_of(text)
        out[c["name"]] = sorted(tg)
        count.update(tg)
    json.dump(out, open(os.path.join(HERE, "t1_card_tags.json"), "w"), indent=0, sort_keys=True)
    rows = []
    for t, n in count.most_common():
        if t.startswith(("has:", "needs:", "hint:")): continue
        p = POLICY.get(t, {})
        rows.append((t, p.get("group", ""), n, ",".join("%s%+g" % kv for kv in sorted(p.get("arch", {}).items())), ";".join(p.get("syn", [])),
                     ";".join("%s>=%s" % kv for kv in sorted(p.get("need", {}).items())), "yes" if p.get("staple") else "", p.get("note", "")))
    L = ["# Ability tags (generated by deckgen/ability_tags.py; the rules and policy live in that file). cards = tier 1 eligible cards with the tag. %d cards, %d distinct ability signatures (tagged once each)." % (len(out), len(sigs_seen)),
         "tags[%d|]{tag|group|cards|arch_weight|synergy|need|staple|note}:" % len(rows)] + ["  %s|%s|%d|%s|%s|%s|%s|%s" % r for r in rows]
    open(os.path.join(HERE, "ABILITY_TAGS.toon"), "w").write("\n".join(L) + "\n")
    forge = collections.Counter(t for tg in out.values() for t in tg if t.startswith(("has:", "needs:", "hint:")))
    print("%d eligible cards tagged; %d distinct signatures; %d ability tags used; Forge Deck lines add %d provides/needs/hint tags" % (len(out), len(sigs_seen), len(rows), len(forge)))
    print("untagged (no ability tag):", sum(1 for tg in out.values() if not any(not t.startswith(("has:", "needs:", "hint:")) for t in tg)))


def main(argv):
    if not argv: return build()
    for n in argv:
        tg = sorted(tags_of(card_text(n)))
        print("%s: %s" % (n, ", ".join(tg) or "(none)"))


if __name__ == "__main__":
    main(sys.argv[1:])

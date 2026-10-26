"""Derived tags and the face: line (TAG_SUGGESTIONS C and D, approved 2026-10-23).

face(text, name)      -> numbers from the card script (mana value, power, toughness, loyalty, colors) plus color identity and rarity from scryfall/cards.json
derived(tags, groups) -> tags computed from the base tags, never read from a script. Rules live here only.
Both are written as their own lines (`face:`, `derived:`) in STARTER_TAGS.toon. They are not part of `tags:` and the blind reader never sees them."""
import os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
_SCRY = {}
EVASION_KW = {"kw:flying", "kw:menace", "kw:shadow", "kw:fear", "kw:intimidate", "kw:skulk", "evasion", "cant_be_blocked"}
EVASION_GRANT = {"grant_kw:flying", "grant_kw:menace", "grant_kw:shadow", "grant_kw:fear", "grant_kw:intimidate", "grant_kw:landwalk", "evasion_grant"}
TOKEN_PROVIDES = (("food", "lifegain"), ("treasure", "mana_source"), ("clue", "draw"), ("blood", "discard"))   # D1 (a): link, so a builder can exclude them
REMOVE_W = 1.0     # remove:* or damage to a creature, one target
FIGHT_W = 0.5      # TAG_SUGGESTIONS S13
SHRINK_W = 0.5     # S13 says "by counter_count vs toughness"; toughness is not in the tags, so a flat 0.5 (unverified)


def _scry():
    if not _SCRY:
        p = os.path.join(HERE, "scryfall", "cards.json")
        if os.path.exists(p): _SCRY.update(json.load(open(p, encoding="utf-8")))
        else: _SCRY["_none"] = {}
    return _SCRY


def _mv(cost):
    n = 0
    for s in cost.split():
        n += int(s) if s.isdigit() else 0 if s == "X" else 1
    return n


def face(text, name):
    f = text.split("\nALTERNATE")[0]
    g = lambda k: next((l.split(":", 1)[1].strip() for l in f.split("\n") if l.startswith(k + ":")), "")
    cost = g("ManaCost"); pt = g("PT"); out = []
    if cost and cost != "no cost": out.append("mv:%d" % _mv(cost))
    else: out.append("mv:0")
    if pt and "/" in pt: p, t = pt.split("/", 1); out += ["power:" + p.lower(), "toughness:" + t.lower()]
    if g("Loyalty"): out.append("loyalty:" + g("Loyalty").lower())
    col = "".join(c for c in "wubrg" if c.upper() in re.sub(r"[^A-Z]", "", cost.upper().replace("X", "")))
    col = col or {"White": "w", "Blue": "u", "Black": "b", "Red": "r", "Green": "g"}.get(g("Colors"), "")
    out.append("colors:" + (col or "c"))
    s = _scry().get(name.lower())
    if s:
        ident = "".join(c for c in "wubrg" if c.upper() in (s.get("color_identity") or ""))
        out += ["identity:" + (ident or "c"), "rarity:" + s.get("rarity", "?")]
    return " ".join(out)


def provided_by(tags, base):
    """D1 (a): (function tag, 'provided_by', token tag) for tags that only the token script supplies; `base` = tags the card script itself gives"""
    links = []
    for ty, fn in TOKEN_PROVIDES:
        if "token_type:" + ty in tags and fn in tags and fn not in base: links.append((fn, "provided_by", "token_type:" + ty))
    return links


def _tokenonly(tags, base):
    return {fn for ty, fn in TOKEN_PROVIDES if "token_type:" + ty in tags and fn in tags and fn not in base}


def derived(tags, groups, base=()):
    """groups: {id: [tags]} (rules and AI tags); tags: the card's full tag list"""
    d = []
    tagset = set(tags)
    gl = [set(ts) for ts in groups.values()]
    one = lambda g: bool(g & {"target_count:one", "target_count:up_to_1", "target_count:2"})
    def isrem(g): return any(t.startswith("remove:") for t in g) or ("damage" in g and bool(g & {"target_type:creature", "target_type:any", "target_type:permanent"}))
    def iswipe(g): return "target_count:all" in g and "target_type:creature" in g and not any(t.startswith("target_filter:") for t in g) and "target_scope:you_control" not in g and (any(t.startswith("remove:") for t in g) or "damage" in g)
    if any(iswipe(g) for g in gl): d.append("wipe")
    # anthem = a static bonus for creatures other than one attached host: positive pump_amount + duration:static + affected_scope:you_control (or pump_team); auras, equipment and one-shot team pumps (Overrun) are not anthems
    if any("duration:static" in g and ("affected_scope:you_control" in g or "pump_team" in g) and any(re.fullmatch(r"pump_amount:\+(\d+|x)/\+(\d+|x)", t) for t in g) for g in gl): d.append("anthem")
    if any(isrem(g) and one(g) for g in gl) or ("fight" in tagset): d.append("spot_removal")
    w = sum(REMOVE_W for g in gl if isrem(g) and "target_count:all" not in g) + sum(FIGHT_W for g in gl if "fight" in g) + sum(SHRINK_W for g in gl if "shrink" in g)
    if "wipe" in d: w += REMOVE_W
    if w: d.append("removal_weight:%g" % w)
    if tagset & EVASION_KW or tagset & EVASION_GRANT: d.append("evasion_pkg")
    if any("trigger:etb" in g and "trigger_scope:self" in g for g in gl): d.append("etb_self")
    if any("trigger:etb" in g and (g & {"trigger_scope:other", "trigger_scope:any"}) for g in gl): d.append("etb_other")
    # token_make is the umbrella for every token; token_kind says which sort (user 2026-10-26: creature, artifact or copy)
    if "token_make" in tagset:
        if "token_type:copy" in tagset: d.append("token_kind:copy")
        if tagset & {"token_cardtype:artifact", "artifact_token"} or any(t.startswith("token_ability:") for t in tagset): d.append("token_kind:artifact")
        if any(t.startswith("token_pt:") for t in tagset): d.append("token_kind:creature")     # a creature token has power/toughness
        if not any(x.startswith("token_kind:") for x in d): d.append("token_kind:artifact" if "investigate" in tagset else "token_kind:creature")     # no power/toughness written (X-sized or varying tokens)
    if any({"target_type:instant", "target_type:sorcery"} <= g for g in gl): d.append("target_type:instant_or_sorcery")     # both stay as tags (a card may name one); this marks the pair
    d = list(dict.fromkeys(d))
    tok = _tokenonly(tags, base)
    out = []
    for g in groups.values():
        if "mana_source" in g and "mana_source" not in tok:
            cols = sorted({t.split(":", 1)[1] for t in g if t.startswith("mana:") and t != "mana:any"} | ({"any"} if "mana:any" in g else set()))
            amt = next((t.split(":", 1)[1] for t in g if t.startswith("mana_amount:")), "")
            if cols and amt: out.append("mana_out:%s:%s" % ("+".join(cols), amt))
    d += list(dict.fromkeys(out))
    return d

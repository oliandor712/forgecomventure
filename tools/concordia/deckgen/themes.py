"""Deck themes from tags (ACTION_PLAN_TAG_DECK.md): umbrella tags and heavy tribal presence replace the old 'commander's creature types'.
A theme is a list of tokens, the same list decks.json carries and build.theme_match reads:
  tag:<umbrella>   the card carries any tag of the umbrella (UMBRELLA below, names as policy_tags.tags_for gives them)
  <Type>           a creature type: kept only when the tribe is real (H74: the commander has a tribal ability for it, or the colours hold HEAVY+ creatures of it)
  noabil, /regex/  unchanged
Library: theme_for(commander pool card, pool) -> list; umbrellas_of(card name) -> set; variant_theme(base, new) -> list; matches(name, token) -> bool."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import policy_tags as pt
import commander_support as cp

HEAVY = 12      # creatures of one type in the commander's colours (user-approved), and cp.FEW of them with a tribal ability, before the tribe is a theme without a tribal ability on the commander
MAX_THEMES = 3
UMBRELLA = {
    "tokens": {"token_make", "pump_team", "scales:Token", "lord:Token"},
    "counters": {"counters_plus", "proliferate", "scales:counters"},
    "reanimation": {"self_mill", "recursion", "reanimate", "temp_reanimate", "mill", "surveil", "discard"},
    "sacrifice": {"sacrifice_outlet", "effect:sacrifice", "dies_trigger", "investigate", "artifact_token"},
    "ramp": {"mana_source", "mana_burst", "land_tutor", "extra_land_drop:*"},   # a trailing * matches any value of the tag
    "artifacts": {"artifact_token", "investigate", "scales:Artifact", "lord:Artifact", "scales:Equipment", "equip", "crew"},
    "spells": {"counterspell", "untap_lands", "trigger:spell_cast", "scales:Instant", "scales:Sorcery", "cost_reduce"},
    "lifegain": {"lifegain", "trigger:gain_life"},
    "evasion": {"evasion", "evasion_grant", "haste_grant", "grant_double_strike", "combat_damage_trigger", "pump_single"},
    "control": {"removal", "bounce", "tap_down", "restrict", "attack_tax", "fog", "shrink"},
    "burn": {"burn", "drain", "life_loss"},
    "enchantments": {"scales:Enchantment", "lord:Enchantment"},
    "etb": {"etb_trigger", "clone"},
}
ORDER = list(UMBRELLA)   # ties between umbrellas keep this order
SKIP_TYPES = cp.SKIP | {"Legendary"}


def hit(tg, s):
    """Tags of the set `s` that card tags `tg` carry (an entry ending in * is a prefix)."""
    return {t for t in tg if t in s or any(x.endswith("*") and t.startswith(x[:-1]) for x in s)}


def umbrellas_of(name):
    tg = pt.tags_for(name)
    return {u for u, s in UMBRELLA.items() if hit(tg, s)}


def matches(name, token):
    return token[4:] in umbrellas_of(name) if token.startswith("tag:") else False


def commander_umbrellas(name):
    """Umbrellas the commander's own tags hit, most hits first. Draw and generic removal alone do not make a theme."""
    tg = pt.tags_for(name)
    hits = {u: len(hit(tg, s)) for u, s in UMBRELLA.items()}
    return [u for u in sorted((u for u in hits if hits[u]), key=lambda u: (-hits[u], ORDER.index(u)))]


def tribes(p, pool):
    """Creature types of the commander that are a real tribe: tribal ability on the commander (H74) or HEAVY creatures of the type in its colours with cp.FEW of them carrying a tribal ability."""
    tg = pt.tags_for(p["name"])
    sub = [t for t in p["types"].replace("—", " ").split() if t not in SKIP_TYPES]
    ident = p["id"]
    out = []
    for t in sub:
        if cp.tribal(tg, t): out.append(t); continue
        same = [q for q in pool.values() if "Creature" in q["types"].split() and t in q["types"].split() and q["id"] <= ident]
        if len(same) >= HEAVY and sum(1 for q in same if cp.tribal(pt.tags_for(q["name"]), t)) >= cp.FEW: out.append(t)
    return out


def theme_for(p, pool, limit=MAX_THEMES):
    """Tribes first (they decide the creature base), then the commander's umbrellas, at most `limit` tokens."""
    out = tribes(p, pool)[:2] + ["tag:" + u for u in commander_umbrellas(p["name"])]
    return list(dict.fromkeys(out))[:limit]


def variant_theme(base, new, limit=MAX_THEMES):
    """A variant keeps the base deck's themes the new commander shares, adds the themes it brings, and drops base themes only to make room:
    the base's first theme always stays, later ones go first."""
    keep = [t for t in base if t in new]
    add = [t for t in new if t not in base]
    out = list(base[:1]) + [t for t in keep if t not in base[:1]]
    out += add + [t for t in base if t not in out]
    return list(dict.fromkeys(out))[:limit]

#!/usr/bin/env python3
"""Strategy data for the deck builder and the balancer: strategies.json roles matched against a card's pool ftags.
  fit(ftags, ids)        -> number of play-line roles of the declared strategies the card fills (0 when ids is empty)
  niche_penalty(ftags, ids) -> how far a niche:* card is weighed down: 0 when a declared strategy uses the niche, else 1 per niche tag
  stages(id)             -> the ordered play-line stages (for balance reports)
A signal 'x' matches ftag x and x:*; 'x:y' matches exactly (see build_strategies.py). Computed conditions (cmc_ge_N, cardtype:*) are ignored."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
_S = None
# which strategy ids pay off a niche:* tag (tag_run.py)
NICHE_USERS = {
    "niche:landfall": {"landfall", "lands_matter", "big_mana"}, "niche:lands": {"landfall", "lands_matter", "big_mana"}, "niche:land": {"stax", "landfall", "lands_matter"},
    "niche:graveyard_hate": {"control", "stax"}, "niche:self_mill": {"graveyard", "reanimator", "self_mill", "mill", "aristocrats"}, "niche:haunt": {"aristocrats"},
    "niche:tribal": {"tribal"}, "niche:storm": {"storm", "spellslinger", "combo"}, "niche:artifact": {"artifacts", "equipment", "treasure", "vehicles"},
    "niche:enchantment": {"enchantress", "control", "sagas", "pillow_fort"}, "niche:aura": {"enchantress", "voltron"}, "niche:equipment": {"equipment", "voltron"},
    "niche:vehicle": {"vehicles", "artifacts"}, "niche:saga": {"sagas", "enchantress", "blink"}, "niche:planeswalker": {"superfriends"}, "niche:battle": {"stompy", "outlaws"},
}


_ALIASES = {}


def load():
    global _S, _ALIASES
    if _S is None:
        f = os.path.join(HERE, "strategies.json")
        d = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}
        _S = d.get("archetypes", {}); _ALIASES = {k: v for k, v in d.get("aliases", {}).items() if v}
    return _S


def resolve(i):
    """old archetype ids (sacrifice, proliferate, aggro...) -> current id; ids dropped without a successor (ramp, card_draw, chaos, colorless) map to themselves and match nothing"""
    load()
    return _ALIASES.get(i, i)


def _match(sig, ftags):
    return any(t == sig or (":" not in sig and t.startswith(sig + ":")) for t in ftags)


def _role_hits(ftags, i):
    S = load()
    return sum(1 for r in S.get(i, {}).get("roles", {}).values() if any(_match(s, ftags) for s in r["sig"] if not s.startswith(("cmc_ge", "cardtype:"))))


def fit(ftags, ids):
    """role matches per archetype; a niche archetype also gets half of its crossover parents' matches"""
    S = load()
    ids = [resolve(i) for i in ids]
    tot = 0
    for i in ids:
        tot += _role_hits(ftags, i)
        a = S.get(i, {})
        if a.get("niche"): tot += sum(_role_hits(ftags, c) for c in a.get("crossover", [])) // 2
    return tot


def baseline_hit(ftags, role):
    """True when the card fills an engine baseline role (recursion, ramp, card_draw, protection) in strategies.json"""
    j = _raw()
    return any(_match(x, ftags) for x in j.get("baseline_roles", {}).get(role, {}).get("sig", []))


def baseline_min(role, ids):
    """lower bound of the baseline range, raised to the archetype uplift (recursion_by_archetype / protection_by_archetype) when a declared archetype has one"""
    j = _raw()
    lo = j.get("baseline_roles", {}).get(role, {}).get("n", [0, 0])[0]
    up = j.get(role + "_by_archetype", {})
    return max([lo] + [up[resolve(i)][0] for i in ids if resolve(i) in up])


def _raw():
    return json.load(open(os.path.join(HERE, "strategies.json"), encoding="utf-8"))


def niche_penalty(ftags, ids):
    load(); ids = {resolve(i) for i in ids}
    return sum(1 for t in ftags if t.startswith("niche:") and not (NICHE_USERS.get(t, set()) & ids))


def stages(i):
    return load().get(resolve(i), {}).get("stages", [])

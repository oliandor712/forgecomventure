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
    "niche:landfall": {"landfall", "ramp", "big_mana"}, "niche:lands": {"landfall", "ramp", "big_mana"}, "niche:land": {"stax", "landfall"},
    "niche:graveyard_hate": {"control", "stax"}, "niche:self_mill": {"graveyard", "reanimator", "mill", "aristocrats"}, "niche:haunt": {"aristocrats", "sacrifice"},
    "niche:tribal": {"tribal"}, "niche:storm": {"storm", "spellslinger", "combo"}, "niche:artifact": {"artifacts", "equipment", "treasure"},
    "niche:enchantment": {"enchantress", "control"}, "niche:aura": {"enchantress", "voltron"}, "niche:equipment": {"equipment", "voltron"},
    "niche:vehicle": {"artifacts", "aggro"}, "niche:saga": {"enchantress", "blink"}, "niche:planeswalker": {"superfriends"}, "niche:battle": {"aggro"},
}


def load():
    global _S
    if _S is None:
        _S = json.load(open(os.path.join(HERE, "strategies.json"), encoding="utf-8"))["archetypes"] if os.path.exists(os.path.join(HERE, "strategies.json")) else {}
    return _S


def _match(sig, ftags):
    return any(t == sig or (":" not in sig and t.startswith(sig + ":")) for t in ftags)


def fit(ftags, ids):
    S = load()
    return sum(1 for i in ids for r in S.get(i, {}).get("roles", {}).values() if any(_match(s, ftags) for s in r["sig"] if not s.startswith(("cmc_ge", "cardtype:"))))


def niche_penalty(ftags, ids):
    ids = set(ids)
    return sum(1 for t in ftags if t.startswith("niche:") and not (NICHE_USERS.get(t, set()) & ids))


def stages(i):
    return load().get(i, {}).get("stages", [])

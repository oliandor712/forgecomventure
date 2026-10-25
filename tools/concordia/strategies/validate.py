#!/usr/bin/env python3
"""Check strategies.json against deckgen/pool.pkl: per role, how many pool cards match the signals, and which named cards are missing."""
import json, os, pickle, sys
H = os.path.dirname(os.path.abspath(__file__))
pool = pickle.load(open(os.path.join(H, "../deckgen/pool.pkl"), "rb"))
cards = pool.values() if isinstance(pool, dict) else pool
S = json.load(open(os.path.join(H, "strategies.json")))["archetypes"]
names = {c["name"] for c in cards}
sys.path.insert(0, os.path.join(H, ".."))
import deck_tier as dt
_cfg = json.load(open(dt.CONFIG)); _rest = {x.lower() for x in _cfg["restrictedCards"]}; _data = dt.build_cache()
def why(n):
    k = n.lower()
    if k in _rest: return "restricted(adventure config)"
    if k not in _data["cards"]: return "name not in Forge"
    if "all" in _data["cards"][k]["flags"]: return "AI:RemoveDeck:All"
    return "no printing >= Sixth Edition / other filter"
cards = list(pool.values() if isinstance(pool, dict) else pool)
tagsets = [set(c.get("ftags") or []) for c in cards]
def hit(sig, ts):
    return any(t == sig or t.startswith(sig + ":") for t in ts)
dead = 0
for a in S.values():
    for r, d in a["roles"].items():
        miss = [n for n in d["cards"] if n not in names]
        sigs = {s: sum(hit(s, ts) for ts in tagsets) for s in d["sig"] if not s.startswith(("cmc_", "cardtype:"))}
        z = [s for s, n in sigs.items() if n == 0]
        if miss or z:
            dead += 1
            print(f"{a['id']}.{r}: missing_cards={[(n, why(n)) for n in miss]} zero_signals={z}")
print("roles with problems:", dead)

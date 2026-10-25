#!/usr/bin/env python3
"""Collect Commander decklists into external/decks.json (the file pool.py counts for popularity and gen_mono.py seeds from).

    python3 tools/concordia/deckgen/collect_decks.py [--per 100] [--brackets 2 3 4] [--edhrec] [--no-net]

Sources: all official precons (spellbinder/precons.json, cached), the most viewed Archidekt Commander decks per bracket
(archidekt.py), and with --edhrec EDHREC's average list per distinct commander (edhrec.py). Every deck:
{name, source, bracket, views, commanders[], cards{name: qty}}. Re-runs reuse the disk caches in external/cache/."""
import os, sys, json, argparse, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import archidekt as AR, edhrec as ED

OUT = os.path.join(HERE, "external", "decks.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per", type=int, default=100); ap.add_argument("--brackets", type=int, nargs="*", default=[2, 3, 4])
    ap.add_argument("--edhrec", action="store_true"); ap.add_argument("--no-net", action="store_true")
    a = ap.parse_args()
    decks = []
    for p in json.load(open(os.path.join(HERE, "spellbinder", "precons.json")))["decks"]:
        decks.append({"name": p["name"], "source": "precon", "bracket": None, "views": 0, "commanders": p["commanders"], "cards": p["cards"]})
    if not a.no_net:
        for b in a.brackets:
            for i, t in enumerate(AR.top(b, a.per)):
                try: d = AR.deck(t["id"])
                except Exception as e: print("skip", t["id"], e); continue
                if not d["commanders"] or sum(d["cards"].values()) < 60: continue
                decks.append({"name": t["name"], "source": "archidekt", "bracket": b, "views": t["views"], "commanders": d["commanders"], "cards": d["cards"]})
            print("bracket", b, "done:", sum(1 for x in decks if x["bracket"] == b))
        if a.edhrec:
            seen = set()
            live = [{"commanders": [d["commander"]]} for d in json.load(open(os.path.join(HERE, "decks.json"), encoding="utf-8")) if d.get("tier", 0) >= 2]
            for x in list(decks) + live:   # the commanders of the collected decks and of every tier 2+ deck in decks.json
                k = tuple(x["commanders"])
                if k in seen: continue
                seen.add(k)
                v = ED.average_deck(k[0])
                if v: decks.append({"name": "EDHREC average " + k[0], "source": "edhrec", "bracket": None, "views": 0, "commanders": list(k), "cards": v["cards"]})
            print("edhrec average decks:", sum(1 for x in decks if x["source"] == "edhrec"))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"built": str(datetime.date.today()), "decks": decks}, open(OUT, "w", encoding="utf-8"))
    print("wrote", len(decks), "decks:", {s: sum(1 for x in decks if x["source"] == s) for s in ("precon", "archidekt", "edhrec")})


if __name__ == "__main__":
    main()

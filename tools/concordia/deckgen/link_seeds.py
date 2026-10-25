#!/usr/bin/env python3
"""Write seed files for the decks in decks.json from the collected lists (external/decks.json, collect_decks.py).

    python3 tools/concordia/deckgen/link_seeds.py            # report only
    python3 tools/concordia/deckgen/link_seeds.py --write    # write external/seeds/<commander>.dck, point d['seed'] at it for decks with none or a missing file

A deck's seed is the best collected list for its commander: the bracket matching its tier (T2 -> 2, T3 -> 3, T4/T5 -> 4) with the most views,
else any Archidekt list, else a precon, else EDHREC's average. Tier 1 never uses seeds (the builder ignores them). Live decks are untouched."""
import os, sys, re, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "..", "..", "forge-gui", "res"))
SEEDS = os.path.join(HERE, "external", "seeds")
BRACKET = {2: 2, 3: 3, 4: 4, 5: 4}
PREFIX = "../../tools/concordia/deckgen/external/seeds/"


def pick(lists, tier):
    def key(x): return (x["source"] == "archidekt", x["bracket"] == BRACKET.get(tier), x["views"], x["source"] == "precon")
    return max(lists, key=key) if lists else None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true"); a = ap.parse_args()
    ext = json.load(open(os.path.join(HERE, "external", "decks.json"), encoding="utf-8"))["decks"]
    by = {}
    for x in ext:
        for c in x["commanders"]: by.setdefault(c.lower(), []).append(x)
    decks = json.load(open(os.path.join(HERE, "decks.json"), encoding="utf-8"))
    n_have = n_new = n_none = 0
    for d in decks:
        tier = d.get("tier") or 0
        if tier < 2: continue
        cur = d.get("seed")
        if cur and os.path.exists(os.path.join(RES, cur)): n_have += 1; continue
        best = pick(by.get(d["commander"].lower(), []), tier)
        if not best: n_none += 1; continue
        n_new += 1
        if a.write:
            os.makedirs(SEEDS, exist_ok=True)
            fn = re.sub(r"[^A-Za-z0-9]+", "_", d["commander"]).strip("_") + ".dck"
            L = ["[metadata]", "Name=seed", "[Commander]"] + ["1 " + c for c in best["commanders"]] + ["[Main]"]
            L += ["%d %s" % (q, c) for c, q in best["cards"].items() if c not in best["commanders"]]
            open(os.path.join(SEEDS, fn), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
            d["seed"] = PREFIX + fn
    if a.write: json.dump(decks, open(os.path.join(HERE, "decks.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("tier 2+ decks: seed on disk %d, new seed %s %d, no collected list %d" % (n_have, "written" if a.write else "available", n_new, n_none))


if __name__ == "__main__":
    main()

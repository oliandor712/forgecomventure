#!/usr/bin/env python3
"""Plans the fresh tier 1 rebuild (user, 2026-10-21): a pool of 100 commanders (20 per colour), 80 of them chosen (16 per colour), each with a
declared archetype and subarchetype, written to t1_fresh.json for build.py. Commander rules for tier 1: legendary creature, one colour, mana
value 2-4, common or uncommon printing, not a commander of any other tier, starter or tutorial deck. Ranking: how many tier 1 eligible cards
of the commander's colour pass the commander's support tests (commander_support.profile and supports, rules H31-H44).
Usage: python3 t1_plan.py        writes t1_fresh.json and T1_COMMANDER_POOL.toon"""
import os, re, sys, json, glob, pickle, collections, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import ability_tags as at, commander_support as cs
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
DECKS = os.path.join(ROOT, "forge-gui/res/adventure/Concordia/decks")
POOL = 20      # commanders per colour in the pool
CHOSEN = 16    # decks per colour
MIN_SUPPORT = 30


def used_elsewhere():
    out = set()
    for f in glob.glob(os.path.join(DECKS, "*/*.dck")):
        if "/tier1/" in f: continue
        sec = None
        for ln in open(f, errors="replace"):
            ln = ln.strip()
            if ln.startswith("["): sec = ln; continue
            m = re.match(r"\d+ ([^|]+)", ln)
            if m and sec == "[Commander]": out.add(m.group(1).strip().lower())
    return out


def ascii_first(name):
    w = re.split(r"[ ,]", name)[0]
    w = unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]", "", w) or "X"


def main():
    pool = pickle.load(open(os.path.join(HERE, "pool.pkl"), "rb"))
    elig = []
    for k, c in at.eligible_pool():
        t = at.card_text(c["name"])
        if t: elig.append((c, t, at.tags_of(t), at.parse(t)[5]))
    taken = used_elsewhere()
    cands = {w: [] for w in "WUBRG"}
    for k, c in pool.items():
        ty = c["types"].split()
        if "Legendary" not in ty or "Creature" not in ty or len(c["id"]) != 1: continue
        if not (set(c["best"]) & {"C", "U"}) or k in taken or c["gc"] or c["mld"]: continue
        col = next(iter(c["id"]))
        prof = cs.profile(c["oracle"], c["types"], c["name"])
        if not prof: continue
        n = sum(1 for e, t, tg, ety in elig if e["id"] <= c["id"] and any(cs.supports(it, e["name"], t, tg, ety) for it in prof))
        cands[col].append((n, c, prof))
    rows, fresh = [], []
    QUOTA = {"tokens": (6, 5), "tribal": (7, 5), "aggro": (7, 6)}   # (pool, chosen) per colour: the mix follows tier 1 today (aggro ~30, tokens ~25, tribal ~25)
    for col in "WUBRG":
        byarch = {"tokens": [], "tribal": [], "aggro": []}
        for n, c, prof in sorted([x for x in cands[col] if x[0] >= MIN_SUPPORT], key=lambda x: (-x[0], x[1]["name"])):
            tb = [it[6:] for it in prof if it.startswith("tribe:")]
            ncre = sum(1 for e, t, tg, ety in elig if e["id"] <= c["id"] and "Creature" in ety and any(x in ety for x in tb)) if tb else 0
            arch = "tribal" if tb and ncre >= 14 else "tokens" if "token" in prof else "aggro"
            byarch[arch].append((n, c, prof, tb, arch))
        picked = []
        for arch, (npool, nch) in QUOTA.items():
            for rank, x in enumerate(byarch[arch][:npool]): picked.append((x, rank < nch))
        # fill a short archetype from the best remaining candidates so the pool is 20 and the chosen set is 16
        have = {id(x[0][1]) for x in picked}
        rest = sorted([x for a in byarch.values() for x in a if id(x[1]) not in have], key=lambda x: (-x[0], x[1]["name"]))
        while len(picked) < POOL and rest: picked.append((rest.pop(0), False))
        while sum(1 for x in picked if x[1]) < CHOSEN:
            nxt = next((k for k, (x, ch) in enumerate(picked) if not ch), None)
            if nxt is None: break
            picked[nxt] = (picked[nxt][0], True)
        for (n, c, prof, tb, arch), ch in picked:
            rows.append((col, arch, c["name"], n, ";".join(prof), "chosen" if ch else "reserve"))
        groups = collections.defaultdict(list)
        for (n, c, prof, tb, arch), ch in picked:
            if ch: groups[arch].append((c, prof, tb))
        used = set()
        for arch, lst in groups.items():
            own = {"aggro": "low-aggro", "tribal": "low-tribal", "tokens": "low-tokens"}[arch]
            for i, (c, prof, tb) in enumerate(sorted(lst, key=lambda x: x[0]["name"])):
                sub = ["low-control", own, None][i % 3]
                base = "T1_%s_%s" % (col, ascii_first(c["name"])); fn = base + ".dck"; j = 2
                while fn in used: fn = "%s%d.dck" % (base, j); j += 1
                used.add(fn)
                theme = tb + [x for x in c["types"].split() if x not in ("Legendary", "Creature")]
                fresh.append(dict(tier=1, file=fn, name=c["name"].split(",")[0], commander=c["name"], colors=col, life=11, theme=list(dict.fromkeys(theme)),
                                  desc="Tier 1 (Bracket 1). Mono-%s %s deck led by %s." % ({"W": "white", "U": "blue", "B": "black", "R": "red", "G": "green"}[col], arch, c["name"]),
                                  archetype=arch, sub=sub, reach=2))
    json.dump(fresh, open(os.path.join(HERE, "t1_fresh.json"), "w"), indent=1, ensure_ascii=False)
    L = ["# Tier 1 commander pool (generated by deckgen/t1_plan.py): 20 per colour, the top 16 per colour are chosen for the fresh rebuild. support = tier 1 eligible cards of the commander's colour that pass its support tests.",
         "pool[%d|]{colour|archetype|commander|support|profile|status}:" % len(rows)] + ["  %s|%s|%s|%d|%s|%s" % r for r in rows]
    open(os.path.join(HERE, "T1_COMMANDER_POOL.toon"), "w").write("\n".join(L) + "\n")
    print("pool %d commanders; chosen %d decks; per colour pool:" % (len(rows), len(fresh)), {c: sum(1 for r in rows if r[0] == c) for c in "WUBRG"})
    print("archetypes:", dict(collections.Counter(d["archetype"] for d in fresh)), "subs:", dict(collections.Counter((d["archetype"], d["sub"]) for d in fresh)))


if __name__ == "__main__":
    main()

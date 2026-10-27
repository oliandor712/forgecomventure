"""Power scorer: additive weights fitted to the EDHREC percentile (non-land cards in deckgen/pool.pkl).
Writes power_scorer/weights.json. Research only: deck_tier.py does not read it yet.
Run from tools/concordia: python power_scorer/fit.py"""
import sys, os, pickle, json, random, statistics as st, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import deck_tier as dt

data = dt.build_cache()
pool = pickle.load(open(dt.POOL, "rb"))
strat = json.load(open(os.path.join(os.path.dirname(HERE), "strategies", "strategies.json"), encoding="utf-8"))
in_strat = collections.defaultdict(set)
for aid, a in strat["archetypes"].items():
    for r in a.get("roles", {}).values():
        for n in r.get("cards", []):
            in_strat[n.lower()].add(aid)


def feats(key, p):
    f = []
    for t in p.get("ftags", ()):
        f += ["t:" + t, "f:" + t.split(":")[0]]
    f += ["cmc:%d" % min(int(float(p.get("cmc") or 0)), 9), "n_colors:%d" % len(p.get("id") or ()),
          "minr:" + str(p.get("minr")), "nabil:%d" % min(int(p.get("nabil") or 0), 6)]
    f += ["type:" + ty.lower() for ty in str(p.get("types", "")).replace("—", " ").split()]
    f.append("strat:%d" % min(len(in_strat.get(key, ())), 4))
    f += ["arch:" + a for a in in_strat.get(key, ())]
    return f


def midrank_pct(vals):
    s = sorted(vals); n = len(s); lo = {}; hi = {}
    for i, v in enumerate(s):
        lo.setdefault(v, i); hi[v] = i
    return [100 * (lo[v] + hi[v]) / 2 / (n - 1) for v in vals]


rows = []
for key, p in pool.items():
    c = data["cards"].get(key)
    if not c or "land" in str(p.get("types", "")).lower():
        continue
    e = dt.edhrec(c)
    if e:
        rows.append((e, feats(key, p)))

y = midrank_pct([r[0] for r in rows])
cnt = collections.Counter(f for r in rows for f in set(r[1]))
vocab = {f: i for i, f in enumerate(f for f, n in cnt.items() if n >= 15)}
X = [[vocab[f] for f in set(r[1]) if f in vocab] for r in rows]
idx = list(range(len(rows))); random.Random(1).shuffle(idx)
cut = int(len(idx) * 0.8); tr, te = idx[:cut], idx[cut:]

w = [0.0] * len(vocab); b = st.mean(y[i] for i in tr)
lam, lr = 0.002, 0.0015
for ep in range(40):
    random.Random(ep).shuffle(tr)
    for i in tr:
        g = b + sum(w[j] for j in X[i]) - y[i]
        b -= lr * g * 0.1
        for j in X[i]:
            w[j] -= lr * (g + lam * w[j] * 100)


def within15(ids):
    p = midrank_pct([b + sum(w[j] for j in X[i]) for i in ids]); t = midrank_pct([y[i] for i in ids])
    return 100 * sum(abs(a - c) <= 15 for a, c in zip(p, t)) / len(ids)


res = {"target": "EDHREC percentile (0-100, midrank)", "bias": b, "cards": len(rows),
       "within15_train": round(within15(tr), 1), "within15_test": round(within15(te), 1),
       "weights": {f: round(w[i], 3) for f, i in sorted(vocab.items())}}
json.dump(res, open(os.path.join(HERE, "weights.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("cards %d features %d train %.1f%% test %.1f%% within 15" % (len(rows), len(vocab), res["within15_train"], res["within15_test"]))

#!/usr/bin/env python3
"""Rewrites REPORT.md from the whole records.csv. Usage: python3 tools/concordia/balance_lab/make_report.py"""
import csv, glob, json, math, os, subprocess, collections, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
LAB = os.path.join(ROOT, "tools/concordia/balance_lab")
rows = list(csv.DictReader(open(os.path.join(LAB, "records.csv"))))
Z = 1.645


def wilson(w, n):
    if n == 0: return (0, 1)
    p = w / n; d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return c - h, c + h


def score(r, side):  # 1 win, .5 draw, 0 loss for side
    return 1 if r["winner"] == side else 0.5 if r["winner"] == "draw" else 0


def power(deck):
    try:
        out = subprocess.run(["python3", ROOT + "/tools/concordia/deck_tier.py", ROOT + "/forge-gui/res/adventure/Concordia/" + deck, "--json"],
                             capture_output=True, text=True).stdout
        d = json.loads(out); d = d[0] if isinstance(d, list) else d
        return d["power"]
    except Exception:
        return None


inner = [r for r in rows if r["kind"] == "inner"]
bonus = [r for r in rows if r["kind"] == "bonus"]
L = ["# Deck balance report", "", "Generated %s from %d games (%d inner-tier, %d bonus). Intervals are 90%% Wilson; draws count half."
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%MZ"), len(rows), len(inner), len(bonus)), ""]
allgames = collections.Counter()
for r in rows:
    allgames[r["deck_a"]] += 1; allgames[r["deck_b"]] += 1
L += ["## Inner-tier results by tier", ""]
outliers = []
for t in "12345":
    g = [r for r in inner if r["tier"] == t]
    if not g: continue
    s1 = sum(1 for r in g if r["winner"] == r["first"]); to = sum(int(r["timeout"]) for r in g)
    lo, hi = wilson(s1, len(g))
    L.append("### Tier %s: %d games, seat-one win rate %.0f%% (%.0f-%.0f%%), timeouts %d%%" % (t, len(g), 100 * s1 / len(g), 100 * lo, 100 * hi, 100 * to // len(g)))
    st = collections.defaultdict(lambda: [0.0, 0])
    for r in g:
        for side, k in (("a", "deck_a"), ("b", "deck_b")):
            st[r[k]][0] += score(r, side); st[r[k]][1] += 1
    L += ["", "| deck | games | win rate | 90% interval |", "|---|---|---|---|"]
    for d, (w, n) in sorted(st.items(), key=lambda x: -x[1][0] / x[1][1]):
        lo, hi = wilson(w, n)
        L.append("| %s | %d | %.0f%% | %.0f-%.0f%% |" % (os.path.basename(d), n, 100 * w / n, 100 * lo, 100 * hi))
        if lo > .5 or hi < .5: outliers.append((t, d, n, w / n, lo, hi))
    L.append("")
L += ["## Outliers (interval clear of 50%)", "", "Deck power is read fresh from deck_tier.py. The card-power scale changed on 2026-10-20 at 16:45 UTC (EDHREC popularity added); power values from before then are not comparable.", ""]
if outliers:
    L += ["| tier | deck | games | win rate | power |", "|---|---|---|---|---|"]
    for t, d, n, p, lo, hi in outliers:
        L.append("| %s | %s | %d | %.0f%% (%.0f-%.0f%%) | %s |" % (t, os.path.basename(d), n, 100 * p, 100 * lo, 100 * hi, power(d)))
else:
    L.append("None yet: with only a few games per deck no interval clears 50%.")
L += ["", "## Bonus impact (enemy = side a; matched sets of 4 games, same pairing and seats)", "",
      "| bonus | sets | enemy win with | without | diff | avg turns with | without |", "|---|---|---|---|---|---|---|"]
by = collections.defaultdict(lambda: collections.defaultdict(list))
for r in bonus:
    by[r["bonus_a"] or "none"][(r["deck_a"], r["deck_b"], r["tier"], r["utc"])].append(r)
base = collections.defaultdict(list)
res = []
for b, sets in by.items():
    if b == "none": continue
    # pair each bonus set with the no-bonus games of the same pairing and timestamp
    wi = [r for s in sets.values() for r in s]
    wo = [r for r in bonus if not r["bonus_a"] and any((r["deck_a"], r["deck_b"], r["utc"]) == (k[0], k[1], k[3]) for k in sets)]
    n1, n0 = len(wi), len(wo)
    if not n1 or not n0: continue
    p1 = sum(score(r, "a") for r in wi) / n1; p0 = sum(score(r, "a") for r in wo) / n0
    se = math.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
    t1 = sum(int(r["turns"]) for r in wi) / n1; t0 = sum(int(r["turns"]) for r in wo) / n0
    res.append((b, n1 // 2 * 2, p1, p0, p1 - p0, Z * se, t1, t0))
for b, s, p1, p0, df, ci, t1, t0 in sorted(res, key=lambda x: -x[4]):
    L.append("| %s | %d | %.0f%% | %.0f%% | %+.0f pts (+/-%.0f) | %.1f | %.1f |" % (b, s / 2, 100 * p1, 100 * p0, 100 * df, 100 * ci, t1, t0))
L += ["", "(a set = 2 games with the bonus + 2 without, seats swapped. Differences use a normal approximation, so +/-0 at 0% or 100% means too few games. Each bonus has only a few games so far; the intervals are wide.)", ""]
heavy = [x for x in res if x[4] >= .25]
small = [x for x in res if abs(x[4]) < .25]
L += ["## Coverage", "", "Decks with fewer than 4 games: %d of %d seen. Games per deck: min %d, median %d, max %d." % (
    sum(1 for v in allgames.values() if v < 4), len(allgames), min(allgames.values()), sorted(allgames.values())[len(allgames) // 2], max(allgames.values())),
    "Not yet in the record: " + ", ".join(sorted(set(["land", "onedrop", "land+onedrop", "life5", "arena", "staff", "legion", "market", "bedlam", "hornet", "life10"]) - set(by))) + ".", ""]
L += ["## What this suggests", ""]
L.append("- Bonuses with a large swing so far (>=25 points, few games, treat as a lead only): " + (", ".join("%s (%+.0f)" % (x[0], 100 * x[4]) for x in heavy) or "none") + ".")
L.append("- Bonuses within +/-25 points: " + (", ".join("%s (%+.0f)" % (x[0], 100 * x[4]) for x in small) or "none") + ".")
L.append("- More matched sets per bonus are needed before proposing a change; the hourly batches keep adding them, least-tested bonus first.")
open(os.path.join(LAB, "REPORT.md"), "w").write("\n".join(L) + "\n")

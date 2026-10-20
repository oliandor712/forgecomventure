#!/usr/bin/env python3
"""Rewrites REPORT.md from the whole records.csv. Usage: python3 tools/concordia/balance_lab/make_report.py"""
import csv, glob, json, math, os, subprocess, collections, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
LAB = os.path.join(ROOT, "tools/concordia/balance_lab")
rows = list(csv.DictReader(open(os.path.join(LAB, "records.csv"), newline="")))
REBUILD = "440176a2"  # deck rebuild (main session, 2026-10-20): rows at or after this commit are on the new decks
_new = {}
REBUILD2 = "58aa312f"  # tier 1-2 decks rebuilt again with a raised floor: T1-2 rows before it are old decks


def is_new(r):
    base = REBUILD2 if r["tier"] in ("1", "2") else REBUILD
    k = (r["commit"], base)
    if k not in _new:
        _new[k] = subprocess.run(["git", "merge-base", "--is-ancestor", base, r["commit"]], cwd=ROOT).returncode == 0
    return _new[k]
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


inner_all = [r for r in rows if r["kind"] == "inner"]
inner = [r for r in inner_all if is_new(r)]  # current balance: new decks only
bonus = [r for r in rows if r["kind"] == "bonus"]
L = ["# Deck balance report", "", "Generated %s from %d games (%d inner-tier, %d bonus). Intervals are 90%% Wilson; draws count half."
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%MZ"), len(rows), len(inner_all), len(bonus)), "",
     "Inner-tier tables below use only the **new decks** (rows at or after the rebuild commit: %s for tiers 3-5, %s for tiers 1-2): %d inner games; %d inner games on the old decks are left out. Bonus impact pools old and new rows, since a matched set compares the same pairing." % (REBUILD, REBUILD2, len(inner), len(inner_all) - len(inner)), ""]
to_rows = [r for r in rows if int(r["timeout"])]
L += ["Timeouts: %d. %s" % (len(to_rows), "; ".join("%s vs %s, %s, turn %s (bonus %s, life %s/%s)" % (os.path.basename(r["deck_a"]), os.path.basename(r["deck_b"]), r["kind"], r["turns"], r["bonus_a"] or "none", r["life_a"], r["life_b"]) for r in to_rows) or "none"), ""]
allgames = collections.Counter()
for r in rows:
    allgames[r["deck_a"]] += 1; allgames[r["deck_b"]] += 1
L += ["## Inner-tier results by tier (new decks)", ""]
if not inner: L += ["No inner-tier games on the new decks yet.", ""]
outliers = []
for t in "12345":
    g = [r for r in inner if r["tier"] == t]
    if not g: continue
    s1 = sum(1 for r in g if r["winner"] == r["first"]); to = sum(int(r["timeout"]) for r in g)
    lo, hi = wilson(s1, len(g))
    L.append("### Tier %s: %d games, seat-one win rate %.0f%% (%.0f-%.0f%%), timeouts %d%%" % (t, len(g), 100 * s1 / len(g), 100 * lo, 100 * hi, 100 * to // len(g)))
    st = collections.defaultdict(lambda: [0.0, 0]); tn = collections.defaultdict(list)
    for r in g:
        for side, k in (("a", "deck_a"), ("b", "deck_b")):
            st[r[k]][0] += score(r, side); st[r[k]][1] += 1; tn[r[k]].append(int(r["turns"]))
    L += ["", "| deck | games | win rate | 90% interval | mean turns | power |", "|---|---|---|---|---|---|"]
    for d, (w, n) in sorted(st.items(), key=lambda x: -x[1][0] / x[1][1]):
        lo, hi = wilson(w, n)
        L.append("| %s | %d | %.0f%% | %.0f-%.0f%% | %.1f | %s |" % (os.path.basename(d), n, 100 * w / n, 100 * lo, 100 * hi, sum(tn[d]) / n, power(d)))
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
    if b == "none" or b.startswith("life"): continue  # life bonuses eliminated by the user, 2026-10-20
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
STARTER_TUNE = "90b337c5"  # starters tuned to deck power 27; earlier starter games are old starters
_st = {}


def st_new(r):
    if r["commit"] not in _st:
        _st[r["commit"]] = subprocess.run(["git", "merge-base", "--is-ancestor", STARTER_TUNE, r["commit"]], cwd=ROOT).returncode == 0
    return _st[r["commit"]]


L += ["## Starter opponents in bonus sets (tuned starters only, Normal and Alt separate)", "",
      "Enemy win rate against each starter file, split by with and without bonus. Games before the tune (%s) are on old starters and are left out: %d of %d starter games." % (
          STARTER_TUNE, sum(1 for r in bonus if "/starter/" in r["deck_b"] and not st_new(r)), sum(1 for r in bonus if "/starter/" in r["deck_b"])), "",
      "| starter | games without bonus | enemy win | games with bonus | enemy win |", "|---|---|---|---|---|"]
sg = collections.defaultdict(lambda: [[0, 0.0], [0, 0.0]])
for r in bonus:
    if "/starter/" in r["deck_b"] and st_new(r):
        k = 1 if r["bonus_a"] else 0
        sg[os.path.basename(r["deck_b"])][k][0] += 1; sg[os.path.basename(r["deck_b"])][k][1] += score(r, "a")
for d, ((n0, w0), (n1, w1)) in sorted(sg.items()):
    L.append("| %s | %d | %s | %d | %s |" % (d, n0, "%.0f%%" % (100 * w0 / n0) if n0 else "-", n1, "%.0f%%" % (100 * w1 / n1) if n1 else "-"))
if not sg: L.append("| none yet | | | | |")
L += [""]
L += ["## Coverage", "", "Decks with fewer than 4 games: %d of %d seen. Games per deck: min %d, median %d, max %d." % (
    sum(1 for v in allgames.values() if v < 4), len(allgames), min(allgames.values()), sorted(allgames.values())[len(allgames) // 2], max(allgames.values())),
    "Not yet in the record: " + ", ".join(sorted(set(["land", "onedrop", "land+onedrop", "arena", "staff", "legion", "market", "bedlam", "hornet"]) - set(by))) + ".", ""]
L += ["## What this suggests", ""]
L.append("- Bonuses with a large swing so far (>=25 points, few games, treat as a lead only): " + (", ".join("%s (%+.0f)" % (x[0], 100 * x[4]) for x in heavy) or "none") + ".")
L.append("- Bonuses within +/-25 points: " + (", ".join("%s (%+.0f)" % (x[0], 100 * x[4]) for x in small) or "none") + ".")
L.append("- More matched sets per bonus are needed before proposing a change; the hourly batches keep adding them, least-tested bonus first.")
open(os.path.join(LAB, "REPORT.md"), "w").write("\n".join(L) + "\n")

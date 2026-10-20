#!/usr/bin/env python3
"""One batch of the deck balance lab: inner-tier pairings and bonus matched sets, appended to records.csv.
Usage: python3 tools/concordia/balance_lab/run_batch.py [--budget 600] [--seed N]
Plays via tools/concordia/sim/run.sh BonusSim; no new game starts after minute 8 of the batch."""
import argparse, csv, glob, os, random, re, subprocess, sys, time, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DECKS = "forge-gui/res/adventure/Concordia/"
LAB = os.path.join(ROOT, "tools/concordia/balance_lab")
REC = os.path.join(LAB, "records.csv")
HEADER = "utc,commit,kind,tier,deck_a,deck_b,life_a,life_b,bonus_a,bonus_b,first,winner,turns,timeout".split(",")
LIFE = {1: 10, 2: 15, 3: 25, 4: 30, 5: 35}
BASIC = {"W": "Plains", "U": "Island", "B": "Swamp", "R": "Mountain", "G": "Forest"}
STAFF = {"W": "Staff of the Sun Magus", "U": "Staff of the Mind Magus", "B": "Staff of the Death Magus",
         "R": "Staff of the Flame Magus", "G": "Staff of the Wild Magus"}
GENERIC_1DROP = {"W": "Adanto Vanguard", "U": "Faerie Miscreant", "B": "Dark Confidant", "R": "Goblin Guide", "G": "Llanowar Elves"}
PREMADE = {"arena": "Phyrexian Arena", "legion": "Legion's Landing", "market": "Black Market",
           "bedlam": "Bedlam", "hornet": "Hornet Nest"}
BONUSES = ["land", "onedrop", "land+onedrop", "life5", "arena", "staff", "legion", "market", "bedlam", "hornet", "life10"]


def rel(p): return os.path.relpath(p, ROOT + "/" + DECKS) if os.path.isabs(p) else p[len(DECKS):] if p.startswith(DECKS) else p


def decks(sub): return sorted(glob.glob(os.path.join(ROOT, DECKS, "decks", sub, "*.dck")))


def colors(deck):
    m = re.match(r"T\d_([WUBRG]+)_", os.path.basename(deck)) or re.match(r"([WUBRG])_Starter", os.path.basename(deck))
    return m.group(1) if m else ""


def one_drop(deck, color):
    names = []
    sec = None
    for ln in open(deck):
        ln = ln.strip()
        if ln.startswith("["): sec = ln; continue
        m = re.match(r"\d+ ([^|]+)", ln)
        if m and sec == "[Main]": names.append(m.group(1).strip())
    for n in sorted(set(names)):
        f = os.path.join(ROOT, "forge-gui/res/cardsfolder", n[0].lower(), re.sub(r"[^a-z0-9_]", "", n.lower().replace(" ", "_").replace("-", "_")) + ".txt")
        if os.path.exists(f):
            t = open(f).read()
            if re.search(r"^ManaCost:(\d|[WUBRG])\s*$", t, re.M) and re.search(r"^ManaCost:[WUBRG]\s*$", t, re.M) and "Types:Creature" in t and "\nAlternateMode" not in t:
                return n
    return GENERIC_1DROP[color]


def bonus_cards(bonus, deck, color):
    out = []
    if bonus in ("land", "land+onedrop"): out.append(BASIC[color])
    if bonus in ("onedrop", "land+onedrop"): out.append(one_drop(deck, color))
    if bonus == "staff": out.append(STAFF[color])
    if bonus in PREMADE: out.append(PREMADE[bonus])
    return ",".join(out) or "-"


def load():
    if not os.path.exists(REC): return []
    return list(csv.DictReader(open(REC)))


def counts(rows):
    c = {}
    for r in rows:
        for k in ("deck_a", "deck_b"): c[r[k]] = c.get(r[k], 0) + 1
    return c


def pick(pool, c, rng, n=1, exclude=()):
    pool = [d for d in pool if d not in exclude]
    w = [1.0 / (1 + c.get(rel(d), 0)) for d in pool]
    out = []
    for _ in range(n):
        d = rng.choices(pool, w)[0]
        i = pool.index(d); pool.pop(i); w.pop(i); out.append(d)
    return out


def play(games, budget_end):
    """games: list of dicts. One JVM per call; returns parsed GAME lines."""
    args = []
    for g in games:
        args += [g["da"], str(g["la"]), g["xa"], g["db"], str(g["lb"]), g["xb"], g["first"], g["label"]]
    p = subprocess.run([ROOT + "/tools/concordia/sim/run.sh", "BonusSim", "forge-gui/", "150"] + args, cwd=ROOT,
                       capture_output=True, text=True, timeout=max(60, budget_end - time.time() + 200))
    res = {}
    for ln in p.stdout.splitlines():
        if ln.startswith("GAME\t"):
            _, label, first, w, turns, to = ln.split("\t")
            res[label] = (first, w, int(turns), int(to))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=600)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--pairings", type=int, default=4)
    ap.add_argument("--sets", type=int, default=2)
    o = ap.parse_args()
    rng = random.Random(o.seed)
    start = time.time(); stop_new = start + 480; end = start + o.budget
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    rows = load(); c = counts(rows)
    new = not os.path.exists(REC)
    f = open(REC, "a", newline=""); w = csv.writer(f)
    if new: w.writerow(HEADER)
    nbonus_done = {b: 0 for b in BONUSES}
    for r in rows:
        if r["kind"] == "bonus": nbonus_done[r["bonus_a"] or r["bonus_b"] or "?"] = nbonus_done.get(r["bonus_a"] or r["bonus_b"], 0) + 1
    plan = [("inner",)] * o.pairings + [("bonus",)] * o.sets
    played = 0
    for step in plan:
        if time.time() > stop_new: break
        utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        games, meta = [], {}
        if step[0] == "inner":
            t = rng.randint(1, 5)
            a, b = pick(decks("tier%d" % t), c, rng, 2)
            for i, first in enumerate(["a", "b"]):
                lab = "i%d" % i
                games.append(dict(da=a, la=LIFE[t], xa="-", db=b, lb=LIFE[t], xb="-", first=first, label=lab))
                meta[lab] = ("inner", t, a, b, LIFE[t], LIFE[t], "", "")
        else:
            bonus = min(BONUSES, key=lambda b: (nbonus_done.get(b, 0), rng.random()))
            t = rng.choice([1, 1, 2, 2, 2, 3, 4, 5])
            mono = [d for d in decks("tier%d" % t) if len(colors(d)) == 1] or decks("tier%d" % t)
            enemy = pick(mono, c, rng)[0]
            col = colors(enemy)[0]
            if t <= 2: opp = rng.choice([d for d in decks("starter") if colors(d) != col] or decks("starter"))
            else: opp = pick(decks("tier%d" % (t + 1)) if t < 5 else decks("tier5"), c, rng)[0]
            # equal life: the higher tier's low end (opponent stands one tier above for t>=3; starter ~ tier of enemy)
            life = LIFE[min(t + 1, 5)] if t > 2 else LIFE[t]
            xe = bonus_cards(bonus, enemy, col)
            lb_extra = 5 if bonus == "life5" else 10 if bonus == "life10" else 0
            if bonus.startswith("life"): xe = "-"
            n = 0
            for with_bonus in (True, False):
                for first in ("a", "b"):
                    lab = "b%d" % n; n += 1
                    bb = bonus if with_bonus else ""
                    games.append(dict(da=enemy, la=life + (lb_extra if with_bonus else 0), xa=xe if with_bonus else "-",
                                      db=opp, lb=life, xb="-", first=first, label=lab))
                    meta[lab] = ("bonus", t, enemy, opp, life + (lb_extra if with_bonus else 0), life, bb, "")
        res = play(games, end)
        for g in games:
            r = res.get(g["label"])
            if not r: continue
            kind, t, da, db, la, lb, ba, bb = meta[g["label"]]
            w.writerow([utc, commit, kind, t, rel(da), rel(db), la, lb, ba, bb, r[0], r[1], r[2], r[3]])
            c[rel(da)] = c.get(rel(da), 0) + 1; c[rel(db)] = c.get(rel(db), 0) + 1
            played += 1
        f.flush()
        if step[0] == "bonus": nbonus_done[bonus] += 1
    f.close()
    print("played", played, "games in %.0fs" % (time.time() - start))


main()

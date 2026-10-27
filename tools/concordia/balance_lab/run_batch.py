#!/usr/bin/env python3
"""One batch of the deck balance lab: inner-tier pairings and bonus matched sets, appended to records.csv.
Usage: python3 tools/concordia/balance_lab/run_batch.py [--seed N]
Plays via tools/concordia/sim/run.sh BonusSim; no new game starts after minute 8 of the batch."""
import argparse, collections, csv, glob, json, os, random, re, subprocess, sys, time, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DECKS = "forge-gui/res/adventure/Concordia/"
LAB = os.path.join(ROOT, "tools/concordia/balance_lab")
WORKER = os.environ.get("BALANCE_WORKER", "")  # a second agent sets e.g. ailab: it appends to records_ailab.csv, everyone reads records*.csv
REC = os.path.join(LAB, "records_%s.csv" % WORKER if WORKER else "records.csv")
HEADER = "utc,commit,kind,tier,deck_a,deck_b,life_a,life_b,bonus_a,bonus_b,first,winner,turns,timeout".split(",")
LIFE = {1: 10, 2: 15, 3: 25, 4: 30, 5: 35}
BASIC = {"W": "Plains", "U": "Island", "B": "Swamp", "R": "Mountain", "G": "Forest"}
STAFF = {"W": "Staff of the Sun Magus", "U": "Staff of the Mind Magus", "B": "Staff of the Death Magus",
         "R": "Staff of the Flame Magus", "G": "Staff of the Wild Magus"}
GENERIC_1DROP = {"W": "Adanto Vanguard", "U": "Faerie Miscreant", "B": "Dark Confidant", "R": "Goblin Guide", "G": "Llanowar Elves"}
PREMADE = {"arena": "Phyrexian Arena", "legion": "Legion's Landing", "market": "Black Market",
           "bedlam": "Bedlam", "hornet": "Hornet Nest"}
# main session, 2026-10-20: land, onedrop, land+onedrop, life5 against arena, staff, life10 first; the rest later
# user, 2026-10-20: life bonuses eliminated as an option; T1-2 order from the bonus review: land and onedrop alone,
# then land+onedrop, 3+ pairings each against all five starters
# 2026-10-20: small bonuses against the premade arena and staff, 5 matched sets each; no life bonuses;
# bedlam, hornet, market, legion wait
STARTER_EPOCH = "2026-10-21T01:25:00Z"  # first batch after the starter rework 5439eb01 (the 01:11 batch ran the old decks); earlier starter games are old decks
BONUSES = ["land", "onedrop", "land+onedrop", "arena", "staff"]


LOCK = "/tmp/claude-0/-home-user-forgecomventure/df4f5a99-d818-5913-95ec-ecc9b6e060fd/scratchpad/balance_lab" + os.environ.get("BALANCE_WORKER", "") + os.environ.get("BALANCE_SLICE", "").replace("/", "of") + ".lock"  # one batch at a time: hourly and mass runs


def lock_held():
    try:
        pid = int(open(LOCK).read().strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def green_pool():
    """Decks of the Green zone's enemies (world/enemies.json entries named Green ...): the priority pool for inner games."""
    en = json.load(open(ROOT + "/" + DECKS + "world/enemies.json"))
    out = set()
    for e in en:
        if str(e.get("name", "")).startswith("Green"):
            out.update(ROOT + "/" + DECKS + d for d in e.get("deck", []))
    return sorted(p for p in out if os.path.exists(p))


SHARDS = ["W", "U", "B"]  # one shard per hour, round-robin by UTC hour; R, G belong to the AI lab and multicolour to the main session (2026-10-21)


def shard_of(deck):
    c = colors(deck)
    return c if len(c) == 1 else "multi"


def shard_decks(shard):
    return [d for d in glob.glob(os.path.join(ROOT, DECKS, "decks", "tier*", "*.dck")) if shard_of(d) == shard]


def rel(p): return os.path.relpath(p, ROOT + "/" + DECKS) if os.path.isabs(p) else p[len(DECKS):] if p.startswith(DECKS) else p


def decks(sub, pool=None):
    all_ = sorted(glob.glob(os.path.join(ROOT, DECKS, "decks", sub, "*.dck")))
    if pool is None: return all_
    sel = [d for d in all_ if d in pool]
    return sel if len(sel) >= 2 else all_


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
    rows = []
    for p in sorted(glob.glob(os.path.join(LAB, "records*.csv"))): rows += list(csv.DictReader(open(p)))
    return rows


REBUILD = "440176a2"  # deck rebuild: coverage counts only games on the new decks
_new = {}
REBUILD_T1 = "f1139925"  # tier 1 regenerated with 30-34 creatures: T1 rows before it are old T1 decks
REBUILD2 = "58aa312f"  # tier 1-2 decks rebuilt again with a raised floor: T1-2 rows before it are old decks


def is_new(r):
    base = REBUILD_T1 if r["tier"] == "1" else REBUILD2 if r["tier"] == "2" else REBUILD
    k = (r["commit"], base)
    if k not in _new:
        _new[k] = subprocess.run(["git", "merge-base", "--is-ancestor", base, r["commit"]], cwd=ROOT).returncode == 0
    return _new[k]


def counts(rows):
    c = {}
    for r in rows:
        if not is_new(r): continue
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
    # Phase logging is standard for every simulation (user, 2026-10-21): each game writes its phase log to a local batch folder,
    # then phase_digest.py compresses it to tools/concordia/ai_lab/digests/<worker>-<utc>/ (pushed with the records) and the raw logs are deleted.
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    batch = "%s-%s-%d" % (WORKER or "lab", stamp, os.getpid())
    logdir = os.path.join(ROOT, "tools/concordia/ai_lab/results/balance_logs", batch)
    env = dict(os.environ, SIM_JAVA_OPTS="-Dlogdir=" + logdir + " -Daidecisionlog=1" + (" -Dseed=" + os.environ["BALANCE_SEED"] if os.environ.get("BALANCE_SEED") else ""))
    p = subprocess.run([ROOT + "/tools/concordia/sim/run.sh", "BonusSim", "forge-gui/", "150"] + args, cwd=ROOT,
                       capture_output=True, text=True, timeout=None, env=env)
    if os.path.isdir(logdir):
        try:
            subprocess.run([sys.executable, ROOT + "/tools/concordia/ai_lab/phase_digest.py", logdir, "--into", "%s-%s" % (WORKER or "lab", stamp[:11])], cwd=ROOT, capture_output=True, text=True, timeout=300)
        finally:
            if not os.environ.get("KEEP_PHASE_LOGS"):
                import shutil; shutil.rmtree(logdir, ignore_errors=True)  # no compute cap (user, 2026-10-21); each game still has its own 150 s limit in BonusSim
    res = {}
    for ln in p.stdout.splitlines():
        if ln.startswith("GAME\t"):
            _, label, first, w, turns, to = ln.split("\t")
            res[label] = (first, w, int(turns), int(to))
    return res


def target_for(d):  # games per deck (user, 2026-10-21): 25 for AI decks, 40 for the starters
    return 40 if "starter" in d else 25


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--pairings", type=int, default=4)
    ap.add_argument("--pool", default="shard", help="shard (this hour's colour shard, default), green (priority) or all")
    ap.add_argument("--shard", default=None, help="W, U, B, R, G or multi; default is the hour's shard in the round-robin")
    ap.add_argument("--sets", type=int, default=2)
    ap.add_argument("--until-done", action="store_true", help="no time caps (user, 2026-10-21): keep batching until every deck in the shard has its target games (25 AI decks, 40 starters)")
    o = ap.parse_args()
    rng = random.Random(o.seed)
    if o.pool == "shard":
        shard = o.shard or SHARDS[datetime.datetime.now(datetime.timezone.utc).hour % len(SHARDS)]
        pool = set(shard_decks(shard))
        sl = os.environ.get("BALANCE_SLICE")  # "k/n": this process takes every n-th deck of the sorted shard, so n processes never share a deck
        if sl:
            k, n = map(int, sl.split("/")); pool = set(d for i, d in enumerate(sorted(pool)) if i % n == k)
        print("shard", shard, len(pool), "decks")
    else:
        pool = None if o.pool == "all" else set(green_pool())
    start = time.time()
    stop_new = end = float("inf")  # no compute cap (user, 2026-10-21)
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    rows = load(); c = counts(rows)
    new = not os.path.exists(REC)
    f = open(REC, "a", newline=""); w = csv.writer(f)
    if new: w.writerow(HEADER)
    nbonus_done = {b: 0 for b in BONUSES}
    for r in rows:
        if r["kind"] == "bonus": nbonus_done[r["bonus_a"] or r["bonus_b"] or "?"] = nbonus_done.get(r["bonus_a"] or r["bonus_b"], 0) + 1
    def underfilled():  # live counts: keep going while a deck in the shard is below 40 games (H28)
        ds = pool if pool is not None else [d for t in range(1, 6) for d in decks("tier%d" % t)]
        return any(c.get(rel(d), 0) < target_for(d) for d in ds)

    def plan_steps():
        if not o.until_done:
            yield from [("inner",)] * o.pairings + [("bonus",)] * o.sets
            return
        while underfilled():
            yield from [("inner",)] * o.pairings + [("bonus",)] * o.sets
    played = 0
    for step in plan_steps():
        if time.time() > stop_new: break
        utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        games, meta = [], {}
        if step[0] == "inner":
            ts = [x for x in range(1, 6) if pool is None or len(decks("tier%d" % x, pool)) >= 2 and any(d in pool for d in decks("tier%d" % x))]
            t = rng.choice(ts or [1, 2, 3, 4, 5])
            a, b = pick(decks("tier%d" % t, pool), c, rng, 2)
            for i, first in enumerate(["a", "b"]):
                lab = "i%d" % i
                games.append(dict(da=a, la=LIFE[t], xa="-", db=b, lb=LIFE[t], xb="-", first=first, label=lab))
                meta[lab] = ("inner", t, a, b, LIFE[t], LIFE[t], "", "")
        else:
            bonus = min(BONUSES, key=lambda b: (nbonus_done.get(b, 0), rng.random()))
            t = rng.choice([1, 2])
            mono = [d for d in decks("tier%d" % t, pool) if len(colors(d)) == 1] or decks("tier%d" % t)
            enemy = pick(mono, c, rng)[0]
            col = colors(enemy)[0]
            if t <= 2:
                # starter games count only since the last starter rework (5439eb01), so Normal and Alt both start at zero
                new = [r for r in rows if r["utc"] >= STARTER_EPOCH]
                used = collections.Counter(r["deck_b"] for r in new if r["kind"] == "bonus" and r["bonus_a"] == bonus)
                # starters split 50/50 between each colour's two versions (Normal and Alt; user, 2026-10-20):
                # least-used colour first, then that colour's less-played version over all starter games
                allst = collections.Counter(r[k] for r in new for k in ("deck_a", "deck_b") if "/starter/" in r[k])
                st = decks("starter")
                byc = collections.defaultdict(list)
                for d in st: byc[os.path.basename(d)[0]].append(d)
                cpick = min(byc, key=lambda c: (sum(used.get(rel(d), 0) for d in byc[c]), rng.random()))
                opp = min(byc[cpick], key=lambda d: (allst.get(rel(d), 0), rng.random()))
            else: opp = pick(decks("tier%d" % (t + 1)) if t < 5 else decks("tier5"), c, rng)[0]
            # equal life: the higher tier's low end (opponent stands one tier above for t>=3; starter ~ tier of enemy)
            life = LIFE[min(t + 1, 5)] if t > 2 else LIFE[t]
            xe = bonus_cards(bonus, enemy, col)
            lb_extra = 0  # life bonuses eliminated (user, 2026-10-20): both sides at equal life
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




def main():
    if lock_held():
        print("another batch holds the lock; skipping this run")
        return
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    open(LOCK, "w").write(str(os.getpid()))
    try:
        run()
    finally:
        os.remove(LOCK)


if __name__ == "__main__":
    main()

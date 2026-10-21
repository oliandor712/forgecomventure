#!/usr/bin/env python3
"""Phase-logged balance batches for the AI lab (user request, 2026-10-21).

Each batch plays two pairings, 10 games each (5 with deck A first, 5 with deck B first), equal life:
  1. aggro vs ramp (same tier, archetypes from build_queue.archetype)
  2. a player starter vs a tier 2 midrange deck
Every game writes its phase log (turn, phase, type, message; same columns as ai_lab/results) to
tools/concordia/ai_lab/results/balance_logs/<worker>-<batch utc>/<label>.tsv, plus INDEX.tsv (label, decks, first, winner, turns).
The games are also appended to records_<worker>.csv in the normal row format. The logs and the records file are pushed together
with push_records.sh. Usage: BALANCE_WORKER=logs python3 tools/concordia/balance_lab/run_logs.py [batches=1] [--no-push]
"""
import datetime, glob, os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("BALANCE_WORKER", "logs")
import run_batch as rb          # play(), REC, HEADER, LIFE, rel(), load(), counts()
import build_queue as bq        # archetype()
import csv

ROOT = rb.ROOT
WORKER = os.environ["BALANCE_WORKER"]
LOGROOT = os.path.join(ROOT, "tools/concordia/ai_lab/results/balance_logs")


def by_arch(tier):
    out = {}
    for d in rb.decks("tier%d" % tier):
        out.setdefault(bq.archetype(d), []).append(d)
    return out


def pairing_aggro_ramp(rng, c):
    tiers = [t for t in range(1, 6) if by_arch(t).get("aggro") and by_arch(t).get("ramp")]
    if not tiers: return None
    t = rng.choice(tiers); arch = by_arch(t)
    a = rb.pick(list(arch["aggro"]), c, rng, 1)[0]; b = rb.pick(list(arch["ramp"]), c, rng, 1)[0]
    return "AGGRO-RAMP", t, a, b


def pairing_starter_mid(rng, c):
    mids = by_arch(2).get("midrange")
    starters = sorted(glob.glob(os.path.join(ROOT, rb.DECKS, "decks", "starter", "*.dck")))
    if not mids or not starters: return None
    return "STARTER-MID", 2, rb.pick(list(starters), c, rng, 1)[0], rb.pick(list(mids), c, rng, 1)[0]


def run_batch(rng, writer, f, commit):
    utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp = utc.replace(":", "").replace("-", "")
    folder = os.path.join(LOGROOT, "%s-%s" % (WORKER, stamp))
    os.environ["SIM_JAVA_OPTS"] = "-Dlogdir=" + folder
    c = rb.counts(rb.load())
    index, played = [], 0
    for fn in (pairing_aggro_ramp, pairing_starter_mid):
        p = fn(rng, c)
        if not p: continue
        tag, t, a, b = p
        games = []
        for i in range(10):
            games.append(dict(da=a, la=rb.LIFE[t], xa="-", db=b, lb=rb.LIFE[t], xb="-", first="a" if i % 2 == 0 else "b", label="%s_%02d" % (tag, i)))
        res = rb.play(games, 10 ** 7)
        for g in games:
            r = res.get(g["label"])
            if not r: continue
            writer.writerow([utc, commit, "inner", t, rb.rel(a), rb.rel(b), rb.LIFE[t], rb.LIFE[t], "", "", r[0], r[1], r[2], r[3]])
            index.append("\t".join([g["label"], rb.rel(a), rb.rel(b), r[0], r[1], str(r[2])]))
            c[rb.rel(a)] = c.get(rb.rel(a), 0) + 1; c[rb.rel(b)] = c.get(rb.rel(b), 0) + 1
            played += 1
        f.flush()
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, "INDEX.tsv"), "w").write("label\tdeck_a\tdeck_b\tfirst\twinner\tturns\n" + "\n".join(index) + "\n")
    return folder, played


def main():
    batches = int(next((x for x in sys.argv[1:] if x.isdigit()), 1))
    rng = random.Random()
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    new = not os.path.exists(rb.REC)
    f = open(rb.REC, "a", newline=""); w = csv.writer(f)
    if new: w.writerow(rb.HEADER)
    for _ in range(batches):
        folder, played = run_batch(rng, w, f, commit)
        print("batch: %d games, logs in %s" % (played, os.path.relpath(folder, ROOT)))
        if "--no-push" not in sys.argv:
            print(subprocess.run([os.path.join(HERE, "push_records.sh"), os.path.relpath(rb.REC, ROOT), os.path.relpath(folder, ROOT)], cwd=ROOT, capture_output=True, text=True).stdout.strip())
    f.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Concordia simulation suite: one program for setup, runs, phase logging, digests, pushes and reports.

Rolls the balance lab's batch runner, the phase-log tool and the AI test overlay into one command, with the balance lab's
efficiency suggestions A-D built in and the user's archetype rule:
  A  one queue of unfinished work for every worker (no colour shards): workers rebuild the state from all suite records
     after each pull and take the cells that still need games, least-known first
  B  foreground chunks: one JVM per chunk of many games (--chunk, default 24), a safe push at the end of every call
  C  adaptive sampling: a cell stops when its 90% Wilson interval is narrow enough (--halfwidth) or it hit --max
  D  full-history clone check at start (fetches the history if the clone is shallow)
  +  seconds per game, archetype, worker and tier on every row
  *  archetype rule (user, 2026-10-21): decks are grouped by archetype, and each game draws a RANDOM deck from the archetype
     group of each side instead of walking the individual decks. A "cell" is (tier, archetype A, archetype B).
Modes: inner (archetype vs archetype within a tier), starter (a starter vs an enemy archetype at a stage), bonus (matched sets).
Games always have equal life on both sides; no life bonuses; both seats alternate inside every pairing.
Every game writes a phase log, is digested by ai_lab/phase_digest.py (hourly folder per worker) and the raw log is deleted.
The AI test patches (ai_lab/patches/SIM_ACTIVE.txt: 010, 011) are compiled onto the SIM classpath only, never into forge-ai/src.

  python3 tools/concordia/suite/sim_suite.py setup
  python3 tools/concordia/suite/sim_suite.py run [--worker W] [--mode inner|starter|bonus|all] [--minutes 9 | --until-done]
  python3 tools/concordia/suite/sim_suite.py status
  python3 tools/concordia/suite/sim_suite.py report
"""
import argparse, collections, csv, datetime, json, math, os, random, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, os.path.join(ROOT, "tools/concordia/balance_lab"))
if "--worker" in sys.argv:  # the runner reads the worker name at import (records and digest folder names)
    os.environ["BALANCE_WORKER"] = sys.argv[sys.argv.index("--worker") + 1]
import run_batch as rb   # play() (phase log + digest), decks(), LIFE, bonus_cards()
import build_queue as bq  # archetype()

HEADER = ["utc", "commit", "worker", "mode", "tier", "arch_a", "arch_b", "deck_a", "deck_b", "life", "first", "winner", "turns",
          "timeout", "seconds", "bonus"]
BONUSES = ["land", "onedrop", "land+onedrop", "staff"]
TARGET = {1: 0.70, 2: 0.70, 3: 0.50, 4: 0.50, 5: 0.50}  # player win-rate target per tier (H29)


def sh(*cmd, **kw):
    return subprocess.run(list(cmd), cwd=ROOT, capture_output=True, text=True, **kw)


def ensure_full_history():  # suggestion D
    if sh("git", "rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        print("shallow clone: fetching the full history (run_batch counts rows with it)")
        sh("git", "fetch", "--unshallow", "origin", "campaign-design")
        if sh("git", "rev-parse", "--is-shallow-repository").stdout.strip() == "true":
            sys.exit("still shallow; fix the clone before running")


def wilson(wins, n, z=1.645):
    if n == 0: return 0.0, 1.0
    p = wins / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def archetypes():
    path = os.path.join(HERE, "archetypes.json")
    cache = json.load(open(path)) if os.path.exists(path) else {}
    out = {}
    for d in rb.decks("tier1") + rb.decks("tier2") + rb.decks("tier3") + rb.decks("tier4") + rb.decks("tier5"):
        k = rb.rel(d)
        if k not in cache: cache[k] = bq.archetype(d)
        out[d] = cache[k]
    json.dump(cache, open(path, "w"), indent=0, sort_keys=True)
    return out


def load_rows():
    rows = []
    for p in sorted(os.listdir(HERE)):
        if p.startswith("records_suite_") and p.endswith(".csv"):
            rows += list(csv.DictReader(open(os.path.join(HERE, p), newline="")))
    return rows


def groups():
    arch = archetypes()
    tier = {t: [d for d in rb.decks("tier%d" % t)] for t in range(1, 6)}
    g = {t: collections.defaultdict(list) for t in tier}
    for t in tier:
        for d in tier[t]: g[t][arch[d]].append(d)
    return g


def cell_list(g, modes):
    cells = []
    for t in range(1, 6):
        archs = sorted(g[t])
        if modes in ("inner", "all"):
            for i, a in enumerate(archs):
                for b in archs[i:]:
                    if a == b and len(g[t][a]) < 2: continue
                    cells.append(("inner", t, a, b))
        if modes in ("starter", "all"):
            for a in archs: cells.append(("starter", t, "starter", a))
        if modes in ("bonus", "all") and t <= 2:
            for a in archs:
                for bo in BONUSES: cells.append(("bonus", t, a, bo))
    return cells


def stats(rows):
    s = collections.defaultdict(lambda: [0, 0.0])  # key -> [n, wins for side a]
    for r in rows:
        if r["mode"] == "bonus":
            continue
        k = (r["mode"], int(r["tier"]), r["arch_a"], r["arch_b"])
        s[k][0] += 1
        s[k][1] += 1.0 if r["winner"] == "a" else (0.5 if r["winner"] == "draw" else 0.0)
    sets = collections.Counter((int(r["tier"]), r["arch_a"], r["bonus"]) for r in rows if r["mode"] == "bonus" and r["bonus"] and r["first"] == "a")
    return s, sets


def pending(cells, rows, a):
    s, sets = stats(rows)
    todo = []
    for c in cells:
        mode, t, x, y = c
        if mode == "bonus":
            n = sets.get((t, x, y), 0)
            if n < a.bonus_sets: todo.append((0, -(a.bonus_sets - n), c))
            continue
        n, w = s.get(c, (0, 0.0))
        if n >= a.max: continue
        lo, hi = wilson(w, n)
        h = (hi - lo) / 2
        if n < a.min: todo.append((0, n, c))
        elif h > a.halfwidth: todo.append((1, -h, c))
    todo.sort(key=lambda x: (x[0], x[1]))
    return [c for _, _, c in todo]


def draw(rng, g, c, starters):
    mode, t, x, y = c
    life = rb.LIFE[t]
    if mode == "inner":
        a = rng.choice(g[t][x]); pool = [d for d in g[t][y] if d != a]
        return a, rng.choice(pool), life, ""
    if mode == "starter":
        a = rng.choice(starters); b = rng.choice(g[t][y])
        return a, b, (rb.LIFE[min(t + 1, 5)] if t > 2 else life), ""
    enemy = rng.choice(g[t][x]); opp = rng.choice(starters)  # bonus: enemy (side a) with the bonus vs a starter
    return enemy, opp, life, y


def plan_chunk(rng, g, cells, rows, a):
    starters = rb.decks("starter")
    games, meta = [], {}
    todo = pending(cells, rows, a)
    if not todo: return None, None
    i = 0
    while len(games) < a.chunk and todo:
        c = todo[i % len(todo)]; i += 1
        da, db, life, bonus = draw(rng, g, c, starters)
        if c[0] == "bonus":
            col = rb.colors(da)[0] if rb.colors(da) else "W"
            xa = rb.bonus_cards(bonus, da, col)
            order = [(True, "a"), (True, "b"), (False, "a"), (False, "b")]
        else:
            xa = "-"; order = [(False, "a"), (False, "b")]
        for with_bonus, first in order:
            lab = "g%d" % len(games)
            games.append(dict(da=da, la=life, xa=xa if with_bonus else "-", db=db, lb=life, xb="-", first=first, label=lab))
            meta[lab] = (c, da, db, life, bonus if with_bonus else "")
    return games, meta


def cmd_setup(a):
    ensure_full_history()
    r = subprocess.run([os.path.join(ROOT, "tools/concordia/sim/setup.sh")], cwd=ROOT, capture_output=True, text=True)
    print((r.stderr + r.stdout).strip()[-400:])
    active = os.path.join(ROOT, "tools/concordia/ai_lab/patches/SIM_ACTIVE.txt")
    print("test overlay patches:", [l.strip() for l in open(active) if l.strip() and not l.startswith("#")] if os.path.exists(active) else "none")
    print("decks by tier and archetype:", {t: {k: len(v) for k, v in sorted(gr.items())} for t, gr in groups().items()})


def cmd_run(a):
    ensure_full_history()
    if not a.no_pull: sh("git", "pull", "--no-rebase", "-q", "origin", "campaign-design")
    g = groups(); cells = cell_list(g, a.mode); rng = random.Random()
    out = os.path.join(HERE, "records_suite_%s.csv" % a.worker)
    new = not os.path.exists(out)
    f = open(out, "a", newline=""); w = csv.writer(f)
    if new: w.writerow(HEADER)
    commit = sh("git", "rev-parse", "--short", "HEAD").stdout.strip()
    os.environ["BALANCE_WORKER"] = a.worker
    end = time.time() + (a.minutes * 60 if not a.until_done else 10 ** 7)
    played = 0; t0 = time.time(); done = False
    while time.time() < end:
        rows = load_rows()
        games, meta = plan_chunk(rng, g, cells, rows, a)
        if not games: done = True; break
        utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        s0 = time.time(); res = rb.play(games, end + 120); per = (time.time() - s0) / max(1, len(games))
        for gm in games:
            r = res.get(gm["label"])
            if not r: continue
            c, da, db, life, bonus = meta[gm["label"]]
            w.writerow([utc, commit, a.worker, c[0], c[1], c[2], c[3] if c[0] != "bonus" else "", rb.rel(da), rb.rel(db), life,
                        r[0], r[1], r[2], r[3], "%.1f" % per, bonus]); played += 1
        f.flush()
        if a.chunks and played >= a.chunks * a.chunk: break
    f.close()
    print("played %d games in %.0fs (%.1f s/game)%s" % (played, time.time() - t0, (time.time() - t0) / max(1, played), "; DONE: every cell has its answer" if done else ""))
    if not a.no_push:
        r = sh(os.path.join(ROOT, "tools/concordia/balance_lab/push_records.sh"), os.path.relpath(out, ROOT), "tools/concordia/ai_lab/digests")
        print(r.stdout.strip()[-120:])
    print("DONE" if done else "NOT DONE")


def cmd_status(a):
    g = groups(); cells = cell_list(g, a.mode); rows = load_rows()
    todo = pending(cells, rows, a)
    print("games recorded: %d; cells: %d; still needing games: %d" % (len(rows), len(cells), len(todo)))
    sec = [float(r["seconds"]) for r in rows if r.get("seconds")]
    if sec: print("seconds per game: mean %.1f; games per hour per worker: about %d" % (sum(sec) / len(sec), 3600 / (sum(sec) / len(sec))))


def cmd_report(a):
    rows = load_rows(); s, sets = stats(rows)
    L = ["# Simulation suite report", "", "Generated %s from %d games (%s)." % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%MZ"), len(rows),
         ", ".join(sorted({r["worker"] for r in rows})) or "no workers"), "90% Wilson intervals; draws count half. Archetype cells draw a random deck from each archetype group.", ""]
    sec = [float(r["seconds"]) for r in rows if r.get("seconds")]
    to = sum(int(r["timeout"]) for r in rows)
    L += ["Throughput: mean %.1f s per game; timeouts %d of %d." % (sum(sec) / max(1, len(sec)), to, len(rows)), ""]
    for t in range(1, 6):
        cells = sorted(k for k in s if k[0] == "inner" and k[1] == t)
        if not cells: continue
        L += ["## Tier %d: archetype against archetype" % t, "", "| archetype A | archetype B | games | A win rate (90%) |", "|---|---|---|---|"]
        for k in cells:
            n, w = s[k]; lo, hi = wilson(w, n)
            L.append("| %s | %s | %d | %.0f%% (%.0f-%.0f%%) |" % (k[2], k[3], n, 100 * w / n, 100 * lo, 100 * hi))
        L.append("")
    stc = sorted(k for k in s if k[0] == "starter")
    if stc:
        L += ["## Starters (player) against enemy archetypes", "", "| tier | enemy archetype | games | player win rate (90%) | target |", "|---|---|---|---|---|"]
        for k in stc:
            n, w = s[k]; lo, hi = wilson(w, n)
            L.append("| %d | %s | %d | %.0f%% (%.0f-%.0f%%) | %.0f%% |" % (k[1], k[3], n, 100 * w / n, 100 * lo, 100 * hi, 100 * TARGET[k[1]]))
        L.append("")
    br = [r for r in rows if r["mode"] == "bonus"]
    if br:
        agg = collections.defaultdict(lambda: [0, 0, 0, 0])  # with: n, enemy wins; without: n, enemy wins
        for r in br:
            e = 1.0 if r["winner"] == "a" else (0.5 if r["winner"] == "draw" else 0.0)
            key = r["bonus"] or None
            if key: agg[key][0] += 1; agg[key][1] += e
        base = [(1.0 if r["winner"] == "a" else 0.5 if r["winner"] == "draw" else 0.0) for r in br if not r["bonus"]]
        L += ["## Bonus sets (enemy is side A)", "", "| bonus | games with | enemy win with | enemy win without (all bonus-set controls) |", "|---|---|---|---|"]
        for k, v in sorted(agg.items()):
            L.append("| %s | %d | %.0f%% | %.0f%% |" % (k, v[0], 100 * v[1] / v[0], 100 * sum(base) / max(1, len(base))))
        L.append("")
    per = collections.Counter()
    for r in rows:
        if r["mode"] == "inner": per[r["deck_a"]] += 1; per[r["deck_b"]] += 1
    if per:
        v = sorted(per.values())
        L += ["## Deck coverage", "", "Decks drawn at least once: %d; games per drawn deck: min %d, median %d, max %d." % (len(v), v[0], v[len(v) // 2], v[-1]), ""]
    open(os.path.join(HERE, "SUITE_REPORT.md"), "w").write("\n".join(L) + "\n")
    print("wrote tools/concordia/suite/SUITE_REPORT.md")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["setup", "run", "status", "report"])
    ap.add_argument("--worker", default=os.environ.get("BALANCE_WORKER", "suite"))
    ap.add_argument("--mode", default="inner", choices=["inner", "starter", "bonus", "all"])
    ap.add_argument("--minutes", type=float, default=9)
    ap.add_argument("--until-done", action="store_true")
    ap.add_argument("--chunk", type=int, default=24, help="games per JVM call (B)")
    ap.add_argument("--chunks", type=int, default=0, help="stop after this many chunks (0 = by time)")
    ap.add_argument("--min", type=int, default=20, help="minimum games per cell")
    ap.add_argument("--max", type=int, default=200, help="maximum games per cell (C)")
    ap.add_argument("--halfwidth", type=float, default=0.10, help="stop a cell when its 90%% interval half-width is at most this (C)")
    ap.add_argument("--bonus-sets", type=int, default=25, help="matched sets per (tier, enemy archetype, bonus)")
    ap.add_argument("--no-push", action="store_true"); ap.add_argument("--no-pull", action="store_true")
    a = ap.parse_args()
    {"setup": cmd_setup, "run": cmd_run, "status": cmd_status, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()

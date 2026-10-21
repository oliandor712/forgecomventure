#!/usr/bin/env python3
"""Compact decision digest for simulation phase logs.

Turns every per-game phase TSV (turn, phase, type, message) in one or more batch folders into:
  digests/<batch>/decisions.tsv.gz  one row per AI decision with the context it was made in
  digests/<batch>/games.tsv         one row per game: result, length, decisions by side, final life
and keeps a running count so the analysis can run every 100 new games.

Usage:
  python3 tools/concordia/ai_lab/phase_digest.py <batch_folder> [more folders]
  python3 tools/concordia/ai_lab/phase_digest.py --status        games received vs games analysed

Decision kinds: ATTACK, BLOCK, NOBLOCK, CAST, TRIGGER, DAMAGE, LIFE, ZONE (graveyard/exile moves).
Columns of decisions.tsv: game, turn, phase, kind, side, detail, life_a, life_b, n
  life_a / life_b are the life totals at the moment of the decision (from the last LIFE line).
  n is the count of attackers, blockers or damage events on that line, else 1.
Phase lines (PHASE) are dropped; the phase name is kept on each decision row, shortened.
"""
import csv, glob, gzip, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIGESTS = os.path.join(HERE, "digests")
MARKER = os.path.join(DIGESTS, "analysed.txt")  # plain number: games already analysed
STEP = 100

NAME_ID = re.compile(r"\s*\(\d+\)")
ASSIGN_BLOCK = re.compile(r"\b(A|B) assigned (.+?) to block (.+?)(?:\.|$)")
DIDNT_BLOCK = re.compile(r"\b(A|B) didn't block (.+?)(?:\.|$)")
LIFE = re.compile(r"Life: (A|B) (-?\d+) > (-?\d+)")
DAMAGE = re.compile(r"^(.+?) \(\d+\) deals (\d+) combat damage to (A|B)")


def short_phase(p):
    p = p.replace("'s ", " ").replace("Declare ", "Dec").replace(" Step", "").replace("Main phase, ", "M")
    return p.strip()


def names(text):
    return [NAME_ID.sub("", n).strip() for n in re.split(r",| and ", text) if n.strip()]


def starting_life(lines):
    """Starting life per side: the 'before' value of each side's first LIFE line."""
    start = {}
    for line in lines:
        m = LIFE.search(line)
        if m and m.group(1) not in start:
            start[m.group(1)] = int(m.group(2))
    return {"A": start.get("A", 40), "B": start.get("B", 40)}


def parse_game(path, label):
    lines = open(path, errors="ignore").read().splitlines()
    life = starting_life(lines)
    rows, turn = [], 0
    for line in lines:
        r = line.rstrip("\n").split("\t")
        if len(r) < 4:
            continue
        try:
            turn = int(r[0])
        except ValueError:
            continue
        phase, typ, msg = r[1], r[2].rstrip("*"), r[3]
        ph = short_phase(phase)
        def lk():
            return (life["A"], life["B"])
        if typ == "LIFE":
            m = LIFE.search(msg)
            if m:
                life[m.group(1)] = int(m.group(3))
            continue
        if typ == "COMBAT" and "Declare Attackers" in phase and " assigned " in msg:
            side = msg[0]
            body = msg.split(" assigned ", 1)[1].rsplit(" to attack", 1)[0]
            ns = names(body)
            rows.append((turn, ph, "ATTACK", side, "; ".join(ns), *lk(), len(ns)))
        elif typ == "COMBAT" and "Declare Blockers" in phase:
            for m in ASSIGN_BLOCK.finditer(msg):
                rows.append((turn, ph, "BLOCK", m.group(1), f"{names(m.group(2))[0]} blocks {names(m.group(3))[0]}", *lk(), 1))
            for m in DIDNT_BLOCK.finditer(msg):
                rows.append((turn, ph, "NOBLOCK", m.group(1), names(m.group(2))[0], *lk(), 1))
        elif typ == "STACK_ADD":
            m = re.match(r"(A|B) cast (.+)", msg)
            if m:
                rows.append((turn, ph, "CAST", m.group(1), m.group(2).split(" (")[0], *lk(), 1))
            elif msg.startswith("triggered"):
                rows.append((turn, ph, "TRIGGER", "", msg[len("triggered "):].split(" (")[0], *lk(), 1))
        elif typ == "DAMAGE":
            m = DAMAGE.search(msg)
            if m:
                rows.append((turn, ph, "DAMAGE", m.group(3), f"{names(m.group(1))[0]} {m.group(2)}", *lk(), int(m.group(2))))
        elif typ == "ZONE_CHANGE" and "from Battlefield" in msg:
            dest = re.search(r"into (\w+) from Battlefield", msg)
            nm = names(msg.split(" was put ", 1)[0])[0] if " was put " in msg else msg[:40]
            rows.append((turn, ph, "ZONE", "", f"{nm} -> {dest.group(1) if dest else '?'}", *lk(), 1))
    return rows


def write_batch(folder, index):
    batch = os.path.basename(os.path.normpath(folder))
    outdir = os.path.join(DIGESTS, batch)
    os.makedirs(outdir, exist_ok=True)
    games = []
    dec_path = os.path.join(outdir, "decisions.tsv.gz")
    with gzip.open(dec_path, "wt", newline="") as dz:
        w = csv.writer(dz, delimiter="\t")
        w.writerow(["game", "turn", "phase", "kind", "side", "detail", "life_a", "life_b", "n"])
        for path in sorted(glob.glob(os.path.join(folder, "*.tsv"))):
            label = os.path.basename(path)[:-4]
            if label == "INDEX":
                continue
            rows = parse_game(path, label)
            cnt = {"A": {"ATTACK": 0, "BLOCK": 0, "CAST": 0}, "B": {"ATTACK": 0, "BLOCK": 0, "CAST": 0}}
            for r in rows:
                w.writerow([label, *r])
                if r[2] in cnt.get(r[3], {}):
                    cnt[r[3]][r[2]] += 1
            last = rows[-1] if rows else None
            games.append([label, batch, last[0] if last else 0,
                          cnt["A"]["ATTACK"], cnt["B"]["ATTACK"], cnt["A"]["BLOCK"], cnt["B"]["BLOCK"],
                          cnt["A"]["CAST"], cnt["B"]["CAST"],
                          last[5] if last else "", last[6] if last else ""])
    with open(os.path.join(outdir, "games.tsv"), "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["game", "batch", "turns", "attacks_a", "attacks_b", "blocks_a", "blocks_b",
                    "casts_a", "casts_b", "last_life_a", "last_life_b"])
        w.writerows(games)
    return len(games)


def received_games():
    total = 0
    for gp in glob.glob(os.path.join(DIGESTS, "*", "games.tsv")):
        with open(gp) as f:
            total += max(0, sum(1 for _ in f) - 1)
    return total


def analysed():
    try:
        return int(open(MARKER).read().strip())
    except (OSError, ValueError):
        return 0


def main(argv):
    if argv and argv[0] == "--status":
        got, done = received_games(), analysed()
        print(f"games digested {got}, analysed {done}, due for analysis {got - done >= STEP} ({got - done} new)")
        return 0
    if not argv:
        print(__doc__)
        return 2
    os.makedirs(DIGESTS, exist_ok=True)
    for folder in argv:
        n = write_batch(folder, None)
        print(f"digested {n} games from {folder}")
    got, done = received_games(), analysed()
    print(f"games digested {got}, analysed {done}, due for analysis {got - done >= STEP}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

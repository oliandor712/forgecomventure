#!/usr/bin/env python3
"""Compact decision digest for simulation phase logs.

Turns every per-game phase TSV (turn, phase, type, message) in one or more batch folders into:
  digests/<batch>/decisions.tsv.gz  one row per AI decision with the context it was made in
  digests/<batch>/games.tsv         one row per game: result, length, decisions by side, final life
and keeps a running count so the analysis can run every 100 new games.

Usage:
  python3 tools/concordia/ai_lab/phase_digest.py <batch_folder> [more folders]
  python3 tools/concordia/ai_lab/phase_digest.py --into <name> <batch_folder>   append to digests/<name>/
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


META_KEYS = ("deck_a", "deck_b", "tier", "archetype", "colour")


def queue_tags():
    """deck path -> (archetype, colour) from the balance lab's QUEUE.toon (empty if missing)."""
    tags = {}
    path = os.path.join(HERE, "..", "balance_lab", "QUEUE.toon")
    try:
        for line in open(path):
            m = re.match(r"\s+(decks/\S+?\.dck)\|\d+\|\d+\|(\w+)\|\w+\|(\w+)", line)
            if m:
                tags[m.group(1)] = (m.group(3), m.group(2))
    except OSError:
        pass
    return tags


TAGS = queue_tags()


def parse_game(path, label):
    """Return (rows, meta). meta comes from GAME header rows written by BonusSim (deck ids, tier,
    archetype, colour); it is empty for logs written before the header existed."""
    lines = open(path, errors="ignore").read().splitlines()
    life = starting_life(lines)
    rows, turn, meta = [], 0, {}
    for line in lines:
        r = line.rstrip("\n").split("\t")
        if len(r) < 4:
            continue
        try:
            turn = int(r[0])
        except ValueError:
            continue
        phase, typ, msg = r[1], r[2].rstrip("*"), r[3]
        if typ == "GAME":
            meta.update(dict(kv.split("=", 1) for kv in msg.split() if "=" in kv))
            continue
        if typ == "AI_DECISION":
            # log-only AI decision rows (patch 010): "<KIND> <player> turn=<n> key=value ..."
            # the row's own turn column is the game's last turn, so the turn comes from the turn= field
            parts = msg.split()
            kind = parts[0] if parts else "?"
            t = next((int(p[5:]) for p in parts if p.startswith("turn=") and p[5:].isdigit()), turn)
            side = parts[1] if len(parts) > 1 and parts[1] in ("A", "B") else ""
            detail = " ".join(parts[2:])
            rows.append((t, "AI", "AI_" + kind, side, detail, life["A"], life["B"], 1))
            continue
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
            elif re.match(r"(A|B) triggered ", msg):
                # the game log writes triggers as "A triggered <source>" (ETB and other triggers)
                rows.append((turn, ph, "TRIGGER", msg[0], msg.split(" triggered ", 1)[1].split(" (")[0], *lk(), 1))
        elif typ == "DAMAGE":
            m = DAMAGE.search(msg)
            if m:
                rows.append((turn, ph, "DAMAGE", m.group(3), f"{names(m.group(1))[0]} {m.group(2)}", *lk(), int(m.group(2))))
        elif typ == "ZONE_CHANGE" and " was put into " in msg:
            # every zone move, not only battlefield exits: command zone, hand, library, exile, stack
            m = re.search(r"was put into (\w+) from (\w+)", msg)
            nm = names(msg.split(" was put ", 1)[0])[0]
            dest, src = (m.group(1), m.group(2)) if m else ("?", "?")
            detail = f"{nm} -> {dest}" if src == "Battlefield" else f"{nm} -> {dest} from {src}"
            rows.append((turn, ph, "ZONE", "", detail, *lk(), 1))
    return rows, meta


def write_batch(folder, into=None):
    """Digest one raw log folder. With into=None the output is digests/<folder name>/ (rewritten).
    With into=<name> the games are appended to digests/<name>/ and game ids are prefixed with the
    raw folder name, so repeated game labels from different calls stay unique. Folders already in
    the target are skipped, so rerunning a folder never double-counts."""
    batch = os.path.basename(os.path.normpath(folder))
    outdir = os.path.join(DIGESTS, into or batch)
    os.makedirs(outdir, exist_ok=True)
    done_path = os.path.join(outdir, "sources.txt")
    done = set(open(done_path).read().split()) if (into and os.path.exists(done_path)) else set()
    if into and batch in done:
        return 0
    prefix = f"{batch}/" if into else ""
    games = []
    metas = []
    mode = "at" if into else "wt"
    dec_path = os.path.join(outdir, "decisions.tsv.gz")
    games_path = os.path.join(outdir, "games.tsv")
    new_games = not (into and os.path.exists(games_path))
    with gzip.open(dec_path, mode, newline="") as dz:
        w = csv.writer(dz, delimiter="\t")
        if not into or os.path.getsize(dec_path) == 0 or new_games:
            w.writerow(["game", "turn", "phase", "kind", "side", "detail", "life_a", "life_b", "n"])
        for path in sorted(glob.glob(os.path.join(folder, "*.tsv"))):
            label = os.path.basename(path)[:-4]
            if label == "INDEX":
                continue
            rows, meta = parse_game(path, label)
            arch, colour = TAGS.get(meta.get("deck_a", ""), ("", ""))
            meta.setdefault("archetype", arch)
            meta.setdefault("colour", colour)
            metas.append([prefix + label] + [meta.get(k, "") for k in META_KEYS])
            cnt = {"A": {"ATTACK": 0, "BLOCK": 0, "CAST": 0}, "B": {"ATTACK": 0, "BLOCK": 0, "CAST": 0}}
            for r in rows:
                w.writerow([prefix + label, *r])
                if r[2] in cnt.get(r[3], {}):
                    cnt[r[3]][r[2]] += 1
            last = rows[-1] if rows else None
            games.append([prefix + label, batch, last[0] if last else 0,
                          cnt["A"]["ATTACK"], cnt["B"]["ATTACK"], cnt["A"]["BLOCK"], cnt["B"]["BLOCK"],
                          cnt["A"]["CAST"], cnt["B"]["CAST"],
                          last[5] if last else "", last[6] if last else ""])
    header = ["game", "batch", "turns", "attacks_a", "attacks_b", "blocks_a", "blocks_b",
              "casts_a", "casts_b", "last_life_a", "last_life_b"]
    with open(games_path, "a" if into else "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        if not into or new_games:
            w.writerow(header)
        w.writerows(games)
    meta_path = os.path.join(outdir, "games_meta.tsv")
    new_meta = not os.path.exists(meta_path)
    with open(meta_path, "a" if into else "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        if not into or new_meta:
            w.writerow(["game", *META_KEYS])
        w.writerows(metas)
    if into:
        with open(done_path, "a") as f:
            f.write(batch + "\n")
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
    into = None
    if "--into" in argv:
        i = argv.index("--into")
        into = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if argv and argv[0] == "--status":
        got, done = received_games(), analysed()
        print(f"games digested {got}, analysed {done}, due for analysis {got - done >= STEP} ({got - done} new)")
        return 0
    if not argv:
        print(__doc__)
        return 2
    os.makedirs(DIGESTS, exist_ok=True)
    for folder in argv:
        n = write_batch(folder, into)
        print(f"digested {n} games from {folder}" + (f" into {into}" if into else ""))
    got, done = received_games(), analysed()
    print(f"games digested {got}, analysed {done}, due for analysis {got - done >= STEP}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

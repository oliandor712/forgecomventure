#!/usr/bin/env python3
"""Tag-set hashes for a card's blind view (the record a reader sees: typing, tags, groups, links).

  shape_hash(card)  numbers -> N, names -> NAME, group ids renamed in card order: equal for cards a reader would word the same way
  exact_hash(card)  shape plus the ordered numbers: equal only for true duplicates
  line_hash(tags)   one group's tag string (pattern() key): the unit for 'read only open lines'

  python3 tag_hash.py stats [--runs g11a,g11b ...]   collisions inside the given runs and against all earlier runs in ~/tagcheck_runs (reads in/ batches only, never keys)
"""
import argparse, collections as C, glob, hashlib, json, os, re, sys

RUNS = os.path.expanduser(os.environ.get("TAGCHECK_DIR") or "~/tagcheck_runs")


def _norm(tag):
    """one tag -> (shape string, numbers); named:/token names become NAME"""
    fam, _, val = tag.partition(":")
    if fam in ("named", "card_name", "token_name"): return fam + ":NAME", []
    nums = re.findall(r"\d+", val)
    return fam + (":" + re.sub(r"\d+", "N", val) if val else ""), nums


def _group(tagstr):
    parts = [_norm(t) for t in tagstr.split()]
    return " ".join(sorted(p[0] for p in parts)), [n for p in sorted(parts) for n in p[1]]


def canon(card):
    """(canonical shape string, number list) of one blind card record"""
    ren, nums, lines = {}, [], []
    for g, ts in card["groups"].items():
        top = g.split(".")[0]
        ren.setdefault(top, "c%d" % (len(ren) + 1))
        s, n = _group(ts); nums += n
        lines.append("%s%s=%s" % (ren[top], g[len(top):], s))
    links = sorted(re.sub(r"\bc\d+", lambda m: ren.get(m.group(0), m.group(0)), re.sub(r"\d+", "N", l)) for l in card.get("links", []))
    flat = sorted(_norm(t)[0] for t in card.get("tags", []))
    return "T:%s|F:%s|G:%s|L:%s" % (",".join(sorted(card.get("typing", []))), ",".join(flat), ";".join(lines), ";".join(links)), nums


def _h(s): return hashlib.sha1(s.encode()).hexdigest()[:12]
def shape_hash(card): return _h(canon(card)[0])
def exact_hash(card): s, n = canon(card); return _h(s + "#" + ",".join(n))
def line_hash(tagstr): return _h(_group(tagstr)[0])


def run_cards(run):
    for f in sorted(glob.glob(os.path.join(RUNS, run, "in", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        for c in (d.get("cards", []) if isinstance(d, dict) else d):
            if isinstance(c, dict) and "groups" in c: yield c      # older layouts without groups are skipped


def seen_lines(exclude_round=""):
    """line hashes of every ability line in every run's input batches, except runs of the given round (name minus its a/b/c letter): lines a reader has been given"""
    out = set()
    for p in glob.glob(os.path.join(RUNS, "*", "in")):
        r = os.path.basename(os.path.dirname(p))
        if exclude_round and re.match(r"^%s[a-z]?$" % re.escape(exclude_round), r): continue
        for c in run_cards(r): out.update(line_hash(t) for t in c["groups"].values())
    return out


def stats(runs):
    allruns = sorted(os.path.basename(p) for p in glob.glob(os.path.join(RUNS, "*")) if os.path.isdir(os.path.join(p, "in")))
    old = [r for r in allruns if r not in runs]
    seen_s, seen_e, seen_l = set(), set(), set()
    for r in old:
        for c in run_cards(r):
            seen_s.add(shape_hash(c)); seen_e.add(exact_hash(c)); seen_l.update(line_hash(t) for t in c["groups"].values())
    uniq = {}
    for r in runs:
        for c in run_cards(r): uniq[(r.rstrip("abc"), c["id"], exact_hash(c))] = c      # a round's a/b/c share cards: count each once
    cards = list(uniq.values()); n = len(cards)
    ss = C.Counter(shape_hash(c) for c in cards); ee = C.Counter(exact_hash(c) for c in cards)
    print("earlier runs: %d, distinct shapes %d, exact %d, lines %d" % (len(old), len(seen_s), len(seen_e), len(seen_l)))
    print("new cards %d: distinct shapes %d, distinct exact %d" % (n, len(ss), len(ee)))
    print("  shape seen in earlier runs: %d (%.0f%%); exact seen: %d (%.0f%%)" % (sum(shape_hash(c) in seen_s for c in cards), 100.0 * sum(shape_hash(c) in seen_s for c in cards) / n, sum(exact_hash(c) in seen_e for c in cards), 100.0 * sum(exact_hash(c) in seen_e for c in cards) / n))
    print("  repeats inside the new cards: shape %d, exact %d" % (n - len(ss), n - len(ee)))
    lines = [line_hash(t) for c in cards for t in c["groups"].values()]
    print("  ability lines %d, already seen %d (%.0f%%)" % (len(lines), sum(l in seen_l for l in lines), 100.0 * sum(l in seen_l for l in lines) / max(len(lines), 1)))
    full = sum(all(line_hash(t) in seen_l for t in c["groups"].values()) for c in cards)
    print("  cards whose every line was seen before: %d (%.0f%%)" % (full, 100.0 * full / n))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("stats"); s.add_argument("--runs", default="")
    a = ap.parse_args()
    runs = [r for r in a.runs.split(",") if r] or sorted(os.path.basename(p) for p in glob.glob(os.path.join(RUNS, "g[12][0-9]?")) if int(re.match(r"g(\d+)", os.path.basename(p)).group(1)) >= 11)
    stats(runs)

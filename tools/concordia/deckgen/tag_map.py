"""Old-to-new tag map (ACTION_PLAN_TAG_DECK.md, step 1). The deck tools still read ability_tags names; the tagger record keeps most of them and replaces the rest.
Generated from the record, never hand-written: for every card in the decks, each ability_tags name is looked up in tag_run.record. Per old name:
  kept      the name is in the record
  replaced  the name was dropped and a structured tag says it (kw:<name>, remove:*, ...): the replacement tags are listed with counts
  dropped   removed on purpose by a tag_run rule (land or self sacrifice is not an outlet, evasion is not a restriction); no replacement
  UNEXPLAINED  dropped with no replacement and no known rule: a silent drop, the check fails
Usage: python3 tag_map.py [--out tags/TAG_MAP.toon]   (exit 1 when any silent drop is found)
Library: load() reads the map; to_new(old_tags) returns the record names for a set of old names."""
import sys, os, re, glob, collections, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tag_run as T, ability_tags as AT, tag_verify as TV
from common import card_files
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "forge-gui", "res", "adventure", "Concordia", "decks"))
OUT = os.path.join(HERE, "tags", "TAG_MAP.toon")
SKIP = ("has:", "needs:", "hint:")


def deck_names():
    names = collections.Counter()
    for f in glob.glob(os.path.join(ROOT, "*", "*.dck")): names.update(T.deck_cards(f))
    return names


def explain(old, new):
    """(kind, replacement tags) for one old name missing from one card's record"""
    o = old.lower()
    if "kw:" + o in new: return "replaced", ["kw:" + o]
    if o in TV.BARE_KEYWORDS: return "replaced", [x for x in sorted(new) if x.startswith(("grant_kw:", "kw:"))][:3] or ["grant_kw:*"]
    if o == "removal":
        r = [x for x in sorted(new) if x.startswith("remove:") or x == "damage"]
        if r: return "replaced", r
    if o == "sacrifice_outlet" and any(x.startswith(("cost_sacrifice_target:", "sacrifice_type:")) for x in new): return "dropped", []
    if o == "restrict" and any(x.startswith("cant_be_blocked") for x in new): return "dropped", []
    rep = [x for x in sorted(new) if x.split(":")[0] == o or x.startswith(o + ":") or x.startswith("kw:" + o)]
    if rep: return "replaced", rep
    return "unexplained", []


def build():
    stat = collections.defaultdict(lambda: collections.Counter())
    rep = collections.defaultdict(collections.Counter)
    bad = collections.defaultdict(list)
    n = 0
    for name in deck_names():
        t = T.find_text(name)
        if not t: continue
        n += 1
        old = {x for x in AT.tags_of(t) if not x.startswith(SKIP)}
        new = set(T.record(name, t)["tags"])
        for o in old:
            if o.lower() in new: stat[o]["kept"] += 1; continue
            k, r = explain(o, new)
            stat[o][k] += 1
            for x in r: rep[o][x] += 1
            if k == "unexplained": bad[o].append(name)
    return n, stat, rep, bad


def write(path, n, stat, rep, bad):
    rows = []
    for o in sorted(stat):
        s = stat[o]
        kind = "UNEXPLAINED" if s["unexplained"] else "replaced" if s["replaced"] and not s["kept"] else "mixed" if s["replaced"] or s["dropped"] else "kept"
        r = " ".join("%s(%d)" % (x, c) for x, c in rep[o].most_common(6))
        rows.append("%s,%s,%d,%d,%d,%d,%s" % (o, kind, s["kept"], s["replaced"], s["dropped"], s["unexplained"], r))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# tag_map.py (generated). %d deck cards. old name -> record. Regenerate, never hand-edit.\n" % n)
        f.write("map[%d]{old,status,kept,replaced,dropped_on_purpose,unexplained,replacement}:\n" % len(rows))
        for r in rows: f.write("  " + r + "\n")


def load(path=OUT):
    """old name -> (status, [replacement tags])"""
    m = {}
    for l in open(path, encoding="utf-8"):
        if not l.startswith("  "): continue
        p = l.strip().split(",", 6)
        m[p[0]] = (p[1], [re.sub(r"\(\d+\)$", "", x) for x in (p[6].split() if len(p) > 6 else [])])
    return m


def to_new(old_tags, m=None):
    m = m or load(); out = set()
    for o in old_tags:
        st, rep = m.get(o, ("kept", []))
        out.add(o.lower())
        out.update(rep)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=OUT); a = ap.parse_args()
    n, stat, rep, bad = build(); write(a.out, n, stat, rep, bad)
    miss = {o: c for o, c in bad.items()}
    print("tag_map: %d cards, %d old names, %d with silent drops -> %s" % (n, len(stat), len(miss), a.out))
    for o, c in sorted(miss.items()): print("  UNEXPLAINED %s on %d cards, e.g. %s" % (o, len(c), c[:3]))
    sys.exit(1 if miss else 0)


if __name__ == "__main__":
    main()

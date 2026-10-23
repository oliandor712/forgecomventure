#!/usr/bin/env python3
"""tag_twins: find already-tagged ability lines that match an untagged line (proposal 1, 2026-10-23).

Index: every non-keyword Oracle line of every card in tags/STARTER_TAGS.toon, paired with its tag group (c1 plus c1.2, c1.3 ...).
Lookup: for a card or a text, the closest indexed lines with a % similarity and their tags. A twin is a starting point for the
tagger, never copied silently: check the differences, and `human_logic.toon` still beats a twin.

  python3 tag_twins.py build                 write tags/ABILITY_TWINS.json (generated, never hand-edited)
  python3 tag_twins.py card "Card Name" ...  twins for each non-keyword line of a card (the card's own record is skipped)
  python3 tag_twins.py text "Oracle line"    twins for a free text line
  python3 tag_twins.py stats                 share of indexed lines that have an exact / near twin on another card

Weight: each indexed line carries the reader accuracy of its card (mean `sim` over every blind-reader result of runs r12 on in
~/tagcheck_runs, `reads` = number of readings; none = no reading yet). Twins are ranked by similarity x accuracy, so a twin the reader
reproduced well comes before an equally similar one it got wrong; a low accuracy marks a twin whose tags may be incomplete. Both numbers are shown.

Similarity: both lines are normalised (card name -> ~, numbers -> N, mana symbols -> {c}, reminder text dropped); 100% = identical
after that, otherwise difflib ratio on the normalised words. Keyword-only lines are excluded. "A-" (Alchemy rebalance) cards are skipped.
"""
import collections, difflib, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TOON = os.path.join(HERE, "tags", "STARTER_TAGS.toon")
OUT = os.path.join(HERE, "tags", "ABILITY_TWINS.json")


def oracle_of_all():
    """name -> Oracle text from the Forge scripts; every face (ALTERNATE section) is its own card, A- cards dropped"""
    out = {}
    for f in glob.glob(os.path.join(ROOT, "forge-gui/res/cardsfolder/*/*.txt")):
        txt = open(f, encoding="utf-8", errors="replace").read()
        for part in re.split(r"^ALTERNATE\s*$", txt, flags=re.M):
            t = part.splitlines()
            name = next((l[5:].strip() for l in t if l.startswith("Name:")), None)
            o = next((l[7:] for l in t if l.startswith("Oracle:")), None)
            if name and o and not name.startswith("A-"):
                out[name] = o
    return out


def ability_lines(name, oracle):
    """non-keyword Oracle lines, reminder text dropped, own name -> ~"""
    out = []
    for l in re.split(r"\\n|\n", oracle):
        l = re.sub(r"\(.*?\)", "", l).strip()
        if not l:
            continue
        l = l.replace(name, "~")
        short = name.split(",")[0]
        if short:
            l = l.replace(short, "~")
        if len(l.split()) <= 3 and not re.search(r"[:.]", l.rstrip(".")):
            continue  # keyword line
        out.append(l)
    return out


def norm(l):
    l = l.lower()
    l = re.sub(r"\d+", "N", l)
    l = re.sub(r"\{[^}]*\}", "{c}", l)
    return re.sub(r"\s+", " ", l).strip()


def parse_toon():
    """card -> {'tags': [...], 'groups': [(id, source, tags)]}"""
    cards, cur, ing = {}, None, False
    for ln in open(TOON, encoding="utf-8"):
        ln = ln.rstrip("\n")
        m = re.match(r"^card: (.+)$", ln)
        if m:
            cur = cards.setdefault(m.group(1).strip().strip('"'), {"tags": [], "groups": []})
            ing = False
            continue
        if cur is None:
            continue
        if ln.startswith("tags: "):
            cur["tags"] = ln[6:].split()
        elif ln.startswith("groups["):
            ing = True
        elif ing and ln.startswith("  "):
            gid, src, tags = (ln.strip().split(",", 2) + ["", ""])[:3]
            cur["groups"].append((gid, src, tags.split()))
        else:
            ing = False
    return cards


def accuracy():
    """card name -> (mean reader sim, readings) from ~/tagcheck_runs/r12*..r15*/results.json (vanilla and text-less cards skipped)"""
    base = os.environ.get("TAGCHECK_DIR") or os.path.expanduser("~/tagcheck_runs")
    acc = collections.defaultdict(list)
    for f in glob.glob(os.path.join(base, "r*", "results.json")):
        m = re.match(r"r(\d+)", os.path.basename(os.path.dirname(f)))
        if not m or int(m.group(1)) < 12:
            continue
        for r in json.load(open(f, encoding="utf-8")).values():
            if r.get("has_text") and not r.get("vanilla") and not r.get("empty_reco") and r.get("name"):
                acc[r["name"]].append(r["sim"])
    return {n: (round(sum(v) / len(v), 3), len(v)) for n, v in acc.items()}


def build():
    oracle = oracle_of_all()
    accs = accuracy()
    cards = parse_toon()
    rows, aligned, unaligned, missing = [], 0, 0, []
    for name, c in cards.items():
        if name not in oracle:
            missing.append(name)
            continue
        lines = ability_lines(name, oracle[name])
        tops = [g for g in c["groups"] if re.match(r"^[cs]\d+$", g[0])]
        ok = len(lines) == len(tops)
        for i, l in enumerate(lines):
            if ok:
                gid = tops[i][0]
                tags = [t for g in c["groups"] if g[0] == gid or g[0].startswith(gid + ".") for t in g[2]]
            else:
                gid, tags = None, [t for g in c["groups"] if re.match(r"^[cs]\d", g[0]) for t in g[2]]
            rows.append({"card": name, "line": i + 1, "text": l, "norm": norm(l), "group": gid, "aligned": ok, "tags": tags,
                         "acc": accs.get(name, (None, 0))[0], "reads": accs.get(name, (None, 0))[1]})
        aligned += len(lines) if ok else 0
        unaligned += 0 if ok else len(lines)
    json.dump(rows, open(OUT, "w", encoding="utf-8"), indent=0)
    print("reader accuracy known for %d of %d cards" % (sum(1 for n in cards if n in accs), len(cards)))
    print("indexed %d lines from %d cards (%d lines aligned to a group, %d unaligned = whole-card tags); %d cards without Oracle: %s"
          % (len(rows), len(cards) - len(missing), aligned, unaligned, len(missing), ", ".join(missing[:8])))


def load():
    if not os.path.exists(OUT):
        build()
    return json.load(open(OUT, encoding="utf-8"))


def shingles(k):
    w = k.split()
    return {" ".join(w[i:i + 3]) for i in range(max(1, len(w) - 2))}


def twins(rows, text, skip_card=None, top=3, floor=0.5):
    """[(pct, row)] best first by pct x reader accuracy (unknown accuracy counts as the mean of the known ones); exact normalised match = 100"""
    k = norm(text)
    res = []
    sk = shingles(k)
    for r in rows:
        if r["card"] == skip_card:
            continue
        if r["norm"] == k:
            res.append((100, r))
            continue
        if not sk & shingles(r["norm"]):
            continue
        s = difflib.SequenceMatcher(None, k.split(), r["norm"].split()).ratio()
        if s >= floor:
            res.append((int(s * 100), r))
    known = [r["acc"] for r in rows if r.get("acc") is not None]
    mean = sum(known) / len(known) if known else 1.0
    res.sort(key=lambda x: -x[0] * (x[1]["acc"] if x[1].get("acc") is not None else mean))
    return res[:top]


def show(rows, text, skip_card=None):
    print("  line: " + text)
    t = twins(rows, text, skip_card)
    if not t:
        print("    no twin >= 50%")
    for pct, r in t:
        a = "reader acc %.2f x%d" % (r["acc"], r["reads"]) if r.get("acc") is not None else "reader acc n/a"
        print("    %3d%%  %s (line %d, group %s%s, %s): %s" % (pct, r["card"], r["line"], r["group"] or "?", "" if r["aligned"] else ", unaligned: whole-card tags", a, r["text"][:90]))
        print("          tags: " + " ".join(r["tags"]))


def stats(rows):
    byn = collections.defaultdict(set)
    for r in rows:
        byn[r["norm"]].add(r["card"])
    ex = sum(1 for r in rows if byn[r["norm"]] - {r["card"]})
    print("lines %d, with an exact twin on another card: %d (%.0f%%)" % (len(rows), ex, 100 * ex / len(rows)))
    rest = [r for r in rows if not (byn[r["norm"]] - {r["card"]})]
    best = [(twins(rows, r["text"], r["card"], 1) or [(0, None)])[0][0] for r in rest]
    for th in (90, 80, 70, 60, 50):
        print("  no exact twin, closest >= %d%%: %.0f%%" % (th, 100 * sum(1 for b in best if b >= th) / max(1, len(best))))
    print("aligned to a tag group: %d of %d lines (%.0f%%)" % (sum(1 for r in rows if r["aligned"]), len(rows), 100 * sum(1 for r in rows if r["aligned"]) / len(rows)))


def main(a):
    if not a:
        print(__doc__)
        return
    if a[0] == "build":
        build()
    elif a[0] == "stats":
        stats(load())
    elif a[0] == "text":
        show(load(), " ".join(a[1:]))
    elif a[0] == "card":
        rows, oracle = load(), oracle_of_all()
        for n in a[1:]:
            print(n)
            if n not in oracle:
                print("  no Oracle text found")
                continue
            for l in ability_lines(n, oracle[n]):
                show(rows, l, skip_card=n)
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])

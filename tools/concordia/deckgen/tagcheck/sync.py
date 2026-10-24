"""Two-way link between the tagger (tag_run.py, tag_extra.py ...) and the tag check (mtg2llm.py, rule tables). Run automatically after `tag_run.py starter` and after `mtg2llm.py mine`;
`python3 sync.py` runs it by hand. It renders every tagged starter unit and writes tags/TAG_GAPS.toon, one row per unit the renderer cannot write:
  open_slot  a rule exists but the tags leave a slot open (no number, no filter): a TAG gap, the tagger should emit the missing tag
  no_rule    no exact or composed rule fits these tags: a RULE gap, a reader run / hand table (HAND_*) should cover this pattern
and a coverage line. tag_run.py reads the previous file at the start of its next run and prints the gap counts, so each side shows what the other side lacks.
Rows are regenerated each time, never hand-merged."""
import os, sys, re, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import mtg2llm as M

OUT = os.path.join(os.path.dirname(HERE), "tags", "TAG_GAPS.toon")


def gaps():
    """(rows, units, rendered) over every tagged starter; row = (card, group, tags, reason)"""
    rows, n, ok = [], 0, 0
    for r, b, _x, _y in M.tag_cards():
        for g, ts in M.units(b["groups"]).items():
            n += 1
            text, st = M.render({g: " ".join(ts)}, b["typing"])
            if not st["missing"]: ok += 1; continue
            v, approx = M.lookup(M.pattern([" ".join(ts)]))
            slot = v is not None and not approx and M.unresolved(M.fill(v["canon"], M.nums(ts)))
            rows.append((r["name"], g, " ".join(ts), "open_slot" if slot else "no_rule"))
    return rows, n, ok


def write():
    rows, n, ok = gaps(); c = collections.Counter(x[3] for x in rows)
    lines = ["# Claude-only file in TOON. Written by tagcheck/sync.py; regenerated, never hand-merged. open_slot = tag gap (tagger), no_rule = rule gap (mtg2llm mine / HAND tables).",
             "# starters: %d units, %d rendered, %d open_slot, %d no_rule" % (n, ok, c["open_slot"], c["no_rule"]),
             "gaps[%d|]{card|group|tags|reason}:" % len(rows)]
    lines += ["%s|%s|%s|%s" % (a, g, t.replace("|", "/"), r) for a, g, t, r in sorted(rows, key=lambda x: (x[3], x[0], x[1]))]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")
    return n, ok, c


def previous():
    """summary line of the last gap file, for the tagger to print before it runs"""
    if not os.path.exists(OUT): return ""
    for l in open(OUT, encoding="utf-8"):
        if l.startswith("# starters:"): return l[2:].strip()
    return ""


if __name__ == "__main__":
    n, ok, c = write()
    print("sync: %d units, %d rendered, %d open_slot (tag gaps), %d no_rule (rule gaps) -> %s" % (n, ok, c["open_slot"], c["no_rule"], OUT))

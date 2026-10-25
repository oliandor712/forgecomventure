#!/usr/bin/env python3
"""reader_metric: what a reader run bought (ACTION_PLAN_TAG_DECK.md, step 10).

Per run it records one row in tags/READER_METRIC.toon:
  run, date, rules (render + compose table entries), rules_new (entries not in the previous row's snapshot), gaps_open (open_slot rows of TAG_GAPS.toon),
  gaps_closed (open_slot rows the previous row had and this one lacks), no_rule, rendered_pct (starter units rendered by rules, no reader), pending (rules seen in one run only).
Second-batch rule: a mined render/compose rule is 'pending' until a second, different run lists it too (tags/RULE_BATCHES.json: rule -> runs that mined it).
This reports pending rules; it does not remove them from render_rules.json (that would change rendering; the user decides).

  python3 reader_metric.py update RUN     add or replace the run's row, refresh RULE_BATCHES.json, print the row
  python3 reader_metric.py show           the table
  python3 reader_metric.py pending        rules still waiting for a second batch
Called by reverse_check.py compare after the post-run mining."""
import datetime, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TAGS = os.path.join(HERE, "..", "tags")
METRIC = os.path.join(TAGS, "READER_METRIC.toon")
BATCHES = os.path.join(TAGS, "RULE_BATCHES.json")
HEAD = "rows[%d|]{run|date|rules|rules_new|gaps_open|gaps_closed|no_rule|rendered_pct|pending}:"


def rule_keys():
    """Every render rule pattern and compose entry, as 'render:<pattern>' / 'compose:<table>:<key>'."""
    out = set()
    r = json.load(open(os.path.join(HERE, "render_rules.json"), encoding="utf-8"))
    out |= {"render:" + k for k in r}
    c = json.load(open(os.path.join(HERE, "compose_rules.json"), encoding="utf-8"))
    for tbl, d in c.items():
        out |= {"compose:%s:%s" % (tbl, k) for k in d}
    return out


def gap_state():
    """(open_slot cards set, no_rule count, rendered pct) from TAG_GAPS.toon."""
    txt = open(os.path.join(TAGS, "TAG_GAPS.toon"), encoding="utf-8").read().splitlines()
    m = re.search(r"(\d+) units, (\d+) rendered, (\d+) open_slot, (\d+) no_rule", txt[1] if len(txt) > 1 else "")
    units, rendered = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    open_slot, no_rule = set(), 0
    for l in txt:
        p = l.split("|")
        if len(p) == 4 and p[3] == "open_slot": open_slot.add(p[0] + "|" + p[1])
        elif len(p) == 4 and p[3] == "no_rule": no_rule += 1
    return open_slot, no_rule, (100.0 * rendered / units if units else 0.0)


def load_rows():
    rows = []
    if os.path.exists(METRIC):
        for l in open(METRIC, encoding="utf-8").read().splitlines():
            if l.startswith("  "): rows.append(l.strip().split("|"))
    return rows


def load_batches():
    return json.load(open(BATCHES, encoding="utf-8")) if os.path.exists(BATCHES) else {}


def update(run):
    keys = rule_keys()
    b = load_batches()
    for k in keys: b.setdefault(k, [])
    for k in keys:
        if run not in b[k]: b[k].append(run)
    for k in [k for k in b if k not in keys]: del b[k]   # rules the table dropped
    json.dump(b, open(BATCHES, "w", encoding="utf-8", newline="\n"), indent=0, sort_keys=True)
    open_slot, no_rule, pct = gap_state()
    rows = [r for r in load_rows() if r[0] != run]
    snap = os.path.join(TAGS, "READER_METRIC.snap.json")
    prev = json.load(open(snap, encoding="utf-8")) if os.path.exists(snap) else {"rules": [], "open": []}
    prev_open = set(prev["open"])
    new_rules = len(keys - set(prev["rules"])) if prev["rules"] else 0
    closed = len(prev_open - open_slot) if prev["open"] else 0
    pending = sum(1 for k in keys if len(b[k]) < 2)
    rows.append([run, datetime.date.today().isoformat(), str(len(keys)), str(new_rules), str(len(open_slot)), str(closed), str(no_rule), "%.1f" % pct, str(pending)])
    json.dump({"rules": sorted(keys), "open": sorted(open_slot)}, open(snap, "w", encoding="utf-8", newline="\n"))
    write(rows)
    return rows[-1]


def write(rows):
    L = ["# Claude-only file in TOON. Written by tagcheck/reader_metric.py; one row per reader run, rows replaced by run name.",
         "# rules_new / gaps_closed are against the previous update (blank history counts 0). pending = rules mined by one run only (second-batch rule).", HEAD % len(rows)]
    L += ["  " + "|".join(r) for r in rows]
    open(METRIC, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "update": print("|".join(update(sys.argv[2])))
    elif cmd == "show": print(open(METRIC, encoding="utf-8").read() if os.path.exists(METRIC) else "no rows yet")
    elif cmd == "pending":
        b = load_batches(); p = sorted(k for k, v in b.items() if len(v) < 2)
        print("%d of %d rules wait for a second batch" % (len(p), len(b)))
        for k in p[:40]: print("  ", k[:120], b[k])
    else: raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

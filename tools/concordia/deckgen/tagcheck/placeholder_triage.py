#!/usr/bin/env python3
"""Placeholder triage (plan: TAG_RUN_AUDIT_AND_PLAN.md, P4b). Reads reader outputs of finished runs and lists every unfilled placeholder
({cost}, {effect}, {filter}, {trigger} ...) with the group's tags and the real Oracle text, grouped by placeholder and by class.

  python3 placeholder_triage.py --runs r13c2a r13c2b r13c2c [--out file.md]

Class is a heuristic from the group's tags, not a verdict:
  cost_amount   placeholder {cost} and an Oracle line with a cost shape (contains ":" or starts with a cost keyword) shows a mana amount (mana amounts are not tags: known structural gap; line match is a heuristic)
  no_tags       the group has no tag besides trigger/cost/scope words (the tags carry nothing for the placeholder)
  has_tags      the group has effect or filter tags and a reader still wrote a placeholder (grammar or reader issue)
Needs results.json in each run dir (written by reverse_check.py compare)."""
import os, re, sys, json, glob, argparse, collections

RUNS = os.environ.get("TAGCHECK_DIR") or os.path.expanduser("~/tagcheck_runs")
PH = re.compile(r"\{([a-z_]+)\}")
SCAFFOLD = ("trigger", "trigger_scope", "cost", "optional", "duration", "condition", "controller", "typing")
MANA = re.compile(r"\{[0-9XWUBRGC/]+\}")


COSTKW = re.compile(r"^(equip|kicker|multikicker|cycling|flashback|ward|suspend|morph|unearth|echo|buyback|level up|bestow|evoke|madness|prowl|overload)", re.I)


def has_cost_amount(orig):
    """True if some Oracle line of the card has a mana amount in a cost position, not just anywhere on the card."""
    return any(MANA.search(seg) and (":" in seg or COSTKW.match(seg.strip()))
               for seg in re.split(r"\n| / ", orig))


def scan(run):
    base = os.path.join(RUNS, run)
    rj = os.path.join(base, "results.json")
    if not os.path.exists(rj):
        print("skip %s: no results.json (run reverse_check.py compare first)" % run, file=sys.stderr)
        return []
    res = json.load(open(rj))
    groups, recs = {}, {}
    for f in sorted(glob.glob(os.path.join(base, "in", "batch_*.json"))):
        for c in json.load(open(f))["cards"]:
            groups[c["id"]] = c.get("groups", {})
    for f in sorted(glob.glob(os.path.join(base, "out", "batch_*.json"))):
        for c in json.load(open(f))["cards"]:
            recs[c["id"]] = c
    rows = []
    for cid, c in recs.items():
        r = res.get(cid, {})
        items = c.get("records") or [{"group": "", "kind": "", "text": c.get("text", "")}]
        for it in items:
            for ph in set(PH.findall(it.get("text", ""))):
                if ph in ("T", "Q"):
                    continue
                gt = groups.get(cid, {}).get(it.get("group"), "")
                words = [w for w in gt.split() if w.split(":")[0] not in SCAFFOLD]
                if ph == "cost" and has_cost_amount(r.get("orig", "")):
                    cls = "cost_amount"
                elif not words:
                    cls = "no_tags"
                else:
                    cls = "has_tags"
                rows.append(dict(run=run, id=cid, name=r.get("name", cid), ph=ph, kind=it.get("kind", ""), group=it.get("group", ""),
                                 gtags=gt, text=it.get("text", ""), orig=r.get("orig", ""), cls=cls))
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--runs", nargs="+", required=True); ap.add_argument("--out", default="")
    a = ap.parse_args()
    rows = [r for run in a.runs for r in scan(run)]
    cards = {r["name"] for r in rows}
    L = ["# Placeholder triage", "", "Runs: %s. Occurrences: %d on %d cards. Class is a heuristic (see script docstring)." % (", ".join(a.runs), len(rows), len(cards)), ""]
    t = collections.Counter((r["ph"], r["cls"]) for r in rows)
    L += ["| Placeholder | cost_amount | no_tags | has_tags | total |", "|---|---|---|---|---|"]
    for ph in sorted({k[0] for k in t}, key=lambda p: -sum(v for k, v in t.items() if k[0] == p)):
        L.append("| `{%s}` | %d | %d | %d | %d |" % (ph, t[(ph, "cost_amount")], t[(ph, "no_tags")], t[(ph, "has_tags")], sum(v for k, v in t.items() if k[0] == ph)))
    L += ["", "## Per placeholder and tag pattern (distinct cards, most frequent first)", ""]
    pat = collections.defaultdict(set)
    for r in rows:
        fam = tuple(sorted({w.split(":")[0] for w in r["gtags"].split() if w.split(":")[0] not in SCAFFOLD})) or ("(none)",)
        pat[(r["ph"], r["cls"], fam)].add(r["name"])
    for (ph, cls, fam), names in sorted(pat.items(), key=lambda kv: -len(kv[1]))[:60]:
        L.append("- `{%s}` %s, tag families `%s`: %d cards (%s)" % (ph, cls, " ".join(fam), len(names), ", ".join(sorted(names)[:4])))
    L += ["", "## Occurrences", "", "| Card | Run | Placeholder | Class | Group tags | Reader text | Oracle |", "|---|---|---|---|---|---|---|"]
    esc = lambda s: s.replace("|", "/")[:160]
    for r in sorted(rows, key=lambda r: (r["ph"], r["cls"], r["name"], r["run"])):
        L.append("| %s | %s | `{%s}` | %s | %s | %s | %s |" % (r["name"], r["run"], r["ph"], r["cls"], esc(r["gtags"]), esc(r["text"]), esc(r["orig"])))
    out = "\n".join(L) + "\n"
    if a.out:
        if os.path.exists(a.out) and not open(a.out, encoding="utf-8").readline().startswith("# Placeholder triage") or os.path.basename(a.out) == "PLACEHOLDER_TRIAGE.md":
            sys.exit("refusing to overwrite %s: it holds hand-written findings; write generated data to another file (e.g. PLACEHOLDER_TRIAGE_DATA.md)" % a.out)
        open(a.out, "w", encoding="utf-8").write(out)
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()

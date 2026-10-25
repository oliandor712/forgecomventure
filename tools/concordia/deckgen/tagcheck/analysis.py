"""One-off analyses over reader output and the card pool (SCRIPT_MERGE_ANALYSIS.md, step 6; was placeholder_triage.py and oracle_style_stats.py).
  python3 analysis.py placeholders --runs r13c2a r13c2b [--out file.md]
  python3 analysis.py style [--holdout N]

placeholders: Placeholder triage (plan: TAG_RUN_AUDIT_AND_PLAN.md, P4b). Reads reader outputs of finished runs and lists every unfilled placeholder
({cost}, {effect}, {filter}, {trigger} ...) with the group's tags and the real Oracle text, grouped by placeholder and by class.

  python3 placeholder_triage.py --runs r13c2a r13c2b r13c2c [--out file.md]

Class is a heuristic from the group's tags, not a verdict:
  cost_amount   placeholder {cost} and an Oracle line with a cost shape (contains ":" or starts with a cost keyword) shows a mana amount (mana amounts are not tags: known structural gap; line match is a heuristic)
  no_tags       the group has no tag besides trigger/cost/scope words (the tags carry nothing for the placeholder)
  has_tags      the group has effect or filter tags and a reader still wrote a placeholder (grammar or reader issue)
Needs results.json in each run dir (written by reverse_check.py compare).

style: Phase 0 of the grammar plan: count how Oracle text is really written over the card pool (forge-gui/res/cardsfolder), so the grammar copies the printed style
instead of anyone's memory. Also draws the random hold-out sample (non-starter cards with ability text), seed 20261022. Usage: python3 oracle_style_stats.py [--holdout N]"""
import os, re, sys, json, glob, argparse, collections, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tag_run as T
from common import card_files


# ---- placeholders ----
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


def placeholders_main():
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


# ---- style ----
ROOT = T.ROOT


def pool():
    out = {}
    for p in card_files(ROOT):
        x = open(p, errors="replace").read()
        m = re.search(r"^Name:(.*)$", x, re.M); o = re.search(r"^Oracle:(.*)$", x, re.M); ty = re.search(r"^Types:(.*)$", x, re.M)
        if m and o and ty and "Token" not in ty.group(1).split() and "\nAlternateMode:" not in x and "ALTERNATE" not in x:
            out[m.group(1).strip()] = (o.group(1).replace("\\n", "\n").strip(), ty.group(1))
    return out


def stats(pl):
    c = collections.Counter(); n = len(pl)
    txt = [t for t, _ in pl.values()]
    allt = "\n".join(txt)
    def cnt(rx, flags=re.I | re.M): return len(re.findall(rx, allt, flags))
    for k, rx in [("When", r"^when\b"), ("Whenever", r"^whenever\b"), ("At the beginning of", r"^at the beginning of\b"),
                  ("draw a card", r"\bdraw a card\b"), ("draw N cards (digit)", r"\bdraw \d+ cards\b"), ("draw N cards (word)", r"\bdraw (two|three|four|five|six|seven) cards\b"),
                  ("deals N damage (digit)", r"\bdeals \d+ damage\b"), ("deals X damage", r"\bdeals x damage\b"),
                  ("+N/+N counter (digit)", r"\+\d+/\+\d+ counter"), ("put a +1/+1 counter", r"\bput a \+1/\+1 counter\b"), ("put N counters (word)", r"\bput (two|three|four) \+1/\+1 counters\b"),
                  ("create a N/N token", r"\bcreate an? \d+/\d+\b"), ("create N tokens (word)", r"\bcreate (two|three|four|five) \d+/\d+\b"),
                  ("you may", r"\byou may\b"), ("instead", r"\binstead\b"), ("up to N target", r"\bup to (one|two|three|\d+) target\b"),
                  ("until end of turn", r"\buntil end of turn\b"), ("target creature an opponent controls", r"target creature an opponent controls"), ("target creature you don't control", r"target creature you don't control"),
                  ("each opponent", r"\beach opponent\b"), ("you control", r"\byou control\b"), ("sacrifice a creature", r"\bsacrifice an? [a-z]+\b"),
                  ("put onto the battlefield", r"\bonto the battlefield\b"), ("return to the battlefield", r"\breturn[^.]*to the battlefield\b"),
                  ("enters (new wording)", r"\benters\b"), ("enters the battlefield (old wording)", r"\benters the battlefield\b"),
                  ("self name or ~", r"~"), ("this creature", r"\bthis creature\b"), ("reminder text in parentheses", r"\([^)]*\)")]:
        c[k] = cnt(rx)
    firsts = collections.Counter()
    for t in txt:
        for line in t.split("\n"):
            w = line.split(" ")[0].lower().rstrip(",:.") if line else ""
            if w: firsts[w] += 1
    kinds = collections.Counter()
    for t in txt:
        for line in t.split("\n"):
            l = line.strip()
            if not l: continue
            kinds["triggered" if re.match(r"^(when|whenever|at the beginning of)\b", l, re.I) else "activated" if re.match(r"^(\{|[A-Z][a-z]+( [a-z]+)?[^:.]*):", l) and ":" in l and l.index(":") < 60 else "other"] += 1
    lines_per_card = collections.Counter(len([x for x in t.split("\n") if x.strip()]) for t in txt)
    return n, c, firsts.most_common(25), kinds, lines_per_card


def holdout(pl, n, seed=20261022):
    starter = set()
    for d in glob.glob(os.path.join(ROOT, "forge-gui/res/adventure/Concordia/decks/starter/*.dck")):
        starter |= set(T.deck_cards(d))
    cand = sorted(k for k, (o, ty) in pl.items() if k not in starter and len(o) > 20 and "Land" not in ty.split() or (k not in starter and len(o) > 40))
    random.Random(seed).shuffle(cand)
    return cand[:n]


def trigger_and_move_stats(pl):
    """when vs whenever by trigger event, and return vs put for moves to the battlefield / to hand, by origin zone (evidence for SCORING_TOLERANCE.md)"""
    EV = [("enters", r"\benters\b"), ("dies", r"\bdies\b"), ("attacks", r"\battacks\b"), ("cast a spell", r"\byou cast\b|\bis cast\b|\bcast an?\b"), ("deals damage", r"\bdeals? (combat )?damage\b"),
          ("put into a graveyard", r"put into a graveyard"), ("becomes tapped/untapped", r"becomes (tapped|untapped)"), ("you gain life", r"you gain life"), ("you draw", r"you draw|draws? a card"), ("blocks / is blocked", r"\bblocks\b|becomes blocked|is blocked")]
    tw = {e: [0, 0] for e, _ in EV}; other = [0, 0]
    mv = collections.Counter()
    for o, _ in pl.values():
        for line in o.split("\n"):
            m = re.match(r"^(when|whenever)\b(.*?)(,|$)", line, re.I)
            if m:
                w = 0 if m.group(1).lower() == "when" else 1
                hit = False
                for e, rx in EV:
                    if re.search(rx, m.group(2), re.I): tw[e][w] += 1; hit = True; break
                if not hit: other[w] += 1
            for mm in re.finditer(r"\b(return|put)s?\b[^.]{0,80}?\b(from (?:your |a |an opponent's |target player's )?(graveyard|hand|library|exile)|from among)?[^.]{0,40}?\b(to|onto|into) (the battlefield|(?:its owner's|your|their) hand|(?:its owner's|your|their) library)", line, re.I):
                verb = mm.group(1).lower(); dest = "battlefield" if "battlefield" in mm.group(5).lower() else "hand" if "hand" in mm.group(5).lower() else "library"
                mv[(dest, verb, (mm.group(3) or "elsewhere").lower())] += 1
    return tw, other, mv


def style_main():
    n_h = int(sys.argv[sys.argv.index("--holdout") + 1]) if "--holdout" in sys.argv else 150
    pl = pool(); n, c, firsts, kinds, lpc = stats(pl)
    here = os.path.dirname(os.path.abspath(__file__))
    H = holdout(pl, n_h); TW = trigger_and_move_stats(pl)
    open(os.path.join(here, "holdout_cards.txt"), "w").write("\n".join(H) + "\n")
    L = ["# Oracle style statistics over the card pool (grammar plan, phase 0)", "",
         "Generated by `tagcheck/oracle_style_stats.py` from %d single-faced non-token cards in `forge-gui/res/cardsfolder` (Oracle: lines). Counts are matches in the whole pool, not cards." % n, "",
         "| Pattern | Matches |", "|---|---|"] + ["| %s | %d |" % kv for kv in c.most_common()] + ["",
         "## First words of ability lines (top 25)", "", ", ".join("%s %d" % kv for kv in firsts), "",
         "## Line kinds (rough)", "", ", ".join("%s %d" % kv for kv in kinds.most_common()), "",
         "## Lines per card", "", ", ".join("%d lines: %d cards" % kv for kv in sorted(lpc.items())[:10]), "",
         "## When vs whenever by trigger event (first clause of triggered lines)", "", "| Event | When | Whenever |", "|---|---|---|"] + ["| %s | %d | %d |" % (e, a_, b_) for e, (a_, b_) in TW[0].items()] + ["| other events | %d | %d |" % tuple(TW[1]), "",
         "## Return vs put, by destination and origin zone (matches in the pool)", "", "| Destination | Verb | Origin | Count |", "|---|---|---|---|"] + ["| %s | %s | %s | %d |" % (k[0], k[1], k[2], v) for k, v in sorted(TW[2].items(), key=lambda kv: (kv[0][0], -kv[1]))[:30]] + ["",
         "Hold-out sample: %d random non-starter cards with ability text (seed 20261022) in `tagcheck/holdout_cards.txt`; used only in phase 5, never to write the grammar." % len(H), "",
         "Unverified: the patterns are regexes (first version); `enters` vs `enters the battlefield` counts overlap."]
    open(os.path.join(here, "ORACLE_STYLE_STATS.md"), "w").write("\n".join(L) + "\n")
    print("pool", n, "holdout", len(H)); print(open(os.path.join(here, "ORACLE_STYLE_STATS.md")).read()[:2500])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "placeholders": sys.argv = sys.argv[1:]; placeholders_main()
    elif cmd == "style": sys.argv = sys.argv[1:]; style_main()
    else: print(__doc__)

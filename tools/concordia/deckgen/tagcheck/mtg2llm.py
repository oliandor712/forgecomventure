#!/usr/bin/env python3
"""MTG2LLM (tool): tags -> text -> score, no agents. Part 1: the grammar miner.

  python3 mtg2llm.py mine [--out render_rules.json]

Mines (tag group, reader line) pairs from the archived reader runs (~/tagcheck_runs/*/in + out). A card is used only when the reader wrote one
' / ' line for each ability unit of the card (groups k1, c1 ...; sub-groups c1.2 belong to c1). For each unit a pattern is built from its tags
(numbers and free values abstracted), and the reader lines are counted per pattern. The most frequent line is the canonical phrasing; the rest
are accepted variants. Writes render_rules.json: {pattern: {"n": units, "top": share, "canon": line, "variants": [[line, n], ...]}}.
Reads reader outputs only; never Oracle text.
"""
import argparse, collections as C, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reverse_check as RC

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.expanduser(os.environ.get("TAGCHECK_DIR") or "~/tagcheck_runs")


def units(groups):
    """ability units of a card: top group id -> its tag strings, in card order"""
    u = C.OrderedDict()
    for g, t in groups.items():
        if g.split(".")[0] != "c0": u.setdefault(g.split(".")[0], []).append(t)   # c0 = card-level labels, no ability line
    eq = [g for g, ts in u.items() if any(t.startswith("kw:equip") for t in " ".join(ts).split())]
    for g in eq: u.move_to_end(g)          # grammar G2: the Equip line is written last
    return u


def pattern(tagstrs):
    """a stable pattern key: tag family, value kept when it changes the wording, numbers abstracted"""
    out = []
    for t in " ".join(tagstrs).split():
        fam, _, val = t.partition(":")
        if fam == "scry_count": out.append("scry"); continue      # one tag now; runs mined before it existed wrote bare scry, and nums() still takes the count
        if not val: out.append(fam)
        else: out.append("%s:%s" % (fam, re.sub(r"\d+", "N", val)))
    return " ".join(sorted(set(out)))


NUMW = r"\b(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\b"


def templ(line):
    """the line with amounts abstracted, so 'draw two cards' and 'draw three cards' count as one phrasing"""
    line = re.sub(r"\{\d+\}", "{N}", line)
    line = re.sub(r"[+\-]\d+/[+\-]\d+", "+N/+N", line)
    line = re.sub(r"\b(?:a|an|one)(?= cards?\b)", "N", line, flags=re.I)      # draw a card = draw N card(s); "a creature" is not an amount
    line = re.sub(r"(?i)("+chr(92)+"bscry )"+NUMW, r"\1N", line)      # scry amounts too; Oracle writes them as digits
    return re.sub(NUMW + r"(?= (?:\w+ )?(?:cards?|damage|life|counters?|tokens?|mana|times))", "N", line, flags=re.I)


def mine():
    rules, used, seen = C.defaultdict(C.Counter), 0, 0
    for r in sorted(glob.glob(os.path.join(RUNS, "*/"))):
        for f in sorted(glob.glob(os.path.join(r, "in", "*.json"))):
            o = os.path.join(r, "out", os.path.basename(f))
            if not os.path.exists(o): continue
            try:
                I = json.load(open(f, encoding="utf-8"))["cards"]
                O = {c["id"]: c for c in json.load(open(o, encoding="utf-8"))["cards"]}
            except Exception: continue
            for c in I:
                if c["id"] not in O: continue
                seen += 1
                u = units(c["groups"])
                lines = [x.strip() for x in O[c["id"]]["text"].split(" / ") if x.strip()]
                if len(u) != len(lines): continue
                used += 1
                for (g, ts), line in zip(u.items(), lines): rules[pattern(ts)][templ(line)] += 1
    out = {}
    for p, cnt in rules.items():
        n = sum(cnt.values()); top = cnt.most_common(1)[0]
        out[p] = {"n": n, "top": round(top[1] / n, 3), "canon": top[0], "variants": [list(x) for x in cnt.most_common(6)[1:]]}
    return out, seen, used


# ---------- renderer: tags -> text (no Oracle text, no agent) ----------------------------------------------------------------------------------
WORDS = "zero a two three four five six seven eight nine ten".split()
_rules = {}


def rules():
    if not _rules:
        _rules.update(json.load(open(os.path.join(HERE, "render_rules.json"), encoding="utf-8")))
    return _rules


def nums(tagstrs):
    """amounts of a unit in tag order: '+2/+2' stays one amount (a P/T amount, kept apart from plain numbers); counter:p1p1 is +1/+1; 'x' is X"""
    out = []
    for t in " ".join(tagstrs).split():
        val = t.partition(":")[2]
        out += re.findall(r"[+\-]\d+/[+\-]\d+|\d+|\bx\b", val)
        if val in ("p1p1", "m1m1"): out.append("+1/+1" if val == "p1p1" else "-1/-1")
    return out


def fill(canon, ns):
    """put the card's amounts back into a mined phrasing: P/T amounts into +N/+N, other numbers into {N} and N, each from its own list; an amount with no tag stays N"""
    pt = [v for v in ns if "/" in v]; pl = [v for v in ns if "/" not in v]
    def sub(m):
        tok = m.group(0)
        if tok.startswith(("+", "-")): return pt.pop(0) if pt else tok
        if not pl: return tok
        v = pl.pop(0)
        if tok == "{N}": return "{%s}" % v.upper()
        if v.lower() == "x": return "X"
        if m.string[:m.start()].lower().endswith("scry ") or re.match(r" (?:\w+ )?(?:damage|life|mana)", m.string[m.end():]): return v      # Oracle writes digits for damage, life and mana
        return WORDS[int(v)] if v.isdigit() and int(v) <= 10 else v
    out = re.sub(r"[+\-]N/[+\-]N|\{N\}|\bN\b", sub, canon)
    return re.sub(r"\ba cards\b", "a card", out).replace("~", "this creature")


def lookup(pat):
    """exact pattern, else the closest mined pattern sharing at least 80% of its tags (flagged approx), else None"""
    R = rules()
    if pat in R: return R[pat], False
    a, best, bs = set(pat.split()), None, 0.8
    for p, v in R.items():
        b = set(p.split()); j = len(a & b) / len(a | b)
        if j >= bs and v["n"] >= 2: best, bs = v, j
    return (best, True) if best else (None, False)


def render(groups):
    """groups: {id: 'tag tag ...'} as in a reader batch card. returns (text, stats)"""
    u = units({g: t for g, t in groups.items()})
    lines, st = [], {"exact": 0, "approx": 0, "missing": 0}
    for g, ts in u.items():
        v, approx = lookup(pattern(ts))
        if approx or v is None:             # scry now sits in its ability's own group (it used to be a separate unit): render the rest, then add the scry sentence
            toks = " ".join(ts).split()
            if any(t.startswith("scry_count") for t in toks) and len(toks) > 1:
                rest = [t for t in toks if t.split(":")[0] != "scry_count"]
                v2, ap2 = lookup(pattern(rest))
                if v2 is not None and not ap2:
                    n = next((t.partition(":")[2] for t in toks if t.startswith("scry_count:")), "N")
                    st["exact"] += 1
                    base = fill(v2["canon"], nums(rest)).rstrip()
                    lines.append(base if re.search("scry", base, re.I) else base + " Scry %s." % n.upper()); continue
        if v is None:
            st["missing"] += 1; lines.append("{%s}" % " ".join(ts)); continue
        st["approx" if approx else "exact"] += 1
        lines.append(fill(v["canon"], nums(ts)))
    return " / ".join(lines), st


def cmd_render(a):
    n = C.Counter(); words = []
    for f in sorted(glob.glob(os.path.join(RUNS, a.run, "in", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if not isinstance(d, dict) or "cards" not in d: continue       # reminder files sit beside the batches
        d = d["cards"]
        o = os.path.join(RUNS, a.run, "out", os.path.basename(f))
        ref = {c["id"]: c["text"] for c in json.load(open(o, encoding="utf-8"))["cards"]} if os.path.exists(o) else {}
        for c in d:
            t, st = render(c.get("groups") or {}); n.update(st); n["cards"] += 1
            words.append({"id": c["id"], "text": t})
            if c["id"] in ref:
                x, y = RC.toks(RC.norm(t)), RC.toks(RC.norm(ref[c["id"]]))
                n["cmp"] += 1; n["same"] += (x == y); n["f1"] += RC.f1(set(x), set(y))[2]
    json.dump(words, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    tot = n["exact"] + n["approx"] + n["missing"]
    if n["cmp"]: print("vs the reader's text (same run, in-sample): exact %.1f%%, mean token F1 %.3f over %d cards" % (100 * n["same"] / n["cmp"], n["f1"] / n["cmp"], n["cmp"]))
    print("cards %d, units %d: exact %d, approx %d, missing %d (%.1f%%)" % (n["cards"], tot, n["exact"], n["approx"], n["missing"], 100 * n["missing"] / max(tot, 1)))


# ---------- tagger: card script -> tag groups (tag_run.record; the Oracle section of the script fills gaps) -------------------------------------
def tag_cards(names=None):
    """blind-shaped records (groups in reader-batch form) for the given card names, or the starters. No Oracle text leaves this function except through
    the verify flags, which are kept apart from the groups"""
    recs = RC.starter_records()
    if names:
        want = {n.strip().lower() for n in names}; recs = [r for r in recs if r["name"].lower() in want]
    return [(r, RC.tag_blind(r)) for r in recs]


def cmd_tag(a):
    pairs = tag_cards(a.cards.split(";") if a.cards else None)
    out, flags, placeholder, nt = [], 0, 0, 0
    for r, b in pairs:
        text, st = render(b["groups"])
        placeholder += st["missing"]; flags += bool(r["verify"]["flags"]); nt += len(b["tags"])
        out.append({"name": r["name"], "groups": b["groups"], "links": b["links"], "rendered": text, "flags": r["verify"]["flags"], "missing_units": st["missing"]})
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("tagged %d cards -> %s; cards with verify flags %d; rendered units with no rule %d" % (len(out), a.out, flags, placeholder))


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("mine"); m.add_argument("--out", default=os.path.join(HERE, "render_rules.json"))
    r = sp.add_parser("render"); r.add_argument("--run", required=True); r.add_argument("--out", default="rendered.json")
    t = sp.add_parser("tag"); t.add_argument("--cards", default=""); t.add_argument("--out", default="tagged.json")
    a = ap.parse_args()
    if a.cmd == "tag": return cmd_tag(a)
    if a.cmd == "render": return cmd_render(a)
    if a.cmd == "mine":
        rules, seen, used = mine()
        json.dump(rules, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        units_n = sum(r["n"] for r in rules.values())
        agree = sum(r["n"] * r["top"] for r in rules.values()) / max(units_n, 1)
        multi = sum(r["n"] for r in rules.values() if r["n"] >= 3)
        print("card readings %d, aligned %d; patterns %d; units %d; units in patterns seen 3+ times %d (%.0f%%); canonical = reader's top line for %.0f%% of units"
              % (seen, used, len(rules), units_n, multi, 100 * multi / max(units_n, 1), 100 * agree))


if __name__ == "__main__":
    main()

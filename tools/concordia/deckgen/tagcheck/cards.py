"""Card-record helpers the guards, sync, tag_audit and mtg2llm need without the reverse-check exporter (SCRIPT_MERGE_ANALYSIS.md, step 3 part 4):
tag_blind (what the blind reader may see of a record), starter_records, pre6_only / is_pre6 (cards older than Sixth Edition are kept out of runs).
Moved unchanged out of reverse_check.py, which re-exports them."""
import os, re, sys, glob
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
import tag_run as T  # noqa: E402
import tag_verify as TV  # noqa: E402


def _fold_scales(groups, rec):
    """an x_is:count_<thing>[_you_control] tag already says 'for each <thing>': drop the scales:<thing> twin from the same group and the scales_with link that joins them (one tag, not three)"""
    twins = {}
    for g, ts in groups.items():
        for t in ts:
            m = re.match(r"^x_is:count_(.+?)(?:_you_control)?$", t)
            if m and ("scales:" + m.group(1)) in ts: twins.setdefault(g, set()).add("scales:" + m.group(1))
    groups = {g: [t for t in ts if t not in twins.get(g, ())] for g, ts in groups.items()}
    links = [l for l in rec["links"] if not (l[1] == "scales_with" and l[2].split(":", 1)[0] in twins and l[2].split(":", 1)[-1].startswith("x_is:count_"))]
    return groups, dict(rec, links=links)


def _fold_x(groups):
    """the cross-check's leftover group x joins the ability it belongs to when that is unambiguous: a trigger tag goes to the only top-level group with no trigger, any other leftover to the only top-level ability group (as a new sub-group); otherwise it stays x"""
    x = groups.get("x")
    if not x: return groups
    tops = [g for g in groups if re.fullmatch(r"c[1-9]\d*", g)]
    if not tops: return groups
    out = dict(groups); trig = [t for t in x if t.startswith("trigger:")]
    if trig:
        free = [g for g in tops if not any(t.startswith("trigger:") for t in groups[g])]
        if len(free) != 1: return groups
        out[free[0]] = trig + groups[free[0]]; rest = [t for t in x if t not in trig]
    elif len(tops) == 1: rest = list(x)
    else: return groups
    del out["x"]
    if rest:
        if len(tops) != 1: return groups
        k = 2 + sum(1 for g in groups if g.startswith(tops[0] + "."))
        out["%s.%d" % (tops[0], k)] = rest
    return out


def tag_blind(rec):
    """the blind view of one record: rules tags, groups and links only. AI Tags (tag_verify.is_ai_tag: opaque metrics, the AILogic reference, umbrella labels) are segregated and not shown at all.
    Group ids are kept; the source of a group (K line, A line ...), clauses, mtgish and AI lines are dropped"""
    groups = {("x" if g == "v" else g): [t for t in ts if not TV.is_ai_tag(t)] for g, ts in rec["groups"].items()}
    groups = _fold_x(groups); groups, rec = _fold_scales(groups, rec)
    ty = ("supertype:", "cardtype:", "type:", "landtype:")
    return {"typing": [t for t in rec["tags"] if t.startswith(ty)], "tags": [t for t in rec["tags"] if not TV.is_ai_tag(t) and not t.startswith(ty)],
            "groups": {g: " ".join(ts) for g, ts in groups.items() if ts}, "links": ["%s %s %s" % l for l in rec["links"] if not any(TV.is_ai_tag(p.split(":", 1)[-1]) for p in (l[0], l[2]))]}


def starter_records():
    import glob, collections as C
    names = C.OrderedDict()
    for d in sorted(glob.glob(os.path.join(T.ROOT, "forge-gui/res/adventure/Concordia/decks/starter/*.dck"))):
        for n in T.deck_cards(d): names[n] = 1
    return [T.record(n, T.find_text(n)) for n in names]


_PRE6 = []
def pre6_only():
    """lower-cased names of cards whose every printing is older than Sixth Edition (1999-04-21): stale formatting, kept out of runs, mining and tests"""
    if _PRE6: return _PRE6[0]
    first, late = set(), set()
    for f in glob.glob(os.path.join(T.ROOT, "forge-gui/res/editions/*.txt")):
        t = open(f, encoding="utf-8", errors="ignore").read()
        d = re.search(r"^Date=(\S+)", t, re.M)
        if not d: continue
        for m in re.finditer(r"^\d+\w*\s+[A-Z]+\s+(.+?)(?:\s+@.*)?$", t, re.M):
            (late if d.group(1) >= "1999-04-21" else first).add(m.group(1).strip().lower())
    _PRE6.append(first - late); return _PRE6[0]


def is_pre6(name): return all(p.strip().lower() in pre6_only() for p in name.split("//"))

_FIRST = []
def first_dates():
    """lower-cased card name -> date of its earliest printing in the Forge editions (ISO string)"""
    if _FIRST: return _FIRST[0]
    d = {}
    for f in glob.glob(os.path.join(T.ROOT, "forge-gui/res/editions/*.txt")):
        t = open(f, encoding="utf-8", errors="ignore").read()
        m = re.search(r"^Date=(\S+)", t, re.M)
        if not m: continue
        for c in re.finditer(r"^\d+\w*\s+[A-Z]+\s+(.+?)(?:\s+@.*)?$", t, re.M):
            n = c.group(1).strip().lower()
            if n not in d or m.group(1) < d[n]: d[n] = m.group(1)
    _FIRST.append(d); return d


MODERN_FROM = "2003-07-28"      # Eighth Edition: the modern card frame
def is_modern(name): return all(first_dates().get(p.strip().lower(), "") >= MODERN_FROM for p in name.split("//"))


from common import eligible_names, is_eligible  # noqa: E402,F401  (moved to common.py so every tagger shares it)

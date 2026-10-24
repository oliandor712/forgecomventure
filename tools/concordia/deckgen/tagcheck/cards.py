"""Card-record helpers the guards, sync, tag_audit and mtg2llm need without the reverse-check exporter (SCRIPT_MERGE_ANALYSIS.md, step 3 part 4):
tag_blind (what the blind reader may see of a record), starter_records, pre6_only / is_pre6 (cards older than Sixth Edition are kept out of runs).
Moved unchanged out of reverse_check.py, which re-exports them."""
import os, re, sys, glob
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
import tag_run as T  # noqa: E402
import tag_verify as TV  # noqa: E402


def tag_blind(rec):
    """the blind view of one record: rules tags, groups and links only. AI Tags (tag_verify.is_ai_tag: opaque metrics, the AILogic reference, umbrella labels) are segregated and not shown at all.
    Group ids are kept; the source of a group (K line, A line ...), clauses, mtgish and AI lines are dropped"""
    groups = {("x" if g == "v" else g): [t for t in ts if not TV.is_ai_tag(t)] for g, ts in rec["groups"].items()}
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
